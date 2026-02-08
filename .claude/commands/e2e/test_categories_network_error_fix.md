# E2E Test: Categories Network Error Fix

## Test Name
Categories Network Error Fix Validation

## User Story

As a user
I want to navigate to the Categories & Tags page without encountering network errors
So that I can manage categories and tags as expected

## Prerequisites
- Application running at configured URL
- User authenticated with admin or manager role
- Backend API available at /api

## Test Steps

### Step 1: Navigate to Categories Page
1. Open the application at the base URL
2. Login with admin test credentials (if required)
3. Navigate to the Categories & Tags page via the sidebar navigation or direct URL `/categories`
4. **Verify** the page loads with the title "Categories & Tags" visible
5. **Verify** no error alert or snackbar is displayed on the page
6. **Screenshot**: `01_categories_page_loaded.png`

### Step 2: Verify Categories Section Renders
1. **Verify** the Categories section is visible on the page
2. **Verify** either the category tree renders with data OR the empty state message "No categories yet" is displayed
3. **Verify** the "Add Root Category" button is visible and clickable
4. **Screenshot**: `02_categories_section.png`

### Step 3: Verify Tags Section Renders
1. **Verify** the Tags section is visible on the page
2. **Verify** either tag chips render with data OR the empty state message "No tags yet" is displayed
3. **Verify** the "Add Tag" button is visible and clickable
4. **Screenshot**: `03_tags_section.png`

### Step 4: Verify No Network Errors
1. Check the browser console for any error messages
2. **Verify** no "Network Error" messages appear in the console
3. **Verify** no "Mixed Content" errors appear in the console
4. **Verify** API requests to `/api/categories/` return successful responses (status 200)
5. **Verify** API requests to `/api/tags/` return successful responses (status 200)
6. **Screenshot**: `04_no_console_errors.png`

### Step 5: Verify Page Refresh Works
1. Click the refresh icon in the Categories section header
2. **Verify** the categories reload without errors
3. Click the refresh icon in the Tags section header
4. **Verify** the tags reload without errors
5. **Verify** no error alerts appear after refreshing
6. **Screenshot**: `05_after_refresh.png`

## Success Criteria

- [ ] Categories page loads with proper layout (Categories and Tags sections)
- [ ] Categories section renders (tree data or empty state)
- [ ] Tags section renders (tag chips or empty state)
- [ ] No "Network Error" messages in the browser console
- [ ] No error alerts or snackbars displayed on the page
- [ ] API requests to `/api/categories/` succeed (status 200)
- [ ] API requests to `/api/tags/` succeed (status 200)
- [ ] Page refresh works without errors

## Notes

- This test validates the fix for GitHub Issue #113 (Network error in the Categories Module)
- The root cause was missing trailing slashes on `/categories` and `/tags` API calls, causing 307 redirects that fail in cross-origin deployments
- In local development (same origin), the test verifies the page loads and data is displayed without errors
- This is the same class of bug fixed in PR #112 for the `/users` endpoints

## Output Format

```json
{
  "test_name": "Categories Network Error Fix Validation",
  "status": "passed|failed",
  "steps_completed": 5,
  "steps_failed": [],
  "screenshots": [
    "01_categories_page_loaded.png",
    "02_categories_section.png",
    "03_tags_section.png",
    "04_no_console_errors.png",
    "05_after_refresh.png"
  ],
  "error": null
}
```
