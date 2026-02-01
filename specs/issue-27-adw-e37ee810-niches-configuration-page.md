# Feature: Niches Configuration Page

## Metadata
issue_number: `27`
adw_id: `e37ee810`
issue_json: `{"number":27,"title":"[Kompass] Phase 10C: Niches Configuration Page","body":"## Context\n**Current Phase:** Phase 10 of 13 - Frontend Portfolio & Clients\n**Current Issue:** KP-027 (Issue 27 of 33)\n**Parallel Execution:** YES - Runs IN PARALLEL with KP-025 and KP-026.\n\n---\n\n## Description\nCreate niches configuration page for client type management.\n\n## Requirements\n\n### File: apps/Client/src/pages/kompass/NichesPage.tsx\n\n#### Features\n- Simple list/cards of niches\n- Each shows: name, description, client count\n- Add niche button\n- Edit/delete actions\n- Delete blocked if has clients\n\n### File: apps/Client/src/components/kompass/NicheForm.tsx\n- Dialog form with: name, description\n\n## Acceptance Criteria\n- [ ] List rendering\n- [ ] Create/edit working\n- [ ] Delete validation\n\nInclude workflow: adw_plan_build_iso\n\n---\n\n## Full Implementation Reference\nFor complete implementation details, dependency graph, and execution commands, see:\n**`ai_docs/KOMPASS_ADW_IMPLEMENTATION_PROMPTS.md`**\n\nThis document contains all 33 issues, parallel execution instructions, and the complete bash script for automated deployment."}`

## Feature Description
This feature implements a Niches Configuration Page for the Kompass Portfolio & Quotation system. Niches are client type classifications (e.g., Constructoras, Hoteles, Retailers) that help categorize clients for targeted portfolio management. The page will provide a user interface to list, create, edit, and delete niches while enforcing business rules (e.g., cannot delete niches that have associated clients).

## User Story
As a Kompass admin or manager
I want to manage niches (client type classifications) through a dedicated configuration page
So that I can categorize clients by business type for targeted portfolio management and better organization

## Problem Statement
Currently, niche management is only available through the backend API. There is no user-friendly interface for administrators to:
- View existing niches with their client counts
- Create new niches to categorize clients
- Edit niche names and descriptions
- Delete unused niches (with protection for niches that have clients)

## Solution Statement
Create a NichesPage component that displays niches in a card/list format, showing each niche's name, description, and client count. Implement a NicheForm dialog component for creating and editing niches. The delete functionality will show a confirmation dialog and handle the 409 Conflict response when attempting to delete niches with associated clients by displaying an appropriate error message.

## Relevant Files
Use these files to implement the feature:

- `apps/Client/src/types/kompass.ts`: Contains TypeScript types for niches (NicheCreate, NicheUpdate, NicheResponse, NicheListResponse, NicheWithClientCount). These types must be used for type-safe API calls.
- `apps/Client/src/services/kompassService.ts`: Contains the nicheService with list, get, create, update, and delete methods. The service layer is already implemented.
- `apps/Client/src/pages/kompass/SuppliersPage.tsx`: Reference implementation for page structure, state management, fetching, filtering, CRUD operations, and dialog patterns.
- `apps/Client/src/components/kompass/SupplierForm.tsx`: Reference implementation for form dialogs using react-hook-form with Material-UI.
- `apps/Client/src/App.tsx`: Route configuration where the new NichesPage route needs to be added.
- `apps/Client/src/components/layout/Sidebar.tsx`: Navigation configuration where the Niches menu item needs to be added.
- `app_docs/feature-15dd75a7-niche-service-crud.md`: Backend documentation for the niche API endpoints and their behavior.
- `.claude/commands/test_e2e.md`: E2E test runner instructions.
- `.claude/commands/e2e/test_suppliers_page.md`: Reference E2E test file for understanding the test format.

### New Files
- `apps/Client/src/pages/kompass/NichesPage.tsx`: Main page component for niches management
- `apps/Client/src/components/kompass/NicheForm.tsx`: Dialog form component for create/edit niche
- `.claude/commands/e2e/test_niches_page.md`: E2E test specification for the niches page

## Implementation Plan
### Phase 1: Foundation
- Review existing types in `kompass.ts` for niche-related interfaces (NicheCreate, NicheUpdate, NicheResponse, NicheWithClientCount)
- Verify nicheService methods in kompassService.ts are implemented correctly
- Add route configuration in App.tsx for `/niches` path
- Add navigation item in Sidebar.tsx for Niches page

### Phase 2: Core Implementation
- Create NicheForm.tsx component with dialog form for name and description fields
- Create NichesPage.tsx with:
  - Card/list view of niches showing name, description, and client count
  - Add Niche button
  - Edit/Delete action buttons per niche
  - Loading and error states
  - Delete confirmation dialog with special handling for 409 Conflict errors

### Phase 3: Integration
- Connect NichesPage to nicheService for API operations
- Implement proper error handling (especially for 409 when deleting niches with clients)
- Test all CRUD operations end-to-end
- Create E2E test specification

## Step by Step Tasks

