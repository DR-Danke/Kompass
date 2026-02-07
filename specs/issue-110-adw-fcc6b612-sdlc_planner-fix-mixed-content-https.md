# Bug: Mixed Content HTTPS Error on Users Administration Module

## Metadata
issue_number: `110`
adw_id: `fcc6b612`
issue_json: `{"number":110,"title":"Error when going to the users administration module","body":"users:1 Mixed Content: The page at 'https://kompass-poc26.vercel.app/users' was loaded over HTTPS, but requested an insecure XMLHttpRequest endpoint 'http://kompass-sv2y.onrender.com/api/users/?page=1&limit=20'. This request has been blocked; the content must be served over HTTPS."}`

## Bug Description
When navigating to the Users administration page at `https://kompass-poc26.vercel.app/users`, the browser blocks all API requests because the frontend (served over HTTPS) is making requests to the backend using HTTP (`http://kompass-sv2y.onrender.com/api/users/...`). Modern browsers enforce the Mixed Content policy, which prevents HTTPS pages from making insecure HTTP XMLHttpRequest/fetch calls. This results in a complete failure to load any data on the Users page (and potentially all other pages making API calls).

**Expected behavior:** The frontend should make API requests over HTTPS to `https://kompass-sv2y.onrender.com/api/...` when the page itself is served over HTTPS.

**Actual behavior:** The frontend makes API requests over HTTP to `http://kompass-sv2y.onrender.com/api/...`, which are blocked by the browser's mixed content security policy, resulting in a "Network Error".

## Problem Statement
The API client in the frontend (`apps/Client/src/api/clients/index.ts`) uses the `VITE_API_URL` environment variable as-is without any protocol validation. If `VITE_API_URL` is configured with `http://` (either in the Vercel environment or as a fallback), and the frontend is served over HTTPS, all API requests will be blocked by the browser's mixed content policy. The application needs a safeguard to ensure API requests always use HTTPS when the page is loaded over HTTPS.

## Solution Statement
Add a URL sanitization utility in the API client initialization (`apps/Client/src/api/clients/index.ts`) that automatically upgrades `http://` URLs to `https://` when the current page is served over HTTPS. This ensures that regardless of how `VITE_API_URL` is configured (in Vercel env vars, `.env` files, or the fallback default), the API client will never make mixed content requests in production. The fix preserves `http://` for local development (where the page is served over `http://localhost`).

## Steps to Reproduce
1. Deploy the frontend to Vercel (served over HTTPS at `https://kompass-poc26.vercel.app`)
2. Set `VITE_API_URL` in Vercel environment variables to `http://kompass-sv2y.onrender.com/api` (HTTP, not HTTPS)
3. Navigate to `https://kompass-poc26.vercel.app/users`
4. Open browser DevTools Console
5. Observe: `Mixed Content: The page at 'https://kompass-poc26.vercel.app/users' was loaded over HTTPS, but requested an insecure XMLHttpRequest endpoint 'http://kompass-sv2y.onrender.com/api/users/?page=1&limit=20'. This request has been blocked.`
6. The Users page shows a network error and no data is loaded

## Root Cause Analysis
The root cause is twofold:

1. **No protocol enforcement in API client:** The `apiClient` in `apps/Client/src/api/clients/index.ts` directly uses `import.meta.env.VITE_API_URL` without checking whether the protocol matches the current page's protocol. Line 3: `const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';`

2. **Environment variable misconfiguration:** The `VITE_API_URL` environment variable in the Vercel deployment is set with `http://` instead of `https://`. Render provides HTTPS for all services by default (`https://kompass-sv2y.onrender.com`), so the backend already supports HTTPS — the frontend just isn't using it.

The fix should address the code-level issue (adding protocol auto-upgrade) so the application is resilient to environment variable misconfiguration. This prevents the same class of bug from recurring even if someone accidentally sets an HTTP URL in production.

## Relevant Files
Use these files to fix the bug:

