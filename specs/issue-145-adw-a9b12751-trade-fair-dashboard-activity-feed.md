# Feature: Trade Fair Dashboard & Activity Feed

## Metadata
issue_number: `145`
adw_id: `a9b12751`
issue_json: ``

## Feature Description
Add a "Trade Fair Activity" section to the existing Kompass Dashboard that provides the back-office team with near-real-time visibility into suppliers captured during trade fairs. The widget displays KPIs (total captures, suppliers created, emails sent, responses), a status breakdown of capture processing stages, and a recent captures list showing company name, contact, status, outreach status, and time ago. The section auto-refreshes every 60 seconds, supports manual refresh, and hides itself when no trade fair captures exist. All UI text is in Spanish (Colombian).

## User Story
As a back-office team member (any role: admin, manager, user, or viewer)
I want to see a Trade Fair Activity section on my dashboard showing recently captured suppliers, their processing status, and outreach progress
So that I can monitor trade fair capture activity in near-real-time and ensure organized data within one day of capture

## Problem Statement
During trade fairs, the field team captures supplier business cards that go through AI extraction and supplier creation. The back-office team currently has no centralized view to monitor capture progress, processing status, or outreach effectiveness. They need a dashboard widget that aggregates trade fair activity data for situational awareness.

## Solution Statement
Extend the existing Dashboard with a new Trade Fair Activity section that queries `business_card_captures` and `suppliers` tables to aggregate capture statistics, status breakdowns, outreach progress, and recent capture details. The backend provides a new `GET /api/dashboard/trade-fair` endpoint, and the frontend renders a conditional widget with KPI cards, status badges, and a recent captures list with auto-refresh.

## Relevant Files
Use these files to implement the feature:

**Backend — Routes & Services:**
- `apps/Server/app/api/dashboard_routes.py` — Add the new `GET /api/dashboard/trade-fair` endpoint here, following the existing pattern with `get_current_user` dependency
- `apps/Server/app/services/dashboard_service.py` — Add `get_trade_fair_activity()` method to the existing `DashboardService` class, following the same connection/query/close pattern
- `apps/Server/app/repository/kompass_repository.py` — Add new repository class `TradeFairRepository` with methods for capture stats and recent captures
- `apps/Server/app/models/kompass_dto.py` — Add DTOs for the trade fair activity response (`TradeFairActivityDTO`, `TradeFairCaptureDTO`)
- `apps/Server/main.py` — Router already registered at `/api/dashboard` prefix, no changes needed

**Backend — Reference (read-only):**
- `apps/Server/database/schema.sql` — Reference for `business_card_captures` table (lines 209-242) and `suppliers` table (lines 111-140) with `outreach_status` field
- `apps/Server/app/config/database.py` — Database connection helpers (`get_database_connection`, `close_database_connection`)
- `apps/Server/app/api/dependencies.py` — Auth dependency `get_current_user`
- `apps/Server/app/services/business_card_service.py` — Reference for business card query patterns
- `apps/Server/app/repository/business_card_repository.py` — Reference for business card table access patterns

**Frontend — Pages & Components:**
- `apps/Client/src/pages/DashboardPage.tsx` — Add the Trade Fair Activity widget section, conditionally rendered
- `apps/Client/src/components/kompass/TradeFairActivity.tsx` — **NEW** component for the trade fair widget
- `apps/Client/src/hooks/kompass/useTradeFairActivity.ts` — **NEW** hook for fetching and auto-refreshing trade fair data
- `apps/Client/src/types/kompass.ts` — Add `TradeFairActivity` and `TradeFairCapture` interfaces
- `apps/Client/src/services/kompassService.ts` — Add `tradeFairService.getActivity()` method

**Frontend — Reference (read-only):**
- `apps/Client/src/hooks/kompass/useDashboard.ts` — Reference for hook pattern
- `apps/Client/src/components/kompass/ActivityFeed.tsx` — Reference for activity list component pattern
- `apps/Client/src/components/kompass/KPICard.tsx` — Reference for KPI card component

