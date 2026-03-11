# Feature: Editable Outreach Email Templates

## Metadata
issue_number: `166`
adw_id: `1ec0e5cf`
issue_json: ``

## Feature Description
Move the 3 existing outreach email templates (introduction, follow_up_catalog, follow_up_pricing) from hardcoded Python (`OUTREACH_TEMPLATES` dict in `email_service.py`) to database-stored records in a new `outreach_templates` table. Add an admin/manager UI on the Settings page to edit template names, subjects, and bodies with live preview and placeholder insertion. Update the existing outreach flow (Suppliers page dialog and auto-send on business card creation) to read templates from the database with fallback to hardcoded defaults for resilience.

## User Story
As an admin or manager
I want to edit outreach email templates (subject lines, body text, and names) directly from the application UI
So that I can customize follow-up email content without requiring code changes or developer intervention

## Problem Statement
Outreach email templates are hardcoded in `apps/Server/app/services/email_service.py` as the `OUTREACH_TEMPLATES` dict. Any change to template content (subject, body, name) requires a code change, commit, and redeployment. This creates a bottleneck where business users depend on developers for simple text changes to outreach emails.

## Solution Statement
Create a new `outreach_templates` database table seeded with the 3 existing templates. Build a repository and service layer to read/update templates from the database. Modify the existing `EmailService` to fetch templates from the database (with hardcoded fallback). Add API endpoints for template CRUD (list, get, update, reset-to-default). Build a template editor UI on the Settings page with editable fields, placeholder variable chips, live preview, and active/inactive toggle. Update the Suppliers page outreach dialog to filter by active templates only.

## Relevant Files
Use these files to implement the feature:

### Existing Files to Modify
- `apps/Server/database/schema.sql` — Add `outreach_templates` table definition and trigger at the end of the file (after quotation_items trigger, line ~560)
- `apps/Server/app/models/kompass_dto.py` — Update `OutreachTemplateDTO` (line ~487) to include `id`, `body`, `is_active`, `sort_order`, `available_placeholders` fields; add `OutreachTemplateUpdateDTO`
- `apps/Server/app/services/email_service.py` — Keep `OUTREACH_TEMPLATES` dict as defaults; modify `get_templates()` and `send_template_email()` to read from DB with fallback
- `apps/Server/app/services/supplier_service.py` — Update `get_outreach_templates()` to pass through from new template service
- `apps/Server/app/api/supplier_routes.py` — Update existing `GET /outreach-templates` route; add `GET /outreach-templates/{template_id}`, `PUT /outreach-templates/{template_id}`, `POST /outreach-templates/{template_id}/reset` routes
- `apps/Client/src/types/kompass.ts` — Update `OutreachTemplate` interface (line ~1275) to include `id`, `body`, `is_active`, `sort_order`, `available_placeholders`; add `OutreachTemplateUpdate` interface
- `apps/Client/src/services/kompassService.ts` — Add `getTemplate()`, `updateTemplate()`, `resetTemplate()` to `supplierService`
- `apps/Client/src/pages/kompass/SettingsPage.tsx` — Replace placeholder content with template management UI
- `apps/Client/src/pages/kompass/SuppliersPage.tsx` — Filter outreach dialog templates by `is_active === true`; show full body in preview
- `apps/Server/main.py` — Verify no new router registration needed (routes are under supplier_routes)

### New Files
- `apps/Server/app/repository/outreach_template_repository.py` — Repository for outreach_templates table CRUD
- `apps/Server/app/services/outreach_template_service.py` — Business logic for template management
- `apps/Server/database/migrations/add_outreach_templates.sql` — Migration SQL: CREATE TABLE + seed data
- `.claude/commands/e2e/test_editable_outreach_templates.md` — E2E test specification for this feature

### Reference Files (read for patterns)
- `apps/Server/app/repository/kompass_repository.py` — Repository pattern: database connection, cursor, commit/rollback, logging
- `apps/Server/app/config/database.py` — `get_database_connection()` and `close_database_connection()` imports
- `apps/Server/app/api/dependencies.py` — `get_current_user` dependency
- `apps/Server/app/api/rbac_dependencies.py` — `require_roles` dependency for admin/manager routes
- `.claude/commands/test_e2e.md` — E2E test runner instructions
- `.claude/commands/e2e/test_supplier_outreach.md` — Existing outreach E2E test (pattern reference)

## Implementation Plan
### Phase 1: Foundation
- Create the `outreach_templates` database table and seed migration with the 3 existing templates
- Create the backend repository layer to interact with the new table
- Create the backend service layer for template business logic
- Update DTOs to support the new template fields

### Phase 2: Core Implementation
- Update `EmailService` to read templates from the database with hardcoded fallback
- Add new API routes for template management (get single, update, reset)
- Update existing `GET /outreach-templates` route to read from DB
- Build the Settings page template editor UI with edit dialog, placeholder chips, live preview, and active toggle

