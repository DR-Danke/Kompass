#!/usr/bin/env python3
"""Batch import script for products from supplier catalog files.

Processes all supplier catalog files from the PROVEEDORES - CATALOGOS directory,
extracts product data using the extraction service, and imports into the database
via the product service's bulk_create_products method.

Usage:
    cd apps/Server
    python -m scripts.import_products              # Full import
    python -m scripts.import_products --dry-run     # Parse only, no DB writes
    python -m scripts.import_products --file "BAÑOS/GRIFERIASS/HUAYI/HUAYI (1).xlsx"
    python -m scripts.import_products --verbose     # Print each product
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.kompass_dto import ProductCreateDTO, ProductStatus
from app.services.extraction_service import extraction_service
from app.services.product_service import product_service

# Output directory for results (matches seed_all.py pattern)
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "import_results.json")
MAPPINGS_FILE = os.path.join(OUTPUT_DIR, "seed_mappings.json")

# Base path for catalog files relative to the repo root
CATALOG_BASE_PATH = os.path.join(
    "Requirements_Gathering",
    "Sourcing",
    "Data",
    "PROVEEDORES - CATALOGOS",
)

# FILE_MAP: Maps each catalog file (relative to CATALOG_BASE_PATH) to its
# supplier name and category path. Keys must match seed_mappings.json entries.
FILE_MAP: dict[str, dict[str, str]] = {
    # --- BAÑOS/GRIFERIASS ---
    "BAÑOS/GRIFERIASS/HUAYI/HUAYI (1).xlsx": {
        "supplier": "HUAYI",
        "category": "BAÑOS/Griferías",
    },
    "BAÑOS/GRIFERIASS/JVK/Quotation JVK.xlsx": {
        "supplier": "JVK",
        "category": "BAÑOS/Griferías",
    },
    "BAÑOS/GRIFERIASS/LAYASDUN/LAYASDUN Quotation.xlsx": {
        "supplier": "LAYASDUN",
        "category": "BAÑOS/Griferías",
    },
    "BAÑOS/GRIFERIASS/PINLSLON BUILDING MATERIALS/2026 Pinslon price list-faucets (2).pdf": {
        "supplier": "PINLSLON",
        "category": "BAÑOS/Griferías",
    },
    # --- BAÑOS/GRIFERIAS_ducha_baño_cocina ---
    "BAÑOS/GRIFERIAS_ducha _baño _cocina/LAYASDUN/Quote from Layasdun 20251201.pdf": {
        "supplier": "LAYASDUN",
        "category": "BAÑOS/Griferías",
    },
    # --- BAÑOS/LAVAMANOS ---
    "BAÑOS/LAVAMANOS/Quotation from Conrazzo.pdf": {
        "supplier": "CONRAZZO",
        "category": "BAÑOS/Lavamanos",
    },
    # --- BAÑOS/SANITARIOS Y MUEBLES DE BAÑO ---
    "BAÑOS/SANITARIOS Y MUEBLES DE BAÑO/Price list From BATH STORE- TAUSU.xlsx": {
        "supplier": "BATH STORE-TAUSU",
        "category": "BAÑOS/Sanitarios y Muebles de Baño",
    },
    # --- BAÑOS (root) ---
    "BAÑOS/STAINLESS.xlsx": {
        "supplier": "HUAYI",
        "category": "BAÑOS/Griferías",
    },
    # --- DECK - FACHADAS ---
    "DECK - FACHADAS/MEXY TECH - DECK/MexyTech catalog (1).pdf": {
        "supplier": "MEXY TECH",
        "category": "DECK - FACHADAS",
    },
    "DECK - FACHADAS/MEXY TECH - DECK/REQUIREMENT FORMAT (3).xlsx": {
        "supplier": "MEXY TECH",
        "category": "DECK - FACHADAS",
    },
    # --- DISPENSADORES ---
    "DISPENSADORES/Quotation LA20251129K.pdf": {
        "supplier": "LAYASDUN",
        "category": "DISPENSADORES",
    },
    # --- DOTACIÓN DE COCINA ---
    "DOTACIÓN DE COCINA/KITCHENWARE -CHINA.xlsx": {
        "supplier": "WIREKING",
        "category": "DOTACIÓN DE COCINA",
    },
    "DOTACIÓN DE COCINA/MAYORISTA COLOMBIA/COT 2026-06 (1).pdf": {
        "supplier": "MAYORISTA COLOMBIA",
        "category": "DOTACIÓN DE COCINA",
    },
    "DOTACIÓN DE COCINA/WIREKING_ DOT COCINA/Wireking Quotation - Kompasstrading -2025-12-01.xlsx": {
        "supplier": "WIREKING",
        "category": "DOTACIÓN DE COCINA",
    },
    # --- ESPEJOS ---
    "ESPEJOS/LUXDREAM/2026 Luxdream Led Mirror E-Brochure.pdf": {
        "supplier": "LUXDREAM",
        "category": "ESPEJOS",
    },
    "ESPEJOS/LUXDREAM/S-Luxdream Led Bathroom Mirror Price List.pdf": {
        "supplier": "LUXDREAM",
        "category": "ESPEJOS",
    },
    # --- ILUMINACIÓN ---
    "ILUMINACIÓN/GEORGE/Precios Iluminación - George.xlsx": {
        "supplier": "GEORGE",
        "category": "ILUMINACIÓN",
    },
    "ILUMINACIÓN/LED_ BWBYONE/BYONE BDEXPO CATALOG 2025.12 (2).pdf": {
        "supplier": "BWBYONE",
        "category": "ILUMINACIÓN",
    },
    "ILUMINACIÓN/LED_ BWBYONE/price list of  track light from Bwbyone Sophia.pdf": {
        "supplier": "BWBYONE",
        "category": "ILUMINACIÓN",
    },
    "ILUMINACIÓN/LED_ BWBYONE/price list of downlight from Bwbyone Sophia.pdf": {
        "supplier": "BWBYONE",
        "category": "ILUMINACIÓN",
    },
    "ILUMINACIÓN/LED_ BWBYONE/price list of panel light from Bwbyone Sophia(经济款）  2026.1.3.pdf": {
        "supplier": "BWBYONE",
        "category": "ILUMINACIÓN",
    },
    # --- MOBILIARIO ---
    "MOBILIARIO/CAMAS_LEIZE/LEIZI Quotation for Aldjandro (1).pdf": {
        "supplier": "LEIZI",
        "category": "MOBILIARIO/Camas",
    },
    "MOBILIARIO/CAMAS_LEIZE/LEIZI-Hotel Mattress Catalog 202508.pdf": {
        "supplier": "LEIZI",
        "category": "MOBILIARIO/Camas",
    },
    "MOBILIARIO/MESAS DE NOCHE USB/NTFT Yifuyuan Bedside table Quotation（2025.9)(1).xlsx": {
        "supplier": "NTFT YIFUYUAN",
        "category": "MOBILIARIO/Mesas de Noche",
    },
    "MOBILIARIO/MOBILIARIO _FOSHAN SHISUO TECHNOLOGY CO LTD/COT FOSHAN SHISUO.xlsx": {
        "supplier": "FOSHAN SHISUO",
        "category": "MOBILIARIO",
    },
    "MOBILIARIO/MOBILIARIO_DHF/KOMPASS TRADING  Quotation sheet  Dec 05,2025.xls": {
        "supplier": "DHF",
        "category": "MOBILIARIO",
    },
    "MOBILIARIO/MOBILIARIO_RESTAURANTE_WEIRE/RESTAURANT FURNITURE CURADO.xlsx": {
        "supplier": "WEIRE",
        "category": "MOBILIARIO/Mobiliario Restaurante",
    },
    "MOBILIARIO/MOBILIARIO_SENCHUAN/SENCHUAN_20251201.pdf": {
        "supplier": "SENCHUAN",
        "category": "MOBILIARIO",
    },
    "MOBILIARIO/MOBILIARIO_SENCHUAN/SENCHUAN_20251201.xlsx": {
        "supplier": "SENCHUAN",
        "category": "MOBILIARIO",
    },
    # --- ONE STOP SHOP ---
    "ONE STOP SHOP/GEORGE/Copy of Shamsa tile quotation 2025.11.30.xlsx": {
        "supplier": "GEORGE",
        "category": "ONE STOP SHOP",
    },
    "ONE STOP SHOP/GEORGE/George - cocina y closets quotation.xlsx": {
        "supplier": "GEORGE",
        "category": "ONE STOP SHOP",
    },
    "ONE STOP SHOP/GEORGE/George - Furniture Quotation.xlsx": {
        "supplier": "GEORGE",
        "category": "ONE STOP SHOP",
    },
    "ONE STOP SHOP/GEORGE/George - Sanitary Quotation.xlsx": {
        "supplier": "GEORGE",
        "category": "ONE STOP SHOP",
    },
    "ONE STOP SHOP/PA HOME/1. PA Quotation for Kitchens & closets-2025.12.05.pdf": {
        "supplier": "PA HOME",
        "category": "ONE STOP SHOP",
    },
    # --- PISOS - GUARDAESCOBAS ---
    "PISOS - GUARDAESCOBAS/CU MATERIALS/Precios CU Materiales seleccionados.xlsx": {
        "supplier": "CU MATERIALS",
        "category": "PISOS - GUARDAESCOBAS/SPC Floor",
    },
    "PISOS - GUARDAESCOBAS/HONGYU/MARBLE IMPRESSION -  HONGYU quotation 20251219 (1).xlsx": {
        "supplier": "HONGYU",
        "category": "PISOS - GUARDAESCOBAS",
    },
    "PISOS - GUARDAESCOBAS/HONGYU/STONE ESSENCE - HONGYU quotation 20251219 (2).xlsx": {
        "supplier": "HONGYU",
        "category": "PISOS - GUARDAESCOBAS",
    },
    "PISOS - GUARDAESCOBAS/HONGYU/WALL TILES - HONGYU quotation 20251219 (3).xlsx": {
        "supplier": "HONGYU",
        "category": "PISOS - GUARDAESCOBAS",
    },
    "PISOS - GUARDAESCOBAS/HONGYU/WOODEN TILES - HONGYU quotation 20251211.xls": {
        "supplier": "HONGYU",
        "category": "PISOS - GUARDAESCOBAS",
    },
    "PISOS - GUARDAESCOBAS/JINGDA_SPC/JINGDA SPC FLOOR - COT.xlsx": {
        "supplier": "JINGDA",
        "category": "PISOS - GUARDAESCOBAS/SPC Floor",
    },
    "PISOS - GUARDAESCOBAS/SOTENG_GUARDAESCOBAS/SOTENG _ COT _ GUARDAESCOBAS.xlsx": {
        "supplier": "SOTENG",
        "category": "PISOS - GUARDAESCOBAS/Guardaescobas",
    },
    "PISOS - GUARDAESCOBAS/SOTENG_GUARDAESCOBAS/【PS线条目录+颜色】-0011 (1).pdf": {
        "supplier": "SOTENG",
        "category": "PISOS - GUARDAESCOBAS/Guardaescobas",
    },
    "PISOS - GUARDAESCOBAS/SOTENG_GUARDAESCOBAS/【PS线条目录+颜色】-0011.pdf": {
        "supplier": "SOTENG",
        "category": "PISOS - GUARDAESCOBAS/Guardaescobas",
    },
    # --- REVESTIMIENTOS ---
    "REVESTIMIENTOS/CU MATERIALS/Precios CU Materiales seleccionados.xlsx": {
        "supplier": "CU MATERIALS",
        "category": "REVESTIMIENTOS",
    },
    "REVESTIMIENTOS/WUXI KAIZE _ PANEL EXT - INT/Wuxi Kaize Import and Export Co., Ltd. 材料目录册(1) (1).pdf": {
        "supplier": "WUXI KAIZE",
        "category": "REVESTIMIENTOS/Panel Exterior",
    },
    "REVESTIMIENTOS/WUXI KAIZE _ PANEL EXT - INT/Wuxi Kaize Indoor & Outdoor Panel Price List – FOB Prices.xlsx": {
        "supplier": "WUXI KAIZE",
        "category": "REVESTIMIENTOS/Panel Exterior",
    },
    # --- TARIMAS & EVENTOS ---
    "TARIMAS & EVENTOS/4 pillar Van-Ruben Tent Truss 24x12m (2).pdf": {
        "supplier": "VAN-RUBEN",
        "category": "TARIMAS & EVENTOS",
    },
}


def load_seed_mappings(path: str) -> dict:
    """Load and parse seed_mappings.json.

    Args:
        path: Path to the seed_mappings.json file.

    Returns:
        Parsed mappings dict with 'categories' and 'suppliers' keys.
    """
    if not os.path.exists(path):
        print(f"ERROR [ImportProducts]: seed_mappings.json not found: {path}")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        mappings = json.load(f)

    if not mappings.get("suppliers"):
        print("ERROR [ImportProducts]: No suppliers found in seed_mappings.json")
        sys.exit(1)

    if not mappings.get("categories"):
        print("ERROR [ImportProducts]: No categories found in seed_mappings.json")
        sys.exit(1)

    return mappings


def resolve_supplier_id(supplier_name: str, mappings: dict) -> Optional[str]:
    """Look up supplier UUID from seed mappings.

    Args:
        supplier_name: Canonical supplier name (e.g. "HUAYI").
        mappings: Parsed seed_mappings.json dict.

    Returns:
        UUID string if found, None otherwise.
    """
    return mappings["suppliers"].get(supplier_name)


def resolve_category_id(category_path: str, mappings: dict) -> Optional[str]:
    """Look up category UUID from seed mappings.

    Args:
        category_path: Category path (e.g. "BAÑOS/Griferías").
        mappings: Parsed seed_mappings.json dict.

    Returns:
        UUID string if found, None otherwise.
    """
    return mappings["categories"].get(category_path)


def process_file(
    file_path: str,
    supplier_id: str,
    category_id: Optional[str],
    dry_run: bool,
    verbose: bool,
) -> dict:
    """Process a single catalog file and import products.

    Args:
        file_path: Full path to the catalog file.
        supplier_id: Resolved supplier UUID string.
        category_id: Resolved category UUID string (or None).
        dry_run: If True, parse only without database writes.
        verbose: If True, print each product being imported.

    Returns:
        Dict with file, total, success, dupes, errors, error_details.
    """
    result = {
        "file": file_path,
        "total": 0,
        "success": 0,
        "dupes": 0,
        "errors": 0,
        "error_details": [],
    }

    ext = os.path.splitext(file_path)[1].lower()

    # Extract products based on file type
    if ext in (".xlsx", ".xls"):
        products, errors = extraction_service.process_excel(file_path)
    elif ext == ".pdf":
        products, errors = extraction_service.process_pdf(file_path)
    elif ext == ".docx":
        print(f"  WARN [ImportProducts]: Skipping .docx file: {file_path}")
        return result
    else:
        print(f"  WARN [ImportProducts]: Unsupported file type '{ext}': {file_path}")
        return result

    if errors:
        for err in errors:
            print(f"  WARN [ImportProducts]: Extraction error: {err}")

    if not products:
        print(f"  WARN [ImportProducts]: No products extracted from: {file_path}")
        return result

    # Convert ExtractedProduct to ProductCreateDTO
    product_dtos = []
    for ep in products:
        if not ep.name:
            if verbose:
                print(f"    SKIP: Product without name (sku={ep.sku})")
            continue

        # Build description with material appended
        description = ep.description or ""
        if ep.material:
            if description:
                description += f" | Material: {ep.material}"
            else:
                description = f"Material: {ep.material}"

        dto = ProductCreateDTO(
            sku=ep.sku if ep.sku else None,
            name=ep.name,
            description=description or None,
            supplier_id=supplier_id,
            category_id=category_id,
            status=ProductStatus.DRAFT,
            unit_cost=ep.price_fob_usd if ep.price_fob_usd is not None else Decimal("0.00"),
            unit_of_measure=ep.unit_of_measure or "piece",
            minimum_order_qty=ep.moq if ep.moq and ep.moq >= 1 else 1,
            dimensions=ep.dimensions,
            origin_country="China",
        )
        product_dtos.append(dto)

    result["total"] = len(product_dtos)

    if verbose:
        for dto in product_dtos:
            print(
                f"    PRODUCT: {dto.sku or '(auto)'} | {dto.name[:50]} | "
                f"${dto.unit_cost} | MOQ:{dto.minimum_order_qty}"
            )

    if dry_run:
        result["success"] = len(product_dtos)
        print(f"  DRY-RUN: Would import {len(product_dtos)} products")
        return result

    # Import via bulk_create_products
    bulk_result = product_service.bulk_create_products(product_dtos)

    result["success"] = bulk_result.success_count

    # Classify failures as duplicates vs other errors
    for failure in bulk_result.failed:
        error_msg = failure.error.lower()
        if "duplicate" in error_msg or "unique" in error_msg:
            result["dupes"] += 1
        else:
            result["errors"] += 1
        result["error_details"].append(
            f"[idx={failure.index}] sku={failure.sku}: {failure.error}"
        )

    return result


def print_summary_table(results: list[dict]) -> None:
    """Print a formatted summary table of import results.

    Args:
        results: List of per-file result dicts.
    """
    col_file = 55
    col_num = 10

    header = (
        f"{'File':<{col_file}} | "
        f"{'Products':>{col_num}} | "
        f"{'Success':>{col_num}} | "
        f"{'Dupes':>{col_num}} | "
        f"{'Errors':>{col_num}}"
    )
    separator = "-" * len(header)

    print(f"\n{separator}")
    print(header)
    print(separator)

    totals = {"total": 0, "success": 0, "dupes": 0, "errors": 0}

    for r in results:
        # Truncate long file paths
        file_display = r["file"]
        if len(file_display) > col_file:
            file_display = "..." + file_display[-(col_file - 3):]

        print(
            f"{file_display:<{col_file}} | "
            f"{r['total']:>{col_num}} | "
            f"{r['success']:>{col_num}} | "
            f"{r['dupes']:>{col_num}} | "
            f"{r['errors']:>{col_num}}"
        )

        totals["total"] += r["total"]
        totals["success"] += r["success"]
        totals["dupes"] += r["dupes"]
        totals["errors"] += r["errors"]

    print(separator)
    print(
        f"{'TOTAL':<{col_file}} | "
        f"{totals['total']:>{col_num}} | "
        f"{totals['success']:>{col_num}} | "
        f"{totals['dupes']:>{col_num}} | "
        f"{totals['errors']:>{col_num}}"
    )
    print(separator)


def write_results_json(
    results: list[dict],
    dry_run: bool,
    file_map_entries: dict,
) -> None:
    """Write detailed import results to JSON file.

    Args:
        results: List of per-file result dicts.
        dry_run: Whether this was a dry-run.
        file_map_entries: The FILE_MAP subset that was processed.
    """
    totals = {
        "files": len(results),
        "products": sum(r["total"] for r in results),
        "success": sum(r["success"] for r in results),
        "dupes": sum(r["dupes"] for r in results),
        "errors": sum(r["errors"] for r in results),
    }

    # Enrich results with supplier/category from FILE_MAP
    enriched_files = []
    for r in results:
        # Find the matching FILE_MAP entry by checking if the file path ends with the key
        supplier = ""
        category = ""
        for key, mapping in file_map_entries.items():
            if r["file"].endswith(key) or key in r["file"]:
                supplier = mapping["supplier"]
                category = mapping["category"]
                break

        enriched_files.append({
            "path": r["file"],
            "supplier": supplier,
            "category": category,
            "total": r["total"],
            "success": r["success"],
            "dupes": r["dupes"],
            "errors": r["errors"],
            "error_details": r["error_details"],
        })

    output = {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "dry_run": dry_run,
        "totals": totals,
        "files": enriched_files,
    }

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nINFO [ImportProducts]: Results written to {OUTPUT_FILE}")


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments.

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="Batch import products from supplier catalog files."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and validate without inserting into database.",
    )
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Process a single file only (relative path within FILE_MAP).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print each product being imported.",
    )
    return parser.parse_args()


def main() -> None:
    """Main execution flow for batch product import."""
    args = parse_args()

    print("=" * 60)
    print("  BATCH PRODUCT IMPORT")
    if args.dry_run:
        print("  MODE: DRY-RUN (no database writes)")
    print("=" * 60)

    # Resolve repo root (3 levels up from scripts/ directory)
    repo_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )

    # Load seed mappings
    print(f"\nINFO [ImportProducts]: Loading seed mappings from {MAPPINGS_FILE}")
    mappings = load_seed_mappings(MAPPINGS_FILE)
    print(
        f"  Suppliers: {len(mappings['suppliers'])} | "
        f"Categories: {len(mappings['categories'])}"
    )

    # Determine which files to process
    entries = FILE_MAP
    if args.file:
        if args.file in FILE_MAP:
            entries = {args.file: FILE_MAP[args.file]}
        else:
            print(f"ERROR [ImportProducts]: File not found in FILE_MAP: {args.file}")
            print("  Available files:")
            for key in sorted(FILE_MAP.keys()):
                print(f"    {key}")
            sys.exit(1)

    catalog_base = os.path.join(repo_root, CATALOG_BASE_PATH)
    print(f"INFO [ImportProducts]: Catalog base: {catalog_base}")
    print(f"INFO [ImportProducts]: Processing {len(entries)} files...\n")

    results = []

    for relative_path, mapping in entries.items():
        supplier_name = mapping["supplier"]
        category_path = mapping["category"]

        print(f"--- {relative_path}")
        print(f"    Supplier: {supplier_name} | Category: {category_path}")

        # Resolve supplier UUID
        supplier_id = resolve_supplier_id(supplier_name, mappings)
        if not supplier_id:
            print(f"  WARN [ImportProducts]: Supplier '{supplier_name}' not found in mappings, skipping")
            results.append({
                "file": relative_path,
                "total": 0,
                "success": 0,
                "dupes": 0,
                "errors": 0,
                "error_details": [f"Supplier not found: {supplier_name}"],
            })
            continue

        # Resolve category UUID
        category_id = resolve_category_id(category_path, mappings)
        if not category_id:
            print(f"  WARN [ImportProducts]: Category '{category_path}' not found in mappings, skipping")
            results.append({
                "file": relative_path,
                "total": 0,
                "success": 0,
                "dupes": 0,
                "errors": 0,
                "error_details": [f"Category not found: {category_path}"],
            })
            continue

        # Build full file path
        full_path = os.path.join(catalog_base, relative_path)
        if not os.path.exists(full_path):
            print(f"  WARN [ImportProducts]: File not found on disk: {full_path}")
            results.append({
                "file": relative_path,
                "total": 0,
                "success": 0,
                "dupes": 0,
                "errors": 0,
                "error_details": [f"File not found: {full_path}"],
            })
            continue

        # Process the file
        file_result = process_file(
            file_path=full_path,
            supplier_id=supplier_id,
            category_id=category_id,
            dry_run=args.dry_run,
            verbose=args.verbose,
        )
        # Store relative path for cleaner output
        file_result["file"] = relative_path
        results.append(file_result)

        print(
            f"    Result: {file_result['total']} extracted, "
            f"{file_result['success']} success, "
            f"{file_result['dupes']} dupes, "
            f"{file_result['errors']} errors"
        )

    # Print summary table
    print_summary_table(results)

    # Write results JSON
    write_results_json(results, args.dry_run, entries)

    # Final summary
    total_products = sum(r["total"] for r in results)
    total_success = sum(r["success"] for r in results)
    total_dupes = sum(r["dupes"] for r in results)
    total_errors = sum(r["errors"] for r in results)

    print(
        f"\nINFO [ImportProducts]: Done. "
        f"{total_products} products extracted, "
        f"{total_success} imported, "
        f"{total_dupes} duplicates, "
        f"{total_errors} errors"
    )


if __name__ == "__main__":
    main()
