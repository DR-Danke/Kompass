# Portfolio API Routes

**ADW ID:** e962d830
**Date:** 2026-01-31
**Specification:** specs/issue-13-adw-e962d830-portfolio-api-routes.md

## Overview

This feature completes the Portfolio API Routes implementation for the Kompass Portfolio & Quotation System. It adds PDF export functionality for portfolios and introduces alias routes for `/items` path pattern to ensure specification compliance while maintaining backward compatibility with existing `/products` routes.

## What Was Built

- PDF export endpoint for portfolios using reportlab library
- Public share endpoint alias (`/share/{token}` in addition to `/shared/{token}`)
- Item management alias routes (`/items` paths alongside existing `/products` paths)
- Comprehensive test coverage for all new endpoints

## Technical Implementation

### Files Modified

- `apps/Server/app/api/portfolio_routes.py`: Added PDF export endpoint, share route alias, and item management alias routes
- `apps/Server/app/services/portfolio_service.py`: Added `generate_pdf()` method for PDF generation with reportlab
- `apps/Server/app/models/kompass_dto.py`: Added `PortfolioAddItemRequestDTO` for the `/items` endpoint request body
- `apps/Server/requirements.txt`: Added reportlab dependency for PDF generation
- `apps/Server/tests/api/test_portfolio_routes.py`: Added tests for PDF export and alias routes

### Key Changes

- **PDF Export** (`GET /{portfolio_id}/export/pdf`): Generates a formatted PDF document with portfolio name, description, niche, product listing (with names, SKUs, notes), and generation timestamp. Uses reportlab's SimpleDocTemplate with A4 page size and styled tables
- **Share Route Alias** (`GET /share/{token}`): Provides specification-compliant path alongside existing `/shared/{token}` route for public portfolio access
- **Item Management Aliases**: Three new routes that mirror existing `/products` endpoints:
  - `POST /{portfolio_id}/items` - Add product (takes product_id in request body)
  - `DELETE /{portfolio_id}/items/{product_id}` - Remove product
  - `PUT /{portfolio_id}/items/reorder` - Reorder products

## How to Use

### PDF Export

1. Authenticate with a valid JWT token
2. Make a GET request to `/api/portfolios/{portfolio_id}/export/pdf`
3. The response will be a downloadable PDF file with the portfolio name as filename

```bash
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/portfolios/{portfolio_id}/export/pdf \
  -o portfolio.pdf
```

### Adding Items via /items Endpoint

```bash
curl -X POST -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"product_id": "<uuid>", "curator_notes": "Optional notes"}' \
  http://localhost:8000/api/portfolios/{portfolio_id}/items
```

### Public Share Access

Both URLs work identically for public portfolio access:
- `/api/portfolios/shared/{token}` (original)
- `/api/portfolios/share/{token}` (alias, spec-compliant)

## Configuration

No additional configuration required. The PDF export uses the existing JWT authentication and reportlab is installed via requirements.txt.

## Testing

Run the portfolio API tests:

```bash
cd apps/Server
source .venv/bin/activate
.venv/bin/pytest tests/api/test_portfolio_routes.py -v --tb=short
```

Test classes added:
- `TestPdfExport`: Tests for PDF generation, authentication, and 404 handling
- `TestItemAliasRoutes`: Tests for `/items` path alias endpoints
- `TestShareAliasRoute`: Tests for `/share/{token}` alias endpoint

## Notes

- The `/items` routes are aliases that call the same underlying service methods as `/products` routes
- PDF export requires authentication (any authenticated user can export)
- The generated PDF includes alternating row colors for readability and a professional table layout
- Empty portfolios generate a valid PDF with "No products in this portfolio" message
