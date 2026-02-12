# Feature: Batch Product Import from Supplier Catalog Files

## Metadata
issue_number: `123`
adw_id: `ad808429`
issue_json: ``

## Feature Description
Create a batch import script that processes all 52 supplier catalog files (Excel and PDF) using the enhanced extraction service introduced in SCD-001. The script loads seed mappings from SCD-002 to resolve supplier UUIDs and category UUIDs, then iterates through a hardcoded FILE_MAP that maps each catalog file to its supplier and category. For each file, it extracts products via `extraction_service.process_excel()` or `extraction_service.process_pdf()`, converts them to `ProductCreateDTO` objects with proper assignments, and bulk-inserts them via `product_service.bulk_create_products()`. The script provides a summary table, detailed JSON output, and supports `--dry-run`, `--file`, and `--verbose` CLI flags.

## User Story
As a Kompass system administrator
I want to run a batch import script that processes all 52 supplier catalog files and populates the products table
So that the product database is seeded with hundreds of real products from actual supplier catalogs, enabling quotation automation

## Problem Statement
After seeding reference data (suppliers, categories, HS codes) in SCD-002, the products table remains empty. The 52 supplier catalog files in various formats (Excel, PDF) need to be processed and their product data imported with correct supplier and category assignments. Manual entry of hundreds of products is impractical; an automated batch script is needed.

## Solution Statement
Create `apps/Server/scripts/import_products.py` — a standalone CLI script that:
1. Loads `seed_mappings.json` to resolve supplier names → UUIDs and category paths → UUIDs
2. Uses a hardcoded `FILE_MAP` dictionary mapping ~50 catalog file paths to their supplier and category
3. Processes each file through the extraction service (Excel or PDF)
4. Converts `ExtractedProduct` objects to `ProductCreateDTO` with correct `supplier_id`, `category_id`, `unit_of_measure`, and material-appended descriptions
5. Calls `product_service.bulk_create_products()` per file with graceful duplicate handling
6. Prints a formatted summary table and writes detailed results to `import_results.json`

## Relevant Files
Use these files to implement the feature:

### Existing Files
- `apps/Server/scripts/seed_all.py` — Reference for script patterns: sys.path setup, output directory, JSON writing, CLI argument handling
- `apps/Server/scripts/seed_suppliers.py` — Reference for supplier name normalization, `KNOWN_SUPPLIERS` list (25 canonical names), repo root path resolution
- `apps/Server/scripts/seed_categories.py` — Reference for `CATEGORY_TREE` structure (11 root categories with subcategories), category path format (`ROOT/Child`)
- `apps/Server/scripts/__init__.py` — Exists (empty), enables `python -m scripts.import_products`
- `apps/Server/app/services/extraction_service.py` — Singleton `extraction_service` at line 957. Methods: `process_excel(file_path) -> Tuple[List[ExtractedProduct], List[str]]` and `process_pdf(file_path) -> Tuple[List[ExtractedProduct], List[str]]`
- `apps/Server/app/services/product_service.py` — Singleton `product_service` at line 521. Method: `bulk_create_products(products: List[ProductCreateDTO]) -> BulkCreateResponseDTO`
- `apps/Server/app/models/extraction_dto.py` — `ExtractedProduct` model with fields: `sku`, `name`, `description`, `price_fob_usd`, `moq`, `dimensions`, `material`, `suggested_category`, `image_urls`, `confidence_score`, `raw_text`, `source_page`, `unit_of_measure`
- `apps/Server/app/models/kompass_dto.py` — `ProductCreateDTO` (line 642): requires `name` and `supplier_id`; optional `sku`, `category_id`, `description`, `unit_cost`, `unit_of_measure`, `minimum_order_qty`, `dimensions`, `status` (defaults to `draft`). Also `BulkCreateResponseDTO` and `BulkCreateErrorDTO`
- `apps/Server/database/schema.sql` — `products` table: `sku VARCHAR(100) NOT NULL UNIQUE` (global unique constraint, NOT per-supplier)
- `.gitignore` — Already includes `apps/Server/scripts/output/` pattern
- `app_docs/feature-aa50456e-repo-helpers-reference-data-seeding.md` — Documentation for reference data seeding patterns and seed_mappings.json structure

### New Files
- `apps/Server/scripts/import_products.py` — The batch import script (main deliverable)

