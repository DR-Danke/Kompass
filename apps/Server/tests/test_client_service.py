"""Unit tests for ClientService.

Tests cover:
- CRUD operations
- Pipeline management
- Status history tracking
- Timing feasibility calculations
- Business rule enforcement
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4

import pytest

from app.models.kompass_dto import (
    ClientCreateDTO,
    ClientSource,
    ClientStatus,
    ClientStatusChangeDTO,
    ClientUpdateDTO,
)
from app.services.client_service import ClientService


# =============================================================================
# Test Fixtures
# =============================================================================


def create_mock_client(
    client_id: Optional[UUID] = None,
    company_name: str = "Test Company",
    status: str = "lead",
    with_crm_fields: bool = False,
) -> Dict[str, Any]:
    """Create a mock client dictionary for testing."""
    now = datetime.now()
    client_id = client_id or uuid4()

    client = {
        "id": client_id,
        "company_name": company_name,
        "contact_name": "John Doe",
        "email": "john@example.com",
        "phone": "+1234567890",
        "address": "123 Main St",
        "city": "New York",
        "state": "NY",
        "country": "USA",
        "postal_code": "10001",
        "niche_id": uuid4(),
        "niche_name": "Construction",
        "status": status,
        "notes": "Test notes",
        "created_at": now,
        "updated_at": now,
        "assigned_to": None,
        "assigned_to_name": None,
        "source": None,
        "project_deadline": None,
    }

    if with_crm_fields:
        client["assigned_to"] = uuid4()
        client["assigned_to_name"] = "Jane Smith"
        client["source"] = "website"
        client["project_deadline"] = (date.today() + timedelta(days=30))

    return client


def create_mock_status_history(
    client_id: Optional[UUID] = None,
    old_status: str = "lead",
    new_status: str = "qualified",
) -> Dict[str, Any]:
    """Create a mock status history entry."""
    return {
        "id": uuid4(),
        "client_id": client_id or uuid4(),
        "old_status": old_status,
        "new_status": new_status,
        "notes": "Status updated",
        "changed_by": uuid4(),
        "changed_by_name": "Admin User",
        "created_at": datetime.now(),
    }


@pytest.fixture
def mock_repository():
    """Create a mock ClientRepository."""
    return MagicMock()


@pytest.fixture
def client_service(mock_repository):
    """Create a ClientService with a mock repository."""
    return ClientService(repository=mock_repository)


# =============================================================================
# Create Client Tests
# =============================================================================


class TestCreateClient:
    """Tests for client creation."""

    def test_create_client_success(self, client_service, mock_repository):
        """Test creating a client successfully."""
        client_id = uuid4()
        mock_client = create_mock_client(client_id=client_id)
        mock_repository.create.return_value = mock_client

        request = ClientCreateDTO(
            company_name="Test Company",
            email="test@example.com",
        )

        result = client_service.create_client(request)

        assert result is not None
        assert result.company_name == "Test Company"
        mock_repository.create.assert_called_once()

    def test_create_client_with_all_fields(self, client_service, mock_repository):
        """Test creating a client with all CRM fields."""
        client_id = uuid4()
        assigned_to = uuid4()
        future_date = date.today() + timedelta(days=30)
        mock_client = create_mock_client(client_id=client_id, with_crm_fields=True)
        mock_repository.create.return_value = mock_client

        request = ClientCreateDTO(
            company_name="Test Company",
            contact_name="John Doe",
            email="john@example.com",
            assigned_to=assigned_to,
            source=ClientSource.WEBSITE,
            project_deadline=future_date,
        )

        result = client_service.create_client(request)

        assert result is not None
        mock_repository.create.assert_called_once()
        call_kwargs = mock_repository.create.call_args[1]
        assert call_kwargs["assigned_to"] == assigned_to
        assert call_kwargs["source"] == "website"
        assert call_kwargs["project_deadline"] == str(future_date)

    def test_create_client_fails_with_past_deadline(self, client_service, mock_repository):
        """Test that creating a client with past deadline fails."""
        past_date = date.today() - timedelta(days=1)

        request = ClientCreateDTO(
            company_name="Test Company",
            project_deadline=past_date,
        )

        with pytest.raises(ValueError, match="Project deadline must be in the future"):
            client_service.create_client(request)

    def test_create_client_returns_none_on_failure(self, client_service, mock_repository):
        """Test that create raises ValueError when repository fails."""
        mock_repository.create.return_value = None

        request = ClientCreateDTO(
            company_name="Test Company",
        )

        with pytest.raises(ValueError, match="Failed to create client"):
            client_service.create_client(request)


# =============================================================================
# Get Client Tests
# =============================================================================


class TestGetClient:
    """Tests for getting a client by ID."""

    def test_get_client_found(self, client_service, mock_repository):
        """Test getting a client that exists."""
        client_id = uuid4()
        mock_client = create_mock_client(client_id=client_id)
        mock_repository.get_by_id.return_value = mock_client

        result = client_service.get_client(client_id)

        assert result is not None
        assert result.id == client_id
        mock_repository.get_by_id.assert_called_once_with(client_id)

    def test_get_client_not_found(self, client_service, mock_repository):
        """Test getting a client that doesn't exist."""
        mock_repository.get_by_id.return_value = None

        result = client_service.get_client(uuid4())

        assert result is None

    def test_get_client_with_quotations(self, client_service, mock_repository):
        """Test getting a client with quotation summary."""
        client_id = uuid4()
        mock_client = create_mock_client(client_id=client_id)
        mock_repository.get_by_id.return_value = mock_client
        mock_repository.get_quotation_summary.return_value = {
            "total_quotations": 5,
            "draft_count": 1,
            "sent_count": 2,
            "accepted_count": 1,
            "rejected_count": 1,
            "expired_count": 0,
            "total_value": Decimal("10000.00"),
        }

        result = client_service.get_client_with_quotations(client_id)

        assert result is not None
        assert result.quotation_summary.total_quotations == 5
        assert result.quotation_summary.total_value == Decimal("10000.00")


