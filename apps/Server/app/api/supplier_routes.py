"""Supplier API routes for managing supplier records.

This module provides REST endpoints for supplier CRUD operations, including
pagination, filtering, search, and related product listing. All endpoints
require authentication and some require admin/manager roles.
"""

from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_current_user
from app.api.rbac_dependencies import require_roles
from app.models.kompass_dto import (
    ProductFilterDTO,
    ProductListResponseDTO,
    SupplierCertificationSummaryDTO,
    SupplierCreateDTO,
    SupplierListResponseDTO,
    SupplierPipelineStatus,
    SupplierPipelineStatusUpdateDTO,
    SupplierResponseDTO,
    SupplierStatus,
    SupplierUpdateDTO,
)
from app.services.product_service import product_service
from app.services.supplier_service import supplier_service

router = APIRouter(tags=["Suppliers"])


@router.get("", response_model=SupplierListResponseDTO)
async def list_suppliers(
    status: Optional[str] = Query(
        None, description="Filter by status: active | inactive | pending_review"
    ),
    country: Optional[str] = Query(None, description="Filter by country"),
    has_products: Optional[bool] = Query(
        None, description="Filter by whether supplier has products"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("name", description="Sort by: name | created_at"),
    sort_order: str = Query("asc", description="Sort order: asc | desc"),
    current_user: dict = Depends(get_current_user),
) -> SupplierListResponseDTO:
    """List suppliers with pagination, filtering, and sorting.

    Args:
        status: Filter by supplier status
        country: Filter by country
        has_products: Filter by whether supplier has products
        page: Page number (1-indexed)
        limit: Items per page (max 100)
        sort_by: Field to sort by
        sort_order: Sort direction
        current_user: Authenticated user (injected)

    Returns:
        Paginated list of suppliers
    """
    print(f"INFO [SupplierRoutes]: Listing suppliers, page {page}")

    # Convert status string to enum if provided
    status_enum: Optional[SupplierStatus] = None
    if status:
        try:
            status_enum = SupplierStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status value: {status}. Must be one of: active, inactive, pending_review",
            )

    return supplier_service.list_suppliers(
        status=status_enum,
        country=country,
        has_products=has_products,
        page=page,
        limit=limit,
        sort_by=sort_by,
    )


@router.post("", response_model=SupplierResponseDTO, status_code=201)
async def create_supplier(
    request: SupplierCreateDTO,
    current_user: dict = Depends(get_current_user),
) -> SupplierResponseDTO:
    """Create a new supplier.

    Args:
        request: Supplier creation data
        current_user: Authenticated user (injected)

    Returns:
        Created supplier

    Raises:
        HTTPException 400: If validation fails
    """
    print(f"INFO [SupplierRoutes]: Creating supplier: {request.name}")

    try:
        result = supplier_service.create_supplier(request)
        print(f"INFO [SupplierRoutes]: Supplier created successfully: {result.id}")
        return result
    except ValueError as e:
        print(f"WARN [SupplierRoutes]: Failed to create supplier: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/search", response_model=List[SupplierResponseDTO])
async def search_suppliers(
    query: str = Query(..., min_length=2, description="Search query"),
    current_user: dict = Depends(get_current_user),
) -> List[SupplierResponseDTO]:
    """Search suppliers by name, email, or contact phone.

    Args:
        query: Search query (min 2 characters)
        current_user: Authenticated user (injected)

    Returns:
        List of matching suppliers (max 50)
    """
    print(f"INFO [SupplierRoutes]: Searching suppliers with query: {query}")

    results = supplier_service.search_suppliers(query)
    print(f"INFO [SupplierRoutes]: Search returned {len(results)} results")
    return results


