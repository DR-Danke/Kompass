# E2E Test: Auto-Navigate to Card Review After Capture

## User Story

As a Kompass sourcing agent at a trade fair
I want to be automatically taken to the review page after uploading a business card
So that I can immediately review and confirm the extracted supplier data without extra navigation steps

## Test Steps

### Step 1: Navigate to Card Capture Page
1. Open the application at the base URL
2. Login with test credentials (if required)
3. Navigate to `/card-capture` page using the sidebar navigation item "Captura Tarjetas" or direct URL
4. **Verify** page title "Captura de Tarjetas" is visible
5. **Verify** upload button/area is visible with camera icon
6. **Screenshot**: `01_card_capture_page_loaded.png`

### Step 2: Upload a Test Business Card Image
1. Create a test image file (small .png or .jpg)
2. Upload the test image using the file input
3. **Verify** upload progress indicator appears (progress bar)
4. **Verify** after upload completes, the extraction phase indicator appears with text "Extrayendo datos de la tarjeta..."
5. **Screenshot**: `02_extraction_phase_indicator.png`

### Step 3: Verify Auto-Navigation to Card Review Page
1. Wait for extraction to complete (up to 35 seconds)
2. **Verify** the browser automatically navigates to `/card-review` page
3. **Verify** the Card Review page title "Revisión de Tarjetas" is visible
4. **Screenshot**: `03_auto_navigated_to_review.png`

### Step 4: Verify Highlighted Row
1. **Verify** the newly captured card row is visible in the table
2. **Verify** the row has a highlight animation (pulse effect with light blue background)
3. Wait 4 seconds for the highlight to clear
4. **Verify** the highlight animation has cleared (row returns to normal background)
5. **Screenshot**: `04_highlighted_row.png`

### Step 5: Verify No Re-Highlight on Refresh
1. Refresh the Card Review page
2. **Verify** no row has the highlight animation after refresh
3. **Screenshot**: `05_no_highlight_after_refresh.png`

### Step 6: Test Timeout Scenario (Optional)
1. Navigate back to `/card-capture`
2. If possible, simulate a scenario where extraction takes longer than 30 seconds
3. **Verify** a timeout message appears with text containing "La extracción está tomando más tiempo"
4. **Verify** a link to the review page is shown
5. **Screenshot**: `06_timeout_message.png`

## Success Criteria

- [ ] Card Capture page loads correctly at `/card-capture`
- [ ] After upload, extraction phase indicator "Extrayendo datos de la tarjeta..." is shown
- [ ] Auto-navigation to `/card-review` occurs after extraction completes
- [ ] Card Review page title "Revisión de Tarjetas" is visible after navigation
- [ ] The newly captured card row has a visible highlight/pulse animation
- [ ] Highlight clears automatically after ~3 seconds
- [ ] Page refresh does not re-trigger the highlight
- [ ] All UI text is in Spanish (Colombian)
- [ ] No console errors during test execution

## Notes

- The extraction phase uses polling (every 2 seconds) to check capture status
- Polling has a 30-second timeout before showing a manual link
- The highlight uses a CSS keyframe animation (`highlightPulse`)
- Navigation state is cleared from browser history after reading to prevent re-highlight on refresh
- The `data-capture-id` attribute on table rows can be used to locate the highlighted row
