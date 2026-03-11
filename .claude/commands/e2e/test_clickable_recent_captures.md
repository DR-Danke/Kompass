# E2E Test: Clickable Recent Captures Navigation

## User Story

As a Kompass sourcing agent at a trade fair
I want to click on a recent capture card to navigate directly to its review details
So that I can quickly review and confirm extracted supplier data without manually navigating to the review page

## Test Steps

### Step 1: Navigate to Card Capture Page
1. Open the application at the base URL
2. Login with test credentials (if required)
3. Navigate to `/card-capture` page using the sidebar navigation item "Captura Tarjetas" or direct URL
4. **Verify** page title "Captura de Tarjetas" is visible
5. **Verify** the "Capturas Recientes" section heading is visible
6. **Screenshot**: `01_card_capture_page_loaded.png`

### Step 2: Verify Recent Captures List Has Cards
1. **Verify** the recent captures list contains at least one capture card
2. If no captures exist, upload a test image first to create one, then verify the card appears
3. **Screenshot**: `02_recent_captures_visible.png`

### Step 3: Verify Hover Feedback on Capture Card
1. Hover over the first capture card in the list
2. **Verify** the cursor changes to pointer (`cursor: pointer`)
3. **Verify** the card shows an elevated shadow on hover
4. **Screenshot**: `03_hover_feedback.png`

### Step 4: Click Capture Card to Navigate
1. Click on the body of the first capture card (not on any action button)
2. **Verify** the browser navigates to `/card-review` page
3. **Verify** the Card Review page title "Revisión de Tarjetas" is visible
4. **Screenshot**: `04_navigated_to_card_review.png`

### Step 5: Verify Highlighted Row on Card Review Page
1. **Verify** the clicked capture's row is visible in the review table
2. **Verify** the row has a highlight animation (pulse effect with light blue background)
3. Wait 4 seconds for the highlight to clear
4. **Screenshot**: `05_highlighted_row.png`

### Step 6: Navigate Back and Verify Action Buttons
1. Navigate back to `/card-capture` page
2. **Verify** the "Captura de Tarjetas" page title is visible
3. If a capture card has an action button visible (e.g., "Extraer", "Reintentar", or "Crear Proveedor"), click the action button
4. **Verify** the page does NOT navigate away from `/card-capture` — the URL remains `/card-capture`
5. **Verify** the action button performs its function without triggering card-level navigation
6. **Screenshot**: `06_action_button_no_navigation.png`

## Success Criteria

- [ ] Card Capture page loads at `/card-capture` with title "Captura de Tarjetas"
- [ ] Recent captures list shows at least one capture card
- [ ] Capture cards show `cursor: pointer` styling on hover
- [ ] Capture cards show elevated shadow on hover
- [ ] Clicking a capture card navigates to `/card-review`
- [ ] Card Review page title "Revisión de Tarjetas" is visible after navigation
- [ ] The clicked capture's row is highlighted with pulse animation
- [ ] Clicking action buttons (Extraer, Reintentar, Crear Proveedor) does NOT trigger navigation
- [ ] All UI text is in Spanish (Colombian)
- [ ] No console errors during test execution

## Notes

- This feature leverages the existing `highlightCaptureId` mechanism on CardReviewPage (built in issue #169)
- Navigation uses React Router's `state` parameter (does not modify the URL path beyond `/card-review`)
- The `data-capture-id` attribute on table rows can be used to locate the highlighted row
- Action buttons use `event.stopPropagation()` to prevent card-level click from firing
