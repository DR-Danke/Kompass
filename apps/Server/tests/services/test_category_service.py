"""Unit tests for CategoryService."""

from datetime import datetime
from unittest.mock import patch
from uuid import uuid4

import pytest

from app.models.kompass_dto import CategoryCreateDTO, CategoryUpdateDTO
from app.services.category_service import CategoryService


@pytest.fixture
def category_service():
    """Create a fresh CategoryService instance for each test."""
    return CategoryService()


@pytest.fixture
def mock_category():
    """Sample category data."""
    return {
        "id": uuid4(),
        "name": "Electronics",
        "description": "Electronic products",
        "parent_id": None,
        "sort_order": 0,
        "is_active": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "parent_name": None,
    }


@pytest.fixture
def mock_child_category(mock_category):
    """Sample child category data."""
    return {
        "id": uuid4(),
        "name": "Smartphones",
        "description": "Mobile phones",
        "parent_id": mock_category["id"],
        "sort_order": 0,
        "is_active": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "parent_name": "Electronics",
    }


class TestCreateCategory:
    """Tests for create_category method."""

    @patch("app.services.category_service.category_repository")
    def test_create_category_without_parent(self, mock_repo, category_service):
        """Test creating a root category."""
        category_id = uuid4()
        mock_repo.create.return_value = {
            "id": category_id,
            "name": "Electronics",
            "description": "Electronic products",
            "parent_id": None,
            "sort_order": 0,
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        request = CategoryCreateDTO(
            name="Electronics",
            description="Electronic products",
        )
        result = category_service.create_category(request)

        assert result is not None
        assert result.name == "Electronics"
        assert result.parent_id is None
        mock_repo.create.assert_called_once()

    @patch("app.services.category_service.category_repository")
    def test_create_category_with_parent(self, mock_repo, category_service, mock_category):
        """Test creating a child category."""
        child_id = uuid4()
        mock_repo.get_by_id.return_value = mock_category
        mock_repo.create.return_value = {
            "id": child_id,
            "name": "Smartphones",
            "description": "Mobile phones",
            "parent_id": mock_category["id"],
            "sort_order": 0,
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        request = CategoryCreateDTO(
            name="Smartphones",
            description="Mobile phones",
            parent_id=mock_category["id"],
        )
        result = category_service.create_category(request)

        assert result is not None
        assert result.name == "Smartphones"
        assert result.parent_id == mock_category["id"]

    @patch("app.services.category_service.category_repository")
    def test_create_category_with_invalid_parent(self, mock_repo, category_service):
        """Test creating a category with non-existent parent fails."""
        mock_repo.get_by_id.return_value = None

        request = CategoryCreateDTO(
            name="Orphan",
            parent_id=uuid4(),
        )
        result = category_service.create_category(request)

        assert result is None
        mock_repo.create.assert_not_called()


class TestGetCategory:
    """Tests for get_category method."""

    @patch("app.services.category_service.category_repository")
    def test_get_existing_category(self, mock_repo, category_service, mock_category):
        """Test getting an existing category."""
        mock_repo.get_by_id.return_value = mock_category

        result = category_service.get_category(mock_category["id"])

        assert result is not None
        assert result.id == mock_category["id"]
        assert result.name == "Electronics"

    @patch("app.services.category_service.category_repository")
    def test_get_nonexistent_category(self, mock_repo, category_service):
        """Test getting a non-existent category returns None."""
        mock_repo.get_by_id.return_value = None

        result = category_service.get_category(uuid4())

        assert result is None


class TestListCategories:
    """Tests for list_categories method."""

    @patch("app.services.category_service.category_repository")
    def test_list_categories_returns_tree(self, mock_repo, category_service):
        """Test list_categories returns properly nested tree."""
        parent_id = uuid4()
        child_id = uuid4()
        grandchild_id = uuid4()

        mock_repo.get_all.return_value = (
            [
                {
                    "id": parent_id,
                    "name": "Electronics",
                    "description": None,
                    "parent_id": None,
                    "sort_order": 0,
                    "is_active": True,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now(),
                },
                {
                    "id": child_id,
                    "name": "Phones",
                    "description": None,
                    "parent_id": parent_id,
                    "sort_order": 0,
                    "is_active": True,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now(),
                },
                {
                    "id": grandchild_id,
                    "name": "Smartphones",
                    "description": None,
                    "parent_id": child_id,
                    "sort_order": 0,
                    "is_active": True,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now(),
                },
            ],
            3,
        )

        result = category_service.list_categories()

        assert len(result) == 1
        assert result[0].name == "Electronics"
        assert result[0].depth == 0
        assert result[0].path == "Electronics"
        assert len(result[0].children) == 1
        assert result[0].children[0].name == "Phones"
        assert result[0].children[0].depth == 1
        assert result[0].children[0].path == "Electronics/Phones"
        assert len(result[0].children[0].children) == 1
        assert result[0].children[0].children[0].name == "Smartphones"
        assert result[0].children[0].children[0].depth == 2

    @patch("app.services.category_service.category_repository")
    def test_list_categories_empty(self, mock_repo, category_service):
        """Test list_categories with no categories."""
        mock_repo.get_all.return_value = ([], 0)

        result = category_service.list_categories()

        assert result == []


class TestUpdateCategory:
    """Tests for update_category method."""

    @patch("app.services.category_service.category_repository")
    def test_update_category_name(self, mock_repo, category_service, mock_category):
        """Test updating category name."""
        updated_category = mock_category.copy()
        updated_category["name"] = "Consumer Electronics"
        mock_repo.get_by_id.return_value = mock_category
        mock_repo.update.return_value = updated_category

        request = CategoryUpdateDTO(name="Consumer Electronics")
        result = category_service.update_category(mock_category["id"], request)

        assert result is not None
        assert result.name == "Consumer Electronics"

    @patch("app.services.category_service.category_repository")
    def test_update_category_self_parent(self, mock_repo, category_service, mock_category):
        """Test cannot set category as its own parent."""
        mock_repo.get_by_id.return_value = mock_category

        request = CategoryUpdateDTO(parent_id=mock_category["id"])
        result = category_service.update_category(mock_category["id"], request)

        assert result is None
        mock_repo.update.assert_not_called()

    @patch("app.services.category_service.category_repository")
    def test_update_nonexistent_category(self, mock_repo, category_service):
        """Test updating non-existent category returns None."""
        mock_repo.get_by_id.return_value = None

        request = CategoryUpdateDTO(name="New Name")
        result = category_service.update_category(uuid4(), request)

        assert result is None


class TestDeleteCategory:
    """Tests for delete_category method."""

    @patch("app.services.category_service.category_repository")
    def test_delete_leaf_category(self, mock_repo, category_service, mock_category):
        """Test deleting a leaf category."""
        mock_repo.get_by_id.return_value = mock_category
        mock_repo.has_children.return_value = False
        mock_repo.has_products.return_value = False
        mock_repo.delete.return_value = True

        result = category_service.delete_category(mock_category["id"])

        assert result is True
        mock_repo.delete.assert_called_once()

    @patch("app.services.category_service.category_repository")
    def test_delete_category_with_children(self, mock_repo, category_service, mock_category):
        """Test cannot delete category with children."""
        mock_repo.get_by_id.return_value = mock_category
        mock_repo.has_children.return_value = True

        result = category_service.delete_category(mock_category["id"])

        assert result is False
        mock_repo.delete.assert_not_called()

    @patch("app.services.category_service.category_repository")
    def test_delete_category_with_products(self, mock_repo, category_service, mock_category):
        """Test cannot delete category with products."""
        mock_repo.get_by_id.return_value = mock_category
        mock_repo.has_children.return_value = False
        mock_repo.has_products.return_value = True

        result = category_service.delete_category(mock_category["id"])

        assert result is False
        mock_repo.delete.assert_not_called()

    @patch("app.services.category_service.category_repository")
    def test_delete_nonexistent_category(self, mock_repo, category_service):
        """Test deleting non-existent category."""
        mock_repo.get_by_id.return_value = None

        result = category_service.delete_category(uuid4())

        assert result is False


class TestMoveCategory:
    """Tests for move_category method."""

    @patch("app.services.category_service.category_repository")
    def test_move_to_new_parent(self, mock_repo, category_service, mock_category):
        """Test moving category to a new parent."""
        new_parent_id = uuid4()
        new_parent = {
            "id": new_parent_id,
            "name": "New Parent",
            "description": None,
            "parent_id": None,
            "sort_order": 0,
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        updated = mock_category.copy()
        updated["parent_id"] = new_parent_id

        mock_repo.get_by_id.side_effect = [mock_category, new_parent, mock_category]
        mock_repo.get_children.return_value = []
        mock_repo.set_parent.return_value = updated

        result = category_service.move_category(mock_category["id"], new_parent_id)

        assert result is not None
        mock_repo.set_parent.assert_called_once()

    @patch("app.services.category_service.category_repository")
    def test_move_to_root(self, mock_repo, category_service, mock_child_category):
        """Test moving category to root level."""
        updated = mock_child_category.copy()
        updated["parent_id"] = None

        mock_repo.get_by_id.return_value = mock_child_category
        mock_repo.set_parent.return_value = updated

        result = category_service.move_category(mock_child_category["id"], None)

        assert result is not None
        mock_repo.set_parent.assert_called_with(mock_child_category["id"], None)

    @patch("app.services.category_service.category_repository")
    def test_move_to_self(self, mock_repo, category_service, mock_category):
        """Test cannot move category to itself."""
        mock_repo.get_by_id.return_value = mock_category

        result = category_service.move_category(mock_category["id"], mock_category["id"])

        assert result is None
        mock_repo.set_parent.assert_not_called()


class TestGetDescendants:
    """Tests for get_descendants method."""

    @patch("app.services.category_service.category_repository")
    def test_get_descendants_multilevel(self, mock_repo, category_service, mock_category):
        """Test getting descendants at multiple levels."""
        child_id = uuid4()
        grandchild_id = uuid4()

        child = {
            "id": child_id,
            "name": "Child",
            "description": None,
            "parent_id": mock_category["id"],
            "sort_order": 0,
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        grandchild = {
            "id": grandchild_id,
            "name": "Grandchild",
            "description": None,
            "parent_id": child_id,
            "sort_order": 0,
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        mock_repo.get_by_id.return_value = mock_category
        mock_repo.get_children.side_effect = [[child], [grandchild], []]

        result = category_service.get_descendants(mock_category["id"])

        assert len(result) == 2
        assert any(d.id == child_id for d in result)
        assert any(d.id == grandchild_id for d in result)

    @patch("app.services.category_service.category_repository")
    def test_get_descendants_no_children(self, mock_repo, category_service, mock_category):
        """Test getting descendants of a leaf category."""
        mock_repo.get_by_id.return_value = mock_category
        mock_repo.get_children.return_value = []

        result = category_service.get_descendants(mock_category["id"])

        assert result == []

    @patch("app.services.category_service.category_repository")
    def test_get_descendants_nonexistent(self, mock_repo, category_service):
        """Test getting descendants of non-existent category."""
        mock_repo.get_by_id.return_value = None

        result = category_service.get_descendants(uuid4())

        assert result == []
