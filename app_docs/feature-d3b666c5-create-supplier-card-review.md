# Create Supplier from Card Review Page

**ADW ID:** d3b666c5
**Date:** 2026-03-11
**Specification:** specs/issue-185-adw-d3b666c5-sdlc_planner-create-supplier-card-review.md

## Overview

Adds a dedicated "Crear Proveedor" button to the Card Review page so users can create a supplier directly after reviewing extracted business card data, without navigating back to the Card Capture page. This eliminates a UX friction point during trade fairs where speed matters.

## What Was Built

- "Crear Proveedor" button in the Card Review page actions column for extracted cards without a linked supplier
- Loading state with spinner and "Creando..." text during supplier creation
- Snackbar feedback for success, duplicate detection, email status, and errors
- "Proveedor vinculado" chip displayed on confirmed cards with a linked supplier
- `createSupplierFromCard` method in the `useCardReview` hook with per-row loading tracking
- E2E test specification for the full create-supplier-from-card-review workflow

## Technical Implementation

### Files Modified

- `apps/Client/src/hooks/kompass/useCardReview.ts`: Added `createSupplierFromCard` method and `creatingSupplierIds` state (Set-based per-row loading tracking). On success, updates card status to `confirmed` with `supplier_id`. On duplicate, sets status to `rejected`.
- `apps/Client/src/pages/kompass/CardReviewPage.tsx`: Added `PersonAddIcon` import, `handleCreateSupplier` handler with snackbar messaging, "Crear Proveedor" button (visible for `extracted` status without `supplier_id`), and "Proveedor vinculado" chip (visible for `confirmed` status with `supplier_id`).
- `.claude/commands/e2e/test_create_supplier_card_review.md`: New E2E test file validating the button visibility, loading states, result feedback, and status transitions.
- `playwright-mcp-config.json`: Minor update for E2E test configuration.

### Key Changes

- The `createSupplierFromCard` method in `useCardReview` calls the existing `businessCardService.createSupplierFromCard()` API — no backend changes were needed
- Per-row loading state uses a `Set<string>` pattern (matching the CardCapturePage approach) to track which card IDs are being processed
- The button is placed before the existing "Aprobar" button in the actions column for visual priority
- Duplicate detection updates the card status to `rejected` in local state
- The existing "Aprobar" button is preserved for batch-compatible approval workflows

## How to Use

1. Navigate to the **Revisión de Tarjetas** page (`/card-review`)
2. Review extracted business card data in the table
3. For cards with "Extraído" status, click the **Crear Proveedor** button in the actions column
4. The button shows a loading spinner with "Creando..." while processing
5. A snackbar notification appears with the result:
   - **Success**: Supplier name and email status
   - **Duplicate**: Error message with existing supplier name
   - **Warning**: Supplier created but email failed or no email address found
6. After successful creation, the card shows a "Proveedor vinculado" chip

## Configuration

No additional configuration required. Uses the existing `POST /api/extract/business-cards/{id}/create-supplier` endpoint.

## Testing

- **TypeScript**: `cd apps/Client && npx tsc --noEmit`
- **Build**: `cd apps/Client && npm run build`
- **Backend**: `cd apps/Server && python -m pytest tests/ -v --tb=short`
- **E2E**: Run `/test_e2e` then execute `e2e:test_create_supplier_card_review`

## Notes

- No backend changes were required — the API endpoint, service logic, and duplicate detection already existed
- The "Aprobar" button remains alongside "Crear Proveedor" because it supports batch workflows (batch approve selected cards)
- The snackbar messaging matches the same pattern used on the CardCapturePage for consistency
