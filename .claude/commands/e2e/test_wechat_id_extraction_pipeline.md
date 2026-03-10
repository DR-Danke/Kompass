# E2E Test: WeChat ID Extraction Pipeline

## User Story

As a Kompass sourcing agent at a Chinese trade fair
I want the WeChat ID extracted from business cards to be visible during review and on the capture page
So that I can verify the extracted WeChat ID before creating a supplier record

## Test Steps

### Step 1: Navigate to Card Review Page
1. Open the application at the base URL
2. Login with test credentials (if required)
3. Navigate to `/card-review` page using the sidebar navigation or direct URL
4. **Verify** page title "Revisión de Tarjetas" is visible
5. **Verify** the table header contains a "WeChat ID" column
6. **Screenshot**: `01_card_review_wechat_column.png`

### Step 2: Verify WeChat ID Column in Review Table
1. If there are captures in the table:
   - **Verify** each row has a cell corresponding to the "WeChat ID" column
   - **Verify** the WeChat ID cell displays either a value or "—" for empty
   - **Verify** if a WeChat ID has a confidence score, a confidence badge (percentage chip) is displayed
2. If the table is empty:
   - This step passes (no captures available in test environment)
3. **Screenshot**: `02_wechat_id_cells.png`

### Step 3: Verify WeChat ID is Editable
1. If there are captures with status "extracted" or "pending":
   - Click on a WeChat ID cell
   - **Verify** the cell becomes an editable text field
   - Type "test_wechat_edit"
   - Press Enter or click outside the field
   - **Verify** the field saves the new value
2. If no editable captures are available:
   - This step passes
3. **Screenshot**: `03_wechat_id_editable.png`

### Step 4: Navigate to Card Capture Page
1. Navigate to `/card-capture` page using the sidebar navigation or direct URL
2. **Verify** page title "Captura de Tarjetas" is visible
3. **Screenshot**: `04_card_capture_page.png`

### Step 5: Verify WeChat ID in Extracted Fields
1. If there are captures with status "extracted":
   - **Verify** extracted fields section is visible (company, contact, phone, email, address)
   - **Verify** if the capture has a `contact_wechat` value, it appears with a chat icon
   - **Verify** if a confidence score exists for WeChat ID, a confidence badge is displayed
2. If no extracted captures are available:
   - This step passes (AI service may not be available in test environment)
3. **Screenshot**: `05_wechat_id_extracted_field.png`

### Step 6: Verify Confidence Badge Colors
1. If confidence badges are visible for WeChat ID on either page:
   - **Verify** scores >= 80% show green badge
   - **Verify** scores >= 50% and < 80% show yellow/warning badge
   - **Verify** scores < 50% show red badge
2. If no confidence badges are visible:
   - This step passes
3. **Screenshot**: `06_confidence_badge_colors.png`

## Success Criteria

- [ ] Card Review page table includes a "WeChat ID" column header
- [ ] WeChat ID cells in the review table show values or "—" for null
- [ ] WeChat ID cells are editable when capture status allows editing
- [ ] Confidence badges appear next to WeChat ID values when confidence data exists
- [ ] Card Capture page shows WeChat ID in extracted fields with a chat icon
- [ ] Confidence badge color coding works correctly (green/yellow/red)
- [ ] No console errors during test execution
- [ ] All UI text is in Spanish (Colombian) except "WeChat ID" (proper noun)

## Notes

- WeChat ID may be null for many business cards — the field should gracefully handle empty values
- The ExtractedField component on CardCapturePage returns null for empty values, so WeChat ID only appears when present
- The EditableCell component on CardReviewPage shows "—" for null values
- AI extraction may not be available in all test environments
- This test validates the UI visibility of WeChat ID; the backend pipeline is verified separately
