#!/usr/bin/env python3
"""Assign HS codes to imported products based on category-to-HS-code mapping.

Usage:
    cd apps/Server
    python -m scripts.assign_hs_codes              # Category mapping only
    python -m scripts.assign_hs_codes --use-ai      # Include AI suggestions
    python -m scripts.assign_hs_codes --dry-run     # Preview only
    python -m scripts.assign_hs_codes --verbose     # Detailed output
"""

import argparse
import json
import os
import sys
import time
from typing import Any, Optional
from uuid import UUID

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.database import close_database_connection, get_database_connection
from app.repository.kompass_repository import product_repository
from app.services.extraction_service import extraction_service

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Hardcoded mapping: category path -> HS code string
# Maps each leaf/direct category to its corresponding HS code.
# ONE STOP SHOP is mapped to None (mixed category, needs AI or manual).
CATEGORY_HS_MAP: dict[str, Optional[str]] = {
    "BAÑOS/Griferías": "7324.90",
    "BAÑOS/Lavamanos": "7324.10",
    "BAÑOS/Sanitarios y Muebles de Baño": "6910.10",
    "DECK - FACHADAS": "4411.14",
    "DISPENSADORES": "8481.80",
    "DOTACIÓN DE COCINA": "7323.93",
    "ESPEJOS": "7013.49",
    "ILUMINACIÓN": "9405.10",
    "MOBILIARIO": "9403.60",  # Default: wooden furniture
    "MOBILIARIO/Camas": "9403.60",
    "MOBILIARIO/Mesas de Noche": "9403.60",
    "MOBILIARIO/Mobiliario Restaurante": "9403.20",
    "MOBILIARIO/Mobiliario a Medida": "9401.61",
    "ONE STOP SHOP": None,  # Mixed category — needs keyword or AI assignment
    "PISOS - GUARDAESCOBAS": "6907.21",  # Default: ceramic tiles
    "PISOS - GUARDAESCOBAS/SPC Floor": "3921.90",
    "PISOS - GUARDAESCOBAS/Guardaescobas": "3917.40",
    "REVESTIMIENTOS": "3921.90",  # Default: plastic panels
    "REVESTIMIENTOS/Panel Exterior": "6907.21",
    "REVESTIMIENTOS/Panel Interior": "6907.21",
    "TARIMAS & EVENTOS": "7610.90",
}

