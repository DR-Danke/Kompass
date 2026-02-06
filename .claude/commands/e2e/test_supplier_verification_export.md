# E2E Test: Supplier Verification Export to Excel

## User Story

As a sourcing manager
I want to export all supplier verification data to an Excel spreadsheet filtered by my selection criteria
So that I can analyze, share, and report on supplier qualification data outside the application

## Test Steps

### Step 1: Navigate to Suppliers Page
1. Open the application at the base URL
2. Login with test credentials (if required)
3. Navigate to `/suppliers` page using the sidebar navigation or direct URL
4. **Verify** page title "Suppliers" is visible
5. **Verify** "Export Excel" button is visible in the header toolbar area
6. **Screenshot**: `01_suppliers_page_with_export_button.png`

### Step 2: Export Excel with No Filters
1. Ensure no filters are applied (all dropdowns set to default/all)
2. Click the "Export Excel" button
3. **Verify** the button shows a loading state (spinner/disabled)
4. **Verify** no error alerts appear after the export completes
5. **Verify** the button returns to its normal state after export
6. **Screenshot**: `02_export_no_filters.png`

### Step 3: Export Excel with Certification Filter
1. Find the certification status filter dropdown
2. Select a certification filter option (e.g., "Certified (Any)" or "Certified A")
3. Wait for the supplier list to update
4. Click the "Export Excel" button
5. **Verify** the button shows a loading state
6. **Verify** no error alerts appear after the export completes
7. **Verify** the button returns to its normal state
8. **Screenshot**: `03_export_with_certification_filter.png`

### Step 4: Export Excel with Search Filter
1. Clear any existing filters
2. Type a search term in the search input field (e.g., "test")
3. Wait for debounced search to complete
4. Click the "Export Excel" button
5. **Verify** the button shows a loading state
6. **Verify** no error alerts appear after the export completes
7. **Verify** the button returns to its normal state
8. **Screenshot**: `04_export_with_search_filter.png`

### Step 5: Verify Button Placement and Style
1. Clear all filters
2. **Verify** "Export Excel" button is next to the view toggle and "Add Supplier" button
3. **Verify** the button has an icon (download icon)
4. **Verify** the button uses an outlined style (visually distinct from "Add Supplier")
5. **Screenshot**: `05_button_placement_and_style.png`

## Success Criteria

- [ ] "Export Excel" button is visible on the Suppliers page header
- [ ] Button has a download icon and outlined style
- [ ] Clicking the button triggers a download (no error alerts)
- [ ] Button shows loading state during export
- [ ] Button returns to normal state after export completes
- [ ] Export works with no filters applied
- [ ] Export works with certification filter applied
- [ ] Export works with search filter applied
- [ ] No console errors during the export flow

## Notes

- The export downloads an .xlsx file named `supplier_verification_export_YYYY-MM-DD.xlsx`
- The button should be disabled while the export is in progress
- Export respects current filter state (status, certification, pipeline, search)