- `apps/Client/src/api/clients/index.ts` — The central API client that initializes axios with the base URL. This is where the protocol upgrade logic needs to be added (line 3).
- `apps/Client/src/components/kompass/SupplierCertificationTab.tsx` — Also reads `VITE_API_URL` directly (line 103) to construct a PDF download URL. This is a secondary location that also needs the protocol fix.
- `apps/Client/.env` — Local development environment file. Should remain unchanged (HTTP for localhost is correct for dev).
- `.env.sample` — Sample environment file for documentation. Should be updated to note HTTPS requirement for production.
- `.claude/commands/test_e2e.md` — E2E test runner instructions (reference for creating E2E test).
- `.claude/commands/e2e/test_suppliers_page.md` — Example E2E test file (reference for format).

### New Files
- `.claude/commands/e2e/test_users_admin_page.md` — New E2E test to validate the Users administration page loads correctly and API calls succeed without mixed content errors.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Add HTTPS Protocol Upgrade Logic to API Client
- Open `apps/Client/src/api/clients/index.ts`
- After reading `VITE_API_URL` on line 3, add a function that checks if the current page is served over HTTPS (`window.location.protocol === 'https:'`) and the API URL starts with `http://` (not `https://`)
- If both conditions are true, replace `http://` with `https://` in the API URL
- This should be a simple inline operation, not an abstraction — something like:
  ```typescript
  let apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
  if (window.location.protocol === 'https:' && apiUrl.startsWith('http://')) {
    apiUrl = apiUrl.replace('http://', 'https://');
  }
  const API_URL = apiUrl;
  ```
- The existing `console.log` on line 5 will automatically reflect the corrected URL

### Step 2: Fix Direct VITE_API_URL Usage in SupplierCertificationTab
- Open `apps/Client/src/components/kompass/SupplierCertificationTab.tsx`
- On line 103, the component reads `VITE_API_URL` directly: `const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';`
- Apply the same HTTPS upgrade logic here:
  ```typescript
  let apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
  if (window.location.protocol === 'https:' && apiUrl.startsWith('http://')) {
    apiUrl = apiUrl.replace('http://', 'https://');
  }
  ```
- This ensures the PDF download URL also uses HTTPS in production

### Step 3: Update .env.sample Documentation
- Open `.env.sample`
- On line 33, update the comment for `VITE_API_URL` to note that production deployments must use `https://`:
  ```
  # IMPORTANT: Use https:// for production deployments to avoid mixed content errors
  VITE_API_URL=http://localhost:8000/api
  ```

### Step 4: Create E2E Test for Users Administration Page
- Read `.claude/commands/e2e/test_suppliers_page.md` and `.claude/commands/test_e2e.md` to understand the E2E test format
- Create a new E2E test file at `.claude/commands/e2e/test_users_admin_page.md` that validates:
  - Navigate to `/users` page
  - Verify the page loads without errors (no mixed content, no network errors)
  - Verify the users table is displayed with data (headers: Name, Email, Role, Status, Actions)
  - Verify API requests to `/api/users/` succeed (no console errors)
  - Take screenshots at each step
- The test should be minimal — focused on proving the mixed content bug is fixed

### Step 5: Run Validation Commands
- Execute all validation commands listed below to confirm the fix works with zero regressions

## Validation Commands
Execute every command to validate the bug is fixed with zero regressions.

- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate no TypeScript errors were introduced
- `cd apps/Client && npm run build` — Run Client production build to validate the fix compiles correctly
- `cd apps/Client && npm run lint` — Run ESLint to validate code quality
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_users_admin_page.md` E2E test file to validate the Users page loads correctly without mixed content errors

## Notes
- Render provides HTTPS by default for all services. The backend at `https://kompass-sv2y.onrender.com` is accessible over HTTPS, so no backend changes are needed.
- The fix is purely frontend — it adds a runtime safeguard that upgrades HTTP to HTTPS when the page itself is HTTPS.
- Local development (http://localhost) is unaffected because the page protocol is `http:`, so the upgrade logic does not trigger.
- The Vercel environment variable `VITE_API_URL` should also be corrected to use `https://` directly, but the code fix ensures resilience regardless of configuration.
- No new libraries are needed for this fix.
