# Feature: Supplier-to-Product Import Pipeline

## Metadata
issue_number: `148`
adw_id: `9477e39c`
issue_json: ``

## Feature Description
This feature connects the supplier capture flow to the existing Import Wizard by enabling the launch of the Import Wizard directly from a supplier's detail page with that supplier pre-selected. When a supplier responds with their brochure/catalog, the team can feed that document into the Import Wizard with the supplier pre-selected, so extracted products are automatically linked to the originating supplier. This completes the pipeline from business card → supplier → products in the Biblia General.

The feature involves:
1. Accepting an optional `supplier_id` URL parameter in the Import Wizard page
2. Pre-selecting and locking the supplier in the wizard when the parameter is present
3. Showing a contextual banner indicating which supplier products are being imported for
4. Adding an "Import Products" action button to the supplier quick actions menu
5. Ensuring the backend extraction/import flow properly passes through the supplier_id

## User Story
As a sourcing team member
I want to launch the Import Wizard from a supplier's profile with the supplier pre-selected
So that extracted products are automatically linked to that supplier without manual selection

## Problem Statement
Currently, after capturing a supplier's business card and creating them in the system, there's no streamlined way to import their product catalog with automatic supplier linking. Users must navigate to the Import Wizard separately and manually select the supplier during the confirm step, which is error-prone and breaks the workflow continuity.

## Solution Statement
Add a `supplier_id` query parameter to the Import Wizard route. When present, the wizard pre-selects and locks the supplier, shows a contextual banner, and skips manual supplier selection during import confirmation. An "Import Products" action is added to the supplier's quick actions menu for direct navigation.

## Relevant Files
Use these files to implement the feature:

**Frontend — Core changes:**
- `apps/Client/src/pages/kompass/ImportWizardPage.tsx` — Main wizard page. Add `useSearchParams` to read `supplier_id` from URL, fetch supplier by ID on mount, pre-select and lock supplier in the Confirm step, show contextual banner at top of page.
- `apps/Client/src/pages/kompass/SuppliersPage.tsx` — Suppliers page. Add `useNavigate` import, add `handleImportProducts` handler that navigates to `/import-wizard?supplier_id={id}`, pass it to `SupplierQuickActionsMenu`.
- `apps/Client/src/components/kompass/SupplierQuickActionsMenu.tsx` — Quick actions menu component. Add "Importar Productos" menu item with navigation callback.
- `apps/Client/src/services/kompassService.ts` — Already has `supplierService.get(id)` method for fetching a single supplier. No changes needed.

**Frontend — Routing (no changes needed):**
- `apps/Client/src/App.tsx` — Route for `/import-wizard` already exists at line 52. Query params are handled natively by React Router.

**Backend — Verify existing flow (minimal/no changes needed):**
- `apps/Server/app/api/extraction_routes.py` — The `confirm_import` endpoint already accepts `supplier_id` in `ConfirmImportRequestDTO`. No changes needed.
- `apps/Server/app/models/extraction_job_dto.py` — `ConfirmImportRequestDTO` already has `supplier_id: UUID` field. No changes needed.
- `apps/Server/app/services/extraction_service.py` — Extraction service processes files independently of supplier. Supplier linking happens at import confirmation time via `ConfirmImportRequestDTO.supplier_id`. No changes needed.

**E2E Test reference files:**
- `.claude/commands/test_e2e.md` — E2E test runner instructions
- `.claude/commands/e2e/test_import_wizard.md` — Existing Import Wizard E2E test for reference

### New Files
- `.claude/commands/e2e/test_supplier_product_import_pipeline.md` — E2E test for the supplier-to-product import pipeline feature

## Implementation Plan

### Phase 1: Foundation
Verify the backend already supports the required flow. The `ConfirmImportRequestDTO` already accepts `supplier_id` as a required field, and the `confirm_import` route already uses it to set `supplier_id` on all created products. The `supplierService.get(id)` frontend method already exists. No backend changes are needed.

