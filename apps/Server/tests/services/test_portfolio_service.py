"""Unit tests for PortfolioService."""

from datetime import datetime
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from app.models.kompass_dto import (
    PortfolioCreateDTO,
    PortfolioFilterDTO,
    PortfolioItemCreateDTO,
    PortfolioUpdateDTO,
    ProductFilterDTO,
    ProductStatus,
)
from app.services.portfolio_service import PortfolioService


@pytest.fixture
def mock_repository():
    """Create a mock portfolio repository."""
    return MagicMock()


@pytest.fixture
def portfolio_service(mock_repository):
    """Create a PortfolioService with mocked repository."""
    return PortfolioService(repository=mock_repository)


@pytest.fixture
def sample_portfolio_data():
    """Sample portfolio data for testing."""
    return {
        "id": uuid4(),
        "name": "Test Portfolio",
        "description": "Test description",
        "niche_id": uuid4(),
        "niche_name": "Test Niche",
        "is_active": True,
        "items": [],
        "item_count": 0,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }


@pytest.fixture
def sample_portfolio_item_data():
    """Sample portfolio item data for testing."""
    return {
        "id": uuid4(),
        "portfolio_id": uuid4(),
        "product_id": uuid4(),
        "product_name": "Test Product",
        "product_sku": "PRD-001",
        "sort_order": 0,
        "notes": "Test notes",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }


class TestCreatePortfolio:
    """Tests for create_portfolio method."""

    def test_create_portfolio_success(
        self, mock_repository, portfolio_service, sample_portfolio_data
    ):
        """Test successful portfolio creation."""
        mock_repository.create.return_value = sample_portfolio_data
        mock_repository.get_by_id.return_value = sample_portfolio_data

        request = PortfolioCreateDTO(
            name="Test Portfolio",
            description="Test description",
        )

        result = portfolio_service.create_portfolio(request)

        assert result is not None
        assert result.name == "Test Portfolio"
        mock_repository.create.assert_called_once()

    def test_create_portfolio_with_items(
        self, mock_repository, portfolio_service, sample_portfolio_data, sample_portfolio_item_data
    ):
        """Test creating portfolio with initial items."""
        sample_portfolio_data["items"] = [sample_portfolio_item_data]
        sample_portfolio_data["item_count"] = 1
        mock_repository.create.return_value = sample_portfolio_data
        mock_repository.get_by_id.return_value = sample_portfolio_data
        mock_repository.add_item.return_value = sample_portfolio_item_data

        product_id = uuid4()
        request = PortfolioCreateDTO(
            name="Test Portfolio",
            items=[
                PortfolioItemCreateDTO(product_id=product_id, sort_order=0),
            ],
        )

        result = portfolio_service.create_portfolio(request)

        assert result is not None
        assert result.item_count == 1
        mock_repository.add_item.assert_called_once()

    def test_create_portfolio_fails(self, mock_repository, portfolio_service):
        """Test that None is returned when creation fails."""
        mock_repository.create.return_value = None

        request = PortfolioCreateDTO(name="Test Portfolio")

        result = portfolio_service.create_portfolio(request)

        assert result is None


class TestGetPortfolio:
    """Tests for get_portfolio method."""

    def test_get_portfolio_found(
        self, mock_repository, portfolio_service, sample_portfolio_data
    ):
        """Test getting an existing portfolio."""
        mock_repository.get_by_id.return_value = sample_portfolio_data
        portfolio_id = sample_portfolio_data["id"]

        result = portfolio_service.get_portfolio(portfolio_id)

        assert result is not None
        assert result.id == portfolio_id
        mock_repository.get_by_id.assert_called_once_with(portfolio_id)

    def test_get_portfolio_not_found(self, mock_repository, portfolio_service):
        """Test that None is returned for non-existent portfolio."""
        mock_repository.get_by_id.return_value = None
        portfolio_id = uuid4()

        result = portfolio_service.get_portfolio(portfolio_id)

        assert result is None


