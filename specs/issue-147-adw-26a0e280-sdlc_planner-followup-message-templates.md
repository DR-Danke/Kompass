# Feature: Follow-Up Message Templates

## Metadata
issue_number: `147`
adw_id: `26a0e280`
issue_json: ``

## Feature Description
Add configurable follow-up message templates that can be sent to suppliers via email and/or WeChat. After initial introduction at a trade fair, the back-office team needs to send follow-up messages requesting pricing information and product catalogs. Templates are configurable (not hardcoded), and messages can be triggered manually from the supplier detail view. The system tracks outreach status on each supplier and supports multiple message channels.

## User Story
As a back-office team member (admin, manager, or user)
I want to send configurable follow-up messages to suppliers via email and/or WeChat from the supplier detail view
So that I can efficiently request product catalogs and pricing information after trade fair meetings

## Problem Statement
After meeting suppliers at trade fairs, the team currently has no way to send structured follow-up messages. The introduction email exists but there's no template system for subsequent outreach (catalog requests, pricing inquiries). The `outreach_status` field exists in the database but is not exposed through the API or UI, making it impossible to track communication progress.

## Solution Statement
Implement a template-based outreach system with:
1. A dictionary of configurable message templates (introduction, follow-up catalog, follow-up pricing)
2. Template rendering with supplier and sender data interpolation
3. A new `POST /api/suppliers/{id}/outreach` endpoint that sends messages via selected channels
4. An outreach dialog in the SuppliersPage with template selection, channel checkboxes, message preview, and optional custom message override
5. Outreach status tracking displayed on supplier cards/rows

## Relevant Files
Use these files to implement the feature:

**Backend — Services:**
- `apps/Server/app/services/email_service.py` — Has existing `send_supplier_introduction()` and `_render_introduction_template()`. Add `OUTREACH_TEMPLATES` dict and `send_template_email()` method.
- `apps/Server/app/services/wechat_service.py` — Has existing `send_supplier_introduction()` and `_render_introduction_message()`. Add `send_template_message()` method.
- `apps/Server/app/services/supplier_service.py` — Has supplier CRUD methods. Add outreach orchestration method to coordinate email/wechat sends and status updates.

**Backend — API:**
- `apps/Server/app/api/supplier_routes.py` — Has CRUD + pipeline + certification routes. Add `POST /api/suppliers/{id}/outreach` endpoint.

**Backend — Models:**
- `apps/Server/app/models/kompass_dto.py` — Has all DTOs. Add `SupplierOutreachRequestDTO`, `SupplierOutreachResultDTO`. Add `outreach_status` to `SupplierResponseDTO`.

**Backend — Repository:**
- `apps/Server/app/repository/kompass_repository.py` — Has supplier repository methods. Add method to update `outreach_status` on the suppliers table.

**Backend — Database:**
- `apps/Server/database/schema.sql` — Reference only. The `outreach_status` column already exists with CHECK constraint: `('none', 'pending', 'contacted', 'responded', 'meeting_scheduled', 'completed')`.

**Frontend — Types:**
- `apps/Client/src/types/kompass.ts` — Has `SupplierResponse` (missing `outreach_status`). Add `outreach_status` field, `SupplierOutreachRequest`, `SupplierOutreachResult` types, and `OutreachTemplate` type.

**Frontend — Services:**
- `apps/Client/src/services/kompassService.ts` — Has `supplierService` object. Add `sendOutreach()` and `getOutreachTemplates()` methods.

**Frontend — Pages:**
- `apps/Client/src/pages/kompass/SuppliersPage.tsx` — Has supplier list/kanban with dialog patterns and quick actions menu. Add outreach dialog and "Send Follow-Up" action.

**Frontend — Components:**
- `apps/Client/src/components/kompass/SupplierQuickActionsMenu.tsx` — Has menu items for edit, delete, pipeline status, etc. Add "Enviar Seguimiento" menu item.

**E2E Test Reference:**
- `.claude/commands/test_e2e.md` — E2E test runner instructions
- `.claude/commands/e2e/test_trade_fair_dashboard.md` — Example E2E test for trade fair features (reference pattern)

### New Files
- `.claude/commands/e2e/test_supplier_outreach.md` — E2E test for supplier outreach/follow-up message functionality

## Implementation Plan

### Phase 1: Foundation
1. Add `outreach_status` to `SupplierResponseDTO` so the field is exposed in API responses
2. Add `SupplierOutreachRequestDTO` and `SupplierOutreachResultDTO` to DTOs
3. Add repository method to update `outreach_status` on a supplier
4. Define `OUTREACH_TEMPLATES` dictionary in `email_service.py`

