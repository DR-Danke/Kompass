"""Tag API routes for managing product tags."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_current_user
from app.api.rbac_dependencies import require_roles
from app.models.kompass_dto import (
    TagCreateDTO,
    TagListResponseDTO,
    TagResponseDTO,
    TagUpdateDTO,
    TagWithCountDTO,
)
from app.services.tag_service import tag_service

router = APIRouter(tags=["Tags"])


@router.get("/", response_model=TagListResponseDTO)
async def list_tags(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: dict = Depends(get_current_user),
) -> TagListResponseDTO:
    """List all tags with product counts and pagination.

    Args:
        page: Page number (1-indexed)
        limit: Items per page (max 100)
        current_user: Authenticated user (injected)

    Returns:
        Paginated list of tags with product counts
    """
    print(f"INFO [TagRoutes]: Listing tags, page {page}, limit {limit}")
    return tag_service.list_tags(page=page, limit=limit)


@router.get("/search", response_model=List[TagResponseDTO])
async def search_tags(
    query: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    current_user: dict = Depends(get_current_user),
) -> List[TagResponseDTO]:
    """Search tags by name for autocomplete.

    Args:
        query: Search query string
        limit: Maximum number of results

    Returns:
        List of matching tags
    """
    print(f"INFO [TagRoutes]: Searching tags with query: {query}")
    return tag_service.search_tags(query, limit)


@router.post("/", response_model=TagResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_tag(
    data: TagCreateDTO,
    current_user: dict = Depends(get_current_user),
) -> TagResponseDTO:
    """Create a new tag.

    Args:
        data: Tag creation data

    Returns:
        Created tag

    Raises:
        HTTPException 400: If creation fails
    """
    print(f"INFO [TagRoutes]: Creating tag: {data.name}")
    result = tag_service.create_tag(data)
    if not result:
        print(f"WARN [TagRoutes]: Failed to create tag: {data.name}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create tag",
        )
    return result


@router.get("/{tag_id}", response_model=TagWithCountDTO)
async def get_tag(
    tag_id: UUID,
    current_user: dict = Depends(get_current_user),
) -> TagWithCountDTO:
    """Get a tag by ID with product count.

    Args:
        tag_id: UUID of the tag

    Returns:
        Tag details with product count

    Raises:
        HTTPException 404: If tag not found
    """
    print(f"INFO [TagRoutes]: Getting tag: {tag_id}")
    result = tag_service.get_tag(tag_id)
    if not result:
        print(f"WARN [TagRoutes]: Tag not found: {tag_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )
    return result


@router.put("/{tag_id}", response_model=TagResponseDTO)
async def update_tag(
    tag_id: UUID,
    data: TagUpdateDTO,
    current_user: dict = Depends(require_roles(["admin", "manager"])),
) -> TagResponseDTO:
    """Update a tag.

    Args:
        tag_id: UUID of the tag to update
        data: Update data

    Returns:
        Updated tag

    Raises:
        HTTPException 404: If tag not found
    """
    print(f"INFO [TagRoutes]: Updating tag: {tag_id}")

    existing = tag_service.get_tag(tag_id)
    if not existing:
        print(f"WARN [TagRoutes]: Tag not found for update: {tag_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    result = tag_service.update_tag(tag_id, data)
    if not result:
        print(f"WARN [TagRoutes]: Failed to update tag: {tag_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update tag",
        )
    return result


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: UUID,
    current_user: dict = Depends(require_roles(["admin", "manager"])),
) -> None:
    """Delete a tag (hard delete with FK cascade).

    Args:
        tag_id: UUID of the tag to delete

    Raises:
        HTTPException 404: If tag not found
    """
    print(f"INFO [TagRoutes]: Deleting tag: {tag_id}")

    success = tag_service.delete_tag(tag_id)
    if not success:
        print(f"WARN [TagRoutes]: Tag not found for delete: {tag_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )
