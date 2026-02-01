# Patch: Fix extraction service API endpoint URLs

## Metadata
adw_id: `d5237c66`
review_change_request: `Issue #1: API endpoint URL mismatch: Frontend extractionService uses '/extraction/upload', '/extraction/{jobId}', '/extraction/{jobId}/results', '/extraction/{jobId}/confirm' but backend routes are registered at '/api/extract/upload', '/api/extract/{job_id}', etc. (main.py:78 shows 'prefix="/api/extract"') Resolution: Change the frontend extractionService in kompassService.ts to use '/extract/' instead of '/extraction/' for all endpoints (lines 767, 777, 783, 790) Severity: blocker`

## Issue Summary
**Original Spec:** N/A
**Issue:** Frontend extractionService uses incorrect API path prefix `/extraction/` instead of `/extract/` which causes all extraction API calls to fail (404 errors)
**Solution:** Update all four extractionService endpoint paths in kompassService.ts from `/extraction/` to `/extract/`

## Files to Modify
Use these files to implement the patch:

- `apps/Client/src/services/kompassService.ts` - Lines 767, 777, 783, 790

## Implementation Steps
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Update extractionService endpoint URLs in kompassService.ts
- Change line 767: `/extraction/upload` → `/extract/upload`
- Change line 777: `/extraction/${jobId}` → `/extract/${jobId}`
- Change line 783: `/extraction/${jobId}/results` → `/extract/${jobId}/results`
- Change line 790: `/extraction/${request.job_id}/confirm` → `/extract/${request.job_id}/confirm`

## Validation
Execute every command to validate the patch is complete with zero regressions.

1. `cd apps/Client && npm run typecheck` - Verify TypeScript compilation passes
2. `cd apps/Client && npm run lint` - Verify no linting errors
3. `cd apps/Client && npm run build` - Verify production build succeeds
4. `cd apps/Server && .venv/bin/ruff check .` - Verify backend linting (no changes expected)
5. `cd apps/Server && .venv/bin/pytest tests/ -v --tb=short` - Verify backend tests pass (no changes expected)

## Patch Scope
**Lines of code to change:** 4
**Risk level:** low
**Testing required:** Frontend build verification, manual testing of import wizard flow
