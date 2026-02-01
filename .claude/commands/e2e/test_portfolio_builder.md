# E2E Test: Portfolio Builder Page

## Test Name
Portfolio Builder Page

## User Story
As a Kompass user (admin, manager, or regular user)
I want to create and manage curated product portfolios using an interactive builder interface
So that I can efficiently build personalized product collections for clients and share them

## Prerequisites
- Application is running and accessible
- User is authenticated with valid credentials
- Database has at least a few sample products and niches
- At least one portfolio exists (or will be created during test)

## Test Steps

### Step 1: Navigate to Portfolios List Page
1. Log in to the application with valid credentials
2. Navigate to the Portfolios page via sidebar or URL `/portfolios`
3. **Verify**: Page loads with title "Portfolios"
4. **Verify**: Portfolio grid is displayed (or empty state if no portfolios)
5. **Screenshot**: `01_portfolios_page_loaded.png`

### Step 2: Test Create New Portfolio
1. Click the "Create Portfolio" button
2. **Verify**: Navigation occurs to portfolio builder page
3. **Verify**: Builder page shows two-column layout
4. **Verify**: Left panel shows product catalog with search
5. **Verify**: Right panel shows empty portfolio area
6. **Screenshot**: `02_new_portfolio_builder.png`

### Step 3: Edit Portfolio Metadata
1. Locate the portfolio name input in the top bar
2. Enter a new name (e.g., "Test Portfolio E2E")
3. **Verify**: Name input updates
4. If niches exist, select a niche from the dropdown
5. **Verify**: Niche selection is applied
6. Toggle the status switch (active/inactive)
7. **Verify**: Status toggle changes state
8. **Screenshot**: `03_portfolio_metadata_edited.png`

### Step 4: Add Products from Catalog
1. In the left panel, locate the product search input
2. Search for a product (if products exist)
3. **Verify**: Products filter based on search term
4. Click on a product in the catalog to add it to the portfolio
5. **Verify**: Product appears in the right panel (portfolio builder)
6. Add 2-3 more products by clicking them
7. **Verify**: All products appear in the portfolio with correct order
8. **Screenshot**: `04_products_added_to_portfolio.png`

### Step 5: Test Drag-and-Drop Reorder
1. Locate a portfolio item in the right panel
2. Drag the item to a different position
3. **Verify**: Item reorders and position updates
4. **Screenshot**: `05_portfolio_reordered.png`

### Step 6: Add Curator Notes
1. Locate a portfolio item with notes input
2. Enter curator notes for the item (e.g., "Best seller for this niche")
3. **Verify**: Notes input accepts text
4. **Screenshot**: `06_curator_notes_added.png`

### Step 7: Remove Product from Portfolio
1. Locate the remove button on a portfolio item
2. Click the remove button
3. **Verify**: Product is removed from portfolio
4. **Verify**: Item count updates
5. **Screenshot**: `07_product_removed.png`

### Step 8: Save Portfolio
1. Click the "Save" button in the top bar
2. **Verify**: Save operation completes (success notification)
3. **Verify**: Portfolio data is persisted
4. **Screenshot**: `08_portfolio_saved.png`

### Step 9: Test Copy Share Link
1. Click the "Copy Share Link" button
2. **Verify**: Link is copied to clipboard (toast notification)
3. **Screenshot**: `09_share_link_copied.png`

### Step 10: Test Preview PDF
1. Click the "Preview PDF" button
2. **Verify**: PDF generation starts (loading indicator shown)
3. **Verify**: PDF opens in new tab or downloads
4. **Screenshot**: `10_pdf_preview.png`

### Step 11: Return to Portfolios List
1. Navigate back to `/portfolios`
2. **Verify**: Newly created portfolio appears in the grid
3. **Verify**: Portfolio card shows: name, niche, product count, status badge
4. **Screenshot**: `11_portfolio_in_list.png`

### Step 12: Test Portfolio Card Actions
1. Locate the newly created portfolio card
2. Click the "Open" action
3. **Verify**: Navigates to builder page with portfolio loaded
4. Navigate back to list
5. Click the "Duplicate" action
6. **Verify**: Duplicate dialog appears
7. Close the dialog
8. **Screenshot**: `12_portfolio_card_actions.png`

### Step 13: Test Delete Portfolio
1. Click the "Delete" action on a portfolio card
2. **Verify**: Delete confirmation dialog appears
3. Cancel the deletion
4. **Verify**: Portfolio remains in list
5. **Screenshot**: `13_delete_confirmation.png`

### Step 14: Test Filters on List Page
1. If niches exist, filter by niche
2. **Verify**: Only portfolios with selected niche are shown
3. Filter by status (active/inactive)
4. **Verify**: Portfolios filter by status
5. Use search input
6. **Verify**: Portfolios filter by name
7. Clear all filters
8. **Screenshot**: `14_filters_applied.png`

## Success Criteria
- [x] Portfolios list page loads without errors
- [x] Create Portfolio navigates to builder
- [x] Portfolio builder shows two-column layout (40%/60%)
- [x] Portfolio metadata (name, niche, status) is editable
- [x] Products can be added from mini catalog
- [x] Products can be reordered via drag-and-drop
- [x] Curator notes can be added per item
- [x] Products can be removed from portfolio
- [x] Save operation persists changes
- [x] Share link can be copied
- [x] PDF preview generates correctly
- [x] Portfolio cards show correct information
- [x] Card actions (Open, Duplicate, Delete) work
- [x] Filters on list page work correctly
- [x] Loading states are shown during operations
- [x] Error states display appropriate messages

## Output Format
```json
{
  "test_name": "Portfolio Builder Page",
  "status": "passed|failed",
  "screenshots": [
    "01_portfolios_page_loaded.png",
    "02_new_portfolio_builder.png",
    "03_portfolio_metadata_edited.png",
    "04_products_added_to_portfolio.png",
    "05_portfolio_reordered.png",
    "06_curator_notes_added.png",
    "07_product_removed.png",
    "08_portfolio_saved.png",
    "09_share_link_copied.png",
    "10_pdf_preview.png",
    "11_portfolio_in_list.png",
    "12_portfolio_card_actions.png",
    "13_delete_confirmation.png",
    "14_filters_applied.png"
  ],
  "error": null
}
```
