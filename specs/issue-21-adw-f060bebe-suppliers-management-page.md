# Feature: Suppliers Management Page

## Metadata
issue_number: `21`
adw_id: `f060bebe`
issue_json: `{"number":21,"title":"[Kompass] Phase 9A: Suppliers Management Page","body":"## Context\n**Current Phase:** Phase 9 of 13 - Frontend Core Pages\n**Current Issue:** KP-021 (Issue 21 of 33)\n**Parallel Execution:** YES - Runs IN PARALLEL with KP-022, KP-023, KP-024.\n\n---\n\n## Description\nCreate suppliers management page with list, create, and edit functionality.\n\n## Requirements\n\n### File: apps/Client/src/pages/kompass/SuppliersPage.tsx\n\n#### Features\n- Data table with columns: Name, Country, WeChat, Email, Status, Product Count, Actions\n- Search bar with instant filtering\n- Status filter dropdown\n- \"Add Supplier\" button opening dialog form\n- Edit action opening same dialog pre-filled\n- Delete with confirmation\n- Click row to see supplier detail with products\n\n### File: apps/Client/src/components/kompass/SupplierForm.tsx\n- Dialog form with fields: name, country, wechat_id, email, website, contact_person, phone, trade_fair_origin, notes\n- Validation with react-hook-form\n- Create and Edit modes\n\n## Acceptance Criteria\n- [ ] List rendering with all columns\n- [ ] Search working\n- [ ] Create form functional\n- [ ] Edit form functional\n- [ ] Delete with confirmation"}`

## Feature Description
Implement a fully functional Suppliers Management Page for the Kompass Portfolio & Quotation Automation System. This page will allow users to view, search, filter, create, edit, and delete suppliers from a centralized interface. The page includes a data table with instant search, status filtering, and a reusable dialog form component for create/edit operations. This is part of Phase 9 (Frontend Core Pages) and is critical for users to manage their supplier database which feeds into product management and quotations.

## User Story
As a Kompass user (admin, manager, or standard user)
I want to manage suppliers through a dedicated page with list, create, edit, and delete capabilities
So that I can maintain an organized supplier database for my import/export operations

## Problem Statement
Currently, the SuppliersPage is a placeholder "Coming Soon" page. Users need a fully functional interface to manage suppliers with:
- Viewing all suppliers in a paginated, searchable table
- Filtering suppliers by status
- Creating new suppliers via a form dialog
- Editing existing supplier information
- Deleting suppliers with confirmation
- Seeing supplier details including associated product count

## Solution Statement
Implement a complete Suppliers Management Page using Material-UI components and React patterns that:
1. Replaces the placeholder SuppliersPage.tsx with a full-featured management page
2. Creates a new SupplierForm.tsx dialog component for create/edit operations
3. Uses the existing supplierService from kompassService.ts for API operations
4. Follows established patterns from the codebase (react-hook-form, Material-UI, TypeScript types)
5. Includes proper error handling, loading states, and user feedback

## Relevant Files
Use these files to implement the feature:

### Core Files to Modify
- `apps/Client/src/pages/kompass/SuppliersPage.tsx` - Main page to replace (currently placeholder)
  - Will become the full suppliers management page with data table, search, filters, and actions

### New Files to Create
- `apps/Client/src/components/kompass/SupplierForm.tsx` - Dialog form component for create/edit modes
- `.claude/commands/e2e/test_suppliers_page.md` - E2E test file for validating suppliers management functionality

### Reference Files (Read-only)
- `apps/Client/src/types/kompass.ts` (lines 180-232) - Contains SupplierCreate, SupplierUpdate, SupplierResponse, SupplierListResponse, SupplierStatus types
- `apps/Client/src/services/kompassService.ts` (lines 128-175) - Contains supplierService with list, get, create, update, delete, search methods
- `apps/Client/src/pages/LoginPage.tsx` - Reference for react-hook-form patterns
- `apps/Client/src/components/layout/MainLayout.tsx` - Layout structure reference
- `apps/Client/src/api/clients/index.ts` - API client configuration
- `.claude/commands/test_e2e.md` - E2E test runner documentation for creating test files
- `app_docs/feature-af7568d5-frontend-types-api-service.md` - Frontend types and services documentation
- `app_docs/feature-98d1d93c-supplier-api-routes.md` - Backend API routes documentation

## Implementation Plan

### Phase 1: Foundation
1. Read and understand the existing Supplier types (SupplierCreate, SupplierUpdate, SupplierResponse, SupplierStatus)
2. Read and understand the supplierService API methods
3. Create the SupplierForm.tsx dialog component with:
   - react-hook-form integration
   - Material-UI Dialog, TextField, Select components
   - Validation rules for required fields
   - Support for both create and edit modes
   - Loading and error states

