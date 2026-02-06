# Feature: Supplier Verification Data Export to Excel

## Metadata
issue_number: `103`
adw_id: `28c175cd`
issue_json: `{"number":103,"title":"Add Supplier verification data export to excel","body":"Currently, the supplier verification for certification process extracts the information and shows it on screen. The user would find it useful to be able to export all the supplier verification data for all suppliers to Excel. \n\nIt would be an export that includes all suppliers that satisfy a selection criteria."}`

## Feature Description
Add the ability to export supplier verification and certification data to an Excel (.xlsx) file. Currently, supplier verification data (extracted from factory audit PDFs via AI) is only viewable on-screen in the Certification tab of each supplier. This feature will allow users to export a comprehensive spreadsheet containing verification data for multiple suppliers at once, filtered by the same criteria available in the Suppliers page (status, certification status, pipeline status, search query). The Excel file will include supplier basic info, certification status, and all extracted audit data (supplier type, employee count, factory area, production lines, certifications, markets served, positive/negative points, classification grades, etc.).

## User Story
As a sourcing manager
I want to export all supplier verification data to an Excel spreadsheet filtered by my selection criteria
So that I can analyze, share, and report on supplier qualification data outside the application without manually reviewing each supplier individually

## Problem Statement
Supplier verification data (extracted from factory audit documents) is currently only accessible by navigating to each individual supplier's Certification tab. For users who need to review, compare, or share verification data across multiple suppliers, this is time-consuming and impractical. There is no way to get a consolidated view of all supplier verification data in a downloadable format.

## Solution Statement
Implement a backend endpoint that queries suppliers with their latest audit data based on filter criteria, generates an Excel workbook using `openpyxl` (already in requirements.txt), and returns it as a downloadable file. Add an "Export Excel" button to the Suppliers page that triggers the download using the current filter state. The export will follow the same patterns used by the existing PDF export for portfolios and quotations (StreamingResponse with blob download on the frontend).

## Relevant Files
Use these files to implement the feature:

### Backend
- `apps/Server/app/api/supplier_routes.py` — Add new `GET /export/excel` endpoint here, following patterns from existing routes. Place it before `/{supplier_id}` path routes to avoid path conflicts.
- `apps/Server/app/services/supplier_service.py` — Add `export_verification_excel()` method that queries data and generates the Excel file using openpyxl.
- `apps/Server/app/repository/kompass_repository.py` — Add `get_all_with_audit_data()` method to `SupplierRepository` that JOINs suppliers with their latest audit data. Use the existing `get_all_with_filters()` method (line 1521) as a pattern for filtering, but extend the SELECT to include audit fields.
- `apps/Server/app/models/kompass_dto.py` — Reference only; no new DTOs needed since the endpoint returns a file, not JSON.
- `apps/Server/database/schema.sql` — Reference for `suppliers` table (line 111) and `supplier_audits` table (line 143) schema to understand all available fields.
- `apps/Server/main.py` — Reference only; supplier routes already registered at line 75.
- `apps/Server/requirements.txt` — Reference only; `openpyxl>=3.1.0` already listed (line 39).

### Frontend
- `apps/Client/src/pages/kompass/SuppliersPage.tsx` — Add "Export Excel" button next to the "Add Supplier" button in the header area (line 429). Wire it to call the new export service method with current filter state.
- `apps/Client/src/services/kompassService.ts` — Add `exportVerificationExcel()` method to `supplierService` object. Follow the existing `exportPdf` blob download pattern (line 498-504).
- `apps/Client/src/api/clients/index.ts` — Reference only; the apiClient is already configured.
- `apps/Client/src/types/kompass.ts` — Reference only; existing types are sufficient.

### Testing & E2E
- `.claude/commands/test_e2e.md` — Read to understand E2E test runner pattern.
- `.claude/commands/e2e/test_suppliers_page.md` — Read as reference for existing suppliers page E2E test structure.
- `apps/Server/tests/` — Add unit test for the export endpoint.

### New Files
- `.claude/commands/e2e/test_supplier_verification_export.md` — New E2E test file for validating the export functionality.

## Implementation Plan
### Phase 1: Foundation
Add the repository method that queries suppliers joined with their latest audit data, supporting the same filters as the existing supplier list. This is the data layer that powers the export.

### Phase 2: Core Implementation
Create the Excel generation logic in the supplier service using openpyxl. Build a well-formatted workbook with a single sheet containing supplier info columns and audit extraction columns. Add the API endpoint that accepts filter parameters and returns the Excel file as a StreamingResponse.

### Phase 3: Integration
Add the "Export Excel" button to the Suppliers page frontend, wire it to the backend endpoint using the current filter state, and trigger a browser file download. Create E2E test to validate the complete flow.

## Step by Step Tasks

