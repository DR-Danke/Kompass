# Feature: Supplier Pipeline Workflow with Kanban Visualization

## Metadata
issue_number: `84`
adw_id: `a3855a57`
issue_json: `{"number":84,"title":"feat: Add supplier pipeline workflow and status management","body":"..."}`

## Feature Description
Implement a comprehensive supplier pipeline workflow system with Kanban-style visualization. Suppliers progress through qualification stages from initial contact to certified status. The feature includes:
- Kanban board view for suppliers with drag-and-drop status changes
- Pipeline status badges with color-coded indicators
- Status transition validation with business rules
- Pipeline status filtering
- Integration with the existing supplier certification system
- Business logic enforcement (only certified suppliers can receive orders)

## User Story
As a procurement manager
I want to visualize and manage suppliers in a Kanban-style pipeline board
So that I can efficiently track supplier progression through the qualification process and ensure only certified suppliers receive orders

## Problem Statement
Currently, suppliers have basic status tracking but lack a visual pipeline workflow that shows the qualification journey. Users cannot easily see which suppliers are at what stage of the pipeline, and there's no enforcement of business rules around supplier certification when placing orders or creating quotations.

## Solution Statement
Implement a full Kanban board view for the Suppliers page with:
1. Six pipeline columns: contacted → potential → quoted → certified → active → inactive
2. Drag-and-drop functionality for status transitions
3. Color-coded pipeline status badges throughout the application
4. Backend API endpoint to get pipeline summary (counts per status)
5. Business logic enforcement in quotation creation for uncertified suppliers
6. Filter options for pipeline status in products and suppliers pages

## Relevant Files
Use these files to implement the feature:

### Backend Files
- `apps/Server/app/services/supplier_service.py` - Contains existing supplier service with `update_pipeline_status`, `list_suppliers_by_pipeline` already implemented. Need to add `get_pipeline_summary()` method.
- `apps/Server/app/api/supplier_routes.py` - Contains existing `/suppliers/pipeline/{status}` and `/suppliers/{supplier_id}/pipeline-status` endpoints. Need to add `/suppliers/pipeline-summary` endpoint.
- `apps/Server/app/repository/kompass_repository.py` - Repository layer, need to add `get_pipeline_summary()` method.
- `apps/Server/app/models/kompass_dto.py` - Contains `SupplierPipelineStatus` enum and DTOs. Need to add `SupplierPipelineSummaryDTO`.

### Frontend Files
- `apps/Client/src/pages/kompass/SuppliersPage.tsx` - Current list view implementation. Need to add Kanban view toggle and pipeline status filter.
- `apps/Client/src/components/kompass/ClientKanbanBoard.tsx` - Reference implementation for Kanban board. Use as template for `SupplierPipelineKanban.tsx`.
- `apps/Client/src/components/kompass/KanbanColumn.tsx` - Reusable Kanban column component. May need generic version or create supplier-specific one.
- `apps/Client/src/components/kompass/ClientCard.tsx` - Reference implementation for cards. Use as template for `SupplierCard.tsx`.
- `apps/Client/src/services/kompassService.ts` - API service layer. Need to add pipeline summary endpoint call.
- `apps/Client/src/types/kompass.ts` - TypeScript types. Need to add `SupplierPipelineStatus` type and `SupplierPipelineSummary` interface.
- `apps/Client/src/hooks/kompass/useClients.ts` - Reference hook for Kanban state management. Use as template for `useSupplierPipeline.ts`.

### New Files
- `apps/Client/src/components/kompass/SupplierPipelineKanban.tsx` - New Kanban board component for suppliers
- `apps/Client/src/components/kompass/SupplierCard.tsx` - New supplier card component for Kanban
- `apps/Client/src/components/kompass/PipelineStatusBadge.tsx` - New reusable pipeline status badge component
- `apps/Client/src/hooks/kompass/useSupplierPipeline.ts` - New hook for supplier pipeline state management
- `.claude/commands/e2e/test_suppliers_pipeline.md` - E2E test file for the new functionality