### Phase 2: Core Implementation
1. Replace SuppliersPage.tsx placeholder with full implementation:
   - Page header with title and "Add Supplier" button
   - Search input with debounced filtering
   - Status filter dropdown (all, active, inactive, pending_review)
   - Data table using Material-UI Table components
   - Pagination using TablePagination
   - Row actions (edit, delete)
   - Loading skeleton while fetching data
   - Empty state when no suppliers found
   - Error alert for API failures

2. Implement state management:
   - suppliers list state
   - pagination state (page, limit, total)
   - search query state with debounce
   - status filter state
   - loading state
   - error state
   - dialog open/close state
   - selected supplier for edit

### Phase 3: Integration
1. Connect to supplierService for all CRUD operations
2. Implement refresh after create/update/delete
3. Add confirmation dialog for delete action
4. Handle API errors gracefully with user feedback
5. Create E2E test file to validate functionality

## Step by Step Tasks

### Step 1: Create SupplierForm Dialog Component
- Create `apps/Client/src/components/kompass/SupplierForm.tsx`
- Import react-hook-form and Material-UI components
- Define Props interface with:
  - `open: boolean` - Dialog visibility
  - `onClose: () => void` - Close handler
  - `onSuccess: () => void` - Success callback
  - `supplier?: SupplierResponse | null` - Supplier for edit mode (null for create)
- Implement form with fields:
  - name (required, TextField)
  - code (optional, TextField)
  - status (Select with active, inactive, pending_review options)
  - contact_name (optional, TextField)
  - contact_email (optional, TextField with email validation)
  - contact_phone (optional, TextField)
  - country (required, default 'CN', TextField)
  - city (optional, TextField)
  - address (optional, TextField multiline)
  - website (optional, TextField with URL validation)
  - notes (optional, TextField multiline)
- Add form validation using react-hook-form register with validation rules
- Handle submit with supplierService.create() or supplierService.update()
- Show loading spinner during submission
- Show error Alert on failure
- Call onSuccess() and onClose() on successful submission
- Pre-fill form fields when supplier prop is provided (edit mode)
- Dialog title: "Add Supplier" for create, "Edit Supplier" for edit

### Step 2: Create E2E Test File
- Create `.claude/commands/e2e/test_suppliers_page.md`
- Define test user story for suppliers management
- Write test steps covering:
  1. Navigate to /suppliers page
  2. Verify page title and table structure visible
  3. Click "Add Supplier" button
  4. Fill in supplier form fields
  5. Submit form and verify new supplier appears in table
  6. Click edit on newly created supplier
  7. Modify supplier name
  8. Submit and verify changes reflected
  9. Click delete on supplier
  10. Confirm deletion in dialog
  11. Verify supplier removed from table
  12. Test search filtering
  13. Test status filter dropdown
- Define success criteria for each step
- Specify screenshot capture points

### Step 3: Replace SuppliersPage Placeholder with Full Implementation
- Replace content of `apps/Client/src/pages/kompass/SuppliersPage.tsx`
- Import required dependencies:
  - React hooks (useState, useEffect, useCallback)
  - Material-UI components (Box, Typography, Button, TextField, Select, MenuItem, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, TablePagination, Paper, IconButton, Chip, Alert, CircularProgress, Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions)
  - Material-UI icons (Add, Edit, Delete, Search)
  - Types from '@/types/kompass' (SupplierResponse, SupplierStatus)
  - Service from '@/services/kompassService' (supplierService)
  - SupplierForm component

### Step 4: Implement State Management
- Define state variables:
  - `suppliers: SupplierResponse[]` - List of suppliers
  - `loading: boolean` - Loading indicator
  - `error: string | null` - Error message
  - `page: number` - Current page (0-indexed for MUI)
  - `limit: number` - Items per page (default 10)
  - `total: number` - Total count for pagination
  - `searchQuery: string` - Search input value
  - `statusFilter: SupplierStatus | 'all'` - Status filter value
  - `formOpen: boolean` - Form dialog open state
  - `selectedSupplier: SupplierResponse | null` - Supplier for edit
  - `deleteDialogOpen: boolean` - Delete confirmation open
  - `supplierToDelete: SupplierResponse | null` - Supplier pending deletion

### Step 5: Implement Data Fetching
- Create `fetchSuppliers` async function using useCallback
- Call supplierService.list() with page, limit, and filters
- Handle search filter parameter
- Handle status filter parameter (omit if 'all')
- Update suppliers, total state on success
- Set error state on failure
- Set loading state during fetch
- Add useEffect to call fetchSuppliers on mount and when filters change
- Implement debounced search with 300ms delay

### Step 6: Implement Table Rendering
- Create TableContainer with Paper wrapper
- Add TableHead with columns:
  - Name
  - Country
  - Contact Email
  - Contact Phone
  - Status
  - Actions
