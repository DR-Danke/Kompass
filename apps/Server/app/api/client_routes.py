"""Client API routes for CRM functionality.

This module provides REST endpoints for client CRUD operations, pipeline
management, status history tracking, and timing feasibility calculations.
All endpoints require authentication and some require admin/manager roles.
"""

from datetime import date
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_current_user
from app.api.rbac_dependencies import require_roles
from app.models.kompass_dto import (
    ClientCreateDTO,
    ClientListResponseDTO,
    ClientResponseDTO,
    ClientSource,
    ClientStatus,
    ClientStatusChangeDTO,
    ClientUpdateDTO,
    ClientWithQuotationsDTO,
    PipelineResponseDTO,
    StatusHistoryResponseDTO,
    TimingFeasibilityDTO,
)
from app.services.client_service import client_service

router = APIRouter(tags=["Clients"])


@router.get("", response_model=ClientListResponseDTO)
async def list_clients(
    status: Optional[str] = Query(
        None, description="Filter by status: active | inactive | prospect"
    ),
    niche_id: Optional[UUID] = Query(None, description="Filter by niche"),
    assigned_to: Optional[UUID] = Query(None, description="Filter by assigned user"),
    source: Optional[str] = Query(
        None, description="Filter by source: website | referral | cold_call | trade_show | linkedin | other"
    ),
    date_from: Optional[date] = Query(None, description="Filter by created_at start date"),
    date_to: Optional[date] = Query(None, description="Filter by created_at end date"),
    search: Optional[str] = Query(None, description="Search by company/contact/email"),
    sort_by: str = Query(
        "company_name", description="Sort by: company_name | created_at | project_deadline"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: dict = Depends(get_current_user),
) -> ClientListResponseDTO:
    """List clients with pagination, filtering, and sorting.

    Args:
        status: Filter by client status
        niche_id: Filter by niche
        assigned_to: Filter by assigned user
        source: Filter by lead source
        date_from: Filter by created_at start date
        date_to: Filter by created_at end date
        search: Search query for company/contact/email
        sort_by: Field to sort by
        page: Page number (1-indexed)
        limit: Items per page (max 100)
        current_user: Authenticated user (injected)

    Returns:
        Paginated list of clients
    """
    print(f"INFO [ClientRoutes]: Listing clients, page {page}")

    # Convert status string to enum if provided
    status_enum: Optional[ClientStatus] = None
    if status:
        try:
            status_enum = ClientStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status value: {status}. Must be one of: active, inactive, prospect",
            )

    # Convert source string to enum if provided
    source_enum: Optional[ClientSource] = None
    if source:
        try:
            source_enum = ClientSource(source)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid source value: {source}. Must be one of: website, referral, cold_call, trade_show, linkedin, other",
            )

    return client_service.list_clients(
        status=status_enum,
        niche_id=niche_id,
        assigned_to=assigned_to,
        source=source_enum,
        date_from=date_from,
        date_to=date_to,
        search=search,
        sort_by=sort_by,
        page=page,
        limit=limit,
    )


@router.post("", response_model=ClientResponseDTO, status_code=201)
async def create_client(
    request: ClientCreateDTO,
    current_user: dict = Depends(get_current_user),
) -> ClientResponseDTO:
    """Create a new client.

    Args:
        request: Client creation data
        current_user: Authenticated user (injected)

    Returns:
        Created client

    Raises:
        HTTPException 400: If validation fails
    """
    print(f"INFO [ClientRoutes]: Creating client: {request.company_name}")

    try:
        result = client_service.create_client(request)
        print(f"INFO [ClientRoutes]: Client created successfully: {result.id}")
        return result
    except ValueError as e:
        print(f"WARN [ClientRoutes]: Failed to create client: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/search", response_model=List[ClientResponseDTO])