### Phase 2: Core Implementation
1. Modify `ImportWizardPage.tsx` to read `supplier_id` from URL query params using `useSearchParams`
2. When `supplier_id` is present, fetch the supplier on mount and store it in state
3. Show a contextual banner at the top: "Importando productos para: {supplier_name}"
4. In the Confirm step, pre-select the supplier and disable the supplier dropdown
5. Add "Importar Productos" to `SupplierQuickActionsMenu` with navigation to `/import-wizard?supplier_id={id}`
6. Wire up the new action in `SuppliersPage.tsx`

### Phase 3: Integration
- Handle invalid `supplier_id` (supplier not found) with an error alert and fallback to normal wizard flow
- Ensure draft save/load works correctly with pre-selected supplier context
- Verify the complete flow: Suppliers page → Import Products action → Import Wizard with pre-selected supplier → Extract → Review → Confirm → Products appear in Biblia General linked to supplier

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create E2E Test Specification
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_import_wizard.md` to understand the E2E test format
- Create `.claude/commands/e2e/test_supplier_product_import_pipeline.md` with test scenarios:
  - Navigate to Suppliers page, find a supplier, click quick actions → "Importar Productos"
  - Verify Import Wizard opens with supplier context banner showing supplier name
  - Verify supplier dropdown is pre-selected and disabled/locked in Confirm step
  - Test with invalid supplier_id — verify error alert and fallback to normal flow
  - Test navigating directly to `/import-wizard` (no supplier_id) — verify normal flow still works

### Step 2: Modify SupplierQuickActionsMenu Component
- Open `apps/Client/src/components/kompass/SupplierQuickActionsMenu.tsx`
- Add a new prop `onImportProducts: (supplier: SupplierResponse) => void`
- Add a new menu item "Importar Productos" with an appropriate icon (e.g., `Inventory2Icon` or `LibraryBooksIcon`) before the "Change Pipeline Status" item
- Wire the click handler to call `onImportProducts(supplier)` after closing the menu

### Step 3: Modify SuppliersPage to Handle Import Products Action
- Open `apps/Client/src/pages/kompass/SuppliersPage.tsx`
- Import `useNavigate` from `react-router-dom`
- Add `handleImportProducts` callback that navigates to `/import-wizard?supplier_id=${supplier.id}`
- Pass `handleImportProducts` as the `onImportProducts` prop to `SupplierQuickActionsMenu`

### Step 4: Modify ImportWizardPage — Read URL Parameter and Fetch Supplier
- Open `apps/Client/src/pages/kompass/ImportWizardPage.tsx`
- Import `useSearchParams` from `react-router-dom`
- Import `supplierService` (already imported)
- Add state: `preSelectedSupplier: SupplierResponse | null`, `preSelectedSupplierError: string | null`, `preSelectedSupplierLoading: boolean`
- Add a `useEffect` that reads `supplier_id` from search params on mount:
  - If `supplier_id` is present, call `supplierService.get(supplier_id)` to fetch the supplier
  - On success: set `preSelectedSupplier` and set `selectedSupplierId` to the supplier's ID
  - On error (404/network): set `preSelectedSupplierError` with a user-friendly message in Spanish

### Step 5: Modify ImportWizardPage — Add Contextual Banner
- Below the page title "Product Import Wizard", add a conditional `Alert` component (severity="info"):
  - Show when `preSelectedSupplier` is set: "Importando productos para: {preSelectedSupplier.name}"
  - Show loading state while fetching the supplier
- If `preSelectedSupplierError` is set, show an error `Alert` with the error message, allowing the user to proceed with normal wizard flow

### Step 6: Modify ImportWizardPage — Lock Supplier in Confirm Step
- In the `renderConfirmStep` function, modify the Supplier `Select` component:
  - When `preSelectedSupplier` is set, set the `Select` to `disabled` and display the pre-selected supplier
  - Ensure `selectedSupplierId` is already set from Step 4's useEffect, so no manual selection is needed
  - Optionally add a small `Chip` or helper text indicating "Pre-seleccionado desde proveedor"

### Step 7: Ensure Draft Save/Load Handles Pre-Selected Supplier
- The draft save already includes `supplierId` in `DraftData` — no structural changes needed
- When loading a draft, if `preSelectedSupplier` is set from URL, the URL-supplied supplier should take priority over the draft's saved supplier
- No code changes expected here — the useEffect in Step 4 runs after draft loading and will override with URL param

### Step 8: Run Validation Commands
- Run TypeScript type checking: `cd apps/Client && npx tsc --noEmit`
- Run ESLint: `cd apps/Client && npm run lint`
- Run frontend build: `cd apps/Client && npm run build`
- Run backend tests: `cd apps/Server && python -m pytest tests/ -v --tb=short` (verify no regressions)
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_supplier_product_import_pipeline.md` E2E test

