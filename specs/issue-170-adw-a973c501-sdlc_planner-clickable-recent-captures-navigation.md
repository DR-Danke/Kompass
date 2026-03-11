# Feature: Make Recent Captures Clickable on Capture Page

## Metadata
issue_number: `170`
adw_id: `a973c501`
issue_json: ``

## Feature Description
The "Recent Captures" section on the CardCapturePage displays captured business cards but they are not clickable. Users expect to click a recent capture to navigate to its review details on the CardReviewPage. This feature adds click handlers to each capture card, provides visual hover feedback (cursor pointer + elevated shadow), and navigates to the CardReviewPage with the capture ID passed via router state so the review page can highlight the relevant row. Action buttons (Extraer, Reintentar, Crear Proveedor) must continue to work independently without triggering the card-level navigation.

## User Story
As a Kompass sourcing agent at a trade fair
I want to click on a recent capture card to navigate directly to its review details
So that I can quickly review and confirm extracted supplier data without manually navigating to the review page

## Problem Statement
The recent captures list on CardCapturePage shows captured business cards with status, extracted fields, and action buttons, but clicking the card body does nothing. Users have no way to navigate from a specific capture to its review on CardReviewPage, breaking the discoverability of the review flow and adding unnecessary friction.

## Solution Statement
Add an `onClick` handler to each capture `<Card>` component that navigates to `/card-review` with `{ state: { highlightCaptureId: captureId } }`. Apply `cursor: pointer` and hover elevation styles to signal clickability. Use `event.stopPropagation()` on all existing action buttons to prevent their clicks from also triggering the card-level navigation.

## Relevant Files
Use these files to implement the feature:

- **`apps/Client/src/pages/kompass/CardCapturePage.tsx`** — The primary file to modify. Contains the recent captures list with `<Card>` components (line 447) that need click handlers, hover styles, and `stopPropagation` on action buttons (lines 531-574).
- **`apps/Client/src/pages/kompass/CardReviewPage.tsx`** — The navigation target. Already handles `highlightCaptureId` from `location.state` (line 178-179) with scroll-to and pulse animation. No changes needed, but useful for understanding the receiving end.
- **`apps/Client/src/App.tsx`** — Route definitions confirming `/card-review` path (line 54). No changes needed.
- **`apps/Client/src/types/kompass.ts`** — Type definitions for `BusinessCardCapture`. No changes needed.
- **`.claude/commands/test_e2e.md`** — Read to understand how to create and run E2E test files.
- **`.claude/commands/e2e/test_card_capture_page.md`** — Existing E2E test for the card capture page. Read for context on test patterns.
- **`.claude/commands/e2e/test_auto_navigate_card_review.md`** — Existing E2E test for auto-navigation. Read for context on highlight verification patterns.

### New Files
- **`.claude/commands/e2e/test_clickable_recent_captures.md`** — New E2E test file to validate clickable capture cards, hover feedback, and navigation with highlight.

## Implementation Plan
### Phase 1: Foundation
No foundational changes are needed. The navigation infrastructure (`useNavigate`, `location.state`, highlight logic on CardReviewPage) already exists. The routes are already configured.

### Phase 2: Core Implementation
Modify `CardCapturePage.tsx` to:
1. Add a `handleCaptureClick` function that navigates to `/card-review` with the capture ID in state
2. Add `onClick`, `cursor: pointer`, hover shadow, and transition styles to each `<Card>` component
3. Add `event.stopPropagation()` to all action button `onClick` handlers to prevent navigation when clicking buttons

