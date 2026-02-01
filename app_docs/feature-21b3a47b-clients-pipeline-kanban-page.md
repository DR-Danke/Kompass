# Clients Pipeline Page (Kanban)

**ADW ID:** 21b3a47b
**Date:** 2026-02-01
**Specification:** specs/issue-26-adw-21b3a47b-clients-pipeline-kanban-page.md

## Overview

A comprehensive client pipeline management page with Kanban board as the default view and an alternative list view. The Kanban board visualizes clients across 6 sales pipeline stages (Lead, Qualified, Quoting, Negotiating, Won, Lost), enabling drag-and-drop status changes. Includes detail drawer for viewing/editing client information and status history, plus CRUD form for client management.

## What Was Built

- **Kanban Board**: Visual pipeline with 6 color-coded columns using dnd-kit for drag-and-drop
- **List View**: Data table with all client fields, sortable and paginated
- **Client Cards**: Compact cards displaying company name, contact, niche badge, deadline, and last activity
- **Detail Drawer**: Side panel with client details, status history timeline, and quotation summary
- **Client Form**: Dialog form for creating/editing clients with all required fields
- **useClients Hook**: State management for pipeline data, view modes, and CRUD operations

## Technical Implementation

### Files Modified

- `apps/Client/src/pages/kompass/ClientsPage.tsx`: Full implementation replacing placeholder, with view toggle, search, and component integration
- `apps/Client/src/types/kompass.ts`: Extended ClientStatus enum with 6 pipeline stages, added PipelineResponse type
- `apps/Client/src/services/kompassService.ts`: Added getPipeline, updateStatus, getStatusHistory, getClientWithQuotations methods
- `apps/Server/app/models/kompass_dto.py`: Extended ClientStatus enum, added StatusHistoryResponse and PipelineResponseDTO
- `apps/Server/app/services/client_service.py`: Added get_pipeline, update_status, get_status_history methods
- `apps/Server/app/api/client_routes.py`: Added /pipeline, /status, /status-history endpoints

### New Files Created

- `apps/Client/src/hooks/kompass/useClients.ts`: Custom hook for client state management with optimistic updates
- `apps/Client/src/components/kompass/ClientKanbanBoard.tsx`: DndContext wrapper with column layout and drag overlay
- `apps/Client/src/components/kompass/KanbanColumn.tsx`: Droppable column with header, count badge, and client list
- `apps/Client/src/components/kompass/ClientCard.tsx`: Draggable card with niche badge and deadline indicator
- `apps/Client/src/components/kompass/ClientDetailDrawer.tsx`: MUI Drawer with tabs for Info, History, Quotations
- `apps/Client/src/components/kompass/ClientForm.tsx`: Dialog form with react-hook-form validation
- `apps/Client/src/components/kompass/ClientListView.tsx`: MUI Table with sorting and actions
- `.claude/commands/e2e/test_clients_pipeline.md`: E2E test specification

### Key Changes

- Extended ClientStatus from 3 values (prospect, active, inactive) to 6 pipeline stages
- Implemented dnd-kit for React 19 compatible drag-and-drop functionality
- Added optimistic UI updates in useClients hook with rollback on error
- Pipeline endpoint returns clients grouped by their 6 status values
- Status history tracking with timestamp, previous/new status, and notes

## How to Use

1. Navigate to the Clients page from the sidebar
2. View clients organized in Kanban columns by default (Lead, Qualified, Quoting, Negotiating, Won, Lost)
3. Drag and drop client cards between columns to update their pipeline status
4. Click on a client card to open the detail drawer with full information
5. Use the toggle button to switch between Kanban and List views
6. Click "Add Client" to create a new client via the form dialog
7. Use the search bar to filter clients across all columns/rows
8. Edit or delete clients from the detail drawer or list view actions

## Configuration

No additional configuration required. The feature uses existing authentication and API infrastructure.

### Column Colors
- Lead: Grey (#f5f5f5)
- Qualified: Blue (#e3f2fd)
- Quoting: Amber (#fff8e1)
- Negotiating: Orange (#fff3e0)
- Won: Green (#e8f5e9)
- Lost: Red (#ffebee)

## Testing

Run the E2E test suite:
```bash
# From project root
cd apps/Client && npx playwright test --grep "clients pipeline"
```

Run backend tests:
```bash
cd apps/Server && .venv/bin/pytest tests/ -v --tb=short
```

Validate frontend:
```bash
cd apps/Client && npm run typecheck && npm run lint && npm run build
```

## Notes

- dnd-kit was chosen over react-beautiful-dnd (unmaintained) for React 19 compatibility
- Niche badges use dynamic colors based on niche name hash
- 8px drag activation constraint prevents accidental drags when clicking
- Search is debounced at 300ms for performance
- Pipeline view height is calculated as viewport minus header (calc(100vh - 250px))
