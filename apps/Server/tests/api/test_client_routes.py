"""Unit tests for client API routes."""

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def mock_user():
    """Sample user data for authentication."""
    return {
        "id": str(uuid4()),
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "role": "user",
        "is_active": True,
    }


@pytest.fixture
def mock_admin_user():
    """Sample admin user data for authorization."""
    return {
        "id": str(uuid4()),
        "email": "admin@example.com",
        "first_name": "Admin",
        "last_name": "User",
        "role": "admin",
        "is_active": True,
    }


@pytest.fixture
def mock_manager_user():
    """Sample manager user data for authorization."""
    return {
        "id": str(uuid4()),
        "email": "manager@example.com",
        "first_name": "Manager",
        "last_name": "User",
        "role": "manager",
        "is_active": True,
    }


@pytest.fixture
def mock_client_data():
    """Sample client data."""
    return {
        "id": uuid4(),
        "company_name": "Test Company",
        "contact_name": "John Doe",
        "email": "john@testcompany.com",
        "phone": "+1234567890",
        "country": "USA",
        "city": "New York",
        "status": "lead",
        "source": "website",
        "niche_id": uuid4(),
        "assigned_to": uuid4(),
        "project_deadline": date.today(),
        "notes": "Test notes",
        "is_active": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }


@pytest.fixture
def mock_client_response(mock_client_data):
    """Sample client response DTO."""
    from app.models.kompass_dto import ClientResponseDTO

    return ClientResponseDTO(**mock_client_data)


@pytest.fixture
def mock_client_list_response(mock_client_response):
    """Sample client list response DTO."""
    from app.models.kompass_dto import ClientListResponseDTO, PaginationDTO

    return ClientListResponseDTO(
        items=[mock_client_response],
        pagination=PaginationDTO(page=1, limit=20, total=1, pages=1),
    )


@pytest.fixture
def mock_pipeline_response(mock_client_response):
    """Sample pipeline response DTO."""
    from app.models.kompass_dto import PipelineResponseDTO

    return PipelineResponseDTO(
        lead=[mock_client_response],
        qualified=[],
        quoting=[],
        negotiating=[],
        won=[],
        lost=[],
    )


@pytest.fixture
def mock_status_history():
    """Sample status history data."""
    from app.models.kompass_dto import StatusHistoryResponseDTO

    return [
        StatusHistoryResponseDTO(
            id=uuid4(),
            client_id=uuid4(),
            old_status="lead",
            new_status="qualified",
            notes="Converted to qualified",
            changed_by=uuid4(),
            created_at=datetime.now(),
        )
    ]


@pytest.fixture
def mock_client_with_quotations(mock_client_data):
    """Sample client with quotations DTO."""
    from app.models.kompass_dto import ClientWithQuotationsDTO, QuotationSummaryDTO

    return ClientWithQuotationsDTO(
        id=mock_client_data["id"],
        company_name=mock_client_data["company_name"],
        contact_name=mock_client_data["contact_name"],
        email=mock_client_data["email"],
        phone=mock_client_data["phone"],
        city=mock_client_data["city"],
        country=mock_client_data["country"],
        status=mock_client_data["status"],
        notes=mock_client_data["notes"],
        niche_id=mock_client_data["niche_id"],
        assigned_to=mock_client_data["assigned_to"],
        source=mock_client_data["source"],
        project_deadline=mock_client_data["project_deadline"],
        created_at=mock_client_data["created_at"],
        updated_at=mock_client_data["updated_at"],
        quotation_summary=QuotationSummaryDTO(
            total_quotations=5,
            draft_count=0,
            sent_count=0,
            accepted_count=2,
            rejected_count=0,
            expired_count=0,
            total_value=Decimal("10000.00"),
        ),
    )