## Implementation Plan
### Phase 1: Foundation
- Build the FILE_MAP dictionary by mapping all 52 catalog files to their supplier names and category paths
- Set up script structure following existing patterns from `seed_all.py` and `seed_suppliers.py`
- Implement seed mappings loader and UUID resolution functions

### Phase 2: Core Implementation
- Implement the main processing loop: iterate FILE_MAP, call extraction service, convert to ProductCreateDTO, call bulk_create_products
- Handle field mapping: `ExtractedProduct` → `ProductCreateDTO` (price_fob_usd → unit_cost, moq → minimum_order_qty, material → appended to description)
- Implement deduplication tracking: detect "unique constraint" or "duplicate" in error messages to count dupes separately
- Add CLI flags: `--dry-run`, `--file`, `--verbose` via `argparse`

### Phase 3: Integration
- Implement summary table output (formatted columns with per-file and total counts)
- Write detailed results to `scripts/output/import_results.json`
- Verify the script runs correctly with `python -m scripts.import_products` from `apps/Server/`

## Step by Step Tasks

### Step 1: Read reference documentation
- Read `app_docs/feature-aa50456e-repo-helpers-reference-data-seeding.md` to understand seed patterns and mappings structure
- Read `apps/Server/scripts/seed_all.py`, `seed_suppliers.py`, and `seed_categories.py` to understand existing script conventions

### Step 2: Create the import_products.py script
- Create `apps/Server/scripts/import_products.py` with the following structure:

**Constants and Configuration:**
```python
CATALOG_BASE_PATH = os.path.join(
    "Requirements_Gathering", "Sourcing", "Data", "PROVEEDORES - CATALOGOS"
)
```

**FILE_MAP dictionary** — Map all ~50 catalog files (relative to `CATALOG_BASE_PATH`) to their supplier name and category path. Based on the actual file listing:

