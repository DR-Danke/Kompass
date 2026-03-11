# Feature: Card Image Lightbox on Review Page

## Metadata
issue_number: `171`
adw_id: `2734e661`
issue_json: ``

## Feature Description
Add a full-size image lightbox/modal to the CardReviewPage so that users can click on a business card thumbnail to view the original photo at full resolution. This enables back-office team members to verify AI extraction accuracy by comparing extracted data against the original card image. The lightbox supports keyboard dismissal (Escape), backdrop click to close, and graceful handling of missing/broken images with placeholder icons.

## User Story
As a back-office team member reviewing business card captures
I want to click a card thumbnail to see the full-size original photo in a lightbox
So that I can verify the AI extraction accuracy against the actual business card before approving or rejecting

## Problem Statement
On the CardReviewPage, clicking the business card thumbnail does nothing. Users cannot view the original card image at full resolution, making it difficult to verify whether the AI correctly extracted company names, contacts, emails, and phone numbers. This is a P1 usability gap that undermines confidence in the extraction review workflow.

## Solution Statement
Add a MUI Dialog-based lightbox that opens when a user clicks a card thumbnail in the review table. The thumbnail will gain a cursor pointer, hover overlay with a zoom icon for visual affordance, and `event.stopPropagation()` to prevent row selection. Missing/broken images will show a `BrokenImage` placeholder icon and disable the lightbox click. The Dialog closes on Escape or backdrop click (built-in MUI behavior). All UI labels remain in Spanish (Colombian).

## Relevant Files
Use these files to implement the feature:

- `apps/Client/src/pages/kompass/CardReviewPage.tsx` — Main file to modify. Contains the review table with the thumbnail column (lines 408-418) that needs click-to-lightbox behavior, and will host the new Dialog lightbox component.
- `apps/Client/src/hooks/kompass/useCardReview.ts` — Hook providing `captures` state array; no modifications needed but reference for understanding data shape.
- `apps/Client/src/types/kompass.ts` — Type definition for `BusinessCardCapture` (line 1054); `image_url` is a `string` type. No modifications needed.
- `.claude/commands/test_e2e.md` — Read to understand E2E test runner format.
- `.claude/commands/e2e/test_card_review_page.md` — Existing E2E test for CardReviewPage; reference for test structure and patterns.

### New Files
- `.claude/commands/e2e/test_card_image_lightbox.md` — New E2E test file validating the lightbox feature.

## Implementation Plan
### Phase 1: Foundation
- Add new MUI icon imports (`ZoomInIcon`, `BrokenImageIcon`, `CloseIcon`) to CardReviewPage.tsx
- Add `IconButton` to imports if not already present
- Add lightbox state variable (`lightboxImage`)

### Phase 2: Core Implementation
- Add the lightbox Dialog component at the bottom of the JSX (before the existing reject dialog)
- Modify the thumbnail cell to be clickable with hover overlay and zoom icon
- Add broken image handling with `BrokenImageIcon` placeholder and disabled click
- Add `onError` handler for `<img>` to handle broken image URLs at runtime

