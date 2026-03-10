# Feature: Add WeChat ID Field to Supplier Data Model

## Metadata
issue_number: `163`
adw_id: `9167a7c8`
issue_json: ``

## Feature Description
Add a dedicated `wechat_id` optional text field to the suppliers data model and propagate it through all application layers: backend DTOs, repository, service, API endpoints, frontend types, and UI forms. The database column already exists in `schema.sql` (line 137: `wechat_id VARCHAR(100)`), so no migration is needed. The field is already used by the trade fair card capture flow (`create_with_trade_fair_metadata`) and outreach system — this feature closes the gap by making it visible and editable through the standard supplier CRUD operations.

## User Story
As a Kompass user managing Chinese suppliers
I want to view and edit WeChat ID directly on the supplier form
So that I can store and reference supplier WeChat contact information for messaging without relying solely on the business card capture flow

## Problem Statement
The `wechat_id` column exists in the database and is already populated by the business card capture workflow, but the standard supplier CRUD path (create/edit forms, list views, DTOs, repository queries) does not include it. Users cannot see or edit WeChat IDs through the supplier management UI.

## Solution Statement
Propagate the `wechat_id` field through all layers of the supplier CRUD stack: backend DTOs, repository SELECT/INSERT/UPDATE queries, service pass-through, frontend TypeScript types, and the SupplierForm component. The field is optional, max 100 characters, no special format validation needed.

## Relevant Files
Use these files to implement the feature:

**Backend — DTOs:**
- `apps/Server/app/models/kompass_dto.py` — Add `wechat_id` to `SupplierCreateDTO` (line 381), `SupplierUpdateDTO` (line 400), and `SupplierResponseDTO` (line 420)

**Backend — Repository:**
- `apps/Server/app/repository/kompass_repository.py` — Add `wechat_id` to:
  - `create()` method (line 1268): function signature, INSERT columns, VALUES, params
  - `get_by_id()` method (line 1407): SELECT columns
  - `get_all()` method (line 1436): SELECT columns
  - `update()` method (line 1496): function signature, SET clause, RETURNING columns
  - `_row_to_dict()` method (line 1696): add mapping at row[12], shift `created_at`/`updated_at` to row[13]/row[14]
  - `_row_to_dict_extended()` method (line 2210): verify if wechat_id needs adding (extended queries already return different fields)

**Backend — Service:**
- `apps/Server/app/services/supplier_service.py` — Add `wechat_id` pass-through in:
  - `create_supplier()` (line 94): pass `wechat_id=request.wechat_id` to repository
  - `update_supplier()` (line 252): add `wechat_id` to `update_kwargs` dict

**Frontend — Types:**
- `apps/Client/src/types/kompass.ts` — Add `wechat_id` to `SupplierCreate` (line 232), `SupplierUpdate` (line 246), `SupplierResponse` (line 262)

**Frontend — Form Component:**
- `apps/Client/src/components/kompass/SupplierForm.tsx` — Add `wechat_id` to:
  - `FormData` interface (line 30)
  - Default values (line 82)
  - Edit reset (line 102)
  - Create reset (line 116)
  - Submit payload (line 138)
  - UI: new TextField after contact_phone (line 293)

**Frontend — Service:**
- `apps/Client/src/services/kompassService.ts` — Generic methods, no changes needed (auto-handles new fields)

**Database:**
- `apps/Server/database/schema.sql` — Already has `wechat_id VARCHAR(100)` at line 137, no changes needed

**E2E Test Reference:**
- `.claude/commands/test_e2e.md` — E2E test runner instructions
- `.claude/commands/e2e/test_basic_query.md` — E2E test format example
- `.claude/commands/e2e/test_suppliers_page.md` — Existing suppliers page E2E test

### New Files
- `.claude/commands/e2e/test_supplier_wechat_id.md` — E2E test for WeChat ID field on supplier form

## Implementation Plan
### Phase 1: Foundation (Backend DTOs + Repository)
Add `wechat_id` to the Pydantic DTOs and all repository SQL queries so the field flows through the data layer. The key challenge is updating `_row_to_dict()` — adding a column to SELECT queries shifts all subsequent row indices.

### Phase 2: Core Implementation (Service + Frontend Types + Form UI)
Wire the field through the service layer and add it to the frontend TypeScript interfaces and SupplierForm component with a new TextField.

### Phase 3: Integration (E2E Test)
Create an E2E test that validates the WeChat ID field appears on the supplier form, can be filled during creation, persists after save, and is editable.

