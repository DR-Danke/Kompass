# E2E Test: Card Image Download Button

## User Story

As a back-office team member reviewing business card captures
I want to download the original business card photo to my device
So that I can keep a local copy for records, offline reference, or sharing with colleagues

## Test Steps

### Step 1: Navigate to Card Review Page
1. Open the application at the base URL
2. Login with test credentials (if required)
3. Navigate to `/card-review` page using direct URL
4. **Verify** page title "Revisión de Tarjetas" is visible
5. **Screenshot**: `01_card_review_page_loaded.png`

### Step 2: Click Thumbnail to Open Lightbox
1. Click on a card thumbnail image in the table
2. **Verify** a lightbox Dialog opens with the full-size image
3. **Screenshot**: `02_lightbox_open.png`

### Step 3: Verify Download Button in Lightbox
1. **Verify** a download button (DownloadIcon) is visible in the lightbox DialogActions bar
2. **Verify** the download button has tooltip "Descargar imagen"
3. **Screenshot**: `03_lightbox_download_button.png`

### Step 4: Click Download Button in Lightbox
1. Click the download button in the lightbox DialogActions bar
2. **Verify** a file download is triggered (a download event or blob URL is created)
3. **Screenshot**: `04_lightbox_download_triggered.png`

### Step 5: Close Lightbox and Verify Table Download Button
1. Close the lightbox by clicking the close button
2. **Verify** a download icon button is visible in the table actions column for captures with valid images
3. **Verify** the table download button has tooltip "Descargar imagen"
4. **Screenshot**: `05_table_download_button.png`

### Step 6: Click Table Download Button
1. Click the download icon button in the table actions column
2. **Verify** a file download is triggered without opening the lightbox
3. **Verify** the lightbox does NOT open after clicking the table download button
4. **Screenshot**: `06_table_download_triggered.png`

## Success Criteria

- [ ] Card Review page loads at `/card-review` with title "Revisión de Tarjetas"
- [ ] Lightbox Dialog contains a download button (DownloadIcon) in the DialogActions bar
- [ ] Lightbox download button has tooltip "Descargar imagen"
- [ ] Clicking the lightbox download button triggers a file download
- [ ] Table actions column contains a download icon button for captures with valid images
- [ ] Table download button has tooltip "Descargar imagen"
- [ ] Clicking the table download button triggers download without opening the lightbox
- [ ] Downloaded files are named with pattern `tarjeta-{name}-{timestamp}.jpg`
- [ ] File names are sanitized (no special characters, max 50 chars)
- [ ] All UI text is in Spanish (Colombian): tooltip "Descargar imagen"
- [ ] No console errors during test execution

## Notes

- The test validates the download button UI presence and click behavior
- If no captures with images exist in the database, steps 2-6 may be skipped — structural validation is acceptable
- Download verification depends on the browser's download API; in headless mode, verify the blob URL creation and link click
- The download handler supports both data URI and HTTP URL image sources