### Step 1: Create E2E Test File
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_suppliers_page.md` to understand E2E test patterns
- Create `.claude/commands/e2e/test_supplier_verification_export.md` with the following test steps:
  1. Navigate to Suppliers page, verify it loads
  2. Verify "Export Excel" button is visible in the header toolbar area
  3. Click "Export Excel" button with no filters applied — verify download triggers (check for no error, button shows loading state, then returns to normal)
  4. Apply certification filter (e.g., "Certified (Any)") and click "Export Excel" again — verify download triggers with filters
  5. Apply search filter and click "Export Excel" — verify download triggers
  6. Screenshots at each step

### Step 2: Add Repository Method for Supplier + Audit Data Query
- Open `apps/Server/app/repository/kompass_repository.py`
- Add a new method `get_all_with_audit_data()` to the `SupplierRepository` class
- The method should:
  - Accept the same filter parameters as `get_all_with_filters()`: `status`, `country`, `has_products`, `certification_status`, `pipeline_status`, `search`, `sort_by`, `sort_order`
  - NOT paginate (export all matching results, not just one page)
  - JOIN `suppliers s` with `supplier_audits a ON s.latest_audit_id = a.id` (LEFT JOIN so suppliers without audits are included)
  - SELECT all supplier fields plus audit extracted data fields: `supplier_type`, `employee_count`, `factory_area_sqm`, `production_lines_count`, `markets_served`, `certifications`, `has_machinery_photos`, `positive_points`, `negative_points`, `products_verified`, `audit_date`, `inspector_name`, `extraction_status`, `ai_classification`, `ai_classification_reason`, `manual_classification`, `classification_notes`
  - Return `List[Dict[str, Any]]` (no pagination tuple needed)
  - Reuse the same WHERE clause logic from `get_all_with_filters()` for consistency
  - Add a safety limit of 5000 rows to prevent memory issues

### Step 3: Add Excel Generation Method to Supplier Service
- Open `apps/Server/app/services/supplier_service.py`
- Add `export_verification_excel()` method that:
  - Accepts the same filter parameters as the list endpoint
  - Calls `supplier_repository.get_all_with_audit_data()` with those filters
  - Uses `openpyxl` to create a workbook with a single sheet named "Supplier Verification Data"
  - Defines columns in this order:
    - **Supplier Info**: Name, Code, Status, Country, City, Contact Name, Contact Email, Contact Phone, Website
    - **Certification Info**: Certification Status, Pipeline Status, Certified At
    - **Audit Info**: Audit Date, Inspector Name, Extraction Status
    - **Extracted Data**: Supplier Type, Employee Count, Factory Area (sqm), Production Lines, Certifications (joined with ", "), Markets Served (formatted as "Region: X%" pairs), Has Machinery Photos, Positive Points (joined with "; "), Negative Points (joined with "; "), Products Verified (joined with ", ")
    - **Classification**: AI Classification, AI Classification Reason, Manual Classification, Classification Notes
  - Formats the header row with bold font and a light background fill color
  - Auto-sizes column widths (approximate based on header length, with a max of 50 chars)
  - Converts list/dict fields to readable strings (e.g., `certifications` array → comma-separated string, `markets_served` dict → "Region1: 30%, Region2: 70%")
  - Saves the workbook to a `BytesIO` buffer and returns the bytes
  - Returns `None` if no data found (empty result set should still return a file with just headers)
  - Actually, return the Excel bytes even for empty results (just headers) so the user knows the export worked but there are no matching suppliers

### Step 4: Add Export Endpoint to Supplier Routes
- Open `apps/Server/app/api/supplier_routes.py`
- Add import for `StreamingResponse` from `fastapi.responses` and `io` module
- Add a new `GET /export/excel` endpoint **before** the `/{supplier_id}` route (to avoid path conflicts with the UUID parameter)
- The endpoint should:
  - Accept the same query parameters as `list_suppliers`: `status`, `country`, `has_products`, `certification_status`, `pipeline_status`, `search`, `sort_by`, `sort_order`
  - Require authentication via `get_current_user` dependency
  - Call `supplier_service.export_verification_excel()` with filter parameters
  - Return a `StreamingResponse` with:
    - `media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"`
    - `Content-Disposition` header with filename like `"supplier_verification_export_YYYY-MM-DD.xlsx"`
  - Handle errors gracefully with appropriate HTTP status codes

### Step 5: Add Frontend Service Method for Excel Export
- Open `apps/Client/src/services/kompassService.ts`
- Add `exportVerificationExcel()` method to the `supplierService` object
- Follow the existing `portfolioService.exportPdf()` pattern (line 498-504):
  - Accept a `filters?: SupplierListFilters` parameter
  - Make a GET request to `/suppliers/export/excel` with filter params
  - Set `responseType: 'blob'`
  - Return the blob response data

