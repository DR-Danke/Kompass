"""API routes for supplier audit operations."""

import os
import tempfile
from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
    UploadFile,
)
from fastapi.responses import RedirectResponse, Response

from app.api.rbac_dependencies import require_roles
from app.models.kompass_dto import (
    AuditType,
    SupplierAuditClassificationDTO,
    SupplierAuditListResponseDTO,
    SupplierAuditResponseDTO,
)
from app.services.audit_service import audit_service
from app.services.auth_service import auth_service
from app.services.storage_service import storage_service


router = APIRouter(tags=["Supplier Audits"])

# File constraints
MAX_AUDIT_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25MB
ALLOWED_EXTENSIONS = {".pdf"}


def _validate_audit_file(file: UploadFile) -> str:
    """Validate uploaded audit file.

    Args:
        file: Uploaded file

    Returns:
        Error message if validation fails, empty string if valid
    """
    if not file.filename:
        return "File must have a filename"

    # Check extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return f"File type '{ext}' not allowed. Only PDF files are supported."

    return ""


async def _process_audit_background(audit_id: UUID) -> None:
    """Process audit extraction in the background.

    Args:
        audit_id: UUID of the audit to process
    """
    try:
        audit_service.process_audit(audit_id)
    except Exception as e:
        print(f"ERROR [AuditRoutes]: Background processing failed for {audit_id}: {e}")


@router.post(
    "/{supplier_id}/audits",
    response_model=SupplierAuditResponseDTO,
    status_code=201,
)
async def upload_audit(
    supplier_id: UUID,
    file: UploadFile,
    background_tasks: BackgroundTasks,
    audit_type: AuditType = Query(default=AuditType.FACTORY_AUDIT),
    current_user: Dict[str, Any] = Depends(
        require_roles(["admin", "manager", "user"])
    ),
) -> SupplierAuditResponseDTO:
    """Upload a PDF audit document for a supplier.

    The document is uploaded and an audit record is created with 'pending' status.
    AI extraction runs in the background and updates the record when complete.

    Args:
        supplier_id: UUID of the supplier
        file: PDF file to upload
        background_tasks: FastAPI background tasks
        audit_type: Type of audit (factory_audit or container_inspection)
        current_user: Authenticated user

    Returns:
        SupplierAuditResponseDTO with created audit record

    Raises:
        HTTPException 400: If file validation fails
        HTTPException 500: If audit creation fails
    """
    print(
        f"INFO [AuditRoutes]: Upload request from user {current_user.get('email')} "
        f"for supplier {supplier_id}"
    )

    # Validate file
    error = _validate_audit_file(file)
    if error:
        raise HTTPException(status_code=400, detail=error)

    # Read file content and check size
    content = await file.read()
    if len(content) > MAX_AUDIT_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum size of {MAX_AUDIT_FILE_SIZE_BYTES // (1024*1024)}MB",
        )

    # Upload to Supabase Storage (production) or fallback to local file (development)
    temp_path = None
    if storage_service.is_configured():
        # Upload to Supabase Storage - returns HTTPS URL
        try:
            document_url = storage_service.upload_file(
                file_content=content,
                file_name=file.filename or "audit.pdf",
                content_type="application/pdf",
                folder=f"suppliers/{supplier_id}/audits",
            )
            print(f"INFO [AuditRoutes]: File uploaded to Supabase Storage: {document_url}")
        except Exception as e:
            print(f"ERROR [AuditRoutes]: Supabase Storage upload failed: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to upload file to storage",
            )
    else:
        # Fallback to local file for development
        print("WARN [AuditRoutes]: Supabase Storage not configured, using local file storage")
        ext = os.path.splitext(file.filename or "")[1].lower()
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=ext, prefix="audit_"
        ) as tmp:
            tmp.write(content)
            temp_path = tmp.name
        document_url = f"file://{temp_path}"

    try:
        # Create audit record
        audit = audit_service.upload_audit(
            supplier_id=supplier_id,
            document_url=document_url,
            document_name=file.filename or "audit.pdf",
            file_size_bytes=len(content),
            audit_type=audit_type,
        )

        # Schedule background processing
        background_tasks.add_task(_process_audit_background, audit.id)

        print(f"INFO [AuditRoutes]: Created audit {audit.id} for supplier {supplier_id}")
        return audit

    except ValueError as e:
        # Clean up temp file on error (only if using local storage)
        if temp_path:
            try:
                os.unlink(temp_path)
            except OSError:
                pass
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Clean up temp file on error (only if using local storage)
        if temp_path:
            try:
                os.unlink(temp_path)
            except OSError:
                pass
        print(f"ERROR [AuditRoutes]: Failed to create audit: {e}")
        raise HTTPException(status_code=500, detail="Failed to create audit record")


