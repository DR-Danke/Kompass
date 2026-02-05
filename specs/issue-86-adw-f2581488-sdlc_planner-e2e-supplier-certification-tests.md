# Chore: Add E2E tests for supplier certification workflow

## Metadata
issue_number: `86`
adw_id: `f2581488`
issue_json: `{}`

## Chore Description
Create comprehensive end-to-end tests for the Supplier Certification feature to ensure the complete workflow functions correctly. This includes:

1. **API Route Tests** - Test all audit-related endpoints (`/api/suppliers/{supplier_id}/audits/*`)
2. **Service Unit Tests** - Additional tests for audit service functionality not covered by existing tests
3. **E2E Test Command** - Create a new E2E test command that covers the full certification workflow including UI interactions

The certification workflow involves:
- Uploading factory audit PDF documents
- AI extraction of audit data (supplier type, certifications, markets served, etc.)
- Classification generation (A/B/C grades) based on scoring algorithm
- Manual classification override with required notes
- Supplier certification status updates
- Pipeline status transitions

## Relevant Files
Use these files to resolve the chore:

### Existing Test Files (reference patterns)
- `apps/Server/tests/api/test_supplier_routes.py` - API route testing patterns with FastAPI TestClient, dependency overrides, and RBAC testing
- `apps/Server/tests/test_audit_service.py` - Existing audit service unit tests (upload, parsing, extraction prompt)
- `apps/Server/tests/test_classification.py` - Existing classification scoring tests (classify_supplier, override_classification)
- `apps/Server/tests/test_supplier_certification_routes.py` - Existing certification filtering tests (list_certified_suppliers, pipeline status)
- `apps/Server/tests/test_kompass/conftest.py` - Shared fixtures (mock users, sample data factories)

### Source Files Under Test
- `apps/Server/app/api/audit_routes.py` - API endpoints for audit CRUD, reprocess, classify, override
- `apps/Server/app/services/audit_service.py` - Business logic for audit processing, classification scoring
- `apps/Server/app/repository/audit_repository.py` - Database operations for audits
- `apps/Server/app/models/kompass_dto.py` - DTOs including AuditType, ExtractionStatus, SupplierAuditResponseDTO

### Existing E2E Commands (reference format)
- `.claude/commands/e2e/test_supplier_certification_tab.md` - E2E test for certification tab UI
- `.claude/commands/e2e/test_suppliers_certification_filters.md` - E2E test for certification filters
- `.claude/commands/e2e/test_suppliers_page.md` - E2E test format reference

### New Files

- `apps/Server/tests/api/test_audit_routes.py` - New API route tests for all audit endpoints
- `.claude/commands/e2e/test_supplier_certification_workflow.md` - New comprehensive E2E test command

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create API Route Tests for Audit Endpoints

Create `apps/Server/tests/api/test_audit_routes.py` with tests for:

**Setup fixtures:**
- `mock_current_user` - Standard user fixture
- `mock_admin_user` - Admin user fixture for RBAC tests
- `mock_viewer_user` - Viewer user (read-only)
- `sample_audit_data` - Sample audit data for mocking
- `sample_audit_response` - SupplierAuditResponseDTO fixture
- `app` - FastAPI test app with dependency overrides
- `client` - TestClient fixture

**Test Classes:**

1. **TestUploadAudit** (`POST /{supplier_id}/audits`)
   - `test_upload_audit_success` - Valid PDF upload creates audit with pending status
   - `test_upload_audit_rejects_non_pdf` - Returns 400 for non-PDF files
   - `test_upload_audit_rejects_large_file` - Returns 400 for files >25MB
   - `test_upload_audit_rejects_no_filename` - Returns 400 for files without filename
   - `test_upload_audit_schedules_background_processing` - Verify background task is scheduled
   - `test_upload_audit_viewer_forbidden` - Viewers cannot upload (403)

2. **TestListSupplierAudits** (`GET /{supplier_id}/audits`)
   - `test_list_audits_success` - Returns paginated list
   - `test_list_audits_empty` - Returns empty list for supplier without audits
   - `test_list_audits_pagination` - Pagination parameters work correctly
   - `test_list_audits_viewer_allowed` - Viewers can list audits

3. **TestGetAudit** (`GET /{supplier_id}/audits/{audit_id}`)
   - `test_get_audit_success` - Returns audit by ID
   - `test_get_audit_not_found` - Returns 404 for non-existent audit
   - `test_get_audit_wrong_supplier` - Returns 400 if audit doesn't belong to supplier