### Phase 3: Integration
- Update the Suppliers page outreach dialog to filter by `is_active` and show full body preview
- Update frontend types and API service methods
- Create E2E test specification
- Validate all existing outreach flows continue working identically

## Step by Step Tasks

### Step 1: Create E2E Test Specification
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_supplier_outreach.md` to understand E2E test format
- Create `.claude/commands/e2e/test_editable_outreach_templates.md` with test steps for:
  - Navigate to Settings page, verify "Plantillas de Seguimiento" section
  - Verify 3 templates listed with name, key, active toggle
  - Click a template to open edit dialog
  - Verify editable fields: Name, Subject, Body
  - Verify placeholder chips are shown and clickable
  - Verify live preview panel renders with sample data
  - Edit a template field and save
  - Verify changes persist after page reload
  - Reset a template to default and verify original content restored
  - Toggle a template inactive, navigate to Suppliers page, verify template hidden from outreach dropdown
  - Toggle back active, verify template reappears
  - All UI labels in Spanish (Colombian)

### Step 2: Database — Create Table and Migration
- Add `outreach_templates` table to `apps/Server/database/schema.sql` after the quotation tables section
- Include columns: `id UUID PK`, `key VARCHAR(50) UNIQUE NOT NULL`, `name VARCHAR(100) NOT NULL`, `subject VARCHAR(255) NOT NULL`, `body TEXT NOT NULL`, `is_active BOOLEAN DEFAULT true`, `sort_order INTEGER DEFAULT 0`, `created_at TIMESTAMPTZ`, `updated_at TIMESTAMPTZ`
- Add `update_outreach_templates_updated_at` trigger using existing `update_updated_at_column()` function
- Create `apps/Server/database/migrations/add_outreach_templates.sql` with:
  - CREATE TABLE IF NOT EXISTS statement
  - Trigger creation
  - INSERT seed data for the 3 existing templates from `OUTREACH_TEMPLATES` dict with exact subjects and bodies, using `ON CONFLICT (key) DO NOTHING`

### Step 3: Backend — Update DTOs
- In `apps/Server/app/models/kompass_dto.py`, update `OutreachTemplateDTO`:
  - Add `id: UUID` field
  - Add `body: str` field (full body text)
  - Keep `body_preview: str` field
  - Add `is_active: bool = True`
  - Add `sort_order: int = 0`
  - Add `available_placeholders: List[str]` (default: `["{contact_name}", "{company_name}", "{fair_name}", "{sender_name}"]`)
- Add `OutreachTemplateUpdateDTO(BaseModel)`:
  - `name: Optional[str] = None`
  - `subject: Optional[str] = None`
  - `body: Optional[str] = None`
  - `is_active: Optional[bool] = None`

### Step 4: Backend — Create Template Repository
- Create `apps/Server/app/repository/outreach_template_repository.py`
- Follow patterns from `kompass_repository.py`: import `get_database_connection`, `close_database_connection`, use `RealDictCursor`
- Implement class `OutreachTemplateRepository` with methods:
  - `list_templates(active_only: bool = True) -> List[Dict]` — SELECT ordered by `sort_order`, optionally filtered by `is_active = true`
  - `get_by_key(key: str) -> Optional[Dict]` — SELECT WHERE key = %s
  - `get_by_id(template_id: UUID) -> Optional[Dict]` — SELECT WHERE id = %s
  - `update(template_id: UUID, updates: Dict) -> Optional[Dict]` — UPDATE with dynamic SET clause for provided fields (name, subject, body, is_active), RETURNING *
  - `reset_to_default(template_id: UUID) -> Optional[Dict]` — Get template by ID to find its key, look up default from `OUTREACH_TEMPLATES` dict, UPDATE with default values, RETURNING *
- Create singleton: `outreach_template_repository = OutreachTemplateRepository()`

### Step 5: Backend — Create Template Service
- Create `apps/Server/app/services/outreach_template_service.py`
- Import `outreach_template_repository` and `OUTREACH_TEMPLATES` from `email_service`
- Implement class `OutreachTemplateService` with methods:
  - `list_templates(active_only: bool = True) -> List[Dict]` — calls repository, enriches each with `body_preview` (first 150 chars + "...") and `available_placeholders`
  - `get_template(key: str) -> Dict` — get by key, fallback to `OUTREACH_TEMPLATES` if not in DB, raise `ValueError` if not found anywhere
  - `get_template_by_id(template_id: UUID) -> Dict` — get by ID, raise `ValueError` if not found
  - `update_template(template_id: UUID, updates: Dict) -> Dict` — validate and update, return enriched result
  - `reset_template(template_id: UUID) -> Dict` — reset to default content from `OUTREACH_TEMPLATES`
  - `get_template_body_rendered(key: str, context: Dict) -> Tuple[str, str]` — get template, substitute placeholders in subject and body, return `(rendered_subject, rendered_body)`
- Create singleton: `outreach_template_service = OutreachTemplateService()`
- Available placeholders constant: `AVAILABLE_PLACEHOLDERS = ["{contact_name}", "{company_name}", "{fair_name}", "{sender_name}"]`

### Step 6: Backend — Update EmailService
- In `apps/Server/app/services/email_service.py`:
  - Keep `OUTREACH_TEMPLATES` dict unchanged (used as defaults/fallback)
  - Modify `get_templates()` static method → regular method that reads from `outreach_template_repository.list_templates(active_only=True)`. If DB call fails/returns empty, fall back to building list from `OUTREACH_TEMPLATES` dict
  - Modify `send_template_email()` to fetch template from `outreach_template_repository.get_by_key(template_name)`. If not found in DB, fall back to `OUTREACH_TEMPLATES[template_name]`. Use fetched template's subject and body for rendering
- Update `supplier_service.py` `get_outreach_templates()` to call updated `email_service.get_templates()` (may need to adjust since it's no longer static)

### Step 7: Backend — Add API Routes
- In `apps/Server/app/api/supplier_routes.py`:
  - Update existing `GET /outreach-templates` to call `outreach_template_service.list_templates()` and return enriched DTOs with `id`, `body`, `is_active`, `sort_order`, `available_placeholders`
  - Add `GET /outreach-templates/{template_id}` — requires `get_current_user`, calls `outreach_template_service.get_template_by_id()`, returns `OutreachTemplateDTO`
  - Add `PUT /outreach-templates/{template_id}` — requires `require_roles(['admin', 'manager'])`, accepts `OutreachTemplateUpdateDTO`, calls `outreach_template_service.update_template()`, returns `OutreachTemplateDTO`
  - Add `POST /outreach-templates/{template_id}/reset` — requires `require_roles(['admin', 'manager'])`, calls `outreach_template_service.reset_template()`, returns `OutreachTemplateDTO`
- Import `OutreachTemplateUpdateDTO` and `outreach_template_service` at top of file

### Step 8: Frontend — Update Types
- In `apps/Client/src/types/kompass.ts`, update `OutreachTemplate` interface:
  - Add `id: string`
  - Add `body: string`
  - Change `body_preview: string` (keep)
  - Add `is_active: boolean`
  - Add `sort_order: number`
  - Add `available_placeholders: string[]`
- Add new interface `OutreachTemplateUpdate`:
  - `name?: string`
  - `subject?: string`
  - `body?: string`
  - `is_active?: boolean`

### Step 9: Frontend — Update API Service
- In `apps/Client/src/services/kompassService.ts`, add methods to `supplierService`:
  - `getTemplate(templateId: string): Promise<OutreachTemplate>` — `GET /suppliers/outreach-templates/${templateId}`
  - `updateTemplate(templateId: string, updates: OutreachTemplateUpdate): Promise<OutreachTemplate>` — `PUT /suppliers/outreach-templates/${templateId}`
  - `resetTemplate(templateId: string): Promise<OutreachTemplate>` — `POST /suppliers/outreach-templates/${templateId}/reset`
- Import `OutreachTemplateUpdate` type

### Step 10: Frontend — Build Template Editor on Settings Page
- Replace `apps/Client/src/pages/kompass/SettingsPage.tsx` placeholder with template management UI
- Use MUI components following existing patterns in the codebase
- **Template List Section** ("Plantillas de Seguimiento"):
  - Show all templates in a list/table with columns: Name, Key, Subject (truncated), Active toggle
  - Active/Inactive toggle (Switch component) — calls `updateTemplate` with `is_active` change
  - Click row to open edit dialog
- **Edit Dialog** ("Editar Plantilla"):
  - `TextField` for Name ("Nombre")
  - `TextField` for Subject ("Asunto")
  - `TextField` multiline for Body ("Cuerpo del Mensaje")
  - "Variables Disponibles" section with clickable `Chip` components for each placeholder (`{contact_name}`, `{company_name}`, `{fair_name}`, `{sender_name}`) — clicking inserts at cursor position in body field
  - "Vista Previa" panel showing rendered template with sample data: `{contact_name}` → "Juan Pérez", `{company_name}` → "Empresa ABC", `{fair_name}` → "Canton Fair 2026", `{sender_name}` → "Kompass"
  - "Guardar" button (primary) — calls PUT endpoint
  - "Cancelar" button — closes dialog
  - "Restaurar Original" button (secondary) — confirmation dialog, then calls POST reset endpoint
- State management with `useState` for templates list, selected template, edit dialog open, loading, snackbar
- Fetch templates on mount with `useEffect`
- Show success/error `Snackbar` after save/reset operations
- Handle unrecognized placeholders: warn with helper text if body contains `{...}` patterns not in `available_placeholders`
- All labels in Spanish (Colombian)

### Step 11: Frontend — Update Outreach Dialog on Suppliers Page
- In `apps/Client/src/pages/kompass/SuppliersPage.tsx`:
  - Filter `outreachTemplates` state to only show templates where `is_active === true` in the template dropdown
  - Update the "Vista previa" section to show the full `body` (rendered with supplier context) instead of just `body_preview`
  - Use the selected template's `body` field with placeholder substitution for preview rendering

### Step 12: Run Validation Commands
- Run `cd apps/Server && python -m pytest tests/ -v --tb=short` to validate backend tests pass
- Run `cd apps/Client && npx tsc --noEmit` to validate TypeScript compilation
- Run `cd apps/Client && npm run build` to validate frontend builds successfully
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_editable_outreach_templates.md` E2E test

