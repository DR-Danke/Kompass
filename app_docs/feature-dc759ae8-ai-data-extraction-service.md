# AI Data Extraction Service

**ADW ID:** dc759ae8
**Date:** 2026-01-31
**Specification:** specs/issue-5-adw-dc759ae8-sdlc_planner-ai-data-extraction-service.md

## Overview

AI-powered data extraction service for automatically extracting product information from supplier catalogs in various formats (PDF, Excel, images). The service leverages Claude or OpenAI Vision APIs to intelligently parse product data and provides image processing capabilities and HS code suggestions for tariff classification.

## What Was Built

- **ExtractionService** - Core service class with AI client management and extraction logic
- **PDF Processing** - Extract product data from PDF catalogs using PyPDF2
- **Excel Processing** - Parse Excel spreadsheets with flexible column mapping
- **Image Processing** - Extract product data from images using AI vision capabilities
- **HS Code Suggestion** - AI-powered Harmonized System code classification
- **Background Removal** - Image processing via RemoveBG API integration
- **Image Resizing** - Pillow-based image manipulation utilities
- **Batch Processing** - Process multiple files with aggregated results and error tracking
- **Graceful Fallbacks** - Degraded operation when AI services are unavailable

## Technical Implementation

### Files Modified

- `apps/Server/app/config/settings.py`: Added AI API key settings (ANTHROPIC_API_KEY, OPENAI_API_KEY, REMOVEBG_API_KEY) and extraction configuration
- `apps/Server/app/models/extraction_dto.py`: Created DTOs for extracted products, results, HS codes, and image processing
- `apps/Server/app/services/extraction_service.py`: Main extraction service with all AI-powered functionality (726 lines)
- `apps/Server/requirements.txt`: Added dependencies (anthropic, openai, pypdf2, openpyxl, pillow)
- `apps/Server/tests/test_extraction_service.py`: Comprehensive unit tests with mocked AI responses

### Key Changes

- **Dual AI Provider Support**: Service supports both Anthropic Claude and OpenAI APIs with automatic fallback
- **Lazy Client Initialization**: AI clients are initialized only when needed to conserve resources
- **File Size Limits**: Enforces limits (PDF: 50MB, Image: 10MB, Excel: 20MB) to prevent memory issues
- **Confidence Scoring**: Calculates extraction confidence based on number of fields successfully extracted
- **Flexible Column Mapping**: Excel parser detects columns by common header name variations (SKU/Reference/Code, Name/Product/Item, etc.)

### Data Transfer Objects

```python
# ExtractedProduct - Product data extracted from documents
class ExtractedProduct(BaseModel):
    sku: Optional[str]
    name: Optional[str]
    description: Optional[str]
    price_fob_usd: Optional[Decimal]
    moq: Optional[int]
    dimensions: Optional[str]
    material: Optional[str]
    suggested_category: Optional[str]
    image_urls: List[str]
    confidence_score: float  # 0.0 to 1.0
    raw_text: Optional[str]
    source_page: Optional[int]

# ExtractionResult - Aggregated batch processing result
class ExtractionResult(BaseModel):
    products: List[ExtractedProduct]
    total_extracted: int
    errors: List[str]
    warnings: List[str]
    processing_time_seconds: float

# HsCodeSuggestion - HS code classification result
class HsCodeSuggestion(BaseModel):
    code: str  # Format: XXXX.XX.XX
    description: str
    confidence_score: float
    reasoning: Optional[str]

# ImageProcessingResult - Image operation result
class ImageProcessingResult(BaseModel):
    original_url: str
    processed_url: str
    operation: ImageOperation  # "remove_bg" or "resize"
```

## How to Use

1. **Import the service singleton**:
   ```python
   from app.services.extraction_service import extraction_service
   ```

2. **Process a single PDF**:
   ```python
   products, errors = extraction_service.process_pdf("/path/to/catalog.pdf")
   ```

3. **Process an Excel file**:
   ```python
   products, errors = extraction_service.process_excel("/path/to/pricelist.xlsx")
   ```

4. **Process a single image**:
   ```python
   product, errors = extraction_service.process_image("/path/to/product.jpg")
   ```

5. **Batch process multiple files**:
   ```python
   result = extraction_service.process_batch([
       "/path/to/catalog.pdf",
       "/path/to/pricelist.xlsx",
       "/path/to/product.png"
   ])
   print(f"Extracted {result.total_extracted} products")
   ```

6. **Get HS code suggestion**:
   ```python
   suggestion = extraction_service.suggest_hs_code("Ceramic coffee mug with handle")
   print(f"HS Code: {suggestion.code} ({suggestion.confidence_score:.0%} confidence)")
   ```

7. **Remove image background**:
   ```python
   result = extraction_service.remove_background("https://example.com/product.jpg")
   # result.processed_url contains data URI or original URL if API unavailable
   ```

8. **Resize an image**:
   ```python
   data_uri, error = extraction_service.resize_image("/path/to/image.jpg", 800, 600)
   ```

## Configuration

### Environment Variables

```bash
# AI Provider API Keys (at least one required for AI features)
ANTHROPIC_API_KEY=sk-ant-...       # Claude API key
OPENAI_API_KEY=sk-...              # OpenAI API key (fallback)

# Image Processing
REMOVEBG_API_KEY=...               # RemoveBG API key (optional)

# Extraction Settings
EXTRACTION_AI_PROVIDER=anthropic   # "anthropic" or "openai"
EXTRACTION_MAX_RETRIES=3           # API retry attempts
EXTRACTION_TIMEOUT_SECONDS=60      # API timeout
```

### AI Provider Selection

The service uses a priority-based provider selection:
1. Uses configured `EXTRACTION_AI_PROVIDER` if API key is available
2. Falls back to the other provider if primary is unavailable
3. Returns degraded results (empty/partial extraction) if no AI is available

## Testing

Run the extraction service tests:

```bash
cd apps/Server
source .venv/bin/activate
pytest tests/test_extraction_service.py -v --tb=short
```

Tests cover:
- PDF processing with mocked PyPDF2
- Excel parsing with various column formats
- AI extraction with mocked Claude/OpenAI responses
- HS code suggestion with mocked AI
- Batch processing with mixed file types
- Graceful fallback when AI unavailable
- Error handling for invalid files

## Notes

- **No API Keys Required**: Service works in degraded mode without AI keys, returning raw text extraction
- **RemoveBG Free Tier**: Limited to 50 API calls/month; consider local fallback for high volume
- **Claude Vision Preferred**: Service prefers Claude's vision capabilities over OpenAI for consistency
- **Backend Only**: This is a backend service with no frontend integration (to be added in later phases)
- **Part of Phase 2D**: Runs in parallel with KP-002, KP-003, and KP-004 backend services
