# Feature: Card Image Download Button

## Metadata
issue_number: `172`
adw_id: `f1974dcd`
issue_json: ``

## Feature Description
Add a download button for the original business card image on the CardReviewPage. The download action is accessible from both the lightbox modal (primary) and the thumbnail row actions column (secondary). Downloaded files have meaningful names derived from the company or contact name. The feature supports both data URI and HTTP URL image sources.

## User Story
As a back-office team member reviewing business card captures
I want to download the original business card photo to my device
So that I can keep a local copy for records, offline reference, or sharing with colleagues

## Problem Statement
Users can view business card images in the lightbox but have no way to download the original photo. They must resort to right-click "Save Image As" which is unintuitive, doesn't work for data URIs, and produces generic file names.

## Solution Statement
Add a download `IconButton` with `DownloadIcon` to the existing lightbox `Dialog` via a `DialogActions` bar and a small download icon in the table actions column. Implement a `handleDownloadImage` utility that converts both data URIs and HTTP URLs to blobs, creates an object URL, and triggers a programmatic download with a sanitized, meaningful filename (`tarjeta-{name}-{timestamp}.jpg`). Track the active capture in lightbox state to derive the filename.

## Relevant Files
Use these files to implement the feature:

- `apps/Client/src/pages/kompass/CardReviewPage.tsx` — Main file to modify. Contains the lightbox Dialog (line 585-612), thumbnail rendering (line 416-475), and actions column (line 544-574). All changes are scoped to this single file.
- `apps/Client/src/types/kompass.ts` — Contains `BusinessCardCapture` interface (line 1054) with `company_name`, `contact_name`, and `image_url` fields used for download filename generation.
- `apps/Client/src/hooks/kompass/useCardReview.ts` — Hook providing `captures` array; no changes needed but useful for understanding data flow.
- `.claude/commands/test_e2e.md` — Read to understand E2E test runner setup and execution.
- `.claude/commands/e2e/test_card_image_lightbox.md` — Read as reference for existing lightbox E2E test pattern; the new download E2E test follows the same structure.

### New Files
- `.claude/commands/e2e/test_card_image_download.md` — E2E test specification for validating the download button UI, click behavior, and file download.

## Implementation Plan
### Phase 1: Foundation
Expand lightbox state to track the full capture object (not just the image URL). This provides access to `company_name` and `contact_name` for generating meaningful download filenames. Add the `handleDownloadImage` utility function.

### Phase 2: Core Implementation
Add a `DialogActions` bar to the lightbox with a download `IconButton`. Add a download icon button in the table actions column for captures with valid images. Import `DownloadIcon` from MUI icons.

### Phase 3: Integration
Create the E2E test file. Run validation commands to ensure no regressions in TypeScript compilation and build.

## Step by Step Tasks

