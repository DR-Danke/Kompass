# Feature: Repository Helpers and Reference Data Seeding Scripts

## Metadata
issue_number: `122`
adw_id: `aa50456e`
issue_json: ``

## Feature Description
Add `get_by_name()` helper methods to SupplierRepository and `get_by_name_and_parent()` to CategoryRepository for idempotent seeding, then create Python scripts to seed categories (from supplier catalog folder structure), suppliers (from Canton Fair master directory Excel), and HS codes (hardcoded Colombian duty rates mapped to categories). A unified seed runner orchestrates all three scripts and outputs a `seed_mappings.json` file for downstream use by SCD-003 (Batch Product Import).

This is Phase 1, Issue 2 of 5 in the Supplier Catalog Data pipeline. It runs in parallel with SCD-001 (Excel Extraction Enhancements) — they touch completely different files.

## User Story
As a system administrator
I want to run idempotent seeding scripts that populate categories, suppliers, and HS codes from real supplier data
So that reference data is ready for batch product imports with correct supplier-category-tariff mappings

## Problem Statement
Before batch-importing 52 supplier catalog files, the database needs reference data: categories matching the folder structure, suppliers from the Canton Fair master directory, and HS codes with Colombian duty rates mapped to categories. Without this data, the batch import (SCD-003) cannot assign supplier IDs, category IDs, or calculate tariffs. Additionally, the repository layer lacks `get_by_name` helpers needed for idempotent upsert patterns.

## Solution Statement
1. Add two repository helper methods (`CategoryRepository.get_by_name_and_parent()` and `SupplierRepository.get_by_name()`) to enable idempotent seeding via check-then-create pattern.
2. Create four Python scripts under `apps/Server/scripts/`:
   - `seed_categories.py` — hardcoded category tree (~20 categories: 11 roots + subcategories)
   - `seed_suppliers.py` — reads Canton Fair Excel, filters to 24 known suppliers
   - `seed_hs_codes.py` — hardcoded 15 HS codes with duty rates
   - `seed_all.py` — unified runner that executes all three in sequence and writes `seed_mappings.json`
3. All scripts are idempotent (running twice produces no duplicates) and use the app's repository layer (not raw SQL).

## Relevant Files
Use these files to implement the feature:

- `apps/Server/app/repository/kompass_repository.py` — Main repository file. Add `get_by_name_and_parent()` to `CategoryRepository` (after line 536) and `get_by_name()` to `SupplierRepository` (after line 1600). Reference `PortfolioRepository.get_by_name()` at line 3373 and `HSCodeRepository.get_by_code()` at line 1060 as patterns. Singleton instances at lines 5095-5105.
- `apps/Server/app/config/database.py` — Database connection helpers (`get_database_connection()`, `close_database_connection()`). All scripts import from here.
- `apps/Server/app/models/kompass_dto.py` — DTOs including `CategoryCreateDTO` (line 203), `SupplierCreateDTO` (line 362), `HSCodeCreateDTO` (line 318). Scripts may use repository methods directly rather than DTOs.
- `apps/Server/database/schema.sql` — Schema reference: `categories` (line 66, no unique name constraint), `suppliers` (line 110, UNIQUE on `code`), `hs_codes` (line 93, UNIQUE on `code`).
- `apps/Server/database/seed_niches.py` — Existing seed script pattern using `INSERT ... ON CONFLICT DO NOTHING` with `get_database_connection()`.
- `apps/Server/scripts/create_admin_user.py` — Existing script pattern with `sys.path.insert()` for importing app modules.
- `apps/Server/tests/test_kompass/conftest.py` — Test fixtures and factory patterns for suppliers, categories, etc.
- `apps/Server/tests/test_kompass/test_supplier_e2e.py` — Test pattern: mocking repository singletons at service level.
- `.gitignore` — Add `scripts/output/` entry.

### New Files
- `apps/Server/scripts/__init__.py` — Package init for scripts module.
- `apps/Server/scripts/seed_categories.py` — Category tree seeding script.
- `apps/Server/scripts/seed_suppliers.py` — Supplier seeding script from Canton Fair Excel.
- `apps/Server/scripts/seed_hs_codes.py` — HS code seeding script.
- `apps/Server/scripts/seed_all.py` — Unified seed runner.
- `apps/Server/scripts/output/.gitkeep` — Placeholder for seed output directory.
- `apps/Server/tests/test_kompass/test_repository_helpers.py` — Unit tests for new repository helper methods.