## Step by Step Tasks

### Step 1: Add `wechat_id` to Backend DTOs
- In `apps/Server/app/models/kompass_dto.py`:
  - **SupplierCreateDTO** (after `contact_phone` field, line 381): Add `wechat_id: Optional[str] = Field(default=None, max_length=100, description="WeChat ID for supplier contact")`
  - **SupplierUpdateDTO** (after `contact_phone` field, line 400): Add `wechat_id: Optional[str] = Field(default=None, max_length=100, description="WeChat ID for supplier contact")`
  - **SupplierResponseDTO** (after `contact_phone` field, line 420): Add `wechat_id: Optional[str] = None`

### Step 2: Add `wechat_id` to Repository `create()` method
- In `apps/Server/app/repository/kompass_repository.py`, method `create()` (line 1268):
  - Add `wechat_id: Optional[str] = None` parameter to function signature (after `notes`)
  - Add `wechat_id` to the INSERT column list (line 1291-1293): append `, wechat_id` after `notes`
  - Add one more `%s` placeholder to VALUES (line 1295): 12 placeholders total
  - Add `wechat_id` to the RETURNING clause (line 1296-1298): add `wechat_id` after `notes`
  - Add `wechat_id` to the params tuple (line 1300-1312): add `wechat_id,` after `notes,`

### Step 3: Add `wechat_id` to Repository SELECT queries and `_row_to_dict()`
- In `apps/Server/app/repository/kompass_repository.py`:
  - **`get_by_id()`** (line 1417-1419): Add `wechat_id` to SELECT, after `notes`: `SELECT id, name, code, status, contact_name, contact_email, contact_phone, address, city, country, website, notes, wechat_id, created_at, updated_at`
  - **`get_all()`** (line 1476-1478): Same SELECT change as above
  - **`_row_to_dict()`** (line 1696-1712): Insert `"wechat_id": row[12]` after `"notes": row[11]`. Shift `"created_at"` to `row[13]` and `"updated_at"` to `row[14]`.
  - **IMPORTANT**: The `create()` RETURNING clause (step 2) must also match this new column order: `id, name, code, status, contact_name, contact_email, contact_phone, address, city, country, website, notes, wechat_id, created_at, updated_at`

### Step 4: Add `wechat_id` to Repository `update()` method
- In `apps/Server/app/repository/kompass_repository.py`, method `update()` (line 1496):
  - Add `wechat_id: Optional[str] = None` parameter to function signature (after `notes`, line 1509)
  - Add update condition block after the `notes` block (after line 1552):
    ```python
    if wechat_id is not None:
        updates.append("wechat_id = %s")
        params.append(wechat_id)
    ```
  - Update the RETURNING clause (line 1565-1567) to include `wechat_id` after `notes`: `RETURNING id, name, code, status, contact_name, contact_email, contact_phone, address, city, country, website, notes, wechat_id, created_at, updated_at`

### Step 5: Add `wechat_id` pass-through in Supplier Service
- In `apps/Server/app/services/supplier_service.py`:
  - **`create_supplier()`** (line 94-106): Add `wechat_id=request.wechat_id,` to the `supplier_repository.create()` call, after `notes=request.notes,`
  - **`update_supplier()`** (line 252-274): Add to the update_kwargs building block, after the `notes` block:
    ```python
    if request.wechat_id is not None:
        update_kwargs["wechat_id"] = request.wechat_id
    ```

### Step 6: Add `wechat_id` to Frontend TypeScript Types
- In `apps/Client/src/types/kompass.ts`:
  - **SupplierCreate** (after `contact_phone`, line 238): Add `wechat_id?: string | null;`
  - **SupplierUpdate** (after `contact_phone`, line 252): Add `wechat_id?: string | null;`
  - **SupplierResponse** (after `contact_phone`, line 269): Add `wechat_id: string | null;`

