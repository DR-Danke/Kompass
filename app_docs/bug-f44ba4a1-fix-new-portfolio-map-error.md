# Bug Fix: New Portfolio Map Error

**ADW ID:** f44ba4a1
**Date:** 2026-02-08
**Specification:** specs/issue-119-adw-f44ba4a1-sdlc_planner-fix-new-portfolio-map-error.md

## Overview

Fixed a crash that occurred when creating a new portfolio. The `ProductCatalogMini` component threw `TypeError: Cannot read properties of undefined (reading 'map')` because API responses with missing `items` or `pagination` fields were not handled defensively, causing the component to set state to `undefined` and crash on subsequent `.map()` calls.

## What Was Built

- Null safety guards for product fetching in `ProductCatalogMini`
- Null safety guards for category fetching in `ProductCatalogMini`
- Optional chaining for pagination access in `ProductCatalogMini`
- E2E test specification for validating new portfolio creation

## Technical Implementation

### Files Modified

- `apps/Client/src/components/kompass/ProductCatalogMini.tsx`: Added `|| []` defaults for `response.items` in product and category fetching, and optional chaining (`?.`) with nullish coalescing (`?? 0`) for `response.pagination.pages`
- `.claude/commands/e2e/test_new_portfolio_map_error.md`: New E2E test spec validating that the Portfolio Builder page loads correctly when creating a new portfolio

### Key Changes

- **Line 64**: `setProducts(prev => [...prev, ...response.items])` changed to `setProducts(prev => [...prev, ...(response.items || [])])` — prevents spreading `undefined` when appending paginated results
- **Line 66**: `setProducts(response.items)` changed to `setProducts(response.items || [])` — prevents setting products state to `undefined` on initial fetch
- **Line 68**: `response.pagination.pages` changed to `response.pagination?.pages ?? 0` — prevents crash when pagination object is missing from response
- **Line 85**: `setCategories(response.items)` changed to `setCategories(response.items || [])` — prevents setting categories state to `undefined`

## How to Use

1. Navigate to the Portfolios page (`/portfolios`)
2. Click the "Create Portfolio" button
3. The Portfolio Builder page loads with a two-column layout:
   - Left panel: Product catalog with search and category filter
   - Right panel: Empty portfolio builder ready for items
4. The page no longer crashes with a white screen if API responses are malformed or missing expected fields

## Configuration

No configuration changes required.

## Testing

- Run TypeScript check: `cd apps/Client && npx tsc --noEmit`
- Run production build: `cd apps/Client && npm run build`
- Run E2E test: Execute the test spec at `.claude/commands/e2e/test_new_portfolio_map_error.md`

## Notes

- The fix follows the same defensive pattern already used in `PortfolioBuilderPage.tsx` (`response.items || []`), maintaining codebase consistency
- Only 4 lines changed in a single file — minimal and surgical fix
- The backend DTOs always return `items` as an array, but the frontend should be defensive against network issues, proxy errors, or malformed responses