**Testing:**
- `apps/Server/tests/services/test_dashboard_service.py` — **NEW** unit tests for trade fair activity method
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_dashboard_kpi.md` to understand E2E test patterns

### New Files
- `apps/Client/src/components/kompass/TradeFairActivity.tsx` — Trade Fair Activity widget component
- `apps/Client/src/hooks/kompass/useTradeFairActivity.ts` — Hook for trade fair data fetching with auto-refresh
- `apps/Server/tests/services/test_dashboard_service.py` — Unit tests for the dashboard trade fair method
- `.claude/commands/e2e/test_trade_fair_dashboard.md` — E2E test definition for validating the trade fair dashboard widget

## Implementation Plan
### Phase 1: Foundation
Add backend DTOs and repository methods for querying trade fair capture statistics and recent captures. This establishes the data access layer needed by the service.

### Phase 2: Core Implementation
Build the dashboard service method and API endpoint. Then implement the frontend types, API service method, custom hook with auto-refresh, and the TradeFairActivity component with KPIs, status badges, and recent captures list.

### Phase 3: Integration
Wire the TradeFairActivity component into the existing DashboardPage with conditional rendering (only show when captures exist). Add unit tests for the backend service and create an E2E test definition. Validate the full stack end-to-end.

## Step by Step Tasks

### Step 1: Create E2E Test Definition
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_dashboard_kpi.md` for E2E test format
- Create `.claude/commands/e2e/test_trade_fair_dashboard.md` with test steps:
  1. Navigate to Dashboard page
  2. Verify the Trade Fair Activity section is visible (or hidden if no captures exist)
  3. Verify KPI cards show: total captures, suppliers created, emails sent, responses
  4. Verify status breakdown badges are rendered with correct colors
  5. Verify recent captures list shows company name, contact, status, outreach status, time ago
  6. Click the refresh button and verify data reloads
  7. Take screenshots at key steps

### Step 2: Add Backend DTOs
- In `apps/Server/app/models/kompass_dto.py`, add:
  - `TradeFairCaptureDTO(BaseModel)` with fields: `id: UUID`, `company_name: Optional[str]`, `contact_name: Optional[str]`, `status: BusinessCardCaptureStatus`, `supplier_id: Optional[UUID]`, `outreach_status: Optional[str]`, `created_at: datetime`
  - `TradeFairActivityDTO(BaseModel)` with fields: `total_captures: int`, `by_status: Dict[str, int]`, `total_suppliers_created: int`, `outreach_status: Dict[str, int]`, `recent_captures: List[TradeFairCaptureDTO]`, `captures_today: int`, `captures_last_48h: int`

### Step 3: Add Repository Methods
- In `apps/Server/app/repository/kompass_repository.py`, add a new `TradeFairRepository` class following the existing repository pattern (connection get/close):
  - `get_capture_stats(self, since: datetime) -> Dict[str, int]` — Query `business_card_captures` for `COUNT(*) GROUP BY status` where `created_at >= since`
  - `get_supplier_outreach_stats(self, since: datetime) -> Dict[str, int]` — Query `suppliers` joined with `business_card_captures` for outreach status counts where the capture `created_at >= since`
  - `get_recent_captures(self, limit: int, since: datetime) -> List[Dict]` — Query `business_card_captures` LEFT JOIN `suppliers` for recent captures with supplier outreach info, ordered by `created_at DESC`, limited by `limit`
  - `get_captures_count(self, since: datetime) -> int` — Simple count of captures since a datetime
  - Create singleton: `trade_fair_repository = TradeFairRepository()`

### Step 4: Add Dashboard Service Method
- In `apps/Server/app/services/dashboard_service.py`:
  - Import `TradeFairActivityDTO`, `TradeFairCaptureDTO`, `BusinessCardCaptureStatus` from DTOs
  - Import `trade_fair_repository` from repository
  - Add method `get_trade_fair_activity(self, hours: int = 48) -> TradeFairActivityDTO`:
    - Calculate `since = datetime.now(timezone.utc) - timedelta(hours=hours)`
    - Calculate `today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)`
    - Call repository methods for: capture stats by status, supplier outreach stats, recent captures (limit 20), captures today count, captures last 48h count
    - Calculate `total_suppliers_created` from captures that have a non-null `supplier_id`
    - Assemble and return `TradeFairActivityDTO`

