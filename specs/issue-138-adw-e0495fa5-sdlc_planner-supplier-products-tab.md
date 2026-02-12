# Feature: Supplier Products Tab

## Metadata
issue_number: `138`
adw_id: `e0495fa5`
issue_json: `{"number":138,"title":"Drill down to products list from the suppliers kanban/list","body":"The Kanban already shows us the number of products associated to each supplier. It would be useful when entering the supplier card, to have a tab that shows the list of products that have been associated."}`

## Feature Description
Add a "Products" tab to the Supplier edit dialog (SupplierForm) that displays a paginated table of all products associated with that supplier. The Kanban board and supplier list already show the product count per supplier. This feature enables users to drill down from a supplier card directly into the list of products linked to that supplier, providing a seamless workflow for supplier-product management without navigating away from the supplier context.

## User Story
As a sourcing manager
I want to see the list of products associated with a supplier directly within the supplier card
So that I can quickly review a supplier's product catalog without leaving the supplier management interface

## Problem Statement
Currently, users can see the number of products per supplier on the Kanban board, but there is no way to drill down into those products from the supplier card. To view a supplier's products, users must navigate to the Products page and manually filter by supplier. This creates unnecessary friction in the workflow.

## Solution Statement
Add a third tab ("Products") to the existing SupplierForm dialog that appears in edit mode. This tab will use the already-existing backend endpoint `GET /api/suppliers/{supplier_id}/products` to fetch and display the supplier's products in a table format with pagination. The implementation leverages the existing `ProductTable`-like presentation pattern and the existing API infrastructure, requiring no backend changes.

## Relevant Files
Use these files to implement the feature:

- `apps/Client/src/components/kompass/SupplierForm.tsx` - The supplier edit dialog that already has tabs (General, Certification). The new "Products" tab will be added here as tab index 2.
- `apps/Client/src/components/kompass/SupplierCertificationTab.tsx` - Reference for the tab component pattern (props interface, data fetching with useCallback, loading/error states). The new SupplierProductsTab will follow this same pattern.
- `apps/Client/src/components/kompass/ProductTable.tsx` - The existing product table component. Used as reference for column structure and display patterns, but a simplified inline table will be built for the tab since ProductTable depends on useProducts hook sort/select types.
- `apps/Client/src/components/kompass/ProductStatusBadge.tsx` - Reuse this component to display product status in the table.
- `apps/Client/src/services/kompassService.ts` - Add a new `getSupplierProducts` method to the `supplierService` object to call `GET /api/suppliers/{supplier_id}/products`.
- `apps/Client/src/types/kompass.ts` - Contains `ProductResponse`, `ProductListResponse`, and `ProductFilter` types already defined. No changes needed.
- `apps/Server/app/api/supplier_routes.py` - The backend endpoint `GET /{supplier_id}/products` already exists and returns `ProductListResponseDTO`. No backend changes needed.
- `.claude/commands/test_e2e.md` - Read this to understand how to create and execute E2E test files.
- `.claude/commands/e2e/test_supplier_certification_tab.md` - Read this as the closest reference for E2E test structure (same supplier dialog, tab-switching pattern).
- `app_docs/feature-2805baf7-supplier-certification-tab.md` - Read this to understand the existing certification tab implementation patterns.
- `app_docs/feature-f060bebe-suppliers-management-page.md` - Read this to understand the suppliers page and form patterns.

### New Files
- `apps/Client/src/components/kompass/SupplierProductsTab.tsx` - New component that displays the products list within the supplier dialog tab.
- `.claude/commands/e2e/test_supplier_products_tab.md` - New E2E test file to validate the supplier products tab functionality.

## Implementation Plan
### Phase 1: Foundation
Add the API service method to fetch supplier products from the frontend. The backend endpoint already exists (`GET /api/suppliers/{supplier_id}/products`), so no backend work is needed. Add the service method to `kompassService.ts` under the `supplierService` object.

### Phase 2: Core Implementation
Create the `SupplierProductsTab` component following the same pattern as `SupplierCertificationTab`:
- Accept `supplierId` and `supplierName` props
- Fetch products on mount using the new service method
- Display products in a Material-UI table with columns: Image, Name/SKU, Category, Price, MOQ, Status
- Support pagination (page/limit controls)
- Handle loading, error, and empty states
- Link to the product (or show info) without navigating away from the dialog

