# Feature: Portfolio Builder Page with Interactive Product Selection

## Metadata
issue_number: `25`
adw_id: `2287ac8d`
issue_json: `{"number":25,"title":"[Kompass] Phase 10A: Portfolio Builder Page","body":"## Context\n**Current Phase:** Phase 10 of 13 - Frontend Portfolio & Clients\n**Current Issue:** KP-025 (Issue 25 of 33)\n**Parallel Execution:** YES - Runs IN PARALLEL with KP-026 and KP-027.\n\n---\n\n## Description\nCreate interactive portfolio builder with product selection.\n\n## Requirements\n\n### File: apps/Client/src/pages/kompass/PortfolioBuilderPage.tsx\n\n#### Layout (Two-column)\n- **Left Panel (40%):** Product catalog mini-view with search and filters\n- **Right Panel (60%):** Current portfolio with products, drag-to-reorder\n\n#### Top Bar\n- Portfolio name (editable), Niche selector dropdown, Status toggle (draft/published)\n- Save, Preview PDF, Copy share link buttons\n\n#### Product Selection\n- Click product in left panel to add to portfolio\n- Drag products within portfolio to reorder\n- Remove button on each portfolio item\n- Curator notes input per item\n\n### File: apps/Client/src/pages/kompass/PortfoliosListPage.tsx\n- Grid of portfolio cards\n- Card shows: name, niche, product count, status badge, cover image\n- Actions: Open, Duplicate, Delete, Copy share link\n\n## Acceptance Criteria\n- [ ] Portfolio builder functional\n- [ ] Product add/remove working\n- [ ] Reorder working\n- [ ] PDF preview generating\n- [ ] Share link working"}`

## Feature Description
Create an interactive portfolio builder interface that allows Kompass users to curate product collections for clients. The feature includes two main pages:

1. **PortfoliosListPage**: A grid-based overview of all portfolios with cards showing portfolio name, niche, product count, status badge, and cover image. Users can open, duplicate, delete portfolios, and copy share links directly from this view.

2. **PortfolioBuilderPage**: A two-column interactive builder where users can:
   - Browse products in a mini-catalog view (left panel, 40% width) with search and filters
   - Build and manage the portfolio (right panel, 60% width) with drag-to-reorder capability
   - Edit portfolio metadata (name, niche, status) in a top bar
   - Add curator notes per product item
   - Preview PDF exports and copy share links

## User Story
As a Kompass sales representative
I want to build curated product collections for my clients using a visual drag-and-drop interface
So that I can efficiently create personalized portfolios and share them with clients

## Problem Statement
Currently, the PortfoliosPage is a placeholder with no functionality. Sales teams need an intuitive interface to:
- Create and manage curated product portfolios
- Select products from the catalog and arrange them in a meaningful order
- Add personalized notes for each product in the context of the client
- Generate shareable links and PDF previews for client presentations

## Solution Statement
Build a comprehensive portfolio management system with:
1. A list page showing all portfolios in a card grid with quick actions
2. A builder page with split-panel design for browsing products and building portfolios
3. Drag-and-drop reordering using @dnd-kit library (following React 19 compatibility)
4. Integration with existing portfolio backend APIs for CRUD, share tokens, and PDF export
5. Custom hooks for portfolio state management following the useProducts pattern

## Relevant Files
Use these files to implement the feature:

**Frontend - Pages (to be created/modified):**
- `apps/Client/src/pages/kompass/PortfoliosPage.tsx` - Replace placeholder with PortfoliosListPage functionality
- `apps/Client/src/pages/kompass/PortfolioBuilderPage.tsx` - New file for the builder interface

**Frontend - Components (to be created):**
- `apps/Client/src/components/kompass/PortfolioCard.tsx` - Portfolio card for the grid view
- `apps/Client/src/components/kompass/PortfolioStatusBadge.tsx` - Status badge component (draft/published)
- `apps/Client/src/components/kompass/ProductCatalogMini.tsx` - Mini product catalog for left panel
- `apps/Client/src/components/kompass/PortfolioBuilder.tsx` - Right panel builder with drag-drop
- `apps/Client/src/components/kompass/PortfolioItemCard.tsx` - Draggable portfolio item with notes

**Frontend - Hooks (to be created):**
- `apps/Client/src/hooks/kompass/usePortfolios.ts` - Hook for portfolio list management
- `apps/Client/src/hooks/kompass/usePortfolioBuilder.ts` - Hook for builder state management

**Frontend - Existing files to reference:**
- `apps/Client/src/pages/kompass/ProductsPage.tsx` - Reference pattern for list page with grid/actions
- `apps/Client/src/hooks/kompass/useProducts.ts` - Reference pattern for data fetching hooks
- `apps/Client/src/components/kompass/ProductCard.tsx` - Reference pattern for card components
- `apps/Client/src/services/kompassService.ts` - portfolioService already implemented (lines 369-463)
- `apps/Client/src/types/kompass.ts` - Portfolio types already defined (lines 343-443)
- `apps/Client/src/App.tsx` - Update routing for new builder page
- `apps/Client/src/components/layout/Sidebar.tsx` - Sidebar navigation (already has Portfolios link)