### Phase 2: Core Implementation
1. Add `send_template_email()` to `email_service.py` that renders a template with supplier data and sends via SMTP (or mock)
2. Add `send_template_message()` to `wechat_service.py` that renders a template and sends via WeChat API (or mock)
3. Add `send_outreach()` orchestration method to `supplier_service.py` that coordinates channel sends and updates outreach_status
4. Add `POST /api/suppliers/{id}/outreach` endpoint to `supplier_routes.py`
5. Add `GET /api/suppliers/outreach-templates` endpoint to return available templates

### Phase 3: Integration
1. Add frontend types (`SupplierOutreachRequest`, `SupplierOutreachResult`, `OutreachTemplate`)
2. Add `outreach_status` to `SupplierResponse` type
3. Add `sendOutreach()` and `getOutreachTemplates()` to `kompassService.ts`
4. Build outreach dialog component in `SuppliersPage.tsx`
5. Add "Enviar Seguimiento" action to `SupplierQuickActionsMenu`
6. Display outreach status chip on supplier cards/rows
7. Create E2E test file

## Step by Step Tasks

### Task 1: Add outreach_status to SupplierResponseDTO
- In `apps/Server/app/models/kompass_dto.py`:
  - Add `outreach_status: Optional[str] = "none"` field to `SupplierResponseDTO`
  - Add `SupplierOutreachRequestDTO` with fields: `template: str = "follow_up_catalog"`, `channels: List[str] = ["email"]`, `custom_message: Optional[str] = None`
  - Add `SupplierOutreachResultDTO` with fields: `email_sent: bool = False`, `wechat_sent: bool = False`, `message: str`, `outreach_status: str`
  - Add `OutreachTemplateDTO` with fields: `key: str`, `name: str`, `subject: str`, `body_preview: str`

### Task 2: Update repository to expose and update outreach_status
- In `apps/Server/app/repository/kompass_repository.py`:
  - Ensure `_row_to_dict()` and `_row_to_dict_extended()` include `outreach_status` in the returned dict
  - Add `update_outreach_status(supplier_id: str, status: str) -> dict` method that executes `UPDATE suppliers SET outreach_status = %s, updated_at = NOW() WHERE id = %s RETURNING *`
  - Verify the SELECT queries for get_by_id / get_all include the `outreach_status` column

### Task 3: Add OUTREACH_TEMPLATES and send_template_email to email_service
- In `apps/Server/app/services/email_service.py`:
  - Add `OUTREACH_TEMPLATES` dictionary at module level with three templates: `introduction`, `follow_up_catalog`, `follow_up_pricing`
  - Each template has `name` (Spanish display name), `subject`, and `body` keys with `{contact_name}`, `{sender_name}`, `{fair_name}`, `{company_name}` placeholders
  - Add `get_templates() -> list[dict]` class method that returns template metadata (key, name, subject, body preview)
  - Add `send_template_email(supplier: dict, template_name: str, custom_message: str = None) -> EmailSendResultDTO` method:
    - Look up template by name (raise ValueError if not found)
    - Build context dict from supplier data: `contact_name`, `company_name`, `fair_name`
    - Add `sender_name` from settings or default "Kompass"
    - If `custom_message` provided, override body with it
    - Render subject and body with `.format(**context)`
    - Call existing `send_email()` with rendered content
    - Return `EmailSendResultDTO`

### Task 4: Add send_template_message to wechat_service
- In `apps/Server/app/services/wechat_service.py`:
  - Import `OUTREACH_TEMPLATES` from `email_service` (shared templates)
  - Add `send_template_message(supplier: dict, template_name: str, custom_message: str = None) -> WeChatSendResultDTO` method:
    - Look up template by name
    - Build context dict from supplier data
    - If `custom_message` provided, override body
    - Render body text with `.format(**context)`
    - Call existing `send_message()` with rendered text to supplier's `wechat_id`
    - Return `WeChatSendResultDTO`

### Task 5: Add outreach orchestration to supplier_service
- In `apps/Server/app/services/supplier_service.py`:
  - Import `email_service` and `wechat_service`
  - Import `OUTREACH_TEMPLATES` from email_service
  - Add `get_outreach_templates() -> list[dict]` method that returns template metadata from `email_service.get_templates()`
  - Add `send_outreach(supplier_id: str, template: str, channels: list[str], custom_message: str = None) -> dict` method:
    - Get supplier by ID (raise 404 if not found)
    - Validate template name exists in OUTREACH_TEMPLATES
    - Validate channels list (must contain 'email' and/or 'wechat')
    - Initialize result: `email_sent=False`, `wechat_sent=False`
    - If 'email' in channels and supplier has `contact_email`: call `email_service.send_template_email()`
    - If 'wechat' in channels and supplier has `wechat_id`: call `wechat_service.send_template_message()`
    - Determine new outreach_status based on results: 'contacted' if any sent, keep current if none sent
    - Call repository `update_outreach_status()` with new status
    - Return `SupplierOutreachResultDTO` with results