### Step 7: Add `wechat_id` to SupplierForm Component
- In `apps/Client/src/components/kompass/SupplierForm.tsx`:
  - **FormData interface** (line 30-42): Add `wechat_id: string;` after `contact_phone`
  - **Default values** (line 82-94): Add `wechat_id: '',` after `contact_phone: '',`
  - **Edit reset** (line 102-114): Add `wechat_id: supplier.wechat_id || '',` after `contact_phone`
  - **Create reset** (line 116-128): Add `wechat_id: '',` after `contact_phone: '',`
  - **Submit payload** (line 138-150): Add `wechat_id: data.wechat_id || null,` after `contact_phone`
  - **UI TextField** (after contact_phone Grid item ending at line 294): Add a new `<Grid item xs={12} sm={6}>` containing a `<TextField>` for WeChat ID:
    ```tsx
    <Grid item xs={12} sm={6}>
      <TextField
        fullWidth
        label="WeChat ID"
        placeholder="ID de WeChat del proveedor"
        {...register('wechat_id', {
          maxLength: {
            value: 100,
            message: 'Máximo 100 caracteres',
          },
        })}
        error={!!errors.wechat_id}
        helperText={errors.wechat_id?.message}
        disabled={loading}
      />
    </Grid>
    ```

### Step 8: Create E2E Test for WeChat ID Field
- Create `.claude/commands/e2e/test_supplier_wechat_id.md` with test steps that:
  1. Navigate to Suppliers page
  2. Click "Add Supplier", verify "WeChat ID" field is present in the form
  3. Fill in supplier data including WeChat ID (e.g., "test_wechat_123")
  4. Save the supplier and verify it appears in the list
  5. Edit the supplier, verify WeChat ID is pre-filled with "test_wechat_123"
  6. Update WeChat ID to a new value, save, and verify the update persists
  7. Clean up: delete the test supplier
- Reference `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_basic_query.md` for format conventions

### Step 9: Run Validation Commands
- Run all validation commands listed below to ensure zero regressions

## Testing Strategy
### Unit Tests
- Backend repository tests: Verify `create()` and `update()` correctly handle `wechat_id` parameter
- Backend service tests: Verify `create_supplier()` and `update_supplier()` pass `wechat_id` through
- Frontend type checks: Verify TypeScript compilation succeeds with new field

### Edge Cases
- `wechat_id` is `null` (not provided) — should create/update supplier without error
- `wechat_id` is empty string — should be stored as `null` (frontend converts `'' → null`)
- `wechat_id` exceeds 100 characters — should be rejected by DTO validation
- Existing suppliers without `wechat_id` — should return `null` in response (backward compatible)
- Editing a supplier that already has a `wechat_id` from card capture — should show the existing value in the form

## Acceptance Criteria
- [ ] `wechat_id` field appears on the supplier create/edit form near the contact phone field
- [ ] Creating a supplier with a WeChat ID stores it in the database and returns it in the response
- [ ] Creating a supplier without a WeChat ID works without error (field is optional)
- [ ] Editing a supplier can update the WeChat ID value
- [ ] Editing a supplier pre-fills the existing WeChat ID value
- [ ] The supplier list/detail view includes the WeChat ID in the response data
- [ ] Backend DTO validates max_length of 100 characters
- [ ] All existing tests pass (zero regressions)
- [ ] TypeScript type check passes
- [ ] Frontend build succeeds

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -m pytest tests/ -v --tb=short` — Run Server tests to validate zero regressions
- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate TypeScript compilation
- `cd apps/Client && npm run build` — Run Client production build to validate no build errors
- `cd apps/Client && npm run lint` — Run Client linter to validate no lint errors
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_supplier_wechat_id.md` E2E test to validate WeChat ID field works end-to-end

## Notes
- The database column `wechat_id VARCHAR(100)` already exists in `schema.sql` (line 137) and in the live database — no migration file is needed
- The `create_with_trade_fair_metadata()` repository method (line 1327) already handles `wechat_id` — no changes needed there
- The `create_supplier_from_card()` service method (line 526) already maps `contact_wechat` to `wechat_id` — no changes needed there
- The `send_outreach()` service method already uses `wechat_id` for WeChat messaging — no changes needed there
- The `kompassService.ts` frontend service uses generic Axios methods that pass through all payload fields — no changes needed there
- The `_row_to_dict_extended()` method (line 2210) does NOT need changes because it maps a different set of columns (includes certification_status, pipeline_status, etc.) and is used by separate query methods that already have their own SELECT lists
- **Row index shift warning**: Adding `wechat_id` to `_row_to_dict()` at position row[12] shifts `created_at` and `updated_at` from [12,13] to [13,14]. ALL SELECT queries using `_row_to_dict()` must be updated in the same commit to avoid index mismatch errors
- UI label "WeChat ID" is kept in English as it is a proper noun. Helper text uses Spanish: "ID de WeChat del proveedor"
