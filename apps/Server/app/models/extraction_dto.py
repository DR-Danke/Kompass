"""AI Data Extraction Service Data Transfer Objects (DTOs)."""

from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class ImageOperation(str, Enum):
    """Supported image processing operations."""

    REMOVE_BG = "remove_bg"
    RESIZE = "resize"


class ExtractedProduct(BaseModel):
    """DTO for a product extracted from a document or image."""

    sku: Optional[str] = Field(default=None, max_length=100)
    name: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = None
    price_fob_usd: Optional[Decimal] = Field(default=None, ge=0)
    moq: Optional[int] = Field(default=None, ge=1)
    dimensions: Optional[str] = Field(default=None, max_length=100)
    material: Optional[str] = Field(default=None, max_length=200)
    suggested_category: Optional[str] = Field(default=None, max_length=200)
    image_urls: List[str] = Field(default_factory=list)
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    raw_text: Optional[str] = None
    source_page: Optional[int] = Field(default=None, ge=1)


class ExtractionResult(BaseModel):
    """DTO for the result of an extraction operation."""

    products: List[ExtractedProduct] = Field(default_factory=list)
    total_extracted: int = Field(default=0, ge=0)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    processing_time_seconds: float = Field(default=0.0, ge=0.0)


class HsCodeSuggestion(BaseModel):
    """DTO for an HS code suggestion."""

    code: str = Field(min_length=1, max_length=20)
    description: str = Field(min_length=1)
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    reasoning: Optional[str] = None


class ImageProcessingResult(BaseModel):
    """DTO for the result of an image processing operation."""

    original_url: str
    processed_url: str
    operation: ImageOperation
