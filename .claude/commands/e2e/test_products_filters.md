# E2E Test: Products Filters Functionality

## Test Name
Products Filters - Category, Supplier, Tags Loading

## User Story
As a Kompass user
I want to use filters on the Products page to narrow down product results
So that I can quickly find products by category, supplier, tags, and other criteria

## Prerequisites
- Application is running and accessible
- User is authenticated with valid credentials
- Backend API is running and responding

## Test Steps

### Step 1: Navigate to Products Page
1. Log in to the application with valid credentials
2. Navigate to the Products page via sidebar or URL `/kompass/products`
3. **Verify**: Page loads without errors (no blank screen)
4. **Verify**: No 422 errors in browser console
5. **Screenshot**: `01_products_page_loaded.png`

### Step 2: Verify Filters Panel Loads
1. Locate the Filters accordion/panel on the page
2. Expand the filters panel if collapsed
3. **Verify**: Filters panel is visible and expanded
4. **Verify**: No JavaScript errors in console related to filters
5. **Screenshot**: `02_filters_panel_expanded.png`

### Step 3: Verify Category Dropdown
1. Locate the Category dropdown/select in the filters
2. Click to open the Category dropdown
3. **Verify**: Dropdown opens without errors
4. **Verify**: Categories are loaded (may show "All Categories" option plus any existing categories)
5. **Verify**: No 422 error on `/api/categories` endpoint
6. **Screenshot**: `03_category_dropdown_open.png`

### Step 4: Verify Supplier Dropdown
1. Locate the Supplier dropdown/select in the filters
2. Click to open the Supplier dropdown
3. **Verify**: Dropdown opens without errors
4. **Verify**: Suppliers are loaded (shows "All Suppliers" option plus any existing suppliers)
5. **Screenshot**: `04_supplier_dropdown_open.png`

### Step 5: Verify Tags Autocomplete
1. Locate the Tags autocomplete input in the filters
2. Click on the Tags input field
3. **Verify**: Input is focusable and functional
4. **Verify**: If tags exist, they appear as options
5. **Verify**: No errors when interacting with tags
6. **Screenshot**: `05_tags_autocomplete.png`

### Step 6: Test Status Filter
1. Locate the Status dropdown
2. Select a status option (e.g., "Active")
3. **Verify**: Filter is applied without errors
4. **Verify**: Products list updates (may show filtered results or empty state)
5. **Screenshot**: `06_status_filter_applied.png`

### Step 7: Test Clear Filters
1. Locate the "Clear Filters" button
2. Click the Clear Filters button
3. **Verify**: All filters are reset
4. **Verify**: Products list shows all products again
5. **Screenshot**: `07_filters_cleared.png`

### Step 8: Verify No Console Errors
1. Open browser developer tools (Console tab)
2. **Verify**: No 422 errors related to `/api/categories/tree`
3. **Verify**: No TypeError related to `Cannot read properties of undefined`
4. **Verify**: API calls to `/api/categories` return 200 status
5. **Screenshot**: `08_console_no_errors.png`

## Success Criteria
- [x] Products page loads without blank screen
- [x] Filters panel expands without errors
- [x] Category dropdown loads and displays categories
- [x] Supplier dropdown loads and displays suppliers
- [x] Tags autocomplete is functional
- [x] Status filter can be applied
- [x] Clear Filters button works
- [x] No 422 errors on `/api/categories/tree` (old broken endpoint)
- [x] API calls to `/api/categories` succeed with 200 status
- [x] No JavaScript TypeError about undefined.filter

## Output Format
```json
{
  "test_name": "Products Filters - Category, Supplier, Tags Loading",
  "status": "passed|failed",
  "screenshots": [
    "01_products_page_loaded.png",
    "02_filters_panel_expanded.png",
    "03_category_dropdown_open.png",
    "04_supplier_dropdown_open.png",
    "05_tags_autocomplete.png",
    "06_status_filter_applied.png",
    "07_filters_cleared.png",
    "08_console_no_errors.png"
  ],
  "error": null
}
```
