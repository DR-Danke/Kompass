# Feature: Auto-navigate to Card Review After Capture

## Metadata
issue_number: `169`
adw_id: `2f828f8f`
issue_json: ``

## Feature Description
After a user captures and uploads a business card photo on the CardCapturePage, the app currently requires manual navigation to the CardReviewPage to review extracted data. This feature adds automatic redirection to the review page after a successful upload and extraction, with a loading indicator during processing. On the review page, the newly captured card is highlighted so the user can immediately identify it.

## User Story
As a sourcing agent at a trade fair
I want to be automatically taken to the review page after uploading a business card
So that I can immediately review and confirm the extracted supplier data without extra navigation steps

## Problem Statement
Currently after uploading a business card on CardCapturePage, the user sees a success message but must manually navigate to CardReviewPage. This creates unnecessary friction — especially at trade fairs where speed matters. The user may forget to review cards, or waste time navigating.

## Solution Statement
1. After a successful upload on CardCapturePage, show an "Extrayendo datos..." phase indicator, then auto-navigate to CardReviewPage with the capture ID in navigation state.
2. If extraction returns `processing` status, poll the capture endpoint every 2 seconds (with 30-second timeout) until status becomes `extracted` or `failed`.
3. On CardReviewPage, read the highlight state from navigation, scroll to and pulse-highlight the newly captured row.
4. Handle edge cases: extraction failure stays on capture page with error, timeout shows manual link, user navigating away cancels polling.

## Relevant Files
Use these files to implement the feature:

- **`apps/Client/src/pages/kompass/CardCapturePage.tsx`** — Main file to modify. Add post-upload extraction phase indicator, polling logic, and auto-navigation to review page after extraction completes.
- **`apps/Client/src/pages/kompass/CardReviewPage.tsx`** — Add highlight-on-navigate behavior: read `highlightCaptureId` from `location.state`, scroll to matching row, apply pulse animation, clear after timeout.
- **`apps/Client/src/services/kompassService.ts`** — Reference only. The `businessCardService.getCapture(id)` method (line 1287) already exists for polling. The `uploadCard()` method (line 1216) handles upload. No changes needed.
- **`apps/Client/src/types/kompass.ts`** — Reference only. `BusinessCardCapture` and `BusinessCardCaptureStatus` types already defined (lines 1052-1085). No changes needed.
- **`apps/Client/src/hooks/kompass/useCardReview.ts`** — Reference only. The review page hook that fetches captures. No changes needed.
- **`.claude/commands/test_e2e.md`** — Read to understand E2E test execution format.
- **`.claude/commands/e2e/test_card_capture_page.md`** — Read as reference for E2E test format and card capture page testing patterns.
- **`ai_docs/KOMPASS_MODULE_GUIDE.md`** — Reference for Kompass module business logic context.

### New Files
- **`.claude/commands/e2e/test_auto_navigate_card_review.md`** — E2E test validating auto-navigation from capture to review page with row highlighting.

## Implementation Plan
### Phase 1: Foundation
Add the extraction phase indicator and polling logic to CardCapturePage. This is the core state machine: upload → extracting → navigate (or error/timeout).

### Phase 2: Core Implementation
Modify the CardCapturePage upload handler to:
1. After upload completes, show "Extrayendo datos..." phase indicator
2. Check capture status — if `extracted`, navigate immediately
3. If `processing`, poll `businessCardService.getCapture(id)` every 2 seconds
4. On `extracted` → navigate to `/kompass/card-review` with `highlightCaptureId` state
5. On `failed` → show error, stay on page
6. On timeout (30s) → show timeout message with manual link

