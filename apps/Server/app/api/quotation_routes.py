"""Quotation API routes.

This module provides REST endpoints for quotation CRUD operations, pricing
calculations, line item management, status transitions, cloning, PDF export,
email sending, and public share links.
All endpoints require authentication except the public share endpoint.
"""

import io
from datetime import date
from typing import Dict, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from starlette import status

from app.api.dependencies import get_current_user
from app.api.rbac_dependencies import require_roles
from app.models.kompass_dto import (
    QuotationCloneDTO,
    QuotationCreateDTO,
    QuotationFilterDTO,
    QuotationItemCreateDTO,
    QuotationItemResponseDTO,
    QuotationItemUpdateDTO,
    QuotationListResponseDTO,
    QuotationPricingDTO,
    QuotationPublicResponseDTO,
    QuotationResponseDTO,
    QuotationSendEmailRequestDTO,
    QuotationSendEmailResponseDTO,
    QuotationShareTokenResponseDTO,
    QuotationStatus,
    QuotationStatusTransitionDTO,
    QuotationUpdateDTO,
)
from app.services.quotation_service import quotation_service

router = APIRouter(tags=["Quotations"])


# =============================================================================
# PUBLIC SHARE ENDPOINT (No Authentication Required)
# =============================================================================


@router.get("/share/{token}", response_model=QuotationPublicResponseDTO)
async def get_quotation_by_share_token(
    token: str,
) -> QuotationPublicResponseDTO:
    """Get a quotation by its share token.

    This endpoint is PUBLIC and does NOT require authentication.

    Args:
        token: JWT share token

    Returns:
        QuotationPublicResponseDTO

    Raises:
        HTTPException 404: If token is invalid, expired, or quotation not found
    """
    print("INFO [QuotationRoutes]: Accessing quotation via share token")

    result = quotation_service.get_by_share_token(token)

    if not result:
        print("WARN [QuotationRoutes]: Invalid or expired share token")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired share token, or quotation not found",
        )

    print(f"INFO [QuotationRoutes]: Retrieved quotation {result.id} via share token")
    return result


# =============================================================================
# CRUD ENDPOINTS
# =============================================================================


@router.get("", response_model=QuotationListResponseDTO)
async def list_quotations(
    client_id: Optional[UUID] = Query(None, description="Filter by client"),
    status: Optional[str] = Query(
        None,
        description="Filter by status: draft | sent | viewed | negotiating | accepted | rejected | expired",
    ),
    created_by: Optional[UUID] = Query(None, description="Filter by creator"),
    date_from: Optional[date] = Query(None, description="Filter by created_at start date"),
    date_to: Optional[date] = Query(None, description="Filter by created_at end date"),
    search: Optional[str] = Query(
        None, description="Search by quotation number or client name"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: dict = Depends(get_current_user),
) -> QuotationListResponseDTO:
    """List quotations with pagination, filtering, and search.

    Args:
        client_id: Filter by client
        status: Filter by quotation status
        created_by: Filter by creator user
        date_from: Filter by created_at start date
        date_to: Filter by created_at end date
        search: Search query for quotation number or client name
        page: Page number (1-indexed)
        limit: Items per page (max 100)
        current_user: Authenticated user (injected)

    Returns:
        Paginated list of quotations
    """
    print(f"INFO [QuotationRoutes]: Listing quotations, page {page}")

    # Convert status string to enum if provided
    status_enum: Optional[QuotationStatus] = None
    if status:
        try:
            status_enum = QuotationStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status value: {status}. Must be one of: draft, sent, viewed, negotiating, accepted, rejected, expired",
            )

    filters = QuotationFilterDTO(
        client_id=client_id,
        status=status_enum,
        created_by=created_by,
        date_from=date_from,
        date_to=date_to,
        search=search,
    )

    return quotation_service.list_quotations(
        filters=filters,
        page=page,
        limit=limit,
    )


@router.post("", response_model=QuotationResponseDTO, status_code=201)
async def create_quotation(
    request: QuotationCreateDTO,
    current_user: dict = Depends(get_current_user),
) -> QuotationResponseDTO:
    """Create a new quotation.

    Args:
        request: Quotation creation data
        current_user: Authenticated user (injected)

    Returns:
        Created quotation

    Raises:
        HTTPException 400: If creation fails
    """
    print(f"INFO [QuotationRoutes]: Creating quotation for client {request.client_id}")

    result = quotation_service.create_quotation(
        request=request,
        created_by=current_user["id"],
    )

    if not result:
        print("WARN [QuotationRoutes]: Failed to create quotation")
        raise HTTPException(status_code=400, detail="Failed to create quotation")

    print(f"INFO [QuotationRoutes]: Quotation created successfully: {result.id}")
    return result


