# Bug Fix: Categories Module Network Error

**ADW ID:** 12b2f588
**Date:** 2026-02-08
**Specification:** specs/issue-113-adw-12b2f588-sdlc_planner-fix-categories-network-error.md

## Overview

Fixed a network error that occurred when navigating to the Categories & Tags management page. The error was caused by missing trailing slashes in frontend API calls, which triggered FastAPI 307 redirects that failed silently in cross-origin deployments due to missing CORS headers on redirect responses.

## What Was Built

- Added trailing slashes to `categoryService` API calls (`list`, `getTree`, `create`)
- Added trailing slashes to `tagService` API calls (`list`, `create`)
- Created an E2E test command to validate the fix

## Technical Implementation

### Files Modified

- `apps/Client/src/services/kompassService.ts`: Added trailing slashes to 5 API endpoint paths in `categoryService` and `tagService` to match backend route definitions
- `.claude/commands/e2e/test_categories_network_error_fix.md`: New E2E test file to validate the categories page loads without network errors

### Key Changes

- `categoryService.list()`: `/categories` → `/categories/`
- `categoryService.getTree()`: `/categories` → `/categories/`
- `categoryService.create()`: `/categories` → `/categories/`
- `tagService.list()`: `/tags` → `/tags/`
- `tagService.create()`: `/tags` → `/tags/`

### Root Cause

FastAPI's default `redirect_slashes=True` redirects requests from `/api/categories` to `/api/categories/` via HTTP 307. In cross-origin deployments (Vercel HTTPS frontend → Render HTTPS backend), the 307 redirect response lacks CORS headers, causing the browser to block the follow-up request. This results in an Axios error with no `response` object (undefined status) and message "Network Error".

This is the same class of bug previously fixed in PR #112 for the `/users` endpoints.

## How to Use

1. Navigate to the Categories & Tags page via the sidebar
2. The page should load successfully without any network error alerts
3. Categories tree and tags list should display correctly

## Configuration

No configuration changes required.

## Testing

- Run TypeScript type check: `cd apps/Client && npx tsc --noEmit`
- Run build: `cd apps/Client && npm run build`
- Run E2E test: Execute `/e2e:test_categories_network_error_fix` slash command

## Notes

- Methods using path parameters (e.g., `/categories/${id}`) were intentionally left unchanged as they resolve correctly without trailing slashes
- Other services (`nicheService`, `supplierService`, `productService`, etc.) may have the same trailing slash issue but are out of scope for this fix
- The `categoryService.move()` method has a separate bug where it sends `parent_id` instead of `new_parent_id` — this should be tracked as a follow-up issue