## Implementation Plan
### Phase 1: Foundation
Add the two repository helper methods needed for idempotent seeding. These are pure additions to existing classes — no existing functionality is modified.

- `CategoryRepository.get_by_name_and_parent(name, parent_id)` — case-insensitive lookup using `LOWER(name) = LOWER(%s)` with `IS NOT DISTINCT FROM` for nullable parent_id
- `SupplierRepository.get_by_name(name)` — case-insensitive lookup using `LOWER(name) = LOWER(%s) LIMIT 1`

### Phase 2: Core Implementation
Create the four seeding scripts following existing patterns from `seed_niches.py` and `create_admin_user.py`:

1. **Category seeding** — Hardcoded tree, creates roots first then children using returned parent UUIDs
2. **Supplier seeding** — Reads Canton Fair Excel with openpyxl (already in requirements), filters to 24 known suppliers via case-insensitive fuzzy matching
3. **HS code seeding** — Hardcoded 15 codes, uses existing `HSCodeRepository.get_by_code()` for idempotency check and `HSCodeRepository.create()` to insert
4. **Unified runner** — Orchestrates all three, writes combined mappings JSON

### Phase 3: Integration
- Add unit tests for the new repository helpers
- Add `scripts/output/` to `.gitignore`
- Verify scripts are runnable from `apps/Server/` via `python -m scripts.seed_all`

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Add `CategoryRepository.get_by_name_and_parent()` helper method
- Open `apps/Server/app/repository/kompass_repository.py`
- After the `_row_to_dict_with_parent` method (line ~536), add `get_by_name_and_parent()`:
  ```python
  def get_by_name_and_parent(self, name: str, parent_id: Optional[UUID] = None) -> Optional[Dict[str, Any]]:
      """Get category by name and parent_id for idempotent seeding."""
  ```
- Query: `SELECT id, name, description, parent_id, sort_order, is_active, created_at, updated_at FROM categories WHERE LOWER(name) = LOWER(%s) AND parent_id IS NOT DISTINCT FROM %s`
- When `parent_id` is None, pass `None` directly (IS NOT DISTINCT FROM handles NULL correctly in PostgreSQL)
- When `parent_id` is a UUID, pass `str(parent_id)`
- Use `_row_to_dict()` to convert the row
- Follow the connection/error/finally pattern from `get_by_id()` (line 365)

### Step 2: Add `SupplierRepository.get_by_name()` helper method
- In the same file, after `_row_to_dict` method of SupplierRepository (line ~1600), add `get_by_name()`:
  ```python
  def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
      """Get supplier by name for deduplication."""
  ```
- Query: `SELECT id, name, code, status, contact_name, contact_email, contact_phone, address, city, country, website, notes, created_at, updated_at FROM suppliers WHERE LOWER(name) = LOWER(%s) LIMIT 1`
- Use `_row_to_dict()` to convert the row
- Follow the pattern from `PortfolioRepository.get_by_name()` at line 3373

### Step 3: Create scripts package structure
- Create `apps/Server/scripts/__init__.py` (empty file)
- Create `apps/Server/scripts/output/` directory
- Create `apps/Server/scripts/output/.gitkeep` (empty file)
- Add `apps/Server/scripts/output/` to root `.gitignore`

### Step 4: Create `seed_categories.py`
- Create `apps/Server/scripts/seed_categories.py`
- Add `sys.path.insert()` pattern from `create_admin_user.py` to support `python -m scripts.seed_categories` from `apps/Server/`
- Define hardcoded `CATEGORY_TREE` data structure:
  ```python
  CATEGORY_TREE = {
      "BAÑOS": ["Griferías", "Lavamanos", "Sanitarios y Muebles de Baño"],
      "DECK - FACHADAS": [],
      "DISPENSADORES": [],
      "DOTACIÓN DE COCINA": [],
      "ESPEJOS": [],
      "ILUMINACIÓN": [],
      "MOBILIARIO": ["Camas", "Mesas de Noche", "Mobiliario Restaurante", "Mobiliario a Medida"],
      "ONE STOP SHOP": [],
      "PISOS - GUARDAESCOBAS": ["SPC Floor", "Guardaescobas"],
      "REVESTIMIENTOS": ["Panel Exterior", "Panel Interior"],
      "TARIMAS & EVENTOS": [],
  }
  ```
- Import `category_repository` from `app.repository.kompass_repository`
- Implement `seed_categories() -> dict` function:
  1. Iterate root categories, use `category_repository.get_by_name_and_parent(name, None)` to check existence
  2. If not found, use `category_repository.create(name=name)` to create
  3. Store root UUID in mappings dict with key = category name
  4. Iterate children using parent UUID, same check-then-create pattern
  5. Store child UUID with key = `"PARENT/CHILD"` (e.g., `"BAÑOS/Griferías"`)
  6. Print created/skipped for each category
  7. Return `{category_path: uuid_string}` dict
