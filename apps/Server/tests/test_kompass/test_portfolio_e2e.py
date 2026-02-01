"""End-to-end tests for Portfolio workflows.

Tests cover:
- Full CRUD workflow (Create -> Read -> Update -> Delete)
- Product management (add, remove, reorder products)
- Portfolio duplication
- Create from product filters
- Share token functionality
- PDF generation (mocked)
"""

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


# =============================================================================
# SERVICE FIXTURES
# =============================================================================


@pytest.fixture
def mock_repository():
    """Create a mock portfolio repository."""
    return MagicMock()


@pytest.fixture
def portfolio_service(mock_repository):
    """Create a PortfolioService with mocked repository."""
    return PortfolioService(repository=mock_repository)


# =============================================================================
# CRUD WORKFLOW TESTS
# =============================================================================


class TestPortfolioCRUDWorkflow:
    """Tests for complete CRUD workflow."""

    def test_create_read_update_delete_flow(
        self, portfolio_service, mock_repository, sample_portfolio_data
    ):
        """Test complete portfolio lifecycle."""
        portfolio_id = sample_portfolio_data["id"]

        # CREATE
        mock_repository.create.return_value = sample_portfolio_data
        mock_repository.get_by_id.return_value = sample_portfolio_data

        create_request = PortfolioCreateDTO(
            name="Test Portfolio",
            description="Test description",
        )
        created = portfolio_service.create_portfolio(create_request)

        assert created is not None
        assert created.name == "Test Portfolio"
        mock_repository.create.assert_called_once()

        # READ
        mock_repository.get_by_id.return_value = sample_portfolio_data
        retrieved = portfolio_service.get_portfolio(portfolio_id)

        assert retrieved is not None
        assert retrieved.id == portfolio_id
        mock_repository.get_by_id.assert_called_with(portfolio_id)

        # UPDATE
        updated_data = sample_portfolio_data.copy()
        updated_data["name"] = "Updated Portfolio Name"
        mock_repository.update.return_value = updated_data

        update_request = PortfolioUpdateDTO(name="Updated Portfolio Name")
        updated = portfolio_service.update_portfolio(portfolio_id, update_request)

        assert updated is not None
        assert updated.name == "Updated Portfolio Name"

        # DELETE
        mock_repository.get_by_id.return_value = sample_portfolio_data
        mock_repository.delete.return_value = True
        deleted = portfolio_service.delete_portfolio(portfolio_id)

        assert deleted is True
        mock_repository.delete.assert_called_once_with(portfolio_id)

    def test_create_portfolio_with_items(
        self, portfolio_service, mock_repository, sample_portfolio_with_items
    ):
        """Test creating portfolio with initial items."""
        mock_repository.create.return_value = sample_portfolio_with_items
        mock_repository.get_by_id.return_value = sample_portfolio_with_items
        mock_repository.add_item.return_value = sample_portfolio_with_items["items"][0]

        product_id = uuid4()
        request = PortfolioCreateDTO(
            name="Test Portfolio",
            items=[
                PortfolioItemCreateDTO(product_id=product_id, sort_order=0),
            ],
        )

        result = portfolio_service.create_portfolio(request)

        assert result is not None
        mock_repository.add_item.assert_called()

    def test_create_portfolio_fails(self, portfolio_service, mock_repository):
        """Test that None is returned when creation fails."""
        mock_repository.create.return_value = None

        request = PortfolioCreateDTO(name="Test Portfolio")

        result = portfolio_service.create_portfolio(request)

        assert result is None


# =============================================================================
# PRODUCT MANAGEMENT TESTS
# =============================================================================


