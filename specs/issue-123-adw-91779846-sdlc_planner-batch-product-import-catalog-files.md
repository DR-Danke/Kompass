# Feature: Batch Product Import from 52 Supplier Catalog Files

## Metadata
issue_number: `123`
adw_id: `91779846`
issue_json: ``

## Feature Description
Create a batch import script (`apps/Server/scripts/import_products.py`) that processes all 52 supplier catalog files from the `PROVEEDORES - CATALOGOS` directory. The script uses the enhanced extraction service (SCD-001) to parse Excel and PDF files, maps each file to the correct supplier and category using `seed_mappings.json` (SCD-002), and imports products into the database via the product service's `bulk_create_products` method. The script includes CLI flags for `--dry-run`, `--file`, and `--verbose` modes, handles duplicate SKU errors gracefully, and produces a summary table with detailed results output.

## User Story
As a Kompass system administrator
I want to batch import products from all 52 supplier catalog files in a single script run
So that the products table is populated with hundreds of products correctly mapped to their suppliers and categories, enabling the quotation automation workflow

## Problem Statement
After seeding reference data (suppliers, categories, HS codes) in SCD-002, the products table remains empty. There are 52 supplier catalog files in various formats (Excel, PDF) across multiple category folders that need to be processed and imported. Manual import is impractical — a reliable, idempotent batch script is needed.

## Solution Statement
Build a Python script with a hardcoded `FILE_MAP` dictionary (more reliable than path-parsing for Spanish filenames) that maps each of the ~50 relevant catalog files to its supplier name and category path. The script loads `seed_mappings.json` to resolve supplier and category UUIDs, uses `extraction_service.process_excel()` and `extraction_service.process_pdf()` to parse files, converts `ExtractedProduct` DTOs to `ProductCreateDTO`, and calls `product_service.bulk_create_products()` per file. Duplicate SKU errors are caught and counted separately. Results are printed as a summary table and written to `import_results.json`.

## Relevant Files
Use these files to implement the feature:

- `apps/Server/scripts/seed_all.py` — Reference for script structure: how to add `sys.path`, load seed mappings, resolve repo root, and pattern for the `OUTPUT_DIR`/`OUTPUT_FILE` constants. Follow the same `sys.path.insert` pattern and output directory pattern.
- `apps/Server/scripts/seed_suppliers.py` — Reference for `KNOWN_SUPPLIERS` list (the 25 supplier names that must match FILE_MAP entries), and for the `normalize_name` pattern.
- `apps/Server/scripts/seed_categories.py` — Reference for `CATEGORY_TREE` (the category hierarchy that determines valid category paths in FILE_MAP).
- `apps/Server/scripts/output/seed_mappings.json` — The mappings file loaded at runtime. Structure: `{"categories": {"BAÑOS": "uuid", "BAÑOS/Griferías": "uuid", ...}, "suppliers": {"HUAYI": "uuid", ...}, "hs_codes": {...}}`.
- `apps/Server/app/services/extraction_service.py` — The extraction service singleton (`extraction_service`). Key methods: `process_excel(file_path) -> Tuple[List[ExtractedProduct], List[str]]` and `process_pdf(file_path) -> Tuple[List[ExtractedProduct], List[str]]`.
- `apps/Server/app/services/product_service.py` — The product service singleton (`product_service`). Key method: `bulk_create_products(products: List[ProductCreateDTO]) -> BulkCreateResponseDTO`.
- `apps/Server/app/models/extraction_dto.py` — `ExtractedProduct` DTO with fields: `sku`, `name`, `description`, `price_fob_usd`, `moq`, `dimensions`, `material`, `suggested_category`, `confidence_score`, `unit_of_measure`.
- `apps/Server/app/models/kompass_dto.py` — `ProductCreateDTO` with fields: `sku` (optional, auto-generated if missing), `name`, `description`, `supplier_id` (UUID), `category_id` (optional UUID), `status` (ProductStatus), `unit_cost`, `unit_of_measure`, `minimum_order_qty`, `dimensions`, `origin_country`. Also `BulkCreateResponseDTO` and `BulkCreateErrorDTO`.
- `apps/Server/database/schema.sql` — Products table schema showing the `UNIQUE` constraint pattern (sku uniqueness is per-supplier, handled at DB level).
- `.gitignore` — Already has `apps/Server/scripts/output/` entry — `import_results.json` will be excluded automatically.
- `apps/Server/scripts/__init__.py` — Existing empty init file for the scripts package.