### Task 6: Add outreach API endpoints
- In `apps/Server/app/api/supplier_routes.py`:
  - Import `SupplierOutreachRequestDTO`, `SupplierOutreachResultDTO`, `OutreachTemplateDTO`
  - Add `POST /api/suppliers/{supplier_id}/outreach` endpoint:
    - Requires auth: `get_current_user` (admin, manager, user roles)
    - Accepts `SupplierOutreachRequestDTO` body
    - Calls `supplier_service.send_outreach()`
    - Returns `SupplierOutreachResultDTO`
    - Error handling: 404 if supplier not found, 400 for invalid template/channels
  - Add `GET /api/suppliers/outreach-templates` endpoint:
    - Requires auth: `get_current_user`
    - Returns list of `OutreachTemplateDTO`
    - Place this route BEFORE `/{supplier_id}` to avoid path conflict

### Task 7: Write backend tests
- In `apps/Server/tests/test_kompass/`:
  - Add test for outreach templates retrieval
  - Add test for outreach endpoint with valid email channel
  - Add test for outreach endpoint with invalid template name (400)
  - Add test for outreach endpoint with supplier not found (404)
  - Add test for outreach_status update after sending

### Task 8: Add frontend types
- In `apps/Client/src/types/kompass.ts`:
  - Add `outreach_status: string | null` to `SupplierResponse` interface
  - Add `outreach_status?: string` to `SupplierWithProductCount` if not inherited
  - Add `SupplierOutreachRequest` interface: `template: string`, `channels: ('email' | 'wechat')[]`, `custom_message?: string`
  - Add `SupplierOutreachResult` interface: `email_sent: boolean`, `wechat_sent: boolean`, `message: string`, `outreach_status: string`
  - Add `OutreachTemplate` interface: `key: string`, `name: string`, `subject: string`, `body_preview: string`

### Task 9: Add frontend API methods
- In `apps/Client/src/services/kompassService.ts`:
  - Add to `supplierService` object:
    - `sendOutreach(supplierId: string, request: SupplierOutreachRequest): Promise<SupplierOutreachResult>` — POST to `/suppliers/${supplierId}/outreach`
    - `getOutreachTemplates(): Promise<OutreachTemplate[]>` — GET from `/suppliers/outreach-templates`

### Task 10: Add outreach dialog to SuppliersPage
- In `apps/Client/src/pages/kompass/SuppliersPage.tsx`:
  - Add state variables: `outreachDialogOpen`, `outreachSupplier`, `outreachLoading`, `outreachTemplates`, `outreachResult`
  - Add `OutreachDialog` inline or as a local component within the file:
    - Template selector dropdown (MUI Select) populated from `getOutreachTemplates()`
    - Channel checkboxes: "Email" (enabled if supplier has contact_email), "WeChat" (enabled if supplier has wechat_id)
    - Optional custom message TextField (multiline)
    - Message preview section showing rendered template
    - "Enviar" button that calls `sendOutreach()` and shows result
    - Success/error feedback via Alert component
    - All labels in Spanish: "Enviar Seguimiento", "Plantilla", "Canales", "Mensaje personalizado", "Vista previa", "Enviar", "Cancelar"
  - On successful send, refresh supplier data to reflect updated outreach_status

### Task 11: Add outreach action to SupplierQuickActionsMenu
- In `apps/Client/src/components/kompass/SupplierQuickActionsMenu.tsx`:
  - Add `onSendOutreach` callback prop
  - Add "Enviar Seguimiento" menu item with a mail/send icon
  - Place it after pipeline status actions, before destructive actions
  - Disable if supplier has no contact_email AND no wechat_id

### Task 12: Display outreach status on supplier rows/cards
- In `apps/Client/src/pages/kompass/SuppliersPage.tsx`:
  - Add an outreach status Chip to the supplier table row (after pipeline status column)
  - Map outreach_status values to Spanish labels and colors:
    - `none` → "Sin contactar" (default/grey)
    - `pending` → "Pendiente" (orange)
    - `contacted` → "Contactado" (blue)
    - `responded` → "Respondió" (green)
    - `meeting_scheduled` → "Reunión agendada" (purple)
    - `completed` → "Completado" (success/green)
  - Only show chip for trade-fair-sourced suppliers (where `source === 'trade_fair'`) or when outreach_status is not 'none'

