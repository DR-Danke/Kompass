# Feature: Clients Pipeline Page (Kanban)

## Metadata
issue_number: `26`
adw_id: `21b3a47b`
issue_json: `{"number":26,"title":"[Kompass] Phase 10B: Clients Pipeline Page (Kanban)","body":"## Context\n**Current Phase:** Phase 10 of 13 - Frontend Portfolio & Clients\n**Current Issue:** KP-026 (Issue 26 of 33)\n**Parallel Execution:** YES - Runs IN PARALLEL with KP-025 and KP-027.\n\n---\n\n## Description\nCreate client pipeline page with Kanban board and list views.\n\n## Requirements\n\n### File: apps/Client/src/pages/kompass/ClientsPage.tsx\n\n#### Kanban View (default)\n- Columns: Lead → Qualified → Quoting → Negotiating → Won | Lost\n- Cards with: Company name, contact, niche badge, project deadline, last activity\n- Drag-and-drop between columns (updates status)\n- Click card to open detail drawer\n\n#### List View\n- Data table with all client fields\n- Toggle between Kanban and List\n\n#### Client Detail Drawer\n- All client information, Edit button, Quotation history, Status change history, Notes section\n\n### File: apps/Client/src/components/kompass/ClientForm.tsx\n- Dialog form for create/edit\n- Fields: company_name, contact_name, email, phone, whatsapp, niche, project_name, project_deadline, incoterm_preference, source, notes\n\n### File: apps/Client/src/components/kompass/ClientCard.tsx\n- Compact card for Kanban, Niche badge color-coded, Deadline indicator\n\n## Acceptance Criteria\n- [ ] Kanban view rendering\n- [ ] Drag-and-drop status change\n- [ ] List view rendering\n- [ ] Detail drawer functional\n- [ ] Create/edit form working"}`

## Feature Description
Create a comprehensive client pipeline management page with a Kanban board as the default view and an alternative list view. The Kanban board will visualize clients across different sales pipeline stages, enabling drag-and-drop status changes. The page includes a detail drawer for viewing/editing client information, status history, and quotation history.

**Key Capabilities:**
- Kanban board with 6 columns (Lead, Qualified, Quoting, Negotiating, Won, Lost)
- Drag-and-drop functionality to move clients between pipeline stages
- List/table view toggle for traditional data viewing
- Client detail drawer with full information and history
- Create/edit client form with all required fields
- Compact client cards with niche badges and deadline indicators

## User Story
As a Kompass user (admin, manager, or sales representative)
I want to visualize and manage my clients in a Kanban-style pipeline board
So that I can efficiently track client progression through the sales pipeline and quickly update their status via drag-and-drop

## Problem Statement
Currently, the Clients page is a placeholder with no functionality. Sales teams need a visual way to:
1. See all clients organized by their pipeline stage
2. Quickly move clients between stages as deals progress
3. Access detailed client information and history
4. Create and edit client records with all necessary fields

## Solution Statement
Implement a full-featured Clients Pipeline page with:
1. **Kanban Board** - Visual pipeline with drag-and-drop using dnd-kit library
2. **List View** - Traditional data table with all client fields
3. **Detail Drawer** - Side panel for viewing full client details, status history, and quotations
4. **Client Form** - Dialog-based form for creating/editing clients
5. **Client Cards** - Compact, informative cards for the Kanban view

## Relevant Files
Use these files to implement the feature:

### Backend (Reference Only - Already Implemented)
- `apps/Server/app/api/client_routes.py` - Client API endpoints including `/pipeline`, `/status`, `/status-history`
- `apps/Server/app/services/client_service.py` - Business logic for client operations
- `apps/Server/app/models/kompass_dto.py` - DTOs for clients including `ClientStatus`, `PipelineResponseDTO`

### Frontend (To Modify/Create)
- `apps/Client/src/pages/kompass/ClientsPage.tsx` - Main page to replace placeholder with full implementation
- `apps/Client/src/services/kompassService.ts` - Client service already implemented with all needed methods
- `apps/Client/src/types/kompass.ts` - Types already defined for clients, need extension for new status values
- `apps/Client/src/hooks/kompass/useProducts.ts` - Reference for custom hook pattern