# =============================================================================
# List Clients Tests
# =============================================================================


class TestListClients:
    """Tests for listing clients with filters."""

    def test_list_clients_basic(self, client_service, mock_repository):
        """Test basic client listing."""
        mock_clients = [
            create_mock_client(company_name=f"Company {i}") for i in range(5)
        ]
        mock_repository.get_all.return_value = (mock_clients, 5)

        result = client_service.list_clients()

        assert len(result.items) == 5
        assert result.pagination.total == 5

    def test_list_clients_with_pagination(self, client_service, mock_repository):
        """Test client listing with pagination."""
        mock_clients = [create_mock_client() for _ in range(10)]
        mock_repository.get_all.return_value = (mock_clients, 100)

        result = client_service.list_clients(page=2, limit=10)

        assert result.pagination.page == 2
        assert result.pagination.limit == 10
        assert result.pagination.total == 100
        assert result.pagination.pages == 10

    def test_list_clients_with_filters(self, client_service, mock_repository):
        """Test client listing with filters."""
        mock_clients = [create_mock_client()]
        mock_repository.get_all.return_value = (mock_clients, 1)

        client_service.list_clients(
            status=ClientStatus.QUALIFIED,
            source=ClientSource.WEBSITE,
            sort_by="created_at",
        )

        mock_repository.get_all.assert_called_once()
        call_kwargs = mock_repository.get_all.call_args[1]
        assert call_kwargs["status"] == "qualified"
        assert call_kwargs["source"] == "website"
        assert call_kwargs["sort_by"] == "created_at"


# =============================================================================
# Update Client Tests
# =============================================================================


class TestUpdateClient:
    """Tests for updating a client."""

    def test_update_client_success(self, client_service, mock_repository):
        """Test successful client update."""
        client_id = uuid4()
        mock_client = create_mock_client(
            client_id=client_id,
            company_name="Updated Company",
        )
        mock_repository.get_by_id.return_value = mock_client
        mock_repository.update.return_value = mock_client

        request = ClientUpdateDTO(company_name="Updated Company")
        result = client_service.update_client(client_id, request)

        assert result is not None
        assert result.company_name == "Updated Company"

    def test_update_client_not_found(self, client_service, mock_repository):
        """Test updating a client that doesn't exist."""
        mock_repository.get_by_id.return_value = None

        request = ClientUpdateDTO(company_name="Updated Company")
        result = client_service.update_client(uuid4(), request)

        assert result is None

    def test_update_client_fails_with_past_deadline(self, client_service, mock_repository):
        """Test that updating with past deadline fails."""
        client_id = uuid4()
        mock_client = create_mock_client(client_id=client_id)
        mock_repository.get_by_id.return_value = mock_client

        past_date = date.today() - timedelta(days=1)
        request = ClientUpdateDTO(project_deadline=past_date)

        with pytest.raises(ValueError, match="Project deadline must be in the future"):
            client_service.update_client(client_id, request)