### Phase 3: Integration
Modify CardReviewPage to:
1. Read `location.state?.highlightCaptureId`
2. After captures load, find the matching row and scroll into view
3. Apply a CSS pulse animation (brief background color highlight)
4. Clear highlight state after 3 seconds

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Task 1: Create E2E Test Specification
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_card_capture_page.md` to understand the E2E test format
- Create `.claude/commands/e2e/test_auto_navigate_card_review.md` with test steps:
  1. Navigate to CardCapturePage
  2. Upload a test business card image
  3. Verify extraction phase indicator ("Extrayendo datos de la tarjeta...") appears
  4. Verify automatic navigation to CardReviewPage occurs
  5. Verify the newly captured card row is highlighted (pulse animation)
  6. Verify highlight clears after a few seconds
  7. Test error case: verify user stays on CardCapturePage when extraction fails

### Task 2: Add Post-Upload Navigation Logic to CardCapturePage
- File: `apps/Client/src/pages/kompass/CardCapturePage.tsx`
- Import `useNavigate` from `react-router-dom`
- Import `Link` from `react-router-dom` (for timeout manual link)
- Add new state variables:
  - `extractionPhase: boolean` — whether showing the extraction loading phase
  - `extractionTimeout: boolean` — whether extraction timed out
  - `lastCaptureId: string | null` — ID of the last uploaded capture for polling
- Modify `handleFileChange` success path (after line 170):
  - After upload succeeds and capture is returned:
    - If `capture.status === 'extracted'`: navigate immediately to `/kompass/card-review` with `{ state: { highlightCaptureId: capture.id } }`
    - If `capture.status === 'processing'` or `capture.status === 'pending'`: set `extractionPhase = true`, `lastCaptureId = capture.id`, and start polling
    - If `capture.status === 'failed'`: show error message, stay on page
- Add polling logic using `useEffect` that activates when `extractionPhase` is true and `lastCaptureId` is set:
  - Poll `businessCardService.getCapture(lastCaptureId)` every 2 seconds
  - On `extracted`: clear polling, navigate to review page with `highlightCaptureId`
  - On `failed`: clear polling, set error message, set `extractionPhase = false`
  - Track elapsed time; after 30 seconds: clear polling, set `extractionTimeout = true`, set `extractionPhase = false`
  - Use `useRef` for the interval ID and a mounted/cancelled flag to handle cleanup on unmount or user navigation away
  - Clean up interval on unmount via useEffect cleanup function

### Task 3: Add Extraction Phase UI to CardCapturePage
- File: `apps/Client/src/pages/kompass/CardCapturePage.tsx`
- Below the existing upload progress bar (after line 328), add a new extraction phase indicator:
  - Show when `extractionPhase` is true
  - Display a `LinearProgress` (indeterminate) with text "Extrayendo datos de la tarjeta..."
  - Style similar to upload progress section
- Add timeout state UI:
  - Show when `extractionTimeout` is true
  - Display an `Alert` with severity "info" containing:
    - Message: "La extracción está tomando más tiempo de lo esperado. Puedes revisar el resultado en la página de revisión."
    - A `Link` (react-router-dom) to `/kompass/card-review` styled as a button

### Task 4: Add Highlight-on-Navigate to CardReviewPage
- File: `apps/Client/src/pages/kompass/CardReviewPage.tsx`
- Import `useLocation` from `react-router-dom`
- Import `useEffect`, `useRef` from React
- Read `location.state?.highlightCaptureId` as `string | undefined`
- Add a `highlightId` state (initialized from location state) and a ref for the highlighted row
- After captures are loaded (when `!isLoading && captures.length > 0`), if `highlightId` is set:
  - Use a `useEffect` to find the table row with the matching capture ID
  - Use `scrollIntoView({ behavior: 'smooth', block: 'center' })` to scroll to it
  - Apply a CSS keyframe animation for a pulse effect (e.g., background transitioning from `rgba(25, 118, 210, 0.15)` to transparent over 3 seconds)
  - After 3 seconds, clear the `highlightId` state
- Add a `data-capture-id` attribute to each `TableRow` so the row can be found programmatically
- Add a `@keyframes` pulse animation using MUI's `sx` prop or inline `<style>`:
  ```
  @keyframes highlightPulse {
    0% { background-color: rgba(25, 118, 210, 0.15); }
    100% { background-color: transparent; }
  }
  ```
- Apply the animation to the row when `capture.id === highlightId`:
  ```tsx
  sx={{ animation: capture.id === highlightId ? 'highlightPulse 3s ease-out' : undefined }}
  ```
- Clear the window history state after reading to prevent re-highlighting on page refresh:
  ```tsx
  window.history.replaceState({}, document.title);
  ```

### Task 5: Validate with Static Analysis
- Run `cd apps/Client && npm run typecheck` to ensure no TypeScript errors
- Run `cd apps/Client && npm run lint` to ensure no ESLint errors
- Run `cd apps/Client && npm run build` to ensure the build succeeds

### Task 6: Run E2E Test
- Read `.claude/commands/test_e2e.md`, then read and execute the new `.claude/commands/e2e/test_auto_navigate_card_review.md` E2E test to validate the feature works end-to-end

### Task 7: Final Validation
- Run all validation commands listed below to confirm zero regressions

## Testing Strategy
### Unit Tests
- No separate unit test files needed — the feature is UI-only with no new business logic functions. Validation is handled by TypeScript type checking, lint, build, and E2E tests.

### Edge Cases
- **Immediate extraction**: Upload returns `extracted` status — navigate immediately without polling
- **Async extraction**: Upload returns `processing` — poll until `extracted` or `failed`
- **Extraction failure**: Upload returns `failed` — show error, stay on page
- **Timeout**: 30 seconds elapse without resolution — show timeout message with manual link
- **User navigates away during polling**: Cleanup interval on unmount to prevent memory leaks or stale navigation
- **Page refresh on review page**: Don't re-highlight (state is cleared from history)
- **Multiple rapid uploads**: Only track the last upload's capture ID for navigation
- **Highlight target not in current filter**: The review page loads all captures by default (no filter), so the highlight target should be visible

## Acceptance Criteria
- After successful upload + extraction, user is automatically navigated to CardReviewPage within 5 seconds
- During extraction processing, a loading indicator with "Extrayendo datos de la tarjeta..." is shown
- The newly captured card row on the review page has a brief visual highlight (pulse animation)
- The highlight auto-clears after ~3 seconds
- If extraction fails, user stays on CardCapturePage with error message "Error al extraer datos. Por favor, intenta de nuevo."
- If extraction times out (30s), a timeout message is shown with a manual link to the review page
- Navigation does not break if user manually navigates away during extraction polling
- No TypeScript, ESLint, or build errors
- All existing tests continue to pass
- UI text is in Spanish (Colombian)

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate no TypeScript errors
- `cd apps/Client && npm run lint` — Run Client ESLint to validate no lint errors
- `cd apps/Client && npm run build` — Run Client production build to validate no build errors
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_auto_navigate_card_review.md` — E2E test validating auto-navigation and highlighting

## Notes
- The `businessCardService.getCapture(id)` method already exists (kompassService.ts:1287) and is used for polling — no backend changes needed.
- The upload endpoint implicitly uses `auto_extract=true`, so extraction is triggered server-side on upload.
- The polling interval (2s) and timeout (30s) are chosen to balance responsiveness with server load.
- `useNavigate` from react-router-dom is already available in the project (React Router 6).
- The highlight pulse animation uses CSS `@keyframes` via MUI's sx prop for simplicity — no external animation library needed.
- No new dependencies are required.
