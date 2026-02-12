# E2E Test: Supplier Products Tab

## User Story

As a sourcing manager
I want to see the list of products associated with a supplier directly within the supplier card
So that I can quickly review a supplier's product catalog without leaving the supplier management interface

## Test Steps

### Step 1: Navigate to Suppliers Page and Open a Supplier
1. Open the application at the base URL
2. Login with test credentials (if required)
3. Navigate to `/suppliers` page using the sidebar navigation or direct URL
4. **Verify** page title "Suppliers" is visible
5. **Verify** supplier data table is visible
6. **Screenshot**: `01_suppliers_page_loaded.png`
7. Click the edit (pencil) icon on the first supplier in the table
8. **Verify** supplier dialog opens
9. **Screenshot**: `02_supplier_dialog_opened.png`

### Step 2: Verify Tab Navigation Shows Three Tabs
1. **Verify** tab navigation is visible with "General", "Certification", and "Products" tabs
2. **Verify** "General" tab is active by default
3. **Verify** all three tabs are clickable
4. **Screenshot**: `03_tabs_visible.png`

### Step 3: Switch to Products Tab
1. Click on the "Products" tab
2. **Verify** "Products" tab becomes active
3. **Verify** products tab content is visible (table or empty state)
4. **Verify** dialog title updates to "Edit Supplier - Products"
5. **Screenshot**: `04_products_tab_active.png`

### Step 4: Verify Products Table Structure
1. If products are loaded:
   - **Verify** table is displayed with column headers: Image, Name, Category, Price, MOQ, Status
   - **Verify** at least one product row is displayed
   - **Verify** product image thumbnail (or placeholder) is visible in the first column
   - **Verify** product name and SKU are displayed
   - **Verify** category name is shown (or dash for uncategorized)
   - **Verify** price is formatted with currency symbol
   - **Verify** MOQ (minimum order quantity) is displayed
   - **Verify** status badge is shown (Active, Inactive, Draft, or Discontinued)
2. **Screenshot**: `05_products_table_data.png`

### Step 5: Verify Pagination Controls
1. If more products exist than the page limit:
   - **Verify** pagination controls are visible below the table
   - **Verify** rows per page selector is available
   - **Verify** navigation arrows (previous/next) are displayed
   - Click next page button if available
   - **Verify** table updates with new page of products
2. If products fit on one page:
   - **Verify** pagination shows correct total count
3. **Screenshot**: `06_pagination_controls.png`

### Step 6: Verify Tab Switching Preserves State
1. Click on "General" tab
2. **Verify** General tab content is shown
3. Click on "Products" tab again
4. **Verify** Products tab reloads and displays correctly
5. Click on "Certification" tab
6. **Verify** Certification tab content is shown
7. **Screenshot**: `07_tab_switching.png`

### Step 7: Verify Empty State for Supplier Without Products
1. Close the current supplier dialog
2. Find and open a supplier that has no products (if available)
3. Switch to the "Products" tab
4. **Verify** empty state message is displayed: "No products associated with this supplier"
5. **Screenshot**: `08_empty_state.png`

### Step 8: Verify Products Tab Hidden for New Supplier
1. Close any open supplier dialog
2. Click "Add Supplier" button
3. **Verify** "Add Supplier" dialog opens
4. **Verify** only "General" tab is shown (no Certification or Products tabs for new suppliers)
5. **Screenshot**: `09_new_supplier_no_tabs.png`
6. Click "Cancel" to close

## Success Criteria

- [ ] Suppliers page loads correctly
- [ ] Supplier dialog opens with tabbed interface in edit mode
- [ ] Three tabs are visible: General, Certification, Products
- [ ] Products tab displays a table with correct columns (Image, Name, Category, Price, MOQ, Status)
- [ ] Products data loads and displays correctly for suppliers with associated products
- [ ] Pagination controls work when there are multiple pages of products
- [ ] Dialog title updates to "Edit Supplier - Products" when Products tab is active
- [ ] Empty state is shown for suppliers with no products
- [ ] Products tab is hidden when creating a new supplier (only General tab shown)
- [ ] Tab switching between General, Certification, and Products works correctly
- [ ] No console errors during test execution

## Notes

- The backend API endpoint `GET /api/suppliers/{id}/products` is expected to return paginated product data
- Products tab is read-only — no edit/delete actions from within the supplier dialog
- Product status badges use the same component as the Products catalog page
- The Products tab uses lazy loading — products are only fetched when the tab is first activated
