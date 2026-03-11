# Card Image Download Button

**ADW ID:** f1974dcd
**Date:** 2026-03-10
**Specification:** specs/issue-172-adw-f1974dcd-sdlc_planner-card-image-download-button.md

## Overview

Adds a download button for business card images on the CardReviewPage. Users can download card images from both the lightbox modal (primary) and the table actions column (secondary), with meaningful filenames derived from the company or contact name.

## What Was Built

- Download button in the lightbox `DialogActions` bar with tooltip "Descargar imagen"
- Download icon button in the table actions column for captures with valid images
- `handleDownloadImage` utility that converts both data URIs and HTTP URLs to blobs and triggers a programmatic download
- Sanitized filename generation: `tarjeta-{name}-{timestamp}.jpg`
- Lightbox state expansion to track the full capture object for filename derivation

## Technical Implementation

### Files Modified

- `apps/Client/src/pages/kompass/CardReviewPage.tsx`: Added `DownloadIcon` import, `lightboxCapture` state, `handleDownloadImage` function, download button in lightbox `DialogActions`, and download icon in table actions column

### Key Changes

- **State expansion**: Added `lightboxCapture` state (`useState<typeof captures[0] | null>`) to track the full capture object when the lightbox opens, enabling access to `company_name` and `contact_name` for filename generation
- **Download handler**: `handleDownloadImage(imageUrl, captureName)` fetches the image as a blob, creates an object URL, and triggers download via a temporary `<a>` element. Works uniformly for both data URIs and HTTP URLs
- **Filename sanitization**: Strips special characters (preserving Spanish accents), replaces whitespace with hyphens, and truncates to 50 characters. Falls back to `'sin-nombre'` when no name is available
- **Lightbox download button**: `DialogActions` bar with black background at the bottom of the lightbox dialog, containing a primary-colored `DownloadIcon` button
- **Table download button**: Small `DownloadIcon` button in the actions column, only shown for captures with valid (non-broken) images. Uses `stopPropagation` to prevent row selection

## How to Use

1. Navigate to the **Card Review** page (`/card-review`)
2. **From lightbox**: Click a business card thumbnail to open the lightbox, then click the download icon at the bottom of the modal
3. **From table**: Click the download icon button in the actions column of any capture row that has a valid image
4. The image downloads as `tarjeta-{company-or-contact-name}-{timestamp}.jpg`

## Configuration

No additional configuration required. Uses existing MUI icons (`@mui/icons-material/Download`) already available in the project.

## Testing

- Run TypeScript type check: `cd apps/Client && npx tsc --noEmit`
- Run production build: `cd apps/Client && npm run build`
- Run lint: `cd apps/Client && npm run lint`
- Run E2E test: `/test_e2e` with `.claude/commands/e2e/test_card_image_download.md`

## Notes

- All changes scoped to a single file (`CardReviewPage.tsx`)
- No backend changes required
- No new npm packages needed
- The `fetch()` API handles both data URIs and HTTP URLs uniformly
- All UI text is in Spanish (Colombian): "Descargar imagen", "sin-nombre"
