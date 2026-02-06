# E2E Test: Supplier Certification Data in Excel Export

## User Story

As a sourcing manager
I want the Excel export to include all extracted audit/certification data for each supplier
So that I can analyze supplier qualification details in a spreadsheet without missing information

## Test Steps

### Step 1: Navigate to Suppliers Page
1. Open the application at the base URL
2. Login with test credentials (if required)
3. Navigate to `/suppliers` page using the sidebar navigation or direct URL
4. **Verify** page title "Suppliers" is visible
5. **Verify** supplier data table is populated with at least one supplier
6. **Screenshot**: `01_suppliers_page_loaded.png`

### Step 2: Open a Supplier and Verify Certification Data On Screen
1. Click the edit (pencil) icon on a supplier that has audit data
2. **Verify** supplier dialog opens
3. Click on the "Certification" tab
4. **Verify** "Certification" tab becomes active
5. **Verify** audit/extraction data is displayed on screen (supplier type, employee count, certifications, positive/negative points, etc.)
6. Note the values shown for: supplier type, employee count, factory area, certifications
7. **Screenshot**: `02_certification_data_on_screen.png`

### Step 3: Return to Suppliers List
1. Close the supplier dialog
2. **Verify** the Suppliers list page is visible again
3. **Screenshot**: `03_suppliers_list_returned.png`

### Step 4: Export Excel and Verify No Errors
1. Click the "Export Excel" button
2. **Verify** the button shows a loading state (spinner/disabled)
3. **Verify** no error alerts appear after the export completes
4. **Verify** the button returns to its normal state after export
5. **Screenshot**: `04_export_completed.png`

### Step 5: Verify Export Contains Audit Data (API Level)
1. Open browser DevTools Network tab before clicking export (or inspect the previous export request)
2. **Verify** the export API call (`GET /api/suppliers/export/excel`) returns status 200
3. **Verify** the response content-type is `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
4. **Verify** the file size is larger than a header-only file (indicating data rows with content)
5. **Screenshot**: `05_network_response_verified.png`

## Success Criteria

- [ ] Suppliers page loads with supplier data visible
- [ ] At least one supplier has audit/certification data visible in the Certification tab
- [ ] Certification tab shows supplier type, employee count, certifications, and other extracted data
- [ ] Excel export button triggers download without errors
- [ ] Export API call returns HTTP 200
- [ ] Exported file contains data (non-trivial file size)
- [ ] No console errors during the export flow

## Notes

- This test validates the fix for issue #105 where audit data was missing from the Excel export
- The root cause was a SQL JOIN on `latest_audit_id` which is only set after classification
- The fix changes the JOIN to use a subquery finding the latest audit by `supplier_id`
- The export downloads an .xlsx file named `supplier_verification_export_YYYY-MM-DD.xlsx`
- Audit columns include: supplier type, employee count, factory area, production lines, markets served, certifications, positive/negative points, products verified, audit date, inspector name, classification
