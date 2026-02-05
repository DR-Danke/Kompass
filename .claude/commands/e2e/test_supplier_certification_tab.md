# E2E Test: Supplier Certification Tab

## User Story

As a sourcing manager
I want to upload factory audits and view extracted summaries with AI-generated classifications
So that I can make faster supplier qualification decisions without manually reviewing lengthy PDF documents

## Test Steps

### Step 1: Navigate to Suppliers Page and Open a Supplier
1. Open the application at the base URL
2. Login with test credentials (if required)
3. Navigate to `/suppliers` page using the sidebar navigation or direct URL
4. **Verify** page title "Suppliers" is visible
5. **Verify** supplier data table is visible
6. **Screenshot**: `01_suppliers_page_loaded.png`
7. Click the edit (pencil) icon on the first supplier in the table
8. **Verify** supplier dialog opens
9. **Screenshot**: `02_supplier_dialog_opened.png`

### Step 2: Switch to Certification Tab
1. **Verify** tab navigation is visible with "General" and "Certification" tabs
2. **Verify** "General" tab is active by default
3. Click on the "Certification" tab
4. **Verify** "Certification" tab becomes active
5. **Verify** certification tab content is visible
6. **Screenshot**: `03_certification_tab_active.png`

### Step 3: Verify Upload Area
1. **Verify** drag-and-drop upload area is visible
2. **Verify** upload area displays text like "Drag and drop a PDF file here"
3. **Verify** "Browse" or file input button is available
4. **Screenshot**: `04_upload_area_visible.png`

### Step 4: Upload an Audit PDF File (Simulated)
1. Locate a test PDF file (or simulate file selection)
2. Trigger file upload via the file input
3. **Verify** upload progress indicator displays during upload
4. **Verify** processing status shows "Processing..." after upload completes
5. **Screenshot**: `05_upload_in_progress.png`
6. Wait for extraction to complete (or timeout after 60 seconds)
7. **Verify** extraction summary displays after processing (or error state if failed)
8. **Screenshot**: `06_extraction_complete.png`

### Step 5: Verify Extraction Summary Display
1. If extraction completed successfully:
   - **Verify** quick summary section displays (supplier type, employee count, factory area, etc.)
   - **Verify** certifications are displayed as chips/badges
   - **Verify** markets served chart is visible (if market data available)
   - **Verify** positive points section is visible with green checkmark icons
   - **Verify** negative points section is visible with warning icons
2. If extraction failed:
   - **Verify** error message is displayed
   - **Verify** "Reprocess" button is visible
3. **Screenshot**: `07_summary_display.png`

### Step 6: Verify Classification Badge
1. **Verify** classification badge is visible in the summary card
2. **Verify** badge shows correct grade (A, B, or C) or "Pending" if not yet classified
3. **Verify** badge has correct color:
   - Grade A: Green background
   - Grade B: Orange background
   - Grade C: Red background
   - Pending: Gray background
4. Hover over the classification badge
5. **Verify** tooltip shows classification reasoning (if available)
6. **Screenshot**: `08_classification_badge.png`

### Step 7: Open Override Dialog and Change Classification
1. **Verify** "Override" button is visible near the classification badge
2. Click the "Override" button
3. **Verify** override dialog opens
4. **Verify** dialog title is "Override Classification"
5. **Verify** current classification is displayed
6. **Verify** classification dropdown is present with A, B, C options
7. **Verify** notes text field is present and required
8. **Screenshot**: `09_override_dialog_open.png`
9. Select a different classification (e.g., if current is B, select A)
10. Leave notes field empty and click Confirm
11. **Verify** validation error shows for notes field (minimum 10 characters required)
12. Enter override notes: "Manual override for testing purposes - quality inspection passed"
13. Click "Confirm" button
14. **Verify** dialog closes
15. **Verify** classification badge updates with new grade
16. **Verify** "Manual" indicator appears on the badge
17. **Screenshot**: `10_classification_overridden.png`

### Step 8: Test View Full PDF Button
1. **Verify** "View Full PDF" button is visible in the audit summary card
2. Click "View Full PDF" button
3. **Verify** PDF opens in a new browser tab (or note if blocked by popup blocker)
4. **Screenshot**: `11_view_pdf_action.png`

### Step 9: Test Reprocess Button (for failed extractions)
1. If there's a failed extraction visible:
   - Click the "Reprocess" button
   - **Verify** processing status changes to "Processing..."
   - **Verify** extraction is re-attempted
2. If no failed extractions:
   - **Verify** Reprocess button is available on successfully processed audits
3. **Screenshot**: `12_reprocess_functionality.png`

### Step 10: Verify Responsive Design
1. Resize the browser viewport to tablet size (768px width)
2. **Verify** certification tab content adjusts responsively
3. **Verify** markets chart resizes appropriately
4. **Verify** positive/negative points columns stack vertically on small screens
5. **Screenshot**: `13_responsive_tablet.png`
6. Resize the browser viewport to mobile size (375px width)
7. **Verify** all content remains accessible and readable
8. **Screenshot**: `14_responsive_mobile.png`
9. Restore browser to normal size

### Step 11: Verify Empty State (Optional - New Supplier)
1. Close the current supplier dialog
2. Click "Add Supplier" button
3. **Verify** "Add Supplier" dialog opens
4. **Verify** only "General" tab is shown (Certification tab hidden for new suppliers)
5. **Screenshot**: `15_new_supplier_no_certification_tab.png`
6. Click "Cancel" to close

### Step 12: Verify Audit History (if multiple audits exist)
1. Open an existing supplier with audits
2. Switch to Certification tab
3. If multiple audits exist:
   - **Verify** "Audit History" section is visible below the main audit summary
   - **Verify** history table shows date, type, status, and classification columns
   - **Verify** clicking a row in history displays that audit's details
4. **Screenshot**: `16_audit_history.png`

## Success Criteria

- [ ] Suppliers page loads correctly
- [ ] Supplier dialog opens with tabbed interface in edit mode
- [ ] Certification tab is visible only for existing suppliers
- [ ] Upload area displays correctly with drag-drop zone
- [ ] File upload shows progress indicator
- [ ] Extraction summary displays after processing
- [ ] Markets served chart renders with correct data
- [ ] Positive and negative points display with appropriate icons
- [ ] Classification badge shows correct color based on grade (A=green, B=orange, C=red)
- [ ] "Pending" badge shown when classification not available
- [ ] Override dialog opens and validates required notes field
- [ ] Classification updates after successful override
- [ ] "Manual" indicator appears on manually overridden classifications
- [ ] View Full PDF opens document in new tab
- [ ] Reprocess button triggers re-extraction for failed audits
- [ ] Responsive design works on tablet and mobile viewports
- [ ] Audit history section displays for suppliers with multiple audits
- [ ] No console errors during test execution

## Notes

- Test PDF files should be available in the test fixtures directory
- The backend API for audits is expected to be available at `/api/suppliers/{id}/audits`
- Extraction processing may be mocked or simulated in test environment
- File upload uses multipart/form-data with progress tracking
- Classification grades: A (Best), B (Acceptable), C (Needs Improvement)
- Override notes require minimum 10 characters
- The certification tab is hidden when creating a new supplier (no supplier ID yet)
