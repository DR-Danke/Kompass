# Feature: Auto-Send Follow-Up Email on Business Card Capture

## Metadata
issue_number: `164`
adw_id: `89205537`
issue_json: ``

## Feature Description
Add a backend setting `AUTO_SEND_CARD_EMAIL` (default: `false`) to control whether an introduction email is automatically sent when a supplier is created from a business card capture. Currently, the system **always** sends an introduction email when the supplier has a `contact_email`. This feature gates that behavior behind a setting so teams can opt-in when ready, while keeping the default as manual outreach via the Suppliers page ("Enviar Seguimiento" quick action). The frontend is updated to surface the email outcome (sent, skipped, failed) in snackbar notifications on both the CardCapturePage and CardReviewPage.

## User Story
As a Kompass sourcing agent at a trade fair
I want the system to optionally auto-send a follow-up email when I confirm a business card
So that I can immediately engage new suppliers without manual steps, or keep manual control when preferred

## Problem Statement
The current implementation unconditionally sends an introduction email when a supplier is created from a business card and has an email address (`supplier_service.py:620-637`). There is no way to disable this — teams that want manual outreach are forced to use mock mode or lack SMTP config to suppress it. Additionally, the frontend receives no feedback about whether an email was sent, failed, or skipped.

## Solution Statement
1. Add `AUTO_SEND_CARD_EMAIL: bool = False` to backend settings, gating the existing auto-send logic.
2. Extend `SupplierFromCardResultDTO` with `email_sent`, `email_error`, and `no_email_address` fields.
3. Update `create_supplier_from_card()` to check the setting before sending and populate the new response fields.
4. Update the frontend `SupplierFromCardResult` type and both card pages (CardCapturePage, CardReviewPage) to display email status in snackbar notifications.

## Relevant Files
Use these files to implement the feature:

**Backend:**
- `apps/Server/app/config/settings.py` — Add `AUTO_SEND_CARD_EMAIL` setting (line 42, after email settings block)
- `apps/Server/app/services/supplier_service.py` — Modify `create_supplier_from_card()` (lines 620-643) to guard email with setting and populate response fields
- `apps/Server/app/models/kompass_dto.py` — Extend `SupplierFromCardResultDTO` (lines 451-460) with email status fields
- `apps/Server/app/api/extraction_routes.py` — No code changes needed; the DTO fields propagate automatically. Verify the `/approve` route (line 571) also returns the updated DTO.
- `apps/Server/app/services/email_service.py` — Reference only; `send_supplier_introduction()` (line 364) is already implemented.
- `apps/Server/app/services/business_card_service.py` — Reference only; `approve_card()` (line 123) delegates to `supplier_service.create_supplier_from_card()`.

**Frontend:**
- `apps/Client/src/types/kompass.ts` — Update `SupplierFromCardResult` interface (lines 1071-1079)
- `apps/Client/src/pages/kompass/CardCapturePage.tsx` — Update `handleCreateSupplier()` (lines 206-243) to show email status snackbars
- `apps/Client/src/pages/kompass/CardReviewPage.tsx` — Update `handleApprove()` (lines 186-197) to show email status snackbars
- `apps/Client/src/hooks/kompass/useCardReview.ts` — Reference only; `approveCard()` already returns `SupplierFromCardResult`

**Testing & E2E:**
- Read `.claude/commands/test_e2e.md` to understand how to run E2E tests
- Read `.claude/commands/e2e/test_basic_query.md` to understand the E2E test file format
- Read `.claude/commands/e2e/test_auto_create_supplier_from_card.md` — existing E2E test for reference

### New Files
- `.claude/commands/e2e/test_auto_send_card_followup_email.md` — New E2E test validating email status notifications after card supplier creation

## Implementation Plan

### Phase 1: Foundation
Add the new backend setting and extend the DTO to carry email status information. These are the shared building blocks that both the service logic and frontend depend on.

### Phase 2: Core Implementation
Guard the existing auto-email logic in `create_supplier_from_card()` with the new setting. Populate the new DTO fields (`email_sent`, `email_error`, `no_email_address`) based on the outcome. Update the frontend TypeScript type to match.

### Phase 3: Integration
Update both CardCapturePage and CardReviewPage to read the new email status fields and display appropriate Spanish-language snackbar notifications. Create an E2E test to validate the feature.