### Phase 3: Integration
- Ensure `event.stopPropagation()` prevents row selection when clicking thumbnails
- Verify Dialog closes on Escape and backdrop click (MUI default)
- Add close button inside lightbox for explicit dismissal
- Create E2E test file for validation

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create E2E Test File
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_card_review_page.md` to understand the E2E test format
- Create `.claude/commands/e2e/test_card_image_lightbox.md` with test steps that validate:
  1. Navigate to `/card-review`
  2. Verify thumbnails are visible in the table
  3. Hover over a thumbnail and verify zoom icon overlay appears
  4. Click a thumbnail and verify lightbox Dialog opens with full-size image
  5. Verify lightbox displays the image with black background
  6. Close lightbox by clicking backdrop or close button
  7. Verify lightbox closes correctly
  8. Verify broken/missing image shows placeholder icon and is not clickable

### Step 2: Add New Imports to CardReviewPage
- Add `ZoomInIcon` from `@mui/icons-material/ZoomIn`
- Add `BrokenImageIcon` from `@mui/icons-material/BrokenImage`
- Add `CloseIcon` from `@mui/icons-material/Close`
- Add `IconButton` to the MUI imports (if not already present)

### Step 3: Add Lightbox State
- Add `const [lightboxImage, setLightboxImage] = useState<string | null>(null);` inside the `CardReviewPage` component, alongside existing state variables

### Step 4: Make Thumbnails Clickable with Hover Overlay
- Replace the existing thumbnail rendering (lines 408-418) with a clickable version:
  - Wrap the `<img>` in a `Box` container with `position: relative`, `cursor: pointer`
  - Add `onClick` handler that calls `setLightboxImage(capture.image_url)` with `event.stopPropagation()`
  - Add a hover overlay `Box` with `ZoomInIcon` that appears on hover (using `opacity` transition and `&:hover` selector on parent)
  - For missing images (`!capture.image_url`), show a `BrokenImageIcon` centered in the 80x80 placeholder, with no click handler

### Step 5: Add Image Error Handling
- Add an `onError` handler to the thumbnail `<img>` that replaces it with a `BrokenImageIcon` placeholder
- Use a local state set or ref to track which image URLs have failed to load, so the lightbox click is disabled for those entries

### Step 6: Add Lightbox Dialog Component
- Add a `Dialog` component before the existing reject confirmation dialog:
  ```
  <Dialog open={!!lightboxImage} onClose={() => setLightboxImage(null)} maxWidth="md" fullWidth>
    <DialogContent sx={{ p: 0, display: 'flex', justifyContent: 'center', alignItems: 'center', bgcolor: 'black', position: 'relative', minHeight: 300 }}>
      <IconButton onClick={() => setLightboxImage(null)} sx={{ position: 'absolute', top: 8, right: 8, color: 'white' }}>
        <Tooltip title="Cerrar"><CloseIcon /></Tooltip>
      </IconButton>
      <Box component="img" src={lightboxImage || ''} alt="Tarjeta de presentación" sx={{ maxWidth: '100%', maxHeight: '80vh', objectFit: 'contain' }} />
    </DialogContent>
  </Dialog>
  ```
- The Dialog closes on Escape key and backdrop click by default (MUI behavior)

### Step 7: Run Validation Commands
- Run `cd apps/Client && npx tsc --noEmit` to verify no TypeScript errors
- Run `cd apps/Client && npm run build` to verify production build succeeds
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_card_image_lightbox.md` E2E test

## Testing Strategy
### Unit Tests
- No unit tests needed; this is a purely presentational UI change with no business logic. The lightbox state is simple open/close boolean behavior managed by React `useState`. Validation is done via E2E tests.

### Edge Cases
- `image_url` is `null` — thumbnail shows `BrokenImageIcon` placeholder, click is disabled
- `image_url` is a valid URL but the image fails to load (404/broken) — `onError` handler shows placeholder, lightbox click is disabled for that entry
- Clicking thumbnail should not trigger row selection (checkbox toggle) — `event.stopPropagation()` on the click handler
- Multiple rapid clicks on different thumbnails — lightbox updates to show the latest clicked image
- Very large images — constrained by `maxHeight: 80vh` and `maxWidth: 100%` with `objectFit: contain`
- Mobile viewports — Dialog is fullWidth with responsive sizing, close button is touch-friendly (48px minimum touch target via IconButton)

## Acceptance Criteria
- Clicking a card thumbnail in the review table opens a full-size lightbox view of the original photo
- The lightbox displays the image on a black background with `objectFit: contain`
- The lightbox can be closed by pressing Escape, clicking the backdrop, or clicking the close button
- A zoom icon overlay appears when hovering over a clickable thumbnail
- Missing images (`image_url` is null) show a `BrokenImageIcon` placeholder and do not trigger the lightbox
- Broken images (load errors) show a placeholder and do not trigger the lightbox
- Clicking a thumbnail does not toggle the row's checkbox selection
- All UI text is in Spanish (Colombian): alt text "Tarjeta de presentación", close tooltip "Cerrar"
- The lightbox works correctly on mobile viewports with touch-friendly close
- TypeScript compiles with no errors
- Production build succeeds with no errors

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate no TypeScript errors
- `cd apps/Client && npm run build` — Run Client production build to validate no build errors
- `cd apps/Client && npm run lint` — Run ESLint to validate no linting errors
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_card_image_lightbox.md` to validate lightbox functionality end-to-end

## Notes
- This feature is frontend-only; no backend changes required.
- Wave 3 (BCC-006) will add a download button to this lightbox, so the Dialog structure should be clean and extensible for adding action buttons later.
- The `Dialog` component is already imported in CardReviewPage.tsx (used by the reject confirmation dialog), minimizing new imports.
- `IconButton` may need to be added to the MUI imports.
- Arrow key navigation between images is listed as optional in the issue and is deferred to keep scope minimal. The current filtered `captures` list could be used for this in a future enhancement.
