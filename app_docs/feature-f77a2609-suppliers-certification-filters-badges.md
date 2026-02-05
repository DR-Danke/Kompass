# Suppliers Page: Certification Filters and Badges

**ADW ID:** f77a2609
**Date:** 2026-02-04
**Specification:** specs/issue-85-adw-f77a2609-sdlc_planner-suppliers-certification-filters-badges.md

## Overview

Enhanced the Suppliers page with certification status visibility, filtering, sorting, and quick actions. Sourcing managers can now quickly identify certified suppliers (Type A/B/C), filter by certification grade or pipeline status, sort by certification-related fields, and take common actions (upload audits, change pipeline status) directly from the list view.

## What Was Built

- **CertificationStatusBadge component**: Displays A/B/C classification badges with warning icons for failed extractions
- **SupplierQuickActionsMenu component**: Three-dot dropdown menu with View/Edit, Upload Audit, View Certification, Change Pipeline Status, and Delete actions
- **Enhanced SuppliersPage**: New table columns, certification filter, sortable headers, and integrated audit upload dialog
- **Backend API enhancements**: Extended `/api/suppliers` with certification_status, pipeline_status, search filters, and sorting

## Technical Implementation

### Files Modified

- `apps/Client/src/components/kompass/CertificationStatusBadge.tsx`: New component - renders grade badges (A/B/C) using ClassificationBadge or Chip for Uncertified/Pending states
- `apps/Client/src/components/kompass/SupplierQuickActionsMenu.tsx`: New component - MUI Menu with IconButton trigger and pipeline status submenu
- `apps/Client/src/pages/kompass/SuppliersPage.tsx`: Major updates - added Certification/Certified Date columns, certification filter dropdown, sortable TableSortLabel headers, integrated AuditUploader dialog
- `apps/Client/src/types/kompass.ts`: Added `SupplierCertificationSummary` interface and `AuditExtractionStatus` type reference
- `apps/Client/src/services/kompassService.ts`: Added `SupplierListFilters` interface and `getCertificationSummary()` method
- `apps/Server/app/api/supplier_routes.py`: Added certification_status, pipeline_status, search query parameters with validation
- `apps/Server/app/services/supplier_service.py`: Extended `list_suppliers()` with new filter and sort parameters
- `apps/Server/app/repository/kompass_repository.py`: Implemented SQL filtering for certification/pipeline status, search across multiple fields, and dynamic ORDER BY clause

### Key Changes

- **Certification filter logic**: "Certified (Any)" filters for `certified_a`, `certified_b`, `certified_c`; "Uncertified" includes both `uncertified` and `pending_review`
- **Sortable columns**: Name, Certification, Pipeline Status, and Certified Date all support ascending/descending sorting
- **Quick actions menu**: Replaces individual Edit/Delete buttons with consolidated three-dot menu; pipeline status submenu allows instant status changes
- **Audit upload integration**: Opens AuditUploader in a dialog, refreshes supplier list on completion to reflect updated certification status
- **Table restructuring**: Removed Contact Email/Phone columns, added Certification and Certified Date columns

## How to Use

1. Navigate to **Kompass > Suppliers** page
2. **Filter by certification**: Use the "Certification" dropdown to filter by All, Certified (Any), Type A/B/C, or Uncertified
3. **Sort the table**: Click column headers (Name, Certification, Pipeline, Certified Date) to toggle ascending/descending sort
4. **Quick actions**: Click the three-dot menu (⋮) on any row to:
   - View/Edit Supplier: Opens supplier form dialog
   - Upload Audit: Opens audit file uploader
   - View Certification Summary: Opens supplier form to review certification tab
   - Change Pipeline Status: Submenu to instantly update status
   - Delete Supplier: Confirms and removes supplier

## Configuration

No additional configuration required. Feature uses existing:
- `CertificationStatus` enum values: `uncertified`, `pending_review`, `certified_a`, `certified_b`, `certified_c`
- `SupplierPipelineStatus` enum values: `contacted`, `potential`, `quoted`, `certified`, `active`, `inactive`

## Testing

Run the E2E test for this feature:
```bash
# Read and follow instructions in:
.claude/commands/e2e/test_suppliers_certification_filters.md
```

Manual testing checklist:
1. Verify certification badges display correctly for suppliers with different statuses
2. Test each certification filter option and confirm correct results
3. Click each sortable header and verify table reorders correctly
4. Test all quick action menu items function as expected
5. Upload an audit via quick actions and verify list refreshes

## Notes

- Warning icon (⚠️) appears on certification badges when `extractionStatus === 'failed'` to indicate manual review needed
- View Certification Summary action is disabled for suppliers without audits
- Pipeline status changes have loading state to prevent double-clicks
- Backend search queries name, email, phone, and supplier code fields simultaneously