class TestListPortfolios:
    """Tests for list_portfolios method."""

    def test_list_portfolios_with_pagination(
        self, mock_repository, portfolio_service, sample_portfolio_data
    ):
        """Test listing portfolios with pagination."""
        mock_repository.get_all.return_value = ([sample_portfolio_data], 1)

        result = portfolio_service.list_portfolios(page=1, limit=20)

        assert len(result.items) == 1
        assert result.pagination.page == 1
        assert result.pagination.limit == 20
        assert result.pagination.total == 1
        assert result.pagination.pages == 1

    def test_list_portfolios_with_filters(
        self, mock_repository, portfolio_service, sample_portfolio_data
    ):
        """Test filtering portfolios."""
        mock_repository.get_all.return_value = ([sample_portfolio_data], 1)
        niche_id = uuid4()

        filters = PortfolioFilterDTO(niche_id=niche_id, is_active=True)
        portfolio_service.list_portfolios(filters=filters)

        call_kwargs = mock_repository.get_all.call_args.kwargs
        assert call_kwargs["niche_id"] == niche_id
        assert call_kwargs["is_active"] is True

    def test_list_portfolios_with_search(
        self, mock_repository, portfolio_service, sample_portfolio_data
    ):
        """Test searching portfolios."""
        mock_repository.search.return_value = [sample_portfolio_data]

        filters = PortfolioFilterDTO(search="test")
        result = portfolio_service.list_portfolios(filters=filters)

        mock_repository.search.assert_called_once()
        assert len(result.items) == 1

    def test_list_portfolios_empty_result(self, mock_repository, portfolio_service):
        """Test empty result handling."""
        mock_repository.get_all.return_value = ([], 0)

        result = portfolio_service.list_portfolios()

        assert len(result.items) == 0
        assert result.pagination.total == 0
        assert result.pagination.pages == 0


class TestUpdatePortfolio:
    """Tests for update_portfolio method."""

    def test_update_portfolio_success(
        self, mock_repository, portfolio_service, sample_portfolio_data
    ):
        """Test successful portfolio update."""
        updated_data = sample_portfolio_data.copy()
        updated_data["name"] = "Updated Name"
        mock_repository.update.return_value = updated_data

        portfolio_id = sample_portfolio_data["id"]
        request = PortfolioUpdateDTO(name="Updated Name")

        result = portfolio_service.update_portfolio(portfolio_id, request)

        assert result is not None
        assert result.name == "Updated Name"

    def test_update_portfolio_not_found(self, mock_repository, portfolio_service):
        """Test updating non-existent portfolio returns None."""
        mock_repository.update.return_value = None
        portfolio_id = uuid4()

        result = portfolio_service.update_portfolio(
            portfolio_id, PortfolioUpdateDTO(name="Test")
        )

        assert result is None


class TestDeletePortfolio:
    """Tests for delete_portfolio method."""

    def test_delete_portfolio_success(
        self, mock_repository, portfolio_service, sample_portfolio_data
    ):
        """Test successful portfolio deletion."""
        mock_repository.get_by_id.return_value = sample_portfolio_data
        mock_repository.delete.return_value = True

        portfolio_id = sample_portfolio_data["id"]
        result = portfolio_service.delete_portfolio(portfolio_id)

        assert result is True
        mock_repository.delete.assert_called_once_with(portfolio_id)

    def test_delete_portfolio_not_found(self, mock_repository, portfolio_service):
        """Test deleting non-existent portfolio returns False."""
        mock_repository.get_by_id.return_value = None
        portfolio_id = uuid4()

        result = portfolio_service.delete_portfolio(portfolio_id)

        assert result is False
        mock_repository.delete.assert_not_called()


