# Bug: Category Tree Endpoint Mismatch Causes Products Page Blank Screen

## Metadata
issue_number: ``
adw_id: ``
issue_json: ``

## Bug Description
When users try to add a new product or access the Products page, the application goes blank with console errors showing:
- `422 (Unprocessable Entity)` on `/api/categories/tree`
- `Cannot read properties of undefined (reading 'filter')` in ProductFilters.tsx:123

The frontend is calling `/api/categories/tree` which does not exist on the backend. The backend exposes `/api/categories/` (root path) which returns the category tree. This endpoint mismatch causes a 422 error, and the subsequent undefined state causes the component to crash.

## Problem Statement
1. **Endpoint Mismatch**: Frontend `categoryService.getTree()` calls `/categories/tree` but backend only provides `/categories/` for tree data
2. **Missing Error Handling**: When the category fetch fails, `tags` remains `undefined` instead of defaulting to an empty array, causing `tags.filter()` to crash the component

## Solution Statement
Fix the frontend API call to use the correct endpoint path `/categories` instead of `/categories/tree`. Additionally, add defensive coding to ensure `tags` state defaults to an empty array to prevent runtime crashes when API calls fail.

## Steps to Reproduce
1. Start the backend and frontend servers
2. Log in to the application
3. Navigate to the Products page (`/kompass/products`)
4. Observe the page goes blank
5. Check browser console - see 422 errors on `/api/categories/tree`
6. See TypeError: `Cannot read properties of undefined (reading 'filter')`

## Root Cause Analysis
1. **API Endpoint Mismatch**:
   - Frontend `kompassService.ts:287` calls `apiClient.get<CategoryTreeNode[]>('/categories/tree')`
   - Backend `category_routes.py:28-38` exposes `GET /api/categories/` which returns `List[CategoryTreeNode]`
   - There is no `/tree` sub-path on the backend

2. **Cascading Failure**:
   - The 422 error causes `fetchCategories()` to fail
   - Even though errors are caught, the `tags` state variable in ProductFilters can become `undefined` if the component renders before `fetchTags()` completes
   - Line 123: `const selectedTags = tags.filter(...)` crashes because `tags` is `undefined`

3. **State Initialization Issue**:
   - The `tags` state is initialized as an empty array `useState<TagResponse[]>([])`
   - However, the crash suggests a race condition or state management issue where `tags` becomes `undefined`

## Relevant Files
Use these files to fix the bug:

- `apps/Client/src/services/kompassService.ts` - Contains the `categoryService.getTree()` method that calls the wrong endpoint `/categories/tree` instead of `/categories`. This is the primary fix location.

- `apps/Client/src/components/kompass/ProductFilters.tsx` - The component that crashes when `tags` is undefined. Add defensive coding to handle undefined state gracefully.

- `apps/Server/app/api/category_routes.py` - Backend category routes for reference. The root `GET /` endpoint returns the tree structure. No changes needed here.

- Read `.claude/commands/test_e2e.md` to understand how to run E2E tests
- Read `.claude/commands/e2e/test_products_catalog.md` as a reference for creating E2E tests

### New Files
- `.claude/commands/e2e/test_products_filters.md` - E2E test file to validate the Products page filters functionality works correctly after the fix

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Fix the Category Service Endpoint
- Open `apps/Client/src/services/kompassService.ts`
- Locate the `categoryService.getTree()` method (around line 285-289)
- Change the endpoint from `/categories/tree` to `/categories`
- The method should call `apiClient.get<CategoryTreeNode[]>('/categories')` instead of `apiClient.get<CategoryTreeNode[]>('/categories/tree')`

### Step 2: Add Defensive Coding to ProductFilters
- Open `apps/Client/src/components/kompass/ProductFilters.tsx`
- Locate line 123 where `selectedTags` is calculated: `const selectedTags = tags.filter((t) => filters.tag_ids?.includes(t.id));`
- Add null check: `const selectedTags = (tags || []).filter((t) => filters.tag_ids?.includes(t.id));`
- This ensures the component doesn't crash if `tags` is unexpectedly undefined

### Step 3: Create E2E Test for Products Filters
- Read `.claude/commands/e2e/test_products_catalog.md` as a reference
- Create `.claude/commands/e2e/test_products_filters.md` with the following test steps:
  1. Navigate to Products page
  2. Verify the filters panel loads without errors
  3. Verify the Category dropdown is populated
  4. Verify the Supplier dropdown is populated
  5. Verify the Tags autocomplete is functional
  6. Apply a filter and verify products are filtered
  7. Clear filters and verify all products return
- Include screenshots to prove the bug is fixed

### Step 4: Run Validation Commands
- Execute all validation commands to ensure the bug is fixed with zero regressions

## Validation Commands
Execute every command to validate the bug is fixed with zero regressions.

- `cd /mnt/c/Users/user/danke_apps/Kompass/apps/Client && npm run typecheck` - Run Client type check to validate TypeScript compiles without errors
- `cd /mnt/c/Users/user/danke_apps/Kompass/apps/Client && npm run lint` - Run ESLint to check for code quality issues
- `cd /mnt/c/Users/user/danke_apps/Kompass/apps/Client && npm run build` - Run Client build to validate production build succeeds
- `cd /mnt/c/Users/user/danke_apps/Kompass/apps/Server && source .venv/bin/activate && python -m pytest tests/ -v --tb=short` - Run Server tests to ensure no regressions
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_products_filters.md` E2E test file to validate the Products page filters functionality works correctly

## Notes
- The backend API is correctly implemented. The issue is purely on the frontend service layer.
- The endpoint `/api/categories/` already returns the tree structure as `List[CategoryTreeNode]`, so no backend changes are needed.
- The 422 error is likely because the route `/api/categories/tree` doesn't exist and FastAPI returns 422 for unprocessable requests or route mismatches.
- After fixing the endpoint, manually verify by:
  1. Opening browser dev tools Network tab
  2. Navigating to Products page
  3. Confirming `GET /api/categories` returns 200 with category tree data
  4. Confirming the filters panel loads correctly with Category dropdown populated
