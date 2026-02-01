# Feature: Dashboard with KPIs and Charts

## Metadata
issue_number: `30`
adw_id: `d4653965`
issue_json: `{"number":30,"title":"[Kompass] Phase 12A: Dashboard with KPIs","body":"## Context\n**Current Phase:** Phase 12 of 13 - Dashboard & Export\n**Current Issue:** KP-030 (Issue 30 of 33)\n**Parallel Execution:** YES - Runs IN PARALLEL with KP-031.\n\n---\n\n## Description\nCreate main dashboard with key performance indicators.\n\n## Requirements\n\n### File: apps/Client/src/pages/kompass/DashboardPage.tsx\n\n#### KPI Cards (top row)\n- Total Products in Biblia General\n- Products Added This Month\n- Active Suppliers\n- Quotations Sent This Week\n- Pipeline Value (sum of quoting + negotiating)\n\n#### Charts\n- Quotations by Status (pie chart)\n- Quotations Trend (line chart - sent vs accepted over time)\n- Top Products Quoted (bar chart)\n\n#### Recent Activity\n- Latest products added\n- Latest quotations sent\n- Latest clients added\n\n#### Quick Actions\n- Add Product button\n- Create Quotation button\n- Import Catalog button\n\n## Acceptance Criteria\n- [ ] All KPIs displaying correct values\n- [ ] Charts rendering\n- [ ] Activity feed showing recent items\n- [ ] Quick actions working\n\nInclude workflow: adw_plan_build_iso"}`

## Feature Description
This feature creates a comprehensive main dashboard for the Kompass application that displays key performance indicators (KPIs), visualizations (charts), recent activity feeds, and quick action buttons. The dashboard serves as the primary landing page after login, providing users with at-a-glance insights into their business operations including product catalog health, quotation pipeline status, and recent system activity.

## User Story
As a Kompass user (admin, manager, or sales representative)
I want to see an overview dashboard with KPIs, charts, and recent activity
So that I can quickly understand the current state of my business and take immediate actions without navigating to individual pages

## Problem Statement
The current dashboard page is a placeholder with generic cards that don't provide any meaningful business intelligence. Users have to navigate to individual pages (Products, Quotations, Clients) to understand the state of their business, which is time-consuming and doesn't provide a holistic view.

## Solution Statement
Implement a full-featured dashboard that aggregates data from across the application:
1. **Backend**: Create a new dashboard statistics API endpoint that efficiently aggregates KPI data, quotation trends, and recent activity in a single request
2. **Frontend**: Transform the existing placeholder `DashboardPage.tsx` into a comprehensive dashboard with KPI cards, interactive charts using Recharts, an activity feed, and quick action buttons
3. **Integration**: Add a custom hook `useDashboardStats` to manage dashboard data fetching and state

## Relevant Files
Use these files to implement the feature:

### Backend Files
- `apps/Server/app/api/` - Contains all API route modules; will add new `dashboard_routes.py`
- `apps/Server/app/services/` - Contains service layer; will add new `dashboard_service.py`
- `apps/Server/main.py` - FastAPI application entry point; register new dashboard router
- `apps/Server/app/models/kompass_dto.py` - DTOs for API responses; add dashboard-related DTOs
- `apps/Server/app/repository/database.py` - Database connection utilities

### Frontend Files
- `apps/Client/src/pages/DashboardPage.tsx` - Existing placeholder to be replaced with full implementation
- `apps/Client/src/services/kompassService.ts` - API service layer; add dashboard service methods
- `apps/Client/src/types/kompass.ts` - TypeScript types; add dashboard-related types
- `apps/Client/src/hooks/kompass/` - Custom hooks directory; add `useDashboard.ts`
- `apps/Client/src/components/kompass/` - Reusable components; add dashboard-specific components

### E2E Test Reference Files
- `.claude/commands/test_e2e.md` - E2E test runner instructions
- `.claude/commands/e2e/test_quotation_creator.md` - Example E2E test file for reference

### New Files
- `apps/Server/app/api/dashboard_routes.py` - New API routes for dashboard statistics
- `apps/Server/app/services/dashboard_service.py` - New service for dashboard data aggregation
- `apps/Client/src/hooks/kompass/useDashboard.ts` - New custom hook for dashboard state
- `apps/Client/src/components/kompass/KPICard.tsx` - Reusable KPI card component
- `apps/Client/src/components/kompass/ActivityFeed.tsx` - Recent activity list component
- `apps/Client/src/components/kompass/QuickActions.tsx` - Quick action buttons component
- `.claude/commands/e2e/test_dashboard_kpi.md` - E2E test file for dashboard functionality

