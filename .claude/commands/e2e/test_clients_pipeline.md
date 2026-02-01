# E2E Test: Clients Pipeline Page (Kanban)

## User Story

As a Kompass user (admin, manager, or sales representative)
I want to visualize and manage my clients in a Kanban-style pipeline board
So that I can efficiently track client progression through the sales pipeline and quickly update their status via drag-and-drop

## Test Steps

### Step 1: Navigate to Clients Page
1. Open the application at the base URL
2. Login with test credentials (if required)
3. Navigate to `/clients` page using the sidebar navigation or direct URL
4. **Verify** page title "Clients Pipeline" is visible
5. **Verify** "Add Client" button is visible
6. **Verify** search input field is present
7. **Verify** view toggle (Kanban/List) is present with Kanban selected by default
8. **Verify** 6 Kanban columns are visible: Lead, Qualified, Quoting, Negotiating, Won, Lost
9. **Screenshot**: `01_clients_pipeline_loaded.png`

### Step 2: Test Kanban View Structure
1. **Verify** each column has a header with title and count badge
2. **Verify** each column has a distinct background color:
   - Lead: grey (#f5f5f5)
   - Qualified: blue (#e3f2fd)
   - Quoting: amber (#fff8e1)
   - Negotiating: orange (#fff3e0)
   - Won: green (#e8f5e9)
   - Lost: red (#ffebee)
3. **Verify** empty columns show "No clients" message
4. **Screenshot**: `02_kanban_columns.png`

### Step 3: Create New Client
1. Click the "Add Client" button
2. **Verify** dialog opens with title "Add Client"
3. **Verify** form fields are present: Company Name (required), Contact Name, Email, Phone, WhatsApp, Address, City, State, Country, Niche, Status, Source, Project Name, Project Deadline, Incoterm Preference, Notes
4. **Screenshot**: `03_add_client_dialog.png`
5. Fill in the form:
   - Company Name: "E2E Test Company"
   - Contact Name: "John Doe"
   - Email: "john@e2etest.com"
   - Phone: "+1 555 123 4567"
   - WhatsApp: "+1 555 987 6543"
   - Status: "Lead"
   - Source: "Website"
   - Project Name: "Q1 Import Project"
   - Project Deadline: (set to 30 days from today)
   - Notes: "Created by E2E test"
6. Click "Create" button
7. **Verify** dialog closes
8. **Verify** new client card appears in the "Lead" column
9. **Verify** client card shows: Company name, contact name, niche badge (if set), deadline indicator
10. **Screenshot**: `04_client_created.png`

### Step 4: Test Drag-and-Drop Status Change
1. Locate the "E2E Test Company" card in the Lead column
2. Drag the card to the "Qualified" column
3. **Verify** success notification appears
4. **Verify** card now appears in the Qualified column
5. **Verify** card is no longer in the Lead column
6. **Screenshot**: `05_drag_drop_status_change.png`

### Step 5: Test Client Detail Drawer
1. Click on the "E2E Test Company" card
2. **Verify** drawer opens from the right side
3. **Verify** drawer shows client information:
   - Company name and contact name in header
   - Status chip
   - Three tabs: Info, History, Quotations
4. **Verify** Info tab shows: Contact information (email, phone, whatsapp), Location, Project details (name, deadline, niche, incoterm), Notes, Status change form
5. **Screenshot**: `06_detail_drawer_info.png`
6. Click on "History" tab
7. **Verify** status history shows the recent change from Lead to Qualified
8. **Screenshot**: `07_detail_drawer_history.png`
9. Click on "Quotations" tab
10. **Verify** quotation summary is displayed (may show "No quotations" for new client)
11. **Screenshot**: `08_detail_drawer_quotations.png`

### Step 6: Test Status Change from Drawer
1. While drawer is open, find the "Change Status" section in Info tab
2. Select "Quoting" from the status dropdown
3. Enter notes: "Moved to quoting phase"
4. Click "Update Status" button
5. **Verify** success notification appears
6. **Verify** status chip in drawer header updates to "Quoting"
7. **Verify** History tab shows the new status change entry
8. Close the drawer by clicking the X button
9. **Verify** client card is now in the "Quoting" column
10. **Screenshot**: `09_status_change_from_drawer.png`

### Step 7: Test Edit Client
1. Click on the "E2E Test Company" card to open drawer
2. Click the edit (pencil) icon in the drawer header
3. **Verify** edit dialog opens with title "Edit Client"
4. **Verify** form is pre-filled with client data
5. **Screenshot**: `10_edit_client_dialog.png`
6. Modify the Contact Name to "Jane Doe"
7. Click "Update" button
8. **Verify** dialog closes
9. **Verify** success notification appears
10. **Verify** client card updates to show "Jane Doe"
11. **Screenshot**: `11_client_updated.png`

### Step 8: Test Search Functionality
1. Type "E2E" in the search input field
2. Wait for debounced search to complete (300ms)
3. **Verify** only clients matching "E2E" are visible in the Kanban columns
4. **Verify** other clients are filtered out
5. Clear the search input
6. **Verify** all clients are visible again
7. **Screenshot**: `12_search_functionality.png`

### Step 9: Test List View Toggle
1. Click on "List" in the view toggle
2. **Verify** view changes from Kanban to data table
3. **Verify** table has columns: Company, Contact, Email, Phone, Niche, Status, Deadline, Source, Actions
4. **Verify** "E2E Test Company" appears in the table
5. **Screenshot**: `13_list_view.png`
6. Click on a row to open the detail drawer
7. **Verify** drawer opens with client details
8. Close the drawer

### Step 10: Test List View Actions
1. In list view, find the row for "E2E Test Company"
2. Click the view icon in Actions column
3. **Verify** detail drawer opens
4. Close the drawer
5. Click the edit icon in Actions column
6. **Verify** edit dialog opens
7. Click "Cancel" to close
8. **Screenshot**: `14_list_view_actions.png`

### Step 11: Delete Client
1. Switch back to Kanban view (if not already)
2. Locate the "E2E Test Company" card
3. Click on the card to open the drawer
4. Switch to list view
5. Click the delete (trash) icon in Actions column for "E2E Test Company"
6. **Verify** confirmation dialog appears
7. **Verify** confirmation message mentions "E2E Test Company"
8. **Screenshot**: `15_delete_confirmation.png`
9. Click "Delete" button to confirm deletion
10. **Verify** dialog closes
11. **Verify** success notification appears
12. **Verify** client "E2E Test Company" is no longer in the table
13. **Screenshot**: `16_client_deleted.png`

### Step 12: Form Validation
1. Click "Add Client" button
2. Leave the Company Name field empty
3. Click "Create" button
4. **Verify** validation error appears for Company Name field ("Company name is required")
5. **Screenshot**: `17_form_validation_company.png`
6. Enter "Test Company" in Company Name
7. Enter invalid email in Email field (e.g., "invalid-email")
8. Click "Create" button
9. **Verify** validation error appears for email field ("Invalid email address")
10. **Screenshot**: `18_form_validation_email.png`
11. Click "Cancel" to close the dialog

## Success Criteria

- [ ] Clients Pipeline page loads with 6 Kanban columns
- [ ] Each column displays correct title and client count badge
- [ ] Columns have distinct background colors as specified
- [ ] "Add Client" button opens the create form dialog
- [ ] Form validates required fields (Company Name) and email format
- [ ] Create operation adds new client card to correct column
- [ ] Drag-and-drop moves client between columns and updates status via API
- [ ] Status update shows success notification
- [ ] Click on client card opens detail drawer
- [ ] Detail drawer shows all client information in tabs (Info, History, Quotations)
- [ ] Status change from drawer updates status and records history
- [ ] Edit button in drawer opens pre-filled edit form
- [ ] Update operation reflects changes in client card
- [ ] Search filters clients across all columns
- [ ] View toggle switches between Kanban and List modes
- [ ] List view renders data table with all expected columns
- [ ] List view actions (view, edit, delete) work correctly
- [ ] Delete confirmation dialog appears before deletion
- [ ] Delete operation removes client from view
- [ ] No console errors during test execution
- [ ] TypeScript compiles without errors

## Notes

- The test creates a client named "E2E Test Company" which should be cleaned up after test
- Default status is "Lead" (maps to first Kanban column)
- Status options: lead, qualified, quoting, negotiating, won, lost
- Source options: website, referral, cold_call, trade_show, linkedin, other
- Incoterm options: FOB, CIF, EXW, DDP, DAP, CFR, CPT, CIP, DAT, FCA, FAS
- Column colors:
  - Lead: grey.100 (#f5f5f5)
  - Qualified: blue.50 (#e3f2fd)
  - Quoting: amber.50 (#fff8e1)
  - Negotiating: orange.50 (#fff3e0)
  - Won: green.50 (#e8f5e9)
  - Lost: red.50 (#ffebee)