### New Files
- `apps/Server/scripts/import_products.py` — The batch import script (this is the main deliverable)

## Implementation Plan
### Phase 1: Foundation
- Load and validate `seed_mappings.json` at script startup
- Build the complete `FILE_MAP` dictionary mapping all ~50 relevant catalog files to their supplier name and category path
- Set up `argparse` for `--dry-run`, `--file <path>`, and `--verbose` CLI flags
- Resolve the base path for catalog files relative to the repo root

### Phase 2: Core Implementation
- Implement the main processing loop: iterate over FILE_MAP entries, resolve supplier_id and category_id from seed mappings, determine file type, call the appropriate extraction service method
- Convert `ExtractedProduct` to `ProductCreateDTO`: map `price_fob_usd` → `unit_cost`, `moq` → `minimum_order_qty`, append `material` to `description`, set `status = "draft"`, carry over `unit_of_measure` and `dimensions`
- Call `product_service.bulk_create_products()` per file (or skip in dry-run mode)
- Track results per file: total extracted, successes, duplicates (detect from error message containing "duplicate" or "unique constraint"), other errors

### Phase 3: Integration
- Print formatted summary table at the end
- Write detailed `import_results.json` to `scripts/output/`
- Handle edge cases: missing files, empty extraction results, files not in FILE_MAP

## Step by Step Tasks

### Step 1: Verify prerequisites exist
- Confirm `apps/Server/scripts/__init__.py` exists (it does)
- Confirm `apps/Server/scripts/output/` is in `.gitignore` (it is)
- Read `apps/Server/scripts/output/seed_mappings.json` to understand the exact structure and available supplier/category names

### Step 2: Create the import_products.py script with FILE_MAP
- Create `apps/Server/scripts/import_products.py`
- Add the `sys.path.insert` pattern matching `seed_all.py`
- Define `CATALOG_BASE_PATH` constant as `Requirements_Gathering/Sourcing/Data/PROVEEDORES - CATALOGOS/`
- Define `FILE_MAP` dictionary with all ~50 relevant catalog files mapped to their supplier and category. The mapping is based on the actual file listing below:

**FILE_MAP entries (all 52 files analyzed, ~47 to include, ~5 to skip):**

Files to SKIP:
1. `CANTON FAIR _OCT _2025/DIRECTORIO PROVEEDORES CANTON FAIR _OCT_2025.xlsx` — Already used for supplier seeding
2. `FORMATO _COTIZACION DOTACION COCINA.xlsx` — Kitchen quotation template
3. `DIRECTORIO DE PROVEEDORES_2026.xlsx` — Provider directory, not product data
4. `MOBILIARIO A MEDIDA/REQUEST FOR QUOTATION (RFQ) _ GEORGE.docx` — RFQ template (.docx), not product data
5. `DECK - FACHADAS/MEXY TECH - DECK/REQUIREMENT FORMAT (1).pdf` — Requirement format template, not product data

Files to INCLUDE (~47 entries):

