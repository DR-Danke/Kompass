# Bug: Fix supplier name blank after card approval

## Metadata
issue_number: `168`
adw_id: `44fe017a`
issue_json: ``

## Bug Description
After approving a business card on the CardReviewPage and creating a supplier, the supplier appears in the Suppliers list with a blank name. The extracted `company_name` is either not properly sanitized before being mapped to the supplier `name` field, or whitespace-only/empty-string values bypass the fallback logic and the NOT NULL constraint. This is a P0 bug affecting the card-to-supplier workflow in the Business Card Capture (BCC) module.

**Expected behavior:** When a card is approved, the supplier `name` should be the `company_name` from the capture record. If `company_name` is missing, `contact_name` should be used as fallback with a note indicating manual review is needed.

**Actual behavior:** Suppliers are created with blank/empty names, suggesting that whitespace-only or empty-string values for `company_name` are passing the truthy check (`company_name or contact_name`) without triggering the fallback to `contact_name`.

## Problem Statement
The `create_supplier_from_card` method in `supplier_service.py` does not strip whitespace from `company_name` or `contact_name` before using them. A whitespace-only string like `" "` is truthy in Python, so `supplier_name = company_name or contact_name` evaluates to `" "` instead of falling through to `contact_name`. This whitespace-only value passes the `if not supplier_name` validation and gets inserted into the database as the supplier name, which renders as blank in the UI. Additionally, when the fallback to `contact_name` IS triggered, no note is added to indicate that manual review is needed for the supplier name.

## Solution Statement
1. **Sanitize extracted fields** in `create_supplier_from_card`: strip whitespace from `company_name` and `contact_name`, and normalize empty/whitespace-only strings to `None` so the `or` fallback works correctly.
2. **Add a fallback note**: when `company_name` is null/empty and `contact_name` is used as the supplier name, append a note to the supplier indicating that the name needs manual review.
3. **Add `contact_wechat` to `BusinessCardUpdateDTO`**: the DTO is missing this field, preventing users from editing the WeChat ID on the CardReviewPage before approval.

## Steps to Reproduce
1. Upload a business card image on the CardCapturePage
2. AI extraction runs — if `company_name` is extracted as an empty string or whitespace-only value (e.g., `" "`)
3. User navigates to CardReviewPage and clicks "Aprobar" on the card
4. Backend creates a supplier with `name=" "` (whitespace) which passes NOT NULL but displays blank
5. Navigate to SuppliersPage — the newly created supplier shows a blank name

## Root Cause Analysis
In `apps/Server/app/services/supplier_service.py` at line 556-566:

```python
company_name = capture.get("company_name")
contact_name = capture.get("contact_name")
...
supplier_name = company_name or contact_name
if not supplier_name:
    raise ValueError(...)
```

The issue is that `capture.get("company_name")` can return:
- `None` — correctly handled by `or` fallback
- `""` (empty string) — correctly handled (falsy in Python)
- `" "` or `"  "` (whitespace-only) — **NOT handled**: truthy in Python, passes validation, creates blank supplier name

Additionally, there is no note added when the code falls back from `company_name` to `contact_name`, which makes it harder for users to identify suppliers that need name review.

## Relevant Files
Use these files to fix the bug:

- `apps/Server/app/services/supplier_service.py` — Contains `create_supplier_from_card()` method (line 529). This is the primary file to fix: add whitespace stripping, normalize empty values to None, and add fallback note.
- `apps/Server/app/models/kompass_dto.py` — Contains `BusinessCardUpdateDTO` (line 675). Missing `contact_wechat` field.
- `apps/Server/tests/services/test_supplier_service.py` — Contains `TestCreateSupplierFromCard` test class (line 427). Need to add tests for whitespace handling and fallback note.
- `apps/Client/src/hooks/kompass/useCardReview.ts` — Frontend approval hook. Verify no body payload override (already confirmed correct — sends only captureId).
- `apps/Client/src/services/kompassService.ts` — Frontend service layer. Verify `approveCard` makes POST with no body (already confirmed correct at line 1320-1326).
- `apps/Client/src/pages/kompass/CardReviewPage.tsx` — Frontend review page with editable company_name cell. Verify field mapping (already confirmed correct at line 379-386).
- `.claude/commands/test_e2e.md` — E2E test runner instructions.
- `.claude/commands/e2e/test_auto_create_supplier_from_card.md` — Existing E2E test for reference on test structure.