- Track and return counts: `{"created": N, "skipped": N}`
- Add `if __name__ == "__main__"` block

### Step 5: Create `seed_suppliers.py`
- Create `apps/Server/scripts/seed_suppliers.py`
- Add `sys.path.insert()` pattern
- Define `KNOWN_SUPPLIERS` list (25 names):
  ```python
  KNOWN_SUPPLIERS = [
      "BWBYONE", "BATH STORE-TAUSU", "CONRAZZO", "CU MATERIALS", "DHF",
      "FOSHAN SHISUO", "GEORGE", "HONGYU", "HUAYI", "JINGDA", "JVK",
      "LAYASDUN", "LEIZI", "LUXDREAM", "MAYORISTA COLOMBIA", "MEXY TECH",
      "NTFT YIFUYUAN", "PA HOME", "PINLSLON", "SENCHUAN", "SOTENG",
      "VAN-RUBEN", "WEIRE", "WIREKING", "WUXI KAIZE",
  ]
  ```
- Define default Excel path relative to repo root:
  ```
  Requirements_Gathering/Sourcing/Data/PROVEEDORES - CATALOGOS/CANTON FAIR _OCT _2025/DIRECTORIO PROVEEDORES CANTON FAIR _OCT_2025.xlsx
  ```
- Accept CLI argument for custom Excel path (`sys.argv[1]` if provided)
- Implement `normalize_name(name: str) -> str` helper: strip whitespace, uppercase, remove extra spaces
- Implement `find_matching_supplier(excel_name: str, known_list: list) -> Optional[str]` helper:
  - Normalize both names, try exact match first
  - Then try `startswith` / `in` containment matching
- Implement `seed_suppliers(excel_path: str) -> dict` function:
  1. Open Excel with `openpyxl.load_workbook(excel_path, read_only=True, data_only=True)`
  2. Access the `"BASE MASTER"` sheet
  3. Read header row to find column indices for: Proveedor, Contacto, Email, Ciudad, Pagina Web, Productos
  4. Iterate data rows, for each row:
     - Extract `Proveedor` value, check against `KNOWN_SUPPLIERS` using fuzzy match
     - If matched and not yet seen, use `supplier_repository.get_by_name(name)` to check DB
     - If not in DB, create via `supplier_repository.create()` with:
       - `name` = matched known supplier name (canonical)
       - `contact_name` from Contacto column
       - `contact_email` from Email column
       - `city` from Ciudad column
       - `website` from Pagina Web column
       - `notes` from Productos column
       - `country = "China"`, `status = "active"`
     - Store UUID in mappings
  5. Return `{supplier_name: uuid_string}` dict
- Track counts: `{"created": N, "skipped": N, "not_found_in_excel": [...]}`
- Add `if __name__ == "__main__"` block
- Note: `pipeline_status` defaults to `"contacted"` via DB schema default. The issue says `"quoted"` but this would need to be set after creation via `update_pipeline_status()`. For simplicity, create with defaults and then update pipeline_status to `"quoted"` via a separate update call, or pass it if the create method supports it. Since the basic `create()` method doesn't accept `pipeline_status`, we'll leave it at the DB default and document this.

