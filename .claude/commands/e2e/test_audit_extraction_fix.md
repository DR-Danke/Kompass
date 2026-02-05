# E2E Test: Audit Extraction Fix Validation

## Overview

This E2E test validates that the audit extraction bug fix is working correctly. The fix addresses the issue where PDF uploads would fail with "Extraction failed. The audit document could not be processed." due to missing `pdf2image` dependency and incorrect handling of `file://` URLs.

## User Story

As a sourcing manager, I want to upload factory audit PDFs and have them processed successfully so that I can view extracted supplier information without encountering extraction errors.

## Prerequisites

- Application running (frontend on port 5173, backend on port 8000)
- Test user credentials available
- Test PDF file available for upload
- `poppler-utils` installed on the system (`sudo apt-get install poppler-utils`)
- `pdf2image` Python package installed
- At least one supplier in the database
- `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` configured in `.env` (optional - extraction will complete but with empty data if not set)

## Test Scenarios

### Scenario 1: Successful PDF Upload and Processing

**Objective:** Verify that PDF upload no longer fails with "Extraction failed" error.

#### Steps

1. **Navigate to Suppliers Page**
   - Open application at http://localhost:5173
   - Login with test credentials
   - Navigate to `/suppliers` page
   - **Verify** page title "Suppliers" is visible
   - **Screenshot**: `01_suppliers_page.png`

2. **Open Supplier for Editing**
   - Click the edit (pencil) icon or three-dot menu on any supplier
   - **Verify** supplier dialog opens
   - **Screenshot**: `02_supplier_dialog.png`

3. **Switch to Certification Tab**
   - Click on "Certification" tab
   - **Verify** tab is active and upload area is visible
   - **Screenshot**: `03_certification_tab.png`

4. **Upload a PDF File**
   - Click the upload area or drag-and-drop a test PDF file
   - **Verify** upload progress indicator appears
   - **Verify** status changes to "Processing..."
   - **Screenshot**: `04_upload_processing.png`

5. **Wait for Extraction to Complete**
   - Wait up to 60 seconds for processing to finish
   - **Critical Check**: The error "Extraction failed. The audit document could not be processed." should NOT appear
   - **Verify** one of the following occurs:
     - Audit Summary Card appears with extracted data (if AI API key configured)
     - Audit Summary Card appears with "AI service not available" message (if no API key)
   - **Screenshot**: `05_extraction_complete.png`

6. **Verify No Error State**
   - **Verify** the red error alert is NOT visible
   - **Verify** "Reprocess" button is available (indicates extraction completed, even if empty)
   - **Screenshot**: `06_no_error_state.png`

### Scenario 2: Verify Local File Reading Works

**Objective:** Confirm that the backend correctly reads files from local `file://` URLs.

#### Steps

7. **Check Backend Logs**
   - Open the backend terminal
   - Look for log messages like:
     - `INFO [AuditService]: Fetching document from file:///tmp/...`
     - `INFO [AuditService]: Read XXXX bytes`
     - NOT `ERROR [AuditService]: httpx client error` or similar
   - **Verify** no httpx-related errors for file:// URLs

### Scenario 3: Error Handling for Missing Dependencies

**Objective:** Verify informative error messages when dependencies are missing.

#### Steps (Only if testing dependency errors)

8. **Test Without Poppler (if applicable)**
   - If poppler is not installed, upload a PDF
   - **Verify** error message mentions "poppler-utils" with installation instructions
   - **Verify** error is user-friendly, not a raw stack trace

## Success Criteria Checklist

- [ ] PDF file uploads successfully (no immediate errors)
- [ ] Processing status shows "Processing..." during extraction
- [ ] **CRITICAL**: "Extraction failed" error does NOT appear for valid PDFs
- [ ] Backend logs show successful file reading from file:// URLs
- [ ] Audit record is created with status "completed" (not "failed")
- [ ] If AI API configured: extracted data displays in summary card
- [ ] If no AI API: summary card shows "AI service not available" but no hard failure
- [ ] Reprocess button is functional
- [ ] No console errors in browser

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

2. Verify dependencies:
   ```bash
   # Check poppler
   which pdftoppm

   # Check pdf2image
   cd apps/Server && .venv/bin/pip list | grep pdf2image
   ```

3. Upload a test PDF and monitor backend logs for:
   - `INFO [AuditService]: Fetching document from file://...`
   - `INFO [AuditService]: Read XXXX bytes`
   - `INFO [AuditService]: Converted X PDF pages to images`
   - `INFO [AuditService]: Extraction completed for audit ...`

## Notes

- The fix resolves the issue where `httpx` cannot fetch `file://` URLs
- Local file reading is now handled separately from remote URL fetching
- Better error messages are provided for missing `pdf2image` or `poppler-utils`
- If extraction still fails, check:
  1. Is `poppler-utils` installed?
  2. Is `pdf2image` installed?
  3. Are AI API keys configured in `.env`?
  4. Check backend logs for specific error messages