```python
FILE_MAP = {
    # BAÑOS/GRIFERIASS
    "BAÑOS/GRIFERIASS/HUAYI/HUAYI (1).xlsx": {
        "supplier": "HUAYI",
        "category": "BAÑOS/Griferías"
    },
    "BAÑOS/GRIFERIASS/JVK/Quotation JVK.xlsx": {
        "supplier": "JVK",
        "category": "BAÑOS/Griferías"
    },
    "BAÑOS/GRIFERIASS/LAYASDUN/LAYASDUN Quotation.xlsx": {
        "supplier": "LAYASDUN",
        "category": "BAÑOS/Griferías"
    },
    "BAÑOS/GRIFERIASS/PINLSLON BUILDING MATERIALS/2026 Pinslon price list-faucets (2).pdf": {
        "supplier": "PINLSLON",
        "category": "BAÑOS/Griferías"
    },
    # BAÑOS/GRIFERIAS_ducha_baño_cocina
    "BAÑOS/GRIFERIAS_ducha _baño _cocina/LAYASDUN/Quote from Layasdun 20251201.pdf": {
        "supplier": "LAYASDUN",
        "category": "BAÑOS/Griferías"
    },
    # BAÑOS/LAVAMANOS
    "BAÑOS/LAVAMANOS/Quotation from Conrazzo.pdf": {
        "supplier": "CONRAZZO",
        "category": "BAÑOS/Lavamanos"
    },
    # BAÑOS/SANITARIOS Y MUEBLES DE BAÑO
    "BAÑOS/SANITARIOS Y MUEBLES DE BAÑO/Price list From BATH STORE- TAUSU.xlsx": {
        "supplier": "BATH STORE-TAUSU",
        "category": "BAÑOS/Sanitarios y Muebles de Baño"
    },
    # BAÑOS (root-level file)
    "BAÑOS/STAINLESS.xlsx": {
        "supplier": "CONRAZZO",
        "category": "BAÑOS"
    },
    # DECK - FACHADAS
    "DECK - FACHADAS/MEXY TECH - DECK/MexyTech catalog (1).pdf": {
        "supplier": "MEXY TECH",
        "category": "DECK - FACHADAS"
    },
    "DECK - FACHADAS/MEXY TECH - DECK/REQUIREMENT FORMAT (3).xlsx": {
        "supplier": "MEXY TECH",
        "category": "DECK - FACHADAS"
    },
    # DISPENSADORES
    "DISPENSADORES/Quotation LA20251129K.pdf": {
        "supplier": "LAYASDUN",
        "category": "DISPENSADORES"
    },
    # DOTACIÓN DE COCINA
    "DOTACIÓN DE COCINA/KITCHENWARE -CHINA.xlsx": {
        "supplier": "GEORGE",
        "category": "DOTACIÓN DE COCINA"
    },
    "DOTACIÓN DE COCINA/MAYORISTA COLOMBIA/COT 2026-06 (1).pdf": {
        "supplier": "MAYORISTA COLOMBIA",
        "category": "DOTACIÓN DE COCINA"
    },
    "DOTACIÓN DE COCINA/WIREKING_ DOT COCINA/Wireking Quotation - Kompasstrading -2025-12-01.xlsx": {
        "supplier": "WIREKING",
        "category": "DOTACIÓN DE COCINA"
    },
    # ESPEJOS
    "ESPEJOS/LUXDREAM/2026 Luxdream Led Mirror E-Brochure.pdf": {
        "supplier": "LUXDREAM",
        "category": "ESPEJOS"
    },
    "ESPEJOS/LUXDREAM/S-Luxdream Led Bathroom Mirror Price List.pdf": {
        "supplier": "LUXDREAM",
        "category": "ESPEJOS"
    },
    # ILUMINACIÓN
    "ILUMINACIÓN/GEORGE/Precios Iluminación - George.xlsx": {
        "supplier": "GEORGE",
        "category": "ILUMINACIÓN"
    },
    "ILUMINACIÓN/LED_ BWBYONE/BYONE BDEXPO CATALOG 2025.12 (2).pdf": {
        "supplier": "BWBYONE",
        "category": "ILUMINACIÓN"
    },
    "ILUMINACIÓN/LED_ BWBYONE/price list of  track light from Bwbyone Sophia.pdf": {
        "supplier": "BWBYONE",
        "category": "ILUMINACIÓN"
    },
    "ILUMINACIÓN/LED_ BWBYONE/price list of downlight from Bwbyone Sophia.pdf": {
        "supplier": "BWBYONE",
        "category": "ILUMINACIÓN"
    },
    "ILUMINACIÓN/LED_ BWBYONE/price list of panel light from Bwbyone Sophia(经济款）  2026.1.3.pdf": {
        "supplier": "BWBYONE",
        "category": "ILUMINACIÓN"
    },
    # MOBILIARIO/CAMAS
    "MOBILIARIO/CAMAS_LEIZE/LEIZI Quotation for Aldjandro (1).pdf": {
        "supplier": "LEIZI",
        "category": "MOBILIARIO/Camas"
    },
    "MOBILIARIO/CAMAS_LEIZE/LEIZI-Hotel Mattress Catalog 202508.pdf": {
        "supplier": "LEIZI",
        "category": "MOBILIARIO/Camas"
    },
    # MOBILIARIO/MESAS DE NOCHE
    "MOBILIARIO/MESAS DE NOCHE USB/NTFT Yifuyuan Bedside table Quotation（2025.9)(1).xlsx": {
        "supplier": "NTFT YIFUYUAN",
        "category": "MOBILIARIO/Mesas de Noche"
    },
    # MOBILIARIO general
    "MOBILIARIO/MOBILIARIO _FOSHAN SHISUO TECHNOLOGY CO LTD/COT FOSHAN SHISUO.xlsx": {
        "supplier": "FOSHAN SHISUO",
        "category": "MOBILIARIO"
    },
    "MOBILIARIO/MOBILIARIO_DHF/KOMPASS TRADING  Quotation sheet  Dec 05,2025.xls": {
        "supplier": "DHF",
        "category": "MOBILIARIO"
    },
    "MOBILIARIO/MOBILIARIO_RESTAURANTE_WEIRE/RESTAURANT FURNITURE CURADO.xlsx": {
        "supplier": "WEIRE",
        "category": "MOBILIARIO/Mobiliario Restaurante"
    },
    "MOBILIARIO/MOBILIARIO_SENCHUAN/SENCHUAN_20251201.pdf": {
        "supplier": "SENCHUAN",
        "category": "MOBILIARIO"
    },
    "MOBILIARIO/MOBILIARIO_SENCHUAN/SENCHUAN_20251201.xlsx": {
        "supplier": "SENCHUAN",
        "category": "MOBILIARIO"
    },
    # ONE STOP SHOP
    "ONE STOP SHOP/GEORGE/Copy of Shamsa tile quotation 2025.11.30.xlsx": {
        "supplier": "GEORGE",
        "category": "ONE STOP SHOP"
    },
    "ONE STOP SHOP/GEORGE/George - Furniture Quotation.xlsx": {
        "supplier": "GEORGE",
        "category": "ONE STOP SHOP"
    },
    "ONE STOP SHOP/GEORGE/George - Sanitary Quotation.xlsx": {
        "supplier": "GEORGE",
        "category": "ONE STOP SHOP"
    },
    "ONE STOP SHOP/GEORGE/George - cocina y closets quotation.xlsx": {
        "supplier": "GEORGE",
        "category": "ONE STOP SHOP"
    },
    "ONE STOP SHOP/PA HOME/1. PA Quotation for Kitchens & closets-2025.12.05.pdf": {
        "supplier": "PA HOME",
        "category": "ONE STOP SHOP"
    },
    # PISOS - GUARDAESCOBAS
    "PISOS - GUARDAESCOBAS/CU MATERIALS/Precios CU Materiales seleccionados.xlsx": {
        "supplier": "CU MATERIALS",
        "category": "PISOS - GUARDAESCOBAS"
    },
    "PISOS - GUARDAESCOBAS/HONGYU/MARBLE IMPRESSION -  HONGYU quotation 20251219 (1).xlsx": {
        "supplier": "HONGYU",
        "category": "PISOS - GUARDAESCOBAS"
    },
    "PISOS - GUARDAESCOBAS/HONGYU/STONE ESSENCE - HONGYU quotation 20251219 (2).xlsx": {
        "supplier": "HONGYU",
        "category": "PISOS - GUARDAESCOBAS"
    },
    "PISOS - GUARDAESCOBAS/HONGYU/WALL TILES - HONGYU quotation 20251219 (3).xlsx": {
        "supplier": "HONGYU",
        "category": "PISOS - GUARDAESCOBAS"
    },
    "PISOS - GUARDAESCOBAS/HONGYU/WOODEN TILES - HONGYU quotation 20251211.xls": {
        "supplier": "HONGYU",
        "category": "PISOS - GUARDAESCOBAS"
    },
    "PISOS - GUARDAESCOBAS/JINGDA_SPC/JINGDA SPC FLOOR - COT.xlsx": {
        "supplier": "JINGDA",
        "category": "PISOS - GUARDAESCOBAS/SPC Floor"
    },
    "PISOS - GUARDAESCOBAS/SOTENG_GUARDAESCOBAS/SOTENG _ COT _ GUARDAESCOBAS.xlsx": {
        "supplier": "SOTENG",
        "category": "PISOS - GUARDAESCOBAS/Guardaescobas"
    },
    # REVESTIMIENTOS
    "REVESTIMIENTOS/CU MATERIALS/Precios CU Materiales seleccionados.xlsx": {
        "supplier": "CU MATERIALS",
        "category": "REVESTIMIENTOS"
    },
    "REVESTIMIENTOS/WUXI KAIZE _ PANEL EXT - INT/Wuxi Kaize Indoor & Outdoor Panel Price List – FOB Prices.xlsx": {
        "supplier": "WUXI KAIZE",
        "category": "REVESTIMIENTOS"
    },
    # TARIMAS & EVENTOS
    "TARIMAS & EVENTOS/4 pillar Van-Ruben Tent Truss 24x12m (2).pdf": {
        "supplier": "VAN-RUBEN",
        "category": "TARIMAS & EVENTOS"
    },
}
```