class TestListClients:
    """Tests for GET /api/clients."""

    @patch("app.api.client_routes.client_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_list_clients_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_client_service,
        client,
        mock_user,
        mock_client_list_response,
    ):
        """Test listing clients returns paginated list."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_client_service.list_clients.return_value = mock_client_list_response

        response = client.get(
            "/api/clients",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert data["pagination"]["total"] == 1
        assert data["pagination"]["page"] == 1

    def test_list_clients_requires_auth(self, client):
        """Test listing clients requires authentication."""
        response = client.get("/api/clients")

        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]

    @patch("app.api.client_routes.client_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_list_clients_with_status_filter(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_client_service,
        client,
        mock_user,
        mock_client_list_response,
    ):
        """Test listing clients with status filter."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_client_service.list_clients.return_value = mock_client_list_response

        response = client.get(
            "/api/clients?status=lead",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK

    @patch("app.api.client_routes.client_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_list_clients_invalid_status_returns_400(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_client_service,
        client,
        mock_user,
    ):
        """Test listing clients with invalid status returns 400."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user

        response = client.get(
            "/api/clients?status=invalid_status",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch("app.api.client_routes.client_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_list_clients_empty(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_client_service,
        client,
        mock_user,
    ):
        """Test listing clients returns empty list when none exist."""
        from app.models.kompass_dto import ClientListResponseDTO, PaginationDTO

        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_client_service.list_clients.return_value = ClientListResponseDTO(
            items=[], pagination=PaginationDTO(page=1, limit=20, total=0, pages=0)
        )

        response = client.get(
            "/api/clients",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["items"] == []
        assert data["pagination"]["total"] == 0


class TestCreateClient:
    """Tests for POST /api/clients."""

    @patch("app.api.client_routes.client_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_create_client_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_client_service,
        client,
        mock_user,
        mock_client_response,
    ):
        """Test creating a client successfully."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_client_service.create_client.return_value = mock_client_response

        response = client.post(
            "/api/clients",
            json={
                "company_name": "Test Company",
                "contact_name": "John Doe",
                "email": "john@test.com",
            },
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["company_name"] == "Test Company"

    @patch("app.api.client_routes.client_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_create_client_validation_error_returns_400(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_client_service,
        client,
        mock_user,
    ):
        """Test client creation validation failure returns 400."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_client_service.create_client.side_effect = ValueError("Validation error")

        response = client.post(
            "/api/clients",
            json={
                "company_name": "Test Company",
                "contact_name": "John Doe",
                "email": "john@test.com",
            },
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestGetClient:
    """Tests for GET /api/clients/{client_id}."""

    @patch("app.api.client_routes.client_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_get_client_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_client_service,
        client,
        mock_user,
        mock_client_response,
    ):
        """Test getting a client by ID."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_client_service.get_client.return_value = mock_client_response

        response = client.get(
            f"/api/clients/{mock_client_response.id}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["company_name"] == "Test Company"

    @patch("app.api.client_routes.client_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_get_client_not_found_returns_404(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_client_service,
        client,
        mock_user,
    ):
        """Test getting non-existent client returns 404."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_client_service.get_client.return_value = None

        response = client.get(
            f"/api/clients/{uuid4()}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateClient:
    """Tests for PUT /api/clients/{client_id}."""

    @patch("app.api.client_routes.client_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_update_client_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_client_service,
        client,
        mock_user,
        mock_client_response,
    ):
        """Test updating a client successfully."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_client_service.update_client.return_value = mock_client_response

        response = client.put(
            f"/api/clients/{mock_client_response.id}",
            json={"company_name": "Updated Company"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK

    @patch("app.api.client_routes.client_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_update_client_not_found_returns_404(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_client_service,
        client,
        mock_user,
    ):
        """Test updating non-existent client returns 404."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_client_service.update_client.return_value = None

        response = client.put(
            f"/api/clients/{uuid4()}",
            json={"company_name": "Updated Company"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch("app.api.client_routes.client_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_update_client_validation_error_returns_400(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_client_service,
        client,
        mock_user,
    ):
        """Test client update validation failure returns 400."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_client_service.update_client.side_effect = ValueError("Validation error")

        response = client.put(
            f"/api/clients/{uuid4()}",
            json={"company_name": "Updated Company"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestDeleteClient:
    """Tests for DELETE /api/clients/{client_id}."""

    @patch("app.api.client_routes.client_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_delete_client_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_client_service,
        client,
        mock_admin_user,
        mock_client_response,
    ):
        """Test deleting a client successfully."""
        mock_auth_service.decode_access_token.return_value = {
            "sub": mock_admin_user["id"]
        }
        mock_user_repo.get_user_by_id.return_value = mock_admin_user
        mock_client_service.delete_client.return_value = True

        response = client.delete(
            f"/api/clients/{mock_client_response.id}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Client deleted successfully"

    @patch("app.api.client_routes.client_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_delete_client_not_found_returns_404(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_client_service,
        client,
        mock_admin_user,
    ):
        """Test deleting non-existent client returns 404."""
        mock_auth_service.decode_access_token.return_value = {
            "sub": mock_admin_user["id"]
        }
        mock_user_repo.get_user_by_id.return_value = mock_admin_user
        mock_client_service.delete_client.return_value = False

        response = client.delete(
            f"/api/clients/{uuid4()}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch("app.api.client_routes.client_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_delete_client_requires_admin_or_manager(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_client_service,
        client,
        mock_user,
    ):
        """Test delete requires admin or manager role."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user

        response = client.delete(
            f"/api/clients/{uuid4()}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @patch("app.api.client_routes.client_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_delete_client_manager_allowed(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_client_service,
        client,
        mock_manager_user,
        mock_client_response,
    ):
        """Test manager role can delete clients."""
        mock_auth_service.decode_access_token.return_value = {
            "sub": mock_manager_user["id"]
        }
        mock_user_repo.get_user_by_id.return_value = mock_manager_user
        mock_client_service.delete_client.return_value = True

        response = client.delete(
            f"/api/clients/{mock_client_response.id}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK

    @patch("app.api.client_routes.client_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_delete_client_with_active_quotations_returns_400(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_client_service,
        client,
        mock_admin_user,
    ):
        """Test deleting client with active quotations returns 400."""
        mock_auth_service.decode_access_token.return_value = {
            "sub": mock_admin_user["id"]
        }
        mock_user_repo.get_user_by_id.return_value = mock_admin_user
        mock_client_service.delete_client.side_effect = ValueError(
            "Cannot delete client with active quotations"
        )

        response = client.delete(
            f"/api/clients/{uuid4()}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Cannot delete client with active quotations" in response.json()["detail"]


class TestGetPipeline:
    """Tests for GET /api/clients/pipeline."""

    @patch("app.api.client_routes.client_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_get_pipeline_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_client_service,
        client,
        mock_user,
        mock_pipeline_response,
    ):
        """Test getting pipeline returns grouped clients."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_client_service.get_pipeline.return_value = mock_pipeline_response

        response = client.get(
            "/api/clients/pipeline",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "lead" in data
        assert "qualified" in data
        assert "quoting" in data
        assert "negotiating" in data
        assert "won" in data
        assert "lost" in data

    @patch("app.api.client_routes.client_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_get_pipeline_empty(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_client_service,
        client,
        mock_user,
    ):
        """Test getting pipeline with no clients."""
        from app.models.kompass_dto import PipelineResponseDTO

        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_client_service.get_pipeline.return_value = PipelineResponseDTO(
            lead=[], qualified=[], quoting=[], negotiating=[], won=[], lost=[]
        )

        response = client.get(
            "/api/clients/pipeline",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["lead"] == []
        assert data["qualified"] == []
        assert data["quoting"] == []
        assert data["negotiating"] == []
        assert data["won"] == []
        assert data["lost"] == []


class TestUpdateClientStatus:
    """Tests for PUT /api/clients/{client_id}/status."""

    @patch("app.api.client_routes.client_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_update_status_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_client_service,
        client,
        mock_user,
        mock_client_response,
    ):
        """Test updating client status successfully."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_client_service.update_status.return_value = mock_client_response

        response = client.put(
            f"/api/clients/{mock_client_response.id}/status",
            json={"new_status": "qualified", "notes": "Converted to qualified"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK

    @patch("app.api.client_routes.client_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_update_status_not_found_returns_404(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_client_service,
        client,
        mock_user,
    ):
        """Test updating status for non-existent client returns 404."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_client_service.update_status.return_value = None

        response = client.put(
            f"/api/clients/{uuid4()}/status",
            json={"new_status": "qualified"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch("app.api.client_routes.client_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_update_status_validation_error_returns_400(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_client_service,
        client,
        mock_user,
    ):
        """Test status update validation failure returns 400."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_client_service.update_status.side_effect = ValueError("Invalid status")

        response = client.put(
            f"/api/clients/{uuid4()}/status",
            json={"new_status": "qualified"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestGetStatusHistory:
    """Tests for GET /api/clients/{client_id}/status-history."""

    @patch("app.api.client_routes.client_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_get_status_history_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_client_service,
        client,
        mock_user,
        mock_client_response,
        mock_status_history,
    ):
        """Test getting status history successfully."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_client_service.get_client.return_value = mock_client_response
        mock_client_service.get_status_history.return_value = mock_status_history

        response = client.get(
            f"/api/clients/{mock_client_response.id}/status-history",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["new_status"] == "qualified"

    @patch("app.api.client_routes.client_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_get_status_history_not_found_returns_404(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_client_service,
        client,
        mock_user,
    ):
        """Test getting status history for non-existent client returns 404."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_client_service.get_client.return_value = None

        response = client.get(
            f"/api/clients/{uuid4()}/status-history",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch("app.api.client_routes.client_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_get_status_history_empty(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_client_service,
        client,
        mock_user,
        mock_client_response,
    ):
        """Test getting empty status history."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_client_service.get_client.return_value = mock_client_response
        mock_client_service.get_status_history.return_value = []

        response = client.get(
            f"/api/clients/{mock_client_response.id}/status-history",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data == []


class TestGetClientHistory:
    """Tests for GET /api/clients/{client_id}/history (alias endpoint)."""

    @patch("app.api.client_routes.client_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_get_client_history_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_client_service,
        client,
        mock_user,
        mock_client_response,
        mock_status_history,
    ):
        """Test getting client history via alias endpoint."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_client_service.get_client.return_value = mock_client_response
        mock_client_service.get_status_history.return_value = mock_status_history

        response = client.get(
            f"/api/clients/{mock_client_response.id}/history",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1

    @patch("app.api.client_routes.client_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_get_client_history_not_found_returns_404(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_client_service,
        client,
        mock_user,
    ):
        """Test getting history via alias for non-existent client returns 404."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_client_service.get_client.return_value = None

        response = client.get(
            f"/api/clients/{uuid4()}/history",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGetClientWithQuotations:
    """Tests for GET /api/clients/{client_id}/quotations."""

    @patch("app.api.client_routes.client_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_get_client_with_quotations_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_client_service,
        client,
        mock_user,
        mock_client_with_quotations,
    ):
        """Test getting client with quotations summary."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_client_service.get_client_with_quotations.return_value = (
            mock_client_with_quotations
        )

        response = client.get(
            f"/api/clients/{mock_client_with_quotations.id}/quotations",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["quotation_summary"]["total_quotations"] == 5
        assert data["quotation_summary"]["accepted_count"] == 2

    @patch("app.api.client_routes.client_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_get_client_with_quotations_not_found_returns_404(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_client_service,
        client,
        mock_user,
    ):
        """Test getting quotations for non-existent client returns 404."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_client_service.get_client_with_quotations.return_value = None

        response = client.get(
            f"/api/clients/{uuid4()}/quotations",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
