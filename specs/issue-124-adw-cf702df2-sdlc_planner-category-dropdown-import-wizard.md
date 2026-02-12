# Feature: Add Category Dropdown to Import Wizard Confirm Step

## Metadata
issue_number: `124`
adw_id: `cf702df2`
issue_json: ``

## Feature Description
Add a Category dropdown to the Import Wizard's confirm step (Step 3) so users can optionally assign a category to all products being imported. The backend already supports `category_id` in the `ConfirmImportRequestDTO` (SCD-001 complete), but the frontend `ImportWizardPage.tsx` has no Category selector — only a Supplier dropdown. This feature also adds a "Unit" column to the `ExtractedProductTable` to display `unit_of_measure` values detected during extraction.

## User Story
As a **Kompass user importing products from supplier catalogs**
I want to **select a category from a dropdown when confirming an import**
So that **all imported products are automatically assigned to the correct category, saving me from updating each product individually afterward**

## Problem Statement
After SCD-001 added `category_id` to the backend `ConfirmImportRequestDTO`, there is no corresponding UI for users to select a category during the Import Wizard's confirm step. Users must currently import products without a category and then manually assign categories afterward. Additionally, the `unit_of_measure` field extracted by the AI is not visible during the review step, preventing users from verifying this data before import.

## Solution Statement
1. Add a Category `Autocomplete` dropdown below the existing Supplier `Select` in the confirm step (Step 3) of `ImportWizardPage.tsx`. Categories will be loaded from `categoryService.getTree()` and flattened into a list with hierarchical path labels (e.g., "BAÑOS > Griferías"). The selection is optional.
2. Update the `ConfirmImportRequestDTO` TypeScript interface to include `category_id?: string`.
3. Pass the selected `category_id` in the confirm import API call.
4. Add a "Unit" column to `ExtractedProductTable` to show `unit_of_measure` when present.
5. Add `unit_of_measure` to the frontend `ExtractedProduct` TypeScript type.

## Relevant Files
Use these files to implement the feature:

- `apps/Client/src/pages/kompass/ImportWizardPage.tsx` — Main file to modify. Contains the 4-step wizard including the confirm step (Step 3) with the Supplier dropdown at lines 574-587, import handler at lines 306-332, and data loading at lines 157-166.
- `apps/Client/src/components/kompass/ExtractedProductTable.tsx` — Table component displaying extracted products. Needs a new "Unit" column for `unit_of_measure`.
- `apps/Client/src/types/kompass.ts` — TypeScript type definitions. The `ExtractedProduct` interface (line 997) needs `unit_of_measure` added. The `ConfirmImportRequestDTO` interface (line 1028) needs `category_id` added. `CategoryTreeNode` (line 152) is already defined with `path` field.
- `apps/Client/src/services/kompassService.ts` — Contains `categoryService.getTree()` (line 399) which returns `CategoryTreeNode[]`. Also contains `extractionService.confirmImport()` (line 912).
- `apps/Server/app/models/extraction_job_dto.py` — Backend DTO already has `category_id: Optional[UUID] = None` on the `ConfirmImportRequestDTO` (line 51). No backend changes needed.
- `apps/Server/app/models/extraction_dto.py` — Backend `ExtractedProduct` already has `unit_of_measure: Optional[str]` (line 32). No backend changes needed.
- `apps/Server/app/api/extraction_routes.py` — Backend `confirm_import` endpoint already maps `request.category_id` to products (line 428). No backend changes needed.
- `.claude/commands/test_e2e.md` — Read this to understand how to create and run E2E test files.
- `.claude/commands/e2e/test_import_wizard.md` — Existing E2E test for the Import Wizard. Reference for the new category dropdown E2E test.

### New Files
- `.claude/commands/e2e/test_import_wizard_category_dropdown.md` — E2E test spec validating the new category dropdown and unit of measure column.

## Implementation Plan
### Phase 1: Foundation — Type Updates
Update TypeScript type definitions to match the backend DTOs that already support `category_id` and `unit_of_measure`. This ensures type safety before modifying components.

### Phase 2: Core Implementation — Component Changes
1. Add the "Unit" column to `ExtractedProductTable` to display `unit_of_measure`.
2. Add category state, loading logic, tree flattening utility, and the Category `Autocomplete` dropdown to `ImportWizardPage.tsx`.
3. Wire `category_id` into the confirm import request payload.
4. Persist `categoryId` in draft data for save/load draft functionality.

