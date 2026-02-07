# E2E Test: Users Administration Page

## User Story

As an admin user
I want to access the Users administration page and see all registered users
So that I can manage user accounts without encountering mixed content or network errors

## Test Steps

### Step 1: Navigate to Users Page
1. Open the application at the base URL
2. Login with admin test credentials (if required)
3. Navigate to `/users` page using the sidebar navigation or direct URL
4. **Verify** page title "Users" or "User Management" is visible
5. **Verify** the page loads without any console errors related to mixed content or network failures
6. **Screenshot**: `01_users_page_loaded.png`

### Step 2: Verify Users Table Structure
1. **Verify** a data table is displayed on the page
2. **Verify** table headers include: Name, Email, Role, Status, Actions
3. **Verify** the table contains at least one row of user data
4. **Screenshot**: `02_users_table_structure.png`

### Step 3: Verify API Requests Succeed
1. Check browser console for any error messages
2. **Verify** no "Mixed Content" errors appear in the console
3. **Verify** no "Network Error" messages appear in the console
4. **Verify** API requests to `/api/users/` return successful responses (status 200)
5. **Screenshot**: `03_no_console_errors.png`

## Success Criteria

- [ ] Users page loads with proper structure (title, table)
- [ ] Users table displays headers: Name, Email, Role, Status, Actions
- [ ] At least one user row is displayed in the table
- [ ] No mixed content errors in the browser console
- [ ] No network errors in the browser console
- [ ] API requests to `/api/users/` succeed without being blocked

## Notes

- This test validates the fix for GitHub Issue #110 (Mixed Content HTTPS error)
- The primary goal is to confirm that API requests from HTTPS pages use HTTPS protocol
- In local development (HTTP), the test simply verifies the page loads and data is displayed
- The Users page requires admin role access