async def search_clients(
    query: str = Query(..., min_length=2, description="Search query"),
    current_user: dict = Depends(get_current_user),
) -> List[ClientResponseDTO]:
    """Search clients by company name, contact name, or email.

    Args:
        query: Search query (min 2 characters)
        current_user: Authenticated user (injected)

    Returns:
        List of matching clients (max 50)
    """
    print(f"INFO [ClientRoutes]: Searching clients with query: {query}")

    results = client_service.search_clients(query)
    print(f"INFO [ClientRoutes]: Search returned {len(results)} results")
    return results


@router.get("/pipeline", response_model=PipelineResponseDTO)
async def get_pipeline(
    current_user: dict = Depends(get_current_user),
) -> PipelineResponseDTO:
    """Get clients grouped by status for pipeline view.

    Args:
        current_user: Authenticated user (injected)

    Returns:
        Clients grouped by status (prospect, active, inactive)
    """
    print("INFO [ClientRoutes]: Getting client pipeline")

    return client_service.get_pipeline()


@router.get("/{client_id}", response_model=ClientResponseDTO)
async def get_client(
    client_id: UUID,
    current_user: dict = Depends(get_current_user),
) -> ClientResponseDTO:
    """Get a client by ID.

    Args:
        client_id: UUID of the client
        current_user: Authenticated user (injected)

    Returns:
        Client data

    Raises:
        HTTPException 404: If client not found
    """
    print(f"INFO [ClientRoutes]: Getting client: {client_id}")

    result = client_service.get_client(client_id)

    if not result:
        print(f"WARN [ClientRoutes]: Client not found: {client_id}")
        raise HTTPException(status_code=404, detail="Client not found")

    print(f"INFO [ClientRoutes]: Found client: {client_id}")
    return result


@router.get("/{client_id}/quotations", response_model=ClientWithQuotationsDTO)
async def get_client_with_quotations(
    client_id: UUID,
    current_user: dict = Depends(get_current_user),
) -> ClientWithQuotationsDTO:
    """Get a client by ID with quotation history summary.

    Args:
        client_id: UUID of the client
        current_user: Authenticated user (injected)

    Returns:
        Client data with quotation summary

    Raises:
        HTTPException 404: If client not found
    """
    print(f"INFO [ClientRoutes]: Getting client with quotations: {client_id}")

    result = client_service.get_client_with_quotations(client_id)

    if not result:
        print(f"WARN [ClientRoutes]: Client not found: {client_id}")
        raise HTTPException(status_code=404, detail="Client not found")

    print(f"INFO [ClientRoutes]: Found client with quotations: {client_id}")
    return result


@router.put("/{client_id}", response_model=ClientResponseDTO)
async def update_client(
    client_id: UUID,
    request: ClientUpdateDTO,
    current_user: dict = Depends(get_current_user),
) -> ClientResponseDTO:
    """Update a client.

    Args:
        client_id: UUID of the client to update
        request: Update data
        current_user: Authenticated user (injected)

    Returns:
        Updated client

    Raises:
        HTTPException 400: If validation fails
        HTTPException 404: If client not found
    """
    print(f"INFO [ClientRoutes]: Updating client: {client_id}")

    try:
        result = client_service.update_client(client_id, request)

        if not result:
            print(f"WARN [ClientRoutes]: Client not found: {client_id}")
            raise HTTPException(status_code=404, detail="Client not found")

        print(f"INFO [ClientRoutes]: Client updated successfully: {client_id}")
        return result
    except ValueError as e:
        print(f"WARN [ClientRoutes]: Failed to update client: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{client_id}")
async def delete_client(
    client_id: UUID,
    current_user: dict = Depends(require_roles(["admin", "manager"])),
) -> Dict[str, str]:
    """Soft delete a client (admin/manager only).

    Sets the client status to inactive. Cannot delete clients
    with active quotations.

    Args:
        client_id: UUID of the client to delete
        current_user: Authenticated admin/manager user (injected)

    Returns:
        Success message

    Raises:
        HTTPException 400: If client has active quotations
        HTTPException 404: If client not found
    """
    print(f"INFO [ClientRoutes]: Deleting client: {client_id}")

    try:
        result = client_service.delete_client(client_id)

        if not result:
            print(f"WARN [ClientRoutes]: Client not found: {client_id}")
            raise HTTPException(status_code=404, detail="Client not found")

        print(f"INFO [ClientRoutes]: Client deleted successfully: {client_id}")
        return {"message": "Client deleted successfully"}
    except ValueError as e:
        print(f"WARN [ClientRoutes]: Blocked deletion of client: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{client_id}/status", response_model=ClientResponseDTO)
