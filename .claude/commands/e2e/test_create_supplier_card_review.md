# E2E Test: Create Supplier from Card Review Page

## User Story

As a back-office team member reviewing trade fair captures
I want to create a supplier directly from the Card Review page after editing extracted data
So that I don't have to navigate back to the Card Capture page to complete the supplier creation workflow

## Test Steps

### Step 1: Navigate to Card Review Page
1. Open the application at the base URL
2. Login with test credentials (if required)
3. Navigate to `/card-review` page using the sidebar navigation or direct URL
4. **Verify** page title "Revisión de Tarjetas" is visible
5. **Verify** the captures table is visible
6. **Screenshot**: `01_card_review_page_loaded.png`

### Step 2: Filter by Extracted Status
1. Click the "Extraídas" filter tab/button
2. **Verify** the filter is selected
3. **Verify** only cards with "Extraído" status are shown (if any exist)
4. **Screenshot**: `02_filtered_extracted.png`

### Step 3: Verify "Crear Proveedor" Button on Extracted Cards
1. If extracted cards exist without a linked supplier:
   - **Verify** a "Crear Proveedor" button is visible in the actions column
   - **Verify** the button has a PersonAdd icon
   - **Verify** the button is a contained primary button (size small)
2. If no extracted cards exist, switch back to "Todos" filter and note there are no testable cards
3. **Screenshot**: `03_create_supplier_button.png`

### Step 4: Verify "Proveedor vinculado" Chip on Confirmed Cards
1. Switch to "Confirmadas" filter tab
2. If confirmed cards with a linked supplier exist:
   - **Verify** a "Proveedor vinculado" chip is visible (outlined, primary color, with CheckCircle icon)
   - **Verify** the "Crear Proveedor" button does NOT appear on confirmed cards
3. **Screenshot**: `04_confirmed_cards_chip.png`

### Step 5: Click "Crear Proveedor" on an Extracted Card
1. Switch back to "Extraídas" filter
2. If an extracted card without a linked supplier exists:
   - Click the "Crear Proveedor" button
   - **Verify** the button text changes to "Creando..." with a spinner (CircularProgress)
   - **Verify** the button is disabled during creation
3. Wait for the operation to complete
4. **Screenshot**: `05_creating_supplier_loading.png`

### Step 6: Verify Supplier Creation Result
1. If creation succeeds:
   - **Verify** a success snackbar appears containing the supplier name
   - **Verify** the card status changes to "Confirmado"
   - **Verify** a "Proveedor vinculado" chip appears replacing the button
   - **Verify** the "Crear Proveedor" button is no longer visible on that card
2. If duplicate detected:
   - **Verify** an error snackbar appears with "Duplicado detectado" message
3. **Screenshot**: `06_creation_result.png`

### Step 7: Verify Existing Approve Button Still Works
1. Switch to "Extraídas" filter
2. If extracted cards remain:
   - **Verify** the "Aprobar" button is still visible alongside or instead of "Crear Proveedor"
   - **Verify** both buttons are functional (do not click Aprobar, just verify it is present)
3. **Screenshot**: `07_approve_button_present.png`

### Step 8: Verify Button Not Shown for Non-Extracted Statuses
1. Switch to "Pendientes" filter
2. If pending cards exist:
   - **Verify** the "Crear Proveedor" button does NOT appear on pending cards
3. Switch to "Rechazadas" filter
4. If rejected cards exist:
   - **Verify** the "Crear Proveedor" button does NOT appear on rejected cards
5. **Screenshot**: `08_button_not_on_other_statuses.png`

## Success Criteria

- [ ] Card Review page loads at `/card-review` with title "Revisión de Tarjetas"
- [ ] "Crear Proveedor" button appears in the actions column for cards with status `extracted` and no linked supplier
- [ ] "Crear Proveedor" button does NOT appear on confirmed, rejected, pending, or failed cards
- [ ] Clicking "Crear Proveedor" shows loading state ("Creando..." with spinner)
- [ ] Button is disabled during supplier creation to prevent double-clicks
- [ ] On successful creation, a success snackbar shows the supplier name
- [ ] On successful creation, the card status updates to "Confirmado"
- [ ] After creation, a "Proveedor vinculado" chip appears instead of the button
- [ ] Duplicate suppliers are detected and shown as error snackbar
- [ ] The existing "Aprobar" button remains functional alongside "Crear Proveedor"
- [ ] All UI text is in Spanish (Colombian)
- [ ] No console errors during test execution

## Notes

- The "Crear Proveedor" button uses the same API endpoint as the CardCapturePage: `POST /api/extract/business-cards/{id}/create-supplier`
- The existing "Aprobar" button is kept alongside "Crear Proveedor" for batch workflow compatibility
- AI extraction may not be available in all test environments — if no extracted cards exist, structural validation is sufficient
- Duplicate detection checks by email (case-insensitive) and phone number
