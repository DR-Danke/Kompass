# E2E Test: Supplier Name Populated After Card Approval

## User Story

As a Kompass sourcing agent
I want the supplier name to be correctly populated when I approve a business card
So that suppliers don't appear with blank names in the Suppliers list

## Test Steps

### Step 1: Navigate to Card Review Page
1. Open the application at the base URL
2. Login with test credentials (if required)
3. Navigate to `/card-review` page using the sidebar navigation or direct URL
4. **Verify** page title "Revisión de Tarjetas" is visible
5. **Screenshot**: `01_card_review_page.png`

### Step 2: Verify Extracted Cards Show Company Name
1. **Verify** the card review table/list is visible
2. **Verify** at least one extracted card is present with status "Extraído"
3. **Verify** the company_name field is visible and populated (not blank) in the editable cell
4. **Verify** the contact_name field is visible in the contact column
5. **Screenshot**: `02_extracted_cards_with_names.png`

### Step 3: Edit Company Name Field
1. Click on the company_name editable cell of an extracted card
2. Clear the field and type a new company name (e.g., "Test Company E2E")
3. Press Enter or click away to save the edit
4. **Verify** the edit persists (cell shows the new value)
5. **Verify** no error snackbar appears
6. **Screenshot**: `03_company_name_edited.png`

### Step 4: Approve Card with Valid Company Name
1. Click the "Aprobar" button on the card with the edited company name
2. **Verify** the approval operation completes (success snackbar appears)
3. **Verify** the card status changes to "Confirmado"
4. **Screenshot**: `04_card_approved.png`

### Step 5: Navigate to Suppliers Page and Verify Name
1. Navigate to `/suppliers` page using the sidebar navigation or direct URL
2. **Verify** page title "Proveedores" is visible
3. Search for the supplier name "Test Company E2E" in the search field
4. **Verify** the supplier appears in the list with the correct name "Test Company E2E" (NOT blank)
5. **Verify** the supplier name cell is not empty or whitespace-only
6. **Screenshot**: `05_supplier_with_correct_name.png`

### Step 6: Verify Contact Name is in Contact Field
1. Click on the supplier row to open details
2. **Verify** the contact_name field shows the original contact name (e.g., "Zhang Wei"), NOT the supplier name
3. **Verify** the supplier name field shows "Test Company E2E"
4. **Screenshot**: `06_supplier_contact_name_correct.png`

## Success Criteria

- [ ] Card Review page loads with title "Revisión de Tarjetas"
- [ ] Extracted cards display company_name in the editable cell (not blank)
- [ ] Company name field is editable and changes persist after saving
- [ ] Card approval succeeds and status changes to "Confirmado"
- [ ] Newly created supplier appears in Suppliers page with the correct company name
- [ ] Supplier name is NOT blank or whitespace-only
- [ ] Contact name appears in the contact field, NOT as the supplier name
- [ ] All UI text is in Spanish (Colombian)
- [ ] No console errors during test execution

## Notes

- This test validates the fix for issue #168 where suppliers were created with blank names
- The fix ensures whitespace-only company names fall back to contact_name
- When contact_name is used as fallback, a note is added for manual review
- The endpoint for approval is POST /api/extract/business-cards/{id}/create-supplier