**Files explicitly excluded** (not in FILE_MAP):
- `CANTON FAIR _OCT _2025/DIRECTORIO PROVEEDORES CANTON FAIR _OCT_2025.xlsx` — Canton Fair directory, used for supplier seeding
- `DIRECTORIO DE PROVEEDORES_2026.xlsx` — Supplier directory, not product data
- `FORMATO _COTIZACION DOTACION COCINA.xlsx` — Kitchen quotation template, not product data
- `MOBILIARIO A MEDIDA/REQUEST FOR QUOTATION (RFQ) _ GEORGE.docx` — RFQ template (.docx), not product data
- `DECK - FACHADAS/MEXY TECH - DECK/REQUIREMENT FORMAT (1).pdf` — Requirement format template, not product data
- `PISOS - GUARDAESCOBAS/SOTENG_GUARDAESCOBAS/【PS线条目录+颜色】-0011 (1).pdf` — Chinese catalog/color chart, duplicated
- `PISOS - GUARDAESCOBAS/SOTENG_GUARDAESCOBAS/【PS线条目录+颜色】-0011.pdf` — Chinese catalog/color chart (original)
- `REVESTIMIENTOS/WUXI KAIZE _ PANEL EXT - INT/Wuxi Kaize Import and Export Co., Ltd. 材料目录册(1) (1).pdf` — Chinese material catalog

