# Bug: Fix Portfolios Module Network Error

## Metadata
issue_number: `115`
adw_id: `d079f018`
issue_json: `{"number":115,"title":"Error when going to the Portfolios module","body":"When I go to the Portfolios module, I get this error:\n\nindex-CYoJxiFF.js:301 ERROR [apiClient]: Response error: undefined Network Error\n...\nindex-CYoJxiFF.js:366 ERROR [PortfoliosPage]: Failed to fetch niches: AxiosError: Network Error"}`

## Bug Description
When the user navigates to the Portfolios module, the page fails to load data and displays network errors in the browser console. Two errors are logged:
1. `ERROR [apiClient]: Response error: undefined Network Error` — a raw network-level failure with no HTTP status code (`undefined` means `error.response?.status` is undefined)
2. `ERROR [PortfoliosPage]: Failed to fetch niches: AxiosError: Network Error` — the PortfoliosPage's niche fetch fails

**Expected behavior:** The Portfolios page loads successfully, displaying the portfolio list with niche filter options.

**Actual behavior:** The page shows errors and no data is loaded. The console logs "Network Error" with no HTTP status code for both the portfolios list and niches list API calls.

## Problem Statement
The frontend `nicheService.list()` and `portfolioService.list()` / `portfolioService.create()` methods call `GET /niches`, `GET /portfolios`, and `POST /portfolios` respectively, without trailing slashes. However, the backend niche router defines its list/create endpoints as `@router.get("/")` and `@router.post("/")` (with trailing slashes). The portfolio router uses `@router.get("")` and `@router.post("")` (empty string). FastAPI's default `redirect_slashes=True` behavior sends a 307 redirect from `/api/niches` to `/api/niches/`. In the deployed environment (frontend on Vercel HTTPS, backend on Render HTTPS on different origins), this 307 redirect does not carry CORS headers, causing the browser to block the redirected request with a raw "Network Error".

## Solution Statement
Add trailing slashes to the frontend `nicheService` and `portfolioService` API calls (`list` and `create` methods) to match the backend route definitions and eliminate the 307 redirects. This is the same fix pattern applied in PR #112 for the `userService` and issue #113 for the `categoryService`/`tagService`.

## Steps to Reproduce
1. Deploy the application (frontend on Vercel, backend on Render) or simulate cross-origin requests
2. Log in with valid credentials
3. Navigate to the Portfolios page via the sidebar navigation
4. Observe the error in the console: `ERROR [apiClient]: Response error: undefined Network Error`
5. Observe the error: `ERROR [PortfoliosPage]: Failed to fetch niches: AxiosError: Network Error`

## Root Cause Analysis
The root cause is a **trailing slash mismatch** between frontend API calls and backend route definitions:

**Frontend calls (in `apps/Client/src/services/kompassService.ts`):**
- `nicheService.list()` → `GET /niches` (line 169, no trailing slash)
- `nicheService.create()` → `POST /niches` (line 183, no trailing slash)
- `portfolioService.list()` → `GET /portfolios` (line 493, no trailing slash)
- `portfolioService.create()` → `POST /portfolios` (line 507, no trailing slash)

**Backend route definitions:**
- `apps/Server/app/api/niche_routes.py` line 21: `@router.get("/", ...)` — trailing slash
- `apps/Server/app/api/niche_routes.py` line 34: `@router.post("/", ...)` — trailing slash
- `apps/Server/app/api/portfolio_routes.py` line 45: `@router.get("", ...)` — empty string (registered as `/api/portfolios` without slash, but FastAPI redirects `/api/portfolios` to `/api/portfolios/` due to `redirect_slashes=True`)
- `apps/Server/app/api/portfolio_routes.py` line 153: `@router.post("", ...)` — empty string

**Route registration in `apps/Server/main.py`:**
- Line 80: `app.include_router(niche_router, prefix="/api/niches")`
- Line 82: `app.include_router(portfolio_router, prefix="/api/portfolios")`

FastAPI's `redirect_slashes=True` (default) redirects `GET /api/niches` → `GET /api/niches/` via 307. In a cross-origin deployment, the 307 redirect response does not include CORS headers, so the browser blocks the follow-up request, resulting in `AxiosError` with no `response` object (hence `undefined` status) and `message: "Network Error"`.