4. **TestReprocessAudit** (`POST /{supplier_id}/audits/{audit_id}/reprocess`)
   - `test_reprocess_audit_success` - Resets extraction and schedules reprocessing
   - `test_reprocess_audit_not_found` - Returns 404 for non-existent audit
   - `test_reprocess_audit_wrong_supplier` - Returns 400 if wrong supplier
   - `test_reprocess_audit_regular_user_forbidden` - Regular users cannot reprocess (403)
   - `test_reprocess_audit_admin_allowed` - Admins can reprocess
   - `test_reprocess_audit_manager_allowed` - Managers can reprocess

5. **TestDeleteAudit** (`DELETE /{supplier_id}/audits/{audit_id}`)
   - `test_delete_audit_success` - Returns 204 on success
   - `test_delete_audit_not_found` - Returns 404 for non-existent audit
   - `test_delete_audit_wrong_supplier` - Returns 400 if wrong supplier
   - `test_delete_audit_regular_user_forbidden` - Regular users cannot delete
   - `test_delete_audit_admin_allowed` - Admins can delete

6. **TestClassifyAudit** (`POST /{supplier_id}/audits/{audit_id}/classify`)
   - `test_classify_audit_success` - Returns audit with classification
   - `test_classify_audit_not_found` - Returns 404 for non-existent audit
   - `test_classify_audit_wrong_supplier` - Returns 400 if wrong supplier
   - `test_classify_audit_extraction_not_completed` - Returns 400 if extraction pending/failed
   - `test_classify_audit_updates_supplier_status` - Verify supplier certification_status updated

7. **TestOverrideClassification** (`PUT /{supplier_id}/audits/{audit_id}/classification`)
   - `test_override_classification_success` - Updates classification with notes
   - `test_override_classification_requires_notes` - Returns 400 if notes empty
   - `test_override_classification_requires_notes_not_whitespace` - Returns 400 if notes only whitespace
   - `test_override_classification_not_found` - Returns 404 for non-existent audit
   - `test_override_classification_wrong_supplier` - Returns 400 if wrong supplier
   - `test_override_classification_regular_user_forbidden` - Regular users cannot override
   - `test_override_classification_invalid_grade` - Returns 400 for invalid grade (D, X, etc.)

### Step 2: Add Additional Service Tests for Edge Cases

Add to `apps/Server/tests/test_audit_service.py`:

**Additional tests for edge cases not covered:**

1. **TestStatusTransitions**
   - `test_process_audit_marks_failed_on_error` - Processing errors set status to 'failed'
   - `test_process_audit_marks_completed_on_success` - Successful processing sets status to 'completed'

2. **TestClassificationEdgeCases**
   - `test_classify_with_empty_markets_served` - Handles None/empty markets_served gracefully
   - `test_classify_with_empty_certifications` - Handles None/empty certifications list
   - `test_classify_trader_lower_score_than_manufacturer` - Traders score lower than manufacturers

### Step 3: Create Comprehensive E2E Test Command

Create `.claude/commands/e2e/test_supplier_certification_workflow.md`:

This E2E test command covers the complete supplier certification workflow, consolidating and extending the existing certification tab and filters tests:

**Test Scenarios:**

1. **Audit Upload Flow**
   - Step 1: Navigate to Suppliers page
   - Step 2: Open supplier dialog and switch to Certification tab
   - Step 3: Upload valid PDF audit document
   - Step 4: Verify upload progress indicator
   - Step 5: Verify processing status transitions (pending → processing → completed)
   - Step 6: Verify extracted summary displays

2. **File Validation (Negative Tests)**
   - Step 7: Attempt upload of non-PDF file (simulate with wrong extension)
   - Step 8: Verify error message about file type
   - Step 9: Verify upload area returns to idle state

3. **AI Extraction Verification**
   - Step 10: Verify extracted fields display (supplier type, employee count, factory area)
   - Step 11: Verify certifications display as chips
   - Step 12: Verify markets served chart renders
   - Step 13: Verify positive/negative points display

4. **Classification Flow**
   - Step 14: Verify classification badge displays with correct grade
   - Step 15: Verify badge has correct color (A=green, B=orange, C=red)
   - Step 16: Hover to verify tooltip shows reasoning

5. **Override Classification Flow**
   - Step 17: Click Override button
   - Step 18: Verify override dialog opens
   - Step 19: Select different classification grade
   - Step 20: Leave notes empty and click Confirm
   - Step 21: Verify validation error for required notes
   - Step 22: Enter valid notes and confirm
   - Step 23: Verify classification badge updates
   - Step 24: Verify "Manual" indicator appears