# =============================================================================
# Delete Client Tests
# =============================================================================


class TestDeleteClient:
    """Tests for deleting a client."""

    def test_delete_client_success(self, client_service, mock_repository):
        """Test successful client deletion."""
        client_id = uuid4()
        mock_client = create_mock_client(client_id=client_id)
        mock_repository.get_by_id.return_value = mock_client
        mock_repository.has_active_quotations.return_value = False
        mock_repository.delete.return_value = True

        result = client_service.delete_client(client_id)

        assert result is True
        mock_repository.delete.assert_called_once_with(client_id)

    def test_delete_client_not_found(self, client_service, mock_repository):
        """Test deleting a client that doesn't exist."""
        mock_repository.get_by_id.return_value = None

        result = client_service.delete_client(uuid4())

        assert result is False

    def test_delete_client_with_active_quotations_fails(
        self, client_service, mock_repository
    ):
        """Test that deleting a client with active quotations fails."""
        client_id = uuid4()
        mock_client = create_mock_client(client_id=client_id)
        mock_repository.get_by_id.return_value = mock_client
        mock_repository.has_active_quotations.return_value = True

        with pytest.raises(ValueError, match="Cannot delete client with active quotations"):
            client_service.delete_client(client_id)


# =============================================================================
# Pipeline Tests
# =============================================================================


class TestPipeline:
    """Tests for pipeline operations."""

    def test_get_pipeline_groups_by_status(self, client_service, mock_repository):
        """Test that pipeline groups clients by status."""
        lead_clients = [create_mock_client(status="lead") for _ in range(3)]
        qualified_clients = [create_mock_client(status="qualified") for _ in range(2)]
        quoting_clients = [create_mock_client(status="quoting") for _ in range(1)]
        negotiating_clients = [create_mock_client(status="negotiating") for _ in range(2)]
        won_clients = [create_mock_client(status="won") for _ in range(1)]
        lost_clients = [create_mock_client(status="lost") for _ in range(1)]

        mock_repository.get_by_status.side_effect = lambda status: {
            "lead": lead_clients,
            "qualified": qualified_clients,
            "quoting": quoting_clients,
            "negotiating": negotiating_clients,
            "won": won_clients,
            "lost": lost_clients,
        }[status]

        result = client_service.get_pipeline()

        assert len(result.lead) == 3
        assert len(result.qualified) == 2
        assert len(result.quoting) == 1
        assert len(result.negotiating) == 2
        assert len(result.won) == 1
        assert len(result.lost) == 1

    def test_update_status_records_history(self, client_service, mock_repository):
        """Test that status update records history."""
        client_id = uuid4()
        user_id = uuid4()
        mock_client = create_mock_client(client_id=client_id, status="lead")
        updated_client = create_mock_client(client_id=client_id, status="qualified")

        mock_repository.get_by_id.return_value = mock_client
        mock_repository.update.return_value = updated_client
        mock_repository.create_status_history.return_value = create_mock_status_history(
            client_id=client_id
        )

        request = ClientStatusChangeDTO(
            new_status=ClientStatus.QUALIFIED,
            notes="Client qualified for next stage",
        )

        result = client_service.update_status(client_id, request, user_id)

        assert result is not None
        mock_repository.create_status_history.assert_called_once()
        call_kwargs = mock_repository.create_status_history.call_args[1]
        assert call_kwargs["client_id"] == client_id
        assert call_kwargs["old_status"] == "lead"
        assert call_kwargs["new_status"] == "qualified"
        assert call_kwargs["notes"] == "Client qualified for next stage"
        assert call_kwargs["changed_by"] == user_id

    def test_get_status_history(self, client_service, mock_repository):
        """Test getting status history for a client."""
        client_id = uuid4()
        mock_client = create_mock_client(client_id=client_id)
        mock_history = [
            create_mock_status_history(client_id=client_id, old_status="lead", new_status="qualified"),
            create_mock_status_history(client_id=client_id, old_status=None, new_status="lead"),
        ]

        mock_repository.get_by_id.return_value = mock_client
        mock_repository.get_status_history.return_value = mock_history

        result = client_service.get_status_history(client_id)

        assert len(result) == 2
        assert result[0].new_status == ClientStatus.QUALIFIED
        assert result[1].new_status == ClientStatus.LEAD


