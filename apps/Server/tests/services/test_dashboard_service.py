"""Unit tests for DashboardService trade fair activity method."""

from datetime import datetime, timezone
from unittest.mock import patch
from uuid import uuid4

import pytest

from app.models.kompass_dto import TradeFairActivityDTO
from app.services.dashboard_service import DashboardService


@pytest.fixture
def dashboard_service():
    """Create a fresh DashboardService instance for each test."""
    return DashboardService()


@pytest.fixture
def sample_captures():
    """Sample capture data for testing."""
    return [
        {
            "id": uuid4(),
            "company_name": "Supplier A",
            "contact_name": "John Doe",
            "status": "confirmed",
            "supplier_id": uuid4(),
            "outreach_status": "contacted",
            "created_at": datetime.now(timezone.utc),
        },
        {
            "id": uuid4(),
            "company_name": "Supplier B",
            "contact_name": "Jane Smith",
            "status": "extracted",
            "supplier_id": None,
            "outreach_status": None,
            "created_at": datetime.now(timezone.utc),
        },
        {
            "id": uuid4(),
            "company_name": None,
            "contact_name": None,
            "status": "pending",
            "supplier_id": None,
            "outreach_status": None,
            "created_at": datetime.now(timezone.utc),
        },
    ]


class TestGetTradeFairActivityEmpty:
    """Tests for get_trade_fair_activity with no data."""

    @patch("app.services.dashboard_service.trade_fair_repository")
    def test_returns_empty_dto_when_no_captures(self, mock_repo, dashboard_service):
        """Test that empty data returns a valid empty DTO."""
        mock_repo.get_capture_stats.return_value = {}
        mock_repo.get_supplier_outreach_stats.return_value = {}
        mock_repo.get_recent_captures.return_value = []
        mock_repo.get_captures_count.return_value = 0

        result = dashboard_service.get_trade_fair_activity()

        assert isinstance(result, TradeFairActivityDTO)
        assert result.total_captures == 0
        assert result.by_status == {}
        assert result.total_suppliers_created == 0
        assert result.recent_captures == []
        assert result.captures_today == 0
        assert result.captures_last_48h == 0

    @patch("app.services.dashboard_service.trade_fair_repository")
    def test_outreach_status_empty_when_no_captures(self, mock_repo, dashboard_service):
        """Test that outreach status has aggregated keys even when empty."""
        mock_repo.get_capture_stats.return_value = {}
        mock_repo.get_supplier_outreach_stats.return_value = {}
        mock_repo.get_recent_captures.return_value = []
        mock_repo.get_captures_count.return_value = 0

        result = dashboard_service.get_trade_fair_activity()

        assert result.outreach_status["email_sent"] == 0
        assert result.outreach_status["responded"] == 0


class TestGetTradeFairActivityWithData:
    """Tests for get_trade_fair_activity with sample data."""

    @patch("app.services.dashboard_service.trade_fair_repository")
    def test_returns_correct_total_captures(self, mock_repo, dashboard_service):
        """Test total captures is sum of all status counts."""
        mock_repo.get_capture_stats.return_value = {
            "pending": 3,
            "confirmed": 2,
            "extracted": 1,
        }
        mock_repo.get_supplier_outreach_stats.return_value = {}
        mock_repo.get_recent_captures.return_value = []
        mock_repo.get_captures_count.return_value = 6

        result = dashboard_service.get_trade_fair_activity()

        assert result.total_captures == 6

    @patch("app.services.dashboard_service.trade_fair_repository")
    def test_status_aggregation(self, mock_repo, dashboard_service):
        """Test by_status reflects capture stats from repository."""
        stats = {"pending": 5, "processing": 2, "confirmed": 3}
        mock_repo.get_capture_stats.return_value = stats
        mock_repo.get_supplier_outreach_stats.return_value = {}
        mock_repo.get_recent_captures.return_value = []
        mock_repo.get_captures_count.return_value = 10

        result = dashboard_service.get_trade_fair_activity()

        assert result.by_status == stats

    @patch("app.services.dashboard_service.trade_fair_repository")
    def test_outreach_aggregation(self, mock_repo, dashboard_service):
        """Test outreach status aggregates email_sent and responded correctly."""
        mock_repo.get_capture_stats.return_value = {}
        mock_repo.get_supplier_outreach_stats.return_value = {
            "none": 2,
            "contacted": 3,
            "responded": 1,
            "meeting_scheduled": 1,
        }
        mock_repo.get_recent_captures.return_value = []
        mock_repo.get_captures_count.return_value = 0

        result = dashboard_service.get_trade_fair_activity()

        # email_sent = contacted + responded + meeting_scheduled = 3+1+1=5
        assert result.outreach_status["email_sent"] == 5
        # responded = responded + meeting_scheduled = 1+1=2
        assert result.outreach_status["responded"] == 2

    @patch("app.services.dashboard_service.trade_fair_repository")
    def test_suppliers_created_count(self, mock_repo, dashboard_service, sample_captures):
        """Test total_suppliers_created counts captures with non-null supplier_id."""
        mock_repo.get_capture_stats.return_value = {"confirmed": 1, "extracted": 1, "pending": 1}
        mock_repo.get_supplier_outreach_stats.return_value = {}
        mock_repo.get_recent_captures.return_value = sample_captures
        mock_repo.get_captures_count.return_value = 3

        result = dashboard_service.get_trade_fair_activity()

        # Only sample_captures[0] has a supplier_id
        assert result.total_suppliers_created == 1

    @patch("app.services.dashboard_service.trade_fair_repository")
    def test_recent_captures_dto_structure(self, mock_repo, dashboard_service, sample_captures):
        """Test recent captures are correctly converted to DTOs."""
        mock_repo.get_capture_stats.return_value = {"confirmed": 1}
        mock_repo.get_supplier_outreach_stats.return_value = {}
        mock_repo.get_recent_captures.return_value = sample_captures
        mock_repo.get_captures_count.return_value = 3

        result = dashboard_service.get_trade_fair_activity()

        assert len(result.recent_captures) == 3
        assert result.recent_captures[0].company_name == "Supplier A"
        assert result.recent_captures[0].status.value == "confirmed"
        assert result.recent_captures[1].company_name == "Supplier B"
        assert result.recent_captures[2].company_name is None

    @patch("app.services.dashboard_service.trade_fair_repository")
    def test_hours_parameter_passed_through(self, mock_repo, dashboard_service):
        """Test that the hours parameter affects the since calculation."""
        mock_repo.get_capture_stats.return_value = {}
        mock_repo.get_supplier_outreach_stats.return_value = {}
        mock_repo.get_recent_captures.return_value = []
        mock_repo.get_captures_count.return_value = 0

        dashboard_service.get_trade_fair_activity(hours=24)

        # Verify repository methods were called
        mock_repo.get_capture_stats.assert_called_once()
        mock_repo.get_supplier_outreach_stats.assert_called_once()
        mock_repo.get_recent_captures.assert_called_once()
        assert mock_repo.get_captures_count.call_count == 2  # today + last Xh


class TestGetTradeFairActivityErrorHandling:
    """Tests for error handling in get_trade_fair_activity."""

    @patch("app.services.dashboard_service.trade_fair_repository")
    def test_returns_empty_dto_on_exception(self, mock_repo, dashboard_service):
        """Test graceful degradation on repository exception."""
        mock_repo.get_capture_stats.side_effect = Exception("DB connection failed")

        result = dashboard_service.get_trade_fair_activity()

        assert isinstance(result, TradeFairActivityDTO)
        assert result.total_captures == 0
