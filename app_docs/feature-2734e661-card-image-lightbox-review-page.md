# Card Image Lightbox on Review Page

**ADW ID:** 2734e661
**Date:** 2026-03-10
**Specification:** specs/issue-171-adw-2734e661-sdlc_planner-card-image-lightbox-review-page.md

## Overview

Adds a full-size image lightbox/modal to the CardReviewPage, allowing back-office team members to click on business card thumbnails to view the original photo at full resolution. This enables verification of AI extraction accuracy by comparing extracted data against the actual card image before approving or rejecting.

## What Was Built

- Clickable card thumbnails with hover zoom overlay in the review table
- MUI Dialog-based lightbox displaying full-size card images on a black background
- Broken/missing image handling with `BrokenImageIcon` placeholder
- Runtime image error detection that disables lightbox for failed URLs
- E2E test specification for lightbox functionality

## Technical Implementation

### Files Modified

- `apps/Client/src/pages/kompass/CardReviewPage.tsx`: Added lightbox Dialog component, clickable thumbnail with hover overlay, broken image tracking state, and `onError` handler for runtime image failures
- `.claude/commands/e2e/test_card_image_lightbox.md`: New E2E test specification covering lightbox open/close, hover overlay, broken image placeholder, and row selection isolation

### Key Changes

- **Lightbox state**: Two new state variables — `lightboxImage` (string | null) for the currently displayed image URL and `brokenImages` (Set<string>) for tracking failed image loads
- **Clickable thumbnails**: Thumbnail `<img>` wrapped in a `Box` with `position: relative`, `cursor: pointer`, and `event.stopPropagation()` to prevent row checkbox toggling when clicking the image
- **Hover overlay**: A semi-transparent black overlay with `ZoomInIcon` appears on hover via CSS `opacity` transition and `&:hover .lightbox-overlay` selector
- **Broken image handling**: Images with null `image_url` or runtime load errors display a `BrokenImageIcon` centered in an 80x80 grey placeholder; lightbox click is disabled for these entries
- **Lightbox Dialog**: MUI `Dialog` (maxWidth="md", fullWidth) with black background, close button (`IconButton` with `CloseIcon` + "Cerrar" tooltip), and image constrained by `maxHeight: 80vh` with `objectFit: contain`. Closes via Escape key, backdrop click, or close button (MUI defaults)

## How to Use

1. Navigate to the **Card Review** page (`/card-review`)
2. Locate a business card capture with a thumbnail image in the table
3. Hover over the thumbnail — a zoom icon overlay appears
4. Click the thumbnail to open the lightbox with the full-size image
5. Close the lightbox by:
   - Clicking the **X** button in the top-right corner
   - Pressing the **Escape** key
   - Clicking the dark backdrop outside the image
6. Cards with missing or broken images display a broken image icon and cannot be clicked

## Configuration

No additional configuration required. This is a frontend-only UI enhancement with no backend changes or new environment variables.

## Testing

- **TypeScript check**: `cd apps/Client && npx tsc --noEmit`
- **Production build**: `cd apps/Client && npm run build`
- **Linting**: `cd apps/Client && npm run lint`
- **E2E test**: Run `/e2e:test_card_image_lightbox` slash command

## Notes

- Frontend-only feature — no backend or database changes
- All UI text is in Spanish (Colombian): alt text "Tarjeta de presentación", close tooltip "Cerrar"
- The Dialog structure is designed to be extensible for a future download button (Wave 3, BCC-006)
- Arrow key navigation between images is deferred; the filtered `captures` list can support this in a future enhancement