### Step 5: Add API Endpoint
- In `apps/Server/app/api/dashboard_routes.py`:
  - Import `TradeFairActivityDTO`
  - Add endpoint `GET /trade-fair` (maps to `/api/dashboard/trade-fair`):
    - Auth: `Depends(get_current_user)` — accessible to all authenticated roles
    - Optional query param: `hours: int = 48`
    - Response model: `TradeFairActivityDTO`
    - Call `dashboard_service.get_trade_fair_activity(hours)`
    - Error handling following existing pattern (ValueError → 400, Exception → 500)

### Step 6: Add Backend Unit Tests
- Create `apps/Server/tests/services/test_dashboard_service.py`:
  - Test `get_trade_fair_activity` returns correct DTO structure
  - Test with mocked repository returning empty data (no captures)
  - Test with mocked repository returning sample data
  - Test status aggregation logic
  - Test outreach status aggregation logic
  - Follow existing test patterns from `tests/services/test_supplier_service.py`

### Step 7: Add Frontend Types
- In `apps/Client/src/types/kompass.ts`, add:
  ```typescript
  export interface TradeFairCapture {
    id: string;
    company_name: string | null;
    contact_name: string | null;
    status: BusinessCardCaptureStatus;
    supplier_id: string | null;
    outreach_status: string | null;
    created_at: string;
  }

  export interface TradeFairActivity {
    total_captures: number;
    by_status: Record<string, number>;
    total_suppliers_created: number;
    outreach_status: Record<string, number>;
    recent_captures: TradeFairCapture[];
    captures_today: number;
    captures_last_48h: number;
  }
  ```

### Step 8: Add Frontend API Service Method
- In `apps/Client/src/services/kompassService.ts`:
  - Import `TradeFairActivity` type
  - Add a new `tradeFairService` export after the `dashboardService`:
    ```typescript
    export const tradeFairService = {
      async getActivity(): Promise<TradeFairActivity> {
        const response = await apiClient.get<TradeFairActivity>('/dashboard/trade-fair');
        return response.data;
      },
    };
    ```

### Step 9: Create useTradeFairActivity Hook
- Create `apps/Client/src/hooks/kompass/useTradeFairActivity.ts`:
  - Follow `useDashboard.ts` pattern
  - State: `activity: TradeFairActivity | null`, `isLoading: boolean`, `error: string | null`
  - Fetch on mount with `tradeFairService.getActivity()`
  - Auto-refresh with `setInterval` every 60 seconds
  - Cleanup interval on unmount to prevent memory leaks
  - Expose `refreshActivity()` for manual refresh
  - Return `{ activity, isLoading, error, refreshActivity }`

### Step 10: Create TradeFairActivity Component
- Create `apps/Client/src/components/kompass/TradeFairActivity.tsx`:
  - Import `useTradeFairActivity` hook
  - **KPI row** (4 cards using Grid): Capturas Totales, Proveedores Creados, Emails Enviados, Respuestas Recibidas
  - **Status breakdown**: Row of colored `Chip` components for each status (pending=orange, processing=blue, extracted=purple, confirmed=green, rejected=red, failed=grey) with count
  - **Recent captures list**: `List` component showing last 20 captures with:
    - Company name (bold) and contact name
    - Status chip (colored)
    - Outreach status chip
    - Time ago (use relative time formatting)
  - **Refresh button**: Manual refresh with RefreshIcon
  - **Conditional render**: If `activity` is null or `total_captures === 0`, return null (hide widget)
  - All text labels in Spanish (Colombian): "Actividad Feria Comercial", "Capturas Totales", "Proveedores Creados", "Emails Enviados", "Respuestas", "Capturas Recientes", "Actualizar", "Hoy", "Últimas 48h"
  - Add `data-testid="trade-fair-activity"` for E2E testing