**Script structure:**
- `sys.path` setup matching existing scripts
- `argparse` for CLI flags (`--dry-run`, `--file`, `--verbose`)
- `load_seed_mappings()` — Load and validate `scripts/output/seed_mappings.json`
- `resolve_supplier_id(supplier_name, mappings)` — Look up supplier UUID from mappings
- `resolve_category_id(category_path, mappings)` — Look up category UUID from mappings
- `convert_to_product_dto(extracted, supplier_id, category_id)` — Map `ExtractedProduct` → `ProductCreateDTO`
- `process_file(file_path, supplier_name, category_path, mappings, args)` — Process a single file end-to-end
- `print_summary_table(results)` — Print formatted summary table
- `write_results_json(results)` — Write detailed results to `import_results.json`
- `main()` — Orchestrate the full import

### Step 3: Implement the conversion function
- Map `ExtractedProduct` fields to `ProductCreateDTO`:
  - `name` → `name` (required — skip product if None/empty)
  - `sku` → `sku` (optional, auto-generated if None)
  - `description` → `description` (if `material` present, append: `"\n\nMaterial: {material}"`)
  - `price_fob_usd` → `unit_cost` (use as-is, Decimal)
  - `moq` → `minimum_order_qty` (default 1)
  - `dimensions` → `dimensions`
  - `unit_of_measure` → `unit_of_measure` (default "piece")
  - `supplier_id` → from FILE_MAP resolution
  - `category_id` → from FILE_MAP resolution
  - `status` → `"draft"` (default)
  - `currency` → `"USD"` (default)
  - `origin_country` → `"China"` (default)

### Step 4: Implement deduplication tracking
- After calling `bulk_create_products()`, inspect `BulkCreateResponseDTO.failed` list
- For each `BulkCreateErrorDTO`, check if the error message contains "unique" or "duplicate" (case-insensitive)
- Track duplicate count separately from other error count per file
- Log duplicates as `WARN` level, other errors as `ERROR` level

### Step 5: Implement the summary table and JSON output
- Summary table format with columns: File, Products, Success, Dupes, Errors
- Pad columns for alignment, print separator line
- Print TOTAL row at the end
- Write `import_results.json` to `scripts/output/` with per-file details:
  ```json
  {
    "summary": { "total_files": N, "total_products": N, "total_success": N, "total_dupes": N, "total_errors": N },
    "files": [
      {
        "file": "relative/path.xlsx",
        "supplier": "SUPPLIER_NAME",
        "category": "CATEGORY/PATH",
        "extracted": N,
        "success": N,
        "duplicates": N,
        "errors": N,
        "error_details": ["..."],
        "skipped_products": ["product with no name at index 3"]
      }
    ]
  }
  ```

### Step 6: Implement CLI flags
- `--dry-run`: Process files and extract products but skip the `bulk_create_products()` call. Print what would be imported.
- `--file <relative_path>`: Only process a single file from FILE_MAP (relative to CATALOG_BASE_PATH). Validate it exists in FILE_MAP.
- `--verbose`: Print each product name, SKU, and price as it's being processed

### Step 7: Test the script with --dry-run
- Run `cd apps/Server && python -m scripts.import_products --dry-run --verbose` to validate:
  - seed_mappings.json loads correctly
  - All FILE_MAP entries resolve to valid supplier and category UUIDs
  - Files are found and readable
  - Extraction produces products
  - Conversion to ProductCreateDTO works
  - Summary table prints correctly

### Step 8: Run validation commands
- Run all validation commands listed below to ensure zero regressions

## Testing Strategy
### Unit Tests
No new unit test files are created for this script — it is a one-time data import utility script following the same pattern as `seed_suppliers.py`, `seed_categories.py`, and `seed_all.py` (none of which have unit tests). Validation is done via `--dry-run` mode and the existing test suite.

### Edge Cases
- **Missing seed_mappings.json**: Script should exit with a clear error message
- **Supplier name not found in mappings**: Log warning, skip the file, continue with next
- **Category path not found in mappings**: Log warning, skip the file, continue with next
- **File not found on disk**: Log warning, skip, continue
- **Empty extraction result** (no products extracted): Log info, record as 0 products, continue
- **Product with no name**: Skip the product with a warning (name is required by ProductCreateDTO)
- **Duplicate SKU**: Handled by bulk_create_products error reporting; counted as "dupe" not "error"
- **Excel .xls format**: Same extraction path as .xlsx (openpyxl handles both via process_excel)
- **PDF with no extractable text**: Extraction service returns empty list; logged and continued
- **Unicode/Spanish characters in file paths**: Handled naturally by Python's os.path and the extraction service
- **Re-running the script** (idempotency): All products that already exist will be reported as duplicates; no data corruption

