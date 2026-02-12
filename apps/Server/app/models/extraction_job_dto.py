"""Data Transfer Objects for extraction job management."""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.extraction_dto import ExtractedProduct


class ExtractionJobStatus(str, Enum):
    """Status values for extraction jobs."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ExtractionJobDTO(BaseModel):
    """DTO representing an extraction job."""

    job_id: UUID
    status: ExtractionJobStatus
    progress: int = Field(default=0, ge=0, le=100)
    total_files: int = Field(default=0, ge=0)
    processed_files: int = Field(default=0, ge=0)
    extracted_products: List[ExtractedProduct] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class UploadResponseDTO(BaseModel):
    """Response DTO for file upload."""

    job_id: UUID


class ConfirmImportRequestDTO(BaseModel):
    """Request DTO for confirming and importing extracted products."""

    job_id: UUID
    product_indices: Optional[List[int]] = Field(
        default=None,
        description="Indices of products to import. If None, import all.",
    )
    supplier_id: UUID = Field(description="Supplier ID to assign to imported products")
    category_id: Optional[UUID] = None


class ConfirmImportResponseDTO(BaseModel):
    """Response DTO for confirm import operation."""

    imported_count: int = Field(default=0, ge=0)
    failed_count: int = Field(default=0, ge=0)
    errors: List[str] = Field(default_factory=list)


class HsCodeSuggestRequestDTO(BaseModel):
    """Request DTO for HS code suggestion."""

    description: str = Field(min_length=1, max_length=5000)


class ImageProcessRequestDTO(BaseModel):
    """Request DTO for image processing (background removal)."""

    image_url: str = Field(min_length=1, max_length=2000)
