# Feature: Add Category Dropdown to Import Wizard Confirm Step

## Metadata
issue_number: `124`
adw_id: `7002513d`
issue_json: ``

## Feature Description
Add a Category dropdown to the Import Wizard's confirm step (Step 3) so users can optionally assign a category to all imported products. The backend already accepts `category_id` in `ConfirmImportRequestDTO` (added by SCD-001), so this is a frontend-only change. Additionally, display the `unit_of_measure` field in the extracted products review table when the data is available from the extraction. The backend `ExtractedProduct` model already includes `unit_of_measure`, but the frontend type and table component do not yet surface it.

## User Story
As a Kompass user importing products from supplier catalogs
I want to assign a category to all imported products during the import confirmation step
So that products are automatically categorized upon import without needing to manually categorize each one afterward

## Problem Statement
The Import Wizard's confirm step (Step 3) currently only allows selecting a supplier. After SCD-001 added `category_id` support to the backend's `ConfirmImportRequestDTO`, there is no UI for users to specify a category during import. Users must manually categorize products after import, which is time-consuming when importing entire supplier catalogs. Additionally, the `unit_of_measure` field extracted by the AI is not displayed during review, meaning users cannot verify this information before importing.

## Solution Statement
1. Add a Category `Autocomplete` dropdown to the confirm step below the existing Supplier dropdown. The categories are loaded from the API as a tree and flattened into a list with hierarchical path display (e.g., "BAÑOS > Griferías"). The selection is optional — if no category is chosen, products import without a category assignment.
2. Update the `ConfirmImportRequestDTO` frontend type to include the optional `category_id` field.
3. Add `unit_of_measure` to the frontend `ExtractedProduct` type and display it as a read-only "Unit" column in the `ExtractedProductTable` component.
4. Pass the selected `category_id` through the confirm import request to the backend.

## Relevant Files
Use these files to implement the feature:

- `apps/Client/src/pages/kompass/ImportWizardPage.tsx` — Main page component. Add category state, load categories on confirm step, add Autocomplete dropdown, pass category_id in import handler.
- `apps/Client/src/components/kompass/ExtractedProductTable.tsx` — Extracted products review table. Add "Unit" column for unit_of_measure display.
- `apps/Client/src/types/kompass.ts` — Type definitions. Add `unit_of_measure` to `ExtractedProduct` interface, add `category_id` to `ConfirmImportRequestDTO`.
- `apps/Client/src/services/kompassService.ts` — Service layer. Contains `categoryService.getTree()` method (already exists, no changes needed) and `extractionService.confirmImport()` (no changes needed, just passes request object).
- `apps/Server/app/models/extraction_job_dto.py` — Backend DTO reference. `ConfirmImportRequestDTO` already has `category_id: Optional[UUID] = None` (line 51). No changes needed.
- `apps/Server/app/models/extraction_dto.py` — Backend DTO reference. `ExtractedProduct` already has `unit_of_measure: Optional[str]` (line 32). No changes needed.
- Read `.claude/commands/test_e2e.md` to understand E2E test runner format.
- Read `.claude/commands/e2e/test_import_wizard.md` to understand existing Import Wizard E2E test patterns.

### New Files
- `.claude/commands/e2e/test_category_dropdown_import_wizard.md` — E2E test specification for the new category dropdown functionality.

## Implementation Plan
### Phase 1: Foundation (Type Updates)
Update the frontend TypeScript types to match the backend DTOs. Add `unit_of_measure` to `ExtractedProduct` and `category_id` to `ConfirmImportRequestDTO`. These are the shared types that both the page and table component depend on.

### Phase 2: Core Implementation (UI Components)
1. Add the "Unit" column to `ExtractedProductTable` to display `unit_of_measure` when available.
2. Add category state, loading logic, tree flattening utility, and `Autocomplete` dropdown to `ImportWizardPage.tsx`.
3. Update the import handler to include `category_id` in the confirm request.

