# Follow-Up Message Templates

**ADW ID:** 26a0e280
**Date:** 2026-03-09
**Specification:** specs/issue-147-adw-26a0e280-sdlc_planner-followup-message-templates.md

## Overview

Adds a configurable follow-up message template system for supplier outreach after trade fair meetings. Back-office users can send templated emails and/or WeChat messages to suppliers directly from the Suppliers page, with template selection, channel toggling, message preview, and optional custom message override. The system tracks outreach status per supplier with visual status chips.

## What Was Built

- **3 outreach message templates**: introduction, catalog request, and pricing inquiry — defined as a server-side `OUTREACH_TEMPLATES` dictionary with placeholder interpolation
- **Template email sending** (`EmailService.send_template_email`) — renders templates with supplier data and sends via SMTP (or mock mode)
- **Template WeChat sending** (`WeChatService.send_template_message`) — renders templates and sends via WeChat API (or mock mode)
- **Outreach orchestration** (`SupplierService.send_outreach`) — coordinates multi-channel sends and updates `outreach_status`
- **REST API endpoints**: `GET /api/suppliers/outreach-templates` and `POST /api/suppliers/{id}/outreach`
- **Outreach dialog UI** on SuppliersPage — template dropdown, channel checkboxes (email/WeChat), message preview, custom message field, and send button
- **"Enviar Seguimiento" quick action** in the supplier context menu
- **Outreach status column** in the supplier table with color-coded Spanish-label chips
- **Frontend types and API client methods** for the outreach workflow
- **E2E test specification** for the outreach feature

## Technical Implementation

### Files Modified

- `apps/Server/app/services/email_service.py`: Added `OUTREACH_TEMPLATES` dictionary (3 templates) and `get_templates()` / `send_template_email()` methods
- `apps/Server/app/services/wechat_service.py`: Added `send_template_message()` method using shared `OUTREACH_TEMPLATES`
- `apps/Server/app/services/supplier_service.py`: Added `get_outreach_templates()` and `send_outreach()` orchestration methods
- `apps/Server/app/api/supplier_routes.py`: Added `GET /outreach-templates` and `POST /{supplier_id}/outreach` endpoints
- `apps/Server/app/models/kompass_dto.py`: Added `SupplierOutreachRequestDTO`, `SupplierOutreachResultDTO`, `OutreachTemplateDTO`; added `outreach_status` to `SupplierResponseDTO` and `SupplierWithProductCountDTO`
- `apps/Server/app/repository/kompass_repository.py`: Added `update_outreach_status()` method; updated all supplier SELECT/RETURNING queries to include `outreach_status` column; updated `_row_to_dict_extended()` index mapping
- `apps/Client/src/types/kompass.ts`: Added `OutreachStatus`, `SupplierOutreachRequest`, `SupplierOutreachResult`, `OutreachTemplate` types; added `outreach_status` to `SupplierResponse`
- `apps/Client/src/services/kompassService.ts`: Added `getOutreachTemplates()` and `sendOutreach()` to `supplierService`
- `apps/Client/src/pages/kompass/SuppliersPage.tsx`: Added outreach dialog, status column, state management, and outreach handlers
- `apps/Client/src/components/kompass/SupplierQuickActionsMenu.tsx`: Added "Enviar Seguimiento" menu item with `SendIcon`
- `.claude/commands/e2e/test_supplier_outreach.md`: New E2E test specification

### Key Changes

- **Templates use Python `.format()` interpolation** with named placeholders: `{contact_name}`, `{company_name}`, `{fair_name}`, `{sender_name}`. Missing data falls back to empty strings or defaults (e.g., "the trade fair").
- **Channel validation is graceful**: if a supplier lacks `contact_email` or `wechat_id`, that channel is skipped (not errored). The UI disables the corresponding checkbox.
- **Outreach status is automatically updated to `"contacted"`** when at least one message is successfully sent, using the existing `outreach_status` CHECK constraint column on the `suppliers` table.
- **The `outreach-templates` route is registered before `/{supplier_id}`** to avoid FastAPI path conflicts.
- **All UI labels are in Spanish** (Colombian): "Enviar Seguimiento", "Plantilla", "Canales", "Vista previa", "Enviar", "Cancelar", and status labels like "Contactado", "Respondió", etc.

## How to Use

1. Navigate to the **Suppliers** page
2. Click the **three-dot menu** (quick actions) on any supplier row
3. Select **"Enviar Seguimiento"** (disabled if supplier has no email or phone)
4. In the outreach dialog:
   - Choose a **template** from the dropdown (Presentación inicial, Solicitud de catálogo, Solicitud de precios)
   - Toggle **Email** and/or **WeChat** channels (disabled if supplier lacks contact info)
   - Review the **message preview**
   - Optionally enter a **custom message** to override the template body
   - Click **"Enviar"**
5. A success/error alert displays the result
6. The supplier's **outreach status chip** updates in the table (e.g., "Contactado")

## Configuration

- **SMTP settings**: Email sending uses the existing `EmailService` configuration (SMTP host, port, credentials via environment variables). Falls back to mock mode if SMTP is not configured.
- **WeChat settings**: WeChat sending uses the existing `WeChatService` configuration (`WECHAT_*` environment variables). Falls back to mock mode if not configured.
- **No database migration needed**: The `outreach_status` column already exists on the `suppliers` table with a CHECK constraint for valid values: `none`, `pending`, `contacted`, `responded`, `meeting_scheduled`, `completed`.

## Testing

- **Backend**: `cd apps/Server && python -m pytest tests/ -v --tb=short`
- **Frontend type check**: `cd apps/Client && npx tsc --noEmit`
- **Frontend build**: `cd apps/Client && npm run build`
- **Frontend lint**: `cd apps/Client && npm run lint`
- **E2E**: Run the `/e2e:test_supplier_outreach` slash command to validate the full outreach workflow

## Notes

- Templates are currently defined in code (`OUTREACH_TEMPLATES` dict in `email_service.py`). A future enhancement could store them in the database with an admin UI for editing.
- The `send_template_email()` wraps plain text in simple HTML for email rendering, converting newlines to `<br>` tags.
- Both email and WeChat services share the same template dictionary to ensure consistency across channels.
- The outreach status chip only displays when the status is not `"none"`, keeping the table clean for suppliers that haven't been contacted.
