# Auto-Send Card Follow-Up Email

**ADW ID:** 89205537
**Date:** 2026-03-10
**Specification:** specs/issue-164-adw-89205537-sdlc_planner-auto-send-card-followup-email.md

## Overview

Adds a configurable `AUTO_SEND_CARD_EMAIL` backend setting (default: `false`) that controls whether an introduction email is automatically sent when a supplier is created from a business card capture. Previously, emails were sent unconditionally when a contact email existed. The frontend now surfaces email outcome (sent, skipped, failed) via snackbar notifications on both CardCapturePage and CardReviewPage.

## What Was Built

- Backend setting `AUTO_SEND_CARD_EMAIL` to gate auto-email behavior
- Extended `SupplierFromCardResultDTO` with email status fields (`email_sent`, `email_error`, `no_email_address`)
- Guarded email-send logic in `create_supplier_from_card()` behind the new setting
- Frontend `SupplierFromCardResult` type updated with matching fields
- CardCapturePage: email status snackbar notifications with warning severity support
- CardReviewPage: email status snackbar notifications with warning severity support
- E2E test specification for validating email status notifications

## Technical Implementation

### Files Modified

- `apps/Server/app/config/settings.py`: Added `AUTO_SEND_CARD_EMAIL: bool = False` setting
- `apps/Server/app/models/kompass_dto.py`: Added `email_sent`, `email_error`, `no_email_address` fields to `SupplierFromCardResultDTO`
- `apps/Server/app/services/supplier_service.py`: Refactored `create_supplier_from_card()` to check `AUTO_SEND_CARD_EMAIL` before sending and populate response fields
- `apps/Client/src/types/kompass.ts`: Added `email_sent`, `email_error`, `no_email_address` to `SupplierFromCardResult` interface
- `apps/Client/src/pages/kompass/CardCapturePage.tsx`: Added warning snackbar state and email status notification logic in `handleCreateSupplier()`
- `apps/Client/src/pages/kompass/CardReviewPage.tsx`: Extended snackbar severity to include `'warning'` and added email status notification logic in `handleApprove()`
- `.claude/commands/e2e/test_auto_send_card_followup_email.md`: New E2E test specification

### Key Changes

- **Setting guard**: The existing unconditional email send in `supplier_service.py` is now wrapped with `settings.AUTO_SEND_CARD_EMAIL` check. When disabled (default), no email is attempted and the response indicates so.
- **Graceful error handling**: Email failures are caught and returned in `email_error` without blocking supplier creation.
- **Single service path**: Both CardCapturePage ("Crear Proveedor") and CardReviewPage ("Approve") flows go through `create_supplier_from_card()`, so the setting guard covers both automatically.
- **Spanish-language notifications**: All snackbar messages are in Spanish to match the application's UI language.
- **Mock mode compatibility**: When `AUTO_SEND_CARD_EMAIL=True` and `EMAIL_MOCK_MODE=True`, mock mode simulates a successful send (`email_sent=True`).

## How to Use

1. **Default behavior (no email):** With the default `AUTO_SEND_CARD_EMAIL=False`, supplier creation from business cards works as before but no automatic email is sent. Use the "Enviar Seguimiento" action on the Suppliers page for manual outreach.

2. **Enable auto-email:** Set `AUTO_SEND_CARD_EMAIL=True` in the backend `.env` file. When a supplier is created from a business card with a valid email, an introduction email is sent automatically.

3. **Frontend feedback:** After creating a supplier from a card, the UI displays:
   - **Success (green):** "Proveedor creado. Correo de seguimiento enviado a {email}" — email sent successfully
   - **Warning (orange):** "No se encontró correo electrónico — seguimiento manual requerido" — no email address on card
   - **Warning (orange):** "Error al enviar correo de seguimiento" — email send failed (supplier still created)
   - **Success (green):** "Proveedor creado: {name}" — auto-email disabled (default)

## Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `AUTO_SEND_CARD_EMAIL` | `bool` | `False` | Enable automatic follow-up email on business card supplier creation |
| `EMAIL_MOCK_MODE` | `bool` | `True` | When true, emails are simulated without SMTP (existing setting) |

## Testing

- **Backend tests:** `cd apps/Server && python -m pytest tests/ -v --tb=short`
- **TypeScript check:** `cd apps/Client && npx tsc --noEmit`
- **Frontend build:** `cd apps/Client && npm run build`
- **E2E test:** Run `/e2e:test_auto_send_card_followup_email` slash command

## Notes

- The default `AUTO_SEND_CARD_EMAIL=False` preserves existing behavior — no automatic emails are sent.
- Manual outreach via "Enviar Seguimiento" on the Suppliers page works regardless of this setting.
- A future iteration (Issue TF-004) will add a dedicated "Trade Fair Follow-Up" email template. The current implementation uses the existing `send_supplier_introduction()` template.
