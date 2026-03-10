# Trade Fair Dashboard Activity Feed

**ADW ID:** a9b12751
**Date:** 2026-03-09
**Specification:** specs/issue-145-adw-a9b12751-trade-fair-dashboard-activity-feed.md

## Overview

Adds a "Trade Fair Activity" widget to the Kompass Dashboard that provides the back-office team with near-real-time visibility into suppliers captured during trade fairs. The widget displays KPIs (total captures, suppliers created, emails sent, responses), a status breakdown of capture processing stages, and a recent captures list with auto-refresh every 60 seconds. All UI text is in Spanish (Colombian).

## What Was Built

- **Backend API endpoint** `GET /api/dashboard/trade-fair` returning aggregated trade fair capture statistics
- **TradeFairRepository** data access layer with methods for capture stats, outreach stats, recent captures, and counts
- **Dashboard service method** `get_trade_fair_activity()` with outreach aggregation logic
- **Frontend TradeFairActivity component** with KPI cards, status badges, recent captures list, and manual refresh
- **useTradeFairActivity hook** with 60-second auto-refresh interval and cleanup on unmount
- **Backend DTOs** `TradeFairActivityDTO` and `TradeFairCaptureDTO`
- **Frontend types** `TradeFairActivity` and `TradeFairCapture` interfaces
- **Unit tests** for the dashboard service trade fair method
- **E2E test definition** for validating the widget end-to-end

## Technical Implementation

### Files Modified

- `apps/Server/app/models/kompass_dto.py`: Added `TradeFairCaptureDTO` and `TradeFairActivityDTO` Pydantic models
- `apps/Server/app/repository/kompass_repository.py`: Added `TradeFairRepository` class with `get_capture_stats()`, `get_supplier_outreach_stats()`, `get_recent_captures()`, `get_captures_count()` methods
- `apps/Server/app/services/dashboard_service.py`: Added `get_trade_fair_activity()` method with outreach aggregation (email_sent, responded)
- `apps/Server/app/api/dashboard_routes.py`: Added `GET /trade-fair` endpoint with optional `hours` query parameter (default 48, max 720)
- `apps/Client/src/types/kompass.ts`: Added `TradeFairCapture` and `TradeFairActivity` interfaces
- `apps/Client/src/services/kompassService.ts`: Added `tradeFairService.getActivity()` API method
- `apps/Client/src/hooks/kompass/useTradeFairActivity.ts`: New hook with auto-refresh via `setInterval`
- `apps/Client/src/components/kompass/TradeFairActivity.tsx`: New widget component (214 lines)
- `apps/Client/src/pages/DashboardPage.tsx`: Integrated `<TradeFairActivity />` between Quick Actions and KPI Cards
- `apps/Server/tests/services/test_dashboard_service.py`: New unit tests for the trade fair activity method
- `.claude/commands/e2e/test_trade_fair_dashboard.md`: New E2E test definition

### Key Changes

- **Outreach aggregation logic**: The service aggregates raw outreach statuses into `email_sent` (contacted + responded + meeting_scheduled + completed) and `responded` (responded + meeting_scheduled + completed) counts for dashboard display
- **Conditional rendering**: The widget returns `null` when no captures exist (`total_captures === 0`), keeping the dashboard clean when there's no trade fair activity
- **Auto-refresh with cleanup**: Uses `setInterval` with `useRef` for the interval ID, properly cleared on component unmount to prevent memory leaks
- **Graceful degradation**: Repository methods return empty defaults on DB connection failure; the service catches exceptions and returns an empty `TradeFairActivityDTO`
- **Relative time formatting**: Custom `getTimeAgo()` function displays Spanish-language relative timestamps (ahora, hace X min, hace Xh, hace X días)

## How to Use

1. Navigate to the Dashboard page after logging in
2. If trade fair captures exist (from the business card capture workflow), the "Actividad Feria Comercial" widget appears automatically between Quick Actions and KPI Cards
3. View KPI cards: Capturas Totales, Proveedores Creados, Emails Enviados, Respuestas
4. Review the status breakdown chips showing capture processing stages with color coding
5. Browse the recent captures list showing company name, contact, status, outreach status, and time ago
6. Click the refresh button to manually reload data; auto-refresh occurs every 60 seconds
7. The widget hides itself when no captures exist

## Configuration

- **Lookback period**: The API accepts an optional `hours` query parameter (default: 48, max: 720) to control how far back captures are included
- **Auto-refresh interval**: Hardcoded to 60 seconds in `useTradeFairActivity.ts` (`AUTO_REFRESH_INTERVAL = 60_000`)
- **No new environment variables** or database migrations required — uses existing `business_card_captures` table and `suppliers.outreach_status` column

## Testing

- **Unit tests**: `cd apps/Server && python -m pytest tests/services/test_dashboard_service.py -v --tb=short`
- **TypeScript check**: `cd apps/Client && npx tsc --noEmit`
- **Build validation**: `cd apps/Client && npm run build`
- **E2E test**: Run the `/test_e2e` command with the `test_trade_fair_dashboard` test definition

## Notes

- The widget is accessible to all authenticated roles (admin, manager, user, viewer)
- Status color mapping: pending=orange, processing=blue, extracted=purple, confirmed=green, rejected=red, failed=grey
- Outreach status labels are in Spanish: Sin contacto, Pendiente, Contactado, Respondió, Reunión, Completado
- The `data-testid="trade-fair-activity"` attribute is set on the root card for E2E test targeting
