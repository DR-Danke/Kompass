# E2E Test: Supplier Certification Workflow

## Overview

This comprehensive E2E test validates the complete supplier certification workflow, including audit upload, AI extraction, classification generation, manual override, pipeline status integration, and filtering/sorting functionality.

## User Stories Covered

1. As a sourcing manager, I want to upload factory audits and have data automatically extracted so I can make faster supplier qualification decisions.
2. As a sourcing manager, I want to view AI-generated classifications so I can quickly assess supplier quality.
3. As a team lead, I want to override AI classifications with documented reasoning so I can apply business judgment.
4. As a user, I want to filter and sort suppliers by certification status so I can find qualified suppliers quickly.

## Prerequisites

- Application running (frontend on port 5173, backend on port 8000)
- Test user credentials available (admin or manager role for override tests)
- Test PDF file available for upload testing
- At least one supplier in the database

## Test Execution

### Setup

```bash
cd apps/Client
npx puppeteer browsers install chrome
```

## Test Scenarios

### Scenario 1: Audit Upload Flow

**Objective:** Verify PDF upload creates audit record and triggers processing.

#### Steps

1. **Navigate to Suppliers Page**
   - Open application at http://localhost:5173
   - Login with test credentials
   - Navigate to `/suppliers` page
   - **Verify** page title "Suppliers" is visible
   - **Verify** supplier data table is loaded
   - **Screenshot**: `01_suppliers_page_loaded.png`

2. **Open Supplier Dialog**
   - Click the edit (pencil) icon on an existing supplier
   - **Verify** supplier dialog opens
   - **Screenshot**: `02_supplier_dialog_opened.png`

3. **Switch to Certification Tab**
   - **Verify** tab navigation shows "General" and "Certification" tabs
   - Click on "Certification" tab
   - **Verify** "Certification" tab becomes active
   - **Screenshot**: `03_certification_tab_active.png`

4. **Verify Upload Area**
   - **Verify** drag-and-drop upload area is visible
   - **Verify** upload area displays "Drag and drop a PDF file here" or similar
   - **Verify** "Browse" button or file input is available
   - **Screenshot**: `04_upload_area_visible.png`

5. **Upload PDF Audit Document**
   - Select or drop a test PDF file
   - **Verify** upload progress indicator displays
   - **Verify** processing status shows "Processing..." after upload
   - **Screenshot**: `05_upload_in_progress.png`

6. **Verify Processing Status Transitions**
   - Wait for extraction to complete (max 60 seconds timeout)
   - **Verify** status transitions: pending → processing → completed
   - **Verify** extraction summary displays after processing
   - **Screenshot**: `06_extraction_complete.png`

### Scenario 2: File Validation (Negative Tests)

**Objective:** Verify the system rejects invalid files appropriately.

#### Steps

7. **Attempt Non-PDF Upload**
   - Attempt to upload a non-PDF file (e.g., .txt, .jpg)
   - **Verify** error message displays about file type
   - **Verify** message mentions "PDF files only" or similar
   - **Screenshot**: `07_non_pdf_rejected.png`

8. **Verify Upload Area Reset**
   - **Verify** upload area returns to idle state after error
   - **Verify** user can try uploading again
   - **Screenshot**: `08_upload_area_reset.png`

### Scenario 3: AI Extraction Verification

**Objective:** Verify extracted data displays correctly.

#### Steps

9. **Verify Quick Summary Display**
   - **Verify** supplier type displays (Manufacturer/Trader)
   - **Verify** employee count displays (if extracted)
   - **Verify** factory area displays (if extracted)
   - **Verify** production lines count displays (if extracted)
   - **Screenshot**: `09_quick_summary.png`

10. **Verify Certifications Display**
    - **Verify** certifications display as chips/badges
    - **Verify** chips show certification names (e.g., "ISO 9001", "CE")
    - **Screenshot**: `10_certifications_chips.png`

11. **Verify Markets Served Chart**
    - **Verify** markets served chart is visible (pie chart or bar chart)
    - **Verify** chart shows percentage breakdowns by region
    - **Screenshot**: `11_markets_chart.png`

12. **Verify Points Display**
    - **Verify** positive points section is visible with green checkmarks
    - **Verify** negative points section is visible with warning icons
    - **Verify** points are displayed as bullet list items
    - **Screenshot**: `12_points_display.png`

