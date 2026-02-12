# E2E Test: Category Dropdown in Import Wizard

## Overview
End-to-end test specification for the Category Dropdown feature in the Import Wizard confirm step and the Unit of Measure column in the review table.

## Prerequisites
- Frontend server running at http://localhost:5173
- Backend server running at http://localhost:8000
- Test user account with admin/manager/user role
- Sample test files (PDF, Excel, or images)
- At least one category exists in the database
- At least one supplier exists in the database

## User Story
As a Kompass user importing products from supplier catalogs, I want to assign a category to all imported products during the import confirmation step, so that products are automatically categorized upon import without needing to manually categorize each one afterward.

## Test Steps

### Scenario 1: Navigate to Import Wizard and Upload Files
1. Log in as a valid user
2. Navigate to the Import Wizard via sidebar (click "Import Wizard" nav item)
3. **Verify**: Import Wizard page loads with Stepper at Step 1 (Upload Files)
4. Upload a valid test file (PDF, Excel, or image)
5. Click "Start Extraction" button
6. Wait for extraction to complete and auto-advance to Step 3 (Review Products)
7. **Screenshot**: `01_review_step_with_products.png`

### Scenario 2: Verify Unit Column in Review Table
1. On the Review step (Step 3), verify the extracted products table is displayed
2. **Verify**: Table headers include "Unit" column between "MOQ" and "Confidence"
3. **Verify**: Unit column displays values when available, or "—" when not
4. **Screenshot**: `02_unit_column_visible.png`

### Scenario 3: Navigate to Confirm Step and Verify Category Dropdown
1. Click "Continue to Import" button to advance to Step 4 (Confirm Import)
2. **Verify**: Confirm step displays import summary card
3. **Verify**: Supplier dropdown is displayed and required
4. **Verify**: Category Autocomplete dropdown renders below Supplier dropdown
5. **Verify**: Category dropdown has label "Category" and helper text "Optional — assign all products to this category"
6. **Screenshot**: `03_confirm_step_with_category_dropdown.png`

### Scenario 4: Verify Category Dropdown Options
1. Click on the Category Autocomplete dropdown to open it
2. **Verify**: Categories load and display in the dropdown options
3. **Verify**: Categories display with hierarchical path notation (e.g., "PARENT > Child")
4. **Verify**: The dropdown supports type-ahead search/filtering
5. **Screenshot**: `04_category_dropdown_options.png`

### Scenario 5: Import Without Category (Optional Selection)
1. Select a supplier from the Supplier dropdown
2. Do NOT select a category
3. **Verify**: "Import Products" button is enabled (category is optional)
4. **Screenshot**: `05_import_without_category.png`

### Scenario 6: Import With Category Selected
1. Select a category from the Category dropdown
2. **Verify**: Selected category displays in the Autocomplete field
3. Select a supplier from the Supplier dropdown
4. Click "Import Products" button
5. **Verify**: Success dialog appears with import count
6. **Screenshot**: `06_import_with_category_success.png`

### Scenario 7: Clear Category Selection
1. Start a new import flow (upload files, wait for extraction, proceed to confirm step)
2. Select a category from the dropdown
3. Clear the category selection using the clear (X) button in the Autocomplete
4. **Verify**: Category dropdown returns to empty state
5. **Verify**: Import can proceed without category
6. **Screenshot**: `07_category_cleared.png`

## Success Criteria
- [ ] Unit column appears in the extracted products review table (Step 3)
- [ ] Unit column shows value when available, "—" when not
- [ ] Category Autocomplete dropdown renders in confirm step below Supplier dropdown
- [ ] Categories load from the API when entering confirm step
- [ ] Categories display with hierarchical path notation (e.g., "PARENT > Child")
- [ ] Category selection is optional — import works without selecting a category
- [ ] Selected category is displayed correctly in the Autocomplete field
- [ ] Import completes successfully with a category selected
- [ ] Category can be cleared after selection
- [ ] Type-ahead search filtering works in the category dropdown

## Error Cases to Test
1. No categories exist in the database: Autocomplete shows empty list, import still works
2. Network error loading categories: Import still works without category selection

## Notes
- The Category dropdown uses MUI Autocomplete for type-ahead search capability
- Categories are loaded as a tree from the API and flattened with hierarchical path labels
- The `category_id` is optional in the backend `ConfirmImportRequestDTO`
- Only active categories (`is_active: true`) are shown in the dropdown
