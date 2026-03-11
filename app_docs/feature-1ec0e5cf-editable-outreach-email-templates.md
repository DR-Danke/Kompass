# Editable Outreach Email Templates

**ADW ID:** 1ec0e5cf
**Date:** 2026-03-10
**Specification:** specs/issue-166-adw-1ec0e5cf-editable-outreach-email-templates.md

## Overview

Moves the 3 hardcoded outreach email templates (introduction, follow_up_catalog, follow_up_pricing) from Python code to a new `outreach_templates` database table. Adds an admin/manager UI on the Settings page for editing template names, subjects, and bodies with live preview and placeholder insertion. Existing outreach flows read from the database with automatic fallback to hardcoded defaults.

## What Was Built

- **Database table** (`outreach_templates`) with UUID PK, unique key, name, subject, body, is_active toggle, and sort_order
- **Migration script** seeding the 3 existing templates with their original content
- **Repository layer** for template CRUD (list, get by key/ID, update, reset to default)
- **Service layer** with business logic, template enrichment, and rendered placeholder substitution
- **API endpoints** for listing (with active filter), getting, updating (admin/manager), and resetting templates
- **Settings page template editor** with edit dialog, placeholder chips, live preview, and active toggle
- **Suppliers page integration** filtering inactive templates from the outreach dropdown and showing full rendered body preview
- **E2E test specification** for the complete template management workflow

## Technical Implementation

### Files Modified

- `apps/Server/database/schema.sql`: Added `outreach_templates` table definition and `updated_at` trigger
- `apps/Server/database/migrations/add_outreach_templates.sql`: New migration with CREATE TABLE + seed data for 3 templates
- `apps/Server/app/models/kompass_dto.py`: Extended `OutreachTemplateDTO` with id, body, is_active, sort_order, available_placeholders; added `OutreachTemplateUpdateDTO`
- `apps/Server/app/repository/outreach_template_repository.py`: New repository with `list_templates`, `get_by_key`, `get_by_id`, `update`, `reset_to_default`
- `apps/Server/app/services/outreach_template_service.py`: New service with template listing (DB + fallback), CRUD, and placeholder rendering
- `apps/Server/app/services/email_service.py`: `get_templates()` and `send_template_email()` now read from DB first, falling back to `OUTREACH_TEMPLATES` dict
- `apps/Server/app/services/supplier_service.py`: Updated `get_outreach_templates()` to use instance method instead of static
- `apps/Server/app/api/supplier_routes.py`: Added `GET /outreach-templates/{id}`, `PUT /outreach-templates/{id}`, `POST /outreach-templates/{id}/reset`; updated `GET /outreach-templates` with `active_only` query param
- `apps/Client/src/types/kompass.ts`: Extended `OutreachTemplate` interface; added `OutreachTemplateUpdate` interface
- `apps/Client/src/services/kompassService.ts`: Added `getTemplate`, `updateTemplate`, `resetTemplate` to `supplierService`; updated `getOutreachTemplates` with `activeOnly` param
- `apps/Client/src/pages/kompass/SettingsPage.tsx`: Replaced placeholder with full template management UI
- `apps/Client/src/pages/kompass/SuppliersPage.tsx`: Filtered templates by `is_active`, added full body preview with placeholder substitution
- `.claude/commands/e2e/test_editable_outreach_templates.md`: E2E test specification

### Key Changes

- **DB-first with fallback**: Both `EmailService.get_templates()` and `send_template_email()` attempt DB reads first. If the DB call fails or returns empty, the hardcoded `OUTREACH_TEMPLATES` dict is used as fallback, ensuring zero downtime if the migration hasn't been applied.
- **RBAC enforcement**: Template updates and resets require `admin` or `manager` roles via `require_roles` dependency. Listing and viewing require any authenticated user.
- **Placeholder system**: Templates support 4 placeholders (`{contact_name}`, `{company_name}`, `{fair_name}`, `{sender_name}`). The UI shows clickable chips that insert at cursor position and warns about unrecognized `{...}` patterns.
- **Reset to default**: The reset endpoint looks up the template's key, fetches default values from the hardcoded `OUTREACH_TEMPLATES` dict, and overwrites name/subject/body while preserving is_active and sort_order.
- **Active toggle**: Templates can be deactivated via a switch on the Settings page. Inactive templates are hidden from the Suppliers page outreach dialog dropdown.

## How to Use

1. **Apply the migration**: Run `apps/Server/database/migrations/add_outreach_templates.sql` against the database to create the table and seed the 3 default templates
2. **Navigate to Settings**: Go to the Settings page (`/settings`) in the application
3. **View templates**: The "Plantillas de Seguimiento" section lists all 3 templates with name, key, subject, and active toggle
4. **Edit a template**: Click a template row or the "Editar" button to open the edit dialog
5. **Modify fields**: Edit the Name (Nombre), Subject (Asunto), or Body (Cuerpo del Mensaje)
6. **Insert placeholders**: Click the placeholder chips under "Variables Disponibles" to insert `{contact_name}`, `{company_name}`, `{fair_name}`, or `{sender_name}` at the cursor position
7. **Preview**: The "Vista Previa" panel shows the rendered template with sample data in real time
8. **Save**: Click "Guardar" to persist changes
9. **Reset to default**: Click "Restaurar Original" in the edit dialog to revert a template to its original content (with confirmation)
10. **Toggle active/inactive**: Use the switch in the template list to activate or deactivate a template. Inactive templates won't appear in the Suppliers page outreach dropdown

## Configuration

- **Database migration**: Must be applied manually — run `add_outreach_templates.sql` against the PostgreSQL database
- **No new environment variables** are required
- **No new dependencies** are required

## Testing

- **Backend**: `cd apps/Server && python -m pytest tests/ -v --tb=short`
- **Frontend typecheck**: `cd apps/Client && npx tsc --noEmit`
- **Frontend build**: `cd apps/Client && npm run build`
- **E2E**: Use `/test_e2e` with the `test_editable_outreach_templates` spec

## Notes

- The `OUTREACH_TEMPLATES` dict in `email_service.py` is intentionally preserved as the source of truth for default/reset values and as a fallback when the database is unavailable
- Template editing is a low-frequency admin operation; simple refetch-after-save pattern is used (no optimistic updates or WebSocket sync)
- The `send_supplier_introduction()` method uses a separate `_render_introduction_template()` which is not affected by this feature — it could be updated in a follow-up for consistency
- All UI labels are in Spanish (Colombian)
