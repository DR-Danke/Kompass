# Bug: Fix "Cannot read properties of undefined (reading 'map')" when creating a new portfolio

## Metadata
issue_number: `119`
adw_id: `f44ba4a1`
issue_json: `{"number":119,"title":"Error when creating a new portfolio","body":"When I click on the option for creating a new portfolio, the console shows this error and the screen goes blank.\n\nError: \nindex-C39CJJzg.js:366 Uncaught TypeError: Cannot read properties of undefined (reading 'map')\n    at dIe (index-C39CJJzg.js:366:137963)\n    at Zw (index-C39CJJzg.js:48:47928)\n    at vC (index-C39CJJzg.js:48:70703)\n    at Az (index-C39CJJzg.js:48:81011)\n    at nL (index-C39CJJzg.js:48:116666)\n    at _V (index-C39CJJzg.js:48:115709)\n    at C1 (index-C39CJJzg.js:48:115539)\n    at Qz (index-C39CJJzg.js:48:112353)\n    at fL (index-C39CJJzg.js:48:124047)\n    at MessagePort.k (index-C39CJJzg.js:25:1531)"}`

## Bug Description
When navigating to create a new portfolio (clicking "Create Portfolio" on the Portfolios page, which navigates to `/portfolios/new`), the application crashes with a white screen and a console error: `Uncaught TypeError: Cannot read properties of undefined (reading 'map')`. The expected behavior is that the Portfolio Builder page renders with an empty portfolio on the right and the product catalog on the left.

## Problem Statement
The `ProductCatalogMini` component calls `.map()` on `products` state (line 205) and `categories` state (line 168), but these arrays can become `undefined` if the API call to fetch products or categories fails or returns an unexpected response shape. When the API request in `fetchProducts` (line 57) or `fetchCategories` (line 84) throws an error, the catch block logs the error but does not reset `products`/`categories` to a safe empty array. If `response.items` is `undefined` (malformed response), the state gets set to `undefined`, and the subsequent `.map()` call crashes the entire component tree.

Additionally, `response.pagination` at line 68 can also be `undefined`, causing `pageNum < response.pagination.pages` to throw.

## Solution Statement
Add null safety guards in `ProductCatalogMini.tsx` to ensure that:
1. `response.items` defaults to `[]` when setting products state (lines 64-66)
2. `response.items` defaults to `[]` when setting categories state (line 85)
3. `response.pagination` is safely accessed with optional chaining (line 68)

This follows the defensive pattern already used in other parts of the codebase, such as `PortfolioBuilderPage.tsx` line 80 (`response.items || []`) and `usePortfolios.ts` which uses `response.items || []`.

## Steps to Reproduce
1. Open the application and log in
2. Navigate to the Portfolios page (`/portfolios`)
3. Click the "Create Portfolio" button
4. Observe the page goes blank/white
5. Open browser console and see: `Uncaught TypeError: Cannot read properties of undefined (reading 'map')`

## Root Cause Analysis
The root cause is in `apps/Client/src/components/kompass/ProductCatalogMini.tsx`. When the `PortfolioBuilderPage` mounts for a new portfolio (`/portfolios/new`), it renders the `ProductCatalogMini` component which immediately fetches products and categories via API calls.

If either API call fails (network error, server error, auth error, or if the response doesn't contain `items`), the error is caught and logged, but the state is never reset. The products state initialized as `[]` on line 45 would remain safe. However, if the response succeeds but `response.items` is `undefined` (e.g., the API returns `{}` or the response shape changes), then:

- Line 64: `setProducts(prev => [...prev, ...response.items])` — spreading `undefined` throws
- Line 66: `setProducts(response.items)` — sets state to `undefined`
- Line 85: `setCategories(response.items)` — sets state to `undefined`

Subsequently:
- Line 168: `categories.map(...)` crashes with "Cannot read properties of undefined (reading 'map')"
- Line 205: `products.map(...)` crashes with "Cannot read properties of undefined (reading 'map')"

Line 68 is also unsafe: `response.pagination.pages` will throw if `response.pagination` is `undefined`.

## Relevant Files
Use these files to fix the bug:

- `apps/Client/src/components/kompass/ProductCatalogMini.tsx` — The component containing the bug. Lines 64-66 (products fetch without null safety), line 68 (pagination access without null safety), and line 85 (categories fetch without null safety) need defensive defaults.
- `apps/Client/src/pages/kompass/PortfolioBuilderPage.tsx` — The parent page that renders `ProductCatalogMini`. Contains the correct pattern at line 80: `response.items || []`. Useful as reference for the fix pattern.
- `apps/Client/src/hooks/kompass/usePortfolioBuilder.ts` — Hook used by the page. No changes needed, but useful for understanding the data flow.
- Read `.claude/commands/e2e/test_portfolio_builder.md` and `.claude/commands/test_e2e.md` to understand how to create an E2E test file for validating this fix.

### New Files
- `.claude/commands/e2e/test_new_portfolio_map_error.md` — New E2E test file to validate that creating a new portfolio no longer crashes.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Add null safety to product fetching in ProductCatalogMini
- Open `apps/Client/src/components/kompass/ProductCatalogMini.tsx`
- On line 64, change `setProducts(prev => [...prev, ...response.items]);` to `setProducts(prev => [...prev, ...(response.items || [])]);`
- On line 66, change `setProducts(response.items);` to `setProducts(response.items || []);`
- On line 68, change `setHasMore(pageNum < response.pagination.pages);` to `setHasMore(pageNum < (response.pagination?.pages ?? 0));`

### Step 2: Add null safety to category fetching in ProductCatalogMini
- In the same file `apps/Client/src/components/kompass/ProductCatalogMini.tsx`
- On line 85, change `setCategories(response.items);` to `setCategories(response.items || []);`

### Step 3: Create E2E test file for new portfolio creation
- Read `.claude/commands/e2e/test_portfolio_builder.md` and `.claude/commands/test_e2e.md` to understand E2E test format
- Create a new E2E test file at `.claude/commands/e2e/test_new_portfolio_map_error.md` that validates:
  1. Navigate to Portfolios page
  2. Click "Create Portfolio" button
  3. Verify the Portfolio Builder page loads without errors (no white screen)
  4. Verify the two-column layout is visible (product catalog on left, portfolio builder on right)
  5. Verify the product catalog search input is visible and functional
  6. Verify the empty portfolio state message is shown on the right panel
  7. Take screenshots to prove the page renders correctly

### Step 4: Run validation commands
- Run all validation commands listed below to confirm the fix works and introduces zero regressions

## Validation Commands
Execute every command to validate the bug is fixed with zero regressions.

- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate no TypeScript errors were introduced
- `cd apps/Client && npm run build` — Run Client build to validate the fix compiles correctly and the production bundle is generated without errors
- Read `.claude/commands/test_e2e.md`, then read and execute the new E2E test `.claude/commands/e2e/test_new_portfolio_map_error.md` to validate this functionality works

## Notes
- The fix follows the exact same defensive pattern already used in `PortfolioBuilderPage.tsx:80` (`response.items || []`), ensuring consistency across the codebase.
- Only 3 lines of code need to change in a single file (`ProductCatalogMini.tsx`), making this a minimal and surgical fix.
- No new libraries or dependencies are required.
- The backend always returns `items` as an array in its response DTOs, but the frontend should be defensive against malformed or unexpected responses (network issues, proxy errors, etc.).