### Phase 3: Integration (Testing & Validation)
1. Create E2E test specification for the new category dropdown.
2. Run TypeScript checks, lint, and build to validate no regressions.
3. Execute E2E test to validate the feature works end-to-end.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Update ExtractedProduct Type
- Open `apps/Client/src/types/kompass.ts`
- Add `unit_of_measure: string | null;` to the `ExtractedProduct` interface (after `source_page`, around line 1009)
- This matches the backend `ExtractedProduct` model which already has `unit_of_measure: Optional[str]`

### Step 2: Update ConfirmImportRequestDTO Type
- In `apps/Client/src/types/kompass.ts`, add `category_id?: string;` to the `ConfirmImportRequestDTO` interface (after `supplier_id`, around line 1031)
- This makes `category_id` optional on the frontend to match the backend's `Optional[UUID]`

### Step 3: Add Unit Column to ExtractedProductTable
- Open `apps/Client/src/components/kompass/ExtractedProductTable.tsx`
- Add a new `<TableCell>` header "Unit" between "MOQ" and "Confidence" columns (after line 98):
  ```
  <TableCell sx={{ minWidth: 80 }}>Unit</TableCell>
  ```
- Add a corresponding `<TableCell>` in the table body (after the MOQ cell, around line 193) that displays the `unit_of_measure` value:
  ```tsx
  <TableCell>
    <Typography variant="body2" sx={{ fontSize: '0.875rem' }}>
      {product.unit_of_measure || '—'}
    </Typography>
  </TableCell>
  ```
- Import `Typography` from `@mui/material` if not already imported

### Step 4: Create E2E Test Specification
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_import_wizard.md` for format reference
- Create `.claude/commands/e2e/test_category_dropdown_import_wizard.md` with test scenarios:
  - Navigate to Import Wizard confirm step (Step 4)
  - Verify Category Autocomplete dropdown renders below Supplier dropdown
  - Verify categories load and display with hierarchical paths (e.g., "BAÑOS > Griferías")
  - Verify category selection is optional (import works without selecting one)
  - Verify selecting a category and importing includes category_id in request
  - Verify Unit column appears in the review table (Step 3)
  - Screenshot each key state

### Step 5: Add Category Dropdown to ImportWizardPage — State and Loading
- Open `apps/Client/src/pages/kompass/ImportWizardPage.tsx`
- Add imports at top of file:
  - `Autocomplete` and `TextField` from `@mui/material` (TextField may already be imported indirectly — check)
  - `CategoryTreeNode` from `@/types/kompass`
  - `categoryService` from `@/services/kompassService`
- Add state variables near the existing confirm step state (after line 143):
  ```typescript
  const [categories, setCategories] = useState<CategoryTreeNode[]>([]);
  const [selectedCategoryId, setSelectedCategoryId] = useState<string>('');
  ```
- Add a helper function to flatten the category tree into a flat list with path labels:
  ```typescript
  interface FlatCategory {
    id: string;
    label: string;
  }

  const flattenCategoryTree = (nodes: CategoryTreeNode[], parentPath = ''): FlatCategory[] => {
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
  };
  ```
- Add a `useMemo` to compute flat categories:
  ```typescript
  const flatCategories = useMemo(() => flattenCategoryTree(categories), [categories]);
  ```
- Extend the existing `useEffect` at line 157 that loads suppliers when `activeStep === 3` to also load categories:
  ```typescript
  categoryService.getTree().then((tree) => {
    setCategories(tree);
  });
  ```

### Step 6: Add Category Autocomplete to Confirm Step UI
- In the `renderConfirmStep` function (line 557), add the Category Autocomplete below the existing Supplier `<FormControl>` (after line 587, before the duplicate SKU warning):
  ```tsx
  <Autocomplete
    options={flatCategories}
    getOptionLabel={(option) => option.label}
    value={flatCategories.find((c) => c.id === selectedCategoryId) || null}
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

### Step 7: Update Import Handler to Include category_id
- In the `handleImport` callback (line 306), update the `extractionService.confirmImport()` call to include `category_id`:
  ```typescript
  const response = await extractionService.confirmImport({
    job_id: jobId,
    product_indices: productIndices,
    supplier_id: selectedSupplierId,
    category_id: selectedCategoryId || undefined,
  });
  ```
- Add `selectedCategoryId` to the `useCallback` dependency array (line 332)