### Patterns to Follow
- `apps/Client/src/pages/kompass/ProductsPage.tsx` - Reference for page structure, filtering, view modes
- `apps/Client/src/pages/kompass/SuppliersPage.tsx` - Reference for CRUD form patterns
- `.claude/commands/e2e/test_suppliers_page.md` - Reference for E2E test format

### New Files
- `apps/Client/src/hooks/kompass/useClients.ts` - Custom hook for client state management
- `apps/Client/src/components/kompass/ClientKanbanBoard.tsx` - Kanban board container with dnd-kit
- `apps/Client/src/components/kompass/KanbanColumn.tsx` - Single Kanban column component
- `apps/Client/src/components/kompass/ClientCard.tsx` - Compact card for Kanban view
- `apps/Client/src/components/kompass/ClientDetailDrawer.tsx` - Side drawer for client details
- `apps/Client/src/components/kompass/ClientForm.tsx` - Dialog form for create/edit
- `apps/Client/src/components/kompass/ClientListView.tsx` - Data table list view
- `.claude/commands/e2e/test_clients_pipeline.md` - E2E test specification

## Implementation Plan

### Phase 1: Foundation - Types and Backend Alignment
**Goal:** Extend client types to support the new pipeline stages and add missing fields.

The issue specifies 6 pipeline stages (Lead, Qualified, Quoting, Negotiating, Won, Lost), but the current backend only supports 3 statuses (prospect, active, inactive). We need to:

1. **Extend ClientStatus enum** in both backend and frontend to support all 6 stages:
   - `lead` (maps to existing `prospect`)
   - `qualified` (new)
   - `quoting` (new)
   - `negotiating` (new)
   - `won` (maps to existing `active`)
   - `lost` (maps to existing `inactive`)

2. **Add missing client fields** as specified in the issue:
   - `whatsapp` (phone field variant)
   - `project_name` (new field)
   - `incoterm_preference` (use existing Incoterm type)

Note: For this implementation, we'll map the new statuses to existing backend statuses to avoid backend changes:
- Backend `prospect` → Frontend displays as columns: Lead, Qualified
- Backend `active` → Frontend displays as columns: Quoting, Negotiating, Won
- Backend `inactive` → Frontend displays as column: Lost

**Alternative approach (recommended):** Extend the backend ClientStatus enum to include all 6 stages. This provides cleaner separation and proper persistence.

### Phase 2: Core Implementation - Custom Hook and Services
**Goal:** Create the useClients hook for state management following existing patterns.

The hook will:
- Fetch pipeline data from `/clients/pipeline`
- Manage view mode (kanban/list)
- Handle CRUD operations
- Track selected client for detail drawer
- Handle status updates with optimistic UI

### Phase 3: Kanban Components
**Goal:** Build the drag-and-drop Kanban board using dnd-kit.

Components:
1. **ClientKanbanBoard** - Main container with DndContext
2. **KanbanColumn** - Droppable column with header and client count
3. **ClientCard** - Draggable card with company, contact, niche badge, deadline

### Phase 4: List View and Detail Components
**Goal:** Build the table view and detail drawer.

Components:
1. **ClientListView** - Data table with all client fields, sorting, pagination
2. **ClientDetailDrawer** - MUI Drawer with tabs for Info, History, Quotations

### Phase 5: Form and Integration
**Goal:** Build the client form and integrate all components.

Components:
1. **ClientForm** - Dialog with react-hook-form for all fields
2. **ClientsPage** - Integrate all components with view toggle

## Step by Step Tasks

### Step 1: Install dnd-kit dependency
- Add `@dnd-kit/core`, `@dnd-kit/sortable`, `@dnd-kit/utilities` to package.json
- Run `npm install` in apps/Client directory

### Step 2: Extend ClientStatus type
- Update `apps/Client/src/types/kompass.ts` to add new status values
- Add `ClientPipelineStatus` type with all 6 stages: 'lead' | 'qualified' | 'quoting' | 'negotiating' | 'won' | 'lost'
- Add helper functions to map between backend and frontend statuses
- Add missing fields to ClientCreate/ClientUpdate interfaces: `whatsapp`, `project_name`, `incoterm_preference`