### Phase 3: Integration — Testing & Validation
1. Create E2E test spec for the new functionality.
2. Run TypeScript type checks, build, and existing tests to ensure zero regressions.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Update `ExtractedProduct` TypeScript type
- Open `apps/Client/src/types/kompass.ts`
- Add `unit_of_measure: string | null;` to the `ExtractedProduct` interface (after `source_page` at line 1009)
- This matches the backend `ExtractedProduct.unit_of_measure: Optional[str]`

### Step 2: Update `ConfirmImportRequestDTO` TypeScript type
- Open `apps/Client/src/types/kompass.ts`
- Add `category_id?: string;` to the `ConfirmImportRequestDTO` interface (after `supplier_id` at line 1031)
- This matches the backend `ConfirmImportRequestDTO.category_id: Optional[UUID]`

### Step 3: Add "Unit" column to `ExtractedProductTable`
- Open `apps/Client/src/components/kompass/ExtractedProductTable.tsx`
- Add a new `<TableCell>` header "Unit" between MOQ and Confidence columns (after line 98)
- Add a corresponding `<TableCell>` in the table body row that displays `product.unit_of_measure || '—'` as plain text (read-only, not editable)
- Keep it simple — no editing needed for unit of measure

### Step 4: Create E2E test spec for category dropdown
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_import_wizard.md` to understand the E2E test format
- Create `.claude/commands/e2e/test_import_wizard_category_dropdown.md` with test scenarios:
  - **Scenario 1**: Navigate to Import Wizard confirm step and verify the Category dropdown renders below the Supplier dropdown
  - **Scenario 2**: Verify categories load and display with hierarchical path labels (e.g., "BAÑOS > Griferías")
  - **Scenario 3**: Select a category and verify it appears as selected
  - **Scenario 4**: Clear category selection and verify import still works without a category (optional field)
  - **Scenario 5**: Verify the "Unit" column appears in the extracted products review table with values when data is available
  - Include success criteria and screenshots

### Step 5: Add category state and loading to `ImportWizardPage.tsx`
- Open `apps/Client/src/pages/kompass/ImportWizardPage.tsx`
- Import `categoryService` alongside existing `supplierService` import (line 34):
  ```typescript
  import { supplierService, productService, extractionService, categoryService } from '@/services/kompassService';
  ```
- Import `CategoryTreeNode` type (line 36):
  ```typescript
  import type { ExtractedProduct, SupplierResponse, ProductResponse, CategoryTreeNode } from '@/types/kompass';
  ```
- Import `Autocomplete` and `TextField` from MUI (add to the MUI import block at line 2):
  ```typescript
  Autocomplete, TextField,
  ```
  Note: `TextField` may already be imported — check first. If not imported at the top level, add it.
- Add state variables in the "Confirm step state" section (after line 146):
  ```typescript
  const [categories, setCategories] = useState<CategoryTreeNode[]>([]);
  const [selectedCategoryId, setSelectedCategoryId] = useState<string>('');
  ```

### Step 6: Add category tree flattening utility
- Inside `ImportWizardPage.tsx`, before the component function (or inside using `useMemo`), add a utility to flatten the category tree into a flat list with path labels:
  ```typescript
  interface FlatCategory {
    id: string;
    label: string; // e.g., "BAÑOS > Griferías"
  }
  ```
- Create a `flattenCategoryTree` function that recursively walks `CategoryTreeNode[]` building path strings using `>` separator:
  ```typescript
  function flattenCategoryTree(nodes: CategoryTreeNode[], parentPath = ''): FlatCategory[] {
    const result: FlatCategory[] = [];
    for (const node of nodes) {
      if (!node.is_active) continue;
      const label = parentPath ? `${parentPath} > ${node.name}` : node.name;
      result.push({ id: node.id, label });
      if (node.children.length > 0) {
        result.push(...flattenCategoryTree(node.children, label));
      }
    }
    return result;
  }
  ```
- Use `useMemo` in the component to compute `flatCategories` from `categories`:
  ```typescript
  const flatCategories = useMemo(() => flattenCategoryTree(categories), [categories]);
  ```

### Step 7: Load categories in the confirm step effect
- In the existing `useEffect` that loads suppliers when `activeStep === 3` (lines 157-166), add a call to load categories:
  ```typescript
  categoryService.getTree().then((tree) => {
    setCategories(tree);
  });
  ```

### Step 8: Add Category Autocomplete dropdown to confirm step UI
- In the `renderConfirmStep()` function (line 557), after the Supplier `FormControl` (line 587), add the Category `Autocomplete`:
  ```typescript
  <Autocomplete
    options={flatCategories}
    getOptionLabel={(option) => option.label}
    value={flatCategories.find(c => c.id === selectedCategoryId) || null}
    onChange={(_, newValue) => setSelectedCategoryId(newValue?.id || '')}
    renderInput={(params) => (
      <TextField
        {...params}
        label="Category"
        helperText="Optional — assign all products to this category"
      />
    )}
    sx={{ mb: 2 }}
    isOptionEqualToValue={(option, value) => option.id === value.id}
  />
  ```

### Step 9: Include `category_id` in the confirm import request
- In the `handleImport` callback (line 306), update the `extractionService.confirmImport()` call to include `category_id`:
  ```typescript
  const response = await extractionService.confirmImport({
    job_id: jobId,
    product_indices: productIndices,
    supplier_id: selectedSupplierId,
    category_id: selectedCategoryId || undefined,
  });
  ```

### Step 10: Persist category in draft save/load
- Update the `DraftData` interface (line 55) to include `categoryId`:
  ```typescript
  interface DraftData {
    filesMetadata: Array<{ name: string; size: number; type: string }>;
    extractedProducts: ExtractedProduct[];
    selectedIndices: number[];
    supplierId: string | null;
    categoryId: string | null;
  }
  ```
- Update `handleSaveDraft` to include `categoryId: selectedCategoryId || null`
- Update `handleLoadDraft` to restore `selectedCategoryId` from `draft.categoryId`

### Step 11: Run validation commands
- Run TypeScript type check: `cd apps/Client && npx tsc --noEmit`
- Run frontend build: `cd apps/Client && npm run build`
- Run backend tests: `cd apps/Server && .venv/bin/pytest tests/ -v --tb=short`
- Run ESLint: `cd apps/Client && npm run lint`
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_import_wizard_category_dropdown.md` to validate the new functionality works

