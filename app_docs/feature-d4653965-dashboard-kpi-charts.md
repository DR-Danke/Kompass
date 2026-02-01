# Dashboard KPIs and Charts

**ADW ID:** d4653965
**Date:** 2026-02-01
**Specification:** specs/issue-30-adw-d4653965-dashboard-kpi-charts.md

## Overview

This feature implements a comprehensive dashboard for the Kompass application, providing key performance indicators (KPIs), interactive charts powered by Recharts, a recent activity feed with tabs, and quick action buttons. The dashboard serves as the primary landing page, giving users at-a-glance insights into their business operations.

## What Was Built

- **KPI Cards Row**: Five metric cards displaying Total Products, Products Added This Month, Active Suppliers, Quotations Sent This Week, and Pipeline Value
- **Interactive Charts**: Three Recharts visualizations - Pie chart (quotations by status), Line chart (30-day quotation trend), and Bar chart (top quoted products)
- **Activity Feed**: Tabbed component showing recent products, quotations, and clients with clickable navigation
- **Quick Actions**: Buttons for Add Product, Create Quotation, and Import Catalog
- **Backend Dashboard API**: New `/api/dashboard` endpoint aggregating statistics from multiple database tables
- **E2E Test File**: Test specification for dashboard functionality validation

## Technical Implementation

### Files Modified

- `apps/Client/package.json`: Added `recharts` charting library dependency
- `apps/Client/src/pages/DashboardPage.tsx`: Complete rewrite with KPIs, charts, and activity feed
- `apps/Client/src/types/kompass.ts`: Added dashboard-related TypeScript interfaces (DashboardKPIs, DashboardStats, etc.)
- `apps/Client/src/services/kompassService.ts`: Added dashboard service methods
- `apps/Server/main.py`: Registered dashboard router at `/api/dashboard`
- `apps/Server/app/models/kompass_dto.py`: Added Pydantic DTOs for dashboard responses

### New Files Created

- `apps/Client/src/components/kompass/KPICard.tsx`: Reusable KPI card with icon, value formatting, and loading skeleton
- `apps/Client/src/components/kompass/ActivityFeed.tsx`: Tabbed activity list with navigation to detail pages
- `apps/Client/src/components/kompass/QuickActions.tsx`: Quick action button group
- `apps/Client/src/hooks/kompass/useDashboard.ts`: Custom hook managing dashboard state and API calls
- `apps/Server/app/api/dashboard_routes.py`: API routes for dashboard statistics
- `apps/Server/app/services/dashboard_service.py`: Service layer for aggregating dashboard data
- `.claude/commands/e2e/test_dashboard_kpi.md`: E2E test specification

### Key Changes

- **Backend Service Pattern**: `DashboardService` uses efficient SQL queries to aggregate data from products, suppliers, clients, quotations, and quotation_items tables
- **Pipeline Value Calculation**: Sums `grand_total` from quotations linked to clients in 'quoting' or 'negotiating' status
- **Trend Data Generation**: Creates 30-day array with daily sent/accepted quotation counts, filling gaps with zeros
- **Frontend State Management**: `useDashboard` hook handles loading, error, and refresh states
- **Responsive Layout**: Uses MUI Grid with breakpoints for mobile-friendly display

## How to Use

1. Log in to the Kompass application
2. Navigate to the Dashboard (default landing page after login)
3. View KPI cards in the top row for quick business metrics
4. Examine the three charts:
   - **Quotations by Status**: Hover over pie segments for counts/percentages
   - **Quotation Trend**: View sent vs accepted quotations over 30 days
   - **Top Quoted Products**: See which products are most frequently quoted
5. Switch between tabs in the Activity Feed to see recent items
6. Click any activity item to navigate to its detail page
7. Use Quick Actions to navigate to common tasks:
   - Add Product → Products page
   - Create Quotation → Quotation creator
   - Import Catalog → Import wizard

## Configuration

No additional configuration required. The dashboard uses existing database connections and authentication.

## Testing

Run the E2E test to validate dashboard functionality:
```bash
# Execute the E2E test command
/test_e2e test_dashboard_kpi
```

The test validates:
- KPI cards display with correct values
- All three charts render properly
- Activity feed tabs switch correctly
- Quick action navigation works

## Notes

- **Empty State Handling**: Charts and activity feed gracefully display "No data" messages when database is empty
- **Loading Skeletons**: All components show skeleton placeholders while data fetches
- **Error Recovery**: Error state includes retry button to re-fetch dashboard data
- **Currency Formatting**: Pipeline value uses USD currency formatting with Intl.NumberFormat
- **Date Handling**: "This month" and "this week" calculations use server-side date ranges
