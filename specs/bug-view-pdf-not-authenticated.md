# Bug: View Full PDF returns "Not authenticated" error

## Metadata
issue_number: ``
adw_id: ``
issue_json: ``

## Bug Description
When clicking "View Full PDF" button in the Audit Summary Card, the user sees:
```json
{"detail":"Not authenticated"}
```

The expected behavior is that the PDF document should open in a new browser tab. Instead, the backend returns a 401 Unauthorized error because the JWT token is not included in the request.

## Problem Statement
The `/download` endpoint requires authentication via the `require_roles` dependency which expects a JWT token in the `Authorization: Bearer <token>` header. However, when the frontend opens the URL in a new browser tab using `window.open()`, it's a plain GET request without any headers - browsers don't include authorization headers when opening URLs in new tabs.

## Solution Statement
Add support for token-based authentication via query parameter for the download endpoint. The frontend will append the JWT token as a query parameter (`?token=xxx`) when opening the download URL. The backend will check for the token in the query parameter and validate it.

This is a common pattern for file download endpoints where the URL needs to be opened directly in the browser.

## Steps to Reproduce
1. Navigate to Suppliers page
2. Click edit on any supplier
3. Go to "Certification" tab
4. Ensure there's a completed audit with a PDF
5. Click "View Full PDF" button
6. **Observe**: New tab opens showing `{"detail":"Not authenticated"}`

## Root Cause Analysis
The root cause is a mismatch between authentication method and request type:

1. **Backend Authentication**: Uses HTTPBearer which requires `Authorization: Bearer <token>` header
2. **Frontend Request**: Uses `window.open(url, '_blank')` which opens a plain GET request
3. **Browser Behavior**: When opening a URL in a new tab, browsers don't include custom headers from the originating page
4. **Result**: The download endpoint receives the request without any authentication token

The fix requires either:
- Option A: Pass token as query parameter (simpler, chosen approach)
- Option B: Create a blob URL with fetch + auth header (more complex)

## Relevant Files
Use these files to fix the bug:

- `apps/Server/app/api/audit_routes.py` - Modify `/download` endpoint to accept token as query parameter
- `apps/Server/app/api/dependencies.py` - May need to add a helper function for query-based auth (or handle inline)
- `apps/Client/src/components/kompass/SupplierCertificationTab.tsx` - Update `handleViewPdf` to include token in URL

## Step by Step Tasks

### Step 1: Modify download endpoint to accept token as query parameter
- Open `apps/Server/app/api/audit_routes.py`
- Import `Optional` from typing and `Query` if not already imported
- Modify the `download_audit_pdf` endpoint:
  - Remove `current_user` dependency from function signature
  - Add `token: Optional[str] = Query(default=None)` parameter
  - Add token validation logic at the beginning of the function:
    ```python
    # Validate token from query parameter
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = auth_service.decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    ```
  - Import `auth_service` from `app.services.auth_service`

### Step 2: Update frontend to include token in download URL
- Open `apps/Client/src/components/kompass/SupplierCertificationTab.tsx`
- Modify the `handleViewPdf` function to:
  - Get the JWT token from localStorage (where it's stored after login)
  - Append the token as a query parameter to the download URL
  ```typescript
  const handleViewPdf = (auditId: string) => {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
    const token = localStorage.getItem('token');
    const downloadUrl = `${apiUrl}/suppliers/${supplierId}/audits/${auditId}/download?token=${token}`;
    console.log(`INFO [SupplierCertificationTab]: Opening PDF via backend: ${downloadUrl}`);
    window.open(downloadUrl, '_blank');
  };
  ```

### Step 3: Update E2E test for View Audit PDF
- Open `.claude/commands/e2e/test_view_audit_pdf.md`
- Add a test scenario that verifies authentication works:
  - Verify the download URL includes a token parameter
  - Verify PDF opens successfully without authentication errors

### Step 4: Run validation commands
- Execute all validation commands to ensure no regressions

## Validation Commands
Execute every command to validate the bug is fixed with zero regressions.

```bash
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
2. Login as a user
3. Navigate to Suppliers > Edit Supplier > Certification tab
4. Click "View Full PDF" on any audit
5. Verify PDF opens in new tab without "Not authenticated" error
6. Verify the URL in the new tab includes `?token=...`

## Notes
1. **Security Consideration**: Tokens in URLs can be logged in browser history and server logs. However, this is acceptable for file download endpoints because:
   - The token is short-lived (24 hours by default)
   - The endpoint only returns PDF files, not sensitive data modification
   - This is a common pattern used by many applications (Google Drive, Dropbox, etc.)
2. **Alternative Approach**: Could use a temporary signed URL pattern, but that adds complexity
3. **Token Storage**: The frontend stores the JWT token in `localStorage` under the key `token` (verify this by checking auth context/service)
