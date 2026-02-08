"""Niche API routes for managing client type classifications."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user
from app.api.rbac_dependencies import require_roles
from app.models.kompass_dto import (
    NicheCreateDTO,
    NicheResponseDTO,
    NicheUpdateDTO,
    NicheWithClientCountDTO,
)
from app.services.niche_service import niche_service

router = APIRouter(tags=["Niches"])


@router.get("", response_model=List[NicheWithClientCountDTO])
async def list_niches(
    current_user: dict = Depends(get_current_user),
) -> List[NicheWithClientCountDTO]:
    """List all niches with client counts.

    Returns:
        List of niches with their client counts
    """
    print("INFO [NicheRoutes]: Listing niches with client counts")
    return niche_service.list_niches()


@router.post("", response_model=NicheResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_niche(
    data: NicheCreateDTO,
    current_user: dict = Depends(get_current_user),
) -> NicheResponseDTO:
    """Create a new niche.

    Args:
        data: Niche creation data

    Returns:
        Created niche

    Raises:
        HTTPException 400: If creation fails (e.g., duplicate name)
    """
    print(f"INFO [NicheRoutes]: Creating niche: {data.name}")
    result = niche_service.create_niche(data)
    if not result:
        print(f"WARN [NicheRoutes]: Failed to create niche: {data.name}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create niche. Name may already exist.",
        )
    return result


@router.get("/{niche_id}", response_model=NicheWithClientCountDTO)
async def get_niche(
    niche_id: UUID,
    current_user: dict = Depends(get_current_user),
) -> NicheWithClientCountDTO:
    """Get a niche by ID with client count.

    Args:
        niche_id: UUID of the niche

    Returns:
        Niche details with client count

    Raises:
        HTTPException 404: If niche not found
    """
    print(f"INFO [NicheRoutes]: Getting niche: {niche_id}")
    result = niche_service.get_niche(niche_id)
    if not result:
        print(f"WARN [NicheRoutes]: Niche not found: {niche_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Niche not found",
        )
    return result


@router.put("/{niche_id}", response_model=NicheResponseDTO)
async def update_niche(
    niche_id: UUID,
    data: NicheUpdateDTO,
    current_user: dict = Depends(require_roles(["admin", "manager"])),
) -> NicheResponseDTO:
    """Update a niche.

    Args:
        niche_id: UUID of the niche to update
        data: Update data

    Returns:
        Updated niche

    Raises:
        HTTPException 404: If niche not found
        HTTPException 400: If update fails
    """
    print(f"INFO [NicheRoutes]: Updating niche: {niche_id}")

    existing = niche_service.get_niche(niche_id)
    if not existing:
        print(f"WARN [NicheRoutes]: Niche not found for update: {niche_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Niche not found",
        )

    result = niche_service.update_niche(niche_id, data)
    if not result:
        print(f"WARN [NicheRoutes]: Failed to update niche: {niche_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update niche.",
        )
    return result


@router.delete("/{niche_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_niche(
    niche_id: UUID,
    current_user: dict = Depends(require_roles(["admin", "manager"])),
) -> None:
    """Delete a niche (soft delete).

    Args:
        niche_id: UUID of the niche to delete

    Raises:
        HTTPException 404: If niche not found
        HTTPException 409: If niche has associated clients
    """
    print(f"INFO [NicheRoutes]: Deleting niche: {niche_id}")

    existing = niche_service.get_niche(niche_id)
    if not existing:
        print(f"WARN [NicheRoutes]: Niche not found for delete: {niche_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Niche not found",
        )

    try:
        success = niche_service.delete_niche(niche_id)
        if not success:
            print(f"WARN [NicheRoutes]: Failed to delete niche: {niche_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete niche.",
            )
    except ValueError as e:
        print(f"WARN [NicheRoutes]: Cannot delete niche with clients: {niche_id}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
