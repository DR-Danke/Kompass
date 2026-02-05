# Feature: Suppliers Page Enhancements with Certification Filters and Badges

## Metadata
issue_number: `85`
adw_id: `f77a2609`
issue_json: `{"number":85,"title":"feat: Add suppliers page enhancements with certification filters and badges","body":"...phase-3"}`

## Feature Description
Enhance the existing Suppliers page with certification status display, filters, and quick actions to enable faster supplier qualification decisions. This feature surfaces certification information prominently in the supplier table, adds filters for certification and pipeline status, provides quick actions for common operations, and enables sorting by new certification-related fields.

## User Story
As a sourcing manager
I want to see supplier certification status and pipeline status prominently displayed with filtering, sorting, and quick actions
So that I can quickly identify certified suppliers, filter by certification grade, and take common actions without navigating away from the list view

## Problem Statement
Currently, the Suppliers page displays basic supplier information but lacks visibility into certification status, making it difficult to:
1. Quickly identify which suppliers are certified (A/B/C) vs uncertified
2. Filter suppliers by certification grade or pipeline status
3. Sort suppliers by certification-related fields (last audit date, certified date)
4. Take quick actions like uploading audits or viewing certification summaries directly from the list

## Solution Statement
Enhance the Suppliers page with:
1. New table columns: Certification Status Badge, Pipeline Status Badge, Last Audit Date
2. New filters: Certification (All/Certified/Type A/B/C/Uncertified), Pipeline Status
3. Quick actions menu with: View/Edit, Upload Audit, View Certification Summary, Change Pipeline Status
4. Sorting capabilities for certification and pipeline fields
5. Visual indicators: color-coded badges, warning icons for failed extractions

## Relevant Files
Use these files to implement the feature:

### Frontend - Core Files
- `apps/Client/src/pages/kompass/SuppliersPage.tsx` - Main page component to enhance with new columns, filters, sorting, and quick actions
- `apps/Client/src/types/kompass.ts` - Already contains `CertificationStatus`, `SupplierPipelineStatus`, `SupplierAuditResponse` types - verify these are complete
- `apps/Client/src/services/kompassService.ts` - Already has `supplierService` and `auditService` - may need to add `getCertifiedSuppliers`, `getSuppliersByPipeline` methods

### Frontend - Components
- `apps/Client/src/components/kompass/ClassificationBadge.tsx` - Existing component for A/B/C classification display (reuse for certification status)
- `apps/Client/src/components/kompass/PipelineStatusBadge.tsx` - Existing component for pipeline status display (already used in SuppliersPage)
- `apps/Client/src/components/kompass/SupplierForm.tsx` - Supplier form with certification tab (for reference)

### Backend - Routes & Services
- `apps/Server/app/api/supplier_routes.py` - Already has `/certified`, `/pipeline-summary`, `/pipeline/{status}` endpoints
- `apps/Server/app/api/audit_routes.py` - Already has audit upload/list/classification endpoints

### E2E Testing
- `.claude/commands/test_e2e.md` - E2E test runner instructions
- `.claude/commands/e2e/test_suppliers_page.md` - Existing suppliers page E2E test (for reference)
- `.claude/commands/e2e/test_supplier_certification_tab.md` - Existing certification tab E2E test (for reference)

### New Files

- `apps/Client/src/components/kompass/CertificationStatusBadge.tsx` - New component for certification status display (wraps ClassificationBadge with status logic)
- `apps/Client/src/components/kompass/SupplierQuickActionsMenu.tsx` - New component for quick actions dropdown menu
- `.claude/commands/e2e/test_suppliers_certification_filters.md` - New E2E test file for certification filters and badges

## Implementation Plan
### Phase 1: Foundation - Types and Service Methods
Verify and extend TypeScript types and API service methods to ensure all certification/pipeline data is accessible from the frontend.

### Phase 2: Core Implementation - UI Components and Page Updates
1. Create CertificationStatusBadge component (wrapper around ClassificationBadge)
2. Create SupplierQuickActionsMenu component with dropdown actions
3. Update SuppliersPage with new table columns, filters, and sorting options

### Phase 3: Integration - Wire Up Actions and State
Connect quick actions (upload audit, view certification summary, change pipeline status) to existing services and modals.

## Step by Step Tasks

### Step 1: Verify and Update Types
- Review `apps/Client/src/types/kompass.ts` to ensure `SupplierResponse` includes: `certification_status`, `pipeline_status`, `latest_audit_id`, `certified_at`
- Verify `CertificationStatus` type includes all values: `'uncertified' | 'pending_review' | 'certified_a' | 'certified_b' | 'certified_c'`
- Ensure `SupplierPipelineStatus` includes all values: `'contacted' | 'potential' | 'quoted' | 'certified' | 'active' | 'inactive'`

### Step 2: Update API Service Methods (if needed)
- Review `apps/Client/src/services/kompassService.ts` for supplier service methods
- Add or verify `getCertifiedSuppliers(grade?: string)` method that calls `/api/suppliers/certified`
- Add or verify `getSuppliersByPipeline(status: string)` method that calls `/api/suppliers/pipeline/{status}`
- Ensure `supplierService.list()` supports new filter parameters: `certification_status`, `pipeline_status`

### Step 3: Create CertificationStatusBadge Component
- Create `apps/Client/src/components/kompass/CertificationStatusBadge.tsx`
- Component accepts `certificationStatus: CertificationStatus` and optional `latestAuditId`
- Map certification status to A/B/C grades or "Uncertified"
- Use existing `ClassificationBadge` for grades, gray Chip for uncertified/pending
- Add warning icon indicator when extraction failed (if `latestAuditId` present but status indicates failure)