### Phase 3: Integration
The CardReviewPage already supports `highlightCaptureId` in `location.state` — no integration changes needed. The feature leverages the existing highlight/scroll mechanism built for the auto-navigate feature (issue #169).

## Step by Step Tasks

### Task 1: Create E2E Test File
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_card_capture_page.md` to understand the E2E test format
- Create `.claude/commands/e2e/test_clickable_recent_captures.md` with the following test steps:
  1. Navigate to `/card-capture` page
  2. Verify recent captures list is visible with at least one capture card
  3. Hover over a capture card and verify visual feedback (cursor pointer, elevated shadow)
  4. Click on a capture card body (not action buttons)
  5. Verify navigation to `/card-review` page
  6. Verify "Revisión de Tarjetas" page title is visible
  7. Verify the clicked capture's row is highlighted with pulse animation
  8. Navigate back to `/card-capture`
  9. Verify action buttons still work without triggering navigation (click "Extraer" or similar button and verify the page does NOT navigate away)

### Task 2: Add Click Handler Function
- In `apps/Client/src/pages/kompass/CardCapturePage.tsx`, add a `handleCaptureClick` function inside the `CardCapturePage` component:
  ```typescript
  const handleCaptureClick = (captureId: string) => {
    navigate('/card-review', { state: { highlightCaptureId: captureId } });
  };
  ```

### Task 3: Add Click and Hover Styles to Capture Cards
- On the `<Card>` component at line 447, add the `onClick` handler and hover/cursor styles:
  ```typescript
  <Card
    key={capture.id}
    sx={{
      overflow: 'hidden',
      cursor: 'pointer',
      transition: 'box-shadow 0.2s ease-in-out',
      '&:hover': { boxShadow: 3 },
    }}
    onClick={() => handleCaptureClick(capture.id)}
  >
  ```

### Task 4: Add stopPropagation to Action Buttons
- Add `event.stopPropagation()` to each action button's `onClick` handler to prevent the card click from firing:
  - **Extraer button** (line 537): Change `onClick={() => handleExtract(capture.id)}` to `onClick={(e) => { e.stopPropagation(); handleExtract(capture.id); }}`
  - **Reintentar button** (line 549): Change `onClick={() => handleExtract(capture.id)}` to `onClick={(e) => { e.stopPropagation(); handleExtract(capture.id); }}`
  - **Crear Proveedor button** (line 560): Change `onClick={() => handleCreateSupplier(capture.id)}` to `onClick={(e) => { e.stopPropagation(); handleCreateSupplier(capture.id); }}`

### Task 5: Run Validation Commands
- Run all validation commands listed below to confirm the feature works with zero regressions

## Testing Strategy
### Unit Tests
No new unit tests needed — the change is purely UI interaction (click handler + styling). Validation is best done via E2E tests and type/build checks.

### Edge Cases
- Clicking action buttons (Extraer, Reintentar, Crear Proveedor) should NOT trigger navigation — validated via `stopPropagation`
- Clicking the "Proveedor vinculado" chip (read-only, no `onClick`) should trigger card navigation (expected behavior since it's informational)
- Cards in all statuses (pending, processing, extracted, confirmed, rejected, failed) should be clickable
- Supplier result alerts within the card should also trigger navigation when clicked (acceptable since they're informational)

## Acceptance Criteria
- Clicking a recent capture card navigates to `/card-review` with the capture ID in router state
- The CardReviewPage highlights and scrolls to the corresponding row
- Capture cards show `cursor: pointer` styling
- Capture cards show elevated shadow on hover
- Clicking "Extraer" button performs extraction without navigating
- Clicking "Reintentar" button performs retry extraction without navigating
- Clicking "Crear Proveedor" button creates supplier without navigating
- All UI text remains in Spanish (Colombian)
- No TypeScript errors, no build errors
- No regressions to existing card capture or card review functionality

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Client && npx tsc --noEmit` — Run TypeScript type check to ensure no type errors
- `cd apps/Client && npm run build` — Run production build to ensure no build errors
- `cd apps/Client && npm run lint` — Run ESLint to ensure no linting issues
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_clickable_recent_captures.md` to validate the clickable captures navigation works end-to-end

## Notes
- This feature leverages the existing `highlightCaptureId` mechanism on CardReviewPage (built in issue #169) — no changes needed on the review page
- The navigation uses React Router's `state` parameter, which does not modify the URL — this is consistent with how the auto-navigate feature works after upload
- No new dependencies or libraries are needed
- Only one file needs to be modified: `CardCapturePage.tsx`
