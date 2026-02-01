# E2E Test: Products Catalog Page

## Test Name
Products Catalog Page (Biblia General)

## User Story
As a Kompass user (admin, manager, or regular user)
I want to browse, search, filter, and manage products in a catalog interface
So that I can efficiently find, view, and maintain product information in the Biblia General

## Prerequisites
- Application is running and accessible
- User is authenticated with valid credentials
- Database has at least a few sample products, suppliers, and categories

## Test Steps

### Step 1: Navigate to Products Page
1. Log in to the application with valid credentials
2. Navigate to the Products page (Biblia General) via sidebar or URL `/kompass/products`
3. **Verify**: Page loads with title "Biblia General"
4. **Verify**: Products grid/table is displayed
5. **Screenshot**: `01_products_page_loaded.png`

### Step 2: Test View Toggle
1. Locate the view toggle buttons (grid/table)
2. If currently in grid view, click the table view button
3. **Verify**: View switches to table mode with columns (Name, SKU, Supplier, Price, Status, etc.)
4. Click the grid view button
5. **Verify**: View switches back to grid mode with product cards
6. **Screenshot**: `02_view_toggle_grid.png`
7. **Screenshot**: `03_view_toggle_table.png`

### Step 3: Test Search Functionality
1. Locate the search input field
2. Enter a search term (e.g., part of a product name or SKU if products exist)
3. Wait for search results to update
4. **Verify**: Products list filters based on search term
5. Clear the search input
6. **Verify**: Full product list is restored
7. **Screenshot**: `04_search_results.png`

### Step 4: Test Filters
1. Open/expand the filters panel
2. If suppliers exist, select a supplier from the dropdown
3. **Verify**: Products list filters to show only products from selected supplier
4. Clear the supplier filter
5. Select a status filter (e.g., "active")
6. **Verify**: Products list shows only products with selected status
7. Click "Clear Filters" button
8. **Verify**: All filters are reset and full product list is shown
9. **Screenshot**: `05_filters_applied.png`

### Step 5: Test Add Product Flow
1. Click the "Add Product" button
2. **Verify**: Product form dialog/modal opens
3. **Verify**: Form shows step indicator (Basic Info, Pricing, Details, Images, Tags)
4. Fill in required fields on Basic Info step (name, supplier)
5. Click "Next" to proceed to Pricing step
6. **Verify**: Pricing fields are shown
7. Click "Cancel" or close the form
8. **Verify**: Form closes without creating product
9. **Screenshot**: `06_add_product_form.png`

### Step 6: Test Product Card/Row Actions
1. If products exist, locate a product in the list
2. Find the edit action (icon or button)
3. Click the edit action
4. **Verify**: Edit form opens with product data pre-filled
5. Close the edit form
6. **Screenshot**: `07_edit_product_form.png`

### Step 7: Test Pagination
1. If more than one page of products exists:
   - Locate pagination controls at the bottom
   - Click "Next" or page number 2
   - **Verify**: Page changes and different products are shown
   - Click "Previous" or page number 1
   - **Verify**: Returns to first page
2. If page size selector exists:
   - Change the page size (e.g., from 10 to 25)
   - **Verify**: More products are shown per page
3. **Screenshot**: `08_pagination.png`

### Step 8: Test Empty State
1. Apply filters that would result in no products (if possible)
2. **Verify**: "No products found" or similar message is displayed
3. Clear filters
4. **Screenshot**: `09_empty_state.png` (if applicable)

## Success Criteria
- [x] Products page loads without errors
- [x] View toggle switches between grid and table views
- [x] Search filters products by name/SKU
- [x] Supplier and status filters work correctly
- [x] Add Product form opens and shows multi-step wizard
- [x] Edit action opens form with pre-filled data
- [x] Pagination controls navigate between pages
- [x] Loading states are shown during data fetching
- [x] Error states display appropriate messages

## Output Format
```json
{
  "test_name": "Products Catalog Page",
  "status": "passed|failed",
  "screenshots": [
    "01_products_page_loaded.png",
    "02_view_toggle_grid.png",
    "03_view_toggle_table.png",
    "04_search_results.png",
    "05_filters_applied.png",
    "06_add_product_form.png",
    "07_edit_product_form.png",
    "08_pagination.png"
  ],
  "error": null
}
```
