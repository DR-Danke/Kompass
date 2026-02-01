"""Unit tests for niche API routes."""

from datetime import datetime
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
def mock_niche():
    """Sample niche data."""
    return {
        "id": uuid4(),
        "name": "Constructoras",
        "description": "Construction companies",
        "is_active": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }


@pytest.fixture
def mock_niche_response(mock_niche):
    """Sample niche response DTO."""
    from app.models.kompass_dto import NicheResponseDTO

    return NicheResponseDTO(**mock_niche)


@pytest.fixture
def mock_niche_with_count(mock_niche):
    """Sample niche with count DTO."""
    from app.models.kompass_dto import NicheWithClientCountDTO

    return NicheWithClientCountDTO(
        id=mock_niche["id"],
        name=mock_niche["name"],
        description=mock_niche["description"],
        is_active=mock_niche["is_active"],
        client_count=5,
        created_at=mock_niche["created_at"],
        updated_at=mock_niche["updated_at"],
    )


class TestListNiches:
    """Tests for GET /api/niches."""

    @patch("app.api.niche_routes.niche_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_list_niches_returns_with_counts(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_niche_service,
        client,
        mock_user,
        mock_niche_with_count,
    ):
        """Test listing niches returns niches with client counts."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_niche_service.list_niches.return_value = [mock_niche_with_count]

        response = client.get(
            "/api/niches/",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Constructoras"
        assert data[0]["client_count"] == 5

    def test_list_niches_requires_auth(self, client):
        """Test listing niches requires authentication."""
        response = client.get("/api/niches/")

        # FastAPI returns 403 when HTTPBearer credentials are not provided
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]

    @patch("app.api.niche_routes.niche_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_list_niches_empty(
        self, mock_user_repo, mock_auth_service, mock_niche_service, client, mock_user
    ):
        """Test listing niches returns empty list when none exist."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_niche_service.list_niches.return_value = []

        response = client.get(
            "/api/niches/",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data == []


class TestCreateNiche:
    """Tests for POST /api/niches."""

    @patch("app.api.niche_routes.niche_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_create_niche_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_niche_service,
        client,
        mock_user,
        mock_niche_response,
    ):
        """Test creating a niche successfully."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_niche_service.create_niche.return_value = mock_niche_response

        response = client.post(
            "/api/niches/",
            json={
                "name": "Constructoras",
                "description": "Construction companies",
                "is_active": True,
            },
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Constructoras"
        assert data["description"] == "Construction companies"

    @patch("app.api.niche_routes.niche_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_create_niche_failure_returns_400(
        self, mock_user_repo, mock_auth_service, mock_niche_service, client, mock_user
    ):
        """Test niche creation failure returns 400."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_niche_service.create_niche.return_value = None

        response = client.post(
            "/api/niches/",
            json={"name": "Failed"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestGetNiche:
    """Tests for GET /api/niches/{niche_id}."""

    @patch("app.api.niche_routes.niche_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_get_niche_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_niche_service,
        client,
        mock_user,
        mock_niche_with_count,
    ):
        """Test getting a niche by ID."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_niche_service.get_niche.return_value = mock_niche_with_count

        response = client.get(
            f"/api/niches/{mock_niche_with_count.id}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Constructoras"
        assert data["client_count"] == 5

    @patch("app.api.niche_routes.niche_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_get_niche_not_found_returns_404(
        self, mock_user_repo, mock_auth_service, mock_niche_service, client, mock_user
    ):
        """Test getting non-existent niche returns 404."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_niche_service.get_niche.return_value = None

        response = client.get(
            f"/api/niches/{uuid4()}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateNiche:
    """Tests for PUT /api/niches/{niche_id}."""

    @patch("app.api.niche_routes.niche_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_update_niche_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_niche_service,
        client,
        mock_admin_user,
        mock_niche_with_count,
        mock_niche_response,
    ):
        """Test updating a niche successfully."""
        mock_auth_service.decode_access_token.return_value = {
            "sub": mock_admin_user["id"]
        }
        mock_user_repo.get_user_by_id.return_value = mock_admin_user
        mock_niche_service.get_niche.return_value = mock_niche_with_count
        mock_niche_service.update_niche.return_value = mock_niche_response

        response = client.put(
            f"/api/niches/{mock_niche_response.id}",
            json={"name": "Updated Name"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK

    @patch("app.api.niche_routes.niche_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_update_niche_requires_admin_or_manager(
        self, mock_user_repo, mock_auth_service, mock_niche_service, client, mock_user
    ):
        """Test update requires admin or manager role."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user

        response = client.put(
            f"/api/niches/{uuid4()}",
            json={"name": "New Name"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @patch("app.api.niche_routes.niche_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_update_niche_not_found_returns_404(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_niche_service,
        client,
        mock_admin_user,
    ):
        """Test updating non-existent niche returns 404."""
        mock_auth_service.decode_access_token.return_value = {
            "sub": mock_admin_user["id"]
        }
        mock_user_repo.get_user_by_id.return_value = mock_admin_user
        mock_niche_service.get_niche.return_value = None

        response = client.put(
            f"/api/niches/{uuid4()}",
            json={"name": "New Name"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch("app.api.niche_routes.niche_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_update_niche_manager_allowed(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_niche_service,
        client,
        mock_manager_user,
        mock_niche_with_count,
        mock_niche_response,
    ):
        """Test manager role can update niches."""
        mock_auth_service.decode_access_token.return_value = {
            "sub": mock_manager_user["id"]
        }
        mock_user_repo.get_user_by_id.return_value = mock_manager_user
        mock_niche_service.get_niche.return_value = mock_niche_with_count
        mock_niche_service.update_niche.return_value = mock_niche_response

        response = client.put(
            f"/api/niches/{mock_niche_response.id}",
            json={"name": "Updated Name"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK


class TestDeleteNiche:
    """Tests for DELETE /api/niches/{niche_id}."""

    @patch("app.api.niche_routes.niche_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_delete_niche_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_niche_service,
        client,
        mock_admin_user,
        mock_niche_with_count,
    ):
        """Test deleting a niche successfully."""
        mock_auth_service.decode_access_token.return_value = {
            "sub": mock_admin_user["id"]
        }
        mock_user_repo.get_user_by_id.return_value = mock_admin_user
        mock_niche_service.get_niche.return_value = mock_niche_with_count
        mock_niche_service.delete_niche.return_value = True

        response = client.delete(
            f"/api/niches/{mock_niche_with_count.id}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    @patch("app.api.niche_routes.niche_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_delete_niche_not_found_returns_404(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_niche_service,
        client,
        mock_admin_user,
    ):
        """Test deleting non-existent niche returns 404."""
        mock_auth_service.decode_access_token.return_value = {
            "sub": mock_admin_user["id"]
        }
        mock_user_repo.get_user_by_id.return_value = mock_admin_user
        mock_niche_service.get_niche.return_value = None

        response = client.delete(
            f"/api/niches/{uuid4()}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch("app.api.niche_routes.niche_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_delete_niche_requires_admin_or_manager(
        self, mock_user_repo, mock_auth_service, mock_niche_service, client, mock_user
    ):
        """Test delete requires admin or manager role."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user

        response = client.delete(
            f"/api/niches/{uuid4()}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @patch("app.api.niche_routes.niche_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_delete_niche_manager_allowed(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_niche_service,
        client,
        mock_manager_user,
        mock_niche_with_count,
    ):
        """Test manager role can delete niches."""
        mock_auth_service.decode_access_token.return_value = {
            "sub": mock_manager_user["id"]
        }
        mock_user_repo.get_user_by_id.return_value = mock_manager_user
        mock_niche_service.get_niche.return_value = mock_niche_with_count
        mock_niche_service.delete_niche.return_value = True

        response = client.delete(
            f"/api/niches/{mock_niche_with_count.id}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    @patch("app.api.niche_routes.niche_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_delete_niche_with_clients_returns_409(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_niche_service,
        client,
        mock_admin_user,
        mock_niche_with_count,
    ):
        """Test deleting niche with clients returns 409 conflict."""
        mock_auth_service.decode_access_token.return_value = {
            "sub": mock_admin_user["id"]
        }
        mock_user_repo.get_user_by_id.return_value = mock_admin_user
        mock_niche_service.get_niche.return_value = mock_niche_with_count
        mock_niche_service.delete_niche.side_effect = ValueError(
            "Cannot delete niche with associated clients"
        )

        response = client.delete(
            f"/api/niches/{mock_niche_with_count.id}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_409_CONFLICT
        assert "Cannot delete niche with associated clients" in response.json()["detail"]
