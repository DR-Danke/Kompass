# Bug Fix: Supplier Name Blank After Card Approval

**ADW ID:** 44fe017a
**Date:** 2026-03-10
**Specification:** specs/issue-168-adw-44fe017a-sdlc_planner-fix-supplier-name-blank-card-approval.md

## Overview

Fixed a P0 bug where suppliers created from business card approval appeared with blank names in the Suppliers list. Whitespace-only `company_name` values (e.g., `" "`) were truthy in Python and bypassed the fallback logic to `contact_name`, resulting in empty-looking supplier names in the UI.

## What Was Built

- Whitespace sanitization for `company_name` and `contact_name` in `create_supplier_from_card`
- Fallback note when `contact_name` is used as the supplier name (flagging manual review)
- `contact_wechat` field added to `BusinessCardUpdateDTO` for CardReviewPage editing
- Unit tests covering whitespace-only names, fallback note, and error scenarios
- E2E test specification for supplier name card approval validation

## Technical Implementation

### Files Modified

- `apps/Server/app/services/supplier_service.py`: Added `.strip()` normalization for `company_name` and `contact_name`, converting whitespace-only strings to `None`. Added fallback note logic when `contact_name` is used as the supplier name, passing `notes=fallback_note` to the repository create call.
- `apps/Server/app/models/kompass_dto.py`: Added `contact_wechat: Optional[str] = None` to `BusinessCardUpdateDTO`.
- `apps/Server/tests/services/test_supplier_service.py`: Added 3 new test methods and updated 1 existing test for whitespace handling, fallback note verification, and error cases.
- `.claude/commands/e2e/test_supplier_name_card_approval.md`: New E2E test specification covering the card-to-supplier name flow.

### Key Changes

- **Whitespace normalization**: `(capture.get("company_name") or "").strip() or None` ensures whitespace-only strings become `None`, allowing the `or` fallback to `contact_name` to work correctly.
- **Fallback note**: When `company_name` is missing/empty and `contact_name` is used, a Spanish note is added: "Nombre de empresa no encontrado — se usó el nombre del contacto. Revisión manual requerida."
- **DTO field addition**: `contact_wechat` was missing from `BusinessCardUpdateDTO`, preventing WeChat ID editing on the CardReviewPage before approval.
- **Test coverage**: Tests validate whitespace-only company name fallback, both-names-whitespace error, and fallback note content.

## How to Use

1. Upload a business card on the Card Capture page
2. Navigate to Card Review page — extracted cards show `company_name` in editable cells
3. Edit `company_name` or `contact_wechat` fields if needed before approval
4. Click "Aprobar" to approve the card and create a supplier
5. Navigate to Suppliers page — the supplier name is correctly populated (never blank)
6. If `company_name` was empty, the supplier uses `contact_name` with a review note in the notes field

## Configuration

No new configuration required.

## Testing

- Run supplier service unit tests: `cd apps/Server && python -m pytest tests/services/test_supplier_service.py -v --tb=short`
- Run all server tests: `cd apps/Server && python -m pytest tests/ -v --tb=short`
- E2E test: Execute `/e2e:test_supplier_name_card_approval` slash command

## Notes

- The `suppliers.name` column has a `NOT NULL` constraint but no `CHECK(name != '')` constraint at the database level — the fix is applied at the service layer.
- The frontend approval flow (`useCardReview.ts`, `kompassService.ts`) was confirmed correct — no changes needed.
- All user-facing messages are in Spanish (Colombian).
