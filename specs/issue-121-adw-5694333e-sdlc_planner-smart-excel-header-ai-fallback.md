# Feature: Smart Excel Header Detection, AI Fallback & Confirm Import Fix

## Metadata
issue_number: `121`
adw_id: `5694333e`
issue_json: `{"number":121,"title":"[Kompass] SCD-001: Smart Excel Header Detection, AI Fallback & Confirm Import Fix"}`

## Feature Description
Enhance the Excel extraction pipeline to handle real-world supplier catalog formats from ~24 Chinese suppliers. Currently, `process_excel()` does exact-match-only on English column headers in row 0, which fails for files with headers at varying rows (1, 2, 3, 7, or 8), Spanish column names, or diverse price unit formats. This feature adds multi-row header scanning (first 10 rows), Spanish/variant column name matching via substring/contains logic, unit-of-measure detection from price column headers, AI fallback for unrecognized sheets, a new `unit_of_measure` field on `ExtractedProduct`, and fixes lost fields (material, category_id) during the confirm import step.

## User Story
As a Kompass operator importing supplier catalog Excel files
I want the system to intelligently detect column headers regardless of row position, language (English/Spanish), or naming conventions
So that I can reliably import product data from diverse real-world supplier catalogs without manual reformatting

## Problem Statement
The current Excel extraction pipeline only checks row 0 for headers using exact-match against a small list of English-only column names. Real supplier files have headers at varying rows, use Spanish column names (PRODUCTO, PRECIO, REFERENCIA), and include format variants (FOB U/P, Unit Price(USD), Price (USD/m2)). When columns aren't matched, product fields are silently dropped. Additionally, `material` and `category_id` are lost during the confirm import step, and there's no AI fallback for Excel files with completely unrecognizable formats.

## Solution Statement
1. **Smart multi-row header scanning**: Scan first 10 rows of each sheet, scoring each row by how many of the 7 column categories (SKU, Name, Price, MOQ, Description, Material, Dimensions) it matches. The highest-scoring row becomes the header row.
2. **Expanded column names + substring matching**: Replace exact matching with contains/substring matching and add Spanish terms plus format variants to all column candidate lists.
3. **Unit-of-measure detection**: Parse the matched price column header text for unit hints (m2, pcs, set, etc.) and populate `unit_of_measure` on `ExtractedProduct`.
4. **AI fallback**: When fewer than 2 column categories match after scanning all 10 rows, serialize the first 50 data rows as a text table and send to the existing AI provider for structured extraction.
5. **DTO additions**: Add `unit_of_measure` to `ExtractedProduct` and `category_id` to `ConfirmImportRequestDTO`.
6. **Confirm import fix**: Map `unit_of_measure`, append `material` to description, and pass `category_id` through during product creation.

## Relevant Files
Use these files to implement the feature:

- `apps/Server/app/services/extraction_service.py` — Main file to modify. Contains `process_excel()` (line 337), `find_column()` helper (line 371), column name mappings (lines 362-369), `_build_extraction_prompt()` (line 84), `_extract_with_anthropic()` (line 146), `_extract_with_openai()` (line 194), `_parse_extraction_response()` (line 101), `_is_ai_available()` (line 64), `_get_preferred_ai_provider()` (line 70). All core changes for 1A, 1B happen here.
- `apps/Server/app/models/extraction_dto.py` — Contains `ExtractedProduct` class (line 17). Add `unit_of_measure` field here (1C).
- `apps/Server/app/models/extraction_job_dto.py` — Contains `ConfirmImportRequestDTO` (line 42). Add `category_id` field here (1D).
- `apps/Server/app/api/extraction_routes.py` — Contains confirm import endpoint (line 345). Fix product conversion logic at lines 414-428 (1D).
- `apps/Server/app/models/kompass_dto.py` — Contains `ProductCreateDTO` (line 642). Reference only — already has `unit_of_measure`, `category_id`, `description` fields.
- `apps/Server/tests/test_extraction_service.py` — Existing extraction service tests. Add new tests for multi-row header detection, Spanish columns, substring matching, unit-of-measure detection, AI fallback.
- `apps/Server/tests/test_extraction_routes.py` — Existing extraction route tests. Add tests for confirm import with material/category_id/unit_of_measure mapping.
- Read `app_docs/feature-dc759ae8-ai-data-extraction-service.md` — Documentation for the extraction service implementation
- Read `app_docs/feature-1ee9c0ae-data-extraction-api-routes.md` — Documentation for the extraction routes implementation

## Implementation Plan
### Phase 1: Foundation
Add the `unit_of_measure` field to `ExtractedProduct` DTO and `category_id` to `ConfirmImportRequestDTO`. These are additive, backward-compatible changes that subsequent work depends on.

