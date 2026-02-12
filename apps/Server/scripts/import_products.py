#!/usr/bin/env python3
"""Batch import script for supplier catalog files into the products table.

Processes Excel and PDF catalog files using the extraction service,
converts extracted products to ProductCreateDTO objects with correct
supplier and category assignments, and bulk-inserts them via the
product service.

Usage:
    cd apps/Server
    python -m scripts.import_products              # Full import
    python -m scripts.import_products --dry-run     # Preview only
    python -m scripts.import_products --file <path> # Single file
    python -m scripts.import_products --verbose     # Detailed output
"""

import argparse
import json
import os
import sys
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.extraction_dto import ExtractedProduct
from app.models.kompass_dto import ProductCreateDTO
from app.services.extraction_service import extraction_service
from app.services.product_service import product_service

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CATALOG_BASE_PATH = os.path.join(
    "Requirements_Gathering", "Sourcing", "Data", "PROVEEDORES - CATALOGOS"
)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
RESULTS_FILE = os.path.join(OUTPUT_DIR, "import_results.json")
MAPPINGS_FILE = os.path.join(OUTPUT_DIR, "seed_mappings.json")

# ---------------------------------------------------------------------------
# FILE_MAP: catalog file -> supplier name + category path
# ---------------------------------------------------------------------------