class TestPortfolioProducts:
    """Tests for product management within portfolios."""

    def test_add_product_to_portfolio(
        self, portfolio_service, mock_repository, sample_portfolio_data
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

    def test_add_product_portfolio_not_found(
        self, portfolio_service, mock_repository
    ):
        """Test adding product to non-existent portfolio."""
        mock_repository.get_by_id.return_value = None
        portfolio_id = uuid4()
        product_id = uuid4()

        result = portfolio_service.add_product_to_portfolio(portfolio_id, product_id)

        assert result is False

    def test_remove_product_from_portfolio(
        self, portfolio_service, mock_repository
    ):
        """Test removing product from portfolio."""
        mock_repository.remove_item.return_value = True

        portfolio_id = uuid4()
        product_id = uuid4()

        result = portfolio_service.remove_product_from_portfolio(portfolio_id, product_id)

        assert result is True
        mock_repository.remove_item.assert_called_once_with(portfolio_id, product_id)

    def test_reorder_products_success(
        self, portfolio_service, mock_repository, sample_portfolio_with_items
    ):
        """Test reordering products successfully."""
        # Include all 3 product IDs from the fixture to pass validation
        product_id_1 = sample_portfolio_with_items["items"][0]["product_id"]
        product_id_2 = sample_portfolio_with_items["items"][1]["product_id"]
        product_id_3 = sample_portfolio_with_items["items"][2]["product_id"]

        mock_repository.get_by_id.return_value = sample_portfolio_with_items
        mock_repository.update_items_sort_orders.return_value = True

        portfolio_id = sample_portfolio_with_items["id"]
        # Reverse order: [3, 2, 1] instead of [1, 2, 3]
        result = portfolio_service.reorder_products(
            portfolio_id, [product_id_3, product_id_2, product_id_1]
        )

        assert result is True
        mock_repository.update_items_sort_orders.assert_called_once()

    def test_reorder_products_missing_products(
        self, portfolio_service, mock_repository, sample_portfolio_with_items
    ):
        """Test reordering with missing products fails."""
        mock_repository.get_by_id.return_value = sample_portfolio_with_items

        portfolio_id = sample_portfolio_with_items["id"]
        result = portfolio_service.reorder_products(portfolio_id, [uuid4()])

        assert result is False
        mock_repository.update_items_sort_orders.assert_not_called()


# =============================================================================
# DUPLICATION TESTS
# =============================================================================


class TestPortfolioDuplication:
    """Tests for portfolio duplication."""

    def test_duplicate_portfolio_success(
        self, portfolio_service, mock_repository, sample_portfolio_with_items
    ):
        """Test successful portfolio duplication."""
        mock_repository.get_by_name.return_value = None

        new_portfolio = sample_portfolio_with_items.copy()
        new_portfolio["id"] = uuid4()
        new_portfolio["name"] = "Duplicated Portfolio"
        mock_repository.create.return_value = new_portfolio
        mock_repository.add_item.return_value = sample_portfolio_with_items["items"][0]

        mock_repository.get_by_id.side_effect = [sample_portfolio_with_items, new_portfolio]

        portfolio_id = sample_portfolio_with_items["id"]
        result = portfolio_service.duplicate_portfolio(portfolio_id, "Duplicated Portfolio")

        assert result is not None
        assert result.name == "Duplicated Portfolio"
        mock_repository.create.assert_called_once()

    def test_duplicate_portfolio_source_not_found(
        self, portfolio_service, mock_repository
    ):
        """Test duplicating non-existent portfolio returns None."""
        mock_repository.get_by_id.return_value = None
        portfolio_id = uuid4()

        result = portfolio_service.duplicate_portfolio(portfolio_id, "New Name")

        assert result is None

    def test_duplicate_portfolio_name_exists(
        self, portfolio_service, mock_repository, sample_portfolio_data
    ):
        """Test duplicating with existing name returns None."""
        mock_repository.get_by_id.return_value = sample_portfolio_data
        mock_repository.get_by_name.return_value = sample_portfolio_data

        portfolio_id = sample_portfolio_data["id"]
        result = portfolio_service.duplicate_portfolio(portfolio_id, "Test Portfolio")

        assert result is None
        mock_repository.create.assert_not_called()


# =============================================================================
# CREATE FROM FILTERS TESTS
# =============================================================================


class TestCreateFromFilters:
    """Tests for creating portfolios from product filters."""

    @patch("app.services.portfolio_service.product_repository")
    def test_create_from_filters_success(
        self, mock_product_repo, portfolio_service, mock_repository, sample_portfolio_data
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
        self, mock_product_repo, portfolio_service, mock_repository, sample_portfolio_data
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

    @patch("app.services.portfolio_service.product_repository")
    def test_create_from_filters_no_products(
        self, mock_product_repo, portfolio_service, mock_repository, sample_portfolio_data
    ):
        """Test creating portfolio when no products match filters."""
        mock_product_repo.get_all.return_value = ([], 0)
        mock_repository.get_by_name.return_value = None
        mock_repository.create.return_value = sample_portfolio_data
        mock_repository.get_by_id.return_value = sample_portfolio_data

        filters = ProductFilterDTO(status=ProductStatus.ACTIVE)
        result = portfolio_service.create_from_filters(
            name="Empty Portfolio",
            filters=filters,
        )

        assert result is not None
        mock_repository.add_item.assert_not_called()


# =============================================================================
# SHARE TOKEN TESTS
# =============================================================================


class TestShareToken:
    """Tests for share token functionality."""

    def test_get_share_token_success(
        self, portfolio_service, mock_repository, sample_portfolio_data
    ):
        """Test generating share token."""
        mock_repository.get_by_id.return_value = sample_portfolio_data
        portfolio_id = sample_portfolio_data["id"]

        result = portfolio_service.get_share_token(portfolio_id)

        assert result is not None
        assert result.portfolio_id == portfolio_id
        assert result.token is not None
        assert result.expires_at is not None

    def test_get_share_token_portfolio_not_found(
        self, portfolio_service, mock_repository
    ):
        """Test generating token for non-existent portfolio."""
        mock_repository.get_by_id.return_value = None
        portfolio_id = uuid4()

        result = portfolio_service.get_share_token(portfolio_id)

        assert result is None

    def test_get_by_share_token_success(
        self, portfolio_service, mock_repository, sample_portfolio_data
    ):
        """Test getting portfolio by valid share token."""
        mock_repository.get_by_id.return_value = sample_portfolio_data
        portfolio_id = sample_portfolio_data["id"]

        token_result = portfolio_service.get_share_token(portfolio_id)
        result = portfolio_service.get_by_share_token(token_result.token)

        assert result is not None
        assert result.id == portfolio_id

    def test_get_by_share_token_invalid(
        self, portfolio_service, mock_repository
    ):
        """Test getting portfolio by invalid token."""
        result = portfolio_service.get_by_share_token("invalid-token")

        assert result is None

    def test_get_by_share_token_inactive_portfolio(
        self, portfolio_service, mock_repository, sample_portfolio_data
    ):
        """Test that inactive portfolios are not returned via share token."""
        mock_repository.get_by_id.return_value = sample_portfolio_data
        portfolio_id = sample_portfolio_data["id"]

        token_result = portfolio_service.get_share_token(portfolio_id)

        sample_portfolio_data["is_active"] = False
        result = portfolio_service.get_by_share_token(token_result.token)

        assert result is None


# =============================================================================
# LIST AND FILTER TESTS
# =============================================================================


class TestListPortfolios:
    """Tests for listing portfolios."""

    def test_list_portfolios_with_pagination(
        self, portfolio_service, mock_repository, sample_portfolio_data
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
        self, portfolio_service, mock_repository, sample_portfolio_data
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
        self, portfolio_service, mock_repository, sample_portfolio_data
    ):
        """Test searching portfolios."""
        mock_repository.search.return_value = [sample_portfolio_data]

        filters = PortfolioFilterDTO(search="test")
        result = portfolio_service.list_portfolios(filters=filters)

        mock_repository.search.assert_called_once()
        assert len(result.items) == 1

    def test_list_portfolios_empty_result(
        self, portfolio_service, mock_repository
    ):
        """Test empty result handling."""
        mock_repository.get_all.return_value = ([], 0)

        result = portfolio_service.list_portfolios()

        assert len(result.items) == 0
        assert result.pagination.total == 0
        assert result.pagination.pages == 0


# =============================================================================
# UPDATE TESTS
# =============================================================================


class TestUpdatePortfolio:
    """Tests for portfolio update operations."""

    def test_update_portfolio_success(
        self, portfolio_service, mock_repository, sample_portfolio_data
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

    def test_update_portfolio_not_found(
        self, portfolio_service, mock_repository
    ):
        """Test updating non-existent portfolio returns None."""
        mock_repository.update.return_value = None
        portfolio_id = uuid4()

        result = portfolio_service.update_portfolio(
            portfolio_id, PortfolioUpdateDTO(name="Test")
        )

        assert result is None


# =============================================================================
# DELETE TESTS
# =============================================================================


class TestDeletePortfolio:
    """Tests for portfolio deletion."""

    def test_delete_portfolio_success(
        self, portfolio_service, mock_repository, sample_portfolio_data
    ):
        """Test successful portfolio deletion."""
        mock_repository.get_by_id.return_value = sample_portfolio_data
        mock_repository.delete.return_value = True

        portfolio_id = sample_portfolio_data["id"]
        result = portfolio_service.delete_portfolio(portfolio_id)

        assert result is True
        mock_repository.delete.assert_called_once_with(portfolio_id)

    def test_delete_portfolio_not_found(
        self, portfolio_service, mock_repository
    ):
        """Test deleting non-existent portfolio returns False."""
        mock_repository.get_by_id.return_value = None
        portfolio_id = uuid4()

        result = portfolio_service.delete_portfolio(portfolio_id)

        assert result is False
        mock_repository.delete.assert_not_called()


# =============================================================================
# GET PORTFOLIO TESTS
# =============================================================================


class TestGetPortfolio:
    """Tests for getting individual portfolios."""

    def test_get_portfolio_found(
        self, portfolio_service, mock_repository, sample_portfolio_data
    ):
        """Test getting an existing portfolio."""
        mock_repository.get_by_id.return_value = sample_portfolio_data
        portfolio_id = sample_portfolio_data["id"]

        result = portfolio_service.get_portfolio(portfolio_id)

        assert result is not None
        assert result.id == portfolio_id
        mock_repository.get_by_id.assert_called_once_with(portfolio_id)

    def test_get_portfolio_not_found(
        self, portfolio_service, mock_repository
    ):
        """Test that None is returned for non-existent portfolio."""
        mock_repository.get_by_id.return_value = None
        portfolio_id = uuid4()

        result = portfolio_service.get_portfolio(portfolio_id)

        assert result is None