**Backend - Already implemented:**
- `apps/Server/app/services/portfolio_service.py` - Complete portfolio service
- `apps/Server/app/api/portfolio_routes.py` - Complete API routes
- Reference: `app_docs/feature-566f84a0-portfolio-service.md` - Documentation of portfolio backend

**E2E Test (to be created):**
- `.claude/commands/e2e/test_portfolio_builder.md` - E2E test file for this feature

### New Files
- `apps/Client/src/pages/kompass/PortfolioBuilderPage.tsx` - Main builder page
- `apps/Client/src/components/kompass/PortfolioCard.tsx` - Card component
- `apps/Client/src/components/kompass/PortfolioStatusBadge.tsx` - Status badge
- `apps/Client/src/components/kompass/ProductCatalogMini.tsx` - Mini catalog
- `apps/Client/src/components/kompass/PortfolioBuilder.tsx` - Builder panel
- `apps/Client/src/components/kompass/PortfolioItemCard.tsx` - Draggable item
- `apps/Client/src/hooks/kompass/usePortfolios.ts` - Portfolios list hook
- `apps/Client/src/hooks/kompass/usePortfolioBuilder.ts` - Builder state hook
- `.claude/commands/e2e/test_portfolio_builder.md` - E2E test specification

## Implementation Plan

### Phase 1: Foundation
1. Install @dnd-kit dependencies for drag-and-drop functionality
2. Create custom hooks (usePortfolios, usePortfolioBuilder) following existing patterns
3. Create shared components (PortfolioStatusBadge, PortfolioCard)

### Phase 2: Core Implementation
1. Implement PortfoliosListPage (replace existing placeholder)
   - Grid layout with portfolio cards
   - Quick actions (Open, Duplicate, Delete, Copy Share Link)
   - Create new portfolio button
2. Implement PortfolioBuilderPage with two-column layout
   - Left panel: ProductCatalogMini with search/filters
   - Right panel: PortfolioBuilder with drag-drop
   - Top bar: Portfolio metadata editing

### Phase 3: Integration
1. Add routing for PortfolioBuilderPage (/portfolios/:id)
2. Connect PDF export functionality
3. Implement share link copy with toast notification
4. Wire up all API calls through portfolioService

## Step by Step Tasks

### Step 1: Install Dependencies
- Install @dnd-kit/core, @dnd-kit/sortable, @dnd-kit/utilities for drag-and-drop
- Command: `cd apps/Client && npm install @dnd-kit/core @dnd-kit/sortable @dnd-kit/utilities`

### Step 2: Create E2E Test Specification
- Read `.claude/commands/test_e2e.md` to understand E2E test format
- Read `.claude/commands/e2e/test_products_catalog.md` for reference pattern
- Create `.claude/commands/e2e/test_portfolio_builder.md` with test steps for:
  - Portfolio list page loading
  - Create new portfolio
  - Open portfolio in builder
  - Add products from mini catalog
  - Reorder products with drag-drop
  - Edit portfolio name and niche
  - Save portfolio
  - Copy share link
  - Preview PDF

### Step 3: Create usePortfolios Hook
- Create `apps/Client/src/hooks/kompass/usePortfolios.ts`
- Follow pattern from useProducts.ts
- Include: list fetching, pagination, filters, CRUD operations
- Include: duplicate, delete, getShareToken actions
- Export types: UsePortfoliosState, UsePortfoliosReturn

### Step 4: Create usePortfolioBuilder Hook
- Create `apps/Client/src/hooks/kompass/usePortfolioBuilder.ts`
- Manage builder state: portfolio data, items, dirty state
- Include: load portfolio, add item, remove item, reorder items, update notes
- Include: save portfolio, get share token, export PDF
- Handle optimistic updates for drag-drop reordering

### Step 5: Create PortfolioStatusBadge Component
- Create `apps/Client/src/components/kompass/PortfolioStatusBadge.tsx`
- Display status with appropriate colors (active=green, inactive=gray)
- Use MUI Chip component

### Step 6: Create PortfolioCard Component
- Create `apps/Client/src/components/kompass/PortfolioCard.tsx`
- Display: cover image, name, niche name, product count, status badge
- Action buttons: Open, Duplicate, Delete, Copy Share Link
- Use MUI Card, CardMedia, CardContent, CardActions
- Handle image placeholder when no products have images

### Step 7: Implement PortfoliosListPage
- Modify `apps/Client/src/pages/kompass/PortfoliosPage.tsx`
- Replace placeholder with full functionality
- Grid of PortfolioCard components using MUI Grid
- "Create Portfolio" button in header
- Search and filter controls (by niche, by status)
- Pagination controls
- Delete confirmation dialog
- Snackbar notifications for actions
- Empty state with call-to-action

