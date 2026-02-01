"""Unit tests for NicheService."""

from datetime import datetime
from unittest.mock import patch
from uuid import uuid4

import pytest

from app.models.kompass_dto import NicheCreateDTO, NicheUpdateDTO
from app.services.niche_service import NicheService


@pytest.fixture
def niche_service():
    """Create a fresh NicheService instance for each test."""
    return NicheService()


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
def mock_niche_with_count(mock_niche):
    """Sample niche data with client count."""
    return {
        **mock_niche,
        "client_count": 5,
    }


class TestCreateNiche:
    """Tests for create_niche method."""

    @patch("app.services.niche_service.niche_repository")
    def test_create_niche_success(self, mock_repo, niche_service, mock_niche):
        """Test creating a niche successfully."""
        mock_repo.create.return_value = mock_niche

        request = NicheCreateDTO(
            name="Constructoras",
            description="Construction companies",
            is_active=True,
        )
        result = niche_service.create_niche(request)

        assert result is not None
        assert result.name == "Constructoras"
        assert result.description == "Construction companies"
        assert result.is_active is True
        mock_repo.create.assert_called_once_with(
            name="Constructoras",
            description="Construction companies",
            is_active=True,
        )

    @patch("app.services.niche_service.niche_repository")
    def test_create_niche_with_defaults(self, mock_repo, niche_service):
        """Test creating a niche with default values."""
        niche_id = uuid4()
        mock_repo.create.return_value = {
            "id": niche_id,
            "name": "Hoteles",
            "description": None,
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        request = NicheCreateDTO(name="Hoteles")
        result = niche_service.create_niche(request)

        assert result is not None
        assert result.name == "Hoteles"
        assert result.description is None
        assert result.is_active is True

    @patch("app.services.niche_service.niche_repository")
    def test_create_niche_failure(self, mock_repo, niche_service):
        """Test niche creation failure."""
        mock_repo.create.return_value = None

        request = NicheCreateDTO(name="Failed")
        result = niche_service.create_niche(request)

        assert result is None


class TestGetNiche:
    """Tests for get_niche method."""

    @patch("app.services.niche_service.niche_repository")
    def test_get_existing_niche_with_count(self, mock_repo, niche_service, mock_niche):
        """Test getting an existing niche with client count."""
        mock_repo.get_by_id.return_value = mock_niche
        mock_repo.count_clients_by_niche.return_value = 10

        result = niche_service.get_niche(mock_niche["id"])

        assert result is not None
        assert result.id == mock_niche["id"]
        assert result.name == "Constructoras"
        assert result.client_count == 10

    @patch("app.services.niche_service.niche_repository")
    def test_get_niche_zero_clients(self, mock_repo, niche_service, mock_niche):
        """Test getting a niche with zero clients."""
        mock_repo.get_by_id.return_value = mock_niche
        mock_repo.count_clients_by_niche.return_value = 0

        result = niche_service.get_niche(mock_niche["id"])

        assert result is not None
        assert result.client_count == 0

    @patch("app.services.niche_service.niche_repository")
    def test_get_nonexistent_niche(self, mock_repo, niche_service):
        """Test getting a non-existent niche returns None."""
        mock_repo.get_by_id.return_value = None

        result = niche_service.get_niche(uuid4())

        assert result is None


class TestListNiches:
    """Tests for list_niches method."""

    @patch("app.services.niche_service.niche_repository")
    def test_list_niches_with_counts(self, mock_repo, niche_service):
        """Test listing all niches with client counts."""
        mock_repo.get_all_with_client_counts.return_value = [
            {
                "id": uuid4(),
                "name": "Constructoras",
                "description": "Construction companies",
                "is_active": True,
                "client_count": 15,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
            {
                "id": uuid4(),
                "name": "Hoteles",
                "description": "Hotels and resorts",
                "is_active": True,
                "client_count": 3,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
        ]

        result = niche_service.list_niches()

        assert len(result) == 2
        assert result[0].name == "Constructoras"
        assert result[0].client_count == 15
        assert result[1].name == "Hoteles"
        assert result[1].client_count == 3

    @patch("app.services.niche_service.niche_repository")
    def test_list_niches_empty(self, mock_repo, niche_service):
        """Test listing niches when none exist."""
        mock_repo.get_all_with_client_counts.return_value = []

        result = niche_service.list_niches()

        assert result == []


class TestUpdateNiche:
    """Tests for update_niche method."""

    @patch("app.services.niche_service.niche_repository")
    def test_update_niche_name(self, mock_repo, niche_service, mock_niche):
        """Test updating niche name."""
        updated_niche = mock_niche.copy()
        updated_niche["name"] = "Constructoras Grandes"
        mock_repo.get_by_id.return_value = mock_niche
        mock_repo.update.return_value = updated_niche

        request = NicheUpdateDTO(name="Constructoras Grandes")
        result = niche_service.update_niche(mock_niche["id"], request)

        assert result is not None
        assert result.name == "Constructoras Grandes"

    @patch("app.services.niche_service.niche_repository")
    def test_update_niche_description(self, mock_repo, niche_service, mock_niche):
        """Test updating niche description."""
        updated_niche = mock_niche.copy()
        updated_niche["description"] = "Updated description"
        mock_repo.get_by_id.return_value = mock_niche
        mock_repo.update.return_value = updated_niche

        request = NicheUpdateDTO(description="Updated description")
        result = niche_service.update_niche(mock_niche["id"], request)

        assert result is not None
        assert result.description == "Updated description"

    @patch("app.services.niche_service.niche_repository")
    def test_update_niche_is_active(self, mock_repo, niche_service, mock_niche):
        """Test updating niche is_active status."""
        updated_niche = mock_niche.copy()
        updated_niche["is_active"] = False
        mock_repo.get_by_id.return_value = mock_niche
        mock_repo.update.return_value = updated_niche

        request = NicheUpdateDTO(is_active=False)
        result = niche_service.update_niche(mock_niche["id"], request)

        assert result is not None
        assert result.is_active is False

    @patch("app.services.niche_service.niche_repository")
    def test_update_niche_all_fields(self, mock_repo, niche_service, mock_niche):
        """Test updating all niche fields."""
        updated_niche = mock_niche.copy()
        updated_niche["name"] = "New Name"
        updated_niche["description"] = "New description"
        updated_niche["is_active"] = False
        mock_repo.get_by_id.return_value = mock_niche
        mock_repo.update.return_value = updated_niche

        request = NicheUpdateDTO(
            name="New Name",
            description="New description",
            is_active=False,
        )
        result = niche_service.update_niche(mock_niche["id"], request)

        assert result is not None
        assert result.name == "New Name"
        assert result.description == "New description"
        assert result.is_active is False

    @patch("app.services.niche_service.niche_repository")
    def test_update_nonexistent_niche(self, mock_repo, niche_service):
        """Test updating non-existent niche returns None."""
        mock_repo.get_by_id.return_value = None

        request = NicheUpdateDTO(name="New Name")
        result = niche_service.update_niche(uuid4(), request)

        assert result is None
        mock_repo.update.assert_not_called()


class TestDeleteNiche:
    """Tests for delete_niche method."""

    @patch("app.services.niche_service.niche_repository")
    def test_delete_niche_success(self, mock_repo, niche_service, mock_niche):
        """Test deleting a niche successfully."""
        mock_repo.get_by_id.return_value = mock_niche
        mock_repo.has_clients.return_value = False
        mock_repo.delete.return_value = True

        result = niche_service.delete_niche(mock_niche["id"])

        assert result is True
        mock_repo.delete.assert_called_once_with(mock_niche["id"])

    @patch("app.services.niche_service.niche_repository")
    def test_delete_niche_with_clients_raises_error(
        self, mock_repo, niche_service, mock_niche
    ):
        """Test delete fails if niche has clients."""
        mock_repo.get_by_id.return_value = mock_niche
        mock_repo.has_clients.return_value = True

        with pytest.raises(ValueError) as exc_info:
            niche_service.delete_niche(mock_niche["id"])

        assert "Cannot delete niche with associated clients" in str(exc_info.value)
        mock_repo.delete.assert_not_called()

    @patch("app.services.niche_service.niche_repository")
    def test_delete_nonexistent_niche(self, mock_repo, niche_service):
        """Test deleting non-existent niche returns False."""
        mock_repo.get_by_id.return_value = None

        result = niche_service.delete_niche(uuid4())

        assert result is False
        mock_repo.has_clients.assert_not_called()
        mock_repo.delete.assert_not_called()

    @patch("app.services.niche_service.niche_repository")
    def test_delete_niche_no_clients_allowed(self, mock_repo, niche_service, mock_niche):
        """Test delete is allowed when niche has zero clients."""
        mock_repo.get_by_id.return_value = mock_niche
        mock_repo.has_clients.return_value = False
        mock_repo.delete.return_value = True

        result = niche_service.delete_niche(mock_niche["id"])

        assert result is True
        mock_repo.has_clients.assert_called_once_with(mock_niche["id"])