## Testing Strategy
### Unit Tests
- **Repository tests**: Verify `list_templates`, `get_by_key`, `get_by_id`, `update`, `reset_to_default` return correct data shapes
- **Service tests**: Verify `list_templates` enriches with `body_preview` and `available_placeholders`; verify `get_template_body_rendered` substitutes all placeholders correctly; verify fallback to `OUTREACH_TEMPLATES` when DB is empty
- **EmailService tests**: Verify `get_templates()` reads from DB; verify `send_template_email()` uses DB template; verify fallback when template not in DB
- **API route tests**: Verify auth requirements (all roles for GET, admin/manager for PUT/POST reset); verify 404 for invalid template_id; verify update returns modified template

### Edge Cases
- Template not found in DB → falls back to hardcoded `OUTREACH_TEMPLATES` dict
- All templates deactivated → outreach dialog shows empty dropdown, user cannot send
- Template body contains unrecognized placeholder → UI warns but allows save
- Concurrent edits to same template → last write wins (acceptable for low-contention admin feature)
- Reset template that was never modified → no-op, returns default content
- Empty subject or body in update → validation should reject (fields required when provided)
- Very long body text → textarea handles scrolling, preview truncates reasonably

## Acceptance Criteria
- [ ] New `outreach_templates` table exists in database with UUID PK, key (unique), name, subject, body, is_active, sort_order, created_at, updated_at
- [ ] 3 existing templates are seeded with exact content matching current `OUTREACH_TEMPLATES` dict
- [ ] `GET /api/suppliers/outreach-templates` returns templates from database with full body, id, is_active, sort_order, available_placeholders
- [ ] `GET /api/suppliers/outreach-templates/{id}` returns single template (auth required)
- [ ] `PUT /api/suppliers/outreach-templates/{id}` updates template (admin/manager only)
- [ ] `POST /api/suppliers/outreach-templates/{id}/reset` resets to hardcoded default (admin/manager only)
- [ ] Settings page shows "Plantillas de Seguimiento" section with template list and active toggles
- [ ] Edit dialog allows editing name, subject, body with placeholder chips and live preview
- [ ] "Restaurar Original" resets template content with confirmation dialog
- [ ] Deactivated templates do not appear in Suppliers page outreach dialog dropdown
- [ ] All existing outreach flows (manual send, auto-send on card creation) continue working identically
- [ ] If template missing from DB, system falls back to hardcoded defaults
- [ ] All UI text in Spanish (Colombian)
- [ ] TypeScript compiles with zero errors
- [ ] Frontend builds successfully
- [ ] Backend tests pass

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -m pytest tests/ -v --tb=short` — Run backend tests to validate zero regressions
- `cd apps/Client && npx tsc --noEmit` — Run TypeScript type check to validate no type errors
- `cd apps/Client && npm run build` — Run frontend build to validate successful compilation
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_editable_outreach_templates.md` to validate the full feature works end-to-end

## Notes
- The `OUTREACH_TEMPLATES` dict in `email_service.py` is intentionally preserved as the source of truth for default/reset values. It serves dual purpose: seed data source and fallback when DB is unavailable.
- No new libraries are needed — this uses existing MUI components (Dialog, TextField, Chip, Switch, Snackbar, Table) and existing backend patterns (psycopg2, FastAPI, Pydantic).
- The migration file (`add_outreach_templates.sql`) should be run manually against the database or via the schema.sql re-application. There is no automated migration runner in this project.
- Template editing is a low-frequency admin operation, so optimistic updates and simple refetch-after-save pattern are sufficient (no need for WebSocket or real-time sync).
- The `send_supplier_introduction()` method in `EmailService` (used by auto-send on card creation) uses `_render_introduction_template()` which is separate from `OUTREACH_TEMPLATES`. Consider updating it to also use the DB template for consistency, but this is optional and can be a follow-up.