@router.get(
    "/{supplier_id}/audits",
    response_model=SupplierAuditListResponseDTO,
)
async def list_supplier_audits(
    supplier_id: UUID,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(
        require_roles(["admin", "manager", "user", "viewer"])
    ),
) -> SupplierAuditListResponseDTO:
    """List all audits for a supplier with pagination.

    Args:
        supplier_id: UUID of the supplier
        page: Page number (1-indexed)
        limit: Number of items per page
        current_user: Authenticated user

    Returns:
        SupplierAuditListResponseDTO with paginated results
    """
    return audit_service.get_supplier_audits(
        supplier_id=supplier_id,
        page=page,
        limit=limit,
    )


@router.get(
    "/{supplier_id}/audits/{audit_id}",
    response_model=SupplierAuditResponseDTO,
)
async def get_audit(
    supplier_id: UUID,
    audit_id: UUID,
    current_user: Dict[str, Any] = Depends(
        require_roles(["admin", "manager", "user", "viewer"])
    ),
) -> SupplierAuditResponseDTO:
    """Get a single audit by ID.

    Args:
        supplier_id: UUID of the supplier
        audit_id: UUID of the audit
        current_user: Authenticated user

    Returns:
        SupplierAuditResponseDTO

    Raises:
        HTTPException 404: If audit not found
        HTTPException 400: If audit doesn't belong to supplier
    """
    audit = audit_service.get_audit(audit_id)

    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    if audit.supplier_id != supplier_id:
        raise HTTPException(
            status_code=400,
            detail="Audit does not belong to this supplier",
        )

    return audit


@router.get(
    "/{supplier_id}/audits/{audit_id}/download",
)
async def download_audit_pdf(
    supplier_id: UUID,
    audit_id: UUID,
    token: Optional[str] = Query(default=None),
):
    """Download or view the audit PDF document.

    For local file:// URLs, reads and serves the file content.
    For HTTPS URLs (Supabase Storage), redirects to the URL.

    Authentication is via query parameter token (since browsers can't send
    Authorization headers when opening URLs in new tabs).

    Args:
        supplier_id: UUID of the supplier
        audit_id: UUID of the audit
        token: JWT token for authentication (passed as query parameter)

    Returns:
        PDF file content or redirect to storage URL

    Raises:
        HTTPException 401: If not authenticated or token invalid
        HTTPException 404: If audit not found or file not found
        HTTPException 400: If audit doesn't belong to supplier
    """
    # Validate token from query parameter
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = auth_service.decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Verify audit exists and belongs to supplier
    audit = audit_service.get_audit(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    if audit.supplier_id != supplier_id:
        raise HTTPException(
            status_code=400,
            detail="Audit does not belong to this supplier",
        )

    document_url = audit.document_url
    if not document_url:
        raise HTTPException(status_code=404, detail="No document URL for this audit")

    # Handle local file:// URLs
    if document_url.startswith("file://"):
        local_path = document_url[7:]  # Remove "file://" prefix
        if not os.path.exists(local_path):
            raise HTTPException(
                status_code=404,
                detail="PDF file not found. It may have been deleted after server restart.",
            )

        try:
            with open(local_path, "rb") as f:
                content = f.read()

            return Response(
                content=content,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f'inline; filename="{audit.document_name or "audit.pdf"}"',
                },
            )
        except PermissionError:
            raise HTTPException(status_code=500, detail="Permission denied reading file")
        except Exception as e:
            print(f"ERROR [AuditRoutes]: Failed to read PDF file: {e}")
            raise HTTPException(status_code=500, detail="Failed to read PDF file")

    # Handle HTTPS URLs (Supabase Storage) - redirect to the URL
    if document_url.startswith("https://"):
        return RedirectResponse(url=document_url, status_code=302)

    # Unknown URL scheme
    raise HTTPException(status_code=400, detail="Unsupported document URL scheme")