## Testing Strategy
### Unit Tests
- No new unit tests needed for this change — the backend already has tests for `category_id` in `TestConfirmImportFieldMapping` (see `tests/test_extraction_routes.py` line 365)
- Frontend changes are UI-only and validated via TypeScript type checking, build, and E2E tests

### Edge Cases
- **No category selected**: Import should work normally without sending `category_id` (field is optional)
- **Empty category tree**: Autocomplete should render with no options and allow proceeding without selection
- **Inactive categories**: Should be filtered out by `flattenCategoryTree` (check `is_active`)
- **Deep category hierarchy**: Path labels should correctly concatenate all ancestors (e.g., "A > B > C > D")
- **Draft with deleted category**: If a saved draft references a category that no longer exists, the Autocomplete should show no selection (graceful degradation via `find()` returning `undefined`)
- **Unit of measure null/empty**: Table should display '—' dash when `unit_of_measure` is null or undefined

## Acceptance Criteria
- [ ] Category dropdown renders in confirm step below Supplier dropdown
- [ ] Categories load from the API on component mount (when reaching Step 3)
- [ ] Categories display with hierarchical path (e.g., "BAÑOS > Griferías")
- [ ] Category selection is optional (import works without selecting one)
- [ ] Selected `category_id` is sent in the confirm import request body
- [ ] Unit of measure column appears in extracted products table when data is available
- [ ] Existing import flow still works (no regressions)
- [ ] TypeScript strict mode passes (`npx tsc --noEmit`)
- [ ] Frontend builds successfully (`npm run build`)
- [ ] Backend tests pass (`pytest tests/ -v --tb=short`)
- [ ] Draft save/load preserves category selection

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate TypeScript types are correct
- `cd apps/Client && npm run lint` — Run ESLint to catch code quality issues
- `cd apps/Client && npm run build` — Run Client build to validate the feature compiles with zero regressions
- `cd apps/Server && .venv/bin/pytest tests/ -v --tb=short` — Run Server tests to validate no backend regressions
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_import_wizard_category_dropdown.md` E2E test file to validate this functionality works

## Notes
- **No backend changes needed**: SCD-001 already added `category_id` to `ConfirmImportRequestDTO` and `unit_of_measure` to `ExtractedProduct` on the backend. This is a frontend-only feature.
- **MUI Autocomplete vs Select**: Using `Autocomplete` instead of `Select` because it supports search/filtering, which is important for potentially long category lists with hierarchical paths.
- **CategoryTreeNode.path field**: The `CategoryTreeNode` interface already has a `path` field, but we build the label manually from the tree structure to ensure correct hierarchical display regardless of the `path` format.
- **Parallel execution**: This issue runs in parallel with SCD-003 (Batch Product Import). They touch completely different files — this modifies frontend components while SCD-003 creates `scripts/import_products.py`.
- **No new libraries required**: All UI components (`Autocomplete`, `TextField`) are already available in MUI.
