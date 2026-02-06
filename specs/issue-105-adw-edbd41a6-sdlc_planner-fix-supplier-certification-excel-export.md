# Bug: Fix Supplier Certification Excel Export Missing Data

## Metadata
issue_number: `105`
adw_id: `edbd41a6`
issue_json: `{"number":105,"title":"Excel export for supplier certifiaction does not show data","body":"The supplier certification process is extracting the information and showing a report on screen. However, the data that is extracted is needed to be exported in the Excel export that is available in the corresponding module. When I export the excel, this data is not populated."}`

## Bug Description
The Suppliers page has an "Export Excel" button that exports supplier verification data including audit/certification information. When clicked, the Excel file is generated and downloaded, but all audit-related columns (supplier type, employee count, factory area, certifications, positive/negative points, classification, etc.) are empty — even though the same data displays correctly on screen in the Supplier Certification Tab.

**Expected behavior:** Excel export includes all extracted audit data (supplier type, employee count, factory area, markets served, certifications, positive/negative points, products verified, classification, etc.) for each supplier that has had an audit processed.

**Actual behavior:** Excel export contains supplier basic info (name, code, status, etc.) but all audit-related columns are empty/blank.

## Problem Statement
The Excel export SQL query joins `suppliers` to `supplier_audits` using `s.latest_audit_id = a.id`, but `latest_audit_id` is only set on the `suppliers` table when a classification is performed (AI or manual override). If a supplier has an audit uploaded and extracted but not yet classified, `latest_audit_id` remains NULL and the LEFT JOIN returns no audit data.

In contrast, the on-screen Certification Tab works correctly because it queries `supplier_audits WHERE supplier_id = %s` directly — it does not depend on `latest_audit_id`.

## Solution Statement
Change the SQL query in `get_all_with_audit_data()` to join on the latest audit per supplier using a subquery that finds the most recent audit by `supplier_id`, instead of relying on `latest_audit_id`. This makes the Excel export work for all suppliers with audits, regardless of classification status.

Replace:
```sql
LEFT JOIN supplier_audits a ON s.latest_audit_id = a.id
```

With:
```sql
LEFT JOIN supplier_audits a ON a.id = (
    SELECT sa.id FROM supplier_audits sa
    WHERE sa.supplier_id = s.id
    ORDER BY sa.created_at DESC
    LIMIT 1
)
```

This is a single-line SQL change in the repository layer. No other code changes are needed — the column selection, mapping, and Excel generation logic are all correct.

## Steps to Reproduce
1. Navigate to the Suppliers page
2. Open a supplier and go to the Certification tab
3. Upload an audit PDF and wait for extraction to complete
4. Observe that the extracted data (supplier type, employee count, certifications, etc.) displays correctly on screen
5. Go back to the Suppliers list page
6. Click the "Export Excel" button
7. Open the downloaded Excel file
8. Observe that audit-related columns (columns beyond the basic supplier info) are all empty

## Root Cause Analysis
The root cause is a data access mismatch between the on-screen display and the Excel export:

1. **On-screen (works):** `SupplierCertificationTab` → `auditService.list(supplierId)` → `GET /suppliers/{id}/audits` → `SELECT ... FROM supplier_audits WHERE supplier_id = %s` — queries audits directly by `supplier_id`, always finds audits.

2. **Excel export (broken):** `handleExportExcel` → `supplierService.exportVerificationExcel()` → `GET /suppliers/export/excel` → `supplier_repository.get_all_with_audit_data()` → `LEFT JOIN supplier_audits a ON s.latest_audit_id = a.id` — depends on `latest_audit_id` being set on the suppliers table.

3. **`latest_audit_id` is only set** in `SupplierRepository.update_certification_status()` which is called from `AuditService._update_supplier_certification()` — and that method is only invoked after AI classification completes or a manual override is performed. For suppliers that have audits extracted but not yet classified, `latest_audit_id` is NULL.

4. **Result:** The LEFT JOIN returns NULL for all audit columns, producing empty cells in the Excel export.

## Relevant Files
Use these files to fix the bug:

