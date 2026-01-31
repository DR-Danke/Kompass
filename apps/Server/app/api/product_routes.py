"""Product API routes for Biblia General (master product database) management.

This module provides RESTful endpoints for product management, including:
- CRUD operations for products
- Image management (add, remove, set primary)
- Tag management (add, remove)
- Advanced filtering and pagination
- Full-text search
"""

from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from starlette import status

from app.api.dependencies import get_current_user
from app.api.rbac_dependencies import require_roles
from app.models.kompass_dto import (
    ProductCreateDTO,
    ProductFilterDTO,
    ProductImageCreateDTO,
    ProductImageResponseDTO,
    ProductListResponseDTO,
    ProductResponseDTO,
    ProductStatus,
    ProductUpdateDTO,
)
from app.services.product_service import product_service

router = APIRouter(tags=["Products"])


@router.get("", response_model=ProductListResponseDTO)
async def list_products(
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
    supplier_id: Optional[UUID] = Query(default=None, description="Filter by supplier ID"),
    category_id: Optional[UUID] = Query(default=None, description="Filter by category ID"),
    product_status: Optional[ProductStatus] = Query(default=None, alias="status", description="Filter by status"),
    price_min: Optional[Decimal] = Query(default=None, ge=0, description="Minimum price"),
    price_max: Optional[Decimal] = Query(default=None, ge=0, description="Maximum price"),
    moq_min: Optional[int] = Query(default=None, ge=1, description="Minimum order quantity"),
    moq_max: Optional[int] = Query(default=None, ge=1, description="Maximum order quantity"),
    tags: Optional[str] = Query(default=None, description="Comma-separated tag UUIDs"),
    has_images: Optional[bool] = Query(default=None, description="Filter by image presence"),
    sort_by: Optional[str] = Query(
        default=None,
        description="Sort field (name, unit_price, created_at, minimum_order_qty)",
    ),
    sort_order: str = Query(default="asc", pattern="^(asc|desc)$", description="Sort order"),
    current_user: dict = Depends(get_current_user),
) -> ProductListResponseDTO:
    """List products with filtering and pagination.

    Args:
        page: Page number (1-indexed)
        limit: Number of items per page
        supplier_id: Filter by supplier
        category_id: Filter by category
        status: Filter by product status
        price_min: Minimum unit price filter
        price_max: Maximum unit price filter
        moq_min: Minimum order quantity filter
        moq_max: Maximum order quantity filter
        tags: Comma-separated list of tag UUIDs
        has_images: Filter products with/without images
        sort_by: Field to sort by
        sort_order: Sort order (asc or desc)
        current_user: Authenticated user

    Returns:
        ProductListResponseDTO with paginated products
    """
    print(f"INFO [ProductRoutes]: Listing products - page={page}, limit={limit}")

    # Parse tags string into list of UUIDs
    tag_ids: Optional[List[UUID]] = None
    if tags:
        try:
            tag_ids = [UUID(tag.strip()) for tag in tags.split(",") if tag.strip()]
        except ValueError as e:
            print(f"WARN [ProductRoutes]: Invalid tag UUID format: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid tag UUID format",
            )

    # Build filter DTO
    filters = ProductFilterDTO(
        supplier_id=supplier_id,
        category_id=category_id,
        status=product_status,
        min_price=price_min,
        max_price=price_max,
        tag_ids=tag_ids,
    )

    result = product_service.list_products(
        filters=filters,
        page=page,
        limit=limit,
        has_images=has_images,
        min_moq=moq_min,
        max_moq=moq_max,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    print(f"INFO [ProductRoutes]: Listed {len(result.items)} products (total: {result.pagination.total})")
    return result


@router.post("", response_model=ProductResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreateDTO,
    current_user: dict = Depends(require_roles(["admin", "manager"])),
) -> ProductResponseDTO:
    """Create a new product.

    Args:
        data: Product creation data
        current_user: Authenticated user with admin or manager role

    Returns:
        Created ProductResponseDTO

    Raises:
        HTTPException 400: If product creation fails
    """
    print(f"INFO [ProductRoutes]: Creating product - name={data.name}, sku={data.sku}")

    result = product_service.create_product(data)

    if not result:
        print("ERROR [ProductRoutes]: Failed to create product")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create product",
        )

    print(f"INFO [ProductRoutes]: Product created - id={result.id}, sku={result.sku}")
    return result