## Testing Strategy

### Unit Tests
- No new backend unit tests needed — the backend flow (`confirm_import` with `supplier_id`) is already tested
- Frontend testing is covered by TypeScript compilation, ESLint, and E2E tests

### Edge Cases
- `supplier_id` in URL is an invalid UUID format — `supplierService.get()` will return a 400/422 error, caught by error handler
- `supplier_id` references a deleted/non-existent supplier — 404 error, caught by error handler, user sees error alert and can proceed normally
- User navigates to Import Wizard without `supplier_id` — normal wizard flow, no changes
- User navigates with `supplier_id` but then refreshes — `useSearchParams` reads from URL on mount, so supplier is re-fetched
- Draft loading with a different supplier than URL param — URL param takes priority
- Multiple suppliers with same name — no issue, we use UUID-based supplier_id

## Acceptance Criteria
- Import Wizard accepts `supplier_id` query parameter and pre-selects the supplier
- Contextual banner shows "Importando productos para: {supplier_name}" when supplier_id is present
- Supplier dropdown is disabled/locked when supplier is pre-selected from URL
- "Importar Productos" menu item appears in supplier quick actions menu on SuppliersPage
- Clicking "Importar Productos" navigates to `/import-wizard?supplier_id={supplier_id}`
- Invalid `supplier_id` shows an error alert and falls back to normal wizard flow
- Normal Import Wizard flow (without `supplier_id`) continues to work unchanged
- Products imported via this flow appear in Biblia General linked to the correct supplier
- All UI text for new elements is in Spanish (Colombian)
- TypeScript compilation passes with zero errors
- ESLint passes with zero errors
- Frontend build succeeds

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Client && npx tsc --noEmit` — Run Client TypeScript check to validate no type errors
- `cd apps/Client && npm run lint` — Run Client ESLint to validate no lint errors
- `cd apps/Client && npm run build` — Run Client production build to validate the feature compiles
- `cd apps/Server && python -m pytest tests/ -v --tb=short` — Run Server tests to validate zero regressions
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_supplier_product_import_pipeline.md` to validate this functionality works end-to-end

## Notes
- **No backend changes required**: The existing `ConfirmImportRequestDTO` already accepts `supplier_id`, and the `confirm_import` endpoint already uses it to set `supplier_id` on all created `ProductCreateDTO` objects. The supplier linking happens at import confirmation time, not during extraction.
- **No new libraries needed**: All required functionality (`useSearchParams`, `useNavigate`) is available from `react-router-dom` which is already a dependency.
- **UI Language**: All new UI strings should be in Spanish (Colombian) as per project convention. Key strings: "Importar Productos", "Importando productos para:", "Pre-seleccionado desde proveedor", "Proveedor no encontrado. Puede seleccionar uno manualmente."
- **This is the final issue (TF-009)** in the Trade Fair Supplier Capture system. It completes the end-to-end pipeline: business card → supplier → products.
