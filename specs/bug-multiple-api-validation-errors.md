# Bug: Multiple API Validation Errors (422) and Undefined Property Crashes

## Metadata
issue_number: ``
adw_id: ``
issue_json: ``

## Bug Description
After navigating through the application, multiple 422 (Unprocessable Entity) errors occur on various API endpoints:
1. `/api/categories/tree` - 422 error (endpoint still being called despite previous fix - browser caching issue)
2. `/api/pricing/hs-codes?page=1&limit=1000` - 422 error due to limit exceeding backend max of 100
3. `/api/pricing/freight-rates?page=1&limit=1000` - 422 error due to limit exceeding backend max of 100
4. NichesPage crashes with `TypeError: Cannot read properties of undefined (reading 'length')` on line 53
5. Autocomplete crashes with `Cannot read properties of undefined (reading 'length')` in MUI

## Problem Statement
1. **Stale Cache**: Browser is caching old JavaScript that still calls `/categories/tree` instead of `/categories`
2. **Limit Mismatch**: Frontend PricingConfigPage calls with `limit=1000` but backend validates `le=100` (max 100)
3. **Missing Null Checks**: Response data `items` property is assumed to exist but may be undefined
4. **Fragile State**: When API calls fail, state becomes undefined instead of defaulting to safe empty arrays

## Solution Statement
1. Fix the PricingConfigPage to use `limit=100` (or use pagination properly)
2. Add defensive null checks in NichesPage for `response.items`
3. Ensure all list responses default to empty arrays when undefined
4. The browser cache issue will be resolved once the user hard-refreshes or clears cache

## Steps to Reproduce
1. Start the application (backend and frontend)
2. Log in and navigate to various pages
3. Navigate to Pricing Config page - see 422 errors on hs-codes and freight-rates
4. Navigate to Niches page - see TypeError about undefined.length
5. Check browser console for multiple 422 errors

## Root Cause Analysis
1. **Limit Validation**: Backend `pricing_routes.py` defines:
   - `limit: int = Query(20, ge=1, le=100, ...)` - max 100 items per page
   - Frontend calls with `limit=1000` which FastAPI rejects with 422

2. **Missing Response Validation**: Pages assume `response.items` exists:
   - `NichesPage.tsx:53` - `response.items.length` crashes when items is undefined

3. **Cache Issue**: Browser has cached old kompassService.ts that calls `/categories/tree`
   - Error shows `kompassService.ts:142` for categories which maps to old file
   - Current file shows `kompassService.ts:287` for categories

## Relevant Files
Use these files to fix the bug:

- `apps/Client/src/pages/kompass/PricingConfigPage.tsx` - Calls `pricingService.listHsCodes(1, 1000)` and `pricingService.listFreightRates(1, 1000)` with invalid limit. Change to use valid limit (100 or paginated approach).

- `apps/Client/src/pages/kompass/NichesPage.tsx` - Line 53 accesses `response.items.length` without null check. Add defensive check for undefined items.

- `apps/Server/app/api/pricing_routes.py` - Backend routes file for reference. Shows `le=100` constraint on limit parameter.

- `apps/Client/src/types/kompass.ts` - May need to check ListResponse types to ensure items is properly typed.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Fix PricingConfigPage Limit Values
- Open `apps/Client/src/pages/kompass/PricingConfigPage.tsx`
- Locate line 92: `const response = await pricingService.listHsCodes(1, 1000);`
- Change to: `const response = await pricingService.listHsCodes(1, 100);`
- Locate line 110: `const response = await pricingService.listFreightRates(1, 1000);`
- Change to: `const response = await pricingService.listFreightRates(1, 100);`
- Note: If more than 100 items are needed, implement proper pagination in the future

### Step 2: Add Null Check to NichesPage
- Open `apps/Client/src/pages/kompass/NichesPage.tsx`
- Locate line 52-53 where `response.items` is accessed:
  ```typescript
  setNiches(response.items as NicheWithClientCount[]);
  console.log(`INFO [NichesPage]: Fetched ${response.items.length} niches`);
  ```
- Add defensive null checks:
  ```typescript
  const items = response.items || [];
  setNiches(items as NicheWithClientCount[]);
  console.log(`INFO [NichesPage]: Fetched ${items.length} niches`);
  ```

### Step 3: Add Defensive Checks to Other List Fetches
- Review any other pages that access `response.items` without null checks
- Add `|| []` fallback where appropriate to prevent crashes

### Step 4: Run Validation Commands
- Execute all validation commands to ensure the bug is fixed with zero regressions

## Validation Commands
Execute every command to validate the bug is fixed with zero regressions.

- `cd /mnt/c/Users/user/danke_apps/Kompass/apps/Client && npm run typecheck` - Run Client type check
- `cd /mnt/c/Users/user/danke_apps/Kompass/apps/Client && npm run build` - Run Client build
- `cd /mnt/c/Users/user/danke_apps/Kompass/apps/Server && source .venv/bin/activate && python -m pytest tests/ -v --tb=short` - Run Server tests

## Notes
- The backend limit validation is intentional - 100 items per page is a reasonable max
- If more items are needed, proper pagination should be implemented in the future
- After deployment, users may need to hard-refresh (Ctrl+Shift+R) to clear cached JavaScript
- The browser caching issue shows calls from `kompassService.ts:142` (old) vs `kompassService.ts:286` (new) - the line numbers confirm mixed versions are running
- Consider adding proper pagination UI to PricingConfigPage if HS codes or freight rates exceed 100 items
