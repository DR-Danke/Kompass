# E2E Test: Portfolios Network Error Fix

## Test Name
Portfolios Network Error Fix Validation

## User Story

As a user
I want to navigate to the Portfolios page without encountering network errors
So that I can manage portfolios and filter by niches as expected

## Prerequisites
- Application running at configured URL
- User authenticated with admin or manager role
- Backend API available at /api

## Test Steps

### Step 1: Navigate to Portfolios Page
1. Open the application at the base URL
2. Login with admin test credentials (if required)
3. Navigate to the Portfolios page via the sidebar navigation or direct URL `/portfolios`
4. **Verify** the page loads with the title "Portfolios" visible
5. **Verify** no error alert or snackbar is displayed on the page
6. **Screenshot**: `01_portfolios_page_loaded.png`

### Step 2: Verify Portfolios Section Renders
1. **Verify** the Portfolios section is visible on the page
2. **Verify** either portfolio cards render with data OR the empty state message is displayed
3. **Verify** the "Create Portfolio" or "New Portfolio" button is visible and clickable
4. **Screenshot**: `02_portfolios_section.png`

### Step 3: Verify Niche Filter Loads
1. **Verify** the niche filter dropdown is visible on the page
2. **Verify** the niche filter dropdown is populated with options OR is present in its default state
3. **Verify** no error messages appear related to loading niches
4. **Screenshot**: `03_niche_filter.png`

### Step 4: Verify No Network Errors
1. Check the browser console for any error messages
2. **Verify** no "Network Error" messages appear in the console
3. **Verify** no "Mixed Content" errors appear in the console
4. **Verify** API requests to `/api/niches/` return successful responses (status 200)
5. **Verify** API requests to `/api/portfolios/` return successful responses (status 200)
6. **Screenshot**: `04_no_console_errors.png`

### Step 5: Verify Page Refresh Works
1. Refresh the page or click the refresh button if available
2. **Verify** the portfolios reload without errors
3. **Verify** the niche filter reloads without errors
4. **Verify** no error alerts appear after refreshing
5. **Screenshot**: `05_after_refresh.png`

## Success Criteria

- [ ] Portfolios page loads with proper layout
- [ ] Portfolios section renders (portfolio cards or empty state)
- [ ] Niche filter dropdown loads with options (or is present)
- [ ] No "Network Error" messages in the browser console
- [ ] No error alerts or snackbars displayed on the page
- [ ] API requests to `/api/niches/` succeed (status 200)
- [ ] API requests to `/api/portfolios/` succeed (status 200)
- [ ] Page refresh works without errors

## Notes

- This test validates the fix for GitHub Issue #115 (Network error in the Portfolios Module)
- The root cause was missing trailing slashes on `/niches` and `/portfolios` API calls, causing 307 redirects that fail in cross-origin deployments
- In local development (same origin), the test verifies the page loads and data is displayed without errors
- This is the same class of bug fixed in PR #112 for the `/users` endpoints and issue #113 for the `/categories` and `/tags` endpoints

## Output Format

```json
{
  "test_name": "Portfolios Network Error Fix Validation",
  "status": "passed|failed",
  "steps_completed": 5,
  "steps_failed": [],
  "screenshots": [
    "01_portfolios_page_loaded.png",
    "02_portfolios_section.png",
    "03_niche_filter.png",
    "04_no_console_errors.png",
    "05_after_refresh.png"
  ],
  "error": null
}
```