### Step 8: Create ProductCatalogMini Component
- Create `apps/Client/src/components/kompass/ProductCatalogMini.tsx`
- Compact product list with search input
- Filter by category dropdown
- Compact ProductCard variant or list items
- Click handler to add product to portfolio
- Visual indication for products already in portfolio

### Step 9: Create PortfolioItemCard Component
- Create `apps/Client/src/components/kompass/PortfolioItemCard.tsx`
- Draggable card using @dnd-kit
- Display: product image, name, price
- Curator notes input field (TextField)
- Remove button (IconButton with delete icon)
- Drag handle indicator

### Step 10: Create PortfolioBuilder Component
- Create `apps/Client/src/components/kompass/PortfolioBuilder.tsx`
- DndContext and SortableContext from @dnd-kit
- List of PortfolioItemCard components
- Handle drag end to reorder
- Empty state when no products added
- Product count display

### Step 11: Implement PortfolioBuilderPage
- Create `apps/Client/src/pages/kompass/PortfolioBuilderPage.tsx`
- Two-column layout (40% left, 60% right)
- Top bar with:
  - Editable portfolio name (TextField)
  - Niche selector (Autocomplete with niches)
  - Status toggle (Switch or ToggleButton for active/inactive)
  - Save button (Button with save icon)
  - Preview PDF button (Button with pdf icon)
  - Copy Share Link button (Button with link icon)
- Left panel: ProductCatalogMini
- Right panel: PortfolioBuilder
- Loading state while fetching
- Handle unsaved changes warning

### Step 12: Update App Routing
- Modify `apps/Client/src/App.tsx`
- Add route: `/portfolios/:id` -> PortfolioBuilderPage
- Keep `/portfolios` -> PortfoliosListPage (modified PortfoliosPage)

### Step 13: Implement PDF Preview and Share Link
- Wire PDF export button to portfolioService.exportPdf()
- Open PDF in new tab or download
- Wire share link button to portfolioService.getShareToken()
- Copy link to clipboard with toast notification

### Step 14: Run Validation Commands
- Execute all validation commands to ensure zero regressions

## Testing Strategy

### Unit Tests
- usePortfolios hook: test list fetching, pagination, filter changes
- usePortfolioBuilder hook: test add/remove/reorder items, save
- PortfolioCard: test action button clicks, display of data
- PortfolioBuilder: test drag-drop reordering

### Edge Cases
- Empty portfolio (no items) - show helpful empty state
- Portfolio with many items - test scrolling and performance
- Adding duplicate product to portfolio - prevent or warn
- Reordering with slow network - optimistic UI update
- PDF export for large portfolio - loading indicator
- Share link expiration - handle gracefully
- Unsaved changes on navigation - warn user

## Acceptance Criteria
- [ ] PortfoliosListPage displays grid of portfolio cards
- [ ] Portfolio cards show name, niche, product count, status badge, cover image
- [ ] Quick actions work: Open, Duplicate, Delete, Copy share link
- [ ] Create new portfolio button navigates to builder
- [ ] PortfolioBuilderPage loads with two-column layout
- [ ] Left panel shows product catalog with search and filters
- [ ] Click on product in left panel adds it to portfolio
- [ ] Products in portfolio can be reordered via drag-and-drop
- [ ] Remove button on each portfolio item works
- [ ] Curator notes input per item works
- [ ] Portfolio name is editable in top bar
- [ ] Niche selector dropdown works
- [ ] Status toggle (active/inactive) works
- [ ] Save button persists changes
- [ ] Preview PDF button generates and shows PDF
- [ ] Copy share link button copies URL to clipboard
- [ ] All existing tests pass (zero regressions)

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Client && npm install @dnd-kit/core @dnd-kit/sortable @dnd-kit/utilities` - Install drag-drop dependencies
- `cd apps/Client && npm run typecheck` - Run Client type check to validate no TypeScript errors
- `cd apps/Client && npm run lint` - Run Client linting to validate code quality
- `cd apps/Client && npm run build` - Run Client build to validate production build works
- `cd apps/Server && source .venv/bin/activate && .venv/bin/pytest tests/ -v --tb=short` - Run Server tests to validate backend still works
- `cd apps/Server && source .venv/bin/activate && .venv/bin/ruff check .` - Run Server linting

Read `.claude/commands/test_e2e.md`, then read and execute the new E2E test file `.claude/commands/e2e/test_portfolio_builder.md` to validate the portfolio builder functionality works.

## Notes
- The backend portfolio service is already complete (see `app_docs/feature-566f84a0-portfolio-service.md`)
- The portfolioService in kompassService.ts already has all required methods
- Portfolio types are already defined in kompass.ts
- The existing ProductsPage provides a good reference pattern for list pages
- The useProducts hook provides a good reference pattern for data fetching
- @dnd-kit is preferred over react-beautiful-dnd for React 19 compatibility
- Cover image for portfolio card should use first product's primary image or placeholder
- PDF preview should open in new tab to avoid disrupting builder state
- Share links are JWT tokens with 30-day expiry (handled by backend)