# Keyword -> HS code mapping for Phase 1.5 (keyword-based assignment).
# Checked against lowercased product name + description.
# Order matters: more specific keywords should come before broad ones.
KEYWORD_HS_MAP: list[tuple[list[str], str]] = [
    # Ceramic sanitaryware
    (["toilet", "inodoro", "wc", "basin", "lavabo"], "6910.10"),
    # Faucets, sanitary fittings, drains
    (["faucet", "grifo", "tap", "mixer", "shower head", "drain", "valve",
      "angle valve", "hosepipe", "tissue holder", "drainer"], "7324.90"),
    # Ceramic tiles
    (["tile", "porcelain", "ceramic", "mosaic", "sintered stone",
      "baldosa"], "6907.21"),
    # Mirrors, glassware
    (["mirror", "espejo", "glass brick", "shower glass"], "7013.49"),
    # Upholstered seating
    (["sofa", "chair", "silla", "seat", "pebble sofa", "ottoman"], "9401.61"),
    # Wooden furniture (broad)
    (["table", "mesa", "cabinet", "closet", "desk", "bed", "cama",
      "dresser", "nightstand", "drawer", "shelf", "bookcase",
      "wardrobe", "vanity", "sideboard"], "9403.60"),
    # Metal furniture
    (["metal frame", "steel table", "metal chair"], "9403.20"),
    # Plastic plates/sheets (SPC, PVC panels)
    (["spc", "pvc wall", "pvc ceiling", "pvc panel", "pvc exterior",
      "acoustic panel"], "3921.90"),
    # MDF/fibreboard (WPC)
    (["wpc", "wood plastic", "deck tile"], "4411.14"),
    # Aluminum structures
    (["aluminum", "aluminium", "truss", "metal panel",
      "outdoor metal"], "7610.90"),
    # Kitchenware
    (["kitchen", "cocina", "rack", "dish rack"], "7323.93"),
    # Lighting
    (["light", "lamp", "led", "chandelier", "luminaria", "downlight",
      "track light", "panel light"], "9405.10"),
    # Baseboards
    (["baseboard", "guardaescoba", "skirting"], "3917.40"),
    # Dispensers
    (["dispenser", "dispensador"], "8481.80"),
    # Concrete/stone boards (treated as ceramic tiles)
    (["concrete board", "stone board", "ripple board"], "6907.21"),
]

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
RESULTS_FILE = os.path.join(OUTPUT_DIR, "hs_assignment_results.json")
MAPPINGS_FILE = os.path.join(OUTPUT_DIR, "seed_mappings.json")


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def load_seed_mappings() -> Optional[dict]:
    """Load and validate seed_mappings.json.

    Returns:
        Parsed mappings dict or None if file is missing/invalid.
    """
    if not os.path.exists(MAPPINGS_FILE):
        print(f"ERROR [AssignHSCodes]: seed_mappings.json not found at {MAPPINGS_FILE}")
        print("  Run 'python -m scripts.seed_all' first to generate mappings.")
        return None

    with open(MAPPINGS_FILE, "r", encoding="utf-8") as f:
        mappings = json.load(f)

    required_keys = ["categories", "hs_codes"]
    for key in required_keys:
        if key not in mappings:
            print(f"ERROR [AssignHSCodes]: Missing '{key}' section in seed_mappings.json")
            return None

    print("INFO [AssignHSCodes]: Loaded seed_mappings.json")
    print(f"  Categories: {len(mappings['categories'])} mapped")
    print(f"  HS codes: {len(mappings['hs_codes'])} mapped")
    return mappings


def build_category_hs_map(
    mappings: dict,
) -> tuple[dict[str, str], dict[str, str]]:
    """Build category_uuid -> hs_code_uuid reverse map.

    Args:
        mappings: Loaded seed_mappings dict with 'categories' and 'hs_codes'.

    Returns:
        Tuple of (reverse_map, hs_code_map):
        - reverse_map: {category_uuid: hs_code_uuid}
        - hs_code_map: {hs_code_string: hs_code_uuid} for AI matching
    """
    categories = mappings["categories"]
    hs_codes = mappings["hs_codes"]
    reverse_map: dict[str, str] = {}

    for category_path, hs_code_str in CATEGORY_HS_MAP.items():
        if hs_code_str is None:
            continue

        category_uuid = categories.get(category_path)
        hs_code_uuid = hs_codes.get(hs_code_str)

        if not category_uuid:
            print(f"  WARN [AssignHSCodes]: Category '{category_path}' not found in seed mappings")
            continue
        if not hs_code_uuid:
            print(f"  WARN [AssignHSCodes]: HS code '{hs_code_str}' not found in seed mappings")
            continue

        reverse_map[category_uuid] = hs_code_uuid

    # Build hs_code_map for AI matching
    hs_code_map: dict[str, str] = {code: uuid for code, uuid in hs_codes.items()}

    print(f"  Reverse map: {len(reverse_map)} category->HS code entries")
    return reverse_map, hs_code_map