### Task 1: Add Route and Navigation
- Open `apps/Client/src/App.tsx` and add import for NichesPage
- Add route `<Route path="niches" element={<NichesPage />} />` in the protected routes section
- Open `apps/Client/src/components/layout/Sidebar.tsx`
- Add navigation item for Niches (use `LocalOfferIcon` or `LabelIcon` from Material-UI icons) after Settings or before Settings

### Task 2: Create E2E Test Specification
- Read `.claude/commands/test_e2e.md` to understand the E2E test format
- Read `.claude/commands/e2e/test_suppliers_page.md` as a reference
- Create `.claude/commands/e2e/test_niches_page.md` with test steps for:
  - Navigate to Niches page
  - Verify page structure (title, add button, cards/list)
  - Create new niche
  - Edit existing niche
  - Delete niche (success case)
  - Delete blocked validation (attempt to delete niche with clients)

### Task 3: Create NicheForm Component
- Create `apps/Client/src/components/kompass/NicheForm.tsx`
- Implement as a Dialog component similar to SupplierForm.tsx
- Use react-hook-form for form handling
- Form fields:
  - Name (required, text field)
  - Description (optional, multiline text area)
- Props: open, onClose, onSuccess, niche (optional for edit mode)
- Handle create and update via nicheService

### Task 4: Create NichesPage Component
- Create `apps/Client/src/pages/kompass/NichesPage.tsx`
- State management:
  - niches array (NicheWithClientCount[])
  - loading, error states
  - formOpen, selectedNiche for form dialog
  - deleteDialogOpen, nicheToDelete for delete confirmation
- Fetch niches using nicheService.list()
- Display as cards (using Card, CardContent, CardActions from Material-UI)
- Each card shows: name, description, client count badge
- Add Niche button opens NicheForm
- Edit button opens NicheForm with selected niche
- Delete button shows confirmation dialog
- Handle 409 error on delete by showing message "Cannot delete niche with associated clients"

### Task 5: Implement Delete Validation
- In the delete confirmation dialog, show the niche name
- On confirm, call nicheService.delete()
- Catch 409 Conflict error (axios error with response.status === 409)
- Display user-friendly error: "This niche cannot be deleted because it has associated clients. Please reassign the clients first."
- Close dialog and refresh list on successful delete

### Task 6: Run Validation Commands
- Run `cd apps/Client && npm run typecheck` to verify TypeScript compilation
- Run `cd apps/Client && npm run lint` to check for linting issues
- Run `cd apps/Client && npm run build` to verify production build
- Run `cd apps/Server && source .venv/bin/activate && python -m pytest tests/ -v --tb=short` to ensure backend tests pass
- Execute E2E test: Read `.claude/commands/test_e2e.md`, then execute `.claude/commands/e2e/test_niches_page.md`

## Testing Strategy
### Unit Tests
- NicheForm renders with empty fields for create mode
- NicheForm pre-fills fields in edit mode
- Form validation prevents submission without required name field
- Page displays loading state while fetching
- Page displays error state on fetch failure

### Edge Cases
- Empty niches list (display "No niches found" message)
- Delete blocked when niche has clients (409 Conflict handling)
- Very long niche names (truncation or wrapping)
- Multiple rapid delete attempts (prevent double-click issues)
- Network error during CRUD operations

## Acceptance Criteria
- [ ] Niches page is accessible via `/niches` route
- [ ] Navigation sidebar includes Niches link with appropriate icon
- [ ] Page displays list/cards of niches with name, description, and client count
- [ ] "Add Niche" button opens form dialog
- [ ] Create form validates required name field
- [ ] Create operation adds new niche to the list
- [ ] Edit button opens form dialog pre-filled with niche data
- [ ] Update operation reflects changes in the list
- [ ] Delete button shows confirmation dialog
- [ ] Delete operation removes niche from list (when allowed)
- [ ] Delete blocked message shown when attempting to delete niche with clients
- [ ] No TypeScript errors
- [ ] No ESLint warnings
- [ ] Production build succeeds
- [ ] E2E tests pass

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Client && npm run typecheck` - Run Client type check to validate TypeScript compilation
- `cd apps/Client && npm run lint` - Run ESLint to check for code quality issues
- `cd apps/Client && npm run build` - Run Client build to validate production build
- `cd apps/Server && source .venv/bin/activate && python -m pytest tests/ -v --tb=short` - Run Server tests to validate backend remains stable
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_niches_page.md` to validate the niches page functionality

## Notes
- The nicheService is already implemented in kompassService.ts with list, get, create, update, delete methods
- The backend returns NicheWithClientCount which includes client_count field for each niche
- The backend returns 409 Conflict when attempting to delete a niche that has associated clients
- Use Material-UI Card components for visual consistency with other Kompass pages
- Follow existing patterns from SuppliersPage.tsx and SupplierForm.tsx
- The niche form is simpler than supplier form (only name and description fields)
- Default niches (seeded): Constructoras, Estudios de Arquitectura, Desarrolladores, Hoteles, Operadores Rentas Cortas, Retailers