### Step 6: Create `seed_hs_codes.py`
- Create `apps/Server/scripts/seed_hs_codes.py`
- Add `sys.path.insert()` pattern
- Import `hs_code_repository` from `app.repository.kompass_repository`
- Define hardcoded `HS_CODES` list:
  ```python
  HS_CODES = [
      {"code": "6910.10", "description": "Ceramic sanitaryware", "duty_rate": Decimal("15.00"), "notes": "Sanitarios y Muebles de Baño"},
      {"code": "7324.90", "description": "Sanitary ware, faucets", "duty_rate": Decimal("15.00"), "notes": "Griferías"},
      {"code": "9403.60", "description": "Wooden furniture", "duty_rate": Decimal("15.00"), "notes": "Mobiliario, Camas, Mesas de Noche"},
      {"code": "9403.20", "description": "Metal furniture", "duty_rate": Decimal("15.00"), "notes": "Mobiliario Restaurante"},
      {"code": "6907.21", "description": "Ceramic tiles/flags", "duty_rate": Decimal("10.00"), "notes": "REVESTIMIENTOS"},
      {"code": "9405.10", "description": "Chandeliers, lighting", "duty_rate": Decimal("15.00"), "notes": "ILUMINACIÓN"},
      {"code": "7013.49", "description": "Glassware, mirrors", "duty_rate": Decimal("15.00"), "notes": "ESPEJOS"},
      {"code": "3921.90", "description": "Plastic plates/sheets (SPC flooring)", "duty_rate": Decimal("10.00"), "notes": "SPC Floor, PISOS - GUARDAESCOBAS"},
      {"code": "7323.93", "description": "Stainless steel kitchenware", "duty_rate": Decimal("15.00"), "notes": "DOTACIÓN DE COCINA"},
      {"code": "3917.40", "description": "Plastic fittings (baseboards)", "duty_rate": Decimal("10.00"), "notes": "Guardaescobas"},
      {"code": "4411.14", "description": "MDF/fibreboard (decking)", "duty_rate": Decimal("5.00"), "notes": "DECK - FACHADAS"},
      {"code": "7324.10", "description": "Stainless steel sinks", "duty_rate": Decimal("15.00"), "notes": "Lavamanos"},
      {"code": "8481.80", "description": "Taps, valves, dispensers", "duty_rate": Decimal("10.00"), "notes": "DISPENSADORES"},
      {"code": "9401.61", "description": "Upholstered seating", "duty_rate": Decimal("15.00"), "notes": "Mobiliario a Medida"},
      {"code": "7610.90", "description": "Aluminum structures (stages)", "duty_rate": Decimal("10.00"), "notes": "TARIMAS & EVENTOS"},
  ]
  ```
- Implement `seed_hs_codes() -> dict` function:
  1. For each HS code entry, use `hs_code_repository.get_by_code(code)` to check existence
  2. If not found, use `hs_code_repository.create(code, description, duty_rate, notes)` to create
  3. Store UUID in mappings
  4. Print created/skipped for each
  5. Return `{hs_code: uuid_string}` dict
- Track counts: `{"created": N, "skipped": N}`
- Add `if __name__ == "__main__"` block

### Step 7: Create `seed_all.py` unified runner
- Create `apps/Server/scripts/seed_all.py`
- Add `sys.path.insert()` pattern
- Import seed functions from sibling modules:
  ```python
  from scripts.seed_categories import seed_categories
  from scripts.seed_suppliers import seed_suppliers
  from scripts.seed_hs_codes import seed_hs_codes
  ```
- Define default Excel path as constant
- Accept optional CLI argument for custom Excel path
- Implement `seed_all(excel_path: str) -> dict` function:
  1. Call `seed_categories()` → get categories mappings
  2. Call `seed_suppliers(excel_path)` → get supplier mappings
  3. Call `seed_hs_codes()` → get HS code mappings
  4. Combine into single dict: `{"categories": {...}, "suppliers": {...}, "hs_codes": {...}}`
  5. Write to `apps/Server/scripts/output/seed_mappings.json` using `json.dump()` with `indent=2`
  6. Print summary: counts of created vs skipped for each entity type
  7. Return combined mappings dict
- Add `if __name__ == "__main__"` block that calls `seed_all()`
- Ensure runnable via: `cd apps/Server && python -m scripts.seed_all`

### Step 8: Add `.gitignore` entry for scripts output
- Edit `.gitignore` to add `apps/Server/scripts/output/` under a new section or existing section

### Step 9: Write unit tests for repository helper methods
- Create `apps/Server/tests/test_kompass/test_repository_helpers.py`
- Follow existing test patterns from `test_supplier_e2e.py`:
  - Mock `get_database_connection` and `close_database_connection`
  - Test `CategoryRepository.get_by_name_and_parent()`:
    - Test finding existing root category (parent_id=None)
    - Test finding existing child category (parent_id=UUID)
    - Test returning None when not found
    - Test case-insensitivity (query with different casing)
    - Test database connection failure returns None
  - Test `SupplierRepository.get_by_name()`:
    - Test finding existing supplier by name
    - Test returning None when not found
    - Test case-insensitivity
    - Test database connection failure returns None
- Use `unittest.mock.patch` for database mocking
- Use factory functions from `conftest.py` for sample data

### Step 10: Run validation commands
- Run `cd apps/Server && .venv/bin/pytest tests/ -v --tb=short` to verify all tests pass
- Run `cd apps/Server && .venv/bin/ruff check .` to verify no lint issues
- Run `cd apps/Client && npm run typecheck` to verify no TypeScript regressions (should be unaffected)
- Run `cd apps/Client && npm run build` to verify build succeeds (should be unaffected)

