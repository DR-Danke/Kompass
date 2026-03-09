"""API routes for AI-powered data extraction."""

import base64
import os
import tempfile
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException, Query, UploadFile

from app.api.rbac_dependencies import require_roles
from app.models.extraction_dto import (
    ExtractedProduct,
    HsCodeSuggestion,
    ImageProcessingResult,
)
from app.models.extraction_job_dto import (
    ConfirmImportRequestDTO,
    ConfirmImportResponseDTO,
    ExtractionJobDTO,
    ExtractionJobStatus,
    HsCodeSuggestRequestDTO,
    ImageProcessRequestDTO,
    UploadResponseDTO,
)
from app.models.kompass_dto import (
    BusinessCardCaptureListResponseDTO,
    BusinessCardCaptureResponseDTO,
    BusinessCardCaptureStatus,
    ProductCreateDTO,
    ProductStatus,
)
from app.services.business_card_service import business_card_service
from app.services.extraction_service import extraction_service
from app.services.product_service import product_service
from app.services.storage_service import storage_service


router = APIRouter(tags=["Extraction"])

# Allowed file extensions and max file size
ALLOWED_EXTENSIONS = {".pdf", ".xlsx", ".xls", ".docx", ".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20MB

# Business card upload constraints
BUSINESS_CARD_ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}
BUSINESS_CARD_MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB
BUSINESS_CARD_CONTENT_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}

# In-memory job store
_job_store: Dict[str, ExtractionJobDTO] = {}


def _create_job(total_files: int) -> ExtractionJobDTO:
    """Create a new extraction job.

    Args:
        total_files: Number of files to process

    Returns:
        New ExtractionJobDTO
    """
    now = datetime.utcnow()
    job = ExtractionJobDTO(
        job_id=uuid4(),
        status=ExtractionJobStatus.PENDING,
        progress=0,
        total_files=total_files,
        processed_files=0,
        extracted_products=[],
        errors=[],
        created_at=now,
        updated_at=now,
    )
    _job_store[str(job.job_id)] = job
    return job


def _get_job(job_id: str) -> Optional[ExtractionJobDTO]:
    """Get a job by ID.

    Args:
        job_id: Job UUID string

    Returns:
        ExtractionJobDTO if found, None otherwise
    """
    return _job_store.get(job_id)


def _update_job_progress(
    job_id: str,
    processed: int,
    products: List[ExtractedProduct],
    errors: List[str],
) -> None:
    """Update job progress.

    Args:
        job_id: Job UUID string
        processed: Number of files processed
        products: List of extracted products
        errors: List of errors
    """
    job = _job_store.get(job_id)
    if job:
        job.processed_files = processed
        job.extracted_products.extend(products)
        job.errors.extend(errors)
        job.progress = (
            int((processed / job.total_files) * 100) if job.total_files > 0 else 0
        )
        job.updated_at = datetime.utcnow()


def _complete_job(
    job_id: str,
    products: List[ExtractedProduct],
    errors: List[str],
) -> None:
    """Mark job as completed.

    Args:
        job_id: Job UUID string
        products: Final list of extracted products
        errors: Final list of errors
    """
    job = _job_store.get(job_id)
    if job:
        job.status = ExtractionJobStatus.COMPLETED
        job.progress = 100
        job.extracted_products = products
        job.errors = errors
        job.processed_files = job.total_files
        job.updated_at = datetime.utcnow()


def _fail_job(job_id: str, error: str) -> None:
    """Mark job as failed.

    Args:
        job_id: Job UUID string
        error: Error message
    """
    job = _job_store.get(job_id)
    if job:
        job.status = ExtractionJobStatus.FAILED
        job.errors.append(error)
        job.updated_at = datetime.utcnow()


def _validate_file(file: UploadFile) -> Optional[str]:
    """Validate uploaded file.

    Args:
        file: Uploaded file

    Returns:
        Error message if validation fails, None if valid
    """
    if not file.filename:
        return "File must have a filename"

    # Check extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return f"File type '{ext}' not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"

    return None


async def _process_files_background(
    job_id: str,
    file_paths: List[str],
) -> None:
    """Process files in the background.

    Args:
        job_id: Job UUID string
        file_paths: List of temporary file paths
    """
    job = _job_store.get(job_id)
    if not job:
        return

    # Update status to processing
    job.status = ExtractionJobStatus.PROCESSING
    job.updated_at = datetime.utcnow()

    try:
        # Process files using extraction service
        result = extraction_service.process_batch(file_paths)

        # Complete the job
        _complete_job(job_id, result.products, result.errors)

    except Exception as e:
        print(f"ERROR [ExtractionRoutes]: Background processing failed: {e}")
        _fail_job(job_id, f"Processing failed: {str(e)}")

    finally:
        # Clean up temp files
        for path in file_paths:
            try:
                if os.path.exists(path):
                    os.unlink(path)
            except OSError as e:
                print(f"WARN [ExtractionRoutes]: Failed to cleanup temp file {path}: {e}")