FILE_MAP: dict[str, dict[str, str]] = {
    # BAÑOS/GRIFERIASS
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
    # BAÑOS/GRIFERIAS_ducha_baño_cocina
    "BAÑOS/GRIFERIAS_ducha _baño _cocina/LAYASDUN/Quote from Layasdun 20251201.pdf": {
        "supplier": "LAYASDUN",
        "category": "BAÑOS/Griferías",
    },
    # BAÑOS/LAVAMANOS
    "BAÑOS/LAVAMANOS/Quotation from Conrazzo.pdf": {
        "supplier": "CONRAZZO",
        "category": "BAÑOS/Lavamanos",
    },
    # BAÑOS/SANITARIOS Y MUEBLES DE BAÑO
    "BAÑOS/SANITARIOS Y MUEBLES DE BAÑO/Price list From BATH STORE- TAUSU.xlsx": {
        "supplier": "BATH STORE-TAUSU",
        "category": "BAÑOS/Sanitarios y Muebles de Baño",
    },
    # BAÑOS (root-level file)
    "BAÑOS/STAINLESS.xlsx": {
        "supplier": "CONRAZZO",
        "category": "BAÑOS",
    },
    # DECK - FACHADAS
    "DECK - FACHADAS/MEXY TECH - DECK/MexyTech catalog (1).pdf": {
        "supplier": "MEXY TECH",
        "category": "DECK - FACHADAS",
    },
    "DECK - FACHADAS/MEXY TECH - DECK/REQUIREMENT FORMAT (3).xlsx": {
        "supplier": "MEXY TECH",
        "category": "DECK - FACHADAS",
    },
    # DISPENSADORES
    "DISPENSADORES/Quotation LA20251129K.pdf": {
        "supplier": "LAYASDUN",
        "category": "DISPENSADORES",
    },
    # DOTACIÓN DE COCINA
    "DOTACIÓN DE COCINA/KITCHENWARE -CHINA.xlsx": {
        "supplier": "GEORGE",
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
    # ESPEJOS
    "ESPEJOS/LUXDREAM/2026 Luxdream Led Mirror E-Brochure.pdf": {
        "supplier": "LUXDREAM",
        "category": "ESPEJOS",
    },
    "ESPEJOS/LUXDREAM/S-Luxdream Led Bathroom Mirror Price List.pdf": {
        "supplier": "LUXDREAM",
        "category": "ESPEJOS",
    },
    # ILUMINACIÓN
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
    # MOBILIARIO/CAMAS
    "MOBILIARIO/CAMAS_LEIZE/LEIZI Quotation for Aldjandro (1).pdf": {
        "supplier": "LEIZI",
        "category": "MOBILIARIO/Camas",
    },
    "MOBILIARIO/CAMAS_LEIZE/LEIZI-Hotel Mattress Catalog 202508.pdf": {
        "supplier": "LEIZI",
        "category": "MOBILIARIO/Camas",
    },
    # MOBILIARIO/MESAS DE NOCHE
    "MOBILIARIO/MESAS DE NOCHE USB/NTFT Yifuyuan Bedside table Quotation（2025.9)(1).xlsx": {
        "supplier": "NTFT YIFUYUAN",
        "category": "MOBILIARIO/Mesas de Noche",
    },
    # MOBILIARIO general
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
    # ONE STOP SHOP
    "ONE STOP SHOP/GEORGE/Copy of Shamsa tile quotation 2025.11.30.xlsx": {
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
    "ONE STOP SHOP/GEORGE/George - cocina y closets quotation.xlsx": {
        "supplier": "GEORGE",
        "category": "ONE STOP SHOP",
    },
    "ONE STOP SHOP/PA HOME/1. PA Quotation for Kitchens & closets-2025.12.05.pdf": {
        "supplier": "PA HOME",
        "category": "ONE STOP SHOP",
    },
    # PISOS - GUARDAESCOBAS
    "PISOS - GUARDAESCOBAS/CU MATERIALS/Precios CU Materiales seleccionados.xlsx": {
        "supplier": "CU MATERIALS",
        "category": "PISOS - GUARDAESCOBAS",
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
    # REVESTIMIENTOS
    "REVESTIMIENTOS/CU MATERIALS/Precios CU Materiales seleccionados.xlsx": {
        "supplier": "CU MATERIALS",
        "category": "REVESTIMIENTOS",
    },
    "REVESTIMIENTOS/WUXI KAIZE _ PANEL EXT - INT/Wuxi Kaize Indoor & Outdoor Panel Price List – FOB Prices.xlsx": {
        "supplier": "WUXI KAIZE",
        "category": "REVESTIMIENTOS",
    },
    # TARIMAS & EVENTOS
    "TARIMAS & EVENTOS/4 pillar Van-Ruben Tent Truss 24x12m (2).pdf": {
        "supplier": "VAN-RUBEN",
        "category": "TARIMAS & EVENTOS",
    },
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def load_seed_mappings() -> Optional[dict]:
    """Load and validate seed_mappings.json.

    Returns:
        Parsed mappings dict or None if file is missing/invalid.
    """
    if not os.path.exists(MAPPINGS_FILE):
        print(f"ERROR [ImportProducts]: seed_mappings.json not found at {MAPPINGS_FILE}")
        print("  Run 'python -m scripts.seed_all' first to generate mappings.")
        return None

    with open(MAPPINGS_FILE, "r", encoding="utf-8") as f:
        mappings = json.load(f)

    required_keys = ["suppliers", "categories"]
    for key in required_keys:
        if key not in mappings:
            print(f"ERROR [ImportProducts]: Missing '{key}' section in seed_mappings.json")
            return None

    print("INFO [ImportProducts]: Loaded seed_mappings.json")
    print(f"  Suppliers: {len(mappings['suppliers'])} mapped")
    print(f"  Categories: {len(mappings['categories'])} mapped")
    return mappings


def resolve_supplier_id(supplier_name: str, mappings: dict) -> Optional[str]:
    """Look up supplier UUID from seed mappings.

    Args:
        supplier_name: Canonical supplier name (e.g. "HUAYI")
        mappings: Loaded seed_mappings dict

    Returns:
        UUID string or None if not found.
    """
    return mappings.get("suppliers", {}).get(supplier_name)


def resolve_category_id(category_path: str, mappings: dict) -> Optional[str]:
    """Look up category UUID from seed mappings.

    Args:
        category_path: Category path (e.g. "BAÑOS/Griferías")
        mappings: Loaded seed_mappings dict

    Returns:
        UUID string or None if not found.
    """
    return mappings.get("categories", {}).get(category_path)


def convert_to_product_dto(
    extracted: ExtractedProduct,
    supplier_id: str,
    category_id: Optional[str],
) -> Optional[ProductCreateDTO]:
    """Convert an ExtractedProduct to a ProductCreateDTO.

    Args:
        extracted: Product data from extraction service
        supplier_id: Resolved supplier UUID string
        category_id: Resolved category UUID string (or None)

    Returns:
        ProductCreateDTO or None if the product has no name.
    """
    product_name = (extracted.name or "").strip()
    if not product_name:
        # Try building name from material (e.g. HONGYU Collection: "Statuario")
        if extracted.material and extracted.material.strip():
            product_name = extracted.material.strip()
        # Try first line of description
        elif extracted.description and extracted.description.strip():
            first_line = extracted.description.strip().split("\n")[0][:200]
            product_name = first_line
        # Last resort: use SKU
        elif extracted.sku and extracted.sku.strip():
            product_name = extracted.sku.strip()
        else:
            return None

    # Build description with material appended
    description = extracted.description or ""
    if extracted.material:
        if description:
            description += f"\n\nMaterial: {extracted.material}"
        else:
            description = f"Material: {extracted.material}"

    return ProductCreateDTO(
        name=product_name,
        sku=extracted.sku,
        description=description or None,
        supplier_id=UUID(supplier_id),
        category_id=UUID(category_id) if category_id else None,
        unit_cost=extracted.price_fob_usd if extracted.price_fob_usd is not None else Decimal("0.00"),
        unit_of_measure=extracted.unit_of_measure or "piece",
        minimum_order_qty=extracted.moq if extracted.moq is not None else 1,
        dimensions=extracted.dimensions,
        origin_country="China",
        currency="USD",
    )


def process_file(
    relative_path: str,
    supplier_name: str,
    category_path: str,
    mappings: dict,
    args: argparse.Namespace,
) -> dict[str, Any]:
    """Process a single catalog file end-to-end.

    Args:
        relative_path: File path relative to CATALOG_BASE_PATH
        supplier_name: Canonical supplier name
        category_path: Category path for seed mappings lookup
        mappings: Loaded seed_mappings dict
        args: CLI arguments

    Returns:
        Result dict with counts and error details.
    """
    result: dict[str, Any] = {
        "file": relative_path,
        "supplier": supplier_name,
        "category": category_path,
        "extracted": 0,
        "success": 0,
        "duplicates": 0,
        "errors": 0,
        "error_details": [],
        "skipped_products": [],
    }

    # Resolve supplier UUID
    supplier_id = resolve_supplier_id(supplier_name, mappings)
    if not supplier_id:
        msg = f"Supplier '{supplier_name}' not found in seed mappings"
        print(f"  WARN [ImportProducts]: {msg} — skipping file")
        result["error_details"].append(msg)
        result["errors"] = 1
        return result

    # Resolve category UUID
    category_id = resolve_category_id(category_path, mappings)
    if not category_id:
        msg = f"Category '{category_path}' not found in seed mappings"
        print(f"  WARN [ImportProducts]: {msg} — skipping file")
        result["error_details"].append(msg)
        result["errors"] = 1
        return result

    # Resolve full file path (relative to repo root)
    repo_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
    full_path = os.path.join(repo_root, CATALOG_BASE_PATH, relative_path)

    if not os.path.exists(full_path):
        msg = f"File not found: {full_path}"
        print(f"  WARN [ImportProducts]: {msg} — skipping")
        result["error_details"].append(msg)
        result["errors"] = 1
        return result

    # Extract products
    ext = os.path.splitext(relative_path)[1].lower()
    try:
        if ext == ".pdf":
            products, errors = extraction_service.process_pdf(full_path)
        else:
            # .xlsx, .xls handled by process_excel
            products, errors = extraction_service.process_excel(full_path)
    except Exception as e:
        msg = f"Extraction failed: {e}"
        print(f"  ERROR [ImportProducts]: {msg}")
        result["error_details"].append(msg)
        result["errors"] = 1
        return result

    if errors:
        for err in errors:
            print(f"  WARN [ImportProducts]: Extraction warning: {err}")

    result["extracted"] = len(products)

    if not products:
        print(f"  INFO [ImportProducts]: No products extracted from {relative_path}")
        return result

    # Convert to ProductCreateDTO
    dtos: list[ProductCreateDTO] = []
    for idx, extracted in enumerate(products):
        dto = convert_to_product_dto(extracted, supplier_id, category_id)
        if dto is None:
            skip_msg = f"Product with no name at index {idx}"
            result["skipped_products"].append(skip_msg)
            if args.verbose:
                print(f"    SKIP: {skip_msg}")
            continue

        if args.verbose:
            price_str = f"${dto.unit_cost}" if dto.unit_cost else "N/A"
            print(f"    Product: {dto.name[:60]:<60} SKU: {dto.sku or 'auto':<20} Price: {price_str}")

        dtos.append(dto)

    if not dtos:
        print(f"  INFO [ImportProducts]: No valid products to import from {relative_path}")
        return result

    # Bulk create (or dry-run)
    if args.dry_run:
        print(f"  DRY-RUN: Would import {len(dtos)} products from {relative_path}")
        result["success"] = len(dtos)
        return result

    bulk_result = product_service.bulk_create_products(dtos)
    result["success"] = bulk_result.success_count

    # Categorize failures: duplicates vs other errors
    for fail in bulk_result.failed:
        error_lower = fail.error.lower()
        if "unique" in error_lower or "duplicate" in error_lower:
            result["duplicates"] += 1
            if args.verbose:
                print(f"    DUPE: {fail.sku or f'index {fail.index}'} — {fail.error}")
        else:
            result["errors"] += 1
            result["error_details"].append(f"Index {fail.index}: {fail.error}")
            print(f"  ERROR [ImportProducts]: {fail.sku or f'index {fail.index}'} — {fail.error}")

    return result


# ---------------------------------------------------------------------------
# Output functions
# ---------------------------------------------------------------------------


def print_summary_table(results: list[dict[str, Any]]) -> None:
    """Print a formatted summary table of import results."""
    # Column widths
    file_w = max(len("File"), max((len(r["file"]) for r in results), default=4))
    file_w = min(file_w, 70)  # Cap width

    print("\n" + "=" * (file_w + 48))
    print(f"  {'File':<{file_w}}  {'Extracted':>9}  {'Success':>7}  {'Dupes':>5}  {'Errors':>6}")
    print("-" * (file_w + 48))

    total_extracted = 0
    total_success = 0
    total_dupes = 0
    total_errors = 0

    for r in results:
        fname = r["file"]
        if len(fname) > file_w:
            fname = "..." + fname[-(file_w - 3):]
        print(
            f"  {fname:<{file_w}}  {r['extracted']:>9}  {r['success']:>7}  "
            f"{r['duplicates']:>5}  {r['errors']:>6}"
        )
        total_extracted += r["extracted"]
        total_success += r["success"]
        total_dupes += r["duplicates"]
        total_errors += r["errors"]

    print("-" * (file_w + 48))
    print(
        f"  {'TOTAL':<{file_w}}  {total_extracted:>9}  {total_success:>7}  "
        f"{total_dupes:>5}  {total_errors:>6}"
    )
    print("=" * (file_w + 48))


def write_results_json(results: list[dict[str, Any]]) -> None:
    """Write detailed import results to JSON file."""
    total_extracted = sum(r["extracted"] for r in results)
    total_success = sum(r["success"] for r in results)
    total_dupes = sum(r["duplicates"] for r in results)
    total_errors = sum(r["errors"] for r in results)

    output = {
        "summary": {
            "total_files": len(results),
            "total_products": total_extracted,
            "total_success": total_success,
            "total_dupes": total_dupes,
            "total_errors": total_errors,
        },
        "files": results,
    }

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nINFO [ImportProducts]: Results written to {RESULTS_FILE}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Orchestrate the batch product import."""
    parser = argparse.ArgumentParser(
        description="Batch import products from supplier catalog files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Extract and convert products but skip database writes",
    )
    parser.add_argument(
        "--file",
        type=str,
        metavar="PATH",
        help="Process a single file from FILE_MAP (path relative to catalog base)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print each product name, SKU, and price as it is processed",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  BATCH PRODUCT IMPORT")
    if args.dry_run:
        print("  MODE: DRY-RUN (no database writes)")
    print("=" * 60)

    # Load seed mappings
    mappings = load_seed_mappings()
    if mappings is None:
        sys.exit(1)

    # Determine which files to process
    if args.file:
        if args.file not in FILE_MAP:
            print(f"ERROR [ImportProducts]: File '{args.file}' not found in FILE_MAP")
            print("  Available files:")
            for key in sorted(FILE_MAP.keys()):
                print(f"    {key}")
            sys.exit(1)
        files_to_process = {args.file: FILE_MAP[args.file]}
    else:
        files_to_process = FILE_MAP

    results: list[dict[str, Any]] = []

    for idx, (rel_path, info) in enumerate(files_to_process.items(), 1):
        supplier = info["supplier"]
        category = info["category"]
        total = len(files_to_process)

        print(f"\n--- [{idx}/{total}] {rel_path}")
        print(f"    Supplier: {supplier} | Category: {category}")

        result = process_file(rel_path, supplier, category, mappings, args)
        results.append(result)

        print(
            f"    Result: {result['extracted']} extracted, "
            f"{result['success']} success, "
            f"{result['duplicates']} dupes, "
            f"{result['errors']} errors"
        )

    # Summary
    print_summary_table(results)
    write_results_json(results)

    print("\nINFO [ImportProducts]: Batch import complete.")


if __name__ == "__main__":
    main()
