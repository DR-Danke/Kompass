# Feature: Quotation Creator Page

## Metadata
issue_number: `28`
adw_id: `e60c5767`
issue_json: `{"number":28,"title":"[Kompass] Phase 11A: Quotation Creator Page","body":"## Context\n**Current Phase:** Phase 11 of 13 - Frontend Quotation\n**Current Issue:** KP-028 (Issue 28 of 33)\n**Parallel Execution:** YES - Runs IN PARALLEL with KP-029.\n\n---\n\n## Description\nCreate comprehensive quotation creator with live pricing calculation.\n\n## Requirements\n\n### File: apps/Client/src/pages/kompass/QuotationCreatorPage.tsx\n\n#### Steps/Sections\n1. **Client Selection:** Search existing or create new, show project timing validation\n2. **Product Selection:** Browse Biblia General or select from Portfolio, add to quote\n3. **Line Items:** Table with product, quantity (editable), unit price, line total\n4. **Pricing Panel:** Live calculation showing all cost components\n5. **Summary:** Grand total in COP, payment terms, validity period, notes\n\n#### Line Items Table\n- Product image thumbnail, Product name/SKU, Quantity input, Unit FOB price (editable override), HS code, Line total, Remove button\n\n#### Pricing Panel (right sidebar)\n- Subtotal FOB USD, Tariffs breakdown, International freight, National freight, Inspection, Insurance, Nationalization, Margin %, **Total COP** (highlighted)\n\n#### Actions\n- Save Draft, Calculate, Preview PDF, Send via Email, Copy share link\n\n### File: apps/Client/src/pages/kompass/QuotationsListPage.tsx\n- Data table of quotations\n- Columns: Quote #, Client, Total COP, Status, Created, Valid Until, Actions\n- Status badges color-coded\n- Filter by status, client, date range\n\n## Acceptance Criteria\n- [ ] Client selection working\n- [ ] Product selection working\n- [ ] Live pricing calculation\n- [ ] PDF preview generating\n- [ ] Email sending functional"}`

## Feature Description
Create a comprehensive Quotation Creator page that allows users to build quotations with multi-step workflow including client selection with project timing validation, product selection from Biblia General or existing portfolios, editable line items table with live pricing calculation, and a pricing panel showing full cost breakdown in COP. Additionally, implement a Quotations List page to display, filter, and manage all quotations with status-based color coding.

## User Story
As a Kompass user (admin, manager, or sales representative)
I want to create professional quotations by selecting clients, adding products from the catalog, and see live pricing calculations
So that I can quickly generate accurate quotations for clients with full cost visibility including tariffs, freight, and margins

## Problem Statement
The current QuotationsPage is a placeholder with no functionality. Users need a comprehensive quotation creation workflow that:
1. Allows selecting existing clients or creating new ones with project timing validation
2. Enables adding products from the Biblia General catalog or from portfolios
3. Shows a full line items table with editable quantities and price overrides
4. Calculates live pricing with all cost components (FOB, tariffs, freight, insurance, nationalization, margin)
5. Provides actions to save drafts, preview PDFs, send emails, and share links
6. Displays all quotations in a filterable list view

## Solution Statement
Build two interconnected pages:
1. **QuotationCreatorPage** - A multi-section quotation builder with:
   - Client selection autocomplete with search and new client creation
   - Product selection with dual modes (catalog browse vs portfolio selection)
   - Line items table with inline editing for quantity and price overrides
   - Live pricing panel (right sidebar) with real-time cost breakdown
   - Action buttons for Save Draft, Calculate, Preview PDF, Send Email, Copy Share Link

2. **QuotationsListPage** - Replace the current placeholder with:
   - Data table showing all quotations with pagination
   - Status badges with color coding per status
   - Filtering by status, client, and date range
   - Quick actions (view, edit, delete, clone)

## Relevant Files
Use these files to implement the feature:

### Existing Files to Modify
- `apps/Client/src/pages/kompass/QuotationsPage.tsx` - Currently a placeholder, will be replaced with the list view
- `apps/Client/src/App.tsx` - Add new routes for quotation creator and list pages
- `apps/Client/src/services/kompassService.ts` - quotationService already exists with full CRUD operations
- `apps/Client/src/types/kompass.ts` - Contains all quotation-related TypeScript types (QuotationResponse, QuotationItemResponse, QuotationPricing, etc.)
- `.claude/commands/test_e2e.md` - Reference for E2E test file structure

### Backend Files (Reference Only - Already Implemented)
- `apps/Server/app/services/quotation_service.py` - QuotationService with pricing engine
- `apps/Server/app/api/quotation_routes.py` - Full REST API including calculate, export PDF, send email, share
- `app_docs/feature-bccd1fc5-quotation-service-pricing-engine.md` - Quotation service documentation
- `app_docs/feature-0884e820-quotation-api-routes.md` - API routes documentation

### Reference Files (Patterns to Follow)
- `apps/Client/src/pages/kompass/ClientsPage.tsx` - Pattern for complex page with search, filters, view modes
- `apps/Client/src/pages/kompass/ProductsPage.tsx` - Pattern for catalog browsing with filters
- `apps/Client/src/pages/kompass/PortfoliosPage.tsx` - Pattern for card-based list with actions
- `apps/Client/src/hooks/kompass/useClients.ts` - Pattern for custom hooks with state management
- `apps/Client/src/hooks/kompass/useProducts.ts` - Pattern for products hook with filtering
- `.claude/commands/e2e/test_products_catalog.md` - E2E test file pattern

### New Files
- `apps/Client/src/pages/kompass/QuotationCreatorPage.tsx` - Main quotation creator page
- `apps/Client/src/pages/kompass/QuotationsListPage.tsx` - Quotations list/management page
- `apps/Client/src/hooks/kompass/useQuotations.ts` - Hook for quotations list management
- `apps/Client/src/hooks/kompass/useQuotationCreator.ts` - Hook for quotation creator state
- `apps/Client/src/components/kompass/QuotationLineItemsTable.tsx` - Line items table component
- `apps/Client/src/components/kompass/QuotationPricingPanel.tsx` - Pricing sidebar component
- `apps/Client/src/components/kompass/ClientSelector.tsx` - Client search/select component
- `apps/Client/src/components/kompass/ProductSelector.tsx` - Product browser/selector component
- `apps/Client/src/components/kompass/QuotationStatusBadge.tsx` - Status badge component
- `apps/Client/src/components/kompass/QuotationActions.tsx` - Action buttons component
- `.claude/commands/e2e/test_quotation_creator.md` - E2E test file for quotation creator

## Implementation Plan
### Phase 1: Foundation
1. Create the E2E test file specification for quotation creator functionality
2. Create useQuotations hook for quotations list management (filtering, pagination, CRUD)
3. Create useQuotationCreator hook for creator state management (client, items, pricing)
4. Create QuotationStatusBadge component for color-coded status display

### Phase 2: Quotations List Page
1. Build QuotationsListPage with data table, columns, pagination
2. Add filtering by status, client, and date range
3. Add action buttons (view, edit, clone, delete)
4. Replace current QuotationsPage placeholder

### Phase 3: Quotation Creator Components
1. Build ClientSelector component with search autocomplete and new client creation
2. Build ProductSelector component with catalog browse and portfolio selection modes
3. Build QuotationLineItemsTable component with inline editing
4. Build QuotationPricingPanel component with live cost breakdown
5. Build QuotationActions component (Save Draft, Calculate, Preview PDF, Send Email, Copy Link)

### Phase 4: Integration
1. Build QuotationCreatorPage integrating all components
2. Add routes for /quotations (list) and /quotations/new and /quotations/:id (edit)
3. Connect pricing panel to backend calculate endpoint for live updates
4. Implement PDF preview, email send, and share link functionality

## Step by Step Tasks