@router.post(
    "/{supplier_id}/audits/{audit_id}/reprocess",
    response_model=SupplierAuditResponseDTO,
)
async def reprocess_audit(
    supplier_id: UUID,
    audit_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(
        require_roles(["admin", "manager"])
    ),
) -> SupplierAuditResponseDTO:
    """Reprocess an audit to re-run AI extraction.

    This resets the extraction fields and schedules a new extraction.

    Args:
        supplier_id: UUID of the supplier
        audit_id: UUID of the audit
        background_tasks: FastAPI background tasks
        current_user: Authenticated user

    Returns:
        SupplierAuditResponseDTO with reset status

    Raises:
        HTTPException 404: If audit not found
        HTTPException 400: If audit doesn't belong to supplier
    """
    print(
        f"INFO [AuditRoutes]: Reprocess request from user {current_user.get('email')} "
        f"for audit {audit_id}"
    )

    # Verify audit exists and belongs to supplier
    existing_audit = audit_service.get_audit(audit_id)
    if not existing_audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    if existing_audit.supplier_id != supplier_id:
        raise HTTPException(
            status_code=400,
            detail="Audit does not belong to this supplier",
        )

    try:
        # Reset extraction fields first
        from app.repository.audit_repository import audit_repository
        reset_audit = audit_repository.reset_extraction(audit_id)
        if not reset_audit:
            raise HTTPException(status_code=500, detail="Failed to reset audit")

        # Schedule background reprocessing
        background_tasks.add_task(_process_audit_background, audit_id)

        # Return the reset audit (with pending status)
        audit = audit_service.get_audit(audit_id)
        if not audit:
            raise HTTPException(status_code=500, detail="Failed to get audit after reset")

        return audit

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/{supplier_id}/audits/{audit_id}",
    status_code=204,
)
async def delete_audit(
    supplier_id: UUID,
    audit_id: UUID,
    current_user: Dict[str, Any] = Depends(
        require_roles(["admin", "manager"])
    ),
) -> None:
    """Delete an audit document.

    Args:
        supplier_id: UUID of the supplier
        audit_id: UUID of the audit
        current_user: Authenticated user

    Raises:
        HTTPException 404: If audit not found
        HTTPException 400: If audit doesn't belong to supplier
    """
    print(
        f"INFO [AuditRoutes]: Delete request from user {current_user.get('email')} "
        f"for audit {audit_id}"
    )

    # Verify audit exists and belongs to supplier
    existing_audit = audit_service.get_audit(audit_id)
    if not existing_audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    if existing_audit.supplier_id != supplier_id:
        raise HTTPException(
            status_code=400,
            detail="Audit does not belong to this supplier",
        )

    success = audit_service.delete_audit(audit_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete audit")


@router.post(
    "/{supplier_id}/audits/{audit_id}/classify",
    response_model=SupplierAuditResponseDTO,
)
async def classify_audit(
    supplier_id: UUID,
    audit_id: UUID,
    current_user: Dict[str, Any] = Depends(
        require_roles(["admin", "manager", "user"])
    ),
) -> SupplierAuditResponseDTO:
    """Classify a supplier based on extracted audit data.

    Analyzes extracted audit data and generates an A/B/C classification
    with human-readable reasoning. Also updates the supplier's
    certification_status.

    Args:
        supplier_id: UUID of the supplier
        audit_id: UUID of the audit
        current_user: Authenticated user

    Returns:
        SupplierAuditResponseDTO with classification data

    Raises:
        HTTPException 404: If audit not found
        HTTPException 400: If audit doesn't belong to supplier or extraction not completed
    """
    print(
        f"INFO [AuditRoutes]: Classify request from user {current_user.get('email')} "
        f"for audit {audit_id}"
    )

    # Verify audit exists and belongs to supplier
    existing_audit = audit_service.get_audit(audit_id)
    if not existing_audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    if existing_audit.supplier_id != supplier_id:
        raise HTTPException(
            status_code=400,
            detail="Audit does not belong to this supplier",
        )

    try:
        return audit_service.classify_supplier(audit_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put(
    "/{supplier_id}/audits/{audit_id}/classification",
    response_model=SupplierAuditResponseDTO,
)
async def override_classification(
    supplier_id: UUID,
    audit_id: UUID,
    classification_data: SupplierAuditClassificationDTO,
    current_user: Dict[str, Any] = Depends(
        require_roles(["admin", "manager"])
    ),
) -> SupplierAuditResponseDTO:
    """Override the AI classification with a manual classification.

    Allows admin/manager users to override the AI-generated classification
    with a manual classification. Notes are required to document the
    reasoning for the override.

    Args:
        supplier_id: UUID of the supplier
        audit_id: UUID of the audit
        classification_data: Classification grade (A/B/C) and required notes
        current_user: Authenticated user

    Returns:
        SupplierAuditResponseDTO with updated classification

    Raises:
        HTTPException 404: If audit not found
        HTTPException 400: If validation fails or audit doesn't belong to supplier
    """
    print(
        f"INFO [AuditRoutes]: Override classification request from user "
        f"{current_user.get('email')} for audit {audit_id}: {classification_data.classification}"
    )

    # Verify audit exists and belongs to supplier
    existing_audit = audit_service.get_audit(audit_id)
    if not existing_audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    if existing_audit.supplier_id != supplier_id:
        raise HTTPException(
            status_code=400,
            detail="Audit does not belong to this supplier",
        )

    # Notes are required for overrides
    if not classification_data.notes or not classification_data.notes.strip():
        raise HTTPException(
            status_code=400,
            detail="Notes are required when overriding classification",
        )

    try:
        return audit_service.override_classification(
            audit_id=audit_id,
            classification=classification_data.classification,
            notes=classification_data.notes,
            user_id=current_user.get("id"),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
