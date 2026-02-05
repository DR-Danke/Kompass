# E2E Test: Suppliers Pipeline Page (Kanban)

## User Story

As a Kompass user (admin or manager)
I want to visualize and manage suppliers in a Kanban-style pipeline board
So that I can efficiently track supplier progression through the qualification process and quickly update their pipeline status via drag-and-drop

## Test Steps

### Step 1: Navigate to Suppliers Page
1. Open the application at the base URL
2. Login with test credentials (if required)
3. Navigate to `/suppliers` page using the sidebar navigation or direct URL
4. **Verify** page title "Suppliers" is visible
5. **Verify** "Add Supplier" button is visible
6. **Verify** search input field is present
7. **Verify** view toggle (List/Kanban) is present with List selected by default
8. **Verify** status and pipeline filter dropdowns are visible in list view
9. **Screenshot**: `01_suppliers_page_loaded.png`

### Step 2: Switch to Kanban View
1. Click the Kanban icon in the view toggle
2. **Verify** view changes from data table to Kanban board
3. **Verify** 6 Kanban columns are visible: Contacted, Potential, Quoted, Certified, Active, Inactive
4. **Verify** each column has a header with title and count badge
5. **Screenshot**: `02_kanban_view.png`

### Step 3: Test Kanban Column Structure
1. **Verify** each column has a distinct background color:
   - Contacted: grey (#f5f5f5)
   - Potential: blue (#e3f2fd)
   - Quoted: amber (#fff8e1)
   - Certified: green (#e8f5e9)
   - Active: green (#c8e6c9)
   - Inactive: red (#ffebee)
2. **Verify** empty columns show "No suppliers" message
3. **Screenshot**: `03_kanban_columns.png`

### Step 4: Create New Supplier
1. Click the "Add Supplier" button
2. **Verify** dialog opens with title "Add Supplier" or "Create Supplier"
3. **Verify** form fields are present: Name (required), Code, Status, Contact Name, Email, Phone, Address, City, Country, Website, Notes
4. **Screenshot**: `04_add_supplier_dialog.png`
5. Fill in the form:
   - Name: "E2E Test Supplier Co."
   - Code: "E2E-SUP-001"
   - Status: "Active"
   - Contact Name: "Wang Wei"
   - Email: "wang@e2etestsupplier.com"
   - Phone: "+86 123 4567 8901"
   - Country: "China"
   - City: "Shenzhen"
   - Notes: "Created by E2E test"
6. Click "Create" or "Save" button
7. **Verify** dialog closes
8. **Verify** success notification appears
9. **Verify** new supplier appears in the list (if in list view) or Kanban board (if in Kanban view)
10. **Screenshot**: `05_supplier_created.png`

### Step 5: Find Supplier in Kanban View
1. Switch to Kanban view (if not already)
2. **Verify** "E2E Test Supplier Co." card appears in the "Contacted" column (default pipeline status)
3. **Verify** supplier card shows: Name, Code, Contact Name, Country, Product count badge
4. **Screenshot**: `06_supplier_in_kanban.png`

### Step 6: Test Drag-and-Drop Status Change
1. Locate the "E2E Test Supplier Co." card in the Contacted column
2. Drag the card to the "Potential" column
3. **Verify** loading overlay appears briefly
4. **Verify** card now appears in the Potential column
5. **Verify** card is no longer in the Contacted column
6. **Verify** column count badges update correctly
7. **Screenshot**: `07_drag_drop_status_change.png`

### Step 7: Test Supplier Card Click
1. Click on the "E2E Test Supplier Co." card
2. **Verify** edit dialog opens (or detail drawer opens)
3. **Verify** dialog/drawer shows supplier information pre-filled
4. **Screenshot**: `08_supplier_card_click.png`
5. Close the dialog/drawer without making changes

### Step 8: Test Search Functionality in Kanban View
1. Type "E2E" in the search input field
2. Wait for debounced search to complete (300ms)
3. **Verify** only suppliers matching "E2E" are visible in the Kanban columns
4. **Verify** other suppliers are filtered out
5. **Screenshot**: `09_search_kanban.png`
6. Clear the search input
7. **Verify** all suppliers are visible again

### Step 9: Test Drag to Another Status
1. Drag "E2E Test Supplier Co." from Potential to "Quoted"
2. **Verify** card moves to Quoted column
3. **Screenshot**: `10_quoted_status.png`
4. Drag card to "Certified" column
5. **Verify** card moves to Certified column
6. **Screenshot**: `11_certified_status.png`

### Step 10: Switch to List View
1. Click on List icon in the view toggle
2. **Verify** view changes from Kanban to data table
3. **Verify** table has columns: Name, Country, Contact Email, Contact Phone, Status, Pipeline, Actions
4. **Verify** "E2E Test Supplier Co." appears in the table
5. **Verify** Pipeline column shows "Certified" badge
6. **Screenshot**: `12_list_view.png`

### Step 11: Test Pipeline Filter in List View
1. Click on the Pipeline filter dropdown
2. Select "Certified"
3. **Verify** only suppliers with "Certified" pipeline status are shown
4. **Verify** "E2E Test Supplier Co." is visible
5. **Screenshot**: `13_pipeline_filter.png`
6. Reset filter to "All Pipeline"
7. **Verify** all suppliers are visible again

### Step 12: Test Status Filter in List View
1. Click on the Status filter dropdown
2. Select "Active"
3. **Verify** only suppliers with "Active" status are shown
4. **Verify** "E2E Test Supplier Co." is visible (since we set status to Active)
5. **Screenshot**: `14_status_filter.png`
6. Reset filter to "All Statuses"

### Step 13: Test Edit Supplier from List View
1. Find "E2E Test Supplier Co." row in the table
2. Click the edit (pencil) icon in Actions column
3. **Verify** edit dialog opens with pre-filled data
4. Modify the Contact Name to "Li Ming"
5. Click "Update" or "Save" button
6. **Verify** dialog closes
7. **Verify** success notification appears
8. **Verify** table updates to show "Li Ming" as contact (if displayed)
9. **Screenshot**: `15_supplier_updated.png`

### Step 14: Delete Supplier
1. Find "E2E Test Supplier Co." row in the table
2. Click the delete (trash) icon in Actions column
3. **Verify** confirmation dialog appears
4. **Verify** confirmation message mentions "E2E Test Supplier Co."
5. **Screenshot**: `16_delete_confirmation.png`
6. Click "Delete" button to confirm
7. **Verify** dialog closes
8. **Verify** success notification appears
9. **Verify** supplier "E2E Test Supplier Co." is no longer in the table
10. **Screenshot**: `17_supplier_deleted.png`

### Step 15: Verify Deletion in Kanban View
1. Switch to Kanban view
2. **Verify** "E2E Test Supplier Co." card is not present in any column
3. **Screenshot**: `18_kanban_after_delete.png`

### Step 16: Form Validation
1. Click "Add Supplier" button
2. Leave the Name field empty
3. Click "Create" or "Save" button
4. **Verify** validation error appears for Name field ("Name is required" or similar)
5. **Screenshot**: `19_form_validation_name.png`
6. Enter "Test Supplier" in Name field
7. Enter invalid email in Email field (e.g., "invalid-email")
8. Click "Create" or "Save" button
9. **Verify** validation error appears for email field ("Invalid email" or similar)
10. **Screenshot**: `20_form_validation_email.png`
11. Click "Cancel" to close the dialog

## Success Criteria

- [ ] Suppliers page loads with list view by default
- [ ] View toggle switches between List and Kanban views
- [ ] Kanban view displays 6 columns with correct titles
- [ ] Each column displays correct supplier count badge
- [ ] Columns have distinct background colors as specified
- [ ] "Add Supplier" button opens the create form dialog
- [ ] Form validates required fields (Name) and email format
- [ ] Create operation adds new supplier to list/Kanban
- [ ] Drag-and-drop moves supplier between columns and updates pipeline status via API
- [ ] Pipeline status update shows loading indicator during API call
- [ ] Click on supplier card opens edit dialog
- [ ] Search filters suppliers in Kanban view across all columns
- [ ] List view renders data table with all expected columns including Pipeline column
- [ ] Pipeline filter in list view correctly filters by pipeline status
- [ ] Status filter in list view correctly filters by supplier status
- [ ] Edit operation reflects changes in list/Kanban
- [ ] Delete confirmation dialog appears before deletion
- [ ] Delete operation removes supplier from view
- [ ] No console errors during test execution
- [ ] TypeScript compiles without errors

## Notes

- The test creates a supplier named "E2E Test Supplier Co." which should be cleaned up after test
- Default pipeline status for new suppliers is "Contacted"
- Pipeline status options: contacted, potential, quoted, certified, active, inactive
- Supplier status options: active, inactive, pending_review
- Column colors match PipelineStatusBadge colors:
  - Contacted: grey (#f5f5f5)
  - Potential: blue (#e3f2fd)
  - Quoted: amber (#fff8e1)
  - Certified: green (#e8f5e9)
  - Active: green (#c8e6c9)
  - Inactive: red (#ffebee)
- Supplier cards display: Name, Code (if present), Contact Name, Country, Product count badge, Certification badge (if certified)
