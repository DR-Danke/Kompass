#!/usr/bin/env python3
"""Unified seed runner that executes all seeding scripts and writes seed_mappings.json."""

import json
import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.seed_categories import seed_categories
from scripts.seed_suppliers import seed_suppliers, DEFAULT_EXCEL_PATH
from scripts.seed_hs_codes import seed_hs_codes

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "seed_mappings.json")


def seed_all(excel_path: str) -> dict:
    """Run all seeding scripts in sequence and write combined mappings.

    Args:
        excel_path: Path to the Canton Fair directory Excel file.

    Returns:
        Combined mappings dict with categories, suppliers, and hs_codes sections.
    """
    print("=" * 60)
    print("  SEED ALL: Reference Data Seeding")
    print("=" * 60)

    # 1. Categories
    print("\n--- Seeding Categories ---")
    cat_result = seed_categories()
    print(
        f"  Categories: {cat_result['created']} created, "
        f"{cat_result['skipped']} skipped"
    )

    # 2. Suppliers
    print("\n--- Seeding Suppliers ---")
    sup_result = seed_suppliers(excel_path)
    print(
        f"  Suppliers: {sup_result['created']} created, "
        f"{sup_result['skipped']} skipped"
    )
    if sup_result.get("not_found_in_excel"):
        print(
            f"  Not found in Excel: {', '.join(sup_result['not_found_in_excel'])}"
        )

    # 3. HS Codes
    print("\n--- Seeding HS Codes ---")
    hs_result = seed_hs_codes()
    print(
        f"  HS Codes: {hs_result['created']} created, "
        f"{hs_result['skipped']} skipped"
    )

    # Combine mappings
    combined = {
        "categories": cat_result["mappings"],
        "suppliers": sup_result["mappings"],
        "hs_codes": hs_result["mappings"],
    }

    # Write to output file
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)

    print("\n--- Summary ---")
    print(f"  Categories: {len(cat_result['mappings'])} mapped")
    print(f"  Suppliers:  {len(sup_result['mappings'])} mapped")
    print(f"  HS Codes:   {len(hs_result['mappings'])} mapped")
    print(f"  Output:     {OUTPUT_FILE}")
    print("=" * 60)

    return combined


if __name__ == "__main__":
    # Accept custom Excel path from CLI or use default
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        # Resolve relative to repo root (3 levels up from scripts/)
        repo_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )
        path = os.path.join(repo_root, DEFAULT_EXCEL_PATH)

    seed_all(path)
