# E2E Test: Auto-Create Supplier from Business Card

## User Story

As a Kompass sourcing agent at a trade fair
I want to automatically create a supplier from an extracted business card
So that I can quickly build my supplier database without manual data entry and avoid duplicate records

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

### Step 3: Verify Extraction Status
1. **Verify** the uploaded card shows a status chip
2. If status is "extracted" (green), proceed to Step 4
3. If status is "pending" or "failed", the auto-create feature cannot be tested (AI service unavailable)
4. **Screenshot**: `03_extraction_status.png`

### Step 4: Verify "Crear Proveedor" Button
1. **Verify** the "Crear Proveedor" button is visible on extracted cards that have no linked supplier
2. **Verify** the button has a PersonAdd icon
3. **Verify** the button is a contained primary button
4. **Screenshot**: `04_create_supplier_button.png`

### Step 5: Click "Crear Proveedor" Button
1. Click the "Crear Proveedor" button on the extracted card
2. **Verify** the button text changes to "Creando..." with a spinner while in progress
3. **Verify** the button is disabled during creation
4. Wait for the operation to complete
5. **Screenshot**: `05_creating_supplier.png`

### Step 6: Verify Supplier Creation Result
1. If creation succeeds:
   - **Verify** success snackbar appears with "Proveedor creado: {name}"
   - **Verify** a green success alert appears on the card with the supplier name
   - **Verify** the capture status changes to "Confirmado"
   - **Verify** "Proveedor vinculado" chip appears on the card
   - **Verify** the "Crear Proveedor" button is no longer visible
2. If duplicate detected:
   - **Verify** error snackbar appears with "Proveedor duplicado: {name}"
   - **Verify** a yellow warning alert appears with the duplicate supplier name
3. **Screenshot**: `06_creation_result.png`

### Step 7: Verify Duplicate Detection
1. Upload the same business card image again
2. Wait for extraction to complete
3. If the card is extracted, click "Crear Proveedor"
4. **Verify** duplicate detection warning appears (if same email/phone was extracted)
5. **Screenshot**: `07_duplicate_detection.png`

### Step 8: Verify Confirmed Card State
1. **Verify** cards with status "Confirmado" show the "Proveedor vinculado" chip
2. **Verify** the "Crear Proveedor" button does NOT appear on confirmed cards
3. **Verify** the "Crear Proveedor" button does NOT appear on rejected cards
4. **Screenshot**: `08_confirmed_state.png`

## Success Criteria

- [ ] Card Capture page loads with title "Captura de Tarjetas"
- [ ] Business card image upload works successfully
- [ ] "Crear Proveedor" button appears only on extracted cards without a linked supplier
- [ ] Button shows loading state ("Creando..." with spinner) during creation
- [ ] Successful creation shows success snackbar and green alert with supplier name
- [ ] Capture status updates to "Confirmado" after successful creation
- [ ] "Proveedor vinculado" chip appears on confirmed captures
- [ ] "Crear Proveedor" button disappears after successful creation
- [ ] Duplicate detection shows warning with existing supplier name
- [ ] Rejected (duplicate) captures do not show "Crear Proveedor" button
- [ ] All UI text is in Spanish (Colombian)
- [ ] No console errors during test execution

## Notes

- AI extraction may not be available in all test environments (no API keys configured)
- When AI is unavailable, the auto-create feature cannot be tested (requires extracted data)
- Duplicate detection checks by email (case-insensitive) and phone number
- The supplier is created with pipeline_status="contacted" and source="trade_fair"
- The endpoint is POST /api/extract/business-cards/{id}/create-supplier
