"""Portfolio API routes for curated product collections.

This module provides RESTful endpoints for portfolio management, including:
- CRUD operations for portfolios
- Product management (add, remove, reorder)
- Portfolio duplication
- Auto-creation from product filters
- Public share links
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from starlette import status

from app.api.dependencies import get_current_user
from app.api.rbac_dependencies import require_roles
from app.models.kompass_dto import (
    PortfolioAddProductRequestDTO,
    PortfolioCreateDTO,
    PortfolioDuplicateRequestDTO,
    PortfolioFilterDTO,
    PortfolioFromFiltersRequestDTO,
    PortfolioListResponseDTO,
    PortfolioPublicResponseDTO,
    PortfolioResponseDTO,
    PortfolioShareTokenResponseDTO,
    PortfolioUpdateDTO,
    ReorderProductsRequestDTO,
)
from app.services.portfolio_service import portfolio_service

router = APIRouter(tags=["Portfolios"])


# =============================================================================
# List and Search Endpoints
# =============================================================================


@router.get("", response_model=PortfolioListResponseDTO)
async def list_portfolios(
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
    niche_id: Optional[UUID] = Query(default=None, description="Filter by niche ID"),
    is_active: Optional[bool] = Query(default=None, description="Filter by active status"),
    current_user: dict = Depends(get_current_user),
) -> PortfolioListResponseDTO:
    """List portfolios with pagination and filters.

    Args:
        page: Page number (1-indexed)
        limit: Number of items per page
        niche_id: Optional filter by niche
        is_active: Optional filter by active status
        current_user: Authenticated user

    Returns:
        PortfolioListResponseDTO with paginated portfolios
    """
    print(f"INFO [PortfolioRoutes]: Listing portfolios - page={page}, limit={limit}")

    filters = PortfolioFilterDTO(
        niche_id=niche_id,
        is_active=is_active,
    )

    result = portfolio_service.list_portfolios(
        filters=filters,
        page=page,
        limit=limit,
    )

    print(f"INFO [PortfolioRoutes]: Listed {len(result.items)} portfolios (total: {result.pagination.total})")
    return result


@router.get("/search", response_model=List[PortfolioResponseDTO])
async def search_portfolios(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(default=50, ge=1, le=100, description="Maximum results"),
    current_user: dict = Depends(get_current_user),
) -> List[PortfolioResponseDTO]:
    """Search portfolios by name or description.

    Args:
        q: Search query string
        limit: Maximum number of results to return
        current_user: Authenticated user

    Returns:
        List of matching PortfolioResponseDTO
    """
    print(f"INFO [PortfolioRoutes]: Searching portfolios - query='{q}', limit={limit}")

    filters = PortfolioFilterDTO(search=q)
    result = portfolio_service.list_portfolios(
        filters=filters,
        page=1,
        limit=limit,
    )

    print(f"INFO [PortfolioRoutes]: Search returned {len(result.items)} results")
    return result.items


# =============================================================================
# Public Share Endpoint (No Authentication)
# =============================================================================


@router.get("/shared/{token}", response_model=PortfolioPublicResponseDTO)
async def get_portfolio_by_share_token(
    token: str,
) -> PortfolioPublicResponseDTO:
    """Get a portfolio by its share token.

    This endpoint is PUBLIC and does NOT require authentication.

    Args:
        token: JWT share token

    Returns:
        PortfolioPublicResponseDTO

    Raises:
        HTTPException 404: If token is invalid, expired, or portfolio not found
    """
    print("INFO [PortfolioRoutes]: Accessing portfolio via share token")

    result = portfolio_service.get_by_share_token(token)

    if not result:
        print("WARN [PortfolioRoutes]: Invalid or expired share token")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired share token, or portfolio not found",
        )

    print(f"INFO [PortfolioRoutes]: Retrieved portfolio {result.id} via share token")
    return result


# =============================================================================
# CRUD Endpoints
# =============================================================================


@router.post("", response_model=PortfolioResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    data: PortfolioCreateDTO,
    current_user: dict = Depends(require_roles(["admin", "manager"])),
) -> PortfolioResponseDTO:
    """Create a new portfolio.

    Args:
        data: Portfolio creation data
        current_user: Authenticated user with admin or manager role

    Returns:
        Created PortfolioResponseDTO

    Raises:
        HTTPException 400: If portfolio creation fails
    """
    print(f"INFO [PortfolioRoutes]: Creating portfolio - name={data.name}")

    result = portfolio_service.create_portfolio(data)

    if not result:
        print("ERROR [PortfolioRoutes]: Failed to create portfolio")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create portfolio",
        )

    print(f"INFO [PortfolioRoutes]: Portfolio created - id={result.id}")
    return result


@router.get("/{portfolio_id}", response_model=PortfolioResponseDTO)
async def get_portfolio(
    portfolio_id: UUID,
    current_user: dict = Depends(get_current_user),
) -> PortfolioResponseDTO:
    """Get a portfolio by ID.

    Args:
        portfolio_id: Portfolio UUID
        current_user: Authenticated user

    Returns:
        PortfolioResponseDTO

    Raises:
        HTTPException 404: If portfolio not found
    """
    print(f"INFO [PortfolioRoutes]: Getting portfolio - id={portfolio_id}")

    result = portfolio_service.get_portfolio(portfolio_id)

    if not result:
        print(f"WARN [PortfolioRoutes]: Portfolio not found - id={portfolio_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found",
        )

    return result


@router.put("/{portfolio_id}", response_model=PortfolioResponseDTO)
async def update_portfolio(
    portfolio_id: UUID,
    data: PortfolioUpdateDTO,
    current_user: dict = Depends(require_roles(["admin", "manager"])),
) -> PortfolioResponseDTO:
    """Update a portfolio.

    Args:
        portfolio_id: Portfolio UUID
        data: Portfolio update data
        current_user: Authenticated user with admin or manager role

    Returns:
        Updated PortfolioResponseDTO

    Raises:
        HTTPException 404: If portfolio not found
    """
    print(f"INFO [PortfolioRoutes]: Updating portfolio - id={portfolio_id}")

    result = portfolio_service.update_portfolio(portfolio_id, data)

    if not result:
        print(f"WARN [PortfolioRoutes]: Portfolio not found for update - id={portfolio_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found",
        )

    print(f"INFO [PortfolioRoutes]: Portfolio updated - id={portfolio_id}")
    return result


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portfolio(
    portfolio_id: UUID,
    current_user: dict = Depends(require_roles(["admin", "manager"])),
) -> None:
    """Soft delete a portfolio (sets is_active=False).

    Args:
        portfolio_id: Portfolio UUID
        current_user: Authenticated user with admin or manager role

    Raises:
        HTTPException 404: If portfolio not found
    """
    print(f"INFO [PortfolioRoutes]: Deleting portfolio - id={portfolio_id}")

    success = portfolio_service.delete_portfolio(portfolio_id)

    if not success:
        print(f"WARN [PortfolioRoutes]: Portfolio not found for deletion - id={portfolio_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found",
        )

    print(f"INFO [PortfolioRoutes]: Portfolio deleted - id={portfolio_id}")


# =============================================================================
# Portfolio Duplication
# =============================================================================


@router.post("/{portfolio_id}/duplicate", response_model=PortfolioResponseDTO, status_code=status.HTTP_201_CREATED)
async def duplicate_portfolio(
    portfolio_id: UUID,
    data: PortfolioDuplicateRequestDTO,
    current_user: dict = Depends(require_roles(["admin", "manager"])),
) -> PortfolioResponseDTO:
    """Duplicate a portfolio with a new name.

    Copies all portfolio items with their notes and sort_order.

    Args:
        portfolio_id: Source portfolio UUID
        data: Contains new_name for the duplicate
        current_user: Authenticated user with admin or manager role

    Returns:
        Created PortfolioResponseDTO for the new portfolio

    Raises:
        HTTPException 404: If source portfolio not found
        HTTPException 400: If name already exists
    """
    print(f"INFO [PortfolioRoutes]: Duplicating portfolio {portfolio_id} to '{data.new_name}'")

    result = portfolio_service.duplicate_portfolio(portfolio_id, data.new_name)

    if not result:
        # Check if source exists
        source = portfolio_service.get_portfolio(portfolio_id)
        if not source:
            print(f"WARN [PortfolioRoutes]: Source portfolio not found - id={portfolio_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source portfolio not found",
            )
        else:
            print(f"WARN [PortfolioRoutes]: Portfolio name '{data.new_name}' already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Portfolio name already exists",
            )

    print(f"INFO [PortfolioRoutes]: Portfolio duplicated - new_id={result.id}")
    return result


# =============================================================================
# Product Management Endpoints
# =============================================================================


@router.post(
    "/{portfolio_id}/products/{product_id}",
    status_code=status.HTTP_201_CREATED,
)
async def add_product_to_portfolio(
    portfolio_id: UUID,
    product_id: UUID,
    data: Optional[PortfolioAddProductRequestDTO] = None,
    current_user: dict = Depends(require_roles(["admin", "manager"])),
) -> dict:
    """Add a product to a portfolio.

    Args:
        portfolio_id: Portfolio UUID
        product_id: Product UUID to add
        data: Optional curator notes
        current_user: Authenticated user with admin or manager role

    Returns:
        Success message

    Raises:
        HTTPException 404: If portfolio not found
        HTTPException 400: If operation fails
    """
    print(f"INFO [PortfolioRoutes]: Adding product {product_id} to portfolio {portfolio_id}")

    curator_notes = data.curator_notes if data else None
    success = portfolio_service.add_product_to_portfolio(
        portfolio_id=portfolio_id,
        product_id=product_id,
        curator_notes=curator_notes,
    )

    if not success:
        # Check if portfolio exists
        portfolio = portfolio_service.get_portfolio(portfolio_id)
        if not portfolio:
            print(f"WARN [PortfolioRoutes]: Portfolio not found - id={portfolio_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found",
            )
        else:
            print("WARN [PortfolioRoutes]: Failed to add product - may be invalid product ID")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to add product (may already exist or invalid product ID)",
            )

    print(f"INFO [PortfolioRoutes]: Product added - portfolio={portfolio_id}, product={product_id}")
    return {"message": "Product added to portfolio successfully"}


@router.delete(
    "/{portfolio_id}/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_product_from_portfolio(
    portfolio_id: UUID,
    product_id: UUID,
    current_user: dict = Depends(require_roles(["admin", "manager"])),
) -> None:
    """Remove a product from a portfolio.

    Args:
        portfolio_id: Portfolio UUID
        product_id: Product UUID to remove
        current_user: Authenticated user with admin or manager role

    Raises:
        HTTPException 404: If portfolio or product not found in portfolio
    """
    print(f"INFO [PortfolioRoutes]: Removing product {product_id} from portfolio {portfolio_id}")

    success = portfolio_service.remove_product_from_portfolio(portfolio_id, product_id)

    if not success:
        print(f"WARN [PortfolioRoutes]: Product not found in portfolio - portfolio={portfolio_id}, product={product_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found in portfolio",
        )

    print(f"INFO [PortfolioRoutes]: Product removed - portfolio={portfolio_id}, product={product_id}")


@router.put("/{portfolio_id}/products/reorder")
async def reorder_products(
    portfolio_id: UUID,
    data: ReorderProductsRequestDTO,
    current_user: dict = Depends(require_roles(["admin", "manager"])),
) -> dict:
    """Reorder products in a portfolio.

    All product IDs currently in the portfolio must be provided in the desired order.

    Args:
        portfolio_id: Portfolio UUID
        data: List of product UUIDs in desired order
        current_user: Authenticated user with admin or manager role

    Returns:
        Success message

    Raises:
        HTTPException 404: If portfolio not found
        HTTPException 400: If product IDs don't match portfolio contents
    """
    print(f"INFO [PortfolioRoutes]: Reordering products in portfolio {portfolio_id}")

    success = portfolio_service.reorder_products(portfolio_id, data.product_ids)

    if not success:
        # Check if portfolio exists
        portfolio = portfolio_service.get_portfolio(portfolio_id)
        if not portfolio:
            print(f"WARN [PortfolioRoutes]: Portfolio not found - id={portfolio_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found",
            )
        else:
            print("WARN [PortfolioRoutes]: Product IDs don't match portfolio contents")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product IDs must match exactly the products in the portfolio",
            )

    print(f"INFO [PortfolioRoutes]: Products reordered in portfolio {portfolio_id}")
    return {"message": "Products reordered successfully"}


# =============================================================================
# Share Token Endpoint
# =============================================================================


@router.post("/{portfolio_id}/share", response_model=PortfolioShareTokenResponseDTO)
async def generate_share_token(
    portfolio_id: UUID,
    current_user: dict = Depends(require_roles(["admin", "manager"])),
) -> PortfolioShareTokenResponseDTO:
    """Generate a share token for public portfolio access.

    The token allows anyone to view the portfolio without authentication.

    Args:
        portfolio_id: Portfolio UUID
        current_user: Authenticated user with admin or manager role

    Returns:
        PortfolioShareTokenResponseDTO with token and expiration

    Raises:
        HTTPException 404: If portfolio not found
    """
    print(f"INFO [PortfolioRoutes]: Generating share token for portfolio {portfolio_id}")

    result = portfolio_service.get_share_token(portfolio_id)

    if not result:
        print(f"WARN [PortfolioRoutes]: Portfolio not found - id={portfolio_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found",
        )

    print(f"INFO [PortfolioRoutes]: Share token generated for portfolio {portfolio_id}")
    return result


# =============================================================================
# Create from Filters Endpoint
# =============================================================================


@router.post("/from-filters", response_model=PortfolioResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_portfolio_from_filters(
    data: PortfolioFromFiltersRequestDTO,
    current_user: dict = Depends(require_roles(["admin", "manager"])),
) -> PortfolioResponseDTO:
    """Create a portfolio from product filter criteria.

    Queries products matching the filters and adds them all to a new portfolio.

    Args:
        data: Portfolio name, optional description/niche, and product filters
        current_user: Authenticated user with admin or manager role

    Returns:
        Created PortfolioResponseDTO

    Raises:
        HTTPException 400: If name already exists or creation fails
    """
    print(f"INFO [PortfolioRoutes]: Creating portfolio from filters - name={data.name}")

    result = portfolio_service.create_from_filters(
        name=data.name,
        filters=data.filters,
        description=data.description,
        niche_id=data.niche_id,
    )

    if not result:
        print("ERROR [PortfolioRoutes]: Failed to create portfolio from filters")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create portfolio (name may already exist)",
        )

    print(f"INFO [PortfolioRoutes]: Portfolio created from filters - id={result.id}, item_count={result.item_count}")
    return result
