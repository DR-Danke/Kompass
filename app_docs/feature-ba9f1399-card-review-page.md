# Card Review Page — Review & Confirm Extracted Suppliers

**ADW ID:** ba9f1399
**Date:** 2026-03-09
**Specification:** specs/issue-144-adw-ba9f1399-sdlc_planner-review-confirm-extracted-suppliers.md

## Overview

A dedicated review interface at `/card-review` where back-office team members can view, edit, approve, or reject business card extractions before supplier creation. This page acts as a quality-control step between AI extraction and automatic supplier creation, allowing correction of AI mistakes, confidence score inspection, and batch processing of multiple cards.

## What Was Built

- **CardReviewPage** — Full review UI with editable inline fields, confidence indicators, status filters, and approve/reject actions
- **useCardReview hook** — State management for captures list, selection, filtering, optimistic updates, and batch operations
- **Backend approve/reject endpoints** — PUT update, POST approve, POST reject API routes for business cards
- **Backend service methods** — `approve_card()` and `reject_card()` on BusinessCardService
- **DTOs** — `BusinessCardUpdateDTO` and `BusinessCardRejectDTO` for typed request validation
- **Frontend API methods** — `updateCapture()`, `approveCard()`, `rejectCard()` on businessCardService
- **Navigation & routing** — Sidebar entry "Revisión Tarjetas" with RateReviewIcon, route at `/card-review`
- **E2E test spec** — `.claude/commands/e2e/test_card_review_page.md`
- **Backend unit tests** — 8 tests covering update, approve, reject, role-based access

## Technical Implementation

### Files Modified

- `apps/Server/app/models/kompass_dto.py`: Added `BusinessCardUpdateDTO` (7 optional fields) and `BusinessCardRejectDTO` (optional reason)
- `apps/Server/app/services/business_card_service.py`: Added `approve_card()` (validates status=extracted, delegates to supplier_service) and `reject_card()` (validates status, stores rejection reason in notes)
- `apps/Server/app/api/extraction_routes.py`: Added 3 endpoints — PUT update, POST approve, POST reject — with role-based access (admin/manager/user), plus `_build_capture_response()` helper
- `apps/Server/tests/test_extraction_routes.py`: Added 8 tests for new endpoints including success, not-found, invalid-status, and viewer-forbidden cases
- `apps/Client/src/services/kompassService.ts`: Added `updateCapture()`, `approveCard()`, `rejectCard()` to businessCardService
- `apps/Client/src/hooks/kompass/useCardReview.ts`: New hook with state management, fetchCaptures, updateField (optimistic), approveCard, rejectCard, batch operations, selection, filtering
- `apps/Client/src/pages/kompass/CardReviewPage.tsx`: New 517-line page component with MUI Table, editable cells, confidence chips, status filters, reject dialog, batch actions, snackbar feedback
- `apps/Client/src/App.tsx`: Added route `/card-review` → `CardReviewPage`
- `apps/Client/src/components/layout/Sidebar.tsx`: Added "Revisión Tarjetas" nav item with RateReviewIcon
- `.claude/commands/e2e/test_card_review_page.md`: E2E test specification

### Key Changes

- **Approve flow**: Validates capture status is "extracted", then delegates to existing `supplier_service.create_supplier_from_card()` which handles duplicate detection, supplier creation, status update to "confirmed", and email outreach
- **Reject flow**: Validates capture status is "extracted", "pending", or "failed", sets status to "rejected", appends rejection reason to notes field prefixed with "Rechazo:"
- **Inline editing**: EditableCell component supports click-to-edit with save on blur/Enter, displays confidence chip alongside each field value
- **Confidence scoring**: Color-coded chips (green ≥80%, yellow ≥50%, red <50%) extracted from `extraction_raw_response.confidence_scores`
- **Batch operations**: Checkbox selection with "Aprobar Seleccionados" / "Rechazar Seleccionados" buttons, processes cards sequentially

## How to Use

1. Navigate to **Revisión Tarjetas** in the sidebar (or go to `/card-review`)
2. Use the status filter toggle buttons (Todos, Pendientes, Extraídas, Confirmadas, Rechazadas) to filter captures
3. Click any editable field (company, contact, email, phone, address, fair) to correct AI extraction errors — changes save on blur or Enter
4. Review confidence score chips next to each field (green = high confidence, yellow = medium, red = low)
5. Click **Aprobar** (green check icon) on an extracted card to create a supplier and trigger outreach email
6. Click **Rechazar** (red cancel icon) to reject a card — a dialog prompts for an optional rejection reason
7. Use checkboxes to select multiple cards, then use batch action buttons to approve or reject in bulk

## Configuration

No additional configuration required. The feature uses existing:
- Business card extraction infrastructure (`/api/extract/business-cards`)
- Supplier creation flow (`supplier_service.create_supplier_from_card()`)
- Email outreach (via existing email service)
- RBAC: admin, manager, and user roles can approve/reject; viewer role is denied

## Testing

- **Backend unit tests**: `cd apps/Server && python -m pytest tests/test_extraction_routes.py -v --tb=short`
- **TypeScript check**: `cd apps/Client && npx tsc --noEmit`
- **Build validation**: `cd apps/Client && npm run build`
- **Lint**: `cd apps/Client && npm run lint`
- **E2E**: Run `/e2e:test_card_review_page` slash command

## Notes

- The approve endpoint reuses `supplier_service.create_supplier_from_card()` which already handles duplicate detection (auto-rejects duplicates), email sending, and status transitions
- The `province` field from the original issue is not in the DB schema — province info should be included in the `address` field
- Rejection reasons are appended to the `notes` field prefixed with "Rechazo:" to preserve existing notes
- Batch operations process cards sequentially (not in parallel) to avoid race conditions