@router.get("/certified", response_model=SupplierListResponseDTO)
async def list_certified_suppliers(
    grade: Optional[str] = Query(
        None, description="Filter by certification grade: A | B | C"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: dict = Depends(get_current_user),
) -> SupplierListResponseDTO:
    """List only certified suppliers (certified_a, certified_b, certified_c).

    Args:
        grade: Optional filter by grade (A, B, C)
        page: Page number (1-indexed)
        limit: Items per page (max 100)
        current_user: Authenticated user (injected)

    Returns:
        Paginated list of certified suppliers
    """
    print(f"INFO [SupplierRoutes]: Listing certified suppliers, grade={grade}, page {page}")

    try:
        result = supplier_service.list_certified_suppliers(
            grade=grade,
            page=page,
            limit=limit,
        )
        print(
            f"INFO [SupplierRoutes]: Found {result.pagination.total} certified suppliers"
        )
        return result
    except ValueError as e:
        print(f"WARN [SupplierRoutes]: Invalid grade parameter: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/pipeline/{status}", response_model=SupplierListResponseDTO)
async def list_suppliers_by_pipeline(
    status: str,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: dict = Depends(get_current_user),
) -> SupplierListResponseDTO:
    """List suppliers filtered by pipeline status.

    Args:
        status: Pipeline status (contacted/potential/quoted/certified/active/inactive)
        page: Page number (1-indexed)
        limit: Items per page (max 100)
        current_user: Authenticated user (injected)

    Returns:
        Paginated list of suppliers with the specified pipeline status
    """
    print(f"INFO [SupplierRoutes]: Listing suppliers by pipeline status={status}, page {page}")

    # Validate pipeline status
    try:
        pipeline_status = SupplierPipelineStatus(status)
    except ValueError:
        valid_statuses = ", ".join([s.value for s in SupplierPipelineStatus])
        raise HTTPException(
            status_code=400,
            detail=f"Invalid pipeline status: {status}. Must be one of: {valid_statuses}",
        )

    result = supplier_service.list_suppliers_by_pipeline(
        pipeline_status=pipeline_status,
        page=page,
        limit=limit,
    )
    print(
        f"INFO [SupplierRoutes]: Found {result.pagination.total} suppliers "
        f"with pipeline_status={status}"
    )
    return result


@router.get("/{supplier_id}")
async def get_supplier(
    supplier_id: UUID,
    current_user: dict = Depends(get_current_user),
) -> Dict:
    """Get a supplier by ID with product count.

    Args:
        supplier_id: UUID of the supplier
        current_user: Authenticated user (injected)

    Returns:
        Supplier data with product_count field

    Raises:
        HTTPException 404: If supplier not found
    """
    print(f"INFO [SupplierRoutes]: Getting supplier: {supplier_id}")

    result = supplier_service.get_supplier_with_product_count(supplier_id)

    if not result:
        print(f"WARN [SupplierRoutes]: Supplier not found: {supplier_id}")
        raise HTTPException(status_code=404, detail="Supplier not found")

    print(f"INFO [SupplierRoutes]: Found supplier: {supplier_id}")
    return result


@router.put("/{supplier_id}", response_model=SupplierResponseDTO)
async def update_supplier(
    supplier_id: UUID,
    request: SupplierUpdateDTO,
    current_user: dict = Depends(get_current_user),
) -> SupplierResponseDTO:
    """Update a supplier.

    Args:
        supplier_id: UUID of the supplier to update
        request: Update data
        current_user: Authenticated user (injected)

    Returns:
        Updated supplier

    Raises:
        HTTPException 400: If validation fails
        HTTPException 404: If supplier not found
    """
    print(f"INFO [SupplierRoutes]: Updating supplier: {supplier_id}")

    try:
        result = supplier_service.update_supplier(supplier_id, request)

        if not result:
            print(f"WARN [SupplierRoutes]: Supplier not found: {supplier_id}")
            raise HTTPException(status_code=404, detail="Supplier not found")

        print(f"INFO [SupplierRoutes]: Supplier updated successfully: {supplier_id}")
        return result
    except ValueError as e:
        print(f"WARN [SupplierRoutes]: Failed to update supplier: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{supplier_id}")
async def delete_supplier(
    supplier_id: UUID,
    current_user: dict = Depends(require_roles(["admin", "manager"])),
) -> Dict[str, str]:
    """Soft delete a supplier (admin/manager only).

    Sets the supplier status to inactive. Cannot delete suppliers
    with active products.

    Args:
        supplier_id: UUID of the supplier to delete
        current_user: Authenticated admin/manager user (injected)

    Returns:
        Success message

    Raises:
        HTTPException 400: If supplier has active products
        HTTPException 404: If supplier not found
    """
    print(f"INFO [SupplierRoutes]: Deleting supplier: {supplier_id}")

    try:
        result = supplier_service.delete_supplier(supplier_id)

        if not result:
            print(f"WARN [SupplierRoutes]: Supplier not found: {supplier_id}")
            raise HTTPException(status_code=404, detail="Supplier not found")

        print(f"INFO [SupplierRoutes]: Supplier deleted successfully: {supplier_id}")
        return {"message": "Supplier deleted successfully"}
    except ValueError as e:
        print(f"WARN [SupplierRoutes]: Blocked deletion of supplier: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{supplier_id}/products", response_model=ProductListResponseDTO)
async def get_supplier_products(
    supplier_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: dict = Depends(get_current_user),
) -> ProductListResponseDTO:
    """Get products for a specific supplier.

    Args:
        supplier_id: UUID of the supplier
        page: Page number (1-indexed)
        limit: Items per page (max 100)
        current_user: Authenticated user (injected)

    Returns:
        Paginated list of products for the supplier

    Raises:
        HTTPException 404: If supplier not found
    """
    print(f"INFO [SupplierRoutes]: Getting products for supplier: {supplier_id}")

    # First verify supplier exists
    supplier = supplier_service.get_supplier(supplier_id)
    if not supplier:
        print(f"WARN [SupplierRoutes]: Supplier not found: {supplier_id}")
        raise HTTPException(status_code=404, detail="Supplier not found")

    # Get products for this supplier
    filters = ProductFilterDTO(supplier_id=supplier_id)
    result = product_service.list_products(filters=filters, page=page, limit=limit)

    print(
        f"INFO [SupplierRoutes]: Found {result.pagination.total} products for supplier"
    )
    return result


@router.put("/{supplier_id}/pipeline-status", response_model=SupplierResponseDTO)
async def update_pipeline_status(
    supplier_id: UUID,
    request: SupplierPipelineStatusUpdateDTO,
    current_user: dict = Depends(require_roles(["admin", "manager"])),
) -> SupplierResponseDTO:
    """Update supplier pipeline status (admin/manager only).

    Args:
        supplier_id: UUID of the supplier
        request: Pipeline status update data
        current_user: Authenticated admin/manager user (injected)

    Returns:
        Updated supplier

    Raises:
        HTTPException 404: If supplier not found
    """
    print(
        f"INFO [SupplierRoutes]: Updating pipeline status for {supplier_id} "
        f"to {request.pipeline_status.value}"
    )

    result = supplier_service.update_pipeline_status(
        supplier_id=supplier_id,
        pipeline_status=request.pipeline_status,
    )

    if not result:
        print(f"WARN [SupplierRoutes]: Supplier not found: {supplier_id}")
        raise HTTPException(status_code=404, detail="Supplier not found")

    print(f"INFO [SupplierRoutes]: Pipeline status updated successfully: {supplier_id}")
    return result


@router.get("/{supplier_id}/certification", response_model=SupplierCertificationSummaryDTO)
async def get_certification_summary(
    supplier_id: UUID,
    current_user: dict = Depends(get_current_user),
) -> SupplierCertificationSummaryDTO:
    """Get certification summary for a supplier including latest audit info.

    Args:
        supplier_id: UUID of the supplier
        current_user: Authenticated user (injected)

    Returns:
        Certification summary with audit details

    Raises:
        HTTPException 404: If supplier not found
    """
    print(f"INFO [SupplierRoutes]: Getting certification summary for: {supplier_id}")

    result = supplier_service.get_certification_summary(supplier_id)

    if not result:
        print(f"WARN [SupplierRoutes]: Supplier not found: {supplier_id}")
        raise HTTPException(status_code=404, detail="Supplier not found")

    print(f"INFO [SupplierRoutes]: Found certification summary for: {supplier_id}")
    return result