### Task 13: Create E2E test file
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_trade_fair_dashboard.md` to understand format
- Create `.claude/commands/e2e/test_supplier_outreach.md` with:
  - User story: Back-office user sends follow-up message to a trade fair supplier
  - Steps:
    1. Navigate to Suppliers page, verify it loads
    2. Find a supplier with trade fair source (or create one via API)
    3. Open quick actions menu for the supplier
    4. Click "Enviar Seguimiento" action
    5. Verify outreach dialog opens with template dropdown, channel checkboxes, preview
    6. Select "Solicitud de catálogo" template
    7. Verify email checkbox is checked, WeChat checkbox state matches supplier data
    8. Verify message preview renders with supplier name
    9. Click "Enviar" button
    10. Verify success feedback shows
    11. Verify dialog closes and outreach status chip updates on supplier row
  - Success criteria: Dialog opens, template renders, send succeeds, status updates

### Task 14: Run validation commands
- Execute all validation commands to ensure zero regressions

## Testing Strategy

### Unit Tests
- Test `OUTREACH_TEMPLATES` dict has all expected keys and placeholders
- Test `send_template_email()` renders templates correctly with mock data
- Test `send_template_message()` renders templates correctly
- Test `send_outreach()` orchestration handles email-only, wechat-only, and both channels
- Test outreach endpoint returns correct response structure
- Test outreach endpoint validates template name (400 on invalid)
- Test outreach endpoint handles supplier not found (404)
- Test outreach_status updates in repository

### Edge Cases
- Supplier has no contact_email → email channel should fail gracefully, wechat can still send
- Supplier has no wechat_id → wechat channel should fail gracefully, email can still send
- Supplier has neither email nor wechat_id → both channels fail, outreach_status unchanged
- Invalid template name → 400 error with descriptive message
- Empty channels list → 400 error (at least one channel required)
- Custom message override replaces template body but keeps template subject
- WeChat service in mock mode → still returns success with mock_mode=true
- Email service in mock mode → still returns success with mock_mode=true
- Template placeholders with missing supplier data → use fallback empty strings or "N/A"

## Acceptance Criteria
- [ ] `OUTREACH_TEMPLATES` dictionary exists with 3 templates: introduction, follow_up_catalog, follow_up_pricing
- [ ] `send_template_email()` renders templates with supplier data and sends via email service
- [ ] `send_template_message()` renders templates and sends via WeChat service
- [ ] `POST /api/suppliers/{id}/outreach` endpoint accepts template, channels, and custom_message
- [ ] Endpoint returns per-channel success/failure and updated outreach_status
- [ ] `GET /api/suppliers/outreach-templates` returns available templates with metadata
- [ ] `outreach_status` field is included in supplier API responses
- [ ] Frontend outreach dialog has template dropdown, channel checkboxes, message preview, send button
- [ ] "Enviar Seguimiento" action appears in supplier quick actions menu
- [ ] Outreach status chip displays on supplier rows with correct Spanish labels and colors
- [ ] WeChat channel checkbox is disabled when supplier has no wechat_id
- [ ] Email channel checkbox is disabled when supplier has no contact_email
- [ ] All UI text is in Spanish (Colombian)
- [ ] Backend tests pass
- [ ] Frontend TypeScript compiles without errors
- [ ] Frontend builds successfully

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -m pytest tests/ -v --tb=short` — Run all backend tests
- `cd apps/Client && npx tsc --noEmit` — Run TypeScript type checking
- `cd apps/Client && npm run build` — Run production build to catch any errors
- `cd apps/Client && npm run lint` — Run ESLint to check code quality
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_supplier_outreach.md` to validate outreach functionality E2E

## Notes
- The `outreach_status` column already exists in the `suppliers` table with a CHECK constraint allowing values: `none`, `pending`, `contacted`, `responded`, `meeting_scheduled`, `completed`. No database migration needed.
- The existing `send_supplier_introduction()` methods in both email_service and wechat_service can remain as-is for backward compatibility. The new template system is additive.
- Templates use Python `.format()` string interpolation with named placeholders: `{contact_name}`, `{sender_name}`, `{fair_name}`, `{company_name}`.
- The `sender_name` should come from a setting or default to the current user's name or "Kompass".
- This feature runs in parallel with Issue #148 (Supplier-to-Product Pipeline). No file conflicts expected as they touch different parts of the codebase.
- Future enhancement: Admin UI for creating/editing templates (stored in database instead of code). Current implementation uses code-level templates as a pragmatic first step.
- The outreach-templates endpoint must be registered BEFORE the `/{supplier_id}` catch-all route to avoid path conflicts in FastAPI.
