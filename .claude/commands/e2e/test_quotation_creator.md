# E2E Test: Quotation Creator Page

## Test Name
Quotation Creator Page

## User Story
As a Kompass user (admin, manager, or sales representative)
I want to create professional quotations by selecting clients, adding products from the catalog, and see live pricing calculations
So that I can quickly generate accurate quotations for clients with full cost visibility including tariffs, freight, and margins

## Prerequisites
- Application is running and accessible
- User is authenticated with valid credentials
- Database has at least a few sample clients, products, and suppliers

## Test Steps

### Step 1: Navigate to Quotations List Page
1. Log in to the application with valid credentials
2. Navigate to the Quotations page via sidebar or URL `/quotations`
3. **Verify**: Page loads with title "Quotations"
4. **Verify**: Quotations table is displayed (may be empty)
5. **Verify**: "New Quotation" button is visible
6. **Screenshot**: `01_quotations_list_page.png`

### Step 2: Test Quotations List Filters
1. If quotations exist, test the status filter dropdown
2. Select a status (e.g., "Draft")
3. **Verify**: Table filters to show only quotations with selected status
4. Clear the status filter
5. Test the date range filter if available
6. **Verify**: Filters work correctly
7. **Screenshot**: `02_quotations_list_filtered.png`

### Step 3: Navigate to Create New Quotation
1. Click the "New Quotation" button
2. **Verify**: Navigates to `/quotations/new`
3. **Verify**: Quotation creator page loads with sections visible
4. **Verify**: Page shows Client Selection section
5. **Verify**: Page shows Product Selection section
6. **Verify**: Page shows Pricing Panel (sidebar)
7. **Screenshot**: `03_quotation_creator_empty.png`

### Step 4: Test Client Selection
1. Locate the Client Selection section
2. Click on the client search/autocomplete field
3. Type a search term to filter clients
4. **Verify**: Autocomplete shows matching clients
5. Select a client from the dropdown
6. **Verify**: Client is selected and displayed
7. **Verify**: Client details (company name, contact info) are shown
8. **Screenshot**: `04_client_selected.png`

### Step 5: Test Product Selection - Catalog Mode
1. Locate the Product Selection section
2. Ensure "Catalog" tab is selected
3. Browse available products
4. Use search or filters to find a specific product
5. Click "Add to Quote" on a product
6. **Verify**: Product appears in the Line Items table
7. **Verify**: Pricing panel updates
8. **Screenshot**: `05_product_added_from_catalog.png`

### Step 6: Test Product Selection - Portfolio Mode
1. Click the "Portfolio" tab in Product Selection
2. If portfolios exist, select one from the dropdown
3. **Verify**: Products from the portfolio are shown
4. Add a product from the portfolio to the quote
5. **Verify**: Product appears in Line Items table
6. **Screenshot**: `06_product_added_from_portfolio.png`

### Step 7: Test Line Items Table
1. Locate the Line Items table
2. **Verify**: Table shows product name, SKU, quantity, unit price, HS code, line total
3. Edit the quantity field for a product
4. **Verify**: Quantity updates
5. **Verify**: Line total recalculates
6. **Verify**: Pricing panel updates with new totals
7. **Screenshot**: `07_line_items_quantity_edit.png`

### Step 8: Test Price Override
1. Click on the unit price field for a line item
2. Enter a custom price (override the default)
3. **Verify**: Price override is indicated visually
4. **Verify**: Line total and pricing panel update
5. **Screenshot**: `08_price_override.png`

### Step 9: Test Line Item Removal
1. Click the remove/delete button on a line item
2. **Verify**: Item is removed from the table
3. **Verify**: Pricing panel updates
4. **Screenshot**: `09_line_item_removed.png`

### Step 10: Test Pricing Panel
1. Add at least 2 products to have meaningful pricing
2. **Verify**: Pricing panel shows:
   - Subtotal FOB USD
   - Tariffs breakdown
   - International freight
   - National freight
   - Inspection
   - Insurance
   - Nationalization
   - Margin %
   - **Total COP** (highlighted)
3. **Verify**: Total COP is prominently displayed
4. **Screenshot**: `10_pricing_panel_complete.png`

### Step 11: Test Calculate Button
1. Click the "Calculate" button in the actions bar
2. **Verify**: Loading state is shown while calculating
3. **Verify**: Pricing panel refreshes with calculated values
4. **Screenshot**: `11_after_calculate.png`

### Step 12: Test Save Draft
1. Ensure client and products are selected
2. Click "Save Draft" button
3. **Verify**: Quotation is saved (success message shown)
4. **Verify**: Page shows quotation number or redirects to edit mode
5. **Screenshot**: `12_draft_saved.png`

### Step 13: Test PDF Preview
1. With a saved quotation, click "Preview PDF" button
2. **Verify**: PDF opens in new tab or modal
3. **Verify**: PDF contains quotation details
4. **Screenshot**: `13_pdf_preview.png`

### Step 14: Test Share Link
1. Click "Copy Share Link" button
2. **Verify**: Share link is copied to clipboard (snackbar confirmation)
3. **Screenshot**: `14_share_link_copied.png`

### Step 15: Test Edit Existing Quotation
1. Navigate back to quotations list
2. Click edit on a quotation
3. **Verify**: Quotation creator loads with existing data
4. **Verify**: Client is pre-selected
5. **Verify**: Line items are pre-populated
6. **Verify**: Pricing panel shows correct values
7. **Screenshot**: `15_edit_existing_quotation.png`

## Success Criteria
- [x] Quotations list page loads without errors
- [x] Status and date filters work correctly
- [x] New quotation page loads with all sections
- [x] Client selection autocomplete works
- [x] Products can be added from catalog
- [x] Products can be added from portfolio
- [x] Line items table displays correctly
- [x] Quantity editing triggers price recalculation
- [x] Price override works and is visually indicated
- [x] Line items can be removed
- [x] Pricing panel shows complete cost breakdown
- [x] Calculate button triggers pricing calculation
- [x] Save Draft creates quotation
- [x] PDF preview generates document
- [x] Share link copies to clipboard
- [x] Edit mode loads existing quotation data
- [x] Loading and error states display appropriately

## Output Format
```json
{
  "test_name": "Quotation Creator Page",
  "status": "passed|failed",
  "screenshots": [
    "01_quotations_list_page.png",
    "02_quotations_list_filtered.png",
    "03_quotation_creator_empty.png",
    "04_client_selected.png",
    "05_product_added_from_catalog.png",
    "06_product_added_from_portfolio.png",
    "07_line_items_quantity_edit.png",
    "08_price_override.png",
    "09_line_item_removed.png",
    "10_pricing_panel_complete.png",
    "11_after_calculate.png",
    "12_draft_saved.png",
    "13_pdf_preview.png",
    "14_share_link_copied.png",
    "15_edit_existing_quotation.png"
  ],
  "error": null
}
```