### Step 4: Create SupplierQuickActionsMenu Component
- Create `apps/Client/src/components/kompass/SupplierQuickActionsMenu.tsx`
- Use MUI `Menu` with `IconButton` trigger (MoreVert icon)
- Menu items:
  - "View/Edit Supplier" - calls `onEdit(supplier)` callback
  - "Upload Audit" - calls `onUploadAudit(supplier)` callback
  - "View Certification Summary" - calls `onViewCertification(supplier)` callback
  - "Change Pipeline Status" - submenu with status options, calls `onChangePipelineStatus(supplier, status)` callback
- Disable "Upload Audit" for new/unsaved suppliers (if no ID)
- Disable "View Certification Summary" for suppliers without audits

### Step 5: Update SuppliersPage with New Table Columns
- Add new table columns after "Status":
  1. "Certification" - displays CertificationStatusBadge
  2. "Last Audit" - displays formatted date from latest audit or "-"
- Update TableHead with new column headers
- Update TableBody row mapping to render new columns
- Ensure proper alignment and truncation for mobile/responsive views

### Step 6: Update SuppliersPage with Certification Filter
- Add new filter dropdown "Certification" after existing "Pipeline" filter
- Options: "All Certifications", "Certified (Any)", "Type A", "Type B", "Type C", "Uncertified"
- Store filter state as `certificationFilter: 'all' | 'certified' | 'A' | 'B' | 'C' | 'uncertified'`
- Pass filter to `supplierService.list()` API call
- Update `fetchSuppliers` callback to include certification filter

### Step 7: Update SuppliersPage with Sorting Options
- Add sorting state: `sortField: string`, `sortOrder: 'asc' | 'desc'`
- Make table headers clickable for sortable fields: Name, Certification, Pipeline Status, Last Audit
- Display sort indicator arrow on active sort column
- Pass sort parameters to `supplierService.list()` API call

### Step 8: Replace Actions Column with Quick Actions Menu
- Remove individual Edit/Delete icon buttons from Actions column
- Replace with SupplierQuickActionsMenu component
- Implement callback handlers:
  - `handleEdit(supplier)` - opens SupplierForm dialog (existing logic)
  - `handleUploadAudit(supplier)` - opens AuditUploader modal (new)
  - `handleViewCertification(supplier)` - opens certification summary modal (new)
  - `handleChangePipelineStatus(supplier, status)` - calls API and refreshes list

### Step 9: Add Upload Audit Modal Integration
- Import existing `AuditUploader` component
- Add state for `auditUploadOpen`, `auditUploadSupplierId`
- Open modal when "Upload Audit" clicked from quick actions
- On successful upload, refresh supplier list and close modal

### Step 10: Add Certification Summary Modal
- Create a simple modal that displays SupplierCertificationTab content
- Or reuse SupplierForm dialog opened to the Certification tab
- Show certification status, latest audit summary, classification badge
- Allow closing without changes

### Step 11: Create E2E Test File
- Create `.claude/commands/e2e/test_suppliers_certification_filters.md`
- Test steps:
  1. Navigate to Suppliers page
  2. Verify new columns visible (Certification, Last Audit)
  3. Test certification filter (select "Type A", verify filtered results)
  4. Test sorting by certification status
  5. Test quick actions menu opens
  6. Test "Upload Audit" action opens uploader
  7. Test "Change Pipeline Status" submenu works
- Success criteria and screenshot specifications

### Step 12: Run Validation Commands
- Execute all validation commands to ensure zero regressions

## Testing Strategy
### Unit Tests
- CertificationStatusBadge: renders correct badge for each status value
- SupplierQuickActionsMenu: renders all menu items, calls correct callbacks
- SuppliersPage: filter state updates correctly, sorting state updates correctly

### Edge Cases
- Supplier with no audits (show "Uncertified" badge, no Last Audit date)
- Supplier with pending extraction (show "Pending" state)
- Supplier with failed extraction (show warning icon)
- Empty filter results (show "No suppliers match your filters" message)
- Rapid filter changes (debounce search correctly)

## Acceptance Criteria
- [ ] Certification badge visible in table showing A/B/C or "Uncertified"
- [ ] Pipeline status badge visible in table
- [ ] Last Audit date column shows formatted date or "-"
- [ ] Filter by certification works (All, Certified, Type A/B/C, Uncertified)
- [ ] Filter by pipeline status works (All, Contacted, Potential, Quoted, Certified, Active, Inactive)
- [ ] Sorting by certification status works
- [ ] Sorting by pipeline status works
- [ ] Sorting by last audit date works
- [ ] Quick actions menu appears on row hover/click
- [ ] "Upload Audit" action opens audit uploader modal
- [ ] "View Certification Summary" shows certification details
- [ ] "Change Pipeline Status" submenu updates status via API
- [ ] Warning icon shows for suppliers with failed audit extractions
- [ ] All existing functionality (add/edit/delete supplier) still works
- [ ] No TypeScript errors, ESLint errors, or build errors

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && .venv/bin/pytest tests/ -v --tb=short` - Run Server tests to validate backend compatibility
- `cd apps/Client && npm run typecheck` - Run Client type check to validate TypeScript types
- `cd apps/Client && npm run lint` - Run ESLint to check for code quality issues
- `cd apps/Client && npm run build` - Run Client build to validate the feature compiles without errors
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_suppliers_certification_filters.md` to validate this functionality works

## Notes
- The backend API already supports certification and pipeline filtering via `/api/suppliers/certified` and `/api/suppliers/pipeline/{status}` endpoints
- Existing `ClassificationBadge` component can be reused for grade display
- Existing `PipelineStatusBadge` component is already used in the table
- The `auditService` already exists with upload/list/reprocess/classify methods
- Consider adding a loading state when changing pipeline status to prevent double-clicks
- The feature should work in both list view and kanban view where applicable
