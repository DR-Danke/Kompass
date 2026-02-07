# E2E Test: Delete Supplier (Hard Delete)

## User Story

As an admin or manager user
I want to permanently delete suppliers and all their associated data
So that I can clean up test data and remove suppliers that are no longer relevant from the database

## Test Steps

### Step 1: Navigate to Suppliers Page
1. Open the application at the base URL
2. Login with test credentials (if required)
3. Navigate to `/suppliers` page using the sidebar navigation or direct URL
4. **Verify** page title "Suppliers" is visible
5. **Verify** data table with suppliers is visible
6. **Screenshot**: `01_suppliers_page_loaded.png`

### Step 2: Create a Test Supplier for Deletion
1. Click the "Add Supplier" button
2. **Verify** dialog opens with title "Add Supplier"
3. Fill in the form:
   - Name: "E2E Delete Test Supplier"
   - Code: "E2E-DEL-001"
   - Status: "Active"
   - Country: "CN"
   - City: "Shanghai"
   - Contact Name: "Delete Test"
   - Contact Email: "delete@e2etest.com"
4. Click "Create" button
5. **Verify** dialog closes
6. **Verify** new supplier "E2E Delete Test Supplier" appears in the table
7. **Screenshot**: `02_test_supplier_created.png`

### Step 3: Open Delete Confirmation Dialog
1. Find the row for "E2E Delete Test Supplier" in the table
2. Click the delete (trash) icon in the Actions column
3. **Verify** confirmation dialog appears with title "Permanently Delete Supplier"
4. **Verify** a warning alert is shown indicating the action is irreversible
5. **Verify** the dialog mentions the supplier name "E2E Delete Test Supplier"
6. **Verify** the dialog shows counts of associated data that will be deleted (products, audit reports)
7. **Verify** the "Delete Permanently" button is present (red/error color)
8. **Verify** a "Cancel" button is present
9. **Screenshot**: `03_delete_confirmation_dialog.png`

### Step 4: Cancel Deletion
1. Click "Cancel" button in the confirmation dialog
2. **Verify** the dialog closes
3. **Verify** the supplier "E2E Delete Test Supplier" is still visible in the table
4. **Screenshot**: `04_deletion_cancelled.png`

### Step 5: Confirm Permanent Deletion
1. Click the delete (trash) icon again for "E2E Delete Test Supplier"
2. **Verify** confirmation dialog appears again with permanent deletion warning
3. Click "Delete Permanently" button
4. **Verify** dialog closes
5. **Verify** supplier "E2E Delete Test Supplier" is no longer visible in the table
6. **Screenshot**: `05_supplier_deleted.png`

### Step 6: Verify Supplier is Fully Removed
1. Type "E2E Delete Test" in the search input field
2. Wait for search to complete
3. **Verify** no results are found for the deleted supplier
4. Clear the search input
5. **Screenshot**: `06_supplier_not_in_search.png`

## Success Criteria

- [ ] Suppliers page loads with proper structure
- [ ] Test supplier can be created successfully
- [ ] Delete confirmation dialog shows "Permanently Delete Supplier" title
- [ ] Warning alert about irreversible action is displayed
- [ ] Dialog shows counts of associated data to be deleted
- [ ] Cancel button closes dialog without deleting
- [ ] "Delete Permanently" button performs the hard delete
- [ ] Supplier is removed from the table after deletion
- [ ] Supplier does not appear in search results after deletion
- [ ] No console errors during test execution

## Notes

- This test creates a supplier named "E2E Delete Test Supplier" which is deleted as part of the test
- Only admin and manager roles can delete suppliers; regular users should see a 403 error
- The hard delete permanently removes the supplier and all associated data (products, audits, images, tags)
- Quotation items referencing deleted products will have their product_id set to NULL