### Phase 2: Core Implementation
Refactor `process_excel()` in `extraction_service.py`:
1. Expand column candidate lists with Spanish terms and format variants.
2. Replace `find_column()` with a new `_find_best_header_row()` method that scans up to 10 rows using substring/contains matching, returning the best header row index and column mapping.
3. Add unit-of-measure detection from the matched price column header.
4. Add AI fallback path: when fewer than 2 column categories match, serialize data rows as a text table and send to AI using the existing provider infrastructure.
5. Parse AI response into `ExtractedProduct` objects using the existing `_parse_extraction_response()` method (adapted for multi-product responses).

### Phase 3: Integration
Fix the confirm import endpoint to map `unit_of_measure`, append `material` to description, and pass `category_id` through to `ProductCreateDTO`. Add comprehensive unit tests throughout.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Add `unit_of_measure` field to ExtractedProduct DTO
- Open `apps/Server/app/models/extraction_dto.py`
- Add `unit_of_measure: Optional[str] = Field(default=None, max_length=50)` to the `ExtractedProduct` class after `source_page` (line 31)
- This is purely additive and backward-compatible

### Step 2: Add `category_id` field to ConfirmImportRequestDTO
- Open `apps/Server/app/models/extraction_job_dto.py`
- Add `from uuid import UUID` to imports (already imported)
- Add `category_id: Optional[UUID] = None` to `ConfirmImportRequestDTO` after `supplier_id` (line 50)

### Step 3: Expand column name candidates and implement substring matching in `process_excel()`
- Open `apps/Server/app/services/extraction_service.py`
- Replace the column name lists (lines 362-369) with expanded lists including Spanish terms and format variants:
  - `sku_columns`: add `"referencia"`, `"ref."`, `"modelo"`, `"item no"`, `"item no."`, `"no."`, `"code"`
  - `name_columns`: add `"producto"`, `"descripcion producto"`, `"nombre"`, `"product type"`
  - `price_columns`: add `"precio"`, `"fob u/p"`, `"u/p"`, `"unit price(usd)"`, `"price (usd/m2)"`, `"costo unitario"`
  - `moq_columns`: add `"qty"`, `"quantity"`, `"cantidad"`
  - `dimensions_columns`: add `"size(mm)"`, `"specification"`, `"medida"` (note: `"size"` is already present)
  - `material_columns`: add `"finish"`, `"acabado"`, `"surface"`, `"collection"`
- Replace the `find_column()` function with a new version that uses **substring/contains matching**: for each header cell, check if any candidate string is contained in the lowercased header OR if the lowercased header is contained in any candidate. This allows matching headers like `"FOB U/P (USD)"` against candidate `"fob u/p"`.

### Step 4: Implement multi-row header scanning (best header row detection)
- In `process_excel()`, replace the current logic that reads headers from only `rows[0]` (line 387)
- Instead, scan up to the first 10 rows (or all rows if fewer):
  - For each candidate row, convert cells to strings, run the substring-matching `find_column()` for all 7 column categories
  - Score each row = number of column categories that matched at least one column
  - Pick the row with the highest score as the header row
  - Use data rows starting from `header_row_index + 1`
- Store the column category mappings as a dict: `{"sku": col_idx, "name": col_idx, "price": col_idx, ...}`
- Define the minimum threshold: proceed with programmatic extraction if score >= 2

### Step 5: Implement unit-of-measure detection from price column header
- After identifying the price column, inspect the original header text for unit hints
- Define a unit mapping dict: `{"m2": "m2", "sqm": "m2", "m²": "m2", "pcs": "piece", "pc": "piece", "piece": "piece", "set": "set", "pair": "pair", "kg": "kg", "ton": "ton", "meter": "meter", "m ": "meter"}`
- Search the price column header text (lowercased) for any of these unit keywords
- If found, set the detected `unit_of_measure` value; otherwise default to `None`
- Pass this `unit_of_measure` into each `ExtractedProduct` created from that sheet

