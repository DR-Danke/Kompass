# E2E Test: Pricing Configuration Page

## User Story

As a Kompass admin or manager
I want to configure pricing parameters through a dedicated page with HS codes, freight rates, and settings tabs
So that I can maintain accurate pricing data for quotation calculations and ensure tariffs, freight costs, and margins are up-to-date

## Test Steps

### Step 1: Navigate to Pricing Page
1. Open the application at the base URL
2. Login with test credentials (if required)
3. Navigate to `/pricing` page using the sidebar navigation or direct URL
4. **Verify** page title "Pricing Configuration" is visible
5. **Verify** three tabs are visible: "HS Codes", "Freight Rates", "Settings"
6. **Verify** "HS Codes" tab is active by default
7. **Screenshot**: `01_pricing_page_loaded.png`

### Step 2: HS Codes Tab - Verify Structure
1. **Verify** search input field is visible
2. **Verify** "Add HS Code" button is visible
3. **Verify** table displays columns: Code, Description, Duty Rate (%), Actions
4. **Verify** HS codes are displayed in table (if any exist) or empty state message is shown
5. **Screenshot**: `02_hs_codes_tab_structure.png`

### Step 3: HS Codes Tab - Search Functionality
1. Enter "01" in the search field
2. **Verify** table filters to show only codes containing "01" in code or description
3. **Screenshot**: `03_hs_codes_search.png`
4. Clear the search field
5. **Verify** all HS codes are shown again

### Step 4: HS Codes Tab - Create New HS Code
1. Click the "Add HS Code" button
2. **Verify** dialog opens with title "Add HS Code"
3. **Verify** form fields are present: Code (required), Description (required), Duty Rate (required)
4. **Screenshot**: `04_add_hs_code_dialog.png`
5. Fill in the form:
   - Code: "9999.99.99.99"
   - Description: "E2E Test HS Code"
   - Duty Rate: "15"
6. Click "Create" button
7. **Verify** dialog closes
8. **Verify** new HS code appears in the table
9. **Screenshot**: `05_hs_code_created.png`

### Step 5: HS Codes Tab - Form Validation
1. Click "Add HS Code" button
2. Leave all fields empty
3. Click "Create" button
4. **Verify** validation errors appear for required fields
5. **Screenshot**: `06_hs_code_validation_error.png`
6. Click "Cancel" to close the dialog

### Step 6: HS Codes Tab - Edit HS Code
1. Find the row for "9999.99.99.99"
2. Click the edit (pencil) icon
3. **Verify** dialog opens with title "Edit HS Code"
4. **Verify** form is pre-filled with HS code data
5. **Screenshot**: `07_edit_hs_code_dialog.png`
6. Modify the Description field to "E2E Test HS Code Updated"
7. Modify the Duty Rate to "20"
8. Click "Update" button
9. **Verify** dialog closes
10. **Verify** changes are reflected in the table
11. **Screenshot**: `08_hs_code_updated.png`

### Step 7: HS Codes Tab - Delete HS Code
1. Find the row for "9999.99.99.99"
2. Click the delete (trash) icon
3. **Verify** confirmation dialog appears with title "Delete HS Code"
4. **Verify** confirmation message mentions the HS code
5. **Screenshot**: `09_hs_code_delete_confirmation.png`
6. Click "Delete" button to confirm
7. **Verify** dialog closes
8. **Verify** HS code "9999.99.99.99" is no longer in the table
9. **Screenshot**: `10_hs_code_deleted.png`

### Step 8: Navigate to Freight Rates Tab
1. Click on the "Freight Rates" tab
2. **Verify** tab content changes
3. **Verify** filter fields are visible: Origin, Destination
4. **Verify** "Add Freight Rate" button is visible
5. **Verify** table displays columns: Origin, Destination, Incoterm, Rate/kg, Rate/cbm, Min Charge, Transit Days, Valid From, Valid Until, Status, Actions
6. **Screenshot**: `11_freight_rates_tab_structure.png`

### Step 9: Freight Rates Tab - Filter Functionality
1. Enter "China" in the Origin filter field
2. **Verify** table filters to show only rates with origin containing "China"
3. **Screenshot**: `12_freight_rates_filtered.png`
4. Clear the Origin filter
5. **Verify** all freight rates are shown again

### Step 10: Freight Rates Tab - Create New Freight Rate
1. Click the "Add Freight Rate" button
2. **Verify** dialog opens with title "Add Freight Rate"
3. **Verify** form fields are present: Origin, Destination, Incoterm, Rate per kg, Rate per cbm, Minimum Charge, Transit Days, Valid From, Valid Until, Notes
4. **Screenshot**: `13_add_freight_rate_dialog.png`
5. Fill in the form:
   - Origin: "E2E Test Port"
   - Destination: "Cartagena"
   - Incoterm: "FOB"
   - Rate per kg: "0.50"
   - Rate per cbm: "150"
   - Minimum Charge: "100"
   - Transit Days: "30"
   - Valid From: Today's date
   - Valid Until: Today's date + 1 year