### New Files
- `.claude/commands/e2e/test_supplier_name_card_approval.md` — New E2E test to validate supplier name is correctly populated after card approval.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### 1. Fix supplier name sanitization in `create_supplier_from_card`
- Open `apps/Server/app/services/supplier_service.py`
- In `create_supplier_from_card()` method, after extracting fields from capture (lines 556-563), add whitespace stripping and normalization:
  ```python
  # Strip and normalize empty/whitespace-only to None
  company_name = (capture.get("company_name") or "").strip() or None
  contact_name = (capture.get("contact_name") or "").strip() or None
  ```
- Keep the existing fallback logic: `supplier_name = company_name or contact_name`
- Keep the existing validation: `if not supplier_name: raise ValueError(...)`

### 2. Add fallback note when using contact_name as supplier name
- In `apps/Server/app/services/supplier_service.py`, after determining `supplier_name` (line 566-568), add logic to set a `notes` value when falling back:
  ```python
  supplier_name = company_name or contact_name
  if not supplier_name:
      raise ValueError("No company or contact name extracted from business card")

  # Flag when contact_name is used as supplier name (company_name missing)
  fallback_note = None
  if not company_name and contact_name:
      fallback_note = "Nombre de empresa no encontrado — se usó el nombre del contacto. Revisión manual requerida."
      print(f"INFO [SupplierService]: Using contact_name as supplier name for capture {capture_id}")
  ```
- Pass this note to the supplier creation call by merging it with any existing notes or using it directly:
  - In the `create_with_trade_fair_metadata` call, set `notes=fallback_note`

### 3. Add `contact_wechat` to `BusinessCardUpdateDTO`
- Open `apps/Server/app/models/kompass_dto.py`
- In `BusinessCardUpdateDTO` class (line 675), add the missing field:
  ```python
  contact_wechat: Optional[str] = None
  ```

### 4. Update unit tests for whitespace handling and fallback note
- Open `apps/Server/tests/services/test_supplier_service.py`
- In the `TestCreateSupplierFromCard` class, add new test methods:
  - `test_whitespace_only_company_name_falls_back_to_contact`: Set `company_name = "  "` and verify the supplier is created with `contact_name` as the name
  - `test_whitespace_only_both_names_raises_error`: Set both `company_name = "  "` and `contact_name = " "` and verify ValueError is raised
  - `test_fallback_note_added_when_using_contact_name`: Set `company_name = None` and verify the supplier is created with a notes field indicating manual review
- Update existing `test_fallback_to_contact_name` to also verify the fallback note is passed

### 5. Create E2E test file for supplier name card approval validation
- Read `.claude/commands/e2e/test_auto_create_supplier_from_card.md` and `.claude/commands/test_e2e.md` and create a new E2E test file in `.claude/commands/e2e/test_supplier_name_card_approval.md` that validates:
  - Navigate to Card Review page
  - Verify extracted cards show company_name in the editable cell
  - Edit the company_name field and verify the edit persists
  - Approve a card with a valid company_name
  - Navigate to Suppliers page and verify the supplier appears with the correct company_name (not blank)
  - Verify the supplier's contact_name is in the contact field, NOT the supplier name
  - Screenshots at each verification step

### 6. Run validation commands
- Execute all validation commands listed below to confirm zero regressions.

## Validation Commands
Execute every command to validate the bug is fixed with zero regressions.

- `cd apps/Server && python -m pytest tests/services/test_supplier_service.py -v --tb=short` — Run supplier service unit tests including new whitespace/fallback tests
- `cd apps/Server && python -m pytest tests/ -v --tb=short` — Run all Server tests to validate zero regressions
- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate no type errors
- `cd apps/Client && npm run build` — Run Client build to validate the build succeeds
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_supplier_name_card_approval.md` E2E test file to validate this functionality works

## Notes
- The frontend approval flow (`useCardReview.ts:approveCard` and `kompassService.ts:approveCard`) is confirmed correct — it sends only the `captureId` via POST with no body payload that could override fields.
- The `CardReviewPage.tsx` correctly uses `EditableCell` with `fieldName="company_name"` and calls `updateField` which sends a PUT request to persist changes before approval.
- The `BusinessCardUpdateDTO` is missing `contact_wechat` — this is a secondary fix included in this plan.
- The `suppliers.name` column has a `NOT NULL` constraint but no `CHECK(name != '')` constraint, so empty or whitespace-only strings can be inserted.
- All user-facing messages must be in Spanish (Colombian).
- No new libraries are needed for this fix.
