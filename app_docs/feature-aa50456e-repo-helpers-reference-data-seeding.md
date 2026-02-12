# Repository Helpers and Reference Data Seeding Scripts

**ADW ID:** aa50456e
**Date:** 2026-02-12
**Specification:** specs/issue-122-adw-aa50456e-sdlc_planner-repo-helpers-reference-data-seeding.md

## Overview

Adds `get_by_name()` and `get_by_name_and_parent()` helper methods to the repository layer and creates four Python seeding scripts that populate categories, suppliers, and HS codes from real supplier data. This is Phase 1, Issue 2 of 5 in the Supplier Catalog Data pipeline, enabling downstream batch product imports (SCD-003) with correct supplier-category-tariff mappings.

## What Was Built

- **CategoryRepository.get_by_name_and_parent()** — Case-insensitive category lookup by name and parent_id using PostgreSQL `IS NOT DISTINCT FROM` for NULL-safe comparison
- **SupplierRepository.get_by_name()** — Case-insensitive supplier lookup by name for deduplication
- **seed_categories.py** — Seeds ~20 categories (11 root + subcategories) from a hardcoded tree matching the supplier catalog folder structure
- **seed_suppliers.py** — Seeds up to 25 suppliers from the Canton Fair master directory Excel file with fuzzy name matching
- **seed_hs_codes.py** — Seeds 15 HS codes with Colombian duty rates mapped to product categories
- **seed_all.py** — Unified runner that orchestrates all three scripts and outputs `seed_mappings.json`
- **Unit tests** — 11 tests covering both new repository helper methods

## Technical Implementation

### Files Modified

- `apps/Server/app/repository/kompass_repository.py`: Added `CategoryRepository.get_by_name_and_parent()` (after line 535) and `SupplierRepository.get_by_name()` (after line 1630) — +61 lines
- `.gitignore`: Added `apps/Server/scripts/output/` entry for seed output directory

### New Files

- `apps/Server/scripts/__init__.py`: Package init for scripts module
- `apps/Server/scripts/seed_categories.py`: Category tree seeding (105 lines) — hardcoded `CATEGORY_TREE` dict with 11 root categories and their subcategories
- `apps/Server/scripts/seed_suppliers.py`: Supplier seeding from Excel (255 lines) — reads Canton Fair Excel, fuzzy-matches against 25 known supplier names, extracts contact info
- `apps/Server/scripts/seed_hs_codes.py`: HS code seeding (150 lines) — 15 hardcoded HS codes with Colombian duty rates (5-15%)
- `apps/Server/scripts/seed_all.py`: Unified runner (93 lines) — orchestrates all three seeders, writes combined `seed_mappings.json`
- `apps/Server/tests/test_kompass/test_repository_helpers.py`: Unit tests (273 lines) — 6 tests for category helper, 5 tests for supplier helper

### Key Changes

- **Idempotent seeding pattern**: All scripts use check-then-create via repository helpers — running twice produces no duplicates
- **Case-insensitive matching**: Both new repository methods use `LOWER(name) = LOWER(%s)` for case-insensitive lookups
- **NULL-safe parent comparison**: `CategoryRepository.get_by_name_and_parent()` uses PostgreSQL's `IS NOT DISTINCT FROM` to correctly handle NULL parent_id for root categories
- **Fuzzy supplier matching**: `seed_suppliers.py` normalizes names (strip, uppercase, collapse spaces) and tries exact match, then startswith/containment matching against the Excel data
- **Mappings output**: `seed_all.py` writes `seed_mappings.json` with UUID mappings for categories, suppliers, and HS codes — consumed by SCD-003 (Batch Product Import)

## How to Use

1. Ensure the backend virtual environment is activated:
   ```bash
   cd apps/Server
   source .venv/bin/activate
   ```

2. **Seed all reference data** (recommended):
   ```bash
   python -m scripts.seed_all
   ```
   This runs categories → suppliers → HS codes in sequence and writes `scripts/output/seed_mappings.json`.

3. **Seed individually** (optional):
   ```bash
   python -m scripts.seed_categories
   python -m scripts.seed_suppliers [optional-excel-path]
   python -m scripts.seed_hs_codes
   ```

4. **Custom Excel path** for supplier seeding:
   ```bash
   python -m scripts.seed_all /path/to/custom-excel.xlsx
   ```

5. The output `seed_mappings.json` file will be at `apps/Server/scripts/output/seed_mappings.json` with this structure:
   ```json
   {
     "categories": {"BAÑOS": "uuid", "BAÑOS/Griferías": "uuid", ...},
     "suppliers": {"BWBYONE": "uuid", "CONRAZZO": "uuid", ...},
     "hs_codes": {"6910.10": "uuid", "7324.90": "uuid", ...}
   }
   ```

## Configuration

- **Canton Fair Excel path**: Default is `Requirements_Gathering/Sourcing/Data/PROVEEDORES - CATALOGOS/CANTON FAIR _OCT _2025/DIRECTORIO PROVEEDORES CANTON FAIR _OCT_2025.xlsx` relative to repo root. Override via CLI argument.
- **Excel sheet**: Scripts look for a `"BASE MASTER"` sheet, falling back to the first sheet if not found.
- **No new dependencies**: Uses `openpyxl` (already in requirements.txt) and Python stdlib modules.

## Testing

Run repository helper unit tests:
```bash
cd apps/Server
.venv/bin/pytest tests/test_kompass/test_repository_helpers.py -v
```

Tests cover:
- Finding root categories (parent_id=None) and child categories (parent_id=UUID)
- Finding existing suppliers by name
- Returning None when not found
- Case-insensitive query verification
- Database connection failure handling
- Database exception handling

## Notes

- **Idempotency**: All scripts are safe to run multiple times — existing records are skipped, not duplicated
- **Pipeline status**: Seeded suppliers get the DB default `pipeline_status = "contacted"` (not `"quoted"`) since `SupplierRepository.create()` doesn't accept pipeline_status as a parameter
- **Parallel with SCD-001**: This feature only adds new methods and files — no conflicts with Excel Extraction Enhancements
- **seed_mappings.json**: Environment-specific (contains UUIDs), added to `.gitignore` via `apps/Server/scripts/output/`
- **Category tree**: 11 roots (BAÑOS, DECK-FACHADAS, DISPENSADORES, DOTACIÓN DE COCINA, ESPEJOS, ILUMINACIÓN, MOBILIARIO, ONE STOP SHOP, PISOS-GUARDAESCOBAS, REVESTIMIENTOS, TARIMAS & EVENTOS) with 9 subcategories