## Implementation Plan

### Phase 1: Foundation
1. Add `recharts` charting library to frontend dependencies
2. Define TypeScript interfaces for dashboard statistics in `apps/Client/src/types/kompass.ts`
3. Define Pydantic DTOs for dashboard response in `apps/Server/app/models/kompass_dto.py`
4. Create the dashboard service layer in the backend to aggregate statistics

### Phase 2: Core Implementation
1. Implement the backend dashboard service with efficient database queries:
   - Total products count
   - Products added this month count
   - Active suppliers count
   - Quotations sent this week count
   - Pipeline value calculation (quoting + negotiating clients)
   - Quotations by status aggregation
   - Quotations trend over time (last 30 days)
   - Top quoted products
   - Recent products, quotations, and clients
2. Create the dashboard API endpoint
3. Add frontend service method for fetching dashboard stats
4. Create the `useDashboard` custom hook
5. Build reusable UI components (KPICard, ActivityFeed, QuickActions)
6. Update the DashboardPage with all required sections

### Phase 3: Integration
1. Register dashboard router in FastAPI main.py
2. Wire up all components in DashboardPage
3. Add navigation for quick actions
4. Test data loading and error states
5. Create E2E test file for dashboard functionality

## Step by Step Tasks

### Step 1: Install Recharts Library
- Navigate to `apps/Client` directory
- Run `npm install recharts` to add the charting library
- Verify the dependency is added to `package.json`

### Step 2: Define Dashboard TypeScript Types
- Open `apps/Client/src/types/kompass.ts`
- Add the following interfaces at the end of the file:
  - `DashboardKPIs` - contains totalProducts, productsAddedThisMonth, activeSuppliers, quotationsSentThisWeek, pipelineValue
  - `QuotationsByStatus` - object with status counts (draft, sent, viewed, negotiating, accepted, rejected, expired)
  - `QuotationTrendPoint` - date and counts for sent/accepted
  - `TopQuotedProduct` - product id, name, sku, quoteCount
  - `RecentProduct` - id, name, sku, supplierName, createdAt
  - `RecentQuotation` - id, quotationNumber, clientName, status, grandTotal, createdAt
  - `RecentClient` - id, companyName, status, createdAt
  - `DashboardStats` - combines all above types

### Step 3: Define Backend Dashboard DTOs
- Open `apps/Server/app/models/kompass_dto.py`
- Add Pydantic models matching the frontend types:
  - `DashboardKPIsDTO`
  - `QuotationsByStatusDTO`
  - `QuotationTrendPointDTO`
  - `TopQuotedProductDTO`
  - `RecentProductDTO`
  - `RecentQuotationDTO`
  - `RecentClientDTO`
  - `DashboardStatsDTO`

### Step 4: Create Dashboard Service
- Create new file `apps/Server/app/services/dashboard_service.py`
- Implement `DashboardService` class with method `get_dashboard_stats()` that:
  - Queries total product count
  - Queries products created in current month
  - Queries active supplier count
  - Queries quotations with status 'sent' created this week
  - Calculates pipeline value from clients in 'quoting' or 'negotiating' status
  - Aggregates quotation counts by status
  - Generates quotation trend data for last 30 days
  - Gets top 5 most quoted products
  - Gets 5 most recent products, quotations, and clients

### Step 5: Create Dashboard API Routes
- Create new file `apps/Server/app/api/dashboard_routes.py`
- Create router with tag "Dashboard"
- Implement `GET /` endpoint that returns `DashboardStatsDTO`
- Requires authentication via `get_current_user` dependency

### Step 6: Register Dashboard Router in Main
- Open `apps/Server/main.py`
- Import dashboard_routes
- Add router with prefix `/api/dashboard`

### Step 7: Add Dashboard Service to Frontend
- Open `apps/Client/src/services/kompassService.ts`
- Add `dashboardService` object with `getStats()` method
- Method calls `GET /dashboard` endpoint and returns `DashboardStats`

### Step 8: Create useDashboard Hook
- Create new file `apps/Client/src/hooks/kompass/useDashboard.ts`
- Implement hook that:
  - Manages loading, error, and data states
  - Fetches dashboard stats on mount
  - Provides refresh function
  - Returns stats, isLoading, error, and refreshStats

### Step 9: Create KPICard Component
- Create new file `apps/Client/src/components/kompass/KPICard.tsx`
- Build a reusable card component that displays:
  - Title
  - Value (with optional formatting)
  - Optional icon
  - Optional trend indicator (up/down percentage)
  - Optional loading skeleton state

