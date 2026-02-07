# Bug Fix: Mixed Content HTTPS Error on Users Administration Module

**ADW ID:** fcc6b612
**Date:** 2026-02-07
**Specification:** specs/issue-110-adw-fcc6b612-sdlc_planner-fix-mixed-content-https.md

## Overview

Fixed a browser Mixed Content security error that blocked all API requests when the frontend (served over HTTPS on Vercel) made requests to the backend using HTTP instead of HTTPS. The fix adds automatic protocol upgrade logic in the API client so HTTP URLs are converted to HTTPS when the page is served over HTTPS, while preserving HTTP for local development.

## What Was Built

- Automatic HTTP-to-HTTPS protocol upgrade in the central API client
- Same protocol upgrade fix in the SupplierCertificationTab PDF download URL
- Updated `.env.sample` with production HTTPS documentation
- New E2E test for the Users Administration page

## Technical Implementation

### Files Modified

- `apps/Client/src/api/clients/index.ts`: Added protocol upgrade logic that checks `window.location.protocol` and upgrades `http://` to `https://` in the API base URL when the page is served over HTTPS
- `apps/Client/src/components/kompass/SupplierCertificationTab.tsx`: Applied the same protocol upgrade logic to the direct `VITE_API_URL` usage for PDF download URLs
- `.env.sample`: Added comment noting HTTPS requirement for production deployments
- `.claude/commands/e2e/test_users_admin_page.md`: New E2E test validating the Users page loads without mixed content errors
- `playwright-mcp-config.json`: Updated video recording directory to match worktree

### Key Changes

- The API client now auto-detects when the page is served over HTTPS and upgrades any `http://` API URL to `https://`, preventing mixed content blocking by browsers
- The fix is resilient to environment variable misconfiguration -- even if `VITE_API_URL` is set with `http://`, the runtime fix ensures HTTPS is used in production
- Local development on `http://localhost` is unaffected since the upgrade only triggers when `window.location.protocol === 'https:'`
- The SupplierCertificationTab, which constructs PDF download URLs directly from `VITE_API_URL`, also received the same fix to prevent mixed content on audit PDF downloads

## How to Use

1. No action required -- the fix is automatic at runtime
2. For new deployments, set `VITE_API_URL` with `https://` in Vercel environment variables (recommended)
3. Even if `VITE_API_URL` is accidentally set with `http://`, the runtime fix will upgrade it to `https://` when the page is served over HTTPS

## Configuration

- `VITE_API_URL`: Should use `https://` for production deployments. The runtime fix handles `http://` gracefully, but using `https://` directly is recommended.

## Testing

- Run TypeScript check: `cd apps/Client && npx tsc --noEmit`
- Run production build: `cd apps/Client && npm run build`
- Run ESLint: `cd apps/Client && npm run lint`
- Run E2E test: Execute `.claude/commands/e2e/test_users_admin_page.md`

## Notes

- Render provides HTTPS by default for all services, so no backend changes were needed
- The fix is purely frontend -- a runtime safeguard added to the API client initialization
- This prevents the entire class of mixed content bugs, not just the Users page
