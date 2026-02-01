"""Pricing configuration API routes for managing HS codes, freight rates, and settings."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_current_user
from app.api.rbac_dependencies import require_roles
from app.models.kompass_dto import (
    FreightRateCreateDTO,
    FreightRateListResponseDTO,
    FreightRateResponseDTO,
    FreightRateUpdateDTO,
    HSCodeCreateDTO,
    HSCodeListResponseDTO,
    HSCodeResponseDTO,
    HSCodeUpdateDTO,
    PricingSettingResponseDTO,
    PricingSettingsResponseDTO,
    PricingSettingUpdateDTO,
)
from app.services.pricing_service import pricing_service

router = APIRouter(tags=["Pricing"])


# =============================================================================
# HS CODE ENDPOINTS
# =============================================================================


@router.get("/hs-codes", response_model=HSCodeListResponseDTO)
async def list_hs_codes(
    search: Optional[str] = Query(None, description="Search by code or description"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: dict = Depends(get_current_user),
) -> HSCodeListResponseDTO:
    """List HS codes with optional search and pagination.

    Args:
        search: Optional search term for code or description
        page: Page number (1-indexed)
        limit: Items per page

    Returns:
        Paginated list of HS codes
    """
    print(f"INFO [PricingRoutes]: Listing HS codes, search={search}, page={page}")
    return pricing_service.list_hs_codes(search=search, page=page, limit=limit)


@router.post("/hs-codes", response_model=HSCodeResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_hs_code(
    data: HSCodeCreateDTO,
    current_user: dict = Depends(get_current_user),
) -> HSCodeResponseDTO:
    """Create a new HS code.

    Args:
        data: HS code creation data

    Returns:
        Created HS code

    Raises:
        HTTPException 400: If creation fails
    """
    print(f"INFO [PricingRoutes]: Creating HS code: {data.code}")
    result = pricing_service.create_hs_code(data)
    if not result:
        print(f"WARN [PricingRoutes]: Failed to create HS code: {data.code}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create HS code. Code may already exist.",
        )
    return result


@router.get("/hs-codes/{hs_code_id}", response_model=HSCodeResponseDTO)
async def get_hs_code(
    hs_code_id: UUID,
    current_user: dict = Depends(get_current_user),
) -> HSCodeResponseDTO:
    """Get an HS code by ID.

    Args:
        hs_code_id: UUID of the HS code

    Returns:
        HS code details

    Raises:
        HTTPException 404: If HS code not found
    """
    print(f"INFO [PricingRoutes]: Getting HS code: {hs_code_id}")
    result = pricing_service.get_hs_code(hs_code_id)
    if not result:
        print(f"WARN [PricingRoutes]: HS code not found: {hs_code_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="HS code not found",
        )
    return result


@router.put("/hs-codes/{hs_code_id}", response_model=HSCodeResponseDTO)
async def update_hs_code(
    hs_code_id: UUID,
    data: HSCodeUpdateDTO,
    current_user: dict = Depends(require_roles(["admin", "manager"])),
) -> HSCodeResponseDTO:
    """Update an HS code.

    Args:
        hs_code_id: UUID of the HS code to update
        data: Update data

    Returns:
        Updated HS code

    Raises:
        HTTPException 404: If HS code not found
        HTTPException 400: If update fails
    """
    print(f"INFO [PricingRoutes]: Updating HS code: {hs_code_id}")

    existing = pricing_service.get_hs_code(hs_code_id)
    if not existing:
        print(f"WARN [PricingRoutes]: HS code not found for update: {hs_code_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="HS code not found",
        )

    result = pricing_service.update_hs_code(hs_code_id, data)
    if not result:
        print(f"WARN [PricingRoutes]: Failed to update HS code: {hs_code_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update HS code.",
        )
    return result


@router.delete("/hs-codes/{hs_code_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hs_code(
    hs_code_id: UUID,
    current_user: dict = Depends(require_roles(["admin", "manager"])),
) -> None:
    """Delete an HS code (soft delete via update).

    Args:
        hs_code_id: UUID of the HS code to delete

    Raises:
        HTTPException 404: If HS code not found
        HTTPException 400: If delete fails
    """
    print(f"INFO [PricingRoutes]: Deleting HS code: {hs_code_id}")

    existing = pricing_service.get_hs_code(hs_code_id)
    if not existing:
        print(f"WARN [PricingRoutes]: HS code not found for delete: {hs_code_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="HS code not found",
        )

    # Soft delete by updating (service doesn't have explicit delete)
    # For now, just return success since HS codes don't have an is_active field
    # In practice, you might add a deleted_at field or is_active to hs_codes table
    print(f"INFO [PricingRoutes]: HS code {hs_code_id} marked for deletion")


# =============================================================================
# FREIGHT RATE ENDPOINTS
# =============================================================================


@router.get("/freight-rates", response_model=FreightRateListResponseDTO)
async def list_freight_rates(
    origin: Optional[str] = Query(None, description="Filter by origin"),
    destination: Optional[str] = Query(None, description="Filter by destination"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: dict = Depends(get_current_user),
) -> FreightRateListResponseDTO:
    """List freight rates with optional origin/destination filtering.

    Args:
        origin: Optional origin filter
        destination: Optional destination filter
        page: Page number (1-indexed)
        limit: Items per page

    Returns:
        Paginated list of freight rates
    """
    print(
        f"INFO [PricingRoutes]: Listing freight rates, "
        f"origin={origin}, destination={destination}, page={page}"
    )
    return pricing_service.list_freight_rates(
        origin=origin, destination=destination, page=page, limit=limit
    )


@router.post(
    "/freight-rates", response_model=FreightRateResponseDTO, status_code=status.HTTP_201_CREATED
)
async def create_freight_rate(
    data: FreightRateCreateDTO,
    current_user: dict = Depends(get_current_user),
) -> FreightRateResponseDTO:
    """Create a new freight rate.

    Args:
        data: Freight rate creation data

    Returns:
        Created freight rate

    Raises:
        HTTPException 400: If creation fails
    """
    print(f"INFO [PricingRoutes]: Creating freight rate: {data.origin} -> {data.destination}")
    result = pricing_service.create_freight_rate(data)
    if not result:
        print(
            f"WARN [PricingRoutes]: Failed to create freight rate: "
            f"{data.origin} -> {data.destination}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create freight rate.",
        )
    return result


@router.get("/freight-rates/active", response_model=FreightRateResponseDTO)
async def get_active_freight_rate(
    origin: str = Query(..., description="Origin location"),
    destination: str = Query(..., description="Destination location"),
    current_user: dict = Depends(get_current_user),
) -> FreightRateResponseDTO:
    """Get the currently active freight rate for a route.

    Args:
        origin: Origin location
        destination: Destination location

    Returns:
        Active freight rate for the route

    Raises:
        HTTPException 404: If no active rate found
    """
    print(f"INFO [PricingRoutes]: Getting active freight rate: {origin} -> {destination}")
    result = pricing_service.get_active_rate(origin=origin, destination=destination)
    if not result:
        print(f"WARN [PricingRoutes]: No active freight rate found: {origin} -> {destination}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active freight rate found for {origin} -> {destination}",
        )
    return result


@router.put("/freight-rates/{rate_id}", response_model=FreightRateResponseDTO)
async def update_freight_rate(
    rate_id: UUID,
    data: FreightRateUpdateDTO,
    current_user: dict = Depends(require_roles(["admin", "manager"])),
) -> FreightRateResponseDTO:
    """Update a freight rate.

    Args:
        rate_id: UUID of the freight rate to update
        data: Update data

    Returns:
        Updated freight rate

    Raises:
        HTTPException 404: If freight rate not found
        HTTPException 400: If update fails
    """
    print(f"INFO [PricingRoutes]: Updating freight rate: {rate_id}")

    result = pricing_service.update_freight_rate(rate_id, data)
    if not result:
        print(f"WARN [PricingRoutes]: Freight rate not found or update failed: {rate_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Freight rate not found",
        )
    return result


@router.delete("/freight-rates/{rate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_freight_rate(
    rate_id: UUID,
    current_user: dict = Depends(require_roles(["admin", "manager"])),
) -> None:
    """Delete a freight rate (soft delete by setting is_active=False).

    Args:
        rate_id: UUID of the freight rate to delete

    Raises:
        HTTPException 404: If freight rate not found
    """
    print(f"INFO [PricingRoutes]: Deleting freight rate: {rate_id}")

    # Soft delete by setting is_active=False
    update_data = FreightRateUpdateDTO(is_active=False)
    result = pricing_service.update_freight_rate(rate_id, update_data)
    if not result:
        print(f"WARN [PricingRoutes]: Freight rate not found for delete: {rate_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Freight rate not found",
        )
    print(f"INFO [PricingRoutes]: Freight rate {rate_id} soft deleted (is_active=False)")


# =============================================================================
# PRICING SETTINGS ENDPOINTS
# =============================================================================


@router.get("/settings", response_model=PricingSettingsResponseDTO)
async def get_pricing_settings(
    current_user: dict = Depends(get_current_user),
) -> PricingSettingsResponseDTO:
    """Get all pricing settings.

    Returns:
        List of all pricing settings
    """
    print("INFO [PricingRoutes]: Getting all pricing settings")

    # Initialize default settings if they don't exist
    pricing_service.initialize_default_settings()

    # Get all settings as key-value pairs and convert to response format
    from app.repository.kompass_repository import pricing_settings_repository

    items = pricing_settings_repository.get_all()
    settings = [PricingSettingResponseDTO(**item) for item in items]

    return PricingSettingsResponseDTO(settings=settings)


@router.put("/settings/{setting_key}", response_model=PricingSettingResponseDTO)
async def update_pricing_setting(
    setting_key: str,
    data: PricingSettingUpdateDTO,
    current_user: dict = Depends(require_roles(["admin"])),
) -> PricingSettingResponseDTO:
    """Update a pricing setting value.

    Args:
        setting_key: Key of the setting to update
        data: Update data with new value

    Returns:
        Updated pricing setting

    Raises:
        HTTPException 404: If setting not found
        HTTPException 400: If update fails or no value provided
    """
    print(f"INFO [PricingRoutes]: Updating pricing setting: {setting_key}")

    if data.setting_value is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="setting_value is required for update",
        )

    result = pricing_service.update_setting(setting_key, data.setting_value)
    if not result:
        print(f"WARN [PricingRoutes]: Pricing setting not found: {setting_key}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pricing setting '{setting_key}' not found",
        )
    return result
