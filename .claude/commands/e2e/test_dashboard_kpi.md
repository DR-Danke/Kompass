# E2E Test: Dashboard KPI Charts

## Test Name
Dashboard KPI Charts

## User Story
As a Kompass user (admin, manager, or sales representative)
I want to see an overview dashboard with KPIs, charts, and recent activity
So that I can quickly understand the current state of my business and take immediate actions without navigating to individual pages

## Prerequisites
- Application is running and accessible
- User is authenticated with valid credentials
- Database may have sample products, quotations, clients, and suppliers for meaningful KPI display

## Test Steps

### Step 1: Navigate to Dashboard
1. Log in to the application with valid credentials
2. Navigate to the Dashboard page via sidebar or URL `/`
3. **Verify**: Page loads with title "Dashboard"
4. **Verify**: Welcome message shows user's name/email
5. **Screenshot**: `01_dashboard_page.png`

### Step 2: Verify Quick Actions Section
1. Locate the Quick Actions section at the top
2. **Verify**: "Add Product" button is visible
3. **Verify**: "Create Quotation" button is visible
4. **Verify**: "Import Catalog" button is visible
5. **Screenshot**: `02_quick_actions.png`

### Step 3: Test Quick Action - Add Product
1. Click the "Add Product" button
2. **Verify**: Navigates to `/products` page
3. Navigate back to Dashboard
4. **Screenshot**: `03_quick_action_add_product.png`

### Step 4: Test Quick Action - Create Quotation
1. Click the "Create Quotation" button
2. **Verify**: Navigates to `/quotations/new` page
3. Navigate back to Dashboard
4. **Screenshot**: `04_quick_action_create_quotation.png`

### Step 5: Test Quick Action - Import Catalog
1. Click the "Import Catalog" button
2. **Verify**: Navigates to `/import-wizard` page
3. Navigate back to Dashboard
4. **Screenshot**: `05_quick_action_import_catalog.png`

### Step 6: Verify KPI Cards Row
1. Locate the KPI cards row
2. **Verify**: "Total Products" card is visible with a numeric value
3. **Verify**: "Added This Month" card is visible with a numeric value
4. **Verify**: "Active Suppliers" card is visible with a numeric value
5. **Verify**: "Quotations This Week" card is visible with a numeric value
6. **Verify**: "Pipeline Value" card is visible with a currency value
7. **Screenshot**: `06_kpi_cards.png`

### Step 7: Verify Charts Section
1. Scroll to the charts section
2. **Verify**: "Quotations by Status" pie chart is visible
3. **Verify**: "Quotation Trend (30 Days)" line chart is visible
4. **Verify**: "Top Quoted Products" bar chart is visible
5. **Screenshot**: `07_charts_section.png`

### Step 8: Verify Quotations by Status Chart
1. Locate the "Quotations by Status" pie chart
2. **Verify**: Chart has legend with status colors
3. **Verify**: If quotations exist, pie slices are displayed with labels
4. **Verify**: If no quotations, "No quotations yet" message is shown
5. **Verify**: Hovering over slices shows tooltip with count
6. **Screenshot**: `08_quotations_by_status_chart.png`

### Step 9: Verify Quotation Trend Chart
1. Locate the "Quotation Trend (30 Days)" line chart
2. **Verify**: X-axis shows dates
3. **Verify**: Y-axis shows count values
4. **Verify**: "Sent" and "Accepted" lines are shown in legend
5. **Verify**: Hovering over points shows tooltip
6. **Screenshot**: `09_quotation_trend_chart.png`

### Step 10: Verify Top Products Chart
1. Locate the "Top Quoted Products" bar chart
2. **Verify**: Y-axis shows product names (truncated if long)
3. **Verify**: X-axis shows quote counts
4. **Verify**: If no quoted products, "No quoted products yet" message is shown
5. **Screenshot**: `10_top_products_chart.png`

### Step 11: Verify Activity Feed Section
1. Scroll to the Activity Feed section
2. **Verify**: Activity Feed card is visible
3. **Verify**: Three tabs are shown: "Products", "Quotations", "Clients"
4. **Verify**: "Products" tab is selected by default
5. **Screenshot**: `11_activity_feed.png`

### Step 12: Test Activity Feed - Products Tab
1. Ensure "Products" tab is selected
2. **Verify**: Recent products are listed (or empty state message)
3. **Verify**: Each product shows name, SKU, supplier, and date
4. Click on a product item
5. **Verify**: Navigates to `/products` page
6. Navigate back to Dashboard
7. **Screenshot**: `12_activity_products_tab.png`

### Step 13: Test Activity Feed - Quotations Tab
1. Click on the "Quotations" tab
2. **Verify**: Recent quotations are listed (or empty state message)
3. **Verify**: Each quotation shows number, client name, status chip, and date
4. Click on a quotation item
5. **Verify**: Navigates to `/quotations/{id}` page
6. Navigate back to Dashboard
7. **Screenshot**: `13_activity_quotations_tab.png`

### Step 14: Test Activity Feed - Clients Tab
1. Click on the "Clients" tab
2. **Verify**: Recent clients are listed (or empty state message)
3. **Verify**: Each client shows company name, status chip, and date
4. Click on a client item
5. **Verify**: Navigates to `/pipeline` page
6. Navigate back to Dashboard
7. **Screenshot**: `14_activity_clients_tab.png`

### Step 15: Test Refresh Button
1. Locate the "Refresh" button in the header
2. Click the Refresh button
3. **Verify**: Loading state is shown briefly
4. **Verify**: Dashboard data reloads
5. **Screenshot**: `15_after_refresh.png`

### Step 16: Test Error State
1. If possible, simulate network error
2. **Verify**: Error message is displayed
3. **Verify**: Retry button is available
4. **Screenshot**: `16_error_state.png`

## Success Criteria
- [x] Dashboard page loads without errors
- [x] Welcome message shows authenticated user's name/email
- [x] Quick Actions section displays all three action buttons
- [x] Quick action "Add Product" navigates to products page
- [x] Quick action "Create Quotation" navigates to /quotations/new
- [x] Quick action "Import Catalog" navigates to /import-wizard
- [x] All 5 KPI cards display with correct formatting
- [x] Pipeline Value shows formatted currency value
- [x] Quotations by Status pie chart renders with legend
- [x] Quotation Trend line chart renders with axes and lines
- [x] Top Quoted Products bar chart renders
- [x] Activity Feed section shows with tabs
- [x] Activity feed tabs switch correctly between categories
- [x] Clicking activity items navigates to appropriate pages
- [x] Refresh button triggers data reload
- [x] Loading states display while data is fetching
- [x] Empty states handled gracefully when no data exists
- [x] Error states display with retry option if API fails

## Output Format
```json
{
  "test_name": "Dashboard KPI Charts",
  "status": "passed|failed",
  "screenshots": [
    "01_dashboard_page.png",
    "02_quick_actions.png",
    "03_quick_action_add_product.png",
    "04_quick_action_create_quotation.png",
    "05_quick_action_import_catalog.png",
    "06_kpi_cards.png",
    "07_charts_section.png",
    "08_quotations_by_status_chart.png",
    "09_quotation_trend_chart.png",
    "10_top_products_chart.png",
    "11_activity_feed.png",
    "12_activity_products_tab.png",
    "13_activity_quotations_tab.png",
    "14_activity_clients_tab.png",
    "15_after_refresh.png",
    "16_error_state.png"
  ],
  "error": null
}
```
