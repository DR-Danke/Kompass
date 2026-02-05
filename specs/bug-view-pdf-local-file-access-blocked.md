# Bug: View Full PDF fails with "Not allowed to load local resource"

## Metadata
issue_number: ``
adw_id: ``
issue_json: ``

## Bug Description
When clicking "View Full PDF" button in the Audit Summary Card, the browser displays an error:
```
Not allowed to load local resource: file:///tmp/audit_5l53l2zj.pdf
```

The expected behavior is that clicking "View Full PDF" should open the PDF document in a new browser tab. Instead, the browser blocks the request because it cannot load local `file://` URLs for security reasons.

## Problem Statement
The `handleViewPdf` function in `SupplierCertificationTab.tsx` calls `window.open(documentUrl, '_blank')` which works for HTTPS URLs (from Supabase Storage) but fails for `file://` URLs (from local development or legacy audit records).

Browsers block `file://` URLs from web pages for security reasons - a web page cannot access local filesystem resources.

## Solution Statement
Create a backend API endpoint that serves audit PDF files. For `file://` URLs, read the file from disk and stream it to the client. For HTTPS URLs (Supabase Storage), either redirect to the URL or proxy the request.

The frontend will call this new endpoint instead of trying to open the URL directly.

## Steps to Reproduce
1. Navigate to Suppliers page
2. Click edit on any supplier
3. Go to "Certification" tab
4. Upload a PDF audit document (when Supabase Storage is not configured)
5. Wait for processing to complete
6. Click "View Full PDF" button
7. **Observe**: Browser console shows "Not allowed to load local resource: file:///tmp/..."

## Root Cause Analysis
The root cause is a mismatch between storage location and access method:

1. **Local Development Storage**: When Supabase Storage is not configured, audit files are saved to `/tmp/` with `file://` URLs stored in the database
2. **Browser Security**: Web browsers block `file://` URLs from web pages to prevent security vulnerabilities
3. **Direct URL Access**: The frontend calls `window.open(documentUrl)` which works for `https://` URLs but fails for `file://` URLs

The fix requires the backend to serve the PDF content, either by:
- Reading local files and streaming them
- Redirecting/proxying Supabase Storage URLs

## Relevant Files
Use these files to fix the bug:

- `apps/Server/app/api/audit_routes.py` - Add new endpoint to serve PDF files
- `apps/Client/src/components/kompass/SupplierCertificationTab.tsx` - Update `handleViewPdf` to use the new backend endpoint
- `apps/Client/src/components/kompass/AuditSummaryCard.tsx` - Receives the `onViewPdf` callback (no changes needed, just for context)
- `apps/Client/src/services/kompassService.ts` - May need to add a method or use direct URL
- Read `.claude/commands/e2e/test_audit_extraction_fix.md` for E2E test format reference

### New Files
- `.claude/commands/e2e/test_view_audit_pdf.md` - E2E test to validate PDF viewing works

## Step by Step Tasks

### Step 1: Add PDF download endpoint to audit_routes.py
- Open `apps/Server/app/api/audit_routes.py`
- Add a new GET endpoint `/{supplier_id}/audits/{audit_id}/download`
- The endpoint should:
  - Verify the audit exists and belongs to the supplier
  - Get the `document_url` from the audit record
  - If URL starts with `file://`:
    - Extract the local path
    - Read the file content
    - Return as a StreamingResponse with `application/pdf` content type
  - If URL starts with `https://`:
    - Return a RedirectResponse to the Supabase Storage URL
  - Set appropriate headers: `Content-Disposition: inline; filename="audit.pdf"` for inline viewing
- Add appropriate authentication (require viewer role or above)

### Step 2: Update frontend to use the new endpoint
- Open `apps/Client/src/components/kompass/SupplierCertificationTab.tsx`
- Modify the `handleViewPdf` function to:
  - Instead of `window.open(documentUrl, '_blank')`
  - Construct the backend URL: `/api/suppliers/{supplierId}/audits/{auditId}/download`
  - Open this URL in a new tab: `window.open(backendUrl, '_blank')`
- Update the `AuditSummaryCard` component usage to pass the audit ID instead of document URL
  - Change `onViewPdf` callback signature from `(documentUrl: string) => void` to `(auditId: string) => void`

### Step 3: Update AuditSummaryCard props and callback
- Open `apps/Client/src/components/kompass/AuditSummaryCard.tsx`
- Change the `onViewPdf` prop type from `(documentUrl: string) => void` to `(auditId: string) => void`
- Update the button onClick handlers to pass `audit.id` instead of `audit.document_url`

### Step 4: Create E2E test file
- Read `.claude/commands/e2e/test_audit_extraction_fix.md` for reference
- Create `.claude/commands/e2e/test_view_audit_pdf.md` that validates:
  - User can navigate to supplier certification tab
  - User can see "View Full PDF" button on a completed audit
  - Clicking the button opens the PDF in a new tab (no console errors)
  - The PDF content is displayed correctly

### Step 5: Run validation commands
- Execute all validation commands to ensure no regressions

## Validation Commands
Execute every command to validate the bug is fixed with zero regressions.

```bash
# Verify the new endpoint exists in audit_routes
grep -q "download" apps/Server/app/api/audit_routes.py && echo "download endpoint found" || echo "download endpoint MISSING"

# Run Server tests
cd apps/Server && .venv/bin/pytest tests/api/test_audit_routes.py -v --tb=short

# Run all Server tests
cd apps/Server && .venv/bin/pytest tests/ -v --tb=short

# Run Client type check
cd apps/Client && npm run typecheck

# Run Client build
cd apps/Client && npm run build
```

After implementation, manually test:
1. Start the application
2. Navigate to Suppliers > Edit Supplier > Certification tab
3. Click "View Full PDF" on an audit with a local file URL
4. Verify PDF opens in new tab without console errors

Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_view_audit_pdf.md` to validate this functionality works.

## Notes
1. **Security**: The new endpoint must verify authentication and that the audit belongs to the requested supplier
2. **Content-Disposition**: Use `inline` (not `attachment`) so the PDF opens in the browser rather than downloading
3. **CORS**: The endpoint returns a file, so CORS shouldn't be an issue when using RedirectResponse for Supabase URLs
4. **Backwards Compatibility**: This fix works for both old `file://` URLs and new Supabase Storage URLs
5. **Temp File Cleanup**: Local temp files may get deleted on server restart; this is expected behavior for development. Production should always use Supabase Storage.