## Acceptance Criteria
- [ ] `import_products.py` exists at `apps/Server/scripts/import_products.py`
- [ ] FILE_MAP covers all ~45 relevant catalog files (excluding templates, directories, and non-product files)
- [ ] Excel files (.xlsx, .xls) are processed using `extraction_service.process_excel()`
- [ ] PDF files are processed using `extraction_service.process_pdf()`
- [ ] Products are created with correct `supplier_id` and `category_id` from seed mappings
- [ ] `unit_of_measure` is preserved from extraction
- [ ] `material` field is appended to `description` when present
- [ ] `price_fob_usd` maps to `unit_cost` on ProductCreateDTO
- [ ] `moq` maps to `minimum_order_qty` on ProductCreateDTO
- [ ] Duplicate SKUs are handled gracefully (logged as warnings, not fatal)
- [ ] Duplicates are counted separately from other errors
- [ ] Summary table is printed at end with per-file and total counts
- [ ] `scripts/output/import_results.json` is written with full details
- [ ] `--dry-run` flag works correctly (no database writes)
- [ ] `--file` flag processes a single file only
- [ ] `--verbose` flag prints each product being imported
- [ ] Script is runnable via `cd apps/Server && python -m scripts.import_products`
- [ ] Script is idempotent (re-running skips duplicates without crashing)
- [ ] Products without a name are skipped with a warning
- [ ] Missing supplier or category mappings for a file result in the file being skipped with a warning
- [ ] Existing pytest test suite passes without regressions

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd /mnt/c/Users/user/danke_apps/Kompass/trees/ad808429/apps/Server && python -c "from scripts.import_products import FILE_MAP; print(f'FILE_MAP has {len(FILE_MAP)} entries')"` — Validate script imports correctly and FILE_MAP is populated
- `cd /mnt/c/Users/user/danke_apps/Kompass/trees/ad808429/apps/Server && python -m scripts.import_products --help` — Validate argparse works and shows usage
- `cd /mnt/c/Users/user/danke_apps/Kompass/trees/ad808429/apps/Server && source .venv/bin/activate && python -m pytest tests/ -v --tb=short 2>&1 | tail -20` — Run Server tests to validate zero regressions
- `cd /mnt/c/Users/user/danke_apps/Kompass/trees/ad808429/apps/Server && source .venv/bin/activate && ruff check scripts/import_products.py` — Lint the new script
- `cd /mnt/c/Users/user/danke_apps/Kompass/trees/ad808429/apps/Client && npm run build` — Run Client build to validate zero regressions (no client changes, but verify)

## Notes
- **SKU uniqueness is GLOBAL, not per-supplier**: The database schema has `sku VARCHAR(100) NOT NULL UNIQUE` — this means SKU must be unique across ALL suppliers, not just within a supplier. If two suppliers have a product with the same SKU, the second insert will fail. The script should handle this gracefully.
- **Singleton instances**: Import `extraction_service` from `app.services.extraction_service` and `product_service` from `app.services.product_service` — these are module-level singletons.
- **No new dependencies**: The script uses only existing packages (openpyxl, PyPDF2 via extraction_service). No `uv add` needed.
- **Catalog base path**: The `CATALOG_BASE_PATH` constant should be relative to the repo root (resolved at runtime like `seed_suppliers.py` does). The catalog files exist in the main repo at `Requirements_Gathering/Sourcing/Data/PROVEEDORES - CATALOGOS/` but may not exist in the worktree — the script should resolve the path relative to the repo root and handle missing files gracefully.
- **File count**: Of the 52 total files, approximately 45 are actual product catalog files mapped in FILE_MAP. The remaining ~7 are excluded (Canton Fair directory, supplier directories, quotation templates, RFQ template, Chinese-only catalogs).
- **Sequential processing**: Process files one at a time to avoid database connection pool issues, following the issue requirement.
- **Conditional documentation**: Per `conditional_docs.md`, when working with seeding scripts and `seed_mappings.json`, reference `app_docs/feature-aa50456e-repo-helpers-reference-data-seeding.md`.