# =============================================================================
# Timing Feasibility Tests
# =============================================================================


class TestTimingFeasibility:
    """Tests for timing feasibility calculations."""

    def test_timing_feasibility_calculation_feasible(
        self, client_service, mock_repository
    ):
        """Test timing feasibility when deadline is achievable."""
        client_id = uuid4()
        future_deadline = date.today() + timedelta(days=60)
        mock_client = create_mock_client(client_id=client_id)
        mock_client["project_deadline"] = future_deadline
        mock_client["country"] = "USA"

        mock_repository.get_by_id.return_value = mock_client

        with patch.object(client_service, "_get_shipping_transit_days", return_value=20):
            result = client_service.calculate_timing_feasibility(
                client_id=client_id,
                product_lead_time_days=14,
            )

        assert result is not None
        assert result.is_feasible is True
        assert result.production_lead_time_days == 14
        assert result.shipping_transit_days == 20
        assert result.total_lead_time_days == 34
        assert result.buffer_days is not None
        assert result.buffer_days > 0

    def test_timing_feasibility_calculation_not_feasible(
        self, client_service, mock_repository
    ):
        """Test timing feasibility when deadline is not achievable."""
        client_id = uuid4()
        tight_deadline = date.today() + timedelta(days=10)
        mock_client = create_mock_client(client_id=client_id)
        mock_client["project_deadline"] = tight_deadline
        mock_client["country"] = "USA"

        mock_repository.get_by_id.return_value = mock_client

        with patch.object(client_service, "_get_shipping_transit_days", return_value=20):
            result = client_service.calculate_timing_feasibility(
                client_id=client_id,
                product_lead_time_days=14,
            )

        assert result is not None
        assert result.is_feasible is False
        assert result.buffer_days is not None
        assert result.buffer_days < 0

    def test_timing_feasibility_no_deadline(self, client_service, mock_repository):
        """Test timing feasibility when no deadline is set."""
        client_id = uuid4()
        mock_client = create_mock_client(client_id=client_id)
        mock_client["project_deadline"] = None

        mock_repository.get_by_id.return_value = mock_client

        result = client_service.calculate_timing_feasibility(
            client_id=client_id,
            product_lead_time_days=14,
        )

        assert result is not None
        assert result.is_feasible is True
        assert "flexible" in result.message.lower()


# =============================================================================
# Search Tests
# =============================================================================


class TestSearchClients:
    """Tests for client search."""

    def test_search_clients_by_company_name(self, client_service, mock_repository):
        """Test searching clients by company name."""
        mock_clients = [
            create_mock_client(company_name="ABC Corp"),
            create_mock_client(company_name="ABC Industries"),
        ]
        mock_repository.search.return_value = mock_clients

        results = client_service.search_clients("ABC")

        assert len(results) == 2
        mock_repository.search.assert_called_once_with(query="ABC", limit=50)

    def test_search_clients_empty_query(self, client_service, mock_repository):
        """Test search with empty query returns empty list."""
        results = client_service.search_clients("")

        assert results == []
        mock_repository.search.assert_not_called()

    def test_search_clients_short_query(self, client_service, mock_repository):
        """Test search with query too short returns empty list."""
        results = client_service.search_clients("A")

        assert results == []
        mock_repository.search.assert_not_called()


# =============================================================================
# DTO Mapping Tests
# =============================================================================


class TestDTOMapping:
    """Tests for DTO mapping."""

    def test_map_to_response_dto_complete(self, client_service, mock_repository):
        """Test mapping a complete client to response DTO."""
        mock_client = create_mock_client(with_crm_fields=True)

        result = client_service._map_to_response_dto(mock_client)

        assert result.id == mock_client["id"]
        assert result.company_name == mock_client["company_name"]
        assert result.status == ClientStatus.LEAD
        assert result.assigned_to == mock_client["assigned_to"]
        assert result.source == ClientSource.WEBSITE

    def test_map_to_response_dto_minimal(self, client_service, mock_repository):
        """Test mapping a minimal client to response DTO."""
        mock_client = create_mock_client()

        result = client_service._map_to_response_dto(mock_client)

        assert result.id == mock_client["id"]
        assert result.assigned_to is None
        assert result.source is None
        assert result.project_deadline is None
