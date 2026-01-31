"""Category API routes for managing hierarchical product categories."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.dependencies import get_current_user
from app.api.rbac_dependencies import require_roles
from app.models.kompass_dto import (
    CategoryCreateDTO,
    CategoryResponseDTO,
    CategoryTreeNode,
    CategoryUpdateDTO,
)
from app.services.category_service import category_service

router = APIRouter(tags=["Categories"])


class CategoryMoveDTO(BaseModel):
    """Request model for moving a category to a new parent."""

    new_parent_id: Optional[UUID] = None


@router.get("/", response_model=List[CategoryTreeNode])
async def list_categories(
    current_user: dict = Depends(get_current_user),
) -> List[CategoryTreeNode]:
    """List all categories as a nested tree structure.

    Returns:
        List of root-level CategoryTreeNode with nested children
    """
    print("INFO [CategoryRoutes]: Listing categories as tree")
    return category_service.list_categories()


@router.post("/", response_model=CategoryResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreateDTO,
    current_user: dict = Depends(get_current_user),
) -> CategoryResponseDTO:
    """Create a new category.

    Args:
        data: Category creation data

    Returns:
        Created category

    Raises:
        HTTPException 400: If creation fails (e.g., parent not found)
    """
    print(f"INFO [CategoryRoutes]: Creating category: {data.name}")
    result = category_service.create_category(data)
    if not result:
        print(f"WARN [CategoryRoutes]: Failed to create category: {data.name}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create category. Parent category may not exist.",
        )
    return result


@router.get("/{category_id}", response_model=CategoryResponseDTO)
async def get_category(
    category_id: UUID,
    current_user: dict = Depends(get_current_user),
) -> CategoryResponseDTO:
    """Get a category by ID.

    Args:
        category_id: UUID of the category

    Returns:
        Category details

    Raises:
        HTTPException 404: If category not found
    """
    print(f"INFO [CategoryRoutes]: Getting category: {category_id}")
    result = category_service.get_category(category_id)
    if not result:
        print(f"WARN [CategoryRoutes]: Category not found: {category_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    return result


@router.put("/{category_id}", response_model=CategoryResponseDTO)
async def update_category(
    category_id: UUID,
    data: CategoryUpdateDTO,
    current_user: dict = Depends(require_roles(["admin", "manager"])),
) -> CategoryResponseDTO:
    """Update a category.

    Args:
        category_id: UUID of the category to update
        data: Update data

    Returns:
        Updated category

    Raises:
        HTTPException 404: If category not found
        HTTPException 400: If update fails (cycle prevention, invalid parent)
    """
    print(f"INFO [CategoryRoutes]: Updating category: {category_id}")

    existing = category_service.get_category(category_id)
    if not existing:
        print(f"WARN [CategoryRoutes]: Category not found for update: {category_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    result = category_service.update_category(category_id, data)
    if not result:
        print(f"WARN [CategoryRoutes]: Failed to update category: {category_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update category. Check for cycle or invalid parent.",
        )
    return result


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: UUID,
    current_user: dict = Depends(require_roles(["admin", "manager"])),
) -> None:
    """Delete a category (soft delete).

    Args:
        category_id: UUID of the category to delete

    Raises:
        HTTPException 404: If category not found
        HTTPException 409: If category has children or products
    """
    print(f"INFO [CategoryRoutes]: Deleting category: {category_id}")

    existing = category_service.get_category(category_id)
    if not existing:
        print(f"WARN [CategoryRoutes]: Category not found for delete: {category_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    success = category_service.delete_category(category_id)
    if not success:
        print(f"WARN [CategoryRoutes]: Cannot delete category with children/products: {category_id}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete category with children or products",
        )


@router.put("/{category_id}/move", response_model=CategoryResponseDTO)
async def move_category(
    category_id: UUID,
    data: CategoryMoveDTO,
    current_user: dict = Depends(require_roles(["admin", "manager"])),
) -> CategoryResponseDTO:
    """Move a category to a new parent.

    Args:
        category_id: UUID of the category to move
        data: Move data with new_parent_id

    Returns:
        Updated category

    Raises:
        HTTPException 404: If category or new parent not found
        HTTPException 400: If move creates a cycle
    """
    print(f"INFO [CategoryRoutes]: Moving category {category_id} to parent {data.new_parent_id}")

    existing = category_service.get_category(category_id)
    if not existing:
        print(f"WARN [CategoryRoutes]: Category not found for move: {category_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    result = category_service.move_category(category_id, data.new_parent_id)
    if not result:
        print(f"WARN [CategoryRoutes]: Failed to move category: {category_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to move category. New parent may not exist or move creates cycle.",
        )
    return result
