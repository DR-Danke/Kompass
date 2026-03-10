# Supplier-to-Product Import Pipeline

**ADW ID:** 9477e39c
**Date:** 2026-03-09
**Specification:** specs/issue-148-adw-9477e39c-sdlc_planner-supplier-product-import-pipeline.md

## Overview

Connects the supplier capture flow to the Import Wizard by allowing users to launch the Import Wizard directly from a supplier's quick actions menu with that supplier pre-selected and locked. This completes the end-to-end pipeline: business card → supplier → products in the Biblia General (TF-009).

## What Was Built

- **"Importar Productos" quick action** on the Suppliers page menu to navigate directly to the Import Wizard with a `supplier_id` query parameter
- **URL parameter support** (`?supplier_id=<uuid>`) in the Import Wizard to pre-select a supplier on page load
- **Contextual info banner** showing "Importando productos para: {supplier_name}" when a supplier is pre-selected
- **Locked supplier dropdown** in the Confirm step that is disabled when a supplier is pre-selected from the URL
- **Error handling** for invalid or non-existent supplier IDs with fallback to normal wizard flow
- **E2E test specification** for the complete supplier-to-product import pipeline flow

## Technical Implementation

### Files Modified

- `apps/Client/src/components/kompass/SupplierQuickActionsMenu.tsx`: Added `onImportProducts` prop and "Importar Productos" menu item with `Inventory2Icon`
- `apps/Client/src/pages/kompass/SuppliersPage.tsx`: Added `useNavigate` and `handleImportProducts` handler that navigates to `/import-wizard?supplier_id={id}`
- `apps/Client/src/pages/kompass/ImportWizardPage.tsx`: Added `useSearchParams` to read `supplier_id`, fetch supplier on mount, show contextual banner, and lock supplier dropdown in the Confirm step

### New Files

- `.claude/commands/e2e/test_supplier_product_import_pipeline.md`: E2E test specification covering quick action navigation, supplier context banner, locked dropdown, invalid supplier_id, and normal flow fallback

### Key Changes

- **No backend changes required**: The existing `ConfirmImportRequestDTO` already accepts `supplier_id`, and `confirm_import` already uses it to set `supplier_id` on created products
- **URL-driven pre-selection**: `useSearchParams` reads `supplier_id` on mount, fetches the supplier via `supplierService.get()`, and stores it in `preSelectedSupplier` state
- **Supplier dropdown locking**: When `preSelectedSupplier` is set, the `Select` component is `disabled` and shows a "Pre-seleccionado desde proveedor" caption
- **Error resilience**: Invalid `supplier_id` shows a Spanish error alert ("Proveedor no encontrado. Puede seleccionar uno manualmente.") and falls back to normal wizard flow
- **URL param priority**: If a draft is loaded with a different supplier, the URL param takes precedence since the `useEffect` runs after draft loading

## How to Use

1. Navigate to the **Suppliers** page
2. Click the **three-dot quick actions menu** on any supplier row
3. Click **"Importar Productos"**
4. The **Import Wizard** opens with a blue info banner: "Importando productos para: {supplier_name}"
5. Upload a catalog file (PDF, Excel, or image) and proceed through extraction and review
6. In the **Confirm step**, the supplier dropdown is pre-selected and locked — no manual selection needed
7. Confirm the import — products are created in the Biblia General linked to the selected supplier

## Configuration

No new configuration required. The feature uses existing routing (`/import-wizard`) and existing backend endpoints.

## Testing

- **TypeScript check**: `cd apps/Client && npx tsc --noEmit`
- **Lint**: `cd apps/Client && npm run lint`
- **Build**: `cd apps/Client && npm run build`
- **Backend tests**: `cd apps/Server && python -m pytest tests/ -v --tb=short`
- **E2E test**: Run `/test_e2e` then execute `test_supplier_product_import_pipeline`

## Notes

- All new UI strings are in Spanish (Colombian) as per project convention
- No new libraries were added — `useSearchParams` and `useNavigate` are from `react-router-dom` (already a dependency)
- This is the final piece (TF-009) of the Trade Fair Supplier Capture pipeline, completing the flow from business card capture through to product catalog import