### Step 8: Update Draft Save/Load to Include Category
- In the `handleSaveDraft` function (line 334), add `categoryId` to the draft data:
  ```typescript
  const draft: DraftData = {
    filesMetadata: selectedFiles.map((f) => ({ name: f.name, size: f.size, type: f.type })),
    extractedProducts: editedProducts,
    selectedIndices: Array.from(selectedIndices),
    supplierId: selectedSupplierId || null,
    categoryId: selectedCategoryId || null,
  };
  ```
- Update the `DraftData` interface to include `categoryId: string | null`
- In the draft loading logic, restore `selectedCategoryId` from the draft:
  ```typescript
  if (draft.categoryId) {
    setSelectedCategoryId(draft.categoryId);
  }
  ```

### Step 9: Run Validation Commands
- Run TypeScript type check: `cd apps/Client && npx tsc --noEmit`
- Run ESLint: `cd apps/Client && npm run lint`
- Run build: `cd apps/Client && npm run build`
- Run backend tests: `cd apps/Server && .venv/bin/pytest tests/ -v --tb=short`
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_category_dropdown_import_wizard.md` to validate E2E

## Testing Strategy
### Unit Tests
- No new unit tests needed — this is a frontend-only UI change with no new business logic. The backend already has tests for `category_id` in `ConfirmImportRequestDTO` (in `tests/test_extraction_routes.py`).
- TypeScript type checking validates the type changes compile correctly.

### Edge Cases
- No categories exist in the database: Autocomplete shows empty list, user can still import without category
- Category tree is deeply nested: Path labels remain readable (e.g., "Level1 > Level2 > Level3")
- User selects a category then clears it: `category_id` should not be sent (undefined, not empty string)
- Draft saved with category, categories list changes before draft load: Selected category may not match — Autocomplete will show null, which is acceptable
- ExtractedProduct has no `unit_of_measure`: Column shows "—" dash placeholder
- All products have `unit_of_measure`: Column shows values like "m2", "piece", "meter"

## Acceptance Criteria
- [ ] Category Autocomplete dropdown renders in confirm step below Supplier dropdown
- [ ] Categories load from the API via `categoryService.getTree()` when entering confirm step
- [ ] Categories display with hierarchical path notation (e.g., "BAÑOS > Griferías")
- [ ] Category selection is optional — import works without selecting a category
- [ ] Selected `category_id` is included in the confirm import request body
- [ ] When no category is selected, `category_id` is not sent (undefined)
- [ ] Unit of measure column appears in the extracted products review table
- [ ] Unit column shows value when available, "—" when not
- [ ] Draft save/load preserves category selection
- [ ] Existing import flow still works with no regressions
- [ ] TypeScript strict mode passes (`npx tsc --noEmit`)
- [ ] ESLint passes (`npm run lint`)
- [ ] Production build succeeds (`npm run build`)

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Client && npx tsc --noEmit` — Run TypeScript type check to verify no type errors
- `cd apps/Client && npm run lint` — Run ESLint to verify no lint errors
- `cd apps/Client && npm run build` — Run production build to verify no build errors
- `cd apps/Server && .venv/bin/pytest tests/ -v --tb=short` — Run backend tests to verify no regressions
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_category_dropdown_import_wizard.md` E2E test file to validate this functionality works

## Notes
- **Backend is already ready**: `ConfirmImportRequestDTO` has `category_id: Optional[UUID] = None` and `ExtractedProduct` has `unit_of_measure: Optional[str]`. No backend changes needed.
- **Parallel execution safe**: This issue only modifies `ImportWizardPage.tsx`, `ExtractedProductTable.tsx`, and `kompass.ts` types — no overlap with SCD-003 which creates `scripts/import_products.py`.
- **Autocomplete vs Select**: Using MUI `Autocomplete` instead of `Select` because it provides type-ahead search, which is much better UX for a potentially long hierarchical category list.
- **Tree flattening**: The `flattenCategoryTree` helper recursively walks `CategoryTreeNode[]` building path strings. Only active categories (`is_active: true`) are included.
- **No new dependencies**: All MUI components used (`Autocomplete`, `TextField`) are already available in the project.