**BAÑOS/GRIFERIASS/**
- `BAÑOS/GRIFERIASS/HUAYI/HUAYI (1).xlsx` → supplier: "HUAYI", category: "BAÑOS/Griferías"
- `BAÑOS/GRIFERIASS/JVK/Quotation JVK.xlsx` → supplier: "JVK", category: "BAÑOS/Griferías"
- `BAÑOS/GRIFERIASS/LAYASDUN/LAYASDUN Quotation.xlsx` → supplier: "LAYASDUN", category: "BAÑOS/Griferías"
- `BAÑOS/GRIFERIASS/PINLSLON BUILDING MATERIALS/2026 Pinslon price list-faucets (2).pdf` → supplier: "PINLSLON", category: "BAÑOS/Griferías"

**BAÑOS/GRIFERIAS_ducha_baño_cocina/**
- `BAÑOS/GRIFERIAS_ducha _baño _cocina/LAYASDUN/Quote from Layasdun 20251201.pdf` → supplier: "LAYASDUN", category: "BAÑOS/Griferías"

**BAÑOS/LAVAMANOS/**
- `BAÑOS/LAVAMANOS/Quotation from Conrazzo.pdf` → supplier: "CONRAZZO", category: "BAÑOS/Lavamanos"

**BAÑOS/SANITARIOS Y MUEBLES DE BAÑO/**
- `BAÑOS/SANITARIOS Y MUEBLES DE BAÑO/Price list From BATH STORE- TAUSU.xlsx` → supplier: "BATH STORE-TAUSU", category: "BAÑOS/Sanitarios y Muebles de Baño"

**BAÑOS/ (root)**
- `BAÑOS/STAINLESS.xlsx` → supplier: "HUAYI", category: "BAÑOS/Griferías" (stainless steel fittings from HUAYI context)

**DECK - FACHADAS/**
- `DECK - FACHADAS/MEXY TECH - DECK/MexyTech catalog (1).pdf` → supplier: "MEXY TECH", category: "DECK - FACHADAS"
- `DECK - FACHADAS/MEXY TECH - DECK/REQUIREMENT FORMAT (3).xlsx` → supplier: "MEXY TECH", category: "DECK - FACHADAS"

**DISPENSADORES/**
- `DISPENSADORES/Quotation LA20251129K.pdf` → supplier: "LAYASDUN", category: "DISPENSADORES"

**DOTACIÓN DE COCINA/**
- `DOTACIÓN DE COCINA/KITCHENWARE -CHINA.xlsx` → supplier: "WIREKING", category: "DOTACIÓN DE COCINA"
- `DOTACIÓN DE COCINA/MAYORISTA COLOMBIA/COT 2026-06 (1).pdf` → supplier: "MAYORISTA COLOMBIA", category: "DOTACIÓN DE COCINA"
- `DOTACIÓN DE COCINA/WIREKING_ DOT COCINA/Wireking Quotation - Kompasstrading -2025-12-01.xlsx` → supplier: "WIREKING", category: "DOTACIÓN DE COCINA"

**ESPEJOS/**
- `ESPEJOS/LUXDREAM/2026 Luxdream Led Mirror E-Brochure.pdf` → supplier: "LUXDREAM", category: "ESPEJOS"
- `ESPEJOS/LUXDREAM/S-Luxdream Led Bathroom Mirror Price List.pdf` → supplier: "LUXDREAM", category: "ESPEJOS"

**ILUMINACIÓN/**
- `ILUMINACIÓN/GEORGE/Precios Iluminación - George.xlsx` → supplier: "GEORGE", category: "ILUMINACIÓN"
- `ILUMINACIÓN/LED_ BWBYONE/BYONE BDEXPO CATALOG 2025.12 (2).pdf` → supplier: "BWBYONE", category: "ILUMINACIÓN"
- `ILUMINACIÓN/LED_ BWBYONE/price list of  track light from Bwbyone Sophia.pdf` → supplier: "BWBYONE", category: "ILUMINACIÓN"
- `ILUMINACIÓN/LED_ BWBYONE/price list of downlight from Bwbyone Sophia.pdf` → supplier: "BWBYONE", category: "ILUMINACIÓN"
- `ILUMINACIÓN/LED_ BWBYONE/price list of panel light from Bwbyone Sophia(经济款）  2026.1.3.pdf` → supplier: "BWBYONE", category: "ILUMINACIÓN"

**MOBILIARIO/**
- `MOBILIARIO/CAMAS_LEIZE/LEIZI Quotation for Aldjandro (1).pdf` → supplier: "LEIZI", category: "MOBILIARIO/Camas"
- `MOBILIARIO/CAMAS_LEIZE/LEIZI-Hotel Mattress Catalog 202508.pdf` → supplier: "LEIZI", category: "MOBILIARIO/Camas"
- `MOBILIARIO/MESAS DE NOCHE USB/NTFT Yifuyuan Bedside table Quotation（2025.9)(1).xlsx` → supplier: "NTFT YIFUYUAN", category: "MOBILIARIO/Mesas de Noche"
- `MOBILIARIO/MOBILIARIO _FOSHAN SHISUO TECHNOLOGY CO LTD/COT FOSHAN SHISUO.xlsx` → supplier: "FOSHAN SHISUO", category: "MOBILIARIO"
- `MOBILIARIO/MOBILIARIO_DHF/KOMPASS TRADING  Quotation sheet  Dec 05,2025.xls` → supplier: "DHF", category: "MOBILIARIO"
- `MOBILIARIO/MOBILIARIO_RESTAURANTE_WEIRE/RESTAURANT FURNITURE CURADO.xlsx` → supplier: "WEIRE", category: "MOBILIARIO/Mobiliario Restaurante"
- `MOBILIARIO/MOBILIARIO_SENCHUAN/SENCHUAN_20251201.pdf` → supplier: "SENCHUAN", category: "MOBILIARIO"
- `MOBILIARIO/MOBILIARIO_SENCHUAN/SENCHUAN_20251201.xlsx` → supplier: "SENCHUAN", category: "MOBILIARIO"

**ONE STOP SHOP/**
- `ONE STOP SHOP/GEORGE/Copy of Shamsa tile quotation 2025.11.30.xlsx` → supplier: "GEORGE", category: "ONE STOP SHOP"
- `ONE STOP SHOP/GEORGE/George - cocina y closets quotation.xlsx` → supplier: "GEORGE", category: "ONE STOP SHOP"
- `ONE STOP SHOP/GEORGE/George - Furniture Quotation.xlsx` → supplier: "GEORGE", category: "ONE STOP SHOP"
- `ONE STOP SHOP/GEORGE/George - Sanitary Quotation.xlsx` → supplier: "GEORGE", category: "ONE STOP SHOP"
- `ONE STOP SHOP/PA HOME/1. PA Quotation for Kitchens & closets-2025.12.05.pdf` → supplier: "PA HOME", category: "ONE STOP SHOP"

**PISOS - GUARDAESCOBAS/**
- `PISOS - GUARDAESCOBAS/CU MATERIALS/Precios CU Materiales seleccionados.xlsx` → supplier: "CU MATERIALS", category: "PISOS - GUARDAESCOBAS/SPC Floor"
- `PISOS - GUARDAESCOBAS/HONGYU/MARBLE IMPRESSION -  HONGYU quotation 20251219 (1).xlsx` → supplier: "HONGYU", category: "PISOS - GUARDAESCOBAS"
- `PISOS - GUARDAESCOBAS/HONGYU/STONE ESSENCE - HONGYU quotation 20251219 (2).xlsx` → supplier: "HONGYU", category: "PISOS - GUARDAESCOBAS"
- `PISOS - GUARDAESCOBAS/HONGYU/WALL TILES - HONGYU quotation 20251219 (3).xlsx` → supplier: "HONGYU", category: "PISOS - GUARDAESCOBAS"
- `PISOS - GUARDAESCOBAS/HONGYU/WOODEN TILES - HONGYU quotation 20251211.xls` → supplier: "HONGYU", category: "PISOS - GUARDAESCOBAS"
- `PISOS - GUARDAESCOBAS/JINGDA_SPC/JINGDA SPC FLOOR - COT.xlsx` → supplier: "JINGDA", category: "PISOS - GUARDAESCOBAS/SPC Floor"
- `PISOS - GUARDAESCOBAS/SOTENG_GUARDAESCOBAS/SOTENG _ COT _ GUARDAESCOBAS.xlsx` → supplier: "SOTENG", category: "PISOS - GUARDAESCOBAS/Guardaescobas"
- `PISOS - GUARDAESCOBAS/SOTENG_GUARDAESCOBAS/【PS线条目录+颜色】-0011 (1).pdf` → supplier: "SOTENG", category: "PISOS - GUARDAESCOBAS/Guardaescobas"
- `PISOS - GUARDAESCOBAS/SOTENG_GUARDAESCOBAS/【PS线条目录+颜色】-0011.pdf` → supplier: "SOTENG", category: "PISOS - GUARDAESCOBAS/Guardaescobas"

**REVESTIMIENTOS/**
- `REVESTIMIENTOS/CU MATERIALS/Precios CU Materiales seleccionados.xlsx` → supplier: "CU MATERIALS", category: "REVESTIMIENTOS"
- `REVESTIMIENTOS/WUXI KAIZE _ PANEL EXT - INT/Wuxi Kaize Import and Export Co., Ltd. 材料目录册(1) (1).pdf` → supplier: "WUXI KAIZE", category: "REVESTIMIENTOS/Panel Exterior"
- `REVESTIMIENTOS/WUXI KAIZE _ PANEL EXT - INT/Wuxi Kaize Indoor & Outdoor Panel Price List – FOB Prices.xlsx` → supplier: "WUXI KAIZE", category: "REVESTIMIENTOS/Panel Exterior"

**TARIMAS & EVENTOS/**
- `TARIMAS & EVENTOS/4 pillar Van-Ruben Tent Truss 24x12m (2).pdf` → supplier: "VAN-RUBEN", category: "TARIMAS & EVENTOS"

### Step 3: Implement seed mappings loading and UUID resolution
- Add function `load_seed_mappings(path: str) -> dict` that reads and parses `seed_mappings.json`
- Add function `resolve_supplier_id(supplier_name: str, mappings: dict) -> Optional[str]` that looks up supplier UUID from mappings
- Add function `resolve_category_id(category_path: str, mappings: dict) -> Optional[str]` that looks up category UUID from mappings
- Handle case where supplier or category is not found in mappings (log warning, skip file)

### Step 4: Implement file processing logic
- Add function `process_file(file_path: str, supplier_id: str, category_id: str, dry_run: bool, verbose: bool) -> dict` that:
  1. Determines file type by extension
  2. Calls `extraction_service.process_excel()` for `.xlsx`/`.xls` or `extraction_service.process_pdf()` for `.pdf`
  3. Skips `.docx` files with a warning
  4. Converts each `ExtractedProduct` to `ProductCreateDTO`:
     - `sku` = extracted `sku` (auto-generated if None)
     - `name` = extracted `name` (REQUIRED — skip products without a name)
     - `description` = extracted `description` + `" | Material: {material}"` if material is present
     - `supplier_id` = resolved UUID
     - `category_id` = resolved UUID
     - `unit_cost` = extracted `price_fob_usd` or Decimal("0.00")
     - `unit_of_measure` = extracted `unit_of_measure` or "piece"
     - `minimum_order_qty` = extracted `moq` or 1
     - `dimensions` = extracted `dimensions`
     - `status` = ProductStatus.DRAFT
     - `origin_country` = "China"
  5. In dry-run mode: log what would be imported, return counts
  6. In normal mode: call `product_service.bulk_create_products(products_list)` and track results
  7. Classify errors: "duplicate" errors (containing "duplicate" or "unique" in error string) vs. other errors
  8. Returns dict with `file`, `total`, `success`, `dupes`, `errors`, `error_details`

### Step 5: Implement CLI argument parsing
- Use `argparse` to define:
  - `--dry-run`: Parse and validate without inserting into database
  - `--file <path>`: Process a single file only (relative path within FILE_MAP)
  - `--verbose`: Print each product being imported

### Step 6: Implement main execution flow
- `main()` function that:
  1. Parses CLI arguments
  2. Resolves repo root (3 levels up from scripts/ directory, matching `seed_all.py` pattern)
  3. Loads seed mappings from `scripts/output/seed_mappings.json`
  4. Validates that seed mappings are not empty
  5. If `--file` flag: filter FILE_MAP to just that file
  6. Iterates over FILE_MAP entries sequentially
  7. For each entry: resolve supplier_id and category_id, build full file path, process file
  8. Collects all results

### Step 7: Implement summary table output
- Print formatted summary table at the end:
  ```
  File                          | Products | Success | Dupes | Errors
  ------------------------------|----------|---------|-------|-------
  BAÑOS/GRIFERIASS/HUAYI/...   |       25 |      23 |     1 |      1
  ...
  TOTAL                         |      450 |     420 |    15 |     15
  ```
- Truncate long file paths to fit the table column width

### Step 8: Implement JSON results output
- Write detailed results to `scripts/output/import_results.json` with structure:
  ```json
  {
    "run_at": "ISO timestamp",
    "dry_run": false,
    "totals": {"files": 47, "products": 450, "success": 420, "dupes": 15, "errors": 15},
    "files": [
      {
        "path": "...",
        "supplier": "HUAYI",
        "category": "BAÑOS/Griferías",
        "total": 25,
        "success": 23,
        "dupes": 1,
        "errors": 1,
        "error_details": ["Duplicate SKU: ABC-123"]
      }
    ]
  }
  ```

### Step 9: Test with --dry-run and --file flags
- Test the script with `--dry-run` to verify parsing works without database writes
- Test with `--file` to verify single file processing
- Test with `--verbose` to verify detailed output

### Step 10: Run validation commands
- Run all validation commands listed below to ensure zero regressions

## Testing Strategy
### Unit Tests
- No formal unit tests are required for this script — it is a one-off data import utility
- Validation is done via `--dry-run` mode which exercises parsing and conversion logic without database writes
- The `--file` flag enables targeted testing of individual catalog files

### Edge Cases
- File not found on disk (extraction service returns empty list with error)
- Empty extraction results (no products found in file) — log warning, continue
- Product without a `name` field — skip that product, log warning
- Duplicate SKU for same supplier — caught by DB unique constraint, counted as "dupe"
- Supplier name not found in seed_mappings — skip file with warning
- Category path not found in seed_mappings — skip file with warning
- `.xls` files (older Excel format) — openpyxl may not support, extraction_service handles this
- Chinese character filenames (e.g., `【PS线条目录+颜色】`) — Python handles Unicode paths natively
- Same file appearing in multiple categories (e.g., `CU MATERIALS/Precios CU Materiales seleccionados.xlsx` appears under both PISOS and REVESTIMIENTOS) — each occurrence imports with different category_id, products may get duplicate SKUs across categories which is acceptable since uniqueness is per-supplier+sku

## Acceptance Criteria
- [ ] `FILE_MAP` covers all ~47 relevant catalog files (excluding the 5 skipped files)
- [ ] Excel files (`.xlsx`, `.xls`) are processed using `extraction_service.process_excel()`
- [ ] PDF files are processed using `extraction_service.process_pdf()`
- [ ] `.docx` files are skipped with a warning
- [ ] Products are created with correct `supplier_id` and `category_id` from seed mappings
- [ ] `unit_of_measure` is preserved from extraction
- [ ] `material` is appended to description when present
- [ ] `price_fob_usd` is mapped to `unit_cost`
- [ ] `moq` is mapped to `minimum_order_qty`
- [ ] `status` is set to `"draft"` for all imported products
- [ ] Duplicate SKUs are handled gracefully (logged, counted separately, not fatal)
- [ ] Summary table is printed at end with accurate counts per file and totals
- [ ] `import_results.json` is written to `scripts/output/` with full details
- [ ] `--dry-run` flag parses and validates without inserting into database
- [ ] `--file` flag processes a single file only
- [ ] `--verbose` flag prints each product being imported
- [ ] Script is idempotent (re-running skips duplicates without crashing)
- [ ] Script is runnable via `cd apps/Server && python -m scripts.import_products`

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd /mnt/c/Users/user/danke_apps/Kompass/trees/91779846/apps/Server && python -c "from scripts.import_products import FILE_MAP; print(f'FILE_MAP has {len(FILE_MAP)} entries')"` — Verify the script imports cleanly and FILE_MAP has ~47 entries
- `cd /mnt/c/Users/user/danke_apps/Kompass/trees/91779846/apps/Server && python -m scripts.import_products --dry-run 2>&1 | tail -60` — Run dry-run mode to verify file parsing works end-to-end without database writes
- `cd /mnt/c/Users/user/danke_apps/Kompass/trees/91779846/apps/Server && python -m scripts.import_products --dry-run --file "BAÑOS/GRIFERIASS/HUAYI/HUAYI (1).xlsx" 2>&1` — Test single-file dry-run
- `cd /mnt/c/Users/user/danke_apps/Kompass/trees/91779846/apps/Server && python -m scripts.import_products --dry-run --verbose --file "BAÑOS/GRIFERIASS/JVK/Quotation JVK.xlsx" 2>&1` — Test verbose single-file dry-run
- `cd /mnt/c/Users/user/danke_apps/Kompass/trees/91779846/apps/Server && python -c "import json; data=json.load(open('scripts/output/import_results.json')); print(f'Results: {data[\"totals\"]}')"` — Verify import_results.json was written correctly after dry-run
- `cd /mnt/c/Users/user/danke_apps/Kompass/trees/91779846/apps/Server && .venv/bin/ruff check scripts/import_products.py` — Lint the new script
- `cd /mnt/c/Users/user/danke_apps/Kompass/trees/91779846/apps/Server && .venv/bin/pytest tests/ -v --tb=short 2>&1 | tail -20` — Run Server tests for zero regressions

## Notes
- The `REQUIREMENT FORMAT (1).pdf` file in the MEXY TECH folder is a template/format document, not a product catalog — it should be skipped in FILE_MAP. Only `REQUIREMENT FORMAT (3).xlsx` and `MexyTech catalog (1).pdf` contain product data.
- The `KITCHENWARE -CHINA.xlsx` file in DOTACIÓN DE COCINA has no obvious supplier folder — mapped to "WIREKING" since Wireking is the primary kitchenware supplier. If this mapping is incorrect, the implementer should verify and adjust.
- `BAÑOS/STAINLESS.xlsx` has no obvious supplier folder — mapped to "HUAYI" based on context (stainless steel fittings are HUAYI's product line). Verify during implementation.
- The `CU MATERIALS/Precios CU Materiales seleccionados.xlsx` file appears in TWO different category folders (PISOS and REVESTIMIENTOS). Both entries should be in FILE_MAP with different category assignments. Since the same file may contain the same SKUs, the second import may produce duplicates which is expected and handled gracefully.
- `.xls` files (older Excel format) may require `xlrd` library. Check if `openpyxl` handles them — if not, add `xlrd` to requirements: `pip install xlrd` / `uv add xlrd`.
- Chinese character PDF filenames (`【PS线条目录+颜色】`) should work but may have limited text extraction quality from PDF content.
- This script does NOT run as part of the application server — it's a one-off data migration script run manually from the command line.
- The script processes files sequentially (not in parallel) to avoid database connection pool exhaustion.
- `origin_country` defaults to "China" for all imported products since all suppliers are Chinese.
