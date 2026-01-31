"""API routes for AI-powered data extraction."""

import os
import tempfile
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile

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
from app.models.kompass_dto import ProductCreateDTO, ProductStatus
from app.services.extraction_service import extraction_service
from app.services.product_service import product_service


router = APIRouter(tags=["Extraction"])

# Allowed file extensions and max file size
ALLOWED_EXTENSIONS = {".pdf", ".xlsx", ".xls", ".docx", ".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20MB

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
        product_dto = ProductCreateDTO(
            sku=extracted.sku,
            name=extracted.name or "Unnamed Product",
            description=extracted.description,
            supplier_id=request.supplier_id,
            status=ProductStatus.DRAFT,
            unit_cost=extracted.price_fob_usd or 0,
            unit_price=extracted.price_fob_usd or 0,
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
