# Patch: Fix card-review navigation paths in CardCapturePage

## Metadata
adw_id: `2f828f8f`
review_change_request: `Navigation paths use '/kompass/card-review' but the actual route is '/card-review'. This affects 3 locations in CardCapturePage.tsx: line 171 (polling success navigate), line 235 (immediate navigate after upload), and line 416 (timeout manual RouterLink). Navigating to '/kompass/card-review' renders a blank content area because no route matches that path in App.tsx. Resolution: Replace all 3 occurrences of '/kompass/card-review' with '/card-review' in CardCapturePage.tsx (lines 171, 235, and 416). Severity: blocker`

## Issue Summary
**Original Spec:** `specs/issue-169-adw-2f828f8f-sdlc_planner-auto-navigate-card-review-after-capture.md`
**Issue:** CardCapturePage navigates to `/kompass/card-review` which does not match any route in App.tsx. The actual route is `/card-review` (defined at `apps/Client/src/App.tsx:54`). This causes a blank page after card upload/extraction.
**Solution:** Replace all 3 occurrences of `/kompass/card-review` with `/card-review` in CardCapturePage.tsx.

## Files to Modify

- `apps/Client/src/pages/kompass/CardCapturePage.tsx` — Fix 3 navigation path strings (lines 171, 235, 416)

## Implementation Steps
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Fix navigation paths in CardCapturePage.tsx
- Line 171: Change `navigate('/kompass/card-review', { state: { highlightCaptureId: lastCaptureId } })` to `navigate('/card-review', { state: { highlightCaptureId: lastCaptureId } })`
- Line 235: Change `navigate('/kompass/card-review', { state: { highlightCaptureId: capture.id } })` to `navigate('/card-review', { state: { highlightCaptureId: capture.id } })`
- Line 416: Change `to="/kompass/card-review"` to `to="/card-review"`

### Step 2: Validate with static analysis and build
- Run TypeScript type check, ESLint, and production build to confirm no regressions

## Validation
Execute every command to validate the patch is complete with zero regressions.

- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate no TypeScript errors
- `cd apps/Client && npm run lint` — Run Client ESLint to validate no lint errors
- `cd apps/Client && npm run build` — Run Client production build to validate no build errors

## Patch Scope
**Lines of code to change:** 3
**Risk level:** low
**Testing required:** Static analysis (typecheck, lint, build) to confirm no regressions. E2E test for auto-navigate feature to confirm navigation works correctly.