async def update_client_status(
    client_id: UUID,
    request: ClientStatusChangeDTO,
    current_user: dict = Depends(get_current_user),
) -> ClientResponseDTO:
    """Update client status with notes and record history.

    Args:
        client_id: UUID of the client
        request: Status change request with new status and optional notes
        current_user: Authenticated user (injected)

    Returns:
        Updated client

    Raises:
        HTTPException 400: If update fails
        HTTPException 404: If client not found
    """
    print(f"INFO [ClientRoutes]: Updating status for client: {client_id}")

    try:
        result = client_service.update_status(
            client_id=client_id,
            status_change=request,
            changed_by=current_user["id"],
        )

        if not result:
            print(f"WARN [ClientRoutes]: Client not found: {client_id}")
            raise HTTPException(status_code=404, detail="Client not found")

        print(
            f"INFO [ClientRoutes]: Status updated successfully for client: {client_id}"
        )
        return result
    except ValueError as e:
        print(f"WARN [ClientRoutes]: Failed to update status: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{client_id}/status-history", response_model=List[StatusHistoryResponseDTO])
async def get_status_history(
    client_id: UUID,
    current_user: dict = Depends(get_current_user),
) -> List[StatusHistoryResponseDTO]:
    """Get status change history for a client.

    Args:
        client_id: UUID of the client
        current_user: Authenticated user (injected)

    Returns:
        List of status history entries

    Raises:
        HTTPException 404: If client not found
    """
    print(f"INFO [ClientRoutes]: Getting status history for client: {client_id}")

    # Check if client exists
    client = client_service.get_client(client_id)
    if not client:
        print(f"WARN [ClientRoutes]: Client not found: {client_id}")
        raise HTTPException(status_code=404, detail="Client not found")

    history = client_service.get_status_history(client_id)
    print(f"INFO [ClientRoutes]: Found {len(history)} status history entries")
    return history


@router.get("/{client_id}/history", response_model=List[StatusHistoryResponseDTO])
async def get_client_history(
    client_id: UUID,
    current_user: dict = Depends(get_current_user),
) -> List[StatusHistoryResponseDTO]:
    """Get status change history for a client (alias for /status-history).

    Args:
        client_id: UUID of the client
        current_user: Authenticated user (injected)

    Returns:
        List of status history entries

    Raises:
        HTTPException 404: If client not found
    """
    return await get_status_history(client_id, current_user)


@router.get("/{client_id}/timing-feasibility", response_model=TimingFeasibilityDTO)
async def get_timing_feasibility(
    client_id: UUID,
    product_lead_time_days: int = Query(..., ge=0, description="Production lead time in days"),
    current_user: dict = Depends(get_current_user),
) -> TimingFeasibilityDTO:
    """Calculate timing feasibility for project deadline.

    Args:
        client_id: UUID of the client
        product_lead_time_days: Production lead time in days
        current_user: Authenticated user (injected)

    Returns:
        Timing feasibility result with breakdown

    Raises:
        HTTPException 404: If client not found
    """
    print(f"INFO [ClientRoutes]: Calculating timing feasibility for client: {client_id}")

    result = client_service.calculate_timing_feasibility(
        client_id=client_id,
        product_lead_time_days=product_lead_time_days,
    )

    if not result:
        print(f"WARN [ClientRoutes]: Client not found: {client_id}")
        raise HTTPException(status_code=404, detail="Client not found")

    print(f"INFO [ClientRoutes]: Timing feasibility calculated: {result.message}")
    return result