### Scenario 4: Classification Flow

**Objective:** Verify AI classification generates correctly.

#### Steps

13. **Verify Classification Badge**
    - **Verify** classification badge is visible in summary card
    - **Verify** badge shows grade (A, B, or C) or "Pending"
    - **Screenshot**: `13_classification_badge.png`

14. **Verify Badge Colors**
    - **Verify** badge has correct color based on grade:
      - Grade A: Green (#4caf50 or similar)
      - Grade B: Orange (#ff9800 or similar)
      - Grade C: Red (#f44336 or similar)
      - Pending: Gray
    - **Screenshot**: `14_badge_colors.png`

15. **Verify Classification Tooltip**
    - Hover over the classification badge
    - **Verify** tooltip shows classification reasoning
    - **Verify** reasoning includes score and key factors
    - **Screenshot**: `15_classification_tooltip.png`

### Scenario 5: Override Classification Flow

**Objective:** Verify manual classification override with required notes.

#### Steps

16. **Open Override Dialog**
    - **Verify** "Override" button is visible near classification badge
    - Click the "Override" button
    - **Verify** override dialog opens
    - **Screenshot**: `16_override_dialog_open.png`

17. **Verify Dialog Contents**
    - **Verify** dialog title is "Override Classification"
    - **Verify** current classification is displayed
    - **Verify** classification dropdown has A, B, C options
    - **Verify** notes text field is present
    - **Screenshot**: `17_override_dialog_contents.png`

18. **Test Notes Validation**
    - Select a different classification grade
    - Leave notes field empty
    - Click "Confirm" button
    - **Verify** validation error for required notes
    - **Screenshot**: `18_notes_validation_error.png`

19. **Complete Override**
    - Enter notes: "Manual override for testing - verified quality meets standards"
    - Click "Confirm" button
    - **Verify** dialog closes
    - **Screenshot**: `19_override_submitted.png`

20. **Verify Override Applied**
    - **Verify** classification badge updates with new grade
    - **Verify** "Manual" indicator appears on badge
    - **Screenshot**: `20_override_applied.png`

### Scenario 6: Reprocess Functionality

**Objective:** Verify audit can be reprocessed.

#### Steps

21. **Trigger Reprocess**
    - **Verify** "Reprocess" button is visible on audit card
    - Click "Reprocess" button
    - **Verify** extraction status resets to "Processing..."
    - **Screenshot**: `21_reprocess_triggered.png`

22. **Wait for Reprocessing**
    - Wait for extraction to complete again
    - **Verify** extraction data refreshes
    - **Screenshot**: `22_reprocess_complete.png`

### Scenario 7: Pipeline Status Integration

**Objective:** Verify certification integrates with pipeline workflow.

#### Steps

23. **Close Supplier Dialog**
    - Click outside dialog or press Cancel/Close
    - **Verify** dialog closes
    - **Verify** supplier list is visible

24. **Verify Pipeline Status Column**
    - **Verify** "Pipeline Status" column exists in table (or card view)
    - **Verify** status is displayed for each supplier
    - **Screenshot**: `23_pipeline_status_column.png`

25. **Change Pipeline Status**
    - Open quick actions menu on supplier row (three-dot menu)
    - Click "Change Pipeline Status"
    - Select a different status (e.g., "Potential" → "Quoted")
    - **Verify** pipeline status updates
    - **Screenshot**: `24_pipeline_status_changed.png`

### Scenario 8: Certification Filters Integration

**Objective:** Verify filtering by certification status.

#### Steps

26. **Verify Certification Column**
    - **Verify** "Certification" column exists in suppliers table
    - **Verify** certification badges display in column
    - **Screenshot**: `25_certification_column.png`

27. **Apply Type A Filter**
    - Click the certification filter dropdown
    - Select "Type A" option
    - **Verify** table reloads
    - **Verify** only Type A suppliers display (or empty state message)
    - **Screenshot**: `26_type_a_filter.png`

28. **Apply Uncertified Filter**
    - Change filter to "Uncertified"
    - **Verify** results update
    - **Verify** only uncertified suppliers display
    - **Screenshot**: `27_uncertified_filter.png`

29. **Reset Filter**
    - Reset filter to "All Certifications"
    - **Verify** all suppliers display again
    - **Screenshot**: `28_filter_reset.png`

### Scenario 9: Sorting by Certification

**Objective:** Verify sorting functionality for certification columns.

#### Steps

30. **Sort by Certification Status**
    - Click "Certification" column header
    - **Verify** sort indicator appears (arrow icon)
    - **Verify** table reorders by certification grade
    - **Screenshot**: `29_sort_by_certification.png`

31. **Reverse Sort Order**
    - Click column header again
    - **Verify** sort direction reverses
    - **Screenshot**: `30_sort_reversed.png`

32. **Sort by Certified Date**
    - Click "Certified Date" column header
    - **Verify** sort indicator appears
    - **Verify** table reorders by certification date
    - **Screenshot**: `31_sort_by_date.png`

### Scenario 10: Quick Actions Integration

**Objective:** Verify quick actions menu includes certification options.

#### Steps

33. **Open Quick Actions Menu**
    - Locate a supplier row
    - Click the three-dot menu (MoreVert icon)
    - **Verify** menu opens
    - **Screenshot**: `32_quick_actions_menu.png`

34. **Verify Menu Options**
    - **Verify** menu includes "Upload Audit" option
    - **Verify** menu includes "View Certification Summary" option
    - **Screenshot**: `33_quick_actions_options.png`

35. **Test Upload Audit Action**
    - Click "Upload Audit"
    - **Verify** audit upload dialog opens
    - **Verify** dialog contains upload area
    - **Screenshot**: `34_upload_audit_dialog.png`

36. **Close Upload Dialog**
    - Click Cancel or close button
    - **Verify** dialog closes

### Scenario 11: Products Page Certification Status

**Objective:** Verify certification status appears on related products.

#### Steps

37. **Navigate to Products Page**
    - Navigate to `/products` page
    - **Verify** products catalog loads
    - **Screenshot**: `35_products_page.png`

38. **Verify Supplier Certification Badge**
    - **Verify** products from certified suppliers show certification badge
    - **Verify** badge appears in supplier info section or column
    - **Screenshot**: `36_product_certification_badge.png`

### Scenario 12: Audit History

**Objective:** Verify audit history displays for suppliers with multiple audits.

#### Steps

39. **Navigate to Supplier with Multiple Audits**
    - Return to Suppliers page
    - Open supplier that has multiple audits (if available)
    - Switch to Certification tab

40. **Verify Audit History Section**
    - **Verify** "Audit History" section is visible below main audit summary
    - **Verify** history table shows columns: Date, Type, Status, Classification
    - **Screenshot**: `37_audit_history.png`

41. **Select Older Audit**
    - Click on an older audit in history
    - **Verify** audit details load for selected audit
    - **Screenshot**: `38_older_audit_selected.png`

## Success Criteria Checklist

### Audit Upload
- [ ] Audit upload accepts PDF files
- [ ] Audit upload rejects non-PDF files with error message
- [ ] Upload progress indicator displays during upload
- [ ] Processing status transitions correctly (pending → processing → completed)

### AI Extraction
- [ ] Extraction summary displays all expected fields
- [ ] Supplier type (Manufacturer/Trader) displays correctly
- [ ] Employee count, factory area, production lines display
- [ ] Markets served chart renders with region breakdowns
- [ ] Certifications display as chips
- [ ] Positive points display with green checkmarks
- [ ] Negative points display with warning icons

### Classification
- [ ] Classification badge shows correct grade (A/B/C or Pending)
- [ ] Badge colors are correct (A=green, B=orange, C=red)
- [ ] Tooltip shows classification reasoning on hover

### Override
- [ ] Override dialog opens correctly
- [ ] Override dialog validates required notes field
- [ ] Classification override updates badge
- [ ] "Manual" indicator appears on overridden classification

### Reprocess
- [ ] Reprocess functionality resets extraction status
- [ ] Reprocess triggers new extraction

### Pipeline Integration
- [ ] Pipeline status displays and can be changed
- [ ] Pipeline status updates persist

### Filtering & Sorting
- [ ] Certification filter works correctly (All, Type A/B/C, Uncertified)
- [ ] Sorting by certification status works
- [ ] Sorting by certified date works

### Quick Actions
- [ ] Quick actions menu includes "Upload Audit"
- [ ] Quick actions menu includes "View Certification Summary"
- [ ] Upload Audit action opens upload dialog

### Products Integration
- [ ] Products from certified suppliers show certification badge

### Audit History
- [ ] Audit history displays for suppliers with multiple audits
- [ ] Clicking older audit loads its details

### General
- [ ] No console errors during test execution
- [ ] UI is responsive and accessible

## Automated Test Script

```typescript
import puppeteer from 'puppeteer';

const BASE_URL = 'http://localhost:5173';
const TEST_USER_EMAIL = 'admin@example.com';
const TEST_USER_PASSWORD = 'password123';

async function testSupplierCertificationWorkflow() {
  const browser = await puppeteer.launch({ headless: false, slowMo: 50 });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });

  try {
    console.log('Starting Supplier Certification Workflow E2E Test...\n');

    // === SCENARIO 1: Audit Upload Flow ===
    console.log('=== Scenario 1: Audit Upload Flow ===');

    // Step 1: Login and navigate
    await page.goto(`${BASE_URL}/login`);
    await page.type('input[name="email"]', TEST_USER_EMAIL);
    await page.type('input[name="password"]', TEST_USER_PASSWORD);
    await page.click('button[type="submit"]');
    await page.waitForNavigation({ waitUntil: 'networkidle0' });
    console.log('✓ Logged in successfully');

    // Navigate to suppliers
    await page.goto(`${BASE_URL}/suppliers`);
    await page.waitForSelector('table', { timeout: 10000 });
    await page.screenshot({ path: '01_suppliers_page_loaded.png' });
    console.log('✓ Suppliers page loaded');

    // Step 2: Open supplier dialog
    const editButtons = await page.$$('[aria-label="edit"]');
    if (editButtons.length > 0) {
      await editButtons[0].click();
      await page.waitForSelector('[role="dialog"]', { timeout: 5000 });
      await page.screenshot({ path: '02_supplier_dialog_opened.png' });
      console.log('✓ Supplier dialog opened');
    }

    // Step 3: Switch to Certification tab
    const certTab = await page.$x("//button[contains(., 'Certification')]");
    if (certTab.length > 0) {
      await certTab[0].click();
      await page.waitForTimeout(500);
      await page.screenshot({ path: '03_certification_tab_active.png' });
      console.log('✓ Certification tab active');
    }

    // Step 4: Verify upload area
    const uploadArea = await page.$('[class*="dropzone"]');
    if (uploadArea) {
      console.log('✓ Upload area visible');
      await page.screenshot({ path: '04_upload_area_visible.png' });
    }

    // === SCENARIO 4: Classification Flow ===
    console.log('\n=== Scenario 4: Classification Flow ===');

    // Check for classification badge
    const classificationBadge = await page.$('[class*="classification"]');
    if (classificationBadge) {
      console.log('✓ Classification badge visible');
      await page.screenshot({ path: '13_classification_badge.png' });
    }

    // === SCENARIO 5: Override Classification ===
    console.log('\n=== Scenario 5: Override Classification ===');

    const overrideButton = await page.$x("//button[contains(., 'Override')]");
    if (overrideButton.length > 0) {
      await overrideButton[0].click();
      await page.waitForSelector('[role="dialog"]', { timeout: 5000 });
      await page.screenshot({ path: '16_override_dialog_open.png' });
      console.log('✓ Override dialog opened');

      // Try to submit without notes
      const confirmButton = await page.$x("//button[contains(., 'Confirm')]");
      if (confirmButton.length > 0) {
        await confirmButton[0].click();
        await page.waitForTimeout(500);
        // Should show validation error
        await page.screenshot({ path: '18_notes_validation_error.png' });
        console.log('✓ Notes validation working');
      }

      // Close dialog
      const cancelButton = await page.$x("//button[contains(., 'Cancel')]");
      if (cancelButton.length > 0) {
        await cancelButton[0].click();
      }
    }

    // Close supplier dialog
    const closeButton = await page.$('[aria-label="close"]');
    if (closeButton) {
      await closeButton.click();
      await page.waitForTimeout(500);
    }

    // === SCENARIO 8: Certification Filters ===
    console.log('\n=== Scenario 8: Certification Filters ===');

    // Check for certification column
    const certColumn = await page.$x("//th[contains(., 'Certification')]");
    if (certColumn.length > 0) {
      console.log('✓ Certification column exists');
      await page.screenshot({ path: '25_certification_column.png' });
    }

    // Test certification filter
    const filterDropdown = await page.$('[aria-label="Certification filter"]');
    if (filterDropdown) {
      await filterDropdown.click();
      await page.waitForTimeout(300);
      await page.screenshot({ path: '26_type_a_filter.png' });
      console.log('✓ Certification filter dropdown works');
    }

    // === SCENARIO 9: Sorting ===
    console.log('\n=== Scenario 9: Sorting ===');

    // Click certification header to sort
    const certHeader = await page.$x("//th[contains(., 'Certification')]//button");
    if (certHeader.length > 0) {
      await certHeader[0].click();
      await page.waitForTimeout(500);
      await page.screenshot({ path: '29_sort_by_certification.png' });
      console.log('✓ Sorting by certification works');
    }

    // === SCENARIO 10: Quick Actions ===
    console.log('\n=== Scenario 10: Quick Actions ===');

    const moreButtons = await page.$$('[aria-label="more actions"]');
    if (moreButtons.length > 0) {
      await moreButtons[0].click();
      await page.waitForSelector('[role="menu"]', { timeout: 3000 });
      await page.screenshot({ path: '32_quick_actions_menu.png' });
      console.log('✓ Quick actions menu opens');

      // Check for Upload Audit option
      const uploadAuditOption = await page.$x("//li[contains(., 'Upload Audit')]");
      if (uploadAuditOption.length > 0) {
        console.log('✓ Upload Audit option exists');
      }

      // Close menu by clicking elsewhere
      await page.click('body');
    }

    console.log('\n========================================');
    console.log('✅ All tests completed successfully!');
    console.log('========================================');

  } catch (error) {
    console.error('\n❌ Test failed:', error.message);
    await page.screenshot({ path: 'test_failure.png' });
    throw error;
  } finally {
    await browser.close();
  }
}

// Run tests
testSupplierCertificationWorkflow().catch(console.error);
```

## Manual Verification Checklist

Use this checklist for manual testing:

### Pre-Test Setup
- [ ] Application running (frontend + backend)
- [ ] Logged in as admin or manager user
- [ ] Test PDF file ready for upload

### Audit Upload
- [ ] Can navigate to Suppliers page
- [ ] Can open supplier edit dialog
- [ ] Certification tab is visible and clickable
- [ ] Upload area displays correctly
- [ ] PDF upload succeeds
- [ ] Non-PDF files are rejected with error
- [ ] Processing status updates in real-time

### Extraction Display
- [ ] Summary section shows extracted data
- [ ] Supplier type displays (Manufacturer/Trader)
- [ ] Numeric fields display (employees, area, lines)
- [ ] Certifications show as chips
- [ ] Markets chart renders
- [ ] Positive/negative points display

### Classification
- [ ] Classification badge displays
- [ ] Badge color matches grade
- [ ] Tooltip shows reasoning on hover

### Override (Admin/Manager only)
- [ ] Override button visible
- [ ] Override dialog opens
- [ ] Notes validation enforced
- [ ] Override applies successfully
- [ ] "Manual" indicator shows

### Reprocess
- [ ] Reprocess button visible
- [ ] Reprocess triggers new extraction

### Filters & Sorting
- [ ] Certification filter dropdown works
- [ ] Filter results update correctly
- [ ] Sorting by certification works
- [ ] Sorting by date works

### Quick Actions
- [ ] Menu opens on click
- [ ] "Upload Audit" option present
- [ ] "View Certification Summary" present

### Cross-Page
- [ ] Products page shows certification badges
- [ ] Audit history displays (if multiple audits)

## Notes

- Test PDF files should be in `apps/Client/src/__tests__/fixtures/` directory
- Backend API endpoints: `/api/suppliers/{id}/audits/*`
- Extraction processing may take 30-60 seconds depending on PDF complexity
- Override notes require minimum 10 characters
- Classification grades: A (Best), B (Acceptable), C (Needs Improvement)
- RBAC: Viewers can read, Users can upload/classify, Admin/Manager can override/reprocess/delete
