# E2E Test: Card Review Page (Review & Confirm Extracted Suppliers)

## User Story

As a back-office team member reviewing trade fair captures
I want to see all extracted business cards, correct any AI mistakes, and approve or reject supplier creation
So that only accurate supplier records enter our database and outreach emails go to the right contacts

## Test Steps

### Step 1: Navigate to Card Review Page
1. Open the application at the base URL
2. Login with test credentials (if required)
3. Navigate to `/card-review` page using the sidebar navigation item "Revisión Tarjetas" or direct URL
4. **Verify** page title "Revisión de Tarjetas" is visible
5. **Screenshot**: `01_card_review_page_loaded.png`

### Step 2: Verify Status Filter Tabs
1. **Verify** status filter tabs/buttons are visible: Todos, Pendientes, Extraídas, Confirmadas, Rechazadas
2. **Verify** "Todos" tab is selected by default
3. **Screenshot**: `02_status_filter_tabs.png`

### Step 3: Verify Captures Table Structure
1. **Verify** the captures table/list is visible
2. **Verify** table shows columns/areas for: image, company, contact, email, phone, status, actions
3. **Verify** batch selection checkboxes are visible (header checkbox for select all)
4. **Screenshot**: `03_captures_table_structure.png`

### Step 4: Verify Editable Fields on Extracted Cards
1. If extracted cards exist in the list, click on a text field (company name or contact name)
2. **Verify** the field becomes editable (TextField appears)
3. **Screenshot**: `04_editable_fields.png`

### Step 5: Verify Confidence Score Indicators
1. If extracted cards exist, **verify** confidence score color indicators are visible
2. **Verify** scores use green (≥80%), yellow (≥50%), or red (<50%) colors
3. **Screenshot**: `05_confidence_indicators.png`

### Step 6: Verify Action Buttons on Extracted Cards
1. If extracted cards exist, **verify** "Aprobar" button (green) is visible
2. **Verify** "Rechazar" button (red) is visible
3. **Screenshot**: `06_action_buttons.png`

### Step 7: Verify Reject Confirmation Dialog
1. If extracted cards exist, click "Rechazar" on a card
2. **Verify** confirmation dialog appears with title "Rechazar Tarjeta"
3. **Verify** optional reason text field "Motivo del rechazo (opcional)" is visible
4. **Verify** Cancel and Confirm buttons are present
5. Click Cancel to dismiss
6. **Screenshot**: `07_reject_dialog.png`

### Step 8: Verify Batch Selection and Actions
1. **Verify** batch selection checkboxes are present on each row
2. Select one or more cards using checkboxes
3. **Verify** batch action bar appears with "Aprobar Seleccionados" and "Rechazar Seleccionados" buttons
4. Deselect all cards
5. **Screenshot**: `08_batch_actions.png`

## Success Criteria

- [ ] Card Review page loads at `/card-review` with title "Revisión de Tarjetas"
- [ ] Page is accessible via sidebar navigation item "Revisión Tarjetas"
- [ ] Status filter tabs are visible (Todos, Pendientes, Extraídas, Confirmadas, Rechazadas)
- [ ] Captures table/list shows image, company, contact, email, phone, status, and actions
- [ ] Extracted fields are editable inline (click to edit)
- [ ] Confidence scores are color-coded (green ≥80%, yellow ≥50%, red <50%)
- [ ] "Aprobar" button is visible on extracted cards
- [ ] "Rechazar" button is visible on extracted/pending/failed cards
- [ ] Reject confirmation dialog shows with optional reason field
- [ ] Batch selection checkboxes and batch action buttons are functional
- [ ] All UI text is in Spanish (Colombian)
- [ ] No console errors during test execution

## Notes

- The test validates UI structure and interactions
- Approve/reject actions may fail if no extracted cards exist in the database — that is acceptable for structural validation
- Status values: pending, processing, extracted, confirmed, rejected, failed
