"""Portfolio service for curated product collections.

This service provides business logic for portfolio management including:
- CRUD operations for portfolios
- Portfolio duplication
- Product management (add, remove, reorder)
- Auto-creation from product filters
- Share token generation and validation for public access
"""

import math
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from jose import JWTError, jwt

from app.config.settings import get_settings
from app.models.kompass_dto import (
    PaginationDTO,
    PortfolioCreateDTO,
    PortfolioFilterDTO,
    PortfolioItemResponseDTO,
    PortfolioListResponseDTO,
    PortfolioPublicResponseDTO,
    PortfolioResponseDTO,
    PortfolioShareTokenResponseDTO,
    PortfolioUpdateDTO,
    ProductFilterDTO,
)
from app.repository.kompass_repository import (
    PortfolioRepository,
    portfolio_repository,
    product_repository,
)


# Share token expiration in days (configurable via environment)
SHARE_TOKEN_EXPIRE_DAYS = 30


class PortfolioService:
    """Service layer for portfolio management operations.

    This service wraps the PortfolioRepository with business logic for:
    - Portfolio CRUD with DTO mapping
    - Portfolio duplication
    - Product management (add, remove, reorder)
    - Auto-creation from product filters
    - Share token generation and validation
    """

    def __init__(
        self,
        repository: Optional[PortfolioRepository] = None,
    ) -> None:
        """Initialize the PortfolioService.

        Args:
            repository: PortfolioRepository instance (uses singleton if not provided)
        """
        self._repository = repository or portfolio_repository
        self._settings = get_settings()

    def _map_item_to_response_dto(
        self, item_dict: dict
    ) -> PortfolioItemResponseDTO:
        """Map a portfolio item dictionary to PortfolioItemResponseDTO.

        Args:
            item_dict: Item dictionary from repository

        Returns:
            PortfolioItemResponseDTO instance
        """
        return PortfolioItemResponseDTO(
            id=item_dict["id"],
            portfolio_id=item_dict["portfolio_id"],
            product_id=item_dict["product_id"],
            product_name=item_dict.get("product_name"),
            product_sku=item_dict.get("product_sku"),
            sort_order=item_dict.get("sort_order", 0),
            notes=item_dict.get("notes"),
            created_at=item_dict["created_at"],
            updated_at=item_dict["updated_at"],
        )

    def _map_to_response_dto(
        self, portfolio_dict: dict
    ) -> PortfolioResponseDTO:
        """Map a portfolio dictionary from repository to PortfolioResponseDTO.

        Args:
            portfolio_dict: Portfolio dictionary from repository

        Returns:
            PortfolioResponseDTO instance
        """
        items = [
            self._map_item_to_response_dto(item)
            for item in portfolio_dict.get("items", [])
        ]

        return PortfolioResponseDTO(
            id=portfolio_dict["id"],
            name=portfolio_dict["name"],
            description=portfolio_dict.get("description"),
            niche_id=portfolio_dict.get("niche_id"),
            niche_name=portfolio_dict.get("niche_name"),
            is_active=portfolio_dict.get("is_active", True),
            items=items,
            item_count=portfolio_dict.get("item_count", len(items)),
            created_at=portfolio_dict["created_at"],
            updated_at=portfolio_dict["updated_at"],
        )

    def _map_to_public_response_dto(
        self, portfolio_dict: dict
    ) -> PortfolioPublicResponseDTO:
        """Map a portfolio dictionary to PortfolioPublicResponseDTO for public access.

        Args:
            portfolio_dict: Portfolio dictionary from repository

        Returns:
            PortfolioPublicResponseDTO instance
        """
        items = [
            self._map_item_to_response_dto(item)
            for item in portfolio_dict.get("items", [])
        ]

        return PortfolioPublicResponseDTO(
            id=portfolio_dict["id"],
            name=portfolio_dict["name"],
            description=portfolio_dict.get("description"),
            niche_name=portfolio_dict.get("niche_name"),
            items=items,
            item_count=portfolio_dict.get("item_count", len(items)),
            created_at=portfolio_dict["created_at"],
        )

    # =========================================================================
    # CRUD Operations
    # =========================================================================

    def create_portfolio(
        self, request: PortfolioCreateDTO
    ) -> Optional[PortfolioResponseDTO]:
        """Create a new portfolio.

        Args:
            request: PortfolioCreateDTO with portfolio details

        Returns:
            PortfolioResponseDTO if created successfully, None otherwise
        """
        portfolio = self._repository.create(
            name=request.name,
            description=request.description,
            niche_id=request.niche_id,
            is_active=request.is_active,
        )

        if not portfolio:
            print("ERROR [PortfolioService]: Failed to create portfolio")
            return None

        portfolio_id = portfolio["id"]

        # Add items if provided
        if request.items:
            for item in request.items:
                self._repository.add_item(
                    portfolio_id=portfolio_id,
                    product_id=item.product_id,
                    sort_order=item.sort_order,
                    notes=item.notes,
                )

            # Refetch to get updated items
            portfolio = self._repository.get_by_id(portfolio_id)
            if not portfolio:
                print("ERROR [PortfolioService]: Failed to fetch created portfolio")
                return None

        print(f"INFO [PortfolioService]: Created portfolio {portfolio_id}")
        return self._map_to_response_dto(portfolio)

    def get_portfolio(
        self, portfolio_id: UUID
    ) -> Optional[PortfolioResponseDTO]:
        """Get a portfolio by ID with all products.

        Args:
            portfolio_id: Portfolio UUID

        Returns:
            PortfolioResponseDTO if found, None otherwise
        """
        portfolio = self._repository.get_by_id(portfolio_id)
        if not portfolio:
            print(f"INFO [PortfolioService]: Portfolio {portfolio_id} not found")
            return None

        return self._map_to_response_dto(portfolio)

    def list_portfolios(
        self,
        filters: Optional[PortfolioFilterDTO] = None,
        page: int = 1,
        limit: int = 20,
    ) -> PortfolioListResponseDTO:
        """List portfolios with filtering and pagination.

        Args:
            filters: PortfolioFilterDTO with filter parameters
            page: Page number (1-indexed)
            limit: Number of items per page

        Returns:
            PortfolioListResponseDTO with items and pagination
        """
        filters = filters or PortfolioFilterDTO()

        # If search is provided, use search method instead
        if filters.search:
            items = self._repository.search(filters.search, limit=limit * page)
            # Apply other filters post-search
            if filters.niche_id:
                items = [i for i in items if i.get("niche_id") == filters.niche_id]
            if filters.is_active is not None:
                items = [i for i in items if i.get("is_active") == filters.is_active]

            total = len(items)
            # Apply pagination
            start = (page - 1) * limit
            end = start + limit
            items = items[start:end]
        else:
            items, total = self._repository.get_all(
                page=page,
                limit=limit,
                niche_id=filters.niche_id,
                is_active=filters.is_active,
            )

        portfolios = [self._map_to_response_dto(item) for item in items]
        pages = math.ceil(total / limit) if limit > 0 else 0

        pagination = PaginationDTO(
            page=page,
            limit=limit,
            total=total,
            pages=pages,
        )

        print(
            f"INFO [PortfolioService]: Listed {len(portfolios)} portfolios "
            f"(page {page}/{pages})"
        )

        return PortfolioListResponseDTO(
            items=portfolios,
            pagination=pagination,
        )

    def update_portfolio(
        self, portfolio_id: UUID, request: PortfolioUpdateDTO
    ) -> Optional[PortfolioResponseDTO]:
        """Update a portfolio.

        Args:
            portfolio_id: Portfolio UUID
            request: PortfolioUpdateDTO with fields to update

        Returns:
            Updated PortfolioResponseDTO if successful, None if not found
        """
        # Build kwargs only for non-None fields
        update_kwargs = {}
        if request.name is not None:
            update_kwargs["name"] = request.name
        if request.description is not None:
            update_kwargs["description"] = request.description
        if request.niche_id is not None:
            update_kwargs["niche_id"] = request.niche_id
        if request.is_active is not None:
            update_kwargs["is_active"] = request.is_active

        portfolio = self._repository.update(portfolio_id, **update_kwargs)
        if not portfolio:
            print(f"INFO [PortfolioService]: Portfolio {portfolio_id} not found")
            return None

        print(f"INFO [PortfolioService]: Updated portfolio {portfolio_id}")
        return self._map_to_response_dto(portfolio)

    def delete_portfolio(self, portfolio_id: UUID) -> bool:
        """Soft delete a portfolio (sets is_active=False).

        Args:
            portfolio_id: Portfolio UUID

        Returns:
            True if deleted, False if not found
        """
        # Check if portfolio exists
        existing = self._repository.get_by_id(portfolio_id)
        if not existing:
            return False

        success = self._repository.delete(portfolio_id)
        if success:
            print(f"INFO [PortfolioService]: Deleted portfolio {portfolio_id}")

        return success

    # =========================================================================
    # Portfolio Duplication
    # =========================================================================

    def duplicate_portfolio(
        self, portfolio_id: UUID, new_name: str
    ) -> Optional[PortfolioResponseDTO]:
        """Duplicate a portfolio with a new name.

        Copies all portfolio items with their notes and sort_order.

        Args:
            portfolio_id: Source portfolio UUID
            new_name: Name for the new portfolio

        Returns:
            PortfolioResponseDTO for the new portfolio, None if source not found
        """
        # Get source portfolio
        source = self._repository.get_by_id(portfolio_id)
        if not source:
            print(f"INFO [PortfolioService]: Source portfolio {portfolio_id} not found")
            return None

        # Check if name already exists
        existing = self._repository.get_by_name(new_name)
        if existing:
            print(f"WARN [PortfolioService]: Portfolio name '{new_name}' already exists")
            return None

        # Create new portfolio
        new_portfolio = self._repository.create(
            name=new_name,
            description=source.get("description"),
            niche_id=source.get("niche_id"),
            is_active=source.get("is_active", True),
        )

        if not new_portfolio:
            print("ERROR [PortfolioService]: Failed to create duplicate portfolio")
            return None

        new_portfolio_id = new_portfolio["id"]

        # Copy all items
        for item in source.get("items", []):
            self._repository.add_item(
                portfolio_id=new_portfolio_id,
                product_id=item["product_id"],
                sort_order=item.get("sort_order", 0),
                notes=item.get("notes"),
            )

        # Refetch to get complete portfolio with items
        new_portfolio = self._repository.get_by_id(new_portfolio_id)
        if not new_portfolio:
            print("ERROR [PortfolioService]: Failed to fetch duplicated portfolio")
            return None

        print(
            f"INFO [PortfolioService]: Duplicated portfolio {portfolio_id} "
            f"to {new_portfolio_id} with name '{new_name}'"
        )

        return self._map_to_response_dto(new_portfolio)

    # =========================================================================
    # Product Management
    # =========================================================================

    def add_product_to_portfolio(
        self,
        portfolio_id: UUID,
        product_id: UUID,
        curator_notes: Optional[str] = None,
    ) -> bool:
        """Add a product to a portfolio.

        Args:
            portfolio_id: Portfolio UUID
            product_id: Product UUID to add
            curator_notes: Optional notes about the product

        Returns:
            True if successful, False otherwise
        """
        # Check if portfolio exists
        portfolio = self._repository.get_by_id(portfolio_id)
        if not portfolio:
            print(f"INFO [PortfolioService]: Portfolio {portfolio_id} not found")
            return False

        # Get current max sort_order
        items = portfolio.get("items", [])
        max_sort = max((i.get("sort_order", 0) for i in items), default=-1)

        result = self._repository.add_item(
            portfolio_id=portfolio_id,
            product_id=product_id,
            sort_order=max_sort + 1,
            notes=curator_notes,
        )

        if result:
            print(
                f"INFO [PortfolioService]: Added product {product_id} "
                f"to portfolio {portfolio_id}"
            )
            return True

        return False

    def remove_product_from_portfolio(
        self, portfolio_id: UUID, product_id: UUID
    ) -> bool:
        """Remove a product from a portfolio.

        Args:
            portfolio_id: Portfolio UUID
            product_id: Product UUID to remove

        Returns:
            True if successful, False otherwise
        """
        success = self._repository.remove_item(portfolio_id, product_id)

        if success:
            print(
                f"INFO [PortfolioService]: Removed product {product_id} "
                f"from portfolio {portfolio_id}"
            )

        return success

    def reorder_products(
        self, portfolio_id: UUID, product_ids: List[UUID]
    ) -> bool:
        """Reorder products in a portfolio.

        Updates sort_order for all products based on their position in the list.

        Args:
            portfolio_id: Portfolio UUID
            product_ids: List of product UUIDs in desired order

        Returns:
            True if successful, False otherwise
        """
        # Validate portfolio exists
        portfolio = self._repository.get_by_id(portfolio_id)
        if not portfolio:
            print(f"INFO [PortfolioService]: Portfolio {portfolio_id} not found")
            return False

        # Get current product IDs in portfolio
        current_product_ids = set(
            item["product_id"] for item in portfolio.get("items", [])
        )

        # Validate all provided product_ids are in the portfolio
        provided_ids = set(product_ids)
        if provided_ids != current_product_ids:
            missing = current_product_ids - provided_ids
            extra = provided_ids - current_product_ids
            if missing:
                print(
                    f"WARN [PortfolioService]: Missing products in reorder: {missing}"
                )
            if extra:
                print(
                    f"WARN [PortfolioService]: Extra products in reorder: {extra}"
                )
            return False

        # Build list of (product_id, sort_order) tuples
        items = [(pid, idx) for idx, pid in enumerate(product_ids)]

        success = self._repository.update_items_sort_orders(portfolio_id, items)

        if success:
            print(
                f"INFO [PortfolioService]: Reordered {len(product_ids)} products "
                f"in portfolio {portfolio_id}"
            )

        return success

    # =========================================================================
    # Auto-creation from Filters
    # =========================================================================

    def create_from_filters(
        self,
        name: str,
        filters: ProductFilterDTO,
        description: Optional[str] = None,
        niche_id: Optional[UUID] = None,
    ) -> Optional[PortfolioResponseDTO]:
        """Create a portfolio from product filter criteria.

        Queries products matching the filters and adds them all to a new portfolio.

        Args:
            name: Name for the new portfolio
            filters: ProductFilterDTO with filter criteria
            description: Optional portfolio description
            niche_id: Optional niche to associate with portfolio

        Returns:
            PortfolioResponseDTO if created successfully, None otherwise
        """
        # Check if name already exists
        existing = self._repository.get_by_name(name)
        if existing:
            print(f"WARN [PortfolioService]: Portfolio name '{name}' already exists")
            return None

        # Get products matching filters
        products, total = product_repository.get_all(
            page=1,
            limit=1000,  # Get all matching products
            category_id=filters.category_id,
            supplier_id=filters.supplier_id,
            status=filters.status.value if filters.status else "active",
            min_price=filters.min_price,
            max_price=filters.max_price,
            search=filters.search,
            tag_ids=filters.tag_ids,
        )

        if not products:
            print("INFO [PortfolioService]: No products match the filter criteria")
            # Still create empty portfolio
            pass

        # Create portfolio
        portfolio = self._repository.create(
            name=name,
            description=description,
            niche_id=niche_id,
            is_active=True,
        )

        if not portfolio:
            print("ERROR [PortfolioService]: Failed to create portfolio from filters")
            return None

        portfolio_id = portfolio["id"]

        # Add all matching products
        for idx, product in enumerate(products):
            self._repository.add_item(
                portfolio_id=portfolio_id,
                product_id=product["id"],
                sort_order=idx,
                notes=None,
            )

        # Refetch complete portfolio
        portfolio = self._repository.get_by_id(portfolio_id)
        if not portfolio:
            print("ERROR [PortfolioService]: Failed to fetch created portfolio")
            return None

        print(
            f"INFO [PortfolioService]: Created portfolio {portfolio_id} from filters "
            f"with {len(products)} products"
        )

        return self._map_to_response_dto(portfolio)

    # =========================================================================
    # Share Token Functionality
    # =========================================================================

    def get_share_token(
        self, portfolio_id: UUID
    ) -> Optional[PortfolioShareTokenResponseDTO]:
        """Generate a share token for public portfolio access.

        Creates a JWT token that can be used to access the portfolio without
        authentication.

        Args:
            portfolio_id: Portfolio UUID

        Returns:
            PortfolioShareTokenResponseDTO with token, or None if portfolio not found
        """
        # Verify portfolio exists
        portfolio = self._repository.get_by_id(portfolio_id)
        if not portfolio:
            print(f"INFO [PortfolioService]: Portfolio {portfolio_id} not found")
            return None

        # Generate JWT token
        expire = datetime.utcnow() + timedelta(days=SHARE_TOKEN_EXPIRE_DAYS)
        payload = {
            "sub": str(portfolio_id),
            "type": "portfolio_share",
            "exp": expire,
        }

        token = jwt.encode(
            payload,
            self._settings.JWT_SECRET_KEY,
            algorithm=self._settings.JWT_ALGORITHM,
        )

        print(
            f"INFO [PortfolioService]: Generated share token for portfolio {portfolio_id}"
        )

        return PortfolioShareTokenResponseDTO(
            token=token,
            portfolio_id=portfolio_id,
            expires_at=expire,
        )

    def get_by_share_token(
        self, token: str
    ) -> Optional[PortfolioPublicResponseDTO]:
        """Get a portfolio by its share token.

        Validates the token and returns the portfolio for public viewing.
        This method does NOT require authentication.

        Args:
            token: JWT share token

        Returns:
            PortfolioPublicResponseDTO if token valid and portfolio exists,
            None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                self._settings.JWT_SECRET_KEY,
                algorithms=[self._settings.JWT_ALGORITHM],
            )

            # Verify token type
            if payload.get("type") != "portfolio_share":
                print("WARN [PortfolioService]: Invalid share token type")
                return None

            portfolio_id_str = payload.get("sub")
            if not portfolio_id_str:
                print("WARN [PortfolioService]: Share token missing portfolio ID")
                return None

            portfolio_id = UUID(portfolio_id_str)

        except JWTError as e:
            print(f"WARN [PortfolioService]: Invalid or expired share token: {e}")
            return None
        except ValueError as e:
            print(f"WARN [PortfolioService]: Invalid portfolio ID in token: {e}")
            return None

        # Get portfolio
        portfolio = self._repository.get_by_id(portfolio_id)
        if not portfolio:
            print(f"INFO [PortfolioService]: Portfolio {portfolio_id} not found")
            return None

        # Check if portfolio is active
        if not portfolio.get("is_active", True):
            print(f"INFO [PortfolioService]: Portfolio {portfolio_id} is inactive")
            return None

        print(f"INFO [PortfolioService]: Accessed portfolio {portfolio_id} via share token")

        return self._map_to_public_response_dto(portfolio)


# Singleton instance
portfolio_service = PortfolioService()