### Step 1: Read existing code and dependencies
- Read `apps/Client/src/pages/kompass/CardReviewPage.tsx` to understand the current lightbox implementation
- Read `apps/Client/src/types/kompass.ts` to understand the `BusinessCardCapture` interface
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_card_image_lightbox.md` to understand E2E test patterns

### Step 2: Create E2E test file for card image download
- Create `.claude/commands/e2e/test_card_image_download.md` following the pattern in `test_card_image_lightbox.md`
- Define test steps:
  1. Navigate to `/card-review` and verify page loads
  2. Click a thumbnail to open lightbox
  3. Verify download button is visible in the lightbox `DialogActions` bar with tooltip "Descargar imagen"
  4. Click the download button and verify a file download is triggered
  5. Close lightbox and verify download icon button is visible in the table actions column for captures with images
  6. Click the table download button and verify download is triggered without opening the lightbox
- Define success criteria covering UI presence, click behavior, and filename format

### Step 3: Expand lightbox state to track the full capture
- In `CardReviewPage.tsx`, add a new state variable:
  ```typescript
  const [lightboxCapture, setLightboxCapture] = useState<typeof captures[0] | null>(null);
  ```
- Update the thumbnail click handler (around line 428-429) to also set the capture:
  ```typescript
  onClick={(e) => {
    e.stopPropagation();
    setLightboxImage(capture.image_url);
    setLightboxCapture(capture);
  }}
  ```
- Update lightbox close to also clear the capture:
  ```typescript
  onClose={() => { setLightboxImage(null); setLightboxCapture(null); }}
  ```
- Update the close button onClick similarly

### Step 4: Implement the download handler function
- Add `handleDownloadImage` function inside `CardReviewPage` component:
  ```typescript
  const handleDownloadImage = async (imageUrl: string | null, captureName: string | null) => {
    if (!imageUrl) return;
    try {
      const response = await fetch(imageUrl);
      const blob = await response.blob();
      const safeName = (captureName || 'sin-nombre')
        .replace(/[^a-zA-Z0-9áéíóúñÁÉÍÓÚÑ\s-]/g, '')
        .trim()
        .replace(/\s+/g, '-')
        .substring(0, 50);
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `tarjeta-${safeName}-${Date.now()}.jpg`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('INFO [CardReviewPage]: Error downloading image', error);
    }
  };
  ```
- The function derives the capture name from `company_name || contact_name || 'sin-nombre'`

### Step 5: Add DownloadIcon import
- Add `DownloadIcon` to the MUI icons imports at the top of the file:
  ```typescript
  import DownloadIcon from '@mui/icons-material/Download';
  ```

### Step 6: Add download button to lightbox DialogActions
- In the lightbox Dialog (around line 585-612), add a `DialogActions` bar after the `DialogContent`:
  ```tsx
  <DialogActions sx={{ justifyContent: 'center', bgcolor: 'black' }}>
    <Tooltip title="Descargar imagen">
      <IconButton
        onClick={() => handleDownloadImage(
          lightboxImage,
          lightboxCapture?.company_name || lightboxCapture?.contact_name || null
        )}
        color="primary"
      >
        <DownloadIcon />
      </IconButton>
    </Tooltip>
  </DialogActions>
  ```

### Step 7: Add download icon to table actions column
- In the actions `TableCell` (around line 544-574), add a download icon button before the approve/reject buttons:
  ```tsx
  {capture.image_url && !brokenImages.has(capture.image_url) && (
    <Tooltip title="Descargar imagen">
      <IconButton
        size="small"
        onClick={(e) => {
          e.stopPropagation();
          handleDownloadImage(
            capture.image_url,
            capture.company_name || capture.contact_name || null
          );
        }}
      >
        <DownloadIcon fontSize="small" />
      </IconButton>
    </Tooltip>
  )}
  ```

### Step 8: Run validation commands
- Run TypeScript type check: `cd apps/Client && npm run typecheck`
- Run build: `cd apps/Client && npm run build`
- Run lint: `cd apps/Client && npm run lint`
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_card_image_download.md` to validate this functionality works

## Testing Strategy
### Unit Tests
No dedicated unit tests needed — this is a purely frontend UI feature with no business logic beyond the download handler. Validation is covered by TypeScript type checking, build verification, and E2E tests.

### Edge Cases
- **No image URL**: Download button should not appear (guarded by `capture.image_url` check)
- **Broken image**: Download button should not appear in thumbnail row (guarded by `brokenImages` check)
- **Data URI images**: `fetch()` handles data URIs natively; no special branching needed
- **HTTP URL images**: Standard `fetch()` + blob conversion
- **Special characters in names**: Sanitized via regex before use in filename
- **Null company and contact names**: Falls back to `'sin-nombre'`
- **Very long names**: Truncated to 50 characters

## Acceptance Criteria
- Download button (DownloadIcon) is visible in the lightbox DialogActions bar with tooltip "Descargar imagen"
- Clicking the lightbox download button saves the card image to the user's device
- Download icon button is visible in the table actions column for captures with valid images
- Clicking the table download button triggers download without opening the lightbox
- Downloaded files are named `tarjeta-{company_name|contact_name|sin-nombre}-{timestamp}.jpg`
- File names are sanitized (no special characters, max 50 chars)
- Download works for both data URI and HTTP URL image sources
- All UI text is in Spanish (Colombian)
- TypeScript compiles without errors
- Production build succeeds without errors
- E2E test passes

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Client && npx tsc --noEmit` — Run TypeScript type check to validate no type errors
- `cd apps/Client && npm run build` — Run production build to validate no build errors
- `cd apps/Client && npm run lint` — Run ESLint to validate no linting errors
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_card_image_download.md` E2E test file to validate this functionality works

## Notes
- All changes are scoped to a single file: `apps/Client/src/pages/kompass/CardReviewPage.tsx`
- No new npm packages required — `@mui/icons-material/Download` is already available in the MUI icons package
- No backend changes required
- The `fetch()` API handles both data URIs and HTTP URLs uniformly, so no conditional branching is needed in the download handler
- The lightbox close handler must be updated in two places: the Dialog `onClose` prop and the close IconButton `onClick`