class TestDuplicatePortfolio:
    """Tests for duplicate_portfolio method."""

    def test_duplicate_portfolio_success(
        self, mock_repository, portfolio_service, sample_portfolio_data, sample_portfolio_item_data
    ):
        """Test successful portfolio duplication."""
        sample_portfolio_data["items"] = [sample_portfolio_item_data]
        mock_repository.get_by_name.return_value = None  # New name doesn't exist

        new_portfolio = sample_portfolio_data.copy()
        new_portfolio["id"] = uuid4()
        new_portfolio["name"] = "Duplicated Portfolio"
        new_portfolio["items"] = [sample_portfolio_item_data]
        mock_repository.create.return_value = new_portfolio
        mock_repository.add_item.return_value = sample_portfolio_item_data

        # First call returns source, second call returns the new portfolio
        mock_repository.get_by_id.side_effect = [sample_portfolio_data, new_portfolio]

        portfolio_id = sample_portfolio_data["id"]
        result = portfolio_service.duplicate_portfolio(portfolio_id, "Duplicated Portfolio")

        assert result is not None
        assert result.name == "Duplicated Portfolio"
        mock_repository.create.assert_called_once()
        mock_repository.add_item.assert_called_once()

    def test_duplicate_portfolio_source_not_found(self, mock_repository, portfolio_service):
        """Test duplicating non-existent portfolio returns None."""
        mock_repository.get_by_id.return_value = None
        portfolio_id = uuid4()

        result = portfolio_service.duplicate_portfolio(portfolio_id, "New Name")

        assert result is None

    def test_duplicate_portfolio_name_exists(
        self, mock_repository, portfolio_service, sample_portfolio_data
    ):
        """Test duplicating with existing name returns None."""
        mock_repository.get_by_id.return_value = sample_portfolio_data
        mock_repository.get_by_name.return_value = sample_portfolio_data  # Name exists

        portfolio_id = sample_portfolio_data["id"]
        result = portfolio_service.duplicate_portfolio(portfolio_id, "Test Portfolio")

        assert result is None
        mock_repository.create.assert_not_called()


class TestProductManagement:
    """Tests for product management methods."""

    def test_add_product_to_portfolio(
        self, mock_repository, portfolio_service, sample_portfolio_data
    ):
        """Test adding product to portfolio."""
        mock_repository.get_by_id.return_value = sample_portfolio_data
        mock_repository.add_item.return_value = {"id": uuid4()}

        portfolio_id = sample_portfolio_data["id"]
        product_id = uuid4()

        result = portfolio_service.add_product_to_portfolio(
            portfolio_id, product_id, curator_notes="Test notes"
        )

        assert result is True
        mock_repository.add_item.assert_called_once()

    def test_add_product_portfolio_not_found(self, mock_repository, portfolio_service):
        """Test adding product to non-existent portfolio."""
        mock_repository.get_by_id.return_value = None
        portfolio_id = uuid4()
        product_id = uuid4()

        result = portfolio_service.add_product_to_portfolio(portfolio_id, product_id)

        assert result is False

    def test_remove_product_from_portfolio(
        self, mock_repository, portfolio_service
    ):
        """Test removing product from portfolio."""
        mock_repository.remove_item.return_value = True

        portfolio_id = uuid4()
        product_id = uuid4()

        result = portfolio_service.remove_product_from_portfolio(portfolio_id, product_id)

        assert result is True
        mock_repository.remove_item.assert_called_once_with(portfolio_id, product_id)

    def test_reorder_products_success(
        self, mock_repository, portfolio_service, sample_portfolio_data, sample_portfolio_item_data
    ):
        """Test reordering products successfully."""
        product_id_1 = uuid4()
        product_id_2 = uuid4()

        item1 = sample_portfolio_item_data.copy()
        item1["product_id"] = product_id_1
        item2 = sample_portfolio_item_data.copy()
        item2["product_id"] = product_id_2

        sample_portfolio_data["items"] = [item1, item2]
        mock_repository.get_by_id.return_value = sample_portfolio_data
        mock_repository.update_items_sort_orders.return_value = True

        portfolio_id = sample_portfolio_data["id"]
        result = portfolio_service.reorder_products(
            portfolio_id, [product_id_2, product_id_1]  # Reverse order
        )

        assert result is True
        mock_repository.update_items_sort_orders.assert_called_once()

    def test_reorder_products_missing_products(
        self, mock_repository, portfolio_service, sample_portfolio_data, sample_portfolio_item_data
    ):
        """Test reordering with missing products fails."""
        product_id_1 = uuid4()
        sample_portfolio_item_data["product_id"] = product_id_1
        sample_portfolio_data["items"] = [sample_portfolio_item_data]
        mock_repository.get_by_id.return_value = sample_portfolio_data

        portfolio_id = sample_portfolio_data["id"]
        # Missing the existing product, adding unknown one
        result = portfolio_service.reorder_products(portfolio_id, [uuid4()])

        assert result is False
        mock_repository.update_items_sort_orders.assert_not_called()


