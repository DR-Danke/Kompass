# Bug: Fix Categories Module Network Error

## Metadata
issue_number: `113`
adw_id: `12b2f588`
issue_json: `{"number":113,"title":"Network error in the Categories Module","body":"When the user goes to the categories module, a network error comes up \nindex-C39CJJzg.js:301 ERROR [apiClient]: Response error: undefined Network Error"}`

## Bug Description
When the user navigates to the Categories & Tags management page, a network error is displayed immediately on page load. The browser console shows: `ERROR [apiClient]: Response error: undefined Network Error`. The `undefined` indicates `error.response?.status` is undefined, meaning there is no HTTP response object at all — this is a raw network-level failure, not an API error with a status code.

**Expected behavior:** The Categories page loads successfully, displaying the category tree and tags list.

**Actual behavior:** The page shows an error alert and no data is loaded. The console logs a "Network Error" with no HTTP status code.

## Problem Statement
The frontend `categoryService.getTree()` and `tagService.list()` methods call `GET /categories` and `GET /tags` respectively, without trailing slashes. However, the backend category and tag routers define their list endpoints as `@router.get("/")` (with a trailing slash). FastAPI's default `redirect_slashes=True` behavior sends a 307 redirect from `/api/categories` to `/api/categories/`. In the deployed environment (frontend on Vercel HTTPS, backend on Render HTTPS on different origins), this 307 redirect does not carry CORS headers, causing the browser to block the redirected request with a raw "Network Error".

## Solution Statement
Add trailing slashes to the frontend `categoryService` and `tagService` API calls (`getTree`, `list`, `create` methods) to match the backend route definitions and eliminate the 307 redirects. This is the same fix pattern applied in PR #112 for the `userService`.

## Steps to Reproduce
1. Deploy the application (frontend on Vercel, backend on Render) or simulate cross-origin requests
2. Log in with valid credentials
3. Navigate to the Categories & Tags page via the sidebar
4. Observe the error alert on the page and the console error: `ERROR [apiClient]: Response error: undefined Network Error`

## Root Cause Analysis
The root cause is a **trailing slash mismatch** between frontend API calls and backend route definitions:

**Frontend calls (in `apps/Client/src/services/kompassService.ts`):**
- `categoryService.getTree()` → `GET /categories` (line 401, no trailing slash)
- `categoryService.list()` → `GET /categories` (line 393, no trailing slash)
- `categoryService.create()` → `POST /categories` (line 413, no trailing slash)
- `tagService.list()` → `GET /tags` (line 444, no trailing slash)
- `tagService.create()` → `POST /tags` (line 458, no trailing slash)

**Backend route definitions:**
- `apps/Server/app/api/category_routes.py` line 28: `@router.get("/"...)` — trailing slash
- `apps/Server/app/api/category_routes.py` line 41: `@router.post("/"...)` — trailing slash
- `apps/Server/app/api/tag_routes.py` line 22: `@router.get("/"...)` — trailing slash
- `apps/Server/app/api/tag_routes.py` line 61: `@router.post("/"...)` — trailing slash

FastAPI's `redirect_slashes=True` (default) redirects `GET /api/categories` → `GET /api/categories/` via 307. In a cross-origin deployment, the 307 redirect response does not include CORS headers, so the browser blocks the follow-up request, resulting in `AxiosError` with no `response` object (hence `undefined` status) and `message: "Network Error"`.

This is the exact same pattern that was fixed in PR #112 for the `/users` endpoints.

## Relevant Files
Use these files to fix the bug:

- `apps/Client/src/services/kompassService.ts` — Contains the `categoryService` and `tagService` objects with API calls missing trailing slashes. This is the **only file that needs modification**.
- `apps/Client/src/hooks/useCategories.ts` — Hook that calls `categoryService.getTree()` on page load; no changes needed but useful for understanding the call chain.
- `apps/Client/src/hooks/useTags.ts` — Hook that calls `tagService.list()` on page load; no changes needed but useful for understanding the call chain.
- `apps/Client/src/pages/kompass/CategoriesPage.tsx` — The page component that triggers both hooks on mount; no changes needed.
- `apps/Client/src/api/clients/index.ts` — The axios client with error interceptor that logs the "Network Error"; no changes needed.
- `apps/Server/app/api/category_routes.py` — Backend routes confirming trailing slash usage (`"/"`); no changes needed.
- `apps/Server/app/api/tag_routes.py` — Backend routes confirming trailing slash usage (`"/"`); no changes needed.
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_categories_tags_management.md` to understand how to run E2E validation.

### New Files
- `.claude/commands/e2e/test_categories_network_error_fix.md` — New E2E test file to validate the categories page loads without network errors.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Add trailing slashes to categoryService API calls
- Open `apps/Client/src/services/kompassService.ts`
- Line 393: Change `'/categories'` to `'/categories/'` in the `list()` method
- Line 401: Change `'/categories'` to `'/categories/'` in the `getTree()` method
- Line 413: Change `'/categories'` to `'/categories/'` in the `create()` method
- Do NOT modify `get()`, `update()`, `delete()`, or `move()` — those use path parameters like `/categories/${id}` which resolve correctly without trailing slashes

### Step 2: Add trailing slashes to tagService API calls
- In the same file `apps/Client/src/services/kompassService.ts`
- Line 444: Change `'/tags'` to `'/tags/'` in the `list()` method
- Line 458: Change `'/tags'` to `'/tags/'` in the `create()` method
- Do NOT modify `get()`, `update()`, `delete()`, or `search()` — those use path parameters or subpaths

### Step 3: Create E2E test file for network error fix validation
- Read `.claude/commands/e2e/test_categories_tags_management.md` and `.claude/commands/e2e/test_users_admin_page.md` as reference for format
- Create `.claude/commands/e2e/test_categories_network_error_fix.md` that validates:
  1. Navigate to the Categories page
  2. Verify the page loads without any "Network Error" in the console
  3. Verify the categories section renders (either empty state or categories tree)
  4. Verify the tags section renders (either empty state or tag chips)
  5. Verify no error alert is displayed on the page
  6. Take screenshots to prove the fix works

### Step 4: Run validation commands
- Run all validation commands listed below to confirm zero regressions

## Validation Commands
Execute every command to validate the bug is fixed with zero regressions.

- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate no TypeScript errors were introduced
- `cd apps/Client && npm run build` — Run Client build to validate the application builds successfully
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_categories_network_error_fix.md` E2E test file to validate the categories page loads without network errors

## Notes
- This is the same class of bug fixed in PR #112 for the `/users` endpoints (commit `8bd99db`). The trailing slash mismatch causes 307 redirects that fail in cross-origin deployments due to missing CORS headers on the redirect response.
- Other services (`nicheService`, `supplierService`, `productService`, etc.) may have the same trailing slash issue, but since the bug report specifically targets the Categories module, this fix is scoped to `categoryService` and `tagService` only (the two services used by the Categories page).
- The `categoryService.move()` method also has a secondary issue: it sends `parent_id` in the payload but the backend `CategoryMoveDTO` expects `new_parent_id`. This is a separate bug that does not affect page load but should be tracked as a follow-up issue.
- No new libraries are needed for this fix.
