# E2E Test: Suppliers Management Page

## User Story

As a Kompass user (admin, manager, or standard user)
I want to manage suppliers through a dedicated page with list, create, edit, and delete capabilities
So that I can maintain an organized supplier database for my import/export operations

## Test Steps

### Step 1: Navigate to Suppliers Page
1. Open the application at the base URL
2. Login with test credentials (if required)
3. Navigate to `/suppliers` page using the sidebar navigation or direct URL
4. **Verify** page title "Suppliers" is visible
5. **Verify** "Add Supplier" button is visible
6. **Verify** search input field is present
7. **Verify** status filter dropdown is present
8. **Verify** data table with headers (Name, Country, Contact Email, Contact Phone, Status, Actions) is visible
9. **Screenshot**: `01_suppliers_page_loaded.png`

### Step 2: Test Search Functionality
1. Type "test" in the search input field
2. Wait for debounced search to complete (300ms)
3. **Verify** table updates with filtered results (or empty state if no matches)
4. Clear the search input
5. **Verify** table shows all suppliers again
6. **Screenshot**: `02_search_functionality.png`

### Step 3: Test Status Filter
1. Click on the status filter dropdown
2. Select "Active" status
3. **Verify** table shows only active suppliers (or empty state)
4. Select "All Statuses" to reset filter
5. **Verify** table shows all suppliers
6. **Screenshot**: `03_status_filter.png`

### Step 4: Create New Supplier
1. Click the "Add Supplier" button
2. **Verify** dialog opens with title "Add Supplier"
3. **Verify** form fields are present: Name, Code, Status, Country, City, Contact Name, Contact Email, Contact Phone, Address, Website, Notes
4. **Screenshot**: `04_add_supplier_dialog.png`
5. Fill in the form:
   - Name: "E2E Test Supplier"
   - Code: "E2E-001"
   - Status: "Active"
   - Country: "CN"
   - City: "Shanghai"
   - Contact Name: "John Doe"
   - Contact Email: "john@e2etest.com"
   - Contact Phone: "+86 123 4567 8900"
   - Website: "https://e2etest.com"
   - Notes: "Created by E2E test"
6. Click "Create" button
7. **Verify** dialog closes
8. **Verify** new supplier appears in the table with name "E2E Test Supplier"
9. **Screenshot**: `05_supplier_created.png`

### Step 5: Edit Existing Supplier
1. Find the row for "E2E Test Supplier" in the table
2. Click the edit (pencil) icon in the Actions column
3. **Verify** dialog opens with title "Edit Supplier"
4. **Verify** form is pre-filled with supplier data
5. **Screenshot**: `06_edit_supplier_dialog.png`
6. Modify the Name field to "E2E Test Supplier Updated"
7. Click "Update" button
8. **Verify** dialog closes
9. **Verify** supplier name is updated in the table to "E2E Test Supplier Updated"
10. **Screenshot**: `07_supplier_updated.png`

### Step 6: Delete Supplier
1. Find the row for "E2E Test Supplier Updated" in the table
2. Click the delete (trash) icon in the Actions column
3. **Verify** confirmation dialog appears
4. **Verify** confirmation message mentions the supplier name
5. **Screenshot**: `08_delete_confirmation.png`
6. Click "Delete" or "Confirm" button to confirm deletion
7. **Verify** dialog closes
8. **Verify** supplier "E2E Test Supplier Updated" is no longer in the table
9. **Screenshot**: `09_supplier_deleted.png`

### Step 7: Form Validation
1. Click "Add Supplier" button
2. Leave the Name field empty
3. Clear the Country field (remove default value)
4. Click "Create" button
5. **Verify** validation error appears for Name field ("Name is required")
6. **Verify** validation error appears for Country field ("Country is required")
7. **Screenshot**: `10_form_validation_errors.png`
8. Enter invalid email in Contact Email field (e.g., "invalid-email")
9. Click "Create" button
10. **Verify** validation error appears for email field
11. Click "Cancel" to close the dialog

### Step 8: Pagination (if applicable)
1. If more than 10 suppliers exist, **Verify** pagination controls are visible
2. If pagination exists, click "Next page" button
3. **Verify** table shows next page of results
4. **Screenshot**: `11_pagination.png`

## Success Criteria

- [ ] Suppliers page loads with proper structure (title, table, filters, add button)
- [ ] Search functionality filters the table in real-time
- [ ] Status filter correctly filters suppliers by status
- [ ] Add Supplier dialog opens and displays all form fields
- [ ] Form validation works for required fields and email format
- [ ] Create operation adds new supplier to table
- [ ] Edit dialog pre-fills with existing supplier data
- [ ] Update operation reflects changes in table
- [ ] Delete confirmation dialog displays before deletion
- [ ] Delete operation removes supplier from table
- [ ] Pagination works correctly (if applicable)
- [ ] No console errors during test execution

## Notes

- The test creates a supplier named "E2E Test Supplier" which should be cleaned up after test
- Default country is "CN" (China)
- Status options: active, inactive, pending_review
- Table columns: Name, Country, Contact Email, Contact Phone, Status, Actions
