# Supplier Products Tab

**ADW ID:** e0495fa5
**Date:** 2026-02-12
**Specification:** specs/issue-138-adw-e0495fa5-sdlc_planner-supplier-products-tab.md

## Overview

Adds a "Products" tab to the Supplier edit dialog, allowing users to drill down from a supplier card directly into the list of products associated with that supplier. This eliminates the need to navigate to the Products page and manually filter by supplier, providing a seamless workflow within the supplier management context.

## What Was Built

- New `SupplierProductsTab` component displaying a paginated table of supplier products
- Integration of the Products tab as the third tab in the SupplierForm dialog (after General and Certification)
- Frontend service method to fetch supplier products via the existing backend endpoint
- E2E test specification for validating the supplier products tab functionality

## Technical Implementation

### Files Modified

- `apps/Client/src/components/kompass/SupplierProductsTab.tsx`: New component (202 lines) rendering a Material-UI table with product data, pagination, loading/error/empty states
- `apps/Client/src/components/kompass/SupplierForm.tsx`: Added Products tab (index 2) to the existing tab group, updated dialog title logic, added TabPanel with SupplierProductsTab
- `apps/Client/src/services/kompassService.ts`: Added `getProducts(supplierId, page, limit)` method to `supplierService` calling `GET /api/suppliers/{supplierId}/products`
- `.claude/commands/e2e/test_supplier_products_tab.md`: New E2E test specification for the feature

### Key Changes

- **No backend changes required** - leverages the existing `GET /api/suppliers/{supplier_id}/products` endpoint that returns paginated `ProductListResponseDTO`
- The Products tab follows the same component pattern as `SupplierCertificationTab` (props interface, `useCallback` data fetching, loading/error states)
- Table columns: Image (Avatar with primary image or placeholder), Name/SKU, Category, Price (Intl.NumberFormat currency formatting), MOQ, Status (using `ProductStatusBadge`)
- Pagination via Material-UI `TablePagination` with 5/10/20 rows-per-page options
- Tab is only visible in edit mode (consistent with existing Certification tab behavior)
- Dialog title dynamically updates: "Edit Supplier", "Edit Supplier - Certification", or "Edit Supplier - Products"

## How to Use

1. Navigate to the Suppliers page (Kanban or list view)
2. Click on a supplier card to open the supplier edit dialog
3. Click the "Products" tab (third tab, after General and Certification)
4. View the paginated table of products associated with that supplier
5. Use pagination controls at the bottom to navigate through product pages
6. The tab is read-only - to edit a product, navigate to the Products page

## Configuration

No additional configuration required. The feature uses the existing backend endpoint and authentication.

## Testing

- **TypeScript**: `cd apps/Client && npx tsc --noEmit` - validates zero type errors
- **Build**: `cd apps/Client && npm run build` - validates successful compilation
- **Backend**: `cd apps/Server && source .venv/bin/activate && python -m pytest tests/ -v --tb=short` - validates zero regressions
- **E2E**: Run the E2E test spec at `.claude/commands/e2e/test_supplier_products_tab.md`

## Notes

- The tab is read-only by design. Users view products but cannot edit/delete from within the supplier dialog.
- Products data is fetched when the tab renders (not lazily on first activation), so switching to the Products tab triggers an API call.
- Products with no images display a placeholder icon (ImageNotSupportedIcon). Products with no category show a dash.
- The existing `ProductResponse` and `ProductListResponse` types from `types/kompass.ts` are reused without modification.
