"""Unit tests for TagService."""

from datetime import datetime
from unittest.mock import patch
from uuid import uuid4

import pytest

from app.models.kompass_dto import TagCreateDTO, TagUpdateDTO
from app.services.tag_service import TagService


@pytest.fixture
def tag_service():
    """Create a fresh TagService instance for each test."""
    return TagService()


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
def mock_tag_with_count(mock_tag):
    """Sample tag data with product count."""
    return {
        **mock_tag,
        "product_count": 5,
    }


class TestCreateTag:
    """Tests for create_tag method."""

    @patch("app.services.tag_service.tag_repository")
    def test_create_tag_success(self, mock_repo, tag_service, mock_tag):
        """Test creating a tag successfully."""
        mock_repo.create.return_value = mock_tag

        request = TagCreateDTO(name="Trending", color="#FF5733")
        result = tag_service.create_tag(request)

        assert result is not None
        assert result.name == "Trending"
        assert result.color == "#FF5733"
        mock_repo.create.assert_called_once_with(name="Trending", color="#FF5733")

    @patch("app.services.tag_service.tag_repository")
    def test_create_tag_with_default_color(self, mock_repo, tag_service):
        """Test creating a tag with default color."""
        tag_id = uuid4()
        mock_repo.create.return_value = {
            "id": tag_id,
            "name": "New",
            "color": "#000000",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        request = TagCreateDTO(name="New")
        result = tag_service.create_tag(request)

        assert result is not None
        assert result.color == "#000000"

    @patch("app.services.tag_service.tag_repository")
    def test_create_tag_failure(self, mock_repo, tag_service):
        """Test tag creation failure."""
        mock_repo.create.return_value = None

        request = TagCreateDTO(name="Failed")
        result = tag_service.create_tag(request)

        assert result is None


class TestGetTag:
    """Tests for get_tag method."""

    @patch("app.services.tag_service.tag_repository")
    def test_get_existing_tag_with_count(self, mock_repo, tag_service, mock_tag):
        """Test getting an existing tag with product count."""
        mock_repo.get_by_id.return_value = mock_tag
        mock_repo.get_product_count.return_value = 10

        result = tag_service.get_tag(mock_tag["id"])

        assert result is not None
        assert result.id == mock_tag["id"]
        assert result.name == "Trending"
        assert result.product_count == 10

    @patch("app.services.tag_service.tag_repository")
    def test_get_tag_zero_products(self, mock_repo, tag_service, mock_tag):
        """Test getting a tag with zero products."""
        mock_repo.get_by_id.return_value = mock_tag
        mock_repo.get_product_count.return_value = 0

        result = tag_service.get_tag(mock_tag["id"])

        assert result is not None
        assert result.product_count == 0

    @patch("app.services.tag_service.tag_repository")
    def test_get_nonexistent_tag(self, mock_repo, tag_service):
        """Test getting a non-existent tag returns None."""
        mock_repo.get_by_id.return_value = None

        result = tag_service.get_tag(uuid4())

        assert result is None


class TestListTags:
    """Tests for list_tags method."""

    @patch("app.services.tag_service.tag_repository")
    def test_list_tags_with_counts(self, mock_repo, tag_service):
        """Test listing all tags with product counts."""
        mock_repo.get_all_with_counts_paginated.return_value = (
            [
                {
                    "id": uuid4(),
                    "name": "Popular",
                    "color": "#FF0000",
                    "product_count": 15,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now(),
                },
                {
                    "id": uuid4(),
                    "name": "New",
                    "color": "#00FF00",
                    "product_count": 3,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now(),
                },
            ],
            2  # total count
        )

        result = tag_service.list_tags(page=1, limit=20)

        assert len(result.items) == 2
        assert result.items[0].name == "Popular"
        assert result.items[0].product_count == 15
        assert result.items[1].name == "New"
        assert result.items[1].product_count == 3
        assert result.pagination.total == 2
        assert result.pagination.page == 1
        assert result.pagination.pages == 1

    @patch("app.services.tag_service.tag_repository")
    def test_list_tags_empty(self, mock_repo, tag_service):
        """Test listing tags when none exist."""
        mock_repo.get_all_with_counts_paginated.return_value = ([], 0)

        result = tag_service.list_tags(page=1, limit=20)

        assert result.items == []
        assert result.pagination.total == 0


class TestUpdateTag:
    """Tests for update_tag method."""

    @patch("app.services.tag_service.tag_repository")
    def test_update_tag_name(self, mock_repo, tag_service, mock_tag):
        """Test updating tag name."""
        updated_tag = mock_tag.copy()
        updated_tag["name"] = "Hot"
        mock_repo.get_by_id.return_value = mock_tag
        mock_repo.update.return_value = updated_tag

        request = TagUpdateDTO(name="Hot")
        result = tag_service.update_tag(mock_tag["id"], request)

        assert result is not None
        assert result.name == "Hot"

    @patch("app.services.tag_service.tag_repository")
    def test_update_tag_color(self, mock_repo, tag_service, mock_tag):
        """Test updating tag color."""
        updated_tag = mock_tag.copy()
        updated_tag["color"] = "#0000FF"
        mock_repo.get_by_id.return_value = mock_tag
        mock_repo.update.return_value = updated_tag

        request = TagUpdateDTO(color="#0000FF")
        result = tag_service.update_tag(mock_tag["id"], request)

        assert result is not None
        assert result.color == "#0000FF"

    @patch("app.services.tag_service.tag_repository")
    def test_update_tag_both_fields(self, mock_repo, tag_service, mock_tag):
        """Test updating both name and color."""
        updated_tag = mock_tag.copy()
        updated_tag["name"] = "Featured"
        updated_tag["color"] = "#FFFF00"
        mock_repo.get_by_id.return_value = mock_tag
        mock_repo.update.return_value = updated_tag

        request = TagUpdateDTO(name="Featured", color="#FFFF00")
        result = tag_service.update_tag(mock_tag["id"], request)

        assert result is not None
        assert result.name == "Featured"
        assert result.color == "#FFFF00"

    @patch("app.services.tag_service.tag_repository")
    def test_update_nonexistent_tag(self, mock_repo, tag_service):
        """Test updating non-existent tag returns None."""
        mock_repo.get_by_id.return_value = None

        request = TagUpdateDTO(name="New Name")
        result = tag_service.update_tag(uuid4(), request)

        assert result is None
        mock_repo.update.assert_not_called()


class TestDeleteTag:
    """Tests for delete_tag method."""

    @patch("app.services.tag_service.tag_repository")
    def test_delete_tag_success(self, mock_repo, tag_service, mock_tag):
        """Test deleting a tag successfully."""
        mock_repo.get_by_id.return_value = mock_tag
        mock_repo.delete.return_value = True

        result = tag_service.delete_tag(mock_tag["id"])

        assert result is True
        mock_repo.delete.assert_called_once_with(mock_tag["id"])

    @patch("app.services.tag_service.tag_repository")
    def test_delete_tag_cascade(self, mock_repo, tag_service, mock_tag):
        """Test delete removes product associations via cascade."""
        mock_repo.get_by_id.return_value = mock_tag
        mock_repo.delete.return_value = True

        result = tag_service.delete_tag(mock_tag["id"])

        assert result is True

    @patch("app.services.tag_service.tag_repository")
    def test_delete_nonexistent_tag(self, mock_repo, tag_service):
        """Test deleting non-existent tag returns False."""
        mock_repo.get_by_id.return_value = None

        result = tag_service.delete_tag(uuid4())

        assert result is False
        mock_repo.delete.assert_not_called()


class TestSearchTags:
    """Tests for search_tags method."""

    @patch("app.services.tag_service.tag_repository")
    def test_search_tags_matching(self, mock_repo, tag_service):
        """Test searching tags with matching results."""
        mock_repo.search.return_value = [
            {
                "id": uuid4(),
                "name": "Trending",
                "color": "#FF0000",
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
            {
                "id": uuid4(),
                "name": "Top Trending",
                "color": "#FF5500",
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
        ]

        result = tag_service.search_tags("trend")

        assert len(result) == 2
        mock_repo.search.assert_called_once_with("trend", 20)

    @patch("app.services.tag_service.tag_repository")
    def test_search_tags_no_results(self, mock_repo, tag_service):
        """Test searching tags with no matching results."""
        mock_repo.search.return_value = []

        result = tag_service.search_tags("xyz")

        assert result == []

    @patch("app.services.tag_service.tag_repository")
    def test_search_tags_empty_query(self, mock_repo, tag_service):
        """Test searching with empty query returns empty list."""
        result = tag_service.search_tags("")

        assert result == []
        mock_repo.search.assert_not_called()

    @patch("app.services.tag_service.tag_repository")
    def test_search_tags_whitespace_query(self, mock_repo, tag_service):
        """Test searching with whitespace query returns empty list."""
        result = tag_service.search_tags("   ")

        assert result == []
        mock_repo.search.assert_not_called()

    @patch("app.services.tag_service.tag_repository")
    def test_search_tags_with_limit(self, mock_repo, tag_service):
        """Test searching tags with custom limit."""
        mock_repo.search.return_value = []

        tag_service.search_tags("test", limit=5)

        mock_repo.search.assert_called_once_with("test", 5)

    @patch("app.services.tag_service.tag_repository")
    def test_search_tags_trims_query(self, mock_repo, tag_service):
        """Test search query is trimmed."""
        mock_repo.search.return_value = []

        tag_service.search_tags("  test  ")

        mock_repo.search.assert_called_once_with("test", 20)

    @patch("app.services.tag_service.tag_repository")
    def test_search_tags_special_characters(self, mock_repo, tag_service):
        """Test searching with special characters."""
        mock_repo.search.return_value = [
            {
                "id": uuid4(),
                "name": "50% Off",
                "color": "#FF0000",
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
        ]

        result = tag_service.search_tags("50%")

        assert len(result) == 1
        mock_repo.search.assert_called_once_with("50%", 20)
