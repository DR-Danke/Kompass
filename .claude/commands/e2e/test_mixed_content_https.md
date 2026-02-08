# E2E Test: Mixed Content HTTPS Validation

## Test Name
Mixed Content HTTPS Validation

## User Story

As a user accessing the application over HTTPS in production
I want all API requests to use HTTPS consistently
So that no mixed content errors block page data from loading

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
6. **Verify** either portfolio cards render with data OR the empty state message is displayed
7. **Screenshot**: `01_portfolios_page_loaded.png`

### Step 2: Verify Portfolios API Requests Succeed
1. Check the browser console for any error messages
2. **Verify** no "Network Error" messages appear in the console
3. **Verify** no "Mixed Content" errors appear in the console
4. **Verify** API requests to `/api/portfolios` return successful responses (status 200)
5. **Screenshot**: `02_portfolios_no_errors.png`

### Step 3: Navigate to Niches Page
1. Navigate to the Niches page via the sidebar navigation or direct URL `/niches`
2. **Verify** the page loads with the title "Niches" visible
3. **Verify** no error alert or snackbar is displayed on the page
4. **Verify** either niche items render with data OR the empty state message is displayed
5. **Screenshot**: `03_niches_page_loaded.png`

### Step 4: Verify Niches API Requests Succeed
1. Check the browser console for any error messages
2. **Verify** no "Network Error" messages appear in the console
3. **Verify** no "Mixed Content" errors appear in the console
4. **Verify** API requests to `/api/niches` return successful responses (status 200)
5. **Screenshot**: `04_niches_no_errors.png`

### Step 5: Verify No Console Errors Across Both Pages
1. Navigate back to the Portfolios page `/portfolios`
2. **Verify** the page loads successfully without errors
3. Check the browser console for any accumulated error messages
4. **Verify** no "Mixed Content" warnings appear in the console across both page navigations
5. **Verify** no "Network Error" messages appear in the console
6. **Screenshot**: `05_no_console_errors.png`

## Success Criteria

- [ ] Portfolios page loads with proper layout and data (or empty state)
- [ ] No "Network Error" messages in the browser console on Portfolios page
- [ ] No "Mixed Content" errors in the browser console on Portfolios page
- [ ] Niches page loads with proper layout and data (or empty state)
- [ ] No "Network Error" messages in the browser console on Niches page
- [ ] No "Mixed Content" errors in the browser console on Niches page
- [ ] API requests to `/api/portfolios` succeed (status 200)
- [ ] API requests to `/api/niches` succeed (status 200)

## Notes

- This test validates the fix for the mixed content HTTPS error caused by FastAPI 307 redirects using `http://` in the Location header behind Render's TLS-terminating proxy
- The fix includes: (1) adding `--proxy-headers --forwarded-allow-ips='*'` to uvicorn, (2) standardizing route trailing slashes to `""`, and (3) removing trailing slashes from frontend API calls
- In local development (same origin, HTTP), the test verifies pages load and data is displayed without errors
- In production (HTTPS), the proxy-headers fix ensures 307 redirect Location headers use `https://`

## Output Format

```json
{
  "test_name": "Mixed Content HTTPS Validation",
  "status": "passed|failed",
  "steps_completed": 5,
  "steps_failed": [],
  "screenshots": [
    "01_portfolios_page_loaded.png",
    "02_portfolios_no_errors.png",
    "03_niches_page_loaded.png",
    "04_niches_no_errors.png",
    "05_no_console_errors.png"
  ],
  "error": null
}
```