@router.get("/search", response_model=List[ProductResponseDTO])
async def search_products(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(default=50, ge=1, le=100, description="Maximum results"),
    current_user: dict = Depends(get_current_user),
) -> List[ProductResponseDTO]:
    """Search products using full-text search.

    Searches across product name, description, and SKU.

    Args:
        q: Search query string
        limit: Maximum number of results to return
        current_user: Authenticated user

    Returns:
        List of matching ProductResponseDTO
    """
    print(f"INFO [ProductRoutes]: Searching products - query='{q}', limit={limit}")

    results = product_service.search_products(query=q, limit=limit)

    print(f"INFO [ProductRoutes]: Search returned {len(results)} results")
    return results


@router.get("/{product_id}", response_model=ProductResponseDTO)
async def get_product(
    product_id: UUID,
    current_user: dict = Depends(get_current_user),
) -> ProductResponseDTO:
    """Get a product by ID.

    Args:
        product_id: Product UUID
        current_user: Authenticated user

    Returns:
        ProductResponseDTO

    Raises:
        HTTPException 404: If product not found
    """
    print(f"INFO [ProductRoutes]: Getting product - id={product_id}")

    result = product_service.get_product(product_id)

    if not result:
        print(f"WARN [ProductRoutes]: Product not found - id={product_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return result


@router.put("/{product_id}", response_model=ProductResponseDTO)
async def update_product(
    product_id: UUID,
    data: ProductUpdateDTO,
    current_user: dict = Depends(require_roles(["admin", "manager"])),
) -> ProductResponseDTO:
    """Update a product.

    Args:
        product_id: Product UUID
        data: Product update data
        current_user: Authenticated user with admin or manager role

    Returns:
        Updated ProductResponseDTO

    Raises:
        HTTPException 404: If product not found
    """
    print(f"INFO [ProductRoutes]: Updating product - id={product_id}")

    result = product_service.update_product(product_id, data)

    if not result:
        print(f"WARN [ProductRoutes]: Product not found for update - id={product_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    print(f"INFO [ProductRoutes]: Product updated - id={product_id}")
    return result


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: UUID,
    current_user: dict = Depends(require_roles(["admin", "manager"])),
) -> None:
    """Soft delete a product (sets status to inactive).

    Args:
        product_id: Product UUID
        current_user: Authenticated user with admin or manager role

    Raises:
        HTTPException 404: If product not found
    """
    print(f"INFO [ProductRoutes]: Deleting product - id={product_id}")

    success = product_service.delete_product(product_id)

    if not success:
        print(f"WARN [ProductRoutes]: Product not found for deletion - id={product_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    print(f"INFO [ProductRoutes]: Product deleted - id={product_id}")


# =============================================================================
# Image Management Endpoints
# =============================================================================


@router.post(
    "/{product_id}/images",
    response_model=ProductImageResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
async def add_product_image(
    product_id: UUID,
    data: ProductImageCreateDTO,
    current_user: dict = Depends(require_roles(["admin", "manager"])),
) -> ProductImageResponseDTO:
    """Add an image to a product.

    Args:
        product_id: Product UUID
        data: Image data (url, alt_text, sort_order, is_primary)
        current_user: Authenticated user with admin or manager role

    Returns:
        Created ProductImageResponseDTO

    Raises:
        HTTPException 404: If product not found
        HTTPException 400: If image creation fails
    """
    print(f"INFO [ProductRoutes]: Adding image to product - product_id={product_id}")

    # Verify product exists
    product = product_service.get_product(product_id)
    if not product:
        print(f"WARN [ProductRoutes]: Product not found - id={product_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    result = product_service.add_product_image(
        product_id=product_id,
        image_url=data.url,
        is_primary=data.is_primary,
        alt_text=data.alt_text,
        sort_order=data.sort_order,
    )

    if not result:
        print(f"ERROR [ProductRoutes]: Failed to add image - product_id={product_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to add image",
        )

    print(f"INFO [ProductRoutes]: Image added - product_id={product_id}, image_id={result.id}")
    return result


@router.delete(
    "/{product_id}/images/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_product_image(
    product_id: UUID,
    image_id: UUID,
    current_user: dict = Depends(require_roles(["admin", "manager"])),
) -> None:
    """Remove an image from a product.

    Args:
        product_id: Product UUID
        image_id: Image UUID to remove
        current_user: Authenticated user with admin or manager role

    Raises:
        HTTPException 404: If image not found
    """
    print(f"INFO [ProductRoutes]: Removing image - product_id={product_id}, image_id={image_id}")

    success = product_service.remove_product_image(product_id, image_id)

    if not success:
        print(f"WARN [ProductRoutes]: Image not found - image_id={image_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found",
        )

    print(f"INFO [ProductRoutes]: Image removed - image_id={image_id}")


@router.put("/{product_id}/images/{image_id}/primary")
async def set_primary_image(
    product_id: UUID,
    image_id: UUID,
    current_user: dict = Depends(require_roles(["admin", "manager"])),
) -> dict:
    """Set a specific image as the primary image for a product.

    Args:
        product_id: Product UUID
        image_id: Image UUID to set as primary
        current_user: Authenticated user with admin or manager role

    Returns:
        Success message

    Raises:
        HTTPException 404: If product or image not found
    """
    print(f"INFO [ProductRoutes]: Setting primary image - product_id={product_id}, image_id={image_id}")

    success = product_service.set_primary_image(product_id, image_id)

    if not success:
        print(f"WARN [ProductRoutes]: Failed to set primary image - product_id={product_id}, image_id={image_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product or image not found",
        )

    print(f"INFO [ProductRoutes]: Primary image set - image_id={image_id}")
    return {"message": "Primary image updated successfully"}


# =============================================================================
# Tag Management Endpoints
# =============================================================================


@router.post(
    "/{product_id}/tags/{tag_id}",
    status_code=status.HTTP_201_CREATED,
)
async def add_tag_to_product(
    product_id: UUID,
    tag_id: UUID,
    current_user: dict = Depends(require_roles(["admin", "manager"])),
) -> dict:
    """Add a tag to a product.

    Args:
        product_id: Product UUID
        tag_id: Tag UUID to add
        current_user: Authenticated user with admin or manager role

    Returns:
        Success message

    Raises:
        HTTPException 400: If tag already exists or operation fails
    """
    print(f"INFO [ProductRoutes]: Adding tag to product - product_id={product_id}, tag_id={tag_id}")

    success = product_service.add_tag_to_product(product_id, tag_id)

    if not success:
        print(f"WARN [ProductRoutes]: Failed to add tag - product_id={product_id}, tag_id={tag_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to add tag (may already exist or invalid IDs)",
        )

    print(f"INFO [ProductRoutes]: Tag added - product_id={product_id}, tag_id={tag_id}")
    return {"message": "Tag added successfully"}


@router.delete(
    "/{product_id}/tags/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_tag_from_product(
    product_id: UUID,
    tag_id: UUID,
    current_user: dict = Depends(require_roles(["admin", "manager"])),
) -> None:
    """Remove a tag from a product.

    Args:
        product_id: Product UUID
        tag_id: Tag UUID to remove
        current_user: Authenticated user with admin or manager role

    Raises:
        HTTPException 404: If tag association not found
    """
    print(f"INFO [ProductRoutes]: Removing tag from product - product_id={product_id}, tag_id={tag_id}")

    success = product_service.remove_tag_from_product(product_id, tag_id)

    if not success:
        print(f"WARN [ProductRoutes]: Tag not found on product - product_id={product_id}, tag_id={tag_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found on product",
        )

    print(f"INFO [ProductRoutes]: Tag removed - product_id={product_id}, tag_id={tag_id}")
