"""Dashboard API routes for KPI statistics and activity feeds.

This module provides REST endpoints for retrieving dashboard statistics
including KPIs, charts data, and recent activity.
"""

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_current_user
from app.models.kompass_dto import DashboardStatsDTO, TradeFairActivityDTO
from app.services.dashboard_service import dashboard_service

router = APIRouter(tags=["Dashboard"])


@router.get("", response_model=DashboardStatsDTO)
async def get_dashboard_stats(
    current_user: dict = Depends(get_current_user),
) -> DashboardStatsDTO:
    """Get dashboard statistics including KPIs, charts data, and activity feeds.

    Returns:
        DashboardStatsDTO containing:
        - kpis: Key performance indicators
        - quotations_by_status: Quotation counts by status for pie chart
        - quotation_trend: 30-day trend data for line chart
        - top_quoted_products: Top 5 most quoted products for bar chart
        - recent_products: 5 most recent products
        - recent_quotations: 5 most recent quotations
        - recent_clients: 5 most recent clients
    """
    print(f"INFO [DashboardRoutes]: User {current_user.get('sub')} fetching dashboard stats")
    try:
        return dashboard_service.get_dashboard_stats()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"ERROR [DashboardRoutes]: Failed to get dashboard stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dashboard statistics")


@router.get("/trade-fair", response_model=TradeFairActivityDTO)
async def get_trade_fair_activity(
    hours: int = Query(default=48, ge=1, le=720),
    current_user: dict = Depends(get_current_user),
) -> TradeFairActivityDTO:
    """Get trade fair activity summary for the dashboard widget.

    Args:
        hours: Number of hours to look back for capture data (default 48, max 720).

    Returns:
        TradeFairActivityDTO with capture statistics, status breakdown, and recent captures.
    """
    print(f"INFO [DashboardRoutes]: User {current_user.get('sub')} fetching trade fair activity")
    try:
        return dashboard_service.get_trade_fair_activity(hours)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"ERROR [DashboardRoutes]: Failed to get trade fair activity: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve trade fair activity")