### Step 1: Create E2E Test Specification File
- Read `.claude/commands/test_e2e.md` to understand E2E test structure
- Read `.claude/commands/e2e/test_products_catalog.md` for reference pattern
- Create `.claude/commands/e2e/test_quotation_creator.md` with test steps for:
  - Navigate to quotations list page
  - Test filtering by status, client, date range
  - Create new quotation (select client, add products, adjust quantities)
  - Verify live pricing calculation updates
  - Save draft and verify persistence
  - Test PDF preview generation
  - Test share link functionality

### Step 2: Create QuotationStatusBadge Component
- Create `apps/Client/src/components/kompass/QuotationStatusBadge.tsx`
- Map status to colors: draft (grey), sent (blue), viewed (purple), negotiating (orange), accepted (green), rejected (red), expired (dark grey)
- Accept status prop and render MUI Chip with appropriate color

### Step 3: Create useQuotations Hook
- Create `apps/Client/src/hooks/kompass/useQuotations.ts`
- Implement state for quotations list, pagination, filters (status, client_id, date range, search)
- Add methods: fetchQuotations, deleteQuotation, cloneQuotation, getShareToken
- Follow pattern from useClients.ts

### Step 4: Create useQuotationCreator Hook
- Create `apps/Client/src/hooks/kompass/useQuotationCreator.ts`
- Implement state for: selectedClient, lineItems, pricingData, quotationSettings (incoterm, validity, notes)
- Add methods: setClient, addItem, updateItem, removeItem, calculatePricing, saveQuotation
- Track isDirty state for unsaved changes warning

### Step 5: Create ClientSelector Component
- Create `apps/Client/src/components/kompass/ClientSelector.tsx`
- Implement MUI Autocomplete with async search using clientService.search()
- Display client name, company, project timing warning if applicable
- Add "Create New Client" option that opens ClientForm dialog
- Show selected client details card

### Step 6: Create ProductSelector Component
- Create `apps/Client/src/components/kompass/ProductSelector.tsx`
- Implement dual-mode selection:
  - Tab 1: Browse Biblia General with search/filter (ProductFilters pattern)
  - Tab 2: Select from existing Portfolio dropdown
- Display product cards with Add to Quote button
- Track which products are already in quote (disable/show "Added" state)

### Step 7: Create QuotationLineItemsTable Component
- Create `apps/Client/src/components/kompass/QuotationLineItemsTable.tsx`
- Implement MUI DataGrid or Table with columns:
  - Image thumbnail (50x50px)
  - Product Name / SKU
  - Quantity (editable NumberField)
  - Unit FOB Price (editable with override indicator)
  - HS Code (display only)
  - Line Total (calculated)
  - Remove button (IconButton with DeleteIcon)
- Emit onChange events for quantity/price changes
- Handle empty state with "No items added" message

### Step 8: Create QuotationPricingPanel Component
- Create `apps/Client/src/components/kompass/QuotationPricingPanel.tsx`
- Display pricing breakdown sections:
  - Subtotal FOB USD
  - Tariffs breakdown (per HS code)
  - International freight
  - National freight
  - Inspection
  - Insurance
  - Nationalization
  - Margin % (editable field)
  - **Total COP** (highlighted, larger font)
- Accept pricing data from useQuotationCreator hook
- Show loading state while calculating

### Step 9: Create QuotationActions Component
- Create `apps/Client/src/components/kompass/QuotationActions.tsx`
- Implement action buttons:
  - Save Draft (primary, always visible)
  - Calculate (secondary, triggers pricing recalculation)
  - Preview PDF (opens PDF in new tab/modal)
  - Send via Email (opens email dialog)
  - Copy Share Link (copies to clipboard with snackbar)
- Handle loading states and error feedback

### Step 10: Build QuotationsListPage
- Create `apps/Client/src/pages/kompass/QuotationsListPage.tsx`
- Use useQuotations hook
- Implement header with title and "New Quotation" button
- Add filter bar with dropdowns: Status, Client, Date Range
- Add search input for quotation number/client name
- Implement MUI DataGrid/Table with columns:
  - Quote # (link to detail)
  - Client name
  - Total COP (formatted currency)
  - Status (QuotationStatusBadge)
  - Created date
  - Valid Until date
  - Actions (View, Edit, Clone, Delete)
- Add pagination
- Handle empty state

