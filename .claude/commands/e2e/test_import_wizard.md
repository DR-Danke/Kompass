# E2E Test: Import Wizard

## Overview
End-to-end test specification for the Product Import Wizard feature.

## Prerequisites
- Frontend server running at http://localhost:5173
- Backend server running at http://localhost:8000
- Test user account with admin/manager/user role
- Sample test files (PDF, Excel, or images)

## Test Scenarios

### Scenario 1: Navigate to Import Wizard
1. Log in as a valid user
2. Navigate to the Import Wizard via sidebar (click "Import Wizard" nav item)
3. **Expected**: Import Wizard page loads with Stepper at Step 1 (Upload Files)
4. **Screenshot**: `import-wizard-initial.png`

### Scenario 2: File Upload Validation
1. From Import Wizard page, attempt to drag an invalid file type (e.g., `.txt`)
2. **Expected**: Error message displays indicating invalid file type
3. Attempt to upload a file larger than 20MB
4. **Expected**: Error message displays indicating file too large
5. Upload valid files (PDF, Excel, or images within size limit)
6. **Expected**: Files appear in the selected files list with name and size
7. **Screenshot**: `import-wizard-files-selected.png`

### Scenario 3: Start Extraction and Processing
1. With valid files selected, click "Start Extraction" button
2. **Expected**: Wizard advances to Step 2 (Processing)
3. **Expected**: Progress bar displays with percentage
4. **Expected**: Status text shows "Processing file X of Y"
5. Wait for processing to complete
6. **Expected**: Wizard auto-advances to Step 3 (Review Products)
7. **Screenshot**: `import-wizard-processing.png`

### Scenario 4: Review and Edit Products
1. On Review step, verify extracted products display in table
2. **Expected**: Table shows columns: Checkbox, Image, SKU, Name, Description, Price, MOQ, Confidence
3. **Expected**: All products are selected by default
4. Click "Select All" checkbox to deselect all
5. **Expected**: No products are selected, "Continue to Import" button is disabled
6. Select individual products using checkboxes
7. Edit a product's name field inline
8. **Expected**: Field updates immediately
9. Clear a product's name field (leave empty)
10. **Expected**: Red validation error appears on the Name field
11. Enter a valid name
12. **Expected**: Validation error clears
13. **Expected**: "Continue to Import" button becomes enabled
14. **Screenshot**: `import-wizard-review.png`

### Scenario 5: Confirm Import
1. Click "Continue to Import" button
2. **Expected**: Wizard advances to Step 4 (Confirm Import)
3. **Expected**: Summary card shows number of selected products
4. **Expected**: Supplier dropdown is displayed and required
5. Select a supplier from dropdown
6. If duplicate SKUs exist, verify warning alert displays
7. **Expected**: List of products to import is visible
8. Click "Import Products" button
9. **Expected**: Success dialog appears with import count
10. **Screenshot**: `import-wizard-success.png`

### Scenario 6: Cancel Import
1. Start a new import, upload files
2. Click "Cancel" button in header
3. **Expected**: Confirmation dialog appears
4. Click "Continue Editing" to dismiss
5. **Expected**: Wizard remains on current step
6. Click "Cancel" again, then "Cancel Import"
7. **Expected**: Wizard resets to Step 1 with no files selected

### Scenario 7: Save and Load Draft
1. Upload files and complete extraction
2. On Review step, modify some products
3. Click "Save Draft" button
4. **Expected**: Snackbar shows "Draft saved successfully"
5. Refresh the page
6. **Expected**: Draft dialog appears asking to resume
7. Click "Load Draft"
8. **Expected**: Review step loads with previously selected products and edits
9. Click "Discard Draft" on another page load
10. **Expected**: Wizard starts fresh from Step 1

### Scenario 8: Back Navigation
1. Complete extraction and reach Review step
2. Click "Back" button
3. **Expected**: Wizard returns to Upload step with empty file list
4. Advance to Confirm step
5. Click "Back" button
6. **Expected**: Wizard returns to Review step with products preserved

## Success Criteria
- [ ] All navigation steps work correctly
- [ ] File validation rejects invalid types and oversized files
- [ ] Drag-and-drop file upload works
- [ ] Click-to-browse file upload works
- [ ] Progress bar updates during extraction
- [ ] Auto-advance from Processing to Review works
- [ ] Inline editing in table works for all editable fields
- [ ] Validation errors display inline with red highlighting
- [ ] Confidence score chips are color-coded correctly
- [ ] Select all checkbox works
- [ ] Individual product selection works
- [ ] Supplier selection is required for import
- [ ] Duplicate SKU warnings display
- [ ] Import completes successfully
- [ ] Success/error dialog shows appropriate message
- [ ] Cancel confirmation works
- [ ] Draft save/load functionality works
- [ ] Back navigation preserves appropriate state

## Error Cases to Test
1. Network error during file upload
2. Extraction job failure
3. Import API failure
4. Empty extraction results (no products found)
5. All products have validation errors

## Notes
- Test with various file types: PDF, XLSX, XLS, PNG, JPG, JPEG
- Test with multiple files in a single upload
- Test with files at the size limit boundary (just under 20MB)
- Verify polling stops when extraction completes or fails