**Call chain on page load:**
1. `PortfoliosPage.tsx` line 74-84: `useEffect` calls `nicheService.list(1, 100)` → triggers network error
2. `usePortfolios.ts` line 69: calls `portfolioService.list(...)` → triggers network error

This is the exact same pattern fixed in issue #113 for categories/tags and PR #112 for users.

## Relevant Files
Use these files to fix the bug:

- `apps/Client/src/services/kompassService.ts` — Contains the `nicheService` and `portfolioService` objects with API calls missing trailing slashes. This is the **only file that needs modification**.
- `apps/Client/src/pages/kompass/PortfoliosPage.tsx` — The page component that calls `nicheService.list()` on mount (line 77); no changes needed but useful for understanding the call chain.
- `apps/Client/src/hooks/kompass/usePortfolios.ts` — Hook that calls `portfolioService.list()` on page load (line 69); no changes needed but useful for understanding the call chain.
- `apps/Server/app/api/niche_routes.py` — Backend routes confirming trailing slash usage (`"/"`); no changes needed.
- `apps/Server/app/api/portfolio_routes.py` — Backend routes confirming empty string usage (`""`); no changes needed.
- `apps/Server/main.py` — Route registration confirming prefixes; no changes needed.
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_categories_network_error_fix.md` to understand how to create E2E validation tests.

### New Files
- `.claude/commands/e2e/test_portfolios_network_error_fix.md` — New E2E test file to validate the portfolios page loads without network errors.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Add trailing slashes to nicheService API calls
- Open `apps/Client/src/services/kompassService.ts`
- Line 169: Change `'/niches'` to `'/niches/'` in the `list()` method
- Line 183: Change `'/niches'` to `'/niches/'` in the `create()` method
- Do NOT modify `get()`, `update()`, or `delete()` — those use path parameters like `/niches/${id}` which resolve correctly without trailing slashes

### Step 2: Add trailing slashes to portfolioService API calls
- In the same file `apps/Client/src/services/kompassService.ts`
- Line 493: Change `'/portfolios'` to `'/portfolios/'` in the `list()` method
- Line 507: Change `'/portfolios'` to `'/portfolios/'` in the `create()` method
- Do NOT modify `get()`, `update()`, `delete()`, `duplicate()`, `getShareToken()`, `getPublic()`, `exportPdf()`, or `createFromFilters()` — those use path parameters or subpaths like `/portfolios/${id}` which resolve correctly

### Step 3: Create E2E test file for portfolios network error fix validation
- Read `.claude/commands/e2e/test_categories_network_error_fix.md` and `.claude/commands/e2e/test_basic_query.md` to understand the E2E test file format
- Create `.claude/commands/e2e/test_portfolios_network_error_fix.md` that validates:
  1. Navigate to the Portfolios page
  2. Verify the page loads with the title "Portfolios" visible
  3. Verify no error alert or snackbar is displayed on the page
  4. Verify the portfolios section renders (either portfolio cards or empty state)
  5. Verify the niche filter dropdown loads with options (or is present)
  6. Verify no "Network Error" messages appear in the console
  7. Verify API requests to `/api/niches/` and `/api/portfolios/` return successful responses
  8. Take screenshots to prove the fix works

### Step 4: Run validation commands
- Run all validation commands listed below to confirm zero regressions

## Validation Commands
Execute every command to validate the bug is fixed with zero regressions.

- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate no TypeScript errors were introduced
- `cd apps/Client && npm run build` — Run Client build to validate the application builds successfully
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_portfolios_network_error_fix.md` E2E test file to validate the portfolios page loads without network errors

## Notes
- This is the same class of bug fixed in PR #112 for the `/users` endpoints and issue #113 for the `/categories` and `/tags` endpoints. The trailing slash mismatch causes 307 redirects that fail in cross-origin deployments due to missing CORS headers on the redirect response.
- The fix is minimal: only 4 string changes in `kompassService.ts` (2 for niches, 2 for portfolios).
- Other services (e.g., `supplierService`, `productService`) may have the same trailing slash issue but are out of scope for this bug report which specifically targets the Portfolios module.
