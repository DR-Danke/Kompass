# E2E Test: Niches Configuration Page

## User Story

As a Kompass admin or manager
I want to manage niches (client type classifications) through a dedicated configuration page
So that I can categorize clients by business type for targeted portfolio management and better organization

## Test Steps

### Step 1: Navigate to Niches Page
1. Open the application at the base URL
2. Login with test credentials (if required)
3. Navigate to `/niches` page using the sidebar navigation or direct URL
4. **Verify** page title "Niches" is visible
5. **Verify** "Add Niche" button is visible
6. **Verify** niche cards are displayed (if niches exist) or empty state message is shown
7. **Screenshot**: `01_niches_page_loaded.png`

### Step 2: Verify Page Structure
1. **Verify** each niche card shows:
   - Niche name
   - Description (or "No description" placeholder)
   - Client count badge with people icon
   - Edit button (pencil icon)
   - Delete button (trash icon)
2. **Verify** default niches are present (Constructoras, Estudios de Arquitectura, Desarrolladores, Hoteles, Operadores Rentas Cortas, Retailers)
3. **Screenshot**: `02_niche_cards_structure.png`

### Step 3: Create New Niche
1. Click the "Add Niche" button
2. **Verify** dialog opens with title "Add Niche"
3. **Verify** form fields are present: Name (required), Description (optional)
4. **Screenshot**: `03_add_niche_dialog.png`
5. Fill in the form:
   - Name: "E2E Test Niche"
   - Description: "Test niche created by E2E test"
6. Click "Create" button
7. **Verify** dialog closes
8. **Verify** new niche card appears with name "E2E Test Niche"
9. **Verify** new niche shows client count of 0
10. **Screenshot**: `04_niche_created.png`

### Step 4: Form Validation
1. Click "Add Niche" button
2. Leave the Name field empty
3. Click "Create" button
4. **Verify** validation error appears for Name field ("Name is required")
5. **Screenshot**: `05_form_validation_error.png`
6. Click "Cancel" to close the dialog

### Step 5: Edit Existing Niche
1. Find the card for "E2E Test Niche"
2. Click the edit (pencil) icon
3. **Verify** dialog opens with title "Edit Niche"
4. **Verify** form is pre-filled with niche data (Name: "E2E Test Niche", Description: "Test niche created by E2E test")
5. **Screenshot**: `06_edit_niche_dialog.png`
6. Modify the Name field to "E2E Test Niche Updated"
7. Modify the Description field to "Updated description"
8. Click "Update" button
9. **Verify** dialog closes
10. **Verify** niche name is updated on the card to "E2E Test Niche Updated"
11. **Screenshot**: `07_niche_updated.png`

### Step 6: Delete Niche (Success Case)
1. Find the card for "E2E Test Niche Updated"
2. Click the delete (trash) icon
3. **Verify** confirmation dialog appears with title "Delete Niche"
4. **Verify** confirmation message mentions the niche name
5. **Screenshot**: `08_delete_confirmation.png`
6. Click "Delete" button to confirm deletion
7. **Verify** dialog closes
8. **Verify** niche "E2E Test Niche Updated" is no longer displayed
9. **Screenshot**: `09_niche_deleted.png`

### Step 7: Delete Blocked Validation (Niche with Clients)
1. Find a niche that has clients associated (check for non-zero client count)
2. If no niches have clients, create a client with a niche assignment first, then return to this test
3. Click the delete (trash) icon for the niche with clients
4. **Verify** confirmation dialog appears
5. Click "Delete" button
6. **Verify** error message appears: "This niche cannot be deleted because it has associated clients. Please reassign the clients first."
7. **Screenshot**: `10_delete_blocked_error.png`
8. Click "Cancel" to close the dialog
9. **Verify** niche still exists in the list

### Step 8: Client Count Display
1. Navigate to `/clients` and create a new client with a niche assignment (if not already done)
2. Navigate back to `/niches`
3. **Verify** the assigned niche shows an updated client count
4. **Screenshot**: `11_client_count_updated.png`

## Success Criteria

- [ ] Niches page loads with proper structure (title, add button, cards grid)
- [ ] Default niches are displayed (Constructoras, Estudios de Arquitectura, etc.)
- [ ] Each niche card shows name, description, client count badge
- [ ] Add Niche dialog opens and displays form fields
- [ ] Form validation works for required Name field
- [ ] Create operation adds new niche card to the grid
- [ ] Edit dialog pre-fills with existing niche data
- [ ] Update operation reflects changes on the card
- [ ] Delete confirmation dialog displays before deletion
- [ ] Delete operation removes niche card from grid (when allowed)
- [ ] Delete blocked message shown when attempting to delete niche with clients
- [ ] Client count badge displays correct number of associated clients
- [ ] No console errors during test execution

## Notes

- The test creates a niche named "E2E Test Niche" which gets deleted during testing
- Default niches seeded in database: Constructoras, Estudios de Arquitectura, Desarrolladores, Hoteles, Operadores Rentas Cortas, Retailers
- Niches are displayed as cards in a responsive grid (3 columns on desktop, 2 on tablet, 1 on mobile)
- Client count is displayed as a chip with a people icon
- Backend returns 409 Conflict when attempting to delete a niche that has associated clients