### Step 6: Implement AI fallback for unrecognized Excel formats
- In `process_excel()`, after the header scanning loop, if the best header row score is < 2 for a sheet:
  - Log: `print(f"WARN [ExtractionService]: AI fallback used for sheet '{sheet.title}' - no header matches found")`
  - Check `self._is_ai_available()` — if AI not available, log a warning and skip the sheet
  - Serialize the first 50 data rows (from the sheet) as a formatted text table string (pipe-separated columns with a header row of column letters or numeric indices)
  - Build a specialized AI prompt for table extraction:
    ```
    Extract product data from this spreadsheet table. Each row may represent a product.
    Return a JSON array of objects, each with: sku, name, description, price_fob_usd (decimal), moq (integer), dimensions, material.
    Use null for missing values. Only return valid JSON array, no additional text.

    Table data:
    {table_text}
    ```
  - Send to AI using the existing provider pattern (`_get_preferred_ai_provider()`, then call `_extract_with_anthropic()` or `_extract_with_openai()`) with `max_tokens=4096`
  - Create a new helper `_extract_excel_with_ai()` that:
    - Calls the preferred AI provider with the table prompt
    - Parses the response as a JSON array
    - Converts each item into an `ExtractedProduct` using `_parse_extraction_response()` for each object (or direct construction)
    - Sets `confidence_score` based on fields present (same formula as `_parse_extraction_response()`)
  - Append the resulting products to the sheet's product list

### Step 7: Fix confirm import endpoint — map unit_of_measure, material, and category_id
- Open `apps/Server/app/api/extraction_routes.py`
- In the product conversion loop (lines 414-428), modify the `ProductCreateDTO` creation:
  - Add `unit_of_measure=extracted.unit_of_measure or "piece"` (falls back to the DTO default)
  - Build description: if `extracted.material` is present, append `"\nMaterial: {extracted.material}"` to the description
  - Add `category_id=request.category_id` to pass the category from the request DTO
- Ensure `minimum_order_qty=extracted.moq or 1` is already there (confirmed it is at line 425)

### Step 8: Write unit tests for multi-row header detection
- Open `apps/Server/tests/test_extraction_service.py`
- Add a new test class `TestSmartHeaderDetection` with these tests:
  - `test_finds_header_in_row_0`: Standard case — headers in first row (backward compatibility)
  - `test_finds_header_in_row_3`: Headers in row 3 with empty/metadata rows above
  - `test_finds_header_in_row_7`: Headers deep in the file (row 7)
  - `test_spanish_column_names`: Headers like "REFERENCIA", "PRODUCTO", "PRECIO", "CANTIDAD"
  - `test_mixed_language_columns`: Mix of English and Spanish headers
  - `test_substring_matching_fob_up`: Header "FOB U/P (USD)" matches price column
  - `test_substring_matching_unit_price_usd`: Header "Unit Price(USD)" matches price column
  - `test_unit_of_measure_from_price_header_m2`: Header "Price (USD/m2)" → unit_of_measure = "m2"
  - `test_unit_of_measure_from_price_header_pcs`: Header "Price/pcs" → unit_of_measure = "piece"
  - `test_unit_of_measure_default_none`: Standard "Price" header → unit_of_measure = None
- Each test should create a temporary Excel file with `openpyxl`, call `process_excel()`, and assert the expected products and field values

### Step 9: Write unit tests for AI fallback path
- Add a new test class `TestExcelAIFallback` with these tests:
  - `test_ai_fallback_triggers_on_low_column_match`: Create an Excel file with unrecognizable headers (e.g., "A", "B", "C"), mock the AI provider to return a JSON array of products, verify products are extracted
  - `test_ai_fallback_skipped_when_ai_unavailable`: Same unrecognizable headers but no AI keys configured — verify empty products and warning
  - `test_ai_fallback_not_triggered_when_columns_match`: Standard headers — verify AI is NOT called
- Use `unittest.mock.patch` on `_extract_with_anthropic` or `_extract_with_openai` to mock AI responses
- Verify the warning log message is printed when fallback activates

### Step 10: Write unit tests for confirm import field mapping
- Open `apps/Server/tests/test_extraction_routes.py`
- Add tests to the existing `TestConfirmImport` class or create a new `TestConfirmImportFieldMapping` class:
  - `test_confirm_maps_unit_of_measure`: Verify `unit_of_measure` from `ExtractedProduct` flows through to `ProductCreateDTO`
  - `test_confirm_appends_material_to_description`: Verify material is appended as `"\nMaterial: {material}"` in the product description
  - `test_confirm_passes_category_id`: Verify `category_id` from the request is passed to all created products
  - `test_confirm_handles_none_material`: Verify no material appendage when material is None

### Step 11: Run validation commands
- Run `cd apps/Server && python -m pytest tests/ -v --tb=short` to validate all existing and new tests pass
- Run `cd apps/Client && npx tsc --noEmit` to validate no TypeScript regressions (confirm import DTO changes are backend-only)
- Run `cd apps/Client && npm run build` to validate client build succeeds