class TestCreateFromFilters:
    """Tests for create_from_filters method."""

    @patch("app.services.portfolio_service.product_repository")
    def test_create_from_filters_success(
        self, mock_product_repo, mock_repository, portfolio_service, sample_portfolio_data
    ):
        """Test creating portfolio from filters with matching products."""
        product_1 = {"id": uuid4(), "name": "Product 1"}
        product_2 = {"id": uuid4(), "name": "Product 2"}
        mock_product_repo.get_all.return_value = ([product_1, product_2], 2)

        mock_repository.get_by_name.return_value = None
        mock_repository.create.return_value = sample_portfolio_data
        mock_repository.add_item.return_value = {"id": uuid4()}
        mock_repository.get_by_id.return_value = sample_portfolio_data

        filters = ProductFilterDTO(status=ProductStatus.ACTIVE)
        result = portfolio_service.create_from_filters(
            name="Test Portfolio",
            filters=filters,
        )

        assert result is not None
        mock_repository.create.assert_called_once()
        assert mock_repository.add_item.call_count == 2

    @patch("app.services.portfolio_service.product_repository")
    def test_create_from_filters_name_exists(
        self, mock_product_repo, mock_repository, portfolio_service, sample_portfolio_data
    ):
        """Test creating portfolio with existing name fails."""
        mock_repository.get_by_name.return_value = sample_portfolio_data

        filters = ProductFilterDTO()
        result = portfolio_service.create_from_filters(
            name="Test Portfolio",
            filters=filters,
        )

        assert result is None
        mock_repository.create.assert_not_called()


class TestShareToken:
    """Tests for share token functionality."""

    def test_get_share_token_success(
        self, mock_repository, portfolio_service, sample_portfolio_data
    ):
        """Test generating share token."""
        mock_repository.get_by_id.return_value = sample_portfolio_data
        portfolio_id = sample_portfolio_data["id"]

        result = portfolio_service.get_share_token(portfolio_id)

        assert result is not None
        assert result.portfolio_id == portfolio_id
        assert result.token is not None
        assert result.expires_at is not None

    def test_get_share_token_portfolio_not_found(self, mock_repository, portfolio_service):
        """Test generating token for non-existent portfolio."""
        mock_repository.get_by_id.return_value = None
        portfolio_id = uuid4()

        result = portfolio_service.get_share_token(portfolio_id)

        assert result is None

    def test_get_by_share_token_success(
        self, mock_repository, portfolio_service, sample_portfolio_data
    ):
        """Test getting portfolio by valid share token."""
        mock_repository.get_by_id.return_value = sample_portfolio_data
        portfolio_id = sample_portfolio_data["id"]

        # First generate a token
        token_result = portfolio_service.get_share_token(portfolio_id)

        # Then retrieve portfolio by token
        result = portfolio_service.get_by_share_token(token_result.token)

        assert result is not None
        assert result.id == portfolio_id

    def test_get_by_share_token_invalid(self, mock_repository, portfolio_service):
        """Test getting portfolio by invalid token."""
        result = portfolio_service.get_by_share_token("invalid-token")

        assert result is None

    def test_get_by_share_token_inactive_portfolio(
        self, mock_repository, portfolio_service, sample_portfolio_data
    ):
        """Test that inactive portfolios are not returned via share token."""
        mock_repository.get_by_id.return_value = sample_portfolio_data
        portfolio_id = sample_portfolio_data["id"]

        # Generate token
        token_result = portfolio_service.get_share_token(portfolio_id)

        # Make portfolio inactive
        sample_portfolio_data["is_active"] = False

        # Try to retrieve - should fail
        result = portfolio_service.get_by_share_token(token_result.token)

        assert result is None
