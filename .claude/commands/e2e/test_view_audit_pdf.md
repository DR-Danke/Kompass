# E2E Test: View Audit PDF

## Overview

This E2E test validates that the "View Full PDF" button works correctly for audit documents. The fix addresses the issue where clicking "View Full PDF" would fail with "Not allowed to load local resource: file:///tmp/..." because browsers block direct access to local file:// URLs.

## User Story

As a sourcing manager, I want to view the original audit PDF document so that I can review the full audit details and verify extracted information.

## Prerequisites

- Application running (frontend on port 5173, backend on port 8000)
- Test user credentials available
- At least one supplier with a completed audit in the database
- Test PDF file available for upload (if no audit exists)

## Test Scenarios

### Scenario 1: View PDF from Completed Audit

**Objective:** Verify that clicking "View Full PDF" opens the PDF in a new browser tab.

#### Steps

1. **Navigate to Suppliers Page**
   - Open application at http://localhost:5173
   - Login with test credentials
   - Navigate to `/suppliers` page
   - **Verify** page title "Suppliers" is visible
   - **Screenshot**: `01_suppliers_page.png`

2. **Open Supplier with Audit**
   - Click the edit (pencil) icon on a supplier that has a completed audit
   - **Verify** supplier dialog opens
   - **Screenshot**: `02_supplier_dialog.png`

3. **Switch to Certification Tab**
   - Click on "Certification" tab
   - **Verify** Latest Audit section is visible with audit summary
   - **Verify** "View Full PDF" button is visible
   - **Screenshot**: `03_certification_tab_with_audit.png`

4. **Click View Full PDF Button**
   - Click the "View Full PDF" button
   - **Verify** a new browser tab opens
   - **Verify** the PDF content is displayed (or browser's PDF viewer loads)
   - **Critical Check**: No console error "Not allowed to load local resource"
   - **Screenshot**: `04_pdf_viewer.png`

5. **Verify No Console Errors**
   - Open browser developer tools (F12)
   - Check the Console tab
   - **Verify** no errors related to "local resource" or "file://"
   - **Screenshot**: `05_no_console_errors.png`

### Scenario 2: View PDF from Failed Audit (Error State)

**Objective:** Verify the View PDF button works even when extraction failed.

#### Steps

6. **Find Audit with Failed Status**
   - Navigate to a supplier with a failed audit (if available)
   - **Verify** the error state shows "Extraction failed"
   - **Verify** "View Full PDF" button is still visible
   - **Screenshot**: `06_failed_audit_view_pdf.png`

7. **Click View Full PDF on Failed Audit**
   - Click the "View Full PDF" button
   - **Verify** PDF opens in new tab
   - **Verify** no console errors

### Scenario 3: Verify Backend Download Endpoint

**Objective:** Confirm the backend serves PDF files correctly.

#### Steps

8. **Check Network Request**
   - Open browser developer tools > Network tab
   - Click "View Full PDF"
   - **Verify** request goes to `/api/suppliers/{id}/audits/{id}/download`
   - **Verify** response is either:
     - 200 with PDF content (for local files)
     - 302 redirect to Supabase Storage URL (for cloud files)
   - **Screenshot**: `07_network_request.png`

## Success Criteria Checklist

- [ ] "View Full PDF" button is visible on completed audits
- [ ] "View Full PDF" button is visible on failed audits
- [ ] Clicking button opens PDF in new browser tab
- [ ] **CRITICAL**: No "Not allowed to load local resource" error in console
- [ ] PDF content displays correctly in browser
- [ ] Network request goes to backend `/download` endpoint
- [ ] Backend returns PDF content or redirects to storage URL
- [ ] Works for both local file:// URLs and Supabase Storage URLs

## Manual Verification Steps

1. Start the application:
   ```bash
   # Terminal 1 - Backend
   cd apps/Server
   source .venv/bin/activate
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

   # Terminal 2 - Frontend
   cd apps/Client
   npm run dev -- --host 0.0.0.0
   ```

2. Test the download endpoint directly:
   ```bash
   # Get a valid audit ID from the database or UI
   curl -I "http://localhost:8000/api/suppliers/{supplier_id}/audits/{audit_id}/download" \
     -H "Authorization: Bearer {token}"

   # Should return 200 with application/pdf or 302 redirect
   ```

3. Upload a new PDF and verify View Full PDF works:
   - Upload PDF via Certification tab
   - Wait for processing
   - Click "View Full PDF"
   - Verify PDF opens without errors

## Notes

- The fix routes PDF viewing through the backend `/download` endpoint
- For local `file://` URLs, the backend reads and serves the file content
- For Supabase Storage `https://` URLs, the backend redirects to the storage URL
- This approach works uniformly regardless of storage location
- Authentication is still required to access the download endpoint
