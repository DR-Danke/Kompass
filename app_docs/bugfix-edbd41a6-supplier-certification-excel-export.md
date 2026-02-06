# Bug Fix: Supplier Certification Excel Export Missing Data

**ADW ID:** edbd41a6
**Date:** 2026-02-06
**Specification:** specs/issue-105-adw-edbd41a6-sdlc_planner-fix-supplier-certification-excel-export.md

## Overview

Fixed a bug where the Suppliers page "Export Excel" button produced an Excel file with empty audit-related columns (supplier type, employee count, factory area, certifications, positive/negative points, classification, etc.), even though the same data displayed correctly on screen in the Supplier Certification Tab. The root cause was a SQL JOIN that relied on `latest_audit_id`, which is only set after AI classification or manual override.

## What Was Built

- Fixed the SQL query in `get_all_with_audit_data()` to use a subquery that finds the most recent audit per supplier, instead of relying on `latest_audit_id`
- Added a unit test validating that audit data appears in the exported Excel file
- Created an E2E test command for validating supplier certification data in Excel exports

## Technical Implementation

### Files Modified

- `apps/Server/app/repository/kompass_repository.py`: Changed the LEFT JOIN in `get_all_with_audit_data()` from `s.latest_audit_id = a.id` to a subquery selecting the most recent audit by `supplier_id`
- `apps/Server/tests/api/test_supplier_routes.py`: Added `test_export_excel_contains_audit_data` test that verifies audit fields (supplier type, employee count, certifications) appear in the Excel output
- `.claude/commands/e2e/test_supplier_certification_excel_data.md`: New E2E test command for validating the full export flow

### Key Changes

- **SQL Fix (single-line change):** Replaced `LEFT JOIN supplier_audits a ON s.latest_audit_id = a.id` with a correlated subquery `LEFT JOIN supplier_audits a ON a.id = (SELECT sa.id FROM supplier_audits sa WHERE sa.supplier_id = s.id ORDER BY sa.created_at DESC LIMIT 1)`. This ensures audit data is included for all suppliers with at least one audit, regardless of classification status.
- **Root Cause:** `latest_audit_id` on the `suppliers` table is only populated when `update_certification_status()` runs after AI classification or manual override. Suppliers with extracted audits but no classification had `latest_audit_id = NULL`, causing the LEFT JOIN to return no audit data.
- **No frontend changes needed:** The column selection, index-based mapping, Excel generation, and frontend export logic were all correct — only the SQL JOIN condition was wrong.

## How to Use

1. Navigate to the **Suppliers** page
2. Ensure at least one supplier has audit data (upload an audit PDF via the Certification tab)
3. Click the **Export Excel** button on the Suppliers list page
4. Open the downloaded Excel file
5. Verify that audit-related columns (Supplier Type, Employee Count, Factory Area, Certifications, Positive Points, Negative Points, etc.) are populated for suppliers with processed audits

## Configuration

No configuration changes required.

## Testing

- **Unit tests:** `cd apps/Server && .venv/bin/pytest tests/api/test_supplier_routes.py -v --tb=short`
- **E2E test:** Run the `/e2e:test_supplier_certification_excel_data` command to validate the full flow
- **Manual test:** Export Excel from the Suppliers page and confirm audit columns contain data

## Notes

- The subquery approach is a standard PostgreSQL pattern that performs well with an existing index on `supplier_audits(supplier_id)`
- This fix also handles the edge case where a supplier has multiple audits — it always picks the most recent one, matching the intended behavior of `latest_audit_id`
- No new libraries are required