6. Click "Create" button
7. **Verify** dialog closes
8. **Verify** new freight rate appears in the table
9. **Screenshot**: `14_freight_rate_created.png`

### Step 11: Freight Rates Tab - Expired Rate Highlighting
1. Find a freight rate where Valid Until is in the past (or create one with past date)
2. **Verify** expired rate row is highlighted with warning color or has "Expired" badge
3. **Screenshot**: `15_expired_rate_highlighting.png`

### Step 12: Freight Rates Tab - Edit Freight Rate
1. Find the row for "E2E Test Port" to "Cartagena"
2. Click the edit (pencil) icon
3. **Verify** dialog opens with title "Edit Freight Rate"
4. **Verify** form is pre-filled with freight rate data
5. **Screenshot**: `16_edit_freight_rate_dialog.png`
6. Modify the Rate per kg to "0.75"
7. Click "Update" button
8. **Verify** dialog closes
9. **Verify** changes are reflected in the table
10. **Screenshot**: `17_freight_rate_updated.png`

### Step 13: Freight Rates Tab - Delete Freight Rate
1. Find the row for "E2E Test Port" to "Cartagena"
2. Click the delete (trash) icon
3. **Verify** confirmation dialog appears
4. Click "Delete" button to confirm
5. **Verify** dialog closes
6. **Verify** freight rate is no longer in the table
7. **Screenshot**: `18_freight_rate_deleted.png`

### Step 14: Navigate to Settings Tab
1. Click on the "Settings" tab
2. **Verify** tab content changes
3. **Verify** settings form is visible with fields:
   - Default Margin %
   - Inspection Cost USD
   - Insurance %
   - Nationalization Cost COP
   - Exchange Rate USD/COP
4. **Verify** each field shows current value
5. **Verify** "Save Settings" button is visible
6. **Screenshot**: `19_settings_tab_structure.png`

### Step 15: Settings Tab - Form Validation
1. Clear the Default Margin % field
2. Enter "-5" (negative value)
3. **Verify** validation error appears (value must be positive or within valid range)
4. **Screenshot**: `20_settings_validation_error.png`

### Step 16: Settings Tab - Update Settings
1. Enter valid values for all fields:
   - Default Margin %: "25"
   - Inspection Cost USD: "150"
   - Insurance %: "0.5"
   - Nationalization Cost COP: "500000"
   - Exchange Rate USD/COP: "4200"
2. Click "Save Settings" button
3. **Verify** confirmation dialog appears asking to confirm changes
4. **Screenshot**: `21_settings_save_confirmation.png`
5. Click "Confirm" or "Save" to proceed
6. **Verify** success notification appears
7. **Verify** settings are saved (values persist after page refresh)
8. **Screenshot**: `22_settings_saved.png`

### Step 17: Tab State Persistence
1. Click on "Freight Rates" tab
2. Refresh the page (F5)
3. **Verify** page reloads (tab may reset to HS Codes or persist based on implementation)
4. **Screenshot**: `23_tab_state_after_refresh.png`

## Success Criteria

- [ ] Pricing page loads with proper structure (title, three tabs)
- [ ] HS Codes tab displays searchable table
- [ ] HS Code search filters by code or description instantly
- [ ] Create HS Code dialog validates required fields
- [ ] Create HS Code operation adds new code to table
- [ ] Edit HS Code dialog pre-fills with existing data
- [ ] Update HS Code operation reflects changes in table
- [ ] Delete HS Code shows confirmation and removes from table
- [ ] Freight Rates tab displays filterable table
- [ ] Freight Rates filter by origin/destination works
- [ ] Expired freight rates are visually highlighted
- [ ] Create Freight Rate dialog works with date pickers
- [ ] Edit Freight Rate dialog pre-fills with existing data
- [ ] Delete Freight Rate shows confirmation and removes from table
- [ ] Settings tab displays all pricing settings
- [ ] Settings form validates numeric inputs
- [ ] Settings save shows confirmation dialog
- [ ] Settings save updates backend and shows success notification
- [ ] Navigation item "Pricing" appears in sidebar
- [ ] No console errors during test execution

## Notes

- The test creates temporary data (HS code 9999.99.99.99, freight rate from E2E Test Port) which gets deleted during testing
- Settings may have default values seeded in the database
- Expired rate detection: valid_until date < today's date
- Settings keys: default_margin_percentage, inspection_cost_usd, insurance_percentage, nationalization_cost_cop, exchange_rate_usd_cop
- Data testid attributes should be used for reliable element selection