@router.get("/{quotation_id}", response_model=QuotationResponseDTO)
async def get_quotation(
    quotation_id: UUID,
    current_user: dict = Depends(get_current_user),
) -> QuotationResponseDTO:
    """Get a quotation by ID.

    Args:
        quotation_id: UUID of the quotation
        current_user: Authenticated user (injected)

    Returns:
        Quotation data

    Raises:
        HTTPException 404: If quotation not found
    """
    print(f"INFO [QuotationRoutes]: Getting quotation: {quotation_id}")

    result = quotation_service.get_quotation(quotation_id)

    if not result:
        print(f"WARN [QuotationRoutes]: Quotation not found: {quotation_id}")
        raise HTTPException(status_code=404, detail="Quotation not found")

    print(f"INFO [QuotationRoutes]: Found quotation: {quotation_id}")
    return result


@router.put("/{quotation_id}", response_model=QuotationResponseDTO)
async def update_quotation(
    quotation_id: UUID,
    request: QuotationUpdateDTO,
    current_user: dict = Depends(get_current_user),
) -> QuotationResponseDTO:
    """Update a quotation.

    Args:
        quotation_id: UUID of the quotation to update
        request: Update data
        current_user: Authenticated user (injected)

    Returns:
        Updated quotation

    Raises:
        HTTPException 404: If quotation not found
    """
    print(f"INFO [QuotationRoutes]: Updating quotation: {quotation_id}")

    result = quotation_service.update_quotation(quotation_id, request)

    if not result:
        print(f"WARN [QuotationRoutes]: Quotation not found: {quotation_id}")
        raise HTTPException(status_code=404, detail="Quotation not found")

    print(f"INFO [QuotationRoutes]: Quotation updated successfully: {quotation_id}")
    return result


@router.delete("/{quotation_id}")
async def delete_quotation(
    quotation_id: UUID,
    current_user: dict = Depends(require_roles(["admin", "manager"])),
) -> Dict[str, str]:
    """Delete a quotation (admin/manager only).

    Args:
        quotation_id: UUID of the quotation to delete
        current_user: Authenticated admin/manager user (injected)

    Returns:
        Success message

    Raises:
        HTTPException 404: If quotation not found
    """
    print(f"INFO [QuotationRoutes]: Deleting quotation: {quotation_id}")

    result = quotation_service.delete_quotation(quotation_id)

    if not result:
        print(f"WARN [QuotationRoutes]: Quotation not found: {quotation_id}")
        raise HTTPException(status_code=404, detail="Quotation not found")

    print(f"INFO [QuotationRoutes]: Quotation deleted successfully: {quotation_id}")
    return {"message": "Quotation deleted successfully"}


@router.post("/{quotation_id}/clone", response_model=QuotationResponseDTO, status_code=201)
async def clone_quotation(
    quotation_id: UUID,
    request: Optional[QuotationCloneDTO] = None,
    current_user: dict = Depends(get_current_user),
) -> QuotationResponseDTO:
    """Clone a quotation to create a new version.

    Creates a copy with a new quotation number and draft status.

    Args:
        quotation_id: UUID of the quotation to clone
        request: Optional clone parameters
        current_user: Authenticated user (injected)

    Returns:
        Cloned quotation

    Raises:
        HTTPException 404: If source quotation not found
    """
    print(f"INFO [QuotationRoutes]: Cloning quotation: {quotation_id}")

    result = quotation_service.clone_quotation(
        quotation_id=quotation_id,
        created_by=current_user["id"],
        clone_request=request,
    )

    if not result:
        print(f"WARN [QuotationRoutes]: Quotation not found for cloning: {quotation_id}")
        raise HTTPException(status_code=404, detail="Quotation not found")

    print(f"INFO [QuotationRoutes]: Quotation cloned successfully: {result.id}")
    return result


@router.get("/{quotation_id}/pricing", response_model=QuotationPricingDTO)
async def calculate_pricing(
    quotation_id: UUID,
    current_user: dict = Depends(get_current_user),
) -> QuotationPricingDTO:
    """Calculate comprehensive pricing for a quotation.

    Computes all cost components including FOB, tariffs, freight, insurance,
    nationalization, and margin to produce the final COP total.

    Args:
        quotation_id: UUID of the quotation
        current_user: Authenticated user (injected)

    Returns:
        Detailed pricing breakdown

    Raises:
        HTTPException 404: If quotation not found
    """
    print(f"INFO [QuotationRoutes]: Calculating pricing for quotation: {quotation_id}")

    result = quotation_service.calculate_pricing(quotation_id)

    if not result:
        print(f"WARN [QuotationRoutes]: Quotation not found: {quotation_id}")
        raise HTTPException(status_code=404, detail="Quotation not found")

    print(
        f"INFO [QuotationRoutes]: Pricing calculated for quotation: {quotation_id}, "
        f"Total: {result.total_cop} COP"
    )
    return result


