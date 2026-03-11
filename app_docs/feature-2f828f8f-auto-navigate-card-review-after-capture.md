# Auto-Navigate to Card Review After Capture

**ADW ID:** 2f828f8f
**Date:** 2026-03-10
**Specification:** specs/issue-169-adw-2f828f8f-sdlc_planner-auto-navigate-card-review-after-capture.md

## Overview

After uploading a business card on CardCapturePage, the app now automatically navigates to CardReviewPage once AI extraction completes. This eliminates manual navigation, improving speed at trade fairs. The newly captured card row is highlighted with a pulse animation so users can immediately identify it.

## What Was Built

- Post-upload extraction phase indicator ("Extrayendo datos de la tarjeta...")
- Polling logic that checks extraction status every 2 seconds (30-second timeout)
- Automatic navigation to CardReviewPage upon successful extraction
- Pulse-highlight animation on the newly captured card row in CardReviewPage
- Timeout fallback UI with manual link to the review page
- Error handling for failed extractions

## Technical Implementation

### Files Modified

- `apps/Client/src/pages/kompass/CardCapturePage.tsx`: Added `useNavigate`, extraction phase state (`extractionPhase`, `extractionTimeout`, `lastCaptureId`), polling `useEffect` with interval/timeout logic, extraction phase UI (indeterminate `LinearProgress`), and timeout `Alert` with link to review page.
- `apps/Client/src/pages/kompass/CardReviewPage.tsx`: Added `useLocation` to read `highlightCaptureId` from navigation state, scroll-to-row logic, `@keyframes highlightPulse` CSS animation on matching `TableRow`, auto-clear after 3 seconds, and `data-capture-id` attributes on rows.
- `.claude/commands/e2e/test_auto_navigate_card_review.md`: New E2E test specification for validating the auto-navigation and highlight flow.

### Key Changes

- **State machine on upload**: After upload, the handler checks capture status — `extracted` navigates immediately, `processing`/`pending` starts polling, `failed` shows an error.
- **Polling with cleanup**: A `useEffect` runs a `setInterval` polling `businessCardService.getCapture(id)` every 2 seconds. Uses `useRef` for interval ID and a `cancelledRef` flag to prevent stale navigation on unmount.
- **Timeout handling**: After 30 seconds without resolution, polling stops and a timeout alert appears with a manual link to `/card-review`.
- **Row highlighting**: CardReviewPage reads `location.state.highlightCaptureId`, scrolls the matching row into view, and applies a 3-second CSS pulse animation (`rgba(25, 118, 210, 0.15)` → transparent). History state is cleared via `window.history.replaceState` to prevent re-highlighting on refresh.
- **Navigation paths**: Routes use `/card-review` path (relative to Kompass routing context).

## How to Use

1. Navigate to the **Card Capture** page
2. Upload a business card photo
3. An indeterminate progress bar appears with "Extrayendo datos de la tarjeta..."
4. Once extraction completes, you are automatically redirected to the **Card Review** page
5. The newly captured card row pulses with a blue highlight for 3 seconds
6. If extraction times out (30s), a message appears with a manual link to the review page

## Configuration

No new environment variables or configuration required. Polling interval (2s) and timeout (30s) are defined as constants in `CardCapturePage.tsx` (`POLL_INTERVAL_MS`, `POLL_TIMEOUT_MS`).

## Testing

- Run `cd apps/Client && npx tsc --noEmit` for TypeScript validation
- Run `cd apps/Client && npm run lint` for ESLint checks
- Run `cd apps/Client && npm run build` for production build verification
- E2E test: `.claude/commands/e2e/test_auto_navigate_card_review.md`

## Notes

- No backend changes required — uses existing `businessCardService.getCapture(id)` endpoint for polling
- No new dependencies added
- All UI text is in Spanish (Colombian)
- The highlight animation uses MUI `sx` prop with inline `@keyframes` — no external animation library