@router.post("/upload", response_model=UploadResponseDTO)
async def upload_files(
    files: List[UploadFile],
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(
        require_roles(["admin", "manager", "user"])
    ),
) -> UploadResponseDTO:
    """Upload files for extraction.

    Accepts multiple files (PDF, Excel, images) and creates an extraction job.
    Files are processed asynchronously in the background.

    Args:
        files: List of files to upload
        background_tasks: FastAPI background tasks
        current_user: Authenticated user

    Returns:
        UploadResponseDTO with job_id

    Raises:
        HTTPException 400: If no files provided or validation fails
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    print(f"INFO [ExtractionRoutes]: Upload request from user {current_user.get('email')}")

    # Validate all files first
    validation_errors = []
    for file in files:
        error = _validate_file(file)
        if error:
            validation_errors.append(f"{file.filename}: {error}")

    if validation_errors:
        raise HTTPException(
            status_code=400,
            detail=f"File validation failed: {'; '.join(validation_errors)}",
        )

    # Create job
    job = _create_job(len(files))
    print(f"INFO [ExtractionRoutes]: Created job {job.job_id} for {len(files)} files")

    # Save files to temp directory and collect paths
    file_paths: List[str] = []
    try:
        for file in files:
            # Check file size by reading content
            content = await file.read()
            if len(content) > MAX_FILE_SIZE_BYTES:
                _fail_job(
                    str(job.job_id),
                    f"File {file.filename} exceeds maximum size of 20MB",
                )
                raise HTTPException(
                    status_code=400,
                    detail=f"File {file.filename} exceeds maximum size of 20MB",
                )

            # Get extension and create temp file
            ext = os.path.splitext(file.filename or "")[1].lower()
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=ext, prefix="extraction_"
            ) as tmp:
                tmp.write(content)
                file_paths.append(tmp.name)

    except HTTPException:
        # Clean up any saved files
        for path in file_paths:
            try:
                if os.path.exists(path):
                    os.unlink(path)
            except OSError:
                pass
        raise

    # Schedule background processing
    background_tasks.add_task(_process_files_background, str(job.job_id), file_paths)

    return UploadResponseDTO(job_id=job.job_id)


# =============================================================================
# BUSINESS CARD CAPTURE GET ENDPOINTS (must precede /{job_id} catch-all)
# =============================================================================


@router.get("/business-cards", response_model=BusinessCardCaptureListResponseDTO)
async def list_business_cards(
    status: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    current_user: Dict[str, Any] = Depends(
        require_roles(["admin", "manager", "user", "viewer"])
    ),
) -> BusinessCardCaptureListResponseDTO:
    """List business card captures with optional status filter.

    Args:
        status: Optional status filter
        limit: Number of items to return
        offset: Number of items to skip
        current_user: Authenticated user

    Returns:
        BusinessCardCaptureListResponseDTO with captures and total count
    """
    captures, total = business_card_service.list_captures(
        status_filter=status,
        limit=limit,
        offset=offset,
    )

    items = [
        BusinessCardCaptureResponseDTO(
            id=c["id"],
            image_url=c["image_url"],
            status=BusinessCardCaptureStatus(c["status"]),
            company_name=c.get("company_name"),
            contact_name=c.get("contact_name"),
            contact_email=c.get("contact_email"),
            contact_phone=c.get("contact_phone"),
            contact_wechat=c.get("contact_wechat"),
            website=c.get("website"),
            address=c.get("address"),
            supplier_id=c.get("supplier_id"),
            fair_name=c.get("fair_name"),
            notes=c.get("notes"),
            captured_by=c.get("captured_by"),
            extraction_raw_response=c.get("extraction_raw_response"),
            created_at=c["created_at"],
            updated_at=c["updated_at"],
        )
        for c in captures
    ]

    return BusinessCardCaptureListResponseDTO(captures=items, total=total)


@router.get("/business-cards/{capture_id}", response_model=BusinessCardCaptureResponseDTO)
async def get_business_card(
    capture_id: UUID,
    current_user: Dict[str, Any] = Depends(
        require_roles(["admin", "manager", "user", "viewer"])
    ),
) -> BusinessCardCaptureResponseDTO:
    """Get a single business card capture by ID.

    Args:
        capture_id: UUID of the capture
        current_user: Authenticated user

    Returns:
        BusinessCardCaptureResponseDTO

    Raises:
        HTTPException 404: If capture not found
    """
    try:
        capture = business_card_service.get_capture(capture_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Business card capture not found")

    return BusinessCardCaptureResponseDTO(
        id=capture["id"],
        image_url=capture["image_url"],
        status=BusinessCardCaptureStatus(capture["status"]),
        company_name=capture.get("company_name"),
        contact_name=capture.get("contact_name"),
        contact_email=capture.get("contact_email"),
        contact_phone=capture.get("contact_phone"),
        contact_wechat=capture.get("contact_wechat"),
        website=capture.get("website"),
        address=capture.get("address"),
        supplier_id=capture.get("supplier_id"),
        fair_name=capture.get("fair_name"),
        notes=capture.get("notes"),
        captured_by=capture.get("captured_by"),
        extraction_raw_response=capture.get("extraction_raw_response"),
        created_at=capture["created_at"],
        updated_at=capture["updated_at"],
    )


@router.get("/{job_id}", response_model=ExtractionJobDTO)
async def get_job_status(
    job_id: UUID,
    current_user: Dict[str, Any] = Depends(
        require_roles(["admin", "manager", "user"])
    ),
) -> ExtractionJobDTO:
    """Get extraction job status.

    Args:
        job_id: Job UUID
        current_user: Authenticated user

    Returns:
        ExtractionJobDTO with current status

    Raises:
        HTTPException 404: If job not found
    """
    job = _get_job(str(job_id))
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


@router.get("/{job_id}/results", response_model=ExtractionJobDTO)
async def get_job_results(
    job_id: UUID,
    current_user: Dict[str, Any] = Depends(
        require_roles(["admin", "manager", "user"])
    ),
) -> ExtractionJobDTO:
    """Get extraction job results.

    Only returns results for completed jobs.

    Args:
        job_id: Job UUID
        current_user: Authenticated user

    Returns:
        ExtractionJobDTO with extracted products

    Raises:
        HTTPException 400: If job not completed
        HTTPException 404: If job not found
    """
    job = _get_job(str(job_id))
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != ExtractionJobStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Job is not completed. Current status: {job.status.value}",
        )

    return job


@router.post("/{job_id}/confirm", response_model=ConfirmImportResponseDTO)
async def confirm_import(
    job_id: UUID,
    request: ConfirmImportRequestDTO,
    current_user: Dict[str, Any] = Depends(
        require_roles(["admin", "manager", "user"])
    ),
) -> ConfirmImportResponseDTO:
    """Confirm and import extracted products.

    Imports selected products (or all if none specified) into the product database.

    Args:
        job_id: Job UUID
        request: ConfirmImportRequestDTO with supplier_id and optional product_indices
        current_user: Authenticated user

    Returns:
        ConfirmImportResponseDTO with import counts and errors

    Raises:
        HTTPException 400: If job not completed or request invalid
        HTTPException 404: If job not found
    """
    job = _get_job(str(job_id))
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != ExtractionJobStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Job is not completed. Current status: {job.status.value}",
        )

    # Validate job_id in request matches path
    if request.job_id != job_id:
        raise HTTPException(
            status_code=400,
            detail="Job ID in request body does not match path parameter",
        )

    products = job.extracted_products

    # Filter products if indices specified
    if request.product_indices is not None:
        selected_products = []
        for idx in request.product_indices:
            if 0 <= idx < len(products):
                selected_products.append(products[idx])
            else:
                return ConfirmImportResponseDTO(
                    imported_count=0,
                    failed_count=0,
                    errors=[f"Invalid product index: {idx}"],
                )
        products = selected_products

    if not products:
        return ConfirmImportResponseDTO(
            imported_count=0,
            failed_count=0,
            errors=["No products to import"],
        )

    print(
        f"INFO [ExtractionRoutes]: Importing {len(products)} products "
        f"for user {current_user.get('email')}"
    )

    # Convert ExtractedProduct to ProductCreateDTO
    product_create_dtos: List[ProductCreateDTO] = []
    for extracted in products:
        # Build description, appending material if present
        description = extracted.description
        if extracted.material:
            material_suffix = f"\nMaterial: {extracted.material}"
            description = (description or "") + material_suffix

        product_dto = ProductCreateDTO(
            sku=extracted.sku,
            name=extracted.name or "Unnamed Product",
            description=description,
            supplier_id=request.supplier_id,
            category_id=request.category_id,
            status=ProductStatus.DRAFT,
            unit_cost=extracted.price_fob_usd or 0,
            unit_price=extracted.price_fob_usd or 0,
            unit_of_measure=extracted.unit_of_measure or "piece",
            minimum_order_qty=extracted.moq or 1,
            dimensions=extracted.dimensions,
        )
        product_create_dtos.append(product_dto)

    # Bulk create products
    result = product_service.bulk_create_products(product_create_dtos)

    return ConfirmImportResponseDTO(
        imported_count=result.success_count,
        failed_count=result.failure_count,
        errors=[error.error for error in result.failed],
    )


@router.post("/image/process", response_model=ImageProcessingResult)
async def process_image(
    request: ImageProcessRequestDTO,
    current_user: Dict[str, Any] = Depends(
        require_roles(["admin", "manager", "user"])
    ),
) -> ImageProcessingResult:
    """Process an image (remove background).

    Args:
        request: ImageProcessRequestDTO with image_url
        current_user: Authenticated user

    Returns:
        ImageProcessingResult with processed image URL
    """
    print(
        f"INFO [ExtractionRoutes]: Image process request from user {current_user.get('email')}"
    )

    result = extraction_service.remove_background(request.image_url)
    return result


@router.post("/hs-code/suggest", response_model=HsCodeSuggestion)
async def suggest_hs_code(
    request: HsCodeSuggestRequestDTO,
    current_user: Dict[str, Any] = Depends(
        require_roles(["admin", "manager", "user"])
    ),
) -> HsCodeSuggestion:
    """Suggest an HS code for a product description.

    Args:
        request: HsCodeSuggestRequestDTO with description
        current_user: Authenticated user

    Returns:
        HsCodeSuggestion with suggested code and confidence

    Raises:
        HTTPException 400: If description is empty
    """
    if not request.description.strip():
        raise HTTPException(status_code=400, detail="Description cannot be empty")

    print(
        f"INFO [ExtractionRoutes]: HS code suggestion request from user {current_user.get('email')}"
    )

    result = extraction_service.suggest_hs_code(request.description)
    return result


@router.post("/business-card", response_model=BusinessCardCaptureResponseDTO, status_code=201)
async def upload_business_card(
    file: UploadFile,
    fair_name: Optional[str] = Form(default=None),
    notes: Optional[str] = Form(default=None),
    current_user: Dict[str, Any] = Depends(
        require_roles(["admin", "manager", "user"])
    ),
) -> BusinessCardCaptureResponseDTO:
    """Upload a business card image for later AI extraction.

    Args:
        file: Image file (.png, .jpg, .jpeg, max 10MB)
        fair_name: Optional trade fair name
        notes: Optional notes
        current_user: Authenticated user

    Returns:
        BusinessCardCaptureResponseDTO with created capture record

    Raises:
        HTTPException 400: If file validation fails
        HTTPException 500: If upload or record creation fails
    """
    print(
        f"INFO [ExtractionRoutes]: Business card upload from user {current_user.get('email')}"
    )

    # Validate filename
    if not file.filename:
        raise HTTPException(status_code=400, detail="File must have a filename")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in BUSINESS_CARD_ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not allowed. Allowed types: .png, .jpg, .jpeg",
        )

    # Read and validate size
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="File is empty")

    if len(content) > BUSINESS_CARD_MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail="File exceeds maximum size of 10MB",
        )

    # Upload to Supabase Storage or fallback to base64
    if storage_service.is_configured():
        try:
            content_type = BUSINESS_CARD_CONTENT_TYPES.get(ext, "image/jpeg")
            image_url = storage_service.upload_file(
                file_content=content,
                file_name=file.filename,
                content_type=content_type,
                folder="business-cards",
            )
            print(f"INFO [ExtractionRoutes]: Business card uploaded to storage: {image_url}")
        except Exception as e:
            print(f"ERROR [ExtractionRoutes]: Storage upload failed: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to upload file to storage",
            )
    else:
        # Fallback to base64 data URL for development
        print("WARN [ExtractionRoutes]: Storage not configured, using base64 data URL")
        content_type = BUSINESS_CARD_CONTENT_TYPES.get(ext, "image/jpeg")
        b64_data = base64.b64encode(content).decode("utf-8")
        image_url = f"data:{content_type};base64,{b64_data}"

    # Create capture record
    try:
        capture = business_card_service.create_capture(
            image_url=image_url,
            fair_name=fair_name,
            notes=notes,
            captured_by=current_user.get("id"),
        )

        return BusinessCardCaptureResponseDTO(
            id=capture["id"],
            image_url=capture["image_url"],
            status=BusinessCardCaptureStatus(capture["status"]),
            company_name=capture.get("company_name"),
            contact_name=capture.get("contact_name"),
            contact_email=capture.get("contact_email"),
            contact_phone=capture.get("contact_phone"),
            contact_wechat=capture.get("contact_wechat"),
            website=capture.get("website"),
            address=capture.get("address"),
            supplier_id=capture.get("supplier_id"),
            fair_name=capture.get("fair_name"),
            notes=capture.get("notes"),
            captured_by=capture.get("captured_by"),
            extraction_raw_response=capture.get("extraction_raw_response"),
            created_at=capture["created_at"],
            updated_at=capture["updated_at"],
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"ERROR [ExtractionRoutes]: Failed to create capture: {e}")
        raise HTTPException(status_code=500, detail="Failed to create capture record")
