# E2E Test: Auto-Send Card Follow-Up Email

## User Story

As a Kompass sourcing agent at a trade fair
I want to see email status feedback when I create a supplier from a business card
So that I know whether a follow-up email was sent, skipped, or failed

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

### Step 3: Wait for Extraction
1. **Verify** the uploaded card shows a status chip
2. If status is "extracted" (green), proceed to Step 4
3. If status is "pending" or "failed", the test cannot proceed (AI service unavailable)
4. **Screenshot**: `03_extraction_status.png`

### Step 4: Click "Crear Proveedor"
1. Click the "Crear Proveedor" button on the extracted card
2. **Verify** the button text changes to "Creando..." with a spinner while in progress
3. Wait for the operation to complete
4. **Screenshot**: `04_creating_supplier.png`

### Step 5: Verify Email Status Notification on Card Capture Page
1. **Verify** a success snackbar appears confirming supplier creation
2. Check for email status notification:
   - If `AUTO_SEND_CARD_EMAIL=true` and email exists: **Verify** success snackbar contains "Correo de seguimiento enviado"
   - If `AUTO_SEND_CARD_EMAIL=true` and no email: **Verify** warning snackbar "No se encontró correo electrónico — seguimiento manual requerido"
   - If `AUTO_SEND_CARD_EMAIL=false` (default): **Verify** success snackbar shows "Proveedor creado: {name}" without email mention
3. **Screenshot**: `05_email_status_card_capture.png`

### Step 6: Navigate to Card Review Page
1. Navigate to `/card-review` page using the sidebar navigation or direct URL
2. **Verify** page title "Revisión de Tarjetas" is visible
3. **Verify** card list is loaded
4. **Screenshot**: `06_card_review_page.png`

### Step 7: Approve a Card on Review Page
1. Find a card with status "extracted" (pending review)
2. Click the approve button on the card
3. Wait for the operation to complete
4. **Screenshot**: `07_approve_card.png`

### Step 8: Verify Email Status Notification on Card Review Page
1. **Verify** a snackbar appears confirming supplier creation
2. Check for email status notification:
   - If `AUTO_SEND_CARD_EMAIL=true` and email exists: **Verify** success snackbar contains "Correo de seguimiento enviado"
   - If `AUTO_SEND_CARD_EMAIL=true` and no email: **Verify** warning snackbar "No se encontró correo electrónico — seguimiento manual requerido"
   - If `AUTO_SEND_CARD_EMAIL=false` (default): **Verify** success snackbar shows "creado exitosamente" without email mention
3. **Screenshot**: `08_email_status_card_review.png`

### Step 9: Verify No Console Errors
1. Check browser console for any JavaScript errors during the test
2. **Screenshot**: `09_console_check.png`

## Success Criteria

- [ ] Card Capture page loads correctly
- [ ] Business card upload and extraction works
- [ ] "Crear Proveedor" creates supplier successfully
- [ ] Email status notification appears in snackbar on CardCapturePage
- [ ] Email status notification appears in snackbar on CardReviewPage
- [ ] Warning snackbar (orange) appears when email is missing or failed
- [ ] Success snackbar (green) appears when email is sent or auto-email is disabled
- [ ] All UI text is in Spanish (Colombian)
- [ ] No console errors during test execution

## Notes

- Default `AUTO_SEND_CARD_EMAIL=false` means no email is attempted — only "Proveedor creado" success message shown
- When `AUTO_SEND_CARD_EMAIL=true` with `EMAIL_MOCK_MODE=true` (default), mock emails succeed and show "Correo de seguimiento enviado"
- Email failure is non-blocking: supplier creation always succeeds, but a warning snackbar indicates email failure
- Both `/card-capture` (create-supplier) and `/card-review` (approve) flows use the same backend logic
- The endpoint is POST /api/extract/business-cards/{id}/create-supplier (CardCapturePage) and POST /api/extract/business-cards/{id}/approve (CardReviewPage)
