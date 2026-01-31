"""Unit tests for tag API routes."""

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
def mock_tag():
    """Sample tag data."""
    return {
        "id": uuid4(),
        "name": "Trending",
        "color": "#FF5733",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }


@pytest.fixture
def mock_tag_response(mock_tag):
    """Sample tag response DTO."""
    from app.models.kompass_dto import TagResponseDTO

    return TagResponseDTO(**mock_tag)


@pytest.fixture
def mock_tag_with_count(mock_tag):
    """Sample tag with count DTO."""
    from app.models.kompass_dto import TagWithCountDTO

    return TagWithCountDTO(
        id=mock_tag["id"],
        name=mock_tag["name"],
        color=mock_tag["color"],
        product_count=5,
        created_at=mock_tag["created_at"],
        updated_at=mock_tag["updated_at"],
    )


class TestListTags:
    """Tests for GET /api/tags."""

    @patch("app.api.tag_routes.tag_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_list_tags_returns_with_counts(
        self, mock_user_repo, mock_auth_service, mock_tag_service, client, mock_user, mock_tag_with_count
    ):
        """Test listing tags returns tags with product counts."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_tag_service.list_tags.return_value = [mock_tag_with_count]

        response = client.get(
            "/api/tags/",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Trending"
        assert data[0]["product_count"] == 5

    def test_list_tags_requires_auth(self, client):
        """Test listing tags requires authentication."""
        response = client.get("/api/tags/")

        # FastAPI returns 403 when HTTPBearer credentials are not provided
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


class TestSearchTags:
    """Tests for GET /api/tags/search."""

    @patch("app.api.tag_routes.tag_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_search_tags_success(
        self, mock_user_repo, mock_auth_service, mock_tag_service, client, mock_user, mock_tag_response
    ):
        """Test searching tags for autocomplete."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_tag_service.search_tags.return_value = [mock_tag_response]

        response = client.get(
            "/api/tags/search?query=trend",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Trending"

    @patch("app.api.tag_routes.tag_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_search_tags_with_limit(
        self, mock_user_repo, mock_auth_service, mock_tag_service, client, mock_user
    ):
        """Test searching tags with custom limit."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_tag_service.search_tags.return_value = []

        response = client.get(
            "/api/tags/search?query=test&limit=5",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        mock_tag_service.search_tags.assert_called_once_with("test", 5)

    @patch("app.api.tag_routes.tag_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_search_tags_empty_results(
        self, mock_user_repo, mock_auth_service, mock_tag_service, client, mock_user
    ):
        """Test searching tags with no results."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_tag_service.search_tags.return_value = []

        response = client.get(
            "/api/tags/search?query=xyz",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data == []


class TestCreateTag:
    """Tests for POST /api/tags."""

    @patch("app.api.tag_routes.tag_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_create_tag_success(
        self, mock_user_repo, mock_auth_service, mock_tag_service, client, mock_user, mock_tag_response
    ):
        """Test creating a tag successfully."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_tag_service.create_tag.return_value = mock_tag_response

        response = client.post(
            "/api/tags/",
            json={"name": "Trending", "color": "#FF5733"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Trending"
        assert data["color"] == "#FF5733"

    @patch("app.api.tag_routes.tag_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_create_tag_failure_returns_400(
        self, mock_user_repo, mock_auth_service, mock_tag_service, client, mock_user
    ):
        """Test tag creation failure returns 400."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_tag_service.create_tag.return_value = None

        response = client.post(
            "/api/tags/",
            json={"name": "Failed"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestGetTag:
    """Tests for GET /api/tags/{tag_id}."""

    @patch("app.api.tag_routes.tag_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_get_tag_success(
        self, mock_user_repo, mock_auth_service, mock_tag_service, client, mock_user, mock_tag_with_count
    ):
        """Test getting a tag by ID."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_tag_service.get_tag.return_value = mock_tag_with_count

        response = client.get(
            f"/api/tags/{mock_tag_with_count.id}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Trending"
        assert data["product_count"] == 5

    @patch("app.api.tag_routes.tag_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_get_tag_not_found_returns_404(
        self, mock_user_repo, mock_auth_service, mock_tag_service, client, mock_user
    ):
        """Test getting non-existent tag returns 404."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_tag_service.get_tag.return_value = None

        response = client.get(
            f"/api/tags/{uuid4()}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateTag:
    """Tests for PUT /api/tags/{tag_id}."""

    @patch("app.api.tag_routes.tag_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_update_tag_success(
        self, mock_user_repo, mock_auth_service, mock_tag_service, client, mock_admin_user, mock_tag_with_count, mock_tag_response
    ):
        """Test updating a tag successfully."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_admin_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_admin_user
        mock_tag_service.get_tag.return_value = mock_tag_with_count
        mock_tag_service.update_tag.return_value = mock_tag_response

        response = client.put(
            f"/api/tags/{mock_tag_response.id}",
            json={"name": "Hot"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK

    @patch("app.api.tag_routes.tag_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_update_tag_requires_admin_or_manager(
        self, mock_user_repo, mock_auth_service, mock_tag_service, client, mock_user
    ):
        """Test update requires admin or manager role."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user

        response = client.put(
            f"/api/tags/{uuid4()}",
            json={"name": "Hot"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @patch("app.api.tag_routes.tag_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_update_tag_not_found_returns_404(
        self, mock_user_repo, mock_auth_service, mock_tag_service, client, mock_admin_user
    ):
        """Test updating non-existent tag returns 404."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_admin_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_admin_user
        mock_tag_service.get_tag.return_value = None

        response = client.put(
            f"/api/tags/{uuid4()}",
            json={"name": "Hot"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteTag:
    """Tests for DELETE /api/tags/{tag_id}."""

    @patch("app.api.tag_routes.tag_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_delete_tag_success(
        self, mock_user_repo, mock_auth_service, mock_tag_service, client, mock_admin_user
    ):
        """Test deleting a tag successfully."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_admin_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_admin_user
        mock_tag_service.delete_tag.return_value = True

        response = client.delete(
            f"/api/tags/{uuid4()}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    @patch("app.api.tag_routes.tag_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_delete_tag_not_found_returns_404(
        self, mock_user_repo, mock_auth_service, mock_tag_service, client, mock_admin_user
    ):
        """Test deleting non-existent tag returns 404."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_admin_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_admin_user
        mock_tag_service.delete_tag.return_value = False

        response = client.delete(
            f"/api/tags/{uuid4()}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch("app.api.tag_routes.tag_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_delete_tag_requires_admin_or_manager(
        self, mock_user_repo, mock_auth_service, mock_tag_service, client, mock_user
    ):
        """Test delete requires admin or manager role."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user

        response = client.delete(
            f"/api/tags/{uuid4()}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @patch("app.api.tag_routes.tag_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_delete_tag_manager_allowed(
        self, mock_user_repo, mock_auth_service, mock_tag_service, client, mock_manager_user
    ):
        """Test manager role can delete tags."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_manager_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_manager_user
        mock_tag_service.delete_tag.return_value = True

        response = client.delete(
            f"/api/tags/{uuid4()}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
