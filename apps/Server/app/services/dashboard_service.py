"""Dashboard service for aggregating statistics and KPIs.

This service provides business logic for retrieving dashboard data including
KPIs, charts data, and recent activity feeds.
"""

from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, List

from app.config.database import close_database_connection, get_database_connection
from app.models.kompass_dto import (
    ClientStatus,
    DashboardKPIsDTO,
    DashboardStatsDTO,
    QuotationsByStatusDTO,
    QuotationStatus,
    QuotationTrendPointDTO,
    RecentClientDTO,
    RecentProductDTO,
    RecentQuotationDTO,
    TopQuotedProductDTO,
)


class DashboardService:
    """Service for aggregating dashboard statistics."""

    def get_dashboard_stats(self) -> DashboardStatsDTO:
        """Get complete dashboard statistics.

        Returns:
            Dashboard statistics DTO with KPIs, charts data, and activity feeds.

        Raises:
            ValueError: If database query fails.
        """
        print("INFO [DashboardService]: Fetching dashboard statistics")

        kpis = self._get_kpis()
        quotations_by_status = self._get_quotations_by_status()
        quotation_trend = self._get_quotation_trend()
        top_quoted_products = self._get_top_quoted_products()
        recent_products = self._get_recent_products()
        recent_quotations = self._get_recent_quotations()
        recent_clients = self._get_recent_clients()

        return DashboardStatsDTO(
            kpis=kpis,
            quotations_by_status=quotations_by_status,
            quotation_trend=quotation_trend,
            top_quoted_products=top_quoted_products,
            recent_products=recent_products,
            recent_quotations=recent_quotations,
            recent_clients=recent_clients,
        )

    def _get_kpis(self) -> DashboardKPIsDTO:
        """Get KPI metrics."""
        conn = get_database_connection()
        if not conn:
            print("WARN [DashboardService]: No database connection for KPIs")
            return DashboardKPIsDTO()

        try:
            with conn.cursor() as cur:
                # Total products
                cur.execute("SELECT COUNT(*) FROM products")
                total_products = cur.fetchone()[0] or 0

                # Products added this month
                first_of_month = date.today().replace(day=1)
                cur.execute(
                    "SELECT COUNT(*) FROM products WHERE created_at >= %s",
                    (first_of_month,),
                )
                products_this_month = cur.fetchone()[0] or 0

                # Active suppliers
                cur.execute(
                    "SELECT COUNT(*) FROM suppliers WHERE status = 'active'"
                )
                active_suppliers = cur.fetchone()[0] or 0

                # Quotations sent this week
                today = date.today()
                start_of_week = today - timedelta(days=today.weekday())
                cur.execute(
                    """
                    SELECT COUNT(*) FROM quotations
                    WHERE status = 'sent' AND created_at >= %s
                    """,
                    (start_of_week,),
                )
                quotations_this_week = cur.fetchone()[0] or 0

                # Pipeline value (sum of grand_total for quotations of clients in quoting/negotiating status)
                cur.execute(
                    """
                    SELECT COALESCE(SUM(q.grand_total), 0)
                    FROM quotations q
                    JOIN clients c ON q.client_id = c.id
                    WHERE c.status IN ('quoting', 'negotiating')
                    """,
                )
                pipeline_value = cur.fetchone()[0] or Decimal("0.00")

                return DashboardKPIsDTO(
                    total_products=total_products,
                    products_added_this_month=products_this_month,
                    active_suppliers=active_suppliers,
                    quotations_sent_this_week=quotations_this_week,
                    pipeline_value=pipeline_value,
                )
        except Exception as e:
            print(f"ERROR [DashboardService]: Failed to get KPIs: {e}")
            return DashboardKPIsDTO()
        finally:
            close_database_connection(conn)

    def _get_quotations_by_status(self) -> QuotationsByStatusDTO:
        """Get quotation counts by status."""
        conn = get_database_connection()
        if not conn:
            return QuotationsByStatusDTO()

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT status, COUNT(*) as count
                    FROM quotations
                    GROUP BY status
                    """
                )
                rows = cur.fetchall()

                status_counts: Dict[str, int] = {row[0]: row[1] for row in rows}

                return QuotationsByStatusDTO(
                    draft=status_counts.get("draft", 0),
                    sent=status_counts.get("sent", 0),
                    viewed=status_counts.get("viewed", 0),
                    negotiating=status_counts.get("negotiating", 0),
                    accepted=status_counts.get("accepted", 0),
                    rejected=status_counts.get("rejected", 0),
                    expired=status_counts.get("expired", 0),
                )
        except Exception as e:
            print(f"ERROR [DashboardService]: Failed to get quotations by status: {e}")
            return QuotationsByStatusDTO()
        finally:
            close_database_connection(conn)

    def _get_quotation_trend(self) -> List[QuotationTrendPointDTO]:
        """Get quotation trend data for the last 30 days."""
        conn = get_database_connection()
        if not conn:
            return []

        try:
            with conn.cursor() as cur:
                thirty_days_ago = date.today() - timedelta(days=30)

                # Get daily counts for sent quotations
                cur.execute(
                    """
                    SELECT DATE(created_at) as day, COUNT(*) as count
                    FROM quotations
                    WHERE status = 'sent' AND DATE(created_at) >= %s
                    GROUP BY DATE(created_at)
                    ORDER BY day
                    """,
                    (thirty_days_ago,),
                )
                sent_rows = cur.fetchall()
                sent_by_date = {str(row[0]): row[1] for row in sent_rows}

                # Get daily counts for accepted quotations
                cur.execute(
                    """
                    SELECT DATE(created_at) as day, COUNT(*) as count
                    FROM quotations
                    WHERE status = 'accepted' AND DATE(created_at) >= %s
                    GROUP BY DATE(created_at)
                    ORDER BY day
                    """,
                    (thirty_days_ago,),
                )
                accepted_rows = cur.fetchall()
                accepted_by_date = {str(row[0]): row[1] for row in accepted_rows}

                # Build 30-day trend with all dates
                trend: List[QuotationTrendPointDTO] = []
                for i in range(30):
                    current_date = thirty_days_ago + timedelta(days=i)
                    date_str = str(current_date)
                    trend.append(
                        QuotationTrendPointDTO(
                            date=date_str,
                            sent=sent_by_date.get(date_str, 0),
                            accepted=accepted_by_date.get(date_str, 0),
                        )
                    )

                return trend
        except Exception as e:
            print(f"ERROR [DashboardService]: Failed to get quotation trend: {e}")
            return []
        finally:
            close_database_connection(conn)

    def _get_top_quoted_products(self) -> List[TopQuotedProductDTO]:
        """Get top 5 most quoted products."""
        conn = get_database_connection()
        if not conn:
            return []

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT p.id, p.name, p.sku, COUNT(qi.id) as quote_count
                    FROM products p
                    JOIN quotation_items qi ON qi.product_id = p.id
                    GROUP BY p.id, p.name, p.sku
                    ORDER BY quote_count DESC
                    LIMIT 5
                    """
                )
                rows = cur.fetchall()

                return [
                    TopQuotedProductDTO(
                        id=row[0],
                        name=row[1],
                        sku=row[2],
                        quote_count=row[3],
                    )
                    for row in rows
                ]
        except Exception as e:
            print(f"ERROR [DashboardService]: Failed to get top quoted products: {e}")
            return []
        finally:
            close_database_connection(conn)

    def _get_recent_products(self) -> List[RecentProductDTO]:
        """Get 5 most recent products."""
        conn = get_database_connection()
        if not conn:
            return []

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT p.id, p.name, p.sku, s.name as supplier_name, p.created_at
                    FROM products p
                    LEFT JOIN suppliers s ON p.supplier_id = s.id
                    ORDER BY p.created_at DESC
                    LIMIT 5
                    """
                )
                rows = cur.fetchall()

                return [
                    RecentProductDTO(
                        id=row[0],
                        name=row[1],
                        sku=row[2],
                        supplier_name=row[3],
                        created_at=row[4],
                    )
                    for row in rows
                ]
        except Exception as e:
            print(f"ERROR [DashboardService]: Failed to get recent products: {e}")
            return []
        finally:
            close_database_connection(conn)

    def _get_recent_quotations(self) -> List[RecentQuotationDTO]:
        """Get 5 most recent quotations."""
        conn = get_database_connection()
        if not conn:
            return []

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT q.id, q.quotation_number, c.company_name, q.status, q.grand_total, q.created_at
                    FROM quotations q
                    LEFT JOIN clients c ON q.client_id = c.id
                    ORDER BY q.created_at DESC
                    LIMIT 5
                    """
                )
                rows = cur.fetchall()

                return [
                    RecentQuotationDTO(
                        id=row[0],
                        quotation_number=row[1],
                        client_name=row[2],
                        status=QuotationStatus(row[3]) if row[3] else QuotationStatus.DRAFT,
                        grand_total=row[4] or Decimal("0.00"),
                        created_at=row[5],
                    )
                    for row in rows
                ]
        except Exception as e:
            print(f"ERROR [DashboardService]: Failed to get recent quotations: {e}")
            return []
        finally:
            close_database_connection(conn)

    def _get_recent_clients(self) -> List[RecentClientDTO]:
        """Get 5 most recent clients."""
        conn = get_database_connection()
        if not conn:
            return []

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, company_name, status, created_at
                    FROM clients
                    ORDER BY created_at DESC
                    LIMIT 5
                    """
                )
                rows = cur.fetchall()

                return [
                    RecentClientDTO(
                        id=row[0],
                        company_name=row[1],
                        status=ClientStatus(row[2]) if row[2] else ClientStatus.LEAD,
                        created_at=row[3],
                    )
                    for row in rows
                ]
        except Exception as e:
            print(f"ERROR [DashboardService]: Failed to get recent clients: {e}")
            return []
        finally:
            close_database_connection(conn)


# Singleton instance
dashboard_service = DashboardService()
