# Quotation API Routes

**ADW ID:** 0884e820
**Date:** 2026-02-01
**Specification:** specs/issue-19-adw-0884e820-quotation-api-routes.md

## Overview

This feature extends the Kompass quotation API with additional endpoints for pricing recalculation, PDF proforma export, email sending, and public share token access. It also updates line item routes to use a nested URL pattern for better consistency.

## What Was Built

- POST `/api/quotations/{id}/calculate` - Recalculate and persist pricing
- GET `/api/quotations/{id}/export/pdf` - Generate PDF proforma document
- POST `/api/quotations/{id}/send` - Send quotation via email (mock mode supported)
- POST `/api/quotations/{id}/share` - Generate share token for public access
- GET `/api/quotations/share/{token}` - Public quotation view (no authentication)
- Updated line item routes to use nested pattern `/{quotation_id}/items/{item_id}`
- Item ownership validation to ensure items belong to specified quotation

## Technical Implementation

### Files Modified

- `apps/Server/app/api/quotation_routes.py`: Added 5 new endpoints and updated line item routes
- `apps/Server/app/models/kompass_dto.py`: Added 5 new DTOs for share tokens, public response, and email functionality
- `apps/Server/app/services/quotation_service.py`: Added PDF generation, share token, email, and item validation methods
- `apps/Server/tests/api/test_quotation_routes.py`: Added tests for all new endpoints
- `apps/Server/tests/services/test_quotation_service.py`: Added unit tests for new service methods

### Key Changes

- **PDF Generation**: Uses reportlab to create professional proforma documents with line items table, totals breakdown, terms, and footer
- **Share Tokens**: JWT-based tokens with 30-day expiration for public quotation access
- **Email Functionality**: Supports mock mode via `EMAIL_MOCK_MODE` environment variable; generates PDF attachment
- **Public Endpoint**: The `/share/{token}` endpoint is defined first in the router to avoid authentication requirement
- **Item Validation**: New `validate_item_belongs_to_quotation()` method ensures items belong to the specified quotation before update/delete

### New DTOs

- `QuotationShareTokenResponseDTO`: Contains `token`, `quotation_id`, `expires_at`
- `QuotationPublicResponseDTO`: Limited quotation data for public viewing (no sensitive internal fields)
- `QuotationPublicItemDTO`: Line item data for public response
- `QuotationSendEmailRequestDTO`: Email recipient details with optional PDF attachment
- `QuotationSendEmailResponseDTO`: Email result with mock mode indicator

## How to Use

### Recalculate Pricing

```bash
POST /api/quotations/{quotation_id}/calculate
Authorization: Bearer <token>
```

Returns updated `QuotationPricingDTO` with recalculated totals persisted to database.

### Export PDF Proforma

```bash
GET /api/quotations/{quotation_id}/export/pdf
Authorization: Bearer <token>
```

Returns a PDF file with filename `{quotation_number}_proforma.pdf`.

### Send Quotation Email

```bash
POST /api/quotations/{quotation_id}/send
Authorization: Bearer <token>
Content-Type: application/json

{
  "recipient_email": "client@example.com",
  "recipient_name": "John Doe",
  "subject": "Your Quotation",
  "message": "Please find attached our quotation.",
  "include_pdf": true
}
```

### Generate Share Token

```bash
POST /api/quotations/{quotation_id}/share
Authorization: Bearer <token>
```

Returns token valid for 30 days.

### Access Public Quotation

```bash
GET /api/quotations/share/{token}
```

No authentication required. Returns `QuotationPublicResponseDTO`.

### Update/Delete Line Items (Nested Routes)

```bash
PUT /api/quotations/{quotation_id}/items/{item_id}
DELETE /api/quotations/{quotation_id}/items/{item_id}
```

Both endpoints validate that the item belongs to the specified quotation.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `EMAIL_MOCK_MODE` | `true` | When true, emails are logged but not sent |
| `JWT_SECRET_KEY` | - | Used for share token generation/validation |
| `JWT_ALGORITHM` | `HS256` | Algorithm for share token JWT |

## Testing

```bash
# Run quotation route tests
cd apps/Server && .venv/bin/pytest tests/api/test_quotation_routes.py -v --tb=short

# Run quotation service tests
cd apps/Server && .venv/bin/pytest tests/services/test_quotation_service.py -v --tb=short

# Run all server tests
cd apps/Server && .venv/bin/pytest tests/ -v --tb=short
```

## Notes

- PDF generation uses the same reportlab styling patterns as portfolio PDF export
- Share token follows the same JWT pattern as portfolio share functionality
- Email sending defaults to mock mode; SMTP integration requires additional configuration
- The public share endpoint is placed at the top of the router to ensure it's matched before authenticated routes
