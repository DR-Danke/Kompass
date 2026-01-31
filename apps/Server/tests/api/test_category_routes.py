"""Unit tests for category API routes."""

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
def mock_category():
    """Sample category data."""
    return {
        "id": uuid4(),
        "name": "Electronics",
        "description": "Electronic products",
        "parent_id": None,
        "parent_name": None,
        "sort_order": 0,
        "is_active": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }


@pytest.fixture
def mock_category_response(mock_category):
    """Sample category response DTO."""
    from app.models.kompass_dto import CategoryResponseDTO

    return CategoryResponseDTO(**mock_category)


@pytest.fixture
def mock_tree_node():
    """Sample category tree node."""
    from app.models.kompass_dto import CategoryTreeNode

    return CategoryTreeNode(
        id=uuid4(),
        name="Electronics",
        description="Electronic products",
        parent_id=None,
        sort_order=0,
        is_active=True,
        depth=0,
        path="Electronics",
        children=[],
    )


class TestListCategories:
    """Tests for GET /api/categories."""

    @patch("app.api.category_routes.category_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_list_categories_returns_tree(
        self, mock_user_repo, mock_auth_service, mock_cat_service, client, mock_user, mock_tree_node
    ):
        """Test listing categories returns tree structure."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_cat_service.list_categories.return_value = [mock_tree_node]

        response = client.get(
            "/api/categories/",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Electronics"
        assert data[0]["depth"] == 0

    def test_list_categories_requires_auth(self, client):
        """Test listing categories requires authentication."""
        response = client.get("/api/categories/")

        # FastAPI returns 403 when HTTPBearer credentials are not provided
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


class TestCreateCategory:
    """Tests for POST /api/categories."""

    @patch("app.api.category_routes.category_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_create_category_success(
        self, mock_user_repo, mock_auth_service, mock_cat_service, client, mock_user, mock_category_response
    ):
        """Test creating a category successfully."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_cat_service.create_category.return_value = mock_category_response

        response = client.post(
            "/api/categories/",
            json={"name": "Electronics", "description": "Electronic products"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Electronics"

    @patch("app.api.category_routes.category_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_create_category_with_invalid_parent_returns_400(
        self, mock_user_repo, mock_auth_service, mock_cat_service, client, mock_user
    ):
        """Test creating category with non-existent parent fails."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_cat_service.create_category.return_value = None

        response = client.post(
            "/api/categories/",
            json={"name": "Orphan", "parent_id": str(uuid4())},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestGetCategory:
    """Tests for GET /api/categories/{category_id}."""

    @patch("app.api.category_routes.category_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_get_category_success(
        self, mock_user_repo, mock_auth_service, mock_cat_service, client, mock_user, mock_category_response
    ):
        """Test getting a category by ID."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_cat_service.get_category.return_value = mock_category_response

        response = client.get(
            f"/api/categories/{mock_category_response.id}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Electronics"

    @patch("app.api.category_routes.category_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_get_category_not_found_returns_404(
        self, mock_user_repo, mock_auth_service, mock_cat_service, client, mock_user
    ):
        """Test getting non-existent category returns 404."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_cat_service.get_category.return_value = None

        response = client.get(
            f"/api/categories/{uuid4()}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateCategory:
    """Tests for PUT /api/categories/{category_id}."""

    @patch("app.api.category_routes.category_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_update_category_success(
        self, mock_user_repo, mock_auth_service, mock_cat_service, client, mock_admin_user, mock_category_response
    ):
        """Test updating a category successfully."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_admin_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_admin_user
        mock_cat_service.get_category.return_value = mock_category_response
        mock_cat_service.update_category.return_value = mock_category_response

        response = client.put(
            f"/api/categories/{mock_category_response.id}",
            json={"name": "Consumer Electronics"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK

    @patch("app.api.category_routes.category_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_update_category_requires_admin_or_manager(
        self, mock_user_repo, mock_auth_service, mock_cat_service, client, mock_user, mock_category_response
    ):
        """Test update requires admin or manager role."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user

        response = client.put(
            f"/api/categories/{mock_category_response.id}",
            json={"name": "Consumer Electronics"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @patch("app.api.category_routes.category_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_update_category_not_found_returns_404(
        self, mock_user_repo, mock_auth_service, mock_cat_service, client, mock_admin_user
    ):
        """Test updating non-existent category returns 404."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_admin_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_admin_user
        mock_cat_service.get_category.return_value = None

        response = client.put(
            f"/api/categories/{uuid4()}",
            json={"name": "Consumer Electronics"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch("app.api.category_routes.category_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_update_category_cycle_returns_400(
        self, mock_user_repo, mock_auth_service, mock_cat_service, client, mock_admin_user, mock_category_response
    ):
        """Test update with cycle returns 400."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_admin_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_admin_user
        mock_cat_service.get_category.return_value = mock_category_response
        mock_cat_service.update_category.return_value = None

        response = client.put(
            f"/api/categories/{mock_category_response.id}",
            json={"parent_id": str(mock_category_response.id)},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestDeleteCategory:
    """Tests for DELETE /api/categories/{category_id}."""

    @patch("app.api.category_routes.category_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_delete_category_success(
        self, mock_user_repo, mock_auth_service, mock_cat_service, client, mock_admin_user, mock_category_response
    ):
        """Test deleting a category successfully."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_admin_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_admin_user
        mock_cat_service.get_category.return_value = mock_category_response
        mock_cat_service.delete_category.return_value = True

        response = client.delete(
            f"/api/categories/{mock_category_response.id}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    @patch("app.api.category_routes.category_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_delete_category_with_children_returns_409(
        self, mock_user_repo, mock_auth_service, mock_cat_service, client, mock_admin_user, mock_category_response
    ):
        """Test deleting category with children returns 409."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_admin_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_admin_user
        mock_cat_service.get_category.return_value = mock_category_response
        mock_cat_service.delete_category.return_value = False

        response = client.delete(
            f"/api/categories/{mock_category_response.id}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_409_CONFLICT

    @patch("app.api.category_routes.category_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_delete_category_not_found_returns_404(
        self, mock_user_repo, mock_auth_service, mock_cat_service, client, mock_admin_user
    ):
        """Test deleting non-existent category returns 404."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_admin_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_admin_user
        mock_cat_service.get_category.return_value = None

        response = client.delete(
            f"/api/categories/{uuid4()}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch("app.api.category_routes.category_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_delete_category_requires_admin_or_manager(
        self, mock_user_repo, mock_auth_service, mock_cat_service, client, mock_user
    ):
        """Test delete requires admin or manager role."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user

        response = client.delete(
            f"/api/categories/{uuid4()}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestMoveCategory:
    """Tests for PUT /api/categories/{category_id}/move."""

    @patch("app.api.category_routes.category_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_move_category_success(
        self, mock_user_repo, mock_auth_service, mock_cat_service, client, mock_admin_user, mock_category_response
    ):
        """Test moving a category to new parent."""
        new_parent_id = uuid4()
        mock_auth_service.decode_access_token.return_value = {"sub": mock_admin_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_admin_user
        mock_cat_service.get_category.return_value = mock_category_response
        mock_cat_service.move_category.return_value = mock_category_response

        response = client.put(
            f"/api/categories/{mock_category_response.id}/move",
            json={"new_parent_id": str(new_parent_id)},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK

    @patch("app.api.category_routes.category_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_move_category_to_root(
        self, mock_user_repo, mock_auth_service, mock_cat_service, client, mock_admin_user, mock_category_response
    ):
        """Test moving a category to root level."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_admin_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_admin_user
        mock_cat_service.get_category.return_value = mock_category_response
        mock_cat_service.move_category.return_value = mock_category_response

        response = client.put(
            f"/api/categories/{mock_category_response.id}/move",
            json={"new_parent_id": None},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK

    @patch("app.api.category_routes.category_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_move_category_cycle_returns_400(
        self, mock_user_repo, mock_auth_service, mock_cat_service, client, mock_admin_user, mock_category_response
    ):
        """Test moving category to descendant returns 400."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_admin_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_admin_user
        mock_cat_service.get_category.return_value = mock_category_response
        mock_cat_service.move_category.return_value = None

        response = client.put(
            f"/api/categories/{mock_category_response.id}/move",
            json={"new_parent_id": str(uuid4())},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch("app.api.category_routes.category_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_move_category_not_found_returns_404(
        self, mock_user_repo, mock_auth_service, mock_cat_service, client, mock_admin_user
    ):
        """Test moving non-existent category returns 404."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_admin_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_admin_user
        mock_cat_service.get_category.return_value = None

        response = client.put(
            f"/api/categories/{uuid4()}/move",
            json={"new_parent_id": str(uuid4())},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch("app.api.category_routes.category_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_move_category_requires_admin_or_manager(
        self, mock_user_repo, mock_auth_service, mock_cat_service, client, mock_user
    ):
        """Test move requires admin or manager role."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user

        response = client.put(
            f"/api/categories/{uuid4()}/move",
            json={"new_parent_id": str(uuid4())},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
