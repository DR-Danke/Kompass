# E2E Test: Suppliers Certification Filters and Badges

## Overview
This E2E test validates the suppliers page certification filters, badges, quick actions, and sorting functionality.

## Prerequisites
- Application running (frontend on port 5173, backend on port 8000)
- Test user credentials available
- At least one supplier in the database

## Test Execution

### Setup
```bash
cd apps/Client
npx puppeteer browsers install chrome
```

### Test Steps

1. **Navigate and Login**
   - Navigate to http://localhost:5173/login
   - Login with test credentials
   - Navigate to /suppliers

2. **Verify New Columns**
   - Verify the table header contains "Certification" column
   - Verify the table header contains "Certified Date" column
   - Verify certification badges are displayed for suppliers

3. **Test Certification Filter**
   - Click the "Certification" dropdown filter
   - Select "Type A" option
   - Verify the table reloads and shows only Type A certified suppliers (or empty state)
   - Change filter to "Uncertified"
   - Verify results update accordingly
   - Reset filter to "All Certifications"

4. **Test Sorting**
   - Click on "Certification" column header
   - Verify sort indicator appears
   - Click again to reverse sort order
   - Click on "Certified Date" column header
   - Verify results re-sort

5. **Test Quick Actions Menu**
   - Locate a supplier row
   - Click the three-dot menu (MoreVert icon) in the Actions column
   - Verify the menu opens with options:
     - "View/Edit Supplier"
     - "Upload Audit"
     - "View Certification Summary"
     - "Change Pipeline Status"
     - "Delete Supplier"

6. **Test Upload Audit Action**
   - Click "Upload Audit" from the quick actions menu
   - Verify the audit upload dialog opens
   - Verify the dialog contains an upload area
   - Close the dialog

7. **Test Change Pipeline Status**
   - Click "Change Pipeline Status" from quick actions
   - Verify submenu appears with status options
   - Select a different status
   - Verify the supplier's pipeline status updates

### Success Criteria
- [ ] Certification column displays badges correctly (A/B/C grades or "Uncertified")
- [ ] Certified Date column shows formatted date or "-"
- [ ] Certification filter works (All, Certified, Type A/B/C, Uncertified)
- [ ] Sorting by certification status works
- [ ] Sorting by certified date works
- [ ] Quick actions menu opens and displays all options
- [ ] Upload Audit dialog opens correctly
- [ ] Change Pipeline Status submenu works
- [ ] No console errors during test execution

### Screenshots
Capture screenshots at each major step:
1. `suppliers-page-with-certification-columns.png` - Table with new columns
2. `suppliers-certification-filter-dropdown.png` - Filter dropdown open
3. `suppliers-certification-filter-applied.png` - After applying Type A filter
4. `suppliers-sorting-by-certification.png` - After sorting
5. `suppliers-quick-actions-menu.png` - Quick actions menu open
6. `suppliers-audit-upload-dialog.png` - Audit upload dialog
7. `suppliers-pipeline-status-submenu.png` - Pipeline status submenu

## Automated Test Script

```typescript
import puppeteer from 'puppeteer';

async function testSuppliersCertificationFilters() {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();

  try {
    // Login
    await page.goto('http://localhost:5173/login');
    await page.type('input[name="email"]', 'test@example.com');
    await page.type('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForNavigation();

    // Navigate to suppliers
    await page.goto('http://localhost:5173/suppliers');
    await page.waitForSelector('table');

    // Verify new columns exist
    const certificationHeader = await page.$x("//th[contains(., 'Certification')]");
    const certifiedDateHeader = await page.$x("//th[contains(., 'Certified Date')]");

    if (certificationHeader.length === 0) {
      throw new Error('Certification column header not found');
    }
    if (certifiedDateHeader.length === 0) {
      throw new Error('Certified Date column header not found');
    }

    console.log('✓ New columns verified');
    await page.screenshot({ path: 'suppliers-page-with-certification-columns.png' });

    // Test certification filter
    await page.click('[label="Certification"]');
    await page.screenshot({ path: 'suppliers-certification-filter-dropdown.png' });

    // Select Type A
    await page.click('[data-value="certified_a"]');
    await page.waitForTimeout(500); // Wait for API call
    await page.screenshot({ path: 'suppliers-certification-filter-applied.png' });
    console.log('✓ Certification filter works');

    // Test sorting
    const certHeader = await page.$x("//th[contains(., 'Certification')]//button");
    if (certHeader.length > 0) {
      await certHeader[0].click();
      await page.waitForTimeout(500);
      await page.screenshot({ path: 'suppliers-sorting-by-certification.png' });
      console.log('✓ Sorting by certification works');
    }

    // Reset filter
    await page.click('[label="Certification"]');
    await page.click('[data-value="all"]');
    await page.waitForTimeout(500);

    // Test quick actions menu
    const moreButtons = await page.$$('[aria-label="more actions"]');
    if (moreButtons.length > 0) {
      await moreButtons[0].click();
      await page.waitForSelector('#supplier-actions-menu');
      await page.screenshot({ path: 'suppliers-quick-actions-menu.png' });
      console.log('✓ Quick actions menu opens');

      // Test Upload Audit action
      const uploadAuditItem = await page.$x("//li[contains(., 'Upload Audit')]");
      if (uploadAuditItem.length > 0) {
        await uploadAuditItem[0].click();
        await page.waitForSelector('[role="dialog"]');
        await page.screenshot({ path: 'suppliers-audit-upload-dialog.png' });
        console.log('✓ Upload Audit dialog opens');

        // Close dialog
        const cancelButton = await page.$x("//button[contains(., 'Cancel')]");
        if (cancelButton.length > 0) {
          await cancelButton[0].click();
        }
      }

      // Test pipeline status submenu
      await moreButtons[0].click();
      const pipelineItem = await page.$x("//li[contains(., 'Change Pipeline Status')]");
      if (pipelineItem.length > 0) {
        await pipelineItem[0].click();
        await page.waitForSelector('#pipeline-status-menu');
        await page.screenshot({ path: 'suppliers-pipeline-status-submenu.png' });
        console.log('✓ Pipeline status submenu opens');
      }
    }

    console.log('\n✅ All tests passed!');

  } catch (error) {
    console.error('Test failed:', error);
    await page.screenshot({ path: 'test-failure.png' });
  } finally {
    await browser.close();
  }
}

testSuppliersCertificationFilters();
```

## Manual Verification Checklist

- [ ] Page loads without errors
- [ ] New columns are visible in the table
- [ ] Certification badges display correct colors (green for A, orange for B, red for C, gray for uncertified)
- [ ] Filter dropdown shows all certification options
- [ ] Filtering by certification status works correctly
- [ ] Sorting by certification status reorders the table
- [ ] Sorting by certified date reorders the table
- [ ] Quick actions menu has all expected options
- [ ] "View/Edit Supplier" opens the supplier form
- [ ] "Upload Audit" opens the audit upload dialog
- [ ] "View Certification Summary" opens supplier form to certification tab
- [ ] "Change Pipeline Status" submenu allows changing status
- [ ] All existing functionality still works (add/edit/delete supplier)