def get_products_without_hs_code() -> list[dict[str, Any]]:
    """Query all products where hs_code_id IS NULL.

    Uses raw SQL for bulk query (consistent with repository pattern).

    Returns:
        List of product dicts with id, name, description, category_id.
    """
    conn = get_database_connection()
    if not conn:
        print("ERROR [AssignHSCodes]: Could not connect to database")
        return []

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, name, description, category_id
                FROM products
                WHERE hs_code_id IS NULL
                ORDER BY name
                """
            )
            columns = ["id", "name", "description", "category_id"]
            rows = cur.fetchall()
            return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print(f"ERROR [AssignHSCodes]: Failed to query products: {e}")
        return []
    finally:
        close_database_connection(conn)


def assign_by_category(
    products: list[dict[str, Any]],
    reverse_map: dict[str, str],
    args: argparse.Namespace,
) -> tuple[int, list[dict[str, Any]]]:
    """Assign HS codes to products using the category reverse map.

    Args:
        products: Products with category_id set.
        reverse_map: {category_uuid: hs_code_uuid} map.
        args: CLI arguments (dry_run, verbose).

    Returns:
        Tuple of (assigned_count, unmatched_products).
    """
    assigned = 0
    unmatched: list[dict[str, Any]] = []

    for product in products:
        category_id = str(product["category_id"])
        hs_code_uuid = reverse_map.get(category_id)

        if not hs_code_uuid:
            unmatched.append(product)
            if args.verbose:
                print(f"  UNMATCHED: {product['name'][:60]} (category_id={category_id})")
            continue

        if args.verbose:
            print(f"  ASSIGN: {product['name'][:60]} -> hs_code={hs_code_uuid[:8]}...")

        if not args.dry_run:
            result = product_repository.update(
                product_id=UUID(str(product["id"])),
                hs_code_id=UUID(hs_code_uuid),
            )
            if not result:
                print(f"  ERROR [AssignHSCodes]: Failed to update product {product['id']}")
                unmatched.append(product)
                continue

        assigned += 1

    return assigned, unmatched


def assign_by_keyword(
    products: list[dict[str, Any]],
    hs_code_map: dict[str, str],
    args: argparse.Namespace,
) -> tuple[int, list[dict[str, Any]]]:
    """Assign HS codes to products using keyword matching on name + description.

    Iterates KEYWORD_HS_MAP in order; first keyword match wins.

    Args:
        products: Unmatched products from category phase.
        hs_code_map: {hs_code_string: hs_code_uuid} for resolving codes.
        args: CLI arguments (dry_run, verbose).

    Returns:
        Tuple of (assigned_count, still_unmatched_products).
    """
    assigned = 0
    unmatched: list[dict[str, Any]] = []

    for product in products:
        # Build searchable text from name + description
        text_parts = []
        if product.get("name"):
            text_parts.append(product["name"])
        if product.get("description"):
            text_parts.append(product["description"])
        text = " ".join(text_parts).lower()

        matched_code: Optional[str] = None
        matched_keyword: Optional[str] = None

        for keywords, hs_code_str in KEYWORD_HS_MAP:
            for kw in keywords:
                if kw in text:
                    matched_code = hs_code_str
                    matched_keyword = kw
                    break
            if matched_code:
                break

        if not matched_code:
            unmatched.append(product)
            if args.verbose:
                print(f"  NO KEYWORD: {product['name'][:60]}")
            continue

        hs_code_uuid = hs_code_map.get(matched_code)
        if not hs_code_uuid:
            if args.verbose:
                print(
                    f"  WARN: Keyword '{matched_keyword}' matched HS code '{matched_code}' "
                    f"but code not in seeded data — skipping {product['name'][:40]}"
                )
            unmatched.append(product)
            continue

        if args.verbose:
            print(f"  KEYWORD: {product['name'][:50]} -> '{matched_keyword}' -> {matched_code}")

        if not args.dry_run:
            result = product_repository.update(
                product_id=UUID(str(product["id"])),
                hs_code_id=UUID(hs_code_uuid),
            )
            if not result:
                print(f"  ERROR [AssignHSCodes]: Failed to update product {product['id']}")
                unmatched.append(product)
                continue

        assigned += 1

    return assigned, unmatched


def assign_by_ai(
    products: list[dict[str, Any]],
    hs_code_map: dict[str, str],
    args: argparse.Namespace,
) -> tuple[int, list[dict[str, Any]]]:
    """Assign HS codes using AI suggestion for unmatched/uncategorized products.

    Args:
        products: Products to process via AI.
        hs_code_map: {hs_code_string: hs_code_uuid} for matching AI results.
        args: CLI arguments (dry_run, verbose).

    Returns:
        Tuple of (ai_assigned_count, still_unmatched_products).
    """
    ai_assigned = 0
    still_unmatched: list[dict[str, Any]] = []

    for idx, product in enumerate(products):
        # Build description for AI
        description_parts = []
        if product.get("name"):
            description_parts.append(product["name"])
        if product.get("description"):
            description_parts.append(product["description"])
        description = " — ".join(description_parts) if description_parts else "Unknown product"

        if args.verbose:
            print(f"  AI [{idx + 1}/{len(products)}]: {product['name'][:50]}...")

        suggestion = extraction_service.suggest_hs_code(description)

        # Rate limit: 1 second between AI calls
        if idx < len(products) - 1:
            time.sleep(1)

        # Check for fallback code
        if suggestion.code == "9999.99.99":
            if args.verbose:
                print("    -> AI returned fallback code, skipping")
            still_unmatched.append(product)
            continue

        # Truncate AI code to XXXX.XX for matching against seeded codes
        ai_code_truncated = suggestion.code[:7]
        hs_code_uuid = hs_code_map.get(ai_code_truncated)

        if not hs_code_uuid:
            if args.verbose:
                print(
                    f"    -> AI suggested '{suggestion.code}' (truncated: '{ai_code_truncated}') "
                    f"— not in seeded codes, skipping"
                )
            still_unmatched.append(product)
            continue

        if args.verbose:
            print(
                f"    -> AI suggested '{ai_code_truncated}' "
                f"(confidence: {suggestion.confidence_score:.2f}) — MATCH"
            )

        if not args.dry_run:
            result = product_repository.update(
                product_id=UUID(str(product["id"])),
                hs_code_id=UUID(hs_code_uuid),
            )
            if not result:
                print(f"  ERROR [AssignHSCodes]: Failed to update product {product['id']}")
                still_unmatched.append(product)
                continue

        ai_assigned += 1

    return ai_assigned, still_unmatched


# ---------------------------------------------------------------------------
# Output functions
# ---------------------------------------------------------------------------


def print_summary(
    total_products: int,
    categorized_count: int,
    uncategorized_count: int,
    mapped_count: int,
    unmatched_count: int,
    keyword_assigned_count: int,
    ai_assigned_count: int,
    still_without_count: int,
    dry_run: bool,
) -> None:
    """Print a formatted summary table."""
    mode = "DRY-RUN" if dry_run else "LIVE"
    print(f"\n{'=' * 55}")
    print(f"  HS CODE ASSIGNMENT SUMMARY ({mode})")
    print(f"{'=' * 55}")
    print(f"  {'Total products without HS code:':<40} {total_products:>6}")
    print(f"  {'With category:':<40} {categorized_count:>6}")
    print(f"  {'Without category:':<40} {uncategorized_count:>6}")
    print(f"{'─' * 55}")
    print(f"  {'Assigned via category map:':<40} {mapped_count:>6}")
    print(f"  {'Assigned via keyword match:':<40} {keyword_assigned_count:>6}")
    if ai_assigned_count > 0:
        print(f"  {'Assigned via AI suggestion:':<40} {ai_assigned_count:>6}")
    print(f"{'─' * 55}")
    print(f"  {'Still without HS code:':<40} {still_without_count:>6}")
    print(f"{'=' * 55}")


def write_results_json(results: dict[str, Any]) -> None:
    """Write detailed results to JSON file."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nINFO [AssignHSCodes]: Results written to {RESULTS_FILE}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Orchestrate the HS code assignment process."""
    parser = argparse.ArgumentParser(
        description="Assign HS codes to products based on category mapping"
    )
    parser.add_argument(
        "--use-ai",
        action="store_true",
        help="Use AI suggestions for unmatched/uncategorized products",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be assigned without database writes",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print each individual assignment",
    )
    args = parser.parse_args()

    print("=" * 55)
    print("  HS CODE ASSIGNMENT TO PRODUCTS")
    if args.dry_run:
        print("  MODE: DRY-RUN (no database writes)")
    if args.use_ai:
        print("  AI SUGGESTIONS: ENABLED")
    print("=" * 55)

    # Load seed mappings
    mappings = load_seed_mappings()
    if mappings is None:
        sys.exit(1)

    # Build reverse map
    reverse_map, hs_code_map = build_category_hs_map(mappings)

    # Get all products without HS codes
    products = get_products_without_hs_code()
    total_products = len(products)

    if total_products == 0:
        print("\nINFO [AssignHSCodes]: 0 products to process. All products already have HS codes.")
        return

    print(f"\nINFO [AssignHSCodes]: Found {total_products} products without HS codes")

    # Split into categorized and uncategorized
    categorized = [p for p in products if p.get("category_id")]
    uncategorized = [p for p in products if not p.get("category_id")]

    print(f"  With category: {len(categorized)}")
    print(f"  Without category: {len(uncategorized)}")

    # Phase 1: Category-based assignment
    print("\n--- Phase 1: Category-based assignment ---")
    mapped_count, unmatched = assign_by_category(categorized, reverse_map, args)
    print(f"  Assigned: {mapped_count}, Unmatched: {len(unmatched)}")

    # Phase 1.5: Keyword-based assignment on remaining unmatched
    keyword_assigned_count = 0
    keyword_candidates = unmatched + uncategorized
    if keyword_candidates:
        print(f"\n--- Phase 1.5: Keyword-based assignment ({len(keyword_candidates)} products) ---")
        keyword_assigned_count, keyword_unmatched = assign_by_keyword(
            keyword_candidates, hs_code_map, args
        )
        print(f"  Assigned: {keyword_assigned_count}, Unmatched: {len(keyword_unmatched)}")
    else:
        keyword_unmatched = []

    # Phase 2: AI-based assignment (optional)
    ai_assigned_count = 0
    ai_still_unmatched: list[dict[str, Any]] = []
    if args.use_ai and keyword_unmatched:
        print(f"\n--- Phase 2: AI-based assignment ({len(keyword_unmatched)} products) ---")
        ai_assigned_count, ai_still_unmatched = assign_by_ai(
            keyword_unmatched, hs_code_map, args
        )
        print(f"  AI assigned: {ai_assigned_count}, Still unmatched: {len(ai_still_unmatched)}")
    else:
        ai_still_unmatched = keyword_unmatched

    still_without_count = len(ai_still_unmatched)

    # Summary
    print_summary(
        total_products=total_products,
        categorized_count=len(categorized),
        uncategorized_count=len(uncategorized),
        mapped_count=mapped_count,
        unmatched_count=len(unmatched),
        keyword_assigned_count=keyword_assigned_count,
        ai_assigned_count=ai_assigned_count,
        still_without_count=still_without_count,
        dry_run=args.dry_run,
    )

    # Write results JSON
    results = {
        "summary": {
            "total_products_without_hs_code": total_products,
            "with_category": len(categorized),
            "without_category": len(uncategorized),
            "assigned_by_category_map": mapped_count,
            "unmatched_after_category": len(unmatched),
            "assigned_by_keyword": keyword_assigned_count,
            "assigned_by_ai": ai_assigned_count,
            "still_without_hs_code": still_without_count,
            "dry_run": args.dry_run,
            "use_ai": args.use_ai,
        },
        "still_without_hs_code": [
            {
                "id": str(p["id"]),
                "name": p["name"],
                "category_id": str(p["category_id"]) if p.get("category_id") else None,
            }
            for p in ai_still_unmatched
        ],
    }
    write_results_json(results)

    print("\nINFO [AssignHSCodes]: HS code assignment complete.")


if __name__ == "__main__":
    main()