### Step 6: Add Export Button to Suppliers Page
- Open `apps/Client/src/pages/kompass/SuppliersPage.tsx`
- Import `FileDownloadIcon` from `@mui/icons-material/FileDownload` (or `DownloadIcon` from `@mui/icons-material/Download`)
- Add state: `const [exporting, setExporting] = useState(false);`
- Add a `handleExportExcel` async function that:
  - Sets `exporting` to `true`
  - Builds the filter object from current state (same filters used by `fetchSuppliers`)
  - Calls `supplierService.exportVerificationExcel(filters)`
  - Creates a blob URL from the response and triggers a download using an anchor element (`document.createElement('a')`, set `href` to blob URL, set `download` to filename, click, then revoke URL)
  - Handles errors by showing an error alert
  - Sets `exporting` to `false` in a finally block
- Add a "Export Excel" button in the header area (line 429, inside the `Box display="flex" gap={2}` next to the view toggle and "Add Supplier" button):
  - Use `variant="outlined"` to visually differentiate from the primary "Add Supplier" button
  - Add `startIcon={<FileDownloadIcon />}`
  - Show `CircularProgress` in place of icon when `exporting` is true
  - Disable the button when `exporting` is true
  - Text: "Export Excel"

### Step 7: Add Backend Unit Test
- Create or add to the existing test file for supplier routes
- Test the export endpoint:
  - Test that the endpoint returns 200 with correct content type
  - Test that the endpoint requires authentication
  - Test that filters are passed through correctly
  - Test that the Excel file can be parsed by openpyxl and has the expected header row

### Step 8: Run Validation Commands
- Run all validation commands listed below to verify zero regressions

## Testing Strategy
### Unit Tests
- Test `supplier_repository.get_all_with_audit_data()` returns correct data structure with joined audit fields
- Test `supplier_service.export_verification_excel()` generates valid Excel bytes with correct headers and data formatting
- Test `GET /suppliers/export/excel` returns correct content type and disposition header
- Test that filters are properly applied (certification_status, pipeline_status, search, etc.)
- Test export with no matching suppliers returns Excel with only headers

### Edge Cases
- Supplier with no audit data (latest_audit_id is NULL) — should still appear in export with blank audit columns
- Supplier with audit but extraction failed — should show extraction_status as "failed" and blank extracted fields
- Array fields that are NULL vs empty array — handle both gracefully
- `markets_served` JSONB that is NULL or empty dict — handle gracefully
- Very long text in positive_points/negative_points — should not break Excel formatting
- Unicode characters in supplier names and audit data — openpyxl handles this natively
- Large number of suppliers (5000 limit enforced by repository)
- All filters applied simultaneously

## Acceptance Criteria
- An "Export Excel" button is visible on the Suppliers page header, next to the existing buttons
- Clicking the button downloads an .xlsx file named `supplier_verification_export_YYYY-MM-DD.xlsx`
- The Excel file contains one row per supplier (matching current filters)
- Each row includes: supplier basic info, certification status, pipeline status, and all extracted audit data from the latest audit
- Array fields (certifications, positive_points, negative_points, products_verified) are formatted as readable comma/semicolon-separated strings
- Markets served JSONB is formatted as readable "Region: X%" pairs
- The header row is visually formatted (bold, background color)
- The export respects the current page filters (status, certification, pipeline, search)
- Suppliers without audit data are included with blank audit columns
- The button shows a loading state while the export is being generated
- No console errors during the export flow
- All existing tests continue to pass
- TypeScript compiles without errors
- Frontend builds successfully

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_supplier_verification_export.md` test file to validate this functionality works.
- `cd apps/Server && .venv/bin/pytest tests/ -v --tb=short` - Run Server tests to validate the feature works with zero regressions
- `cd apps/Client && npx tsc --noEmit` - Run Client type check to validate the feature works with zero regressions
- `cd apps/Client && npm run build` - Run Client build to validate the feature works with zero regressions

## Notes
- `openpyxl>=3.1.0` is already in `apps/Server/requirements.txt` (line 39), so **no new dependencies are needed**.
- The existing PDF export pattern (StreamingResponse + blob download) is well-established in the codebase for both portfolios and quotations, so this Excel export follows the same proven pattern.
- The `/export/excel` route MUST be placed before the `/{supplier_id}` route in `supplier_routes.py` to avoid FastAPI interpreting "export" as a UUID parameter.
- Column auto-sizing in openpyxl is approximate (based on character count) since true auto-fit requires rendering; use a reasonable max width of ~50 characters.
- Future enhancement: consider adding sheet-level Excel filters (autofilter) so users can further filter within Excel.
- The `markets_served` field is a JSONB dict with keys like "Asia", "Europe", "North America" and percentage values. Format as: "Asia: 60%, Europe: 30%, North America: 10%".