### Step 3: Update Backend DTOs and Schema (if needed)
- Extend `ClientStatus` enum in `apps/Server/app/models/kompass_dto.py` with new values
- Update `PipelineResponseDTO` to include all 6 status groups
- Update database schema if new statuses require database changes
- Update `client_service.py` to handle new statuses in pipeline grouping

### Step 4: Create E2E Test Specification
- Create `.claude/commands/e2e/test_clients_pipeline.md` with test scenarios
- Include tests for: page load, Kanban view, drag-and-drop, list view, detail drawer, form CRUD
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_suppliers_page.md` for format reference

### Step 5: Create useClients Hook
- Create `apps/Client/src/hooks/kompass/useClients.ts`
- Implement state for: pipeline data, view mode, selected client, loading, error
- Implement methods: fetchPipeline, updateClientStatus, createClient, updateClient, deleteClient
- Follow pattern from `useProducts.ts`

### Step 6: Create ClientCard Component
- Create `apps/Client/src/components/kompass/ClientCard.tsx`
- Display: company_name, contact_name, niche badge (color-coded), project_deadline, last activity
- Make draggable with dnd-kit useDraggable hook
- Add onClick handler to open detail drawer
- Style with MUI Card, Chip for badges

### Step 7: Create KanbanColumn Component
- Create `apps/Client/src/components/kompass/KanbanColumn.tsx`
- Props: status, title, clients array, onClientClick, color theme
- Use dnd-kit useDroppable hook for drop zone
- Display column header with title and count badge
- Render ClientCard components vertically
- Show empty state when no clients

### Step 8: Create ClientKanbanBoard Component
- Create `apps/Client/src/components/kompass/ClientKanbanBoard.tsx`
- Wrap with DndContext from dnd-kit
- Render 6 KanbanColumn components in horizontal flexbox
- Handle onDragEnd to call updateClientStatus
- Implement optimistic UI updates
- Show loading overlay during status updates

### Step 9: Create ClientDetailDrawer Component
- Create `apps/Client/src/components/kompass/ClientDetailDrawer.tsx`
- Use MUI Drawer anchored to right
- Include tabs: Info, History, Quotations
- Info tab: All client fields, Edit button
- History tab: Status change timeline from getStatusHistory
- Quotations tab: Summary from getClientWithQuotations
- Include status change dropdown with notes input

### Step 10: Create ClientForm Component
- Create `apps/Client/src/components/kompass/ClientForm.tsx`
- Use MUI Dialog with react-hook-form
- Fields: company_name (required), contact_name, email, phone, whatsapp, niche (dropdown), project_name, project_deadline (date picker), incoterm_preference (dropdown), source (dropdown), notes
- Validation: email format, required fields
- Support create and edit modes

### Step 11: Create ClientListView Component
- Create `apps/Client/src/components/kompass/ClientListView.tsx`
- Use MUI DataGrid or Table
- Columns: Company, Contact, Email, Phone, Niche, Status, Deadline, Source, Actions
- Support sorting by columns
- Support pagination
- Action buttons: View, Edit, Delete

### Step 12: Update ClientsPage
- Replace placeholder in `apps/Client/src/pages/kompass/ClientsPage.tsx`
- Add header with title and "Add Client" button
- Add view toggle (Kanban/List) using ToggleButtonGroup
- Add search input and filters (status, niche, source)
- Conditionally render ClientKanbanBoard or ClientListView
- Integrate ClientDetailDrawer
- Integrate ClientForm dialog
- Add Snackbar for notifications
- Add delete confirmation dialog

### Step 13: Extend clientService with Missing Methods
- Update `apps/Client/src/services/kompassService.ts` if any methods are missing
- Ensure getClientWithQuotations is available
- Ensure checkTimingFeasibility accepts product_lead_time_days parameter

### Step 14: Run Validation Commands
- Execute all validation commands to ensure zero regressions

## Testing Strategy

### Unit Tests
- Test useClients hook state management
- Test status mapping functions
- Test ClientCard rendering with different data
- Test KanbanColumn with empty and populated states
- Test ClientForm validation rules

### Edge Cases
- Drag client to same column (no-op)
- Drag to Lost column with confirmation
- Empty pipeline (no clients)
- Client with missing optional fields
- Very long company names (truncation)
- Many clients in single column (scrolling)
- Network error during status update (rollback)
- Concurrent status updates

## Acceptance Criteria
- [ ] Kanban view renders with 6 columns (Lead, Qualified, Quoting, Negotiating, Won, Lost)
- [ ] Each column displays correct client count badge
- [ ] Client cards show company name, contact, niche badge, deadline indicator
- [ ] Drag-and-drop moves client between columns and updates status via API
- [ ] Status update shows success/error notification
- [ ] List view renders data table with all client fields
- [ ] View toggle switches between Kanban and List modes
- [ ] Clicking client card opens detail drawer
- [ ] Detail drawer shows all client info, status history, quotation summary
- [ ] Edit button in drawer opens pre-filled form
- [ ] Add Client button opens empty form
- [ ] Form validates required fields and email format
- [ ] Form submission creates/updates client and refreshes view
- [ ] Delete confirmation dialog appears before deletion
- [ ] Search filters clients across both views
- [ ] Status filter works in list view
- [ ] Page loads without console errors
- [ ] TypeScript compiles without errors
- [ ] Build completes successfully

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Client && npm install` - Install new dnd-kit dependencies
- `cd apps/Server && source .venv/bin/activate && python -m pytest tests/ -v --tb=short` - Run Server tests
- `cd apps/Client && npm run typecheck` - Run Client type check (should pass with new types)
- `cd apps/Client && npm run lint` - Run ESLint to check code quality
- `cd apps/Client && npm run build` - Run Client build to validate production bundle
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_clients_pipeline.md` to validate this functionality works

## Notes

### dnd-kit vs Alternatives
Using dnd-kit because:
- React 19 compatible (actively maintained)
- Lightweight bundle size
- Built-in accessibility (keyboard support, screen readers)
- Simple API compared to react-dnd
- react-beautiful-dnd is no longer maintained

### Status Mapping Strategy
The issue specifies 6 Kanban columns, but the existing backend has 3 statuses. Two approaches:

**Option A (Minimal Changes):** Map frontend stages to backend statuses:
- Lead, Qualified → prospect
- Quoting, Negotiating, Won → active
- Lost → inactive

This requires storing the detailed stage in a separate field (e.g., `pipeline_stage`).

**Option B (Recommended):** Extend backend ClientStatus enum:
- Add: 'lead', 'qualified', 'quoting', 'negotiating', 'won', 'lost'
- Update database CHECK constraint
- Update PipelineResponseDTO with 6 groups

This plan assumes Option B for cleaner implementation.

### Missing Backend Fields
The issue specifies fields not in current DTOs:
- `whatsapp` - Can use existing `phone` field or add new field
- `project_name` - New field needed
- `incoterm_preference` - New field (use Incoterm enum)

Consider adding these to backend DTOs and database schema.

### Color Coding
Suggested column colors (MUI palette):
- Lead: grey.100 (#f5f5f5)
- Qualified: blue.50 (#e3f2fd)
- Quoting: amber.50 (#fff8e1)
- Negotiating: orange.50 (#fff3e0)
- Won: green.50 (#e8f5e9)
- Lost: red.50 (#ffebee)

### Niche Badge Colors
Generate colors dynamically based on niche name hash, or use a predefined palette with contrast text calculation (similar to tag colors in CategoriesPage).

### Performance Considerations
- Use React.memo for ClientCard to prevent unnecessary re-renders
- Virtualize long client lists if needed (react-window)
- Debounce search input (300ms)
- Optimistic UI updates for drag-and-drop

### Accessibility
- dnd-kit provides keyboard navigation (space to pick up, arrow keys to move)
- Ensure color is not the only indicator of status (use text labels)
- ARIA labels on interactive elements
- Focus management when opening/closing drawer