### Step 11: Build QuotationCreatorPage
- Create `apps/Client/src/pages/kompass/QuotationCreatorPage.tsx`
- Use useQuotationCreator hook
- Layout: Two-column (main content + right sidebar)
- Main content sections:
  1. Client Selection section (ClientSelector)
  2. Product Selection section (ProductSelector with tabs)
  3. Line Items section (QuotationLineItemsTable)
  4. Summary section (notes, terms, validity period fields)
- Right sidebar: QuotationPricingPanel (sticky)
- Top actions bar: QuotationActions
- Handle edit mode (load existing quotation by ID)

### Step 12: Update Routing and Navigation
- Update `apps/Client/src/App.tsx`:
  - Change `/quotations` route to QuotationsListPage
  - Add `/quotations/new` route to QuotationCreatorPage
  - Add `/quotations/:id` route to QuotationCreatorPage (edit mode)
- Update sidebar navigation if needed

### Step 13: Run Validation Commands
- Execute all validation commands to ensure zero regressions
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_quotation_creator.md`

## Testing Strategy
### Unit Tests
- useQuotations hook: test filtering, pagination, CRUD operations
- useQuotationCreator hook: test item management, pricing calculation triggers
- QuotationStatusBadge: test correct color mapping for each status
- QuotationLineItemsTable: test add/update/remove item operations
- QuotationPricingPanel: test correct display of pricing breakdown

### Edge Cases
- Empty quotation (no items) - should disable calculate/save
- Client without project deadline - no timing warning shown
- Products without images - show placeholder
- Zero quantity items - should be prevented or removed
- Price override below cost - show warning
- Quotation with expired validity - show expired badge
- Large number of line items (50+) - pagination or virtual scrolling
- Network error during calculate - show error, keep previous values
- Concurrent edit detection - warn if quotation was modified elsewhere

## Acceptance Criteria
- [x] Quotations list page displays all quotations with proper columns and formatting
- [x] Status badges show correct colors for each quotation status
- [x] Filtering works for status, client, and date range
- [x] "New Quotation" button navigates to creator page
- [x] Client selection shows search autocomplete with project timing info
- [x] New client can be created inline from client selector
- [x] Products can be added from Biblia General browse
- [x] Products can be added from existing portfolio selection
- [x] Line items table shows all required columns with inline editing
- [x] Quantity changes trigger live pricing recalculation
- [x] Price override is visually indicated and functions correctly
- [x] Pricing panel shows complete cost breakdown
- [x] Total COP is prominently displayed
- [x] Save Draft creates/updates quotation with draft status
- [x] Calculate button triggers backend pricing calculation
- [x] Preview PDF opens generated PDF document
- [x] Send via Email opens email dialog and sends successfully
- [x] Copy share link copies public URL to clipboard
- [x] Edit mode loads existing quotation data correctly
- [x] Form validation prevents submission of invalid data
- [x] Loading and error states are handled gracefully

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && .venv/bin/pytest tests/ -v --tb=short` - Run Server tests to validate the feature works with zero regressions
- `cd apps/Client && npm run typecheck` - Run Client type check to validate the feature works with zero regressions
- `cd apps/Client && npm run lint` - Run Client linting to catch code quality issues
- `cd apps/Client && npm run build` - Run Client build to validate the feature works with zero regressions
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_quotation_creator.md` E2E test file to validate this functionality works

## Notes
- The backend quotation service and API routes are already fully implemented (KP-017 and KP-019)
- PDF generation uses reportlab on the backend - frontend just calls the endpoint
- Email sending supports mock mode via EMAIL_MOCK_MODE environment variable
- Share tokens are JWT-based with 30-day expiration
- The pricing engine formula: Total COP = (FOB + Tariffs + Int'l Freight + Inspection + Insurance) × Exchange Rate + National Freight + Nationalization + Margin
- Status transitions follow a defined workflow: draft→sent→viewed→negotiating→accepted/rejected/expired
- Consider adding debounce on quantity/price inputs to avoid excessive API calls during typing
- The pricing panel should show "Calculating..." while waiting for backend response