## Step by Step Tasks

### Step 1: Add `AUTO_SEND_CARD_EMAIL` Setting
- Open `apps/Server/app/config/settings.py`
- Add `AUTO_SEND_CARD_EMAIL: bool = False` after the `EMAIL_MOCK_MODE` setting (line 42)
- Add a comment: `# Auto-send follow-up email on business card supplier creation`

### Step 2: Extend `SupplierFromCardResultDTO`
- Open `apps/Server/app/models/kompass_dto.py`
- Add three new fields to `SupplierFromCardResultDTO` (after line 460, before the closing of the class):
  - `email_sent: bool = False`
  - `email_error: Optional[str] = None`
  - `no_email_address: bool = False`

### Step 3: Update `create_supplier_from_card()` Service Logic
- Open `apps/Server/app/services/supplier_service.py`
- Replace lines 620-643 (the current email-send block + return statement) with the new guarded logic:
  1. Import and read `get_settings()` to get the `AUTO_SEND_CARD_EMAIL` value
  2. Initialize tracking variables: `email_sent = False`, `email_error = None`, `no_email_address = not bool(contact_email)`, `auto_email_enabled = settings.AUTO_SEND_CARD_EMAIL`
  3. If `auto_email_enabled` and `contact_email`: try to send the introduction email, capture success/error
  4. If not `auto_email_enabled`: log that auto-email is disabled
  5. Return `SupplierFromCardResultDTO` with all existing fields plus the three new email status fields

### Step 4: Update Frontend TypeScript Type
- Open `apps/Client/src/types/kompass.ts`
- Add three new fields to `SupplierFromCardResult` interface (after `message: string;` at line 1078):
  - `email_sent: boolean;`
  - `email_error?: string;`
  - `no_email_address: boolean;`

### Step 5: Update CardCapturePage Email Status Notifications
- Open `apps/Client/src/pages/kompass/CardCapturePage.tsx`
- Modify `handleCreateSupplier()` (lines 213-221, the `result.success` branch):
  - If `result.email_sent`: show success snackbar "Proveedor creado. Correo de seguimiento enviado a {email}"
    - Extract email from the capture object (`captures.find(c => c.id === captureId)?.contact_email`)
  - If `result.no_email_address`: show warning snackbar "Proveedor creado. No se encontró correo electrónico — seguimiento manual requerido"
  - If `result.email_error`: show success for supplier + warning for email "Proveedor creado. Error al enviar correo de seguimiento"
  - Default (auto-email disabled, no error): show current success message "Proveedor creado: {supplier_name}"
- Add a `warning` severity option to the snackbar state if not already present, or use two separate snackbars (success + warning). The page currently uses separate `error` and `success` state strings with dedicated Snackbar components. Add a `warning` state + Snackbar for the orange/warning messages.

### Step 6: Update CardReviewPage Email Status Notifications
- Open `apps/Client/src/pages/kompass/CardReviewPage.tsx`
- Modify `handleApprove()` (lines 186-197):
  - The current snackbar state is `{ message: string; severity: 'success' | 'error' }`. Extend the severity union to include `'warning'`.
  - If `result.is_duplicate`: keep existing error snackbar
  - If `result.email_sent`: set snackbar with success severity "Proveedor creado. Correo de seguimiento enviado"
  - If `result.no_email_address`: set snackbar with warning severity "Proveedor creado. No se encontró correo electrónico — seguimiento manual requerido"
  - If `result.email_error`: set snackbar with warning severity "Proveedor creado. Error al enviar correo de seguimiento"
  - Default (auto-email disabled): keep existing success message "Proveedor \"{name}\" creado exitosamente"
- Update the Snackbar `<Alert>` component to use the dynamic severity from state (it likely already does via `snackbar.severity`).