### Step 10: Create ActivityFeed Component
- Create new file `apps/Client/src/components/kompass/ActivityFeed.tsx`
- Build a component that displays:
  - Three tabs: Products, Quotations, Clients
  - List of recent items for each tab
  - Item click navigates to detail page
  - Loading skeleton state
  - Empty state message

### Step 11: Create QuickActions Component
- Create new file `apps/Client/src/components/kompass/QuickActions.tsx`
- Build a component with three action buttons:
  - Add Product - navigates to /products (with add dialog trigger)
  - Create Quotation - navigates to /quotations/new
  - Import Catalog - navigates to /import-wizard

### Step 12: Update DashboardPage with Full Implementation
- Open `apps/Client/src/pages/DashboardPage.tsx`
- Replace placeholder content with full implementation:
  - Import useDashboard hook
  - Import Recharts components (PieChart, LineChart, BarChart)
  - Import KPICard, ActivityFeed, QuickActions components
  - Layout structure:
    - Welcome header with user name
    - Quick actions row
    - KPI cards row (5 cards in a grid)
    - Charts section (3 charts in a row)
    - Recent activity section
  - Handle loading states with skeletons
  - Handle error states with retry option

### Step 13: Create E2E Test File for Dashboard
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_quotation_creator.md` to understand E2E test format
- Create new file `.claude/commands/e2e/test_dashboard_kpi.md`
- Define test steps for:
  - Page load and KPI display verification
  - Chart rendering verification
  - Activity feed tab switching
  - Quick action button navigation
  - Success criteria checklist
  - Screenshot capture points

### Step 14: Run Validation Commands
- Execute all validation commands to ensure zero regressions
- Run backend tests
- Run frontend type check
- Run frontend build
- Execute E2E test for dashboard

## Testing Strategy

### Unit Tests
- Backend service tests for `dashboard_service.py`:
  - Test KPI calculations with mock data
  - Test date range filtering for "this month" and "this week"
  - Test pipeline value aggregation
  - Test trend data generation
- Frontend hook tests for `useDashboard.ts`:
  - Test loading state transitions
  - Test error handling
  - Test refresh functionality

### Edge Cases
- Empty database (no products, quotations, or clients)
- No quotations sent this week
- No products added this month
- No clients in pipeline
- Large numbers (ensure proper formatting)
- Missing or null client names on quotations
- Timezone handling for date-based queries

## Acceptance Criteria
- [ ] Dashboard page loads without errors
- [ ] All 5 KPI cards display correct values from database
- [ ] Pie chart shows quotations by status with interactive legend
- [ ] Line chart shows quotation trend (sent vs accepted) over last 30 days
- [ ] Bar chart shows top 5 most quoted products
- [ ] Activity feed shows latest 5 products, quotations, and clients
- [ ] Activity feed tabs switch correctly between categories
- [ ] Quick action "Add Product" navigates to products page
- [ ] Quick action "Create Quotation" navigates to /quotations/new
- [ ] Quick action "Import Catalog" navigates to /import-wizard
- [ ] Loading skeletons display while data is fetching
- [ ] Error state displays with retry option if API fails
- [ ] Empty states handled gracefully when no data exists

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

1. Install dependencies and run backend tests:
```bash
cd apps/Server && source .venv/bin/activate && .venv/bin/pytest tests/ -v --tb=short
```

2. Run backend linting:
```bash
cd apps/Server && source .venv/bin/activate && .venv/bin/ruff check .
```

3. Run frontend type check:
```bash
cd apps/Client && npm run typecheck
```

4. Run frontend lint:
```bash
cd apps/Client && npm run lint
```

5. Run frontend build:
```bash
cd apps/Client && npm run build
```

6. Execute E2E test:
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_dashboard_kpi.md` test file to validate this functionality works.

## Notes
- **Chart Library**: Using Recharts (https://recharts.org/) which is a composable charting library built on React components. It integrates well with MUI and has a small bundle size.
- **Pipeline Value Calculation**: The pipeline value is calculated by summing the `grand_total` of all quotations associated with clients in 'quoting' or 'negotiating' status. This provides a financial forecast of potential revenue.
- **Date Handling**: All "this month" and "this week" calculations should use UTC to avoid timezone issues. The backend should calculate these ranges server-side.
- **Performance**: The dashboard endpoint aggregates multiple queries. Consider caching in the future if the database grows large. For now, optimize with efficient SQL queries using CTEs where appropriate.
- **Charting Data Format**: Recharts expects data as arrays of objects. Ensure the backend returns data in the correct format to minimize frontend transformation.
- **Responsive Design**: Use MUI Grid with appropriate breakpoints so charts and KPI cards stack properly on mobile devices.