## Testing Strategy
### Unit Tests
- **Multi-row header detection**: Test Excel files with headers at rows 0, 3, 7, and 8 to verify the best-header-row algorithm works across all positions
- **Spanish/variant column matching**: Test with Spanish-only headers, mixed English/Spanish headers, and format-variant headers (FOB U/P, Unit Price(USD))
- **Substring matching**: Test that partial matches work (header containing "price" matches price column) while avoiding false positives
- **Unit-of-measure detection**: Test extraction of m2, pcs, set, kg, and default None from various price header formats
- **AI fallback**: Mock AI responses to test the fallback path triggers correctly (<2 matches), parses responses, and handles errors gracefully
- **Confirm import mapping**: Test that unit_of_measure, material (appended to description), and category_id flow through correctly

### Edge Cases
- Excel file where ALL rows are data (no recognizable headers at all) — should trigger AI fallback
- Excel file with multiple sheets where some have recognizable headers and others don't — mixed programmatic + AI extraction
- Excel with empty header cells interspersed with valid ones
- Price column header with multiple unit hints (e.g., "Price USD/m2/pcs") — should pick the first match
- Very long table (>50 rows) sent to AI fallback — should only send first 50 rows
- AI returns malformed JSON — should handle gracefully with empty products and error logged
- Column header is just whitespace or None — should not match any category
- Backward compatibility: Excel files that work today must continue to work identically

## Acceptance Criteria
- [ ] Header detection scans first 10 rows and picks the row with the most column matches
- [ ] Spanish column names (PRODUCTO, PRECIO, REFERENCIA, CANTIDAD, etc.) are recognized
- [ ] Substring matching works (header "FOB U/P (USD)" matches price column)
- [ ] Unit of measure is detected from price column headers (m2, pcs, etc.)
- [ ] AI fallback activates when fewer than 2 columns match, returning valid ExtractedProduct objects
- [ ] AI fallback logs a WARN message when triggered
- [ ] AI fallback uses max_tokens=4096 for table-extraction requests
- [ ] `unit_of_measure` field added to ExtractedProduct DTO (Optional[str], max_length=50)
- [ ] `category_id` field added to ConfirmImportRequestDTO (Optional[UUID])
- [ ] `unit_of_measure` is mapped from ExtractedProduct to ProductCreateDTO during confirm import
- [ ] Material is appended to description as "\nMaterial: {material}" during confirm import
- [ ] `category_id` is passed through from ConfirmImportRequestDTO to all created ProductCreateDTOs
- [ ] All existing extraction tests still pass (backward compatibility)
- [ ] New unit tests for multi-row header detection with Spanish column names (10+ test cases)
- [ ] New unit test for AI fallback path (mocked AI response, 3+ test cases)
- [ ] New unit tests for confirm import field mapping (4+ test cases)

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -m pytest tests/test_extraction_service.py -v --tb=short` — Run extraction service tests including all new header detection and AI fallback tests
- `cd apps/Server && python -m pytest tests/test_extraction_routes.py -v --tb=short` — Run extraction route tests including new confirm import field mapping tests
- `cd apps/Server && python -m pytest tests/ -v --tb=short` — Run full server test suite to validate zero regressions
- `cd apps/Server && python -m ruff check .` — Run Python linter to validate code quality
- `cd apps/Client && npx tsc --noEmit` — Run TypeScript type check (no frontend changes expected, but validates no regressions)
- `cd apps/Client && npm run build` — Run client build to validate no regressions

## Notes
- **No new dependencies needed**: `openpyxl` is already installed for Excel processing, and the Anthropic/OpenAI clients are already configured in `extraction_service.py`.
- **AI model for fallback**: Reuse the same model (`claude-sonnet-4-20250514` for Anthropic, `gpt-4o` for OpenAI) already configured in the service, but increase `max_tokens` to 4096 for table extraction.
- **Backward compatibility is critical**: The `find_column()` change from exact to substring matching must be verified against existing test cases. All 3 existing Excel test cases (`test_processes_excel_with_standard_columns`, `test_processes_excel_with_alternative_columns`, `test_skips_empty_rows`) must continue to pass.
- **Parallel execution**: This issue (SCD-001) runs in parallel with SCD-002 (Repository Helpers + Reference Data Seeding). They touch completely different files — no conflicts expected.
- **The `moq` field IS already mapped** in the confirm import endpoint at line 425 (`minimum_order_qty=extracted.moq or 1`). The issue description's concern about lost fields applies to `material`, `unit_of_measure`, and `category_id` only.
- **Frontend impact**: No frontend changes are needed for this issue. The `ExtractedProduct` DTO change (adding `unit_of_measure`) is backward-compatible since it's Optional with default None. The frontend Import Wizard will automatically display the new field if it extends its product table.
