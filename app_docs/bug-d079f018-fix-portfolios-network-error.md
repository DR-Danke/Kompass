# Bug Fix: Portfolios Module Network Error

**ADW ID:** d079f018
**Date:** 2026-02-08
**Specification:** specs/issue-115-adw-d079f018-sdlc_planner-fix-portfolios-network-error.md

## Overview

Fixed network errors that occurred when navigating to the Portfolios page. The root cause was a trailing slash mismatch between frontend API calls and backend route definitions, causing FastAPI 307 redirects that fail in cross-origin deployments due to missing CORS headers on the redirect response.

## What Was Built

- Fixed `nicheService.list()` and `nicheService.create()` API paths to include trailing slashes
- Fixed `portfolioService.list()` and `portfolioService.create()` API paths to include trailing slashes
- Created E2E test command for validating the portfolios network error fix

## Technical Implementation

### Files Modified

- `apps/Client/src/services/kompassService.ts`: Added trailing slashes to 4 API endpoint paths (`/niches` → `/niches/` and `/portfolios` → `/portfolios/`) in the `list()` and `create()` methods of `nicheService` and `portfolioService`
- `.claude/commands/e2e/test_portfolios_network_error_fix.md`: New E2E test command to validate the Portfolios page loads without network errors

### Key Changes

- `nicheService.list()` (line 169): Changed `'/niches'` to `'/niches/'` to match backend `@router.get("/")`
- `nicheService.create()` (line 183): Changed `'/niches'` to `'/niches/'` to match backend `@router.post("/")`
- `portfolioService.list()` (line 493): Changed `'/portfolios'` to `'/portfolios/'` to avoid FastAPI `redirect_slashes=True` 307 redirect
- `portfolioService.create()` (line 507): Changed `'/portfolios'` to `'/portfolios/'` to avoid FastAPI 307 redirect
- Methods using path parameters (e.g., `/portfolios/${id}`, `/niches/${id}`) were intentionally left unchanged as they resolve correctly without trailing slashes

## How to Use

1. Navigate to the Portfolios page via the sidebar navigation
2. The page should load successfully without network errors in the console
3. The niche filter dropdown should populate with available niches
4. Portfolio cards or an empty state message should display correctly

## Configuration

No configuration changes required. This fix only modifies frontend API call paths.

## Testing

- Run TypeScript type check: `cd apps/Client && npx tsc --noEmit`
- Run production build: `cd apps/Client && npm run build`
- Run E2E test: Execute `/e2e:test_portfolios_network_error_fix` to validate the page loads without network errors
- Manually verify: Navigate to the Portfolios page in a cross-origin deployment and confirm no `Network Error` messages appear in the browser console

## Notes

- This is the same class of bug previously fixed in PR #112 (users endpoints) and issue #113 (categories/tags endpoints)
- The trailing slash mismatch causes FastAPI's `redirect_slashes=True` default to issue 307 redirects, which lack CORS headers in cross-origin deployments (Vercel frontend + Render backend)
- Other services may have similar trailing slash issues but are out of scope for this fix