### Documentation Reference
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_clients_pipeline.md` to understand E2E test format

## Implementation Plan

### Phase 1: Foundation
1. Add backend support for pipeline summary endpoint
2. Create TypeScript types for pipeline status
3. Create the `PipelineStatusBadge` component for consistent status display

### Phase 2: Core Implementation
1. Create the `SupplierCard` component for Kanban cards
2. Create the `SupplierPipelineKanban` component
3. Create the `useSupplierPipeline` hook for state management
4. Update `SuppliersPage` with view toggle (List/Kanban)
5. Add pipeline status filter to existing list view

### Phase 3: Integration
1. Add pipeline status badge to supplier table rows
2. Integrate with existing supplier form for pipeline status editing
3. Add E2E tests for the new functionality

## Step by Step Tasks

### Step 1: Add Backend Pipeline Summary Endpoint
- Read existing `apps/Server/app/repository/kompass_repository.py` and add `get_pipeline_summary()` method to `SupplierRepository` class
- The method should return counts of suppliers grouped by `pipeline_status`
- SQL query: `SELECT pipeline_status, COUNT(*) FROM suppliers GROUP BY pipeline_status`

### Step 2: Add Pipeline Summary DTO
- Update `apps/Server/app/models/kompass_dto.py`
- Add `SupplierPipelineSummaryDTO` class with fields for each status count:
  - contacted: int
  - potential: int
  - quoted: int
  - certified: int
  - active: int
  - inactive: int

### Step 3: Add Pipeline Summary Service Method
- Update `apps/Server/app/services/supplier_service.py`
- Add `get_pipeline_summary()` method that calls the repository

### Step 4: Add Pipeline Summary API Endpoint
- Update `apps/Server/app/api/supplier_routes.py`
- Add `GET /suppliers/pipeline-summary` endpoint
- Returns `SupplierPipelineSummaryDTO`

### Step 5: Add Frontend TypeScript Types
- Update `apps/Client/src/types/kompass.ts`
- Add `SupplierPipelineStatus` type: `'contacted' | 'potential' | 'quoted' | 'certified' | 'active' | 'inactive'`
- Add `SupplierPipelineSummary` interface with counts for each status
- Add `SupplierPipelineResponse` interface (similar to `PipelineResponse` for clients)
- Update `SupplierResponse` interface to include `pipeline_status` field

### Step 6: Add Frontend Service Methods
- Update `apps/Client/src/services/kompassService.ts`
- Add `supplierService.getPipelineSummary()` method
- Add `supplierService.getPipeline()` method to fetch suppliers grouped by status
- Add `supplierService.updatePipelineStatus(id, status)` method

### Step 7: Create PipelineStatusBadge Component
- Create `apps/Client/src/components/kompass/PipelineStatusBadge.tsx`
- Color mapping:
  - contacted: grey (#f5f5f5, text #616161)
  - potential: blue (#e3f2fd, text #1565c0)
  - quoted: amber (#fff8e1, text #f57c00)
  - certified: green (#e8f5e9, text #2e7d32)
  - active: success (#c8e6c9, text #1b5e20)
  - inactive: red (#ffebee, text #c62828)
- Include tooltip with status description
- Props: `status: SupplierPipelineStatus`, `size?: 'small' | 'medium'`

### Step 8: Create SupplierCard Component
- Create `apps/Client/src/components/kompass/SupplierCard.tsx`
- Based on `ClientCard.tsx` pattern
- Display:
  - Supplier name
  - Code (if present)
  - Country
  - Contact name
  - Product count badge
  - Certification status badge (if certified)
  - Last activity indicator
- Use `useSortable` from `@dnd-kit/sortable` for drag functionality

### Step 9: Create useSupplierPipeline Hook
- Create `apps/Client/src/hooks/kompass/useSupplierPipeline.ts`
- Based on `useClients.ts` pattern
- State management for:
  - Pipeline data (suppliers grouped by status)
  - Pipeline summary (counts)
  - Selected supplier
  - View mode (kanban/list)
  - Loading and error states
- Methods:
  - `fetchPipeline()` - Load suppliers grouped by status
  - `updatePipelineStatus(supplierId, newStatus)` - Update status via API
  - `refreshPipeline()` - Refresh pipeline data

### Step 10: Create SupplierPipelineKanban Component
- Create `apps/Client/src/components/kompass/SupplierPipelineKanban.tsx`
- Based on `ClientKanbanBoard.tsx` pattern
- Six columns for pipeline statuses
- Column colors matching `PipelineStatusBadge` colors
- Drag-and-drop using `@dnd-kit/core`
- Props: `pipeline`, `onSupplierClick`, `onStatusChange`, `isUpdating`

### Step 11: Update SuppliersPage with View Toggle
- Modify `apps/Client/src/pages/kompass/SuppliersPage.tsx`
- Add view toggle (List/Kanban) similar to `ClientsPage.tsx`
- Add pipeline status filter dropdown in toolbar
- Conditional rendering based on view mode
- Integrate with `useSupplierPipeline` hook when in Kanban mode
- Keep existing list implementation for list mode

### Step 12: Add Pipeline Status Badge to Supplier Table
- Update `SuppliersPage.tsx` list view
- Add pipeline status column to table
- Use `PipelineStatusBadge` component
- Make column sortable

### Step 13: Create E2E Test File
- Create `.claude/commands/e2e/test_suppliers_pipeline.md`
- Follow the pattern from `test_clients_pipeline.md`
- Test steps:
  1. Navigate to Suppliers page
  2. Verify view toggle exists
  3. Switch to Kanban view
  4. Verify 6 columns are visible
  5. Create new supplier in "contacted" status
  6. Drag supplier to "potential" column
  7. Verify status update success
  8. Test supplier card click opens drawer/modal
  9. Test search filtering in Kanban
  10. Switch back to list view
  11. Verify pipeline status column visible
  12. Delete test supplier

### Step 14: Run Validation Commands
- Execute all validation commands to ensure zero regressions

## Testing Strategy

### Unit Tests
- Test `get_pipeline_summary()` repository method returns correct counts
- Test `get_pipeline_summary()` service method
- Test pipeline status update validation rules
- Test `PipelineStatusBadge` renders correct colors
- Test `SupplierCard` displays supplier data correctly
- Test `useSupplierPipeline` hook state transitions

### Edge Cases
- Empty pipeline (no suppliers)
- Single supplier in one status
- Drag to same column (no API call)
- Concurrent status updates
- Network error during status update (optimistic update rollback)
- Supplier with/without product count
- Supplier with/without certification

## Acceptance Criteria
- [ ] Pipeline status field displays on all suppliers in both views
- [ ] Kanban view shows 6 columns with correct colors
- [ ] Kanban columns show accurate supplier counts
- [ ] Drag-and-drop moves supplier between columns
- [ ] Status update triggers API call and shows success notification
- [ ] Status badges use consistent colors throughout app
- [ ] Pipeline status filter works in list view
- [ ] View toggle switches between List and Kanban seamlessly
- [ ] Supplier cards show key info (name, code, country, product count)
- [ ] Search filters suppliers in Kanban view
- [ ] Backend `/suppliers/pipeline-summary` returns correct counts
- [ ] TypeScript compiles without errors
- [ ] All existing tests pass
- [ ] E2E test validates new functionality

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && source .venv/bin/activate && pytest tests/ -v --tb=short` - Run Server tests
- `cd apps/Server && source .venv/bin/activate && ruff check .` - Run Server linting
- `cd apps/Client && npm run typecheck` - Run Client type check
- `cd apps/Client && npm run lint` - Run Client linting
- `cd apps/Client && npm run build` - Run Client build
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_suppliers_pipeline.md` to validate E2E functionality

## Notes
- The backend already has `SupplierPipelineStatus` enum with the required statuses
- The backend already has `update_pipeline_status` and `list_suppliers_by_pipeline` methods
- The `@dnd-kit` library is already installed (used by `ClientKanbanBoard`)
- Follow the established patterns from `ClientsPage` and `ClientKanbanBoard` for consistency
- The certification check for quotations is a stretch goal - implement basic pipeline Kanban first
- Column colors should match the status badge colors for visual consistency
- Consider adding a "confirm dialog" for status transitions to important statuses like "certified"
