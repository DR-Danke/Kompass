# PDF Generation Service

**ADW ID:** 5d18ddf7
**Date:** 2026-02-01
**Specification:** specs/issue-31-adw-5d18ddf7-pdf-generation-service.md

## Overview

A dedicated PDF generation service that provides professional-grade PDF documents for portfolios and quotations with enhanced features including cover pages, Kompass branding, QR codes linking to digital versions, product tables, pricing breakdowns, and page numbers on all pages.

## What Was Built

- Centralized `pdf_service.py` module with two generator classes
- `PortfolioPDFGenerator` - Generates portfolio PDFs with cover page, product listing, and QR code
- `QuotationPDFGenerator` - Generates proforma invoice PDFs with header, items table, pricing breakdown, and terms
- QR code generation utility using the `qrcode` library
- Consistent branding and styling across all PDF documents
- Refactored `portfolio_service.py` and `quotation_service.py` to use the new service

## Technical Implementation

### Files Modified

- `apps/Server/app/services/pdf_service.py`: New dedicated PDF generation module (868 lines)
- `apps/Server/app/services/portfolio_service.py`: Refactored to use `pdf_service`, removed 145 lines of PDF logic
- `apps/Server/app/services/quotation_service.py`: Refactored to use `pdf_service`, removed 215 lines of PDF logic
- `apps/Server/requirements.txt`: Added `qrcode[pil]>=7.4.0` dependency
- `apps/Server/tests/services/test_pdf_service.py`: New unit tests (559 lines)

### Key Changes

- **Centralized PDF generation**: All PDF logic moved to `pdf_service.py` with dedicated generator classes
- **Branding constants**: Consistent colors (Material Design blue `#1976d2`), fonts (Helvetica), and margins
- **Portfolio PDFs now include**:
  - Cover page with Kompass branding, portfolio name, niche, and description
  - Product count indicator
  - QR code linking to share URL (generated automatically)
  - Product table with alternating row colors
  - Page numbers on all pages
  - Company name in header (after cover page)
- **Quotation PDFs (Proforma Invoice) now include**:
  - Professional header with "PROFORMA INVOICE" title
  - Quotation metadata (number, status, incoterm, validity dates)
  - Client billing information section
  - Line items table with product, quantity, unit, unit price, and total
  - Pricing breakdown (subtotal, freight, insurance, other costs, discount, grand total)
  - Payment terms, terms & conditions, and notes sections
  - Footer with generation timestamp and item count
  - Page numbers on all pages

### Architecture

```
pdf_service.py
├── Constants (colors, fonts, margins, branding)
├── Utility Functions
│   ├── create_qr_code(url, size) -> BytesIO
│   ├── create_styles() -> Dict[str, ParagraphStyle]
│   ├── _truncate_text(text, max_length) -> str
│   └── _safe_get(data, key, default) -> Any
├── PortfolioPDFGenerator
│   ├── _create_cover_page() -> List
│   ├── _create_product_pages() -> List
│   ├── _page_header_footer(canvas, doc)
│   └── generate() -> bytes
├── QuotationPDFGenerator
│   ├── _create_header() -> List
│   ├── _create_items_table() -> List
│   ├── _create_pricing_breakdown() -> List
│   ├── _create_terms_section() -> List
│   ├── _create_footer_section() -> List
│   ├── _page_header_footer(canvas, doc)
│   └── generate() -> bytes
└── Convenience Functions
    ├── generate_portfolio_pdf(portfolio, share_url) -> bytes
    └── generate_quotation_pdf(quotation) -> bytes
```

## How to Use

### Generating Portfolio PDFs

The portfolio PDF is generated automatically when exporting via the API:

```
GET /api/portfolios/{id}/export/pdf
```

Programmatically:
```python
from app.services.pdf_service import generate_portfolio_pdf

portfolio_data = {
    "name": "My Portfolio",
    "niche_name": "Electronics",
    "description": "Sample portfolio",
    "items": [
        {"product_name": "Product A", "product_sku": "SKU001", "notes": "Note"}
    ]
}
share_url = "https://example.com/portfolios/share/abc123"
pdf_bytes = generate_portfolio_pdf(portfolio_data, share_url)
```

### Generating Quotation PDFs

The quotation PDF is generated automatically when exporting via the API:

```
GET /api/quotations/{id}/export/pdf
```

Programmatically:
```python
from app.services.pdf_service import generate_quotation_pdf

quotation_data = {
    "quotation_number": "QT-001",
    "client_name": "Client Corp",
    "status": "draft",
    "currency": "USD",
    "items": [...],
    "subtotal": Decimal("100.00"),
    "grand_total": Decimal("120.00"),
    # ... other fields
}
pdf_bytes = generate_quotation_pdf(quotation_data)
```

## Configuration

### Branding Constants (in pdf_service.py)

| Constant | Value | Description |
|----------|-------|-------------|
| `PRIMARY_COLOR` | `#1976d2` | Material Design blue |
| `COMPANY_NAME` | `Kompass` | Company branding |
| `COMPANY_TAGLINE` | `Your Global Trade Partner` | Tagline |
| `MARGIN` | `0.75 inch` | Page margins |
| `PAGE_SIZE` | `A4` | Document size |

### Dependencies

- `reportlab>=4.0.0` - PDF generation
- `qrcode[pil]>=7.4.0` - QR code generation

## Testing

Run PDF service tests:
```bash
cd apps/Server
.venv/bin/pytest tests/services/test_pdf_service.py -v --tb=short
```

Test coverage includes:
- Portfolio PDF generation with various data scenarios
- Quotation PDF generation with all sections
- QR code generation
- Empty items handling
- Edge cases (missing fields, long text truncation)

## Notes

- QR codes are generated in-memory without file I/O for performance
- PDF generation typically completes in under 1 second for typical documents
- Logo is a text placeholder until actual branding assets are available
- Product images are not yet embedded (requires image storage infrastructure)
- Share URL for QR code is automatically generated using the first CORS origin as base URL