- `apps/Server/app/repository/kompass_repository.py` — Contains `get_all_with_audit_data()` method (line 1655) with the broken SQL JOIN on `s.latest_audit_id = a.id`. **This is the only file that needs to be modified.**
- `apps/Server/app/services/supplier_service.py` — Contains `export_verification_excel()` method (line 552) that calls the repository and generates the Excel. No changes needed but useful for understanding the full flow.
- `apps/Server/app/services/audit_service.py` — Contains `_update_supplier_certification()` (line 753) that sets `latest_audit_id`. Confirms the root cause — no changes needed.
- `apps/Server/tests/api/test_supplier_routes.py` — Contains `TestExportVerificationExcel` test class (line 484). Tests use mocks so they don't test the actual SQL. A new integration-style unit test should validate the fix.
- `apps/Client/src/pages/kompass/SuppliersPage.tsx` — Contains `handleExportExcel` (line 292). No changes needed but confirms the frontend flow.
- `apps/Client/src/services/kompassService.ts` — Contains `exportVerificationExcel()` API call (line 228). No changes needed.
- `.claude/commands/test_e2e.md` — E2E test runner instructions for creating and running E2E tests
- `.claude/commands/e2e/test_supplier_verification_export.md` — Existing E2E test for the export feature, to be updated to validate data presence

### New Files
- `.claude/commands/e2e/test_supplier_certification_excel_data.md` — New E2E test to validate that audit data appears in the exported Excel file

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Fix the SQL JOIN in `get_all_with_audit_data()`
- Open `apps/Server/app/repository/kompass_repository.py`
- Locate the `get_all_with_audit_data()` method (line 1655)
- Find the SQL query at line 1758:
  ```sql
  LEFT JOIN supplier_audits a ON s.latest_audit_id = a.id
  ```
- Replace it with a subquery that finds the latest audit by `supplier_id`:
  ```sql
  LEFT JOIN supplier_audits a ON a.id = (
      SELECT sa.id FROM supplier_audits sa
      WHERE sa.supplier_id = s.id
      ORDER BY sa.created_at DESC
      LIMIT 1
  )
  ```
- This ensures that the export includes audit data for all suppliers with at least one audit, regardless of whether `latest_audit_id` has been set via classification

### Step 2: Add a unit test for the fix
- Open `apps/Server/tests/api/test_supplier_routes.py`
- Add a new test method in the `TestExportVerificationExcel` class that verifies the service is called correctly when suppliers have audit data but no classification (i.e., `latest_audit_id` is NULL)
- The test should mock the service to return data with populated audit fields and verify the Excel response contains that data

### Step 3: Create E2E test file for certification data in Excel export
- Read `.claude/commands/e2e/test_supplier_verification_export.md` and `.claude/commands/e2e/test_supplier_certification_tab.md` as reference examples
- Create a new E2E test file at `.claude/commands/e2e/test_supplier_certification_excel_data.md` that validates:
  1. Navigate to Suppliers page
  2. Open a supplier that has audit data visible in the Certification tab
  3. Confirm audit data is displayed on screen (supplier type, certifications, etc.)
  4. Go back to Suppliers list
  5. Click "Export Excel" button
  6. Verify the export completes without errors
  7. Take screenshots at each step to prove the flow works

### Step 4: Run validation commands
- Run all validation commands listed below to confirm the fix works with zero regressions

## Validation Commands
Execute every command to validate the bug is fixed with zero regressions.

- `cd apps/Server && .venv/bin/pytest tests/ -v --tb=short` — Run Server tests to validate the bug is fixed with zero regressions
- `cd apps/Server && .venv/bin/ruff check .` — Run linting to ensure code quality
- `cd apps/Client && npm run typecheck` — Run Client type check to validate no type regressions
- `cd apps/Client && npm run build` — Run Client build to validate the build is not broken
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_supplier_certification_excel_data.md` E2E test file to validate this functionality works

## Notes
- The fix is a single SQL change in one file (`kompass_repository.py`). The column selection, index-based mapping, Excel generation, and frontend code are all correct and require no changes.
- The subquery approach (`SELECT sa.id ... ORDER BY sa.created_at DESC LIMIT 1`) is a standard PostgreSQL pattern that performs well with an existing index on `supplier_audits(supplier_id)`.
- This fix also handles the edge case where a supplier has multiple audits — it always picks the most recent one, which is the same behavior intended by `latest_audit_id`.
- No new libraries are required.