@router.put("/{quotation_id}/status", response_model=QuotationResponseDTO)
async def update_status(
    quotation_id: UUID,
    request: QuotationStatusTransitionDTO,
    current_user: dict = Depends(get_current_user),
) -> QuotationResponseDTO:
    """Update quotation status.

    Validates that the status transition is allowed before updating.
    Valid transitions:
    - draft -> sent
    - sent -> viewed, accepted, rejected, expired
    - viewed -> negotiating, accepted, rejected, expired
    - negotiating -> accepted, rejected, expired

    Args:
        quotation_id: UUID of the quotation
        request: Status transition request
        current_user: Authenticated user (injected)

    Returns:
        Updated quotation

    Raises:
        HTTPException 400: If status transition is invalid
        HTTPException 404: If quotation not found
    """
    print(
        f"INFO [QuotationRoutes]: Updating status for quotation: {quotation_id} "
        f"to {request.new_status.value}"
    )

    try:
        result = quotation_service.update_status(quotation_id, request)

        if not result:
            print(f"WARN [QuotationRoutes]: Quotation not found: {quotation_id}")
            raise HTTPException(status_code=404, detail="Quotation not found")

        print(
            f"INFO [QuotationRoutes]: Status updated successfully for quotation: {quotation_id}"
        )
        return result
    except ValueError as e:
        print(f"WARN [QuotationRoutes]: Invalid status transition: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# =============================================================================
# CALCULATE, PDF EXPORT, EMAIL, AND SHARE TOKEN ENDPOINTS
# =============================================================================


@router.post("/{quotation_id}/calculate", response_model=QuotationPricingDTO)
async def recalculate_and_persist_pricing(
    quotation_id: UUID,
    current_user: dict = Depends(get_current_user),
) -> QuotationPricingDTO:
    """Recalculate pricing for a quotation and persist the results.

    Computes all cost components and updates the quotation totals in the database.

    Args:
        quotation_id: UUID of the quotation
        current_user: Authenticated user (injected)

    Returns:
        Detailed pricing breakdown

    Raises:
        HTTPException 404: If quotation not found
    """
    print(f"INFO [QuotationRoutes]: Recalculating and persisting pricing for quotation: {quotation_id}")

    result = quotation_service.recalculate_and_persist(quotation_id)

    if not result:
        print(f"WARN [QuotationRoutes]: Quotation not found: {quotation_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quotation not found")

    print(
        f"INFO [QuotationRoutes]: Pricing recalculated and persisted for quotation: {quotation_id}, "
        f"Total: {result.total_cop} COP"
    )
    return result


@router.get("/{quotation_id}/export/pdf")
async def export_quotation_pdf(
    quotation_id: UUID,
    current_user: dict = Depends(get_current_user),
) -> StreamingResponse:
    """Export a quotation as a PDF proforma document.

    Generates a formatted PDF with quotation details, line items, and totals.

    Args:
        quotation_id: UUID of the quotation
        current_user: Authenticated user (injected)

    Returns:
        StreamingResponse with PDF content

    Raises:
        HTTPException 404: If quotation not found
    """
    print(f"INFO [QuotationRoutes]: Exporting PDF for quotation: {quotation_id}")

    pdf_bytes = quotation_service.generate_pdf(quotation_id)

    if not pdf_bytes:
        print(f"WARN [QuotationRoutes]: Quotation not found for PDF export: {quotation_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quotation not found",
        )

    # Get quotation for filename
    quotation = quotation_service.get_quotation(quotation_id)
    filename = f"{quotation.quotation_number}_proforma.pdf" if quotation else "quotation.pdf"

    print(f"INFO [QuotationRoutes]: PDF exported for quotation {quotation_id}")

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.post("/{quotation_id}/send", response_model=QuotationSendEmailResponseDTO)
async def send_quotation_email(
    quotation_id: UUID,
    request: QuotationSendEmailRequestDTO,
    current_user: dict = Depends(get_current_user),
) -> QuotationSendEmailResponseDTO:
    """Send a quotation via email.

    Sends the quotation to the specified recipient with optional PDF attachment.
    Supports mock mode via EMAIL_MOCK_MODE environment variable.

    Args:
        quotation_id: UUID of the quotation
        request: Email sending request with recipient details
        current_user: Authenticated user (injected)

    Returns:
        QuotationSendEmailResponseDTO with result

    Raises:
        HTTPException 404: If quotation not found
    """
    print(f"INFO [QuotationRoutes]: Sending quotation {quotation_id} to {request.recipient_email}")

    result = quotation_service.send_email(quotation_id, request)

    if not result:
        print(f"WARN [QuotationRoutes]: Quotation not found: {quotation_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quotation not found",
        )

    print(f"INFO [QuotationRoutes]: Email send result for quotation {quotation_id}: {result.success}")
    return result


@router.post("/{quotation_id}/share", response_model=QuotationShareTokenResponseDTO)
async def generate_share_token(
    quotation_id: UUID,
    current_user: dict = Depends(get_current_user),
) -> QuotationShareTokenResponseDTO:
    """Generate a share token for public quotation access.

    The token allows anyone to view the quotation without authentication.

    Args:
        quotation_id: UUID of the quotation
        current_user: Authenticated user (injected)

    Returns:
        QuotationShareTokenResponseDTO with token and expiration

    Raises:
        HTTPException 404: If quotation not found
    """
    print(f"INFO [QuotationRoutes]: Generating share token for quotation {quotation_id}")

    result = quotation_service.get_share_token(quotation_id)

    if not result:
        print(f"WARN [QuotationRoutes]: Quotation not found: {quotation_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quotation not found",
        )

    print(f"INFO [QuotationRoutes]: Share token generated for quotation {quotation_id}")
    return result


# =============================================================================
# LINE ITEM ENDPOINTS
# =============================================================================


@router.post("/{quotation_id}/items", response_model=QuotationItemResponseDTO, status_code=201)
async def add_item(
    quotation_id: UUID,
    request: QuotationItemCreateDTO,
    current_user: dict = Depends(get_current_user),
) -> QuotationItemResponseDTO:
    """Add a line item to a quotation.

    Args:
        quotation_id: UUID of the quotation
        request: Item creation data
        current_user: Authenticated user (injected)

    Returns:
        Created line item

    Raises:
        HTTPException 404: If quotation not found
    """
    print(f"INFO [QuotationRoutes]: Adding item to quotation: {quotation_id}")

    result = quotation_service.add_item(quotation_id, request)

    if not result:
        print(f"WARN [QuotationRoutes]: Quotation not found: {quotation_id}")
        raise HTTPException(status_code=404, detail="Quotation not found")

    print(f"INFO [QuotationRoutes]: Item added successfully to quotation: {quotation_id}")
    return result


@router.put("/{quotation_id}/items/{item_id}", response_model=QuotationItemResponseDTO)
async def update_item(
    quotation_id: UUID,
    item_id: UUID,
    request: QuotationItemUpdateDTO,
    current_user: dict = Depends(get_current_user),
) -> QuotationItemResponseDTO:
    """Update a quotation line item.

    Args:
        quotation_id: UUID of the quotation
        item_id: UUID of the item to update
        request: Update data
        current_user: Authenticated user (injected)

    Returns:
        Updated line item

    Raises:
        HTTPException 404: If quotation or item not found
        HTTPException 400: If item doesn't belong to the quotation
    """
    print(f"INFO [QuotationRoutes]: Updating item {item_id} in quotation {quotation_id}")

    # Validate item belongs to quotation
    if not quotation_service.validate_item_belongs_to_quotation(quotation_id, item_id):
        print(f"WARN [QuotationRoutes]: Item {item_id} not found in quotation {quotation_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found in the specified quotation",
        )

    result = quotation_service.update_item(item_id, request)

    if not result:
        print(f"WARN [QuotationRoutes]: Item not found: {item_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    print(f"INFO [QuotationRoutes]: Item updated successfully: {item_id}")
    return result


@router.delete("/{quotation_id}/items/{item_id}")
async def remove_item(
    quotation_id: UUID,
    item_id: UUID,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, str]:
    """Remove a line item from a quotation.

    Args:
        quotation_id: UUID of the quotation
        item_id: UUID of the item to remove
        current_user: Authenticated user (injected)

    Returns:
        Success message

    Raises:
        HTTPException 404: If quotation or item not found
        HTTPException 400: If item doesn't belong to the quotation
    """
    print(f"INFO [QuotationRoutes]: Removing item {item_id} from quotation {quotation_id}")

    # Validate item belongs to quotation
    if not quotation_service.validate_item_belongs_to_quotation(quotation_id, item_id):
        print(f"WARN [QuotationRoutes]: Item {item_id} not found in quotation {quotation_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found in the specified quotation",
        )

    result = quotation_service.remove_item(item_id)

    if not result:
        print(f"WARN [QuotationRoutes]: Item not found: {item_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    print(f"INFO [QuotationRoutes]: Item removed successfully: {item_id}")
    return {"message": "Item removed successfully"}