- Map suppliers to TableRow components
- Display status using Chip with color variants:
  - active: success (green)
  - inactive: default (gray)
  - pending_review: warning (orange)
- Add IconButton for edit and delete actions
- Add TablePagination component with page/limit controls
- Show loading skeleton during fetch
- Show empty state message when no suppliers

### Step 7: Implement Create/Edit Functionality
- Add "Add Supplier" button in page header
- On click: setFormOpen(true), setSelectedSupplier(null)
- On edit action: setFormOpen(true), setSelectedSupplier(supplier)
- Pass formOpen, selectedSupplier to SupplierForm
- On SupplierForm success: fetchSuppliers() to refresh list

### Step 8: Implement Delete Functionality
- On delete action: setSupplierToDelete(supplier), setDeleteDialogOpen(true)
- Create delete confirmation Dialog
- Show supplier name in confirmation message
- On confirm: call supplierService.delete(id)
- On success: close dialog, fetchSuppliers()
- On error: show error Alert
- Loading state during delete operation

### Step 9: Implement Search and Filter
- Add search TextField with InputAdornment (Search icon)
- On change: setSearchQuery(value), debounced fetch
- Add status Select with options:
  - All Statuses (value: 'all')
  - Active (value: 'active')
  - Inactive (value: 'inactive')
  - Pending Review (value: 'pending_review')
- On change: setStatusFilter(value), fetch immediately
- Reset page to 0 when filters change

### Step 10: Run Validation Commands
- Run TypeScript check to verify no type errors
- Run lint to verify code quality
- Run build to verify successful compilation
- Run backend pytest to verify API integration still works
- Read and execute E2E test file to validate functionality

## Testing Strategy

### Unit Tests
- SupplierForm validates required fields (name, country)
- SupplierForm validates email format
- SupplierForm validates website URL format
- SupplierForm pre-fills data in edit mode
- SuppliersPage fetches suppliers on mount
- SuppliersPage applies search filter
- SuppliersPage applies status filter
- Delete confirmation prevents accidental deletion

### Edge Cases
- Empty supplier list shows appropriate message
- API error during fetch shows error alert
- API error during create shows error in dialog
- API error during delete shows error alert
- Very long supplier names truncate properly
- Pagination works correctly at boundaries
- Search with special characters handled
- Rapid filter changes don't cause race conditions

## Acceptance Criteria
- [ ] Page displays data table with columns: Name, Country, Contact Email, Contact Phone, Status, Actions
- [ ] Search bar filters suppliers in real-time with debounce
- [ ] Status filter dropdown filters by active/inactive/pending_review
- [ ] "Add Supplier" button opens dialog form
- [ ] Dialog form validates required fields (name, country)
- [ ] Create form submits and new supplier appears in table
- [ ] Edit action opens dialog with pre-filled data
- [ ] Edit form submits and changes reflect in table
- [ ] Delete action shows confirmation dialog
- [ ] Delete confirmation removes supplier from table
- [ ] Loading states shown during async operations
- [ ] Error messages shown for API failures
- [ ] Pagination controls work correctly
- [ ] TypeScript compiles with no errors
- [ ] ESLint passes with no errors
- [ ] Build completes successfully

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd /mnt/c/Users/user/danke_apps/Kompass/trees/f060bebe/apps/Client && npm run typecheck` - Run Client type check to verify no TypeScript errors
- `cd /mnt/c/Users/user/danke_apps/Kompass/trees/f060bebe/apps/Client && npm run lint` - Run Client lint to verify code quality
- `cd /mnt/c/Users/user/danke_apps/Kompass/trees/f060bebe/apps/Client && npm run build` - Run Client build to verify successful compilation
- `cd /mnt/c/Users/user/danke_apps/Kompass/trees/f060bebe/apps/Server && source .venv/bin/activate && .venv/bin/pytest tests/ -v --tb=short` - Run Server tests to verify API works with zero regressions
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_suppliers_page.md` E2E test to validate suppliers management functionality works end-to-end

## Notes
- The supplierService is already fully implemented with all required CRUD methods
- Types (SupplierCreate, SupplierUpdate, SupplierResponse, SupplierStatus) are already defined
- Route /suppliers is already configured in App.tsx
- Sidebar navigation already includes Suppliers menu item
- Follow existing logging convention: `console.log(\`INFO [ComponentName]: message\`)`
- Use @/ path alias for imports (e.g., '@/types/kompass', '@/services/kompassService')
- No `any` types allowed - use proper TypeScript typing
- Soft limit of 1000 lines per file - if SuppliersPage grows large, consider extracting helper functions
- The issue mentions WeChat and trade_fair_origin fields but these are not in the backend DTO - use the actual fields from SupplierCreate/SupplierResponse types which include contact_name, contact_email, contact_phone instead
- Status column uses SupplierStatus type: 'active' | 'inactive' | 'pending_review'
