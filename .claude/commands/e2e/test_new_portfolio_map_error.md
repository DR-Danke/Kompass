# E2E Test: New Portfolio Map Error Fix

## Test Name
New Portfolio Map Error Fix

## User Story
As a Kompass user
I want to create a new portfolio without the page crashing
So that I can build product portfolios for my clients

## Prerequisites
- Application is running and accessible
- User is authenticated with valid credentials

## Test Steps

### Step 1: Navigate to Portfolios Page
1. Log in to the application with valid credentials
2. Navigate to the Portfolios page via sidebar or URL `/portfolios`
3. **Verify**: Page loads with title "Portfolios"
4. **Screenshot**: `01_portfolios_page_loaded.png`

### Step 2: Click Create Portfolio Button
1. Click the "Create Portfolio" button
2. **Verify**: Navigation occurs to the portfolio builder page (`/portfolios/new`)
3. **Verify**: No white screen or crash occurs
4. **Verify**: No console errors about "Cannot read properties of undefined (reading 'map')"
5. **Screenshot**: `02_create_portfolio_clicked.png`

### Step 3: Verify Two-Column Layout
1. **Verify**: The Portfolio Builder page shows a two-column layout
2. **Verify**: Left panel contains the product catalog section
3. **Verify**: Right panel contains the portfolio builder area
4. **Screenshot**: `03_two_column_layout.png`

### Step 4: Verify Product Catalog Search Input
1. Locate the product search input in the left panel
2. **Verify**: Search input with placeholder "Search products..." is visible
3. Click on the search input and type a search term
4. **Verify**: The input accepts text without errors
5. **Screenshot**: `04_product_catalog_search.png`

### Step 5: Verify Category Filter
1. Locate the Category dropdown in the left panel
2. **Verify**: Category dropdown is visible and functional
3. Click on the dropdown
4. **Verify**: "All Categories" option is present
5. **Screenshot**: `05_category_filter.png`

### Step 6: Verify Empty Portfolio State
1. Look at the right panel (portfolio builder area)
2. **Verify**: The portfolio name input is visible and editable
3. **Verify**: The empty portfolio state is displayed (no items yet)
4. **Screenshot**: `06_empty_portfolio_state.png`

### Step 7: Verify Page Stability
1. Wait 3 seconds to ensure no delayed crashes occur
2. **Verify**: Page remains rendered and functional (no white screen)
3. **Verify**: No JavaScript errors in the console
4. **Screenshot**: `07_page_stable.png`

## Success Criteria
- [x] Portfolios list page loads without errors
- [x] Clicking "Create Portfolio" navigates to builder page without crash
- [x] No "Cannot read properties of undefined (reading 'map')" error
- [x] Two-column layout is visible (product catalog left, portfolio builder right)
- [x] Product catalog search input is visible and functional
- [x] Category filter dropdown is visible and functional
- [x] Empty portfolio state is shown correctly
- [x] Page remains stable after loading (no delayed crashes)

## Output Format
```json
{
  "test_name": "New Portfolio Map Error Fix",
  "status": "passed|failed",
  "screenshots": [
    "01_portfolios_page_loaded.png",
    "02_create_portfolio_clicked.png",
    "03_two_column_layout.png",
    "04_product_catalog_search.png",
    "05_category_filter.png",
    "06_empty_portfolio_state.png",
    "07_page_stable.png"
  ],
  "error": null
}
```