### Step 7: Create E2E Test Specification
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_basic_query.md` for format reference
- Create `.claude/commands/e2e/test_auto_send_card_followup_email.md` with these test steps:
  1. Navigate to Card Capture page
  2. Upload a business card with a valid email address
  3. Wait for extraction to complete
  4. Click "Crear Proveedor"
  5. Verify supplier creation success message appears
  6. Verify email status notification appears (content depends on `AUTO_SEND_CARD_EMAIL` setting — in test/mock mode it should show either "auto-email disabled" default message or mock email sent message)
  7. Navigate to Card Review page
  8. Approve an extracted card
  9. Verify email status notification on approval result
  10. Screenshot each step
- Success criteria: supplier creation succeeds, email status is surfaced in UI, no console errors

### Step 8: Run Validation Commands
- Execute all validation commands listed below to confirm zero regressions

## Testing Strategy

### Unit Tests
- Verify `AUTO_SEND_CARD_EMAIL` defaults to `False` in `Settings`
- Verify `SupplierFromCardResultDTO` accepts the new fields and defaults are correct
- Verify `create_supplier_from_card()` does NOT send email when `AUTO_SEND_CARD_EMAIL=False`
- Verify `create_supplier_from_card()` sends email when `AUTO_SEND_CARD_EMAIL=True` and `contact_email` is present
- Verify `create_supplier_from_card()` does NOT send email when `contact_email` is empty even if setting is `True`
- Verify email failure is caught and returned in `email_error` without raising

### Edge Cases
- `AUTO_SEND_CARD_EMAIL=True` but `contact_email` is `None` → `no_email_address=True`, no email sent
- `AUTO_SEND_CARD_EMAIL=True` but `contact_email` is empty string `""` → `no_email_address=True`, no email sent
- `AUTO_SEND_CARD_EMAIL=True`, valid email, but SMTP fails → `email_sent=False`, `email_error` has message
- `AUTO_SEND_CARD_EMAIL=True`, valid email, `EMAIL_MOCK_MODE=True` → `email_sent=True` (mock mode succeeds)
- `AUTO_SEND_CARD_EMAIL=False` (default) → existing behavior preserved, no email attempted
- Duplicate supplier detected → no email sent (supplier creation fails before email logic)

## Acceptance Criteria
- [ ] `AUTO_SEND_CARD_EMAIL` setting exists in `settings.py` with default `False`
- [ ] When `AUTO_SEND_CARD_EMAIL=false` (default), no introduction email is sent on card supplier creation
- [ ] When `AUTO_SEND_CARD_EMAIL=true` and supplier has email, introduction email is sent
- [ ] When `AUTO_SEND_CARD_EMAIL=true` and supplier has NO email, `no_email_address=True` in response
- [ ] Email failures are caught gracefully — supplier creation still succeeds
- [ ] `SupplierFromCardResultDTO` includes `email_sent`, `email_error`, `no_email_address` fields
- [ ] Frontend `SupplierFromCardResult` type includes the new fields
- [ ] CardCapturePage shows email status in snackbar notifications (Spanish)
- [ ] CardReviewPage shows email status in snackbar notifications (Spanish)
- [ ] Manual outreach ("Enviar Seguimiento") works regardless of setting
- [ ] All existing tests pass with zero regressions
- [ ] TypeScript compiles with no errors
- [ ] Frontend builds successfully

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -m pytest tests/ -v --tb=short` — Run backend tests to validate zero regressions
- `cd apps/Client && npx tsc --noEmit` — Run TypeScript type check to validate no type errors
- `cd apps/Client && npm run build` — Run frontend production build to validate no build errors
- `cd apps/Client && npm run lint` — Run ESLint to validate no lint errors
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_auto_send_card_followup_email.md` to validate email status notifications work end-to-end

## Notes
- The existing auto-email code at `supplier_service.py:620-637` already sends emails unconditionally when `contact_email` exists. This feature wraps that behavior with the setting guard — the core email logic stays the same.
- Both `create-supplier` (CardCapturePage) and `approve` (CardReviewPage) endpoints funnel through `supplier_service.create_supplier_from_card()`, so the setting guard covers both flows automatically.
- `EMAIL_MOCK_MODE=True` (default) will simulate email sends without SMTP. When `AUTO_SEND_CARD_EMAIL=True` + `EMAIL_MOCK_MODE=True`, the response will show `email_sent=True` because mock mode returns success.
- Wave 2 (Issue TF-004) will add a dedicated "Trade Fair Follow-Up" email template. This implementation uses the existing `send_supplier_introduction()` template which is already appropriate for trade fair follow-ups.
- No new libraries required.