6. **Reprocess Functionality**
   - Step 25: Click Reprocess button on audit
   - Step 26: Verify extraction status resets to processing
   - Step 27: Wait for extraction to complete again

7. **Pipeline Status Integration**
   - Step 28: Close supplier dialog
   - Step 29: Navigate to Suppliers Pipeline page (if exists) or verify status column
   - Step 30: Verify supplier shows in correct pipeline status
   - Step 31: Change pipeline status via quick actions menu
   - Step 32: Verify pipeline status updates

8. **Certification Filters Integration**
   - Step 33: Navigate back to Suppliers page
   - Step 34: Verify Certification column displays badge
   - Step 35: Apply certification filter (Type A)
   - Step 36: Verify only Type A suppliers display (or empty state)
   - Step 37: Apply uncertified filter
   - Step 38: Verify results update

9. **Sorting by Certification**
   - Step 39: Click Certification column header to sort
   - Step 40: Verify sort indicator appears
   - Step 41: Click again to reverse sort
   - Step 42: Click Certified Date column header
   - Step 43: Verify sort by date works

10. **Quick Actions Integration**
    - Step 44: Open quick actions menu on a supplier row
    - Step 45: Verify menu includes "Upload Audit" option
    - Step 46: Verify menu includes "View Certification Summary" option
    - Step 47: Click "Upload Audit"
    - Step 48: Verify audit upload dialog opens
    - Step 49: Close dialog

11. **Products Page Certification Status**
    - Step 50: Navigate to Products Catalog page
    - Step 51: Verify products from certified suppliers show certification badge
    - Step 52: Verify certification filter exists (if implemented)

12. **Audit History**
    - Step 53: Navigate back to Suppliers page
    - Step 54: Open supplier with multiple audits
    - Step 55: Verify audit history section displays
    - Step 56: Click on older audit in history
    - Step 57: Verify audit details load

**Success Criteria Checklist:**
- [ ] Audit upload accepts PDF files
- [ ] Audit upload rejects non-PDF files with error
- [ ] Upload progress indicator displays
- [ ] Processing status transitions correctly
- [ ] Extraction summary displays all expected fields
- [ ] Markets served chart renders
- [ ] Certifications display as chips
- [ ] Classification badge shows correct grade and color
- [ ] Override dialog validates required notes
- [ ] Classification override updates badge and shows "Manual" indicator
- [ ] Reprocess functionality resets and re-extracts
- [ ] Pipeline status displays and can be changed
- [ ] Certification filter works correctly
- [ ] Sorting by certification status works
- [ ] Sorting by certified date works
- [ ] Quick actions menu includes certification options
- [ ] Audit history displays for suppliers with multiple audits
- [ ] No console errors during test execution

### Step 4: Run Validation Commands to Ensure All Tests Pass

Run all test commands to validate the chore is complete with zero regressions:

1. Run the new API route tests
2. Run the existing audit service tests
3. Run the existing classification tests
4. Run the existing certification routes tests
5. Run linting to ensure code quality

## Validation Commands
Execute every command to validate the chore is complete with zero regressions.

- `cd apps/Server && ../.venv/bin/pytest tests/api/test_audit_routes.py -v --tb=short` - Run new audit route tests
- `cd apps/Server && ../.venv/bin/pytest tests/test_audit_service.py -v --tb=short` - Run audit service tests
- `cd apps/Server && ../.venv/bin/pytest tests/test_classification.py -v --tb=short` - Run classification tests
- `cd apps/Server && ../.venv/bin/pytest tests/test_supplier_certification_routes.py -v --tb=short` - Run certification routes tests
- `cd apps/Server && ../.venv/bin/pytest tests/ -v --tb=short` - Run all server tests to check for regressions
- `cd apps/Server && ../.venv/bin/ruff check .` - Run linting

## Notes

- The E2E test command file (`.claude/commands/e2e/test_supplier_certification_workflow.md`) is a comprehensive manual test specification that can be executed using Playwright MCP integration or manual testing
- The existing tests in `test_audit_service.py` and `test_classification.py` already cover most service-level functionality - the new API route tests focus on HTTP layer concerns (status codes, authentication, validation)
- File upload tests use mock content since actual PDF processing requires external AI APIs
- The 25MB file size limit is validated at the route level
- RBAC tests verify that:
  - Viewers (read-only) can list/get audits but cannot upload/modify
  - Regular users can upload and classify but cannot delete/override
  - Admin/Manager users have full access
- The classification scoring algorithm is well-tested in `test_classification.py` - no additional scoring tests needed
- Background task scheduling for audit processing is mocked in route tests
