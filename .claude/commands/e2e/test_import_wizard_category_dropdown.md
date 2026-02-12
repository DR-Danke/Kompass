# E2E Test: Import Wizard Category Dropdown

## Overview
End-to-end test specification for the Category Dropdown and Unit of Measure column added to the Import Wizard.

## Prerequisites
- Frontend server running at http://localhost:5173
- Backend server running at http://localhost:8000
- Test user account with admin/manager/user role
- At least one supplier in the database
- At least one active category in the database (preferably with hierarchical children)
- Sample test files (PDF, Excel, or images) for extraction

## Test Scenarios

### Scenario 1: Category Dropdown Renders in Confirm Step
1. Log in as a valid user
2. Navigate to the Import Wizard via sidebar
3. Upload a valid file and complete extraction (reach Step 3 - Review Products)
4. Select at least one product and click "Continue to Import"
5. **Verify**: Import Wizard is at Step 4 (Confirm Import)
6. **Verify**: Supplier dropdown is visible
7. **Verify**: Category Autocomplete dropdown renders below the Supplier dropdown with label "Category"
8. **Verify**: Helper text reads "Optional — assign all products to this category"
9. **Screenshot**: `01_category_dropdown_visible.png`

### Scenario 2: Categories Load with Hierarchical Path Labels
1. From the Confirm step, click on the Category Autocomplete dropdown
2. **Verify**: Categories load and display as options in the dropdown
3. **Verify**: Categories with parents display hierarchical path labels using " > " separator (e.g., "BAÑOS > Griferías")
4. **Verify**: Root-level categories display without any prefix
5. **Screenshot**: `02_category_options_hierarchical.png`

### Scenario 3: Select and Clear Category
1. From the Category Autocomplete dropdown, select a category
2. **Verify**: The selected category appears in the Autocomplete input field
3. Click the clear button (X) on the Autocomplete to deselect the category
4. **Verify**: The Category field is empty again
5. **Verify**: The "Import Products" button remains functional (category is optional)
6. **Screenshot**: `03_category_select_and_clear.png`

### Scenario 4: Import Works Without Category (Optional Field)
1. On the Confirm step, select a Supplier but do NOT select a Category
2. Click "Import Products"
3. **Verify**: Import completes successfully (success dialog appears)
4. **Verify**: No errors related to missing category
5. **Screenshot**: `04_import_without_category.png`

### Scenario 5: Unit Column in Extracted Products Table
1. Start a new import, upload files and complete extraction
2. On the Review step (Step 3), examine the extracted products table
3. **Verify**: The table header includes a "Unit" column between "MOQ" and "Confidence"
4. **Verify**: Products with `unit_of_measure` data display the value in the Unit column
5. **Verify**: Products without `unit_of_measure` data display an em dash (—) in the Unit column
6. **Screenshot**: `05_unit_column_visible.png`

## Success Criteria
- [ ] Category Autocomplete dropdown is visible in the Confirm step (Step 4)
- [ ] Category dropdown renders below the Supplier dropdown
- [ ] Categories load from the API and display in the dropdown
- [ ] Categories show hierarchical path labels with " > " separator
- [ ] A category can be selected and cleared
- [ ] Import works without selecting a category (optional field)
- [ ] "Unit" column appears in the extracted products review table
- [ ] Products without unit_of_measure display an em dash (—)
- [ ] No regressions in existing Import Wizard functionality

## Notes
- The Category field is optional — the import should succeed with or without a category selected
- The Unit column is read-only (not editable like Name, SKU, Price, MOQ)
- Categories are loaded when the user reaches Step 4 (Confirm Import)