### Step 11: Integrate Widget into DashboardPage
- In `apps/Client/src/pages/DashboardPage.tsx`:
  - Import `TradeFairActivity` component
  - Add `<TradeFairActivity />` as a new `<Grid item xs={12}>` section between the Quick Actions and the KPI Cards rows
  - The component handles its own conditional rendering (returns null when no captures), so no wrapper logic needed in DashboardPage

### Step 12: Run Validation Commands
- Run all validation commands listed below to confirm zero regressions

## Testing Strategy
### Unit Tests
- **Backend `test_dashboard_service.py`:**
  - Test `get_trade_fair_activity` returns `TradeFairActivityDTO` with correct structure
  - Test with mocked empty results (no captures) — all counts should be 0, empty lists
  - Test with mocked capture data — verify status aggregation, outreach aggregation, counts
  - Test `hours` parameter is passed through to repository
  - Test repository methods return None on connection failure (graceful degradation)

### Edge Cases
- No `business_card_captures` records exist → widget hidden, endpoint returns all zeros
- Captures exist but none have linked suppliers → `total_suppliers_created = 0`, `outreach_status` all zero
- All captures are older than 48 hours → `captures_today = 0`, `captures_last_48h = 0`, but `total_captures` reflects actual count based on `hours` parameter
- Captures with NULL `company_name` or `contact_name` → display gracefully (show "—" or skip)
- Database connection failure → service returns default empty DTO, frontend shows error state
- Auto-refresh cleanup on component unmount → no memory leaks
- Concurrent dashboard load + trade fair load → independent hooks, no interference

## Acceptance Criteria
- `GET /api/dashboard/trade-fair` returns correct JSON structure with `total_captures`, `by_status`, `total_suppliers_created`, `outreach_status`, `recent_captures`, `captures_today`, `captures_last_48h`
- Endpoint is accessible to all authenticated roles (admin, manager, user, viewer)
- Trade Fair Activity widget renders on dashboard when captures exist
- Widget is hidden when no captures exist (no empty widget shown)
- KPIs display: total captures, suppliers created, emails sent, responses received
- Status breakdown shows colored badges for each capture status with counts
- Recent captures list shows company name, contact name, status chip, outreach status chip, relative time
- Manual refresh button triggers data reload
- Auto-refresh fires every 60 seconds without memory leaks
- All UI text is in Spanish (Colombian)
- TypeScript compiles without errors
- Frontend builds without errors
- Backend tests pass without regressions

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -m pytest tests/ -v --tb=short` — Run all Server tests to validate the feature works with zero regressions
- `cd apps/Client && npx tsc --noEmit` — Run Client TypeScript type check to validate no type errors
- `cd apps/Client && npm run build` — Run Client production build to validate no build errors
- `cd apps/Client && npm run lint` — Run Client linting to validate code quality
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_trade_fair_dashboard.md` E2E test to validate this functionality works end-to-end

## Notes
- **Parallel execution**: This issue (TF-006) runs in parallel with TF-005 (Review UI) and TF-007 (WeChat) in separate worktrees. Avoid modifying files that those issues also modify if possible.
- **Database**: The `business_card_captures` table and `suppliers.outreach_status` column already exist from TF-003. No migrations needed.
- **Outreach status values**: The `suppliers.outreach_status` column uses: `none`, `pending`, `contacted`, `responded`, `meeting_scheduled`, `completed`. For the dashboard, we aggregate `email_sent` as captures where the linked supplier has `outreach_status IN ('contacted', 'responded', 'meeting_scheduled', 'completed')` and `responded` as those with `outreach_status IN ('responded', 'meeting_scheduled', 'completed')`.
- **No new libraries required**: All needed MUI components (Card, Chip, Grid, List, etc.) and recharts are already available.
- **Repository pattern**: The codebase uses direct SQL via psycopg2 with `get_database_connection`/`close_database_connection`. Follow the same pattern — no ORM.
- **Auto-refresh**: Use `setInterval` with cleanup in `useEffect` return. Do not use `setTimeout` chains.
