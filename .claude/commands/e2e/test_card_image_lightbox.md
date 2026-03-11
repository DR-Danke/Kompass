# E2E Test: Card Image Lightbox on Review Page

## User Story

As a back-office team member reviewing business card captures
I want to click a card thumbnail to see the full-size original photo in a lightbox
So that I can verify the AI extraction accuracy against the actual business card before approving or rejecting

## Test Steps

### Step 1: Navigate to Card Review Page
1. Open the application at the base URL
2. Login with test credentials (if required)
3. Navigate to `/card-review` page using direct URL
4. **Verify** page title "Revisión de Tarjetas" is visible
5. **Screenshot**: `01_card_review_page_loaded.png`

### Step 2: Verify Thumbnails Visible in Table
1. **Verify** the captures table is visible with card rows
2. **Verify** thumbnail images are visible in the "Imagen" column
3. **Verify** thumbnails have cursor pointer style indicating they are clickable
4. **Screenshot**: `02_thumbnails_visible.png`

### Step 3: Verify Hover Overlay with Zoom Icon
1. Hover over a card thumbnail image
2. **Verify** a zoom icon overlay appears on hover
3. **Screenshot**: `03_hover_zoom_overlay.png`

### Step 4: Click Thumbnail to Open Lightbox
1. Click on a card thumbnail image
2. **Verify** a lightbox Dialog opens with the full-size image
3. **Verify** the lightbox has a black background
4. **Verify** the image is displayed with `object-fit: contain`
5. **Verify** a close button (X icon) is visible in the top-right corner
6. **Screenshot**: `04_lightbox_open.png`

### Step 5: Close Lightbox via Close Button
1. Click the close button (X icon) in the lightbox
2. **Verify** the lightbox closes and the table is visible again
3. **Screenshot**: `05_lightbox_closed_button.png`

### Step 6: Close Lightbox via Backdrop Click
1. Click on a thumbnail to re-open the lightbox
2. Click on the backdrop (outside the dialog content)
3. **Verify** the lightbox closes
4. **Screenshot**: `06_lightbox_closed_backdrop.png`

### Step 7: Verify Thumbnail Click Does Not Toggle Row Selection
1. Note the current checkbox state of a row
2. Click on the thumbnail image in that row
3. **Verify** the lightbox opens but the row checkbox state has NOT changed
4. Close the lightbox
5. **Screenshot**: `07_no_row_selection_toggle.png`

### Step 8: Verify Broken/Missing Image Placeholder
1. If any cards have missing or broken images, **verify** a broken image placeholder icon is displayed
2. **Verify** the placeholder is NOT clickable (no cursor pointer, no lightbox opens on click)
3. **Screenshot**: `08_broken_image_placeholder.png`

## Success Criteria

- [ ] Card Review page loads at `/card-review` with title "Revisión de Tarjetas"
- [ ] Thumbnail images are visible in the table with cursor pointer style
- [ ] Hovering over a thumbnail shows a zoom icon overlay
- [ ] Clicking a thumbnail opens a lightbox Dialog with the full-size image
- [ ] Lightbox displays image on a black background with `object-fit: contain`
- [ ] Lightbox has a close button (X icon) in the top-right corner
- [ ] Lightbox closes when clicking the close button
- [ ] Lightbox closes when clicking the backdrop
- [ ] Clicking a thumbnail does NOT toggle the row checkbox selection
- [ ] Missing/broken images show a placeholder icon and are not clickable
- [ ] All UI text is in Spanish (Colombian): alt text "Tarjeta de presentación", close tooltip "Cerrar"
- [ ] No console errors during test execution

## Notes

- The test validates the lightbox UI and interaction behavior
- If no captures with images exist in the database, steps 2-7 may be skipped — structural validation is acceptable
- Broken image testing depends on data availability; step 8 is best-effort
