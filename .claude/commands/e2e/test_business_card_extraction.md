# E2E Test: Business Card AI Extraction

## User Story

As a Kompass sourcing agent at a trade fair
I want uploaded business card photos to be automatically processed by AI to extract contact information
So that I can quickly digitize supplier details without manual data entry

## Test Steps

### Step 1: Navigate to Card Capture Page
1. Open the application at the base URL
2. Login with test credentials (if required)
3. Navigate to `/card-capture` page using the sidebar navigation or direct URL
4. **Verify** page title "Captura de Tarjetas" is visible
5. **Verify** upload area is visible
6. **Screenshot**: `01_card_capture_page.png`

### Step 2: Upload a Business Card Image
1. Enter "Canton Fair 2026" in the fair name field
2. Create a test image file (small PNG or JPG)
3. Upload the test image via the file input
4. **Verify** upload completes (success snackbar appears)
5. **Verify** the capture appears in the recent captures list
6. **Screenshot**: `02_card_uploaded.png`

### Step 3: Verify Auto-Extraction Behavior
1. **Verify** the uploaded card shows a status — either "extracted" (green) if AI extracted successfully, or "failed" (red) if AI service was unavailable, or "pending" (orange) if auto-extract didn't run
2. **Verify** the status chip is visible on the capture card
3. **Screenshot**: `03_extraction_status.png`

### Step 4: Verify Extracted Fields Display (If Extracted)
1. If the capture status is "extracted":
   - **Verify** extracted fields are displayed (company name, contact name, phone, email, address)
   - **Verify** each field has a confidence badge (percentage chip)
   - **Verify** confidence badges use color coding (green >= 80%, yellow >= 50%, red < 50%)
2. If the capture status is "pending" or "failed":
   - This step passes (AI service may not be available in test environment)
3. **Screenshot**: `04_extracted_fields.png`

### Step 5: Verify Extract/Retry Buttons
1. If a capture has status "pending":
   - **Verify** "Extraer" button is visible with a robot icon
   - Click the "Extraer" button
   - **Verify** a spinner appears while extraction is in progress
   - **Verify** the status updates after extraction completes
2. If a capture has status "failed":
   - **Verify** "Reintentar" button is visible with a replay icon
   - **Verify** error message "Error en la extracción" is shown
3. **Screenshot**: `05_action_buttons.png`

### Step 6: Verify Card Layout
1. **Verify** each capture card shows:
   - Image thumbnail on the left
   - Status chip in the header
   - Timestamp on the right side of the header
   - Extracted fields or pending message below
   - Action buttons at the bottom when applicable
2. **Screenshot**: `06_card_layout.png`

### Step 7: Upload Second Card
1. Upload another test image
2. **Verify** the new capture appears at the top of the list
3. **Verify** both captures are visible
4. **Screenshot**: `07_multiple_captures.png`

## Success Criteria

- [ ] Card Capture page loads with title "Captura de Tarjetas"
- [ ] Business card image upload works successfully
- [ ] Upload returns a capture with a valid status (pending, extracted, or failed)
- [ ] Status chips display with correct colors (pending=orange, extracted=green, failed=red, processing=blue)
- [ ] When status is "extracted", contact fields are displayed with confidence badges
- [ ] Confidence badges use green/yellow/red color coding based on score
- [ ] "Extraer" button is visible for pending captures
- [ ] "Reintentar" button is visible for failed captures
- [ ] Spinner appears during extraction processing
- [ ] Multiple captures can be listed with most recent first
- [ ] All UI text is in Spanish (Colombian)
- [ ] No console errors during test execution

## Notes

- AI extraction may not be available in all test environments (no API keys configured)
- When AI is unavailable, uploads will succeed but extraction will fail gracefully
- The auto-extract feature triggers extraction during upload by default
- Confidence scores range from 0.0 to 1.0 and are displayed as percentages
- The extraction endpoint is POST /api/extract/business-cards/{id}/extract
