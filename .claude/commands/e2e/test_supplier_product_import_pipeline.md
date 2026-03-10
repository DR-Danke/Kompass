# E2E Test: Supplier-to-Product Import Pipeline

## Overview
End-to-end test specification for the Supplier-to-Product Import Pipeline feature. This validates that the Import Wizard can be launched from a supplier's quick actions menu with the supplier pre-selected, and that products imported through this flow are correctly linked to the originating supplier.

## User Story
As a sourcing team member, I want to launch the Import Wizard from a supplier's profile with the supplier pre-selected, so that extracted products are automatically linked to that supplier without manual selection.

## Prerequisites
- Frontend server running at http://localhost:5173
- Backend server running at http://localhost:8000
- Test user account with admin/manager role
- At least one supplier exists in the system

## Test Steps

### Step 1: Navigate to Suppliers Page
1. Log in as a valid user
2. Navigate to the Suppliers page via sidebar
3. **Verify**: Suppliers page loads with supplier table visible
4. **Screenshot**: `01_suppliers_page.png`

### Step 2: Open Quick Actions and Click "Importar Productos"
1. Find a supplier row in the table
2. Note the supplier's name for later verification
3. Click the quick actions menu (three-dot icon) on that supplier row
4. **Verify**: Quick actions menu opens with "Importar Productos" menu item visible
5. **Screenshot**: `02_quick_actions_menu.png`
6. Click "Importar Productos"
7. **Verify**: Browser navigates to `/import-wizard?supplier_id=<uuid>`
8. **Screenshot**: `03_import_wizard_with_supplier.png`

### Step 3: Verify Supplier Context Banner
1. On the Import Wizard page, look for the contextual info banner
2. **Verify**: An info Alert is displayed containing "Importando productos para:" followed by the supplier name noted in Step 2
3. **Verify**: The Stepper is at Step 1 (Upload Files) — normal wizard flow
4. **Screenshot**: `04_supplier_context_banner.png`

### Step 4: Verify Supplier Dropdown is Locked in Confirm Step
1. Upload a valid test file (PDF, Excel, or image) to start extraction
2. Wait for extraction to complete and auto-advance to Review step
3. Select at least one product and click "Continue to Import"
4. On the Confirm step, locate the Supplier dropdown
5. **Verify**: The Supplier dropdown is disabled (locked)
6. **Verify**: The Supplier dropdown displays the pre-selected supplier name
7. **Verify**: A helper text or chip shows "Pre-seleccionado desde proveedor"
8. **Screenshot**: `05_locked_supplier_dropdown.png`

### Step 5: Test Normal Flow Without supplier_id
1. Navigate directly to `/import-wizard` (no query parameters)
2. **Verify**: Import Wizard loads normally without any supplier context banner
3. **Verify**: No error messages are shown
4. **Screenshot**: `06_normal_import_wizard.png`

### Step 6: Test Invalid supplier_id
1. Navigate to `/import-wizard?supplier_id=00000000-0000-0000-0000-000000000000`
2. **Verify**: An error Alert is displayed with message about supplier not found
3. **Verify**: The wizard still loads and is usable (fallback to normal flow)
4. **Screenshot**: `07_invalid_supplier_error.png`

## Success Criteria
- [ ] "Importar Productos" menu item appears in supplier quick actions menu
- [ ] Clicking "Importar Productos" navigates to `/import-wizard?supplier_id=<uuid>`
- [ ] Contextual info banner shows "Importando productos para: {supplier_name}"
- [ ] Supplier dropdown is disabled/locked when supplier_id is in URL
- [ ] Pre-selected supplier name is displayed in the locked dropdown
- [ ] Helper text "Pre-seleccionado desde proveedor" is visible
- [ ] Invalid supplier_id shows error alert and falls back to normal flow
- [ ] Normal Import Wizard flow (no supplier_id) continues to work unchanged
- [ ] All UI text for new elements is in Spanish

## Error Cases to Test
1. Invalid UUID format in supplier_id parameter
2. Non-existent supplier_id (valid UUID, supplier not found)
3. Network error when fetching supplier details

## Notes
- All new UI strings are in Spanish (Colombian) as per project convention
- The backend already supports `supplier_id` in `ConfirmImportRequestDTO` — no backend changes needed
- This is the final piece (TF-009) of the Trade Fair Supplier Capture pipeline