## Testing Strategy
### Unit Tests
- **`CategoryRepository.get_by_name_and_parent()`**: Mock database cursor to return a row matching by name+parent_id. Verify correct SQL query is executed with LOWER() and IS NOT DISTINCT FROM. Test both root (parent_id=None) and child (parent_id=UUID) cases.
- **`SupplierRepository.get_by_name()`**: Mock database cursor to return a row matching by name. Verify correct SQL query with LOWER() and LIMIT 1. Test found and not-found cases.
- **Seeding script logic** (optional, covered by idempotency design): Could add integration tests if a test database is available, but the primary validation is running the scripts against the real database.

### Edge Cases
- Category with same name but different parent (e.g., two subcategories named "Panel" under different roots) — `get_by_name_and_parent()` disambiguates via parent_id
- Supplier names with extra whitespace, mixed casing, or slight variations in the Excel file — fuzzy matching normalizes
- Running seed scripts twice — idempotent, second run skips all existing records
- Canton Fair Excel missing expected columns or having empty rows — script handles gracefully with error logging
- Database connection failure mid-seeding — each operation uses independent connections (repository pattern), partial seeds are safe to re-run
- HS code with same code already exists — `get_by_code()` check prevents duplicate insert (plus UNIQUE constraint as safety net)

## Acceptance Criteria
- [ ] `CategoryRepository.get_by_name_and_parent()` works correctly (case-insensitive, handles NULL parent_id via IS NOT DISTINCT FROM)
- [ ] `SupplierRepository.get_by_name()` works correctly (case-insensitive, returns first match)
- [ ] Category tree seeding creates ~20 categories (11 roots + subcategories matching the folder structure)
- [ ] Supplier seeding creates up to 24 suppliers from the Canton Fair master Excel (only those in the known list)
- [ ] HS code seeding creates 15 HS codes with correct duty rates
- [ ] All scripts are idempotent — running twice produces no duplicates
- [ ] `seed_all.py` generates valid `seed_mappings.json` with categories, suppliers, and hs_codes sections
- [ ] Unit tests pass for the new repository helper methods
- [ ] All scripts can be run from `apps/Server/` directory via `python -m scripts.<name>`
- [ ] No lint errors (ruff check passes)
- [ ] No regressions in existing tests

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd /mnt/c/Users/user/danke_apps/Kompass/trees/aa50456e/apps/Server && .venv/bin/pytest tests/ -v --tb=short` - Run all Server tests including new repository helper tests
- `cd /mnt/c/Users/user/danke_apps/Kompass/trees/aa50456e/apps/Server && .venv/bin/ruff check .` - Run linting to verify no style issues
- `cd /mnt/c/Users/user/danke_apps/Kompass/trees/aa50456e/apps/Client && npm run typecheck` - Run Client type check (no regressions expected)
- `cd /mnt/c/Users/user/danke_apps/Kompass/trees/aa50456e/apps/Client && npm run build` - Run Client build (no regressions expected)

## Notes
- **No new dependencies required**: `openpyxl` is already in `requirements.txt`. `json`, `sys`, `os`, `decimal` are stdlib.
- **Pipeline status**: The issue specifies `pipeline_status = "quoted"` for seeded suppliers, but `SupplierRepository.create()` does not accept `pipeline_status` as a parameter. The DB default is `"contacted"`. Two options: (a) use `update_pipeline_status()` after creation, or (b) leave at default and note this for SCD-003. Recommend option (a) for completeness.
- **Canton Fair Excel path**: The path `Requirements_Gathering/Sourcing/Data/PROVEEDORES - CATALOGOS/CANTON FAIR _OCT _2025/DIRECTORIO PROVEEDORES CANTON FAIR _OCT_2025.xlsx` is relative to the repo root. The script should resolve this relative to the working directory or accept a CLI override.
- **Parallel with SCD-001**: This issue modifies `kompass_repository.py` (adding methods only, no changes to existing methods) and creates new scripts. SCD-001 modifies extraction-related files. No conflicts expected.
- **Seed mappings output**: The `seed_mappings.json` file in `scripts/output/` will be consumed by SCD-003 (Batch Product Import) to resolve supplier and category IDs during import. It contains UUIDs that are environment-specific, hence added to `.gitignore`.
- **IS NOT DISTINCT FROM**: This PostgreSQL-specific operator handles NULL comparison correctly (`NULL IS NOT DISTINCT FROM NULL` returns true), which is critical for matching root categories where `parent_id` is NULL.
