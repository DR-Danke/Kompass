# E2E Test: Supplier WeChat ID Field

## User Story

As a Kompass user managing Chinese suppliers
I want to view and edit WeChat ID directly on the supplier form
So that I can store and reference supplier WeChat contact information for messaging

## Test Steps

### Step 1: Navigate to Suppliers Page
1. Open the application at the base URL
2. Login with test credentials (if required)
3. Navigate to `/suppliers` page using the sidebar navigation or direct URL
4. **Verify** page title "Suppliers" is visible
5. **Verify** "Add Supplier" button is visible
6. **Screenshot**: `01_suppliers_page_loaded.png`

### Step 2: Verify WeChat ID Field in Add Supplier Form
1. Click the "Add Supplier" button
2. **Verify** dialog opens with title "Add Supplier"
3. **Verify** "WeChat ID" field is present in the form (after Contact Phone)
4. **Verify** "WeChat ID" field has placeholder text "ID de WeChat del proveedor"
5. **Screenshot**: `02_wechat_id_field_visible.png`

### Step 3: Create Supplier with WeChat ID
1. Fill in the form:
   - Name: "E2E WeChat Test Supplier"
   - Code: "WECHAT-001"
   - Status: "Active"
   - Country: "CN"
   - City: "Shenzhen"
   - Contact Name: "Zhang Wei"
   - Contact Email: "zhang@wechattest.com"
   - Contact Phone: "+86 138 0000 1234"
   - WeChat ID: "test_wechat_123"
   - Notes: "Created by WeChat ID E2E test"
2. Click "Create" button
3. **Verify** dialog closes
4. **Verify** new supplier "E2E WeChat Test Supplier" appears in the table
5. **Screenshot**: `03_supplier_with_wechat_created.png`

### Step 4: Verify WeChat ID Persists in Edit Form
1. Find the row for "E2E WeChat Test Supplier" in the table
2. Click the edit (pencil) icon in the Actions column
3. **Verify** dialog opens with title "Edit Supplier"
4. **Verify** "WeChat ID" field is pre-filled with "test_wechat_123"
5. **Screenshot**: `04_wechat_id_prefilled.png`

### Step 5: Update WeChat ID
1. Clear the "WeChat ID" field
2. Type "updated_wechat_456" in the "WeChat ID" field
3. Click "Update" button
4. **Verify** dialog closes
5. **Screenshot**: `05_wechat_id_updated.png`

### Step 6: Verify Updated WeChat ID Persists
1. Find the row for "E2E WeChat Test Supplier" in the table
2. Click the edit (pencil) icon in the Actions column
3. **Verify** "WeChat ID" field is pre-filled with "updated_wechat_456"
4. **Screenshot**: `06_wechat_id_update_persisted.png`
5. Click "Cancel" to close the dialog

### Step 7: Clean Up - Delete Test Supplier
1. Find the row for "E2E WeChat Test Supplier" in the table
2. Click the delete (trash) icon in the Actions column
3. **Verify** confirmation dialog appears
4. Click "Delete" or "Confirm" button to confirm deletion
5. **Verify** supplier "E2E WeChat Test Supplier" is no longer in the table
6. **Screenshot**: `07_test_supplier_deleted.png`

## Success Criteria

- [ ] WeChat ID field appears on the supplier create form
- [ ] WeChat ID field appears on the supplier edit form
- [ ] Creating a supplier with a WeChat ID stores it correctly
- [ ] Editing a supplier pre-fills the existing WeChat ID value
- [ ] Updating WeChat ID to a new value persists correctly
- [ ] Test supplier is cleaned up after test execution
- [ ] No console errors during test execution

## Notes

- The WeChat ID field should appear after Contact Phone in the form
- WeChat ID is optional — leaving it empty should not cause errors
- Maximum length is 100 characters
- The field label is "WeChat ID" (English, as it's a proper noun)
- Placeholder text is in Spanish: "ID de WeChat del proveedor"