### Phase 3: Integration
Integrate the new tab into the existing `SupplierForm` dialog:
- Add "Products" as tab index 2 (after General and Certification)
- Update the dialog title logic to reflect the active tab
- Only show the tab in edit mode (consistent with existing behavior)
- Create E2E test to validate the feature

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create E2E Test Specification
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_supplier_certification_tab.md` to understand the E2E test patterns
- Create `.claude/commands/e2e/test_supplier_products_tab.md` with the following test steps:
  1. Navigate to Suppliers page and open a supplier (that has products associated)
  2. Verify tab navigation shows "General", "Certification", and "Products" tabs
  3. Click on "Products" tab and verify it becomes active
  4. Verify product table is displayed with columns (Image, Name, Category, Price, MOQ, Status)
  5. Verify products data loads and is displayed correctly
  6. If more than one page of products, verify pagination controls work
  7. Verify empty state if a supplier has no products
- Include screenshots at each verification step
- Include success criteria checklist

### Step 2: Add Frontend Service Method
- Open `apps/Client/src/services/kompassService.ts`
- Add a `getProducts` method to the `supplierService` object:
  ```typescript
  async getProducts(
    supplierId: string,
    page = 1,
    limit = 20
  ): Promise<ProductListResponse> {
    const response = await apiClient.get<ProductListResponse>(
      `/suppliers/${supplierId}/products`,
      { params: { page, limit } }
    );
    return response.data;
  },
  ```
- Ensure `ProductListResponse` is already imported (it should be)

### Step 3: Create SupplierProductsTab Component
- Create `apps/Client/src/components/kompass/SupplierProductsTab.tsx`
- Follow the `SupplierCertificationTab` component pattern:
  - Props: `supplierId: string`, `supplierName: string`
  - State: products array, loading, error, pagination (page, limit, total)
  - Fetch products on mount using `supplierService.getProducts(supplierId, page, limit)`
  - Refetch when page changes
- Render a Material-UI `Table` with these columns:
  - Image thumbnail (Avatar with product primary image or placeholder icon)
  - Name (with SKU shown as secondary text below)
  - Category name
  - Price (formatted with currency)
  - MOQ (minimum order quantity)
  - Status (using `ProductStatusBadge` component)
- Add `TablePagination` component for page navigation
- Handle states:
  - Loading: show `CircularProgress`
  - Error: show `Alert` with error message
  - Empty: show `Typography` message "No products associated with this supplier"
- Keep the component read-only (no edit/delete actions from this tab)

### Step 4: Integrate Products Tab into SupplierForm
- Open `apps/Client/src/components/kompass/SupplierForm.tsx`
- Import the new `SupplierProductsTab` component
- Add the "Products" tab to the `Tabs` component (index 2):
  ```tsx
  <Tab label="Products" id="supplier-tab-2" aria-controls="supplier-tabpanel-2" />
  ```
- Add the corresponding `TabPanel` for the Products tab:
  ```tsx
  {isEditMode && supplier && (
    <TabPanel value={activeTab} index={2}>
      <SupplierProductsTab
        supplierId={supplier.id}
        supplierName={supplier.name}
      />
    </TabPanel>
  )}
  ```
- Update the `dialogTitle` logic to include tab 2:
  ```typescript
  const dialogTitle = isEditMode
    ? `Edit Supplier${activeTab === 1 ? ' - Certification' : activeTab === 2 ? ' - Products' : ''}`
    : 'Add Supplier';
  ```

### Step 5: Run Validation Commands
- Run TypeScript type checking to ensure no type errors
- Run the frontend build to ensure it compiles
- Run backend tests to confirm no regressions
- Read `.claude/commands/test_e2e.md`, then read and execute the new E2E test `.claude/commands/e2e/test_supplier_products_tab.md` to validate this functionality works

## Testing Strategy
### Unit Tests
- No new backend tests required (existing endpoint is already tested)
- Frontend type checking validates component props and service method types
- E2E test validates the full user flow

### Edge Cases
- Supplier with zero products: should show an empty state message
- Supplier with many products: pagination should work correctly
- Products with no images: should show placeholder icon
- Products with no category: should show dash or empty cell
- Network error during fetch: should show error alert
- Tab switching: products should only load when the Products tab is activated (lazy loading)

## Acceptance Criteria
- [ ] A "Products" tab appears in the supplier edit dialog (only in edit mode, alongside General and Certification)
- [ ] Clicking the Products tab displays a table of products associated with that supplier
- [ ] The table shows: image thumbnail, name/SKU, category, price, MOQ, and status
- [ ] Pagination controls allow navigating through large product lists
- [ ] Empty state is shown when a supplier has no associated products
- [ ] Loading spinner is shown while products are being fetched
- [ ] Error state is shown if the API call fails
- [ ] Dialog title updates to reflect the active tab
- [ ] TypeScript compiles with zero errors
- [ ] Frontend builds successfully
- [ ] Backend tests pass with zero regressions
- [ ] E2E test validates the complete workflow

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- Read `.claude/commands/test_e2e.md`, then read and execute the new E2E `.claude/commands/e2e/test_supplier_products_tab.md` test file to validate this functionality works.

- `cd apps/Server && source .venv/bin/activate && python -m pytest tests/ -v --tb=short` - Run Server tests to validate zero regressions
- `cd apps/Client && npx tsc --noEmit` - Run Client type check to validate zero type errors
- `cd apps/Client && npm run build` - Run Client build to validate successful compilation

## Notes
- The backend endpoint `GET /api/suppliers/{supplier_id}/products` already exists and returns paginated `ProductListResponseDTO`. No backend changes are needed.
- The `ProductListResponse` and `ProductResponse` types are already defined in `apps/Client/src/types/kompass.ts`.
- The `SupplierCertificationTab` component serves as the primary reference pattern for the new tab component (same props shape, same data-fetching pattern, same error/loading states).
- The Products tab is read-only — users view the products list but do not edit/delete products from within the supplier dialog. To edit a product, users should navigate to the Products page.
- Consider lazy-loading the products data (only fetch when the tab is first activated) to avoid unnecessary API calls when users only view the General or Certification tabs.
