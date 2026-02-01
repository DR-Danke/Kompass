# Quotation Service with Pricing Engine

**ADW ID:** bccd1fc5
**Date:** 2026-01-31
**Specification:** specs/issue-17-adw-bccd1fc5-quotation-service-pricing-engine.md

## Overview

This feature implements a comprehensive quotation service that provides full CRUD operations for quotations with an integrated pricing engine. The service automatically calculates pricing based on FOB costs, tariffs (HS codes), international/national freight, inspection, insurance, nationalization costs, and configurable margins. It includes support for line item management, status workflow transitions, and quotation cloning functionality.

## What Was Built

- **QuotationService** - Business logic layer for quotation lifecycle management
- **Pricing Engine** - Comprehensive cost calculation following the import pricing formula
- **Line Item Management** - CRUD operations for quotation line items
- **Status Workflow** - Validated state transitions for quotation lifecycle
- **Quotation Cloning** - Create new versions from existing quotations
- **REST API Endpoints** - Full CRUD and specialized operations via `/api/quotations`

## Technical Implementation

### Files Modified

- `apps/Server/app/services/__init__.py`: Added quotation_service export
- `apps/Server/main.py`: Registered quotation_routes router
- `apps/Server/app/models/kompass_dto.py`: Added new DTOs (QuotationPricingDTO, QuotationStatusTransitionDTO, QuotationCloneDTO)

### Files Created

- `apps/Server/app/services/quotation_service.py`: Main service implementation (915 lines)
- `apps/Server/app/api/quotation_routes.py`: REST API endpoints (431 lines)
- `apps/Server/tests/services/test_quotation_service.py`: Unit tests (653 lines)
- `apps/Server/tests/api/test_quotation_routes.py`: API integration tests (891 lines)

### Key Changes

- **Pricing Engine Formula**: Implements `Total COP = (FOB + Tariffs + Int'l Freight + Inspection + Insurance) × Exchange Rate + National Freight + Nationalization + Margin`
- **Status Workflow**: Enforces valid transitions: draft→sent→viewed→negotiating→accepted/rejected/expired
- **Repository Pattern**: Uses dependency injection for testability
- **Integration with PricingService**: Fetches tariff rates, freight rates, and pricing settings

## How to Use

### Creating a Quotation

```python
from app.services.quotation_service import quotation_service
from app.models.kompass_dto import QuotationCreateDTO

request = QuotationCreateDTO(
    client_id=client_uuid,
    incoterm=Incoterm.FOB,
    currency="USD",
    items=[...]  # Optional initial items
)
quotation = quotation_service.create_quotation(request, created_by=user_id)
```

### Calculating Pricing

```python
pricing = quotation_service.calculate_pricing(quotation_id)
# Returns QuotationPricingDTO with all cost components
```

### Updating Status

```python
from app.models.kompass_dto import QuotationStatusTransitionDTO, QuotationStatus

transition = QuotationStatusTransitionDTO(new_status=QuotationStatus.SENT)
updated = quotation_service.update_status(quotation_id, transition)
```

### Cloning a Quotation

```python
cloned = quotation_service.clone_quotation(
    quotation_id=source_id,
    created_by=user_id,
    clone_request=QuotationCloneDTO(notes="Updated pricing for Q2")
)
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/quotations` | List with pagination and filters |
| POST | `/api/quotations` | Create quotation |
| GET | `/api/quotations/{id}` | Get by ID |
| PUT | `/api/quotations/{id}` | Update quotation |
| DELETE | `/api/quotations/{id}` | Delete (admin/manager only) |
| POST | `/api/quotations/{id}/clone` | Clone quotation |
| GET | `/api/quotations/{id}/pricing` | Calculate pricing |
| PUT | `/api/quotations/{id}/status` | Update status |
| POST | `/api/quotations/{id}/items` | Add line item |
| PUT | `/api/quotations/items/{item_id}` | Update line item |
| DELETE | `/api/quotations/items/{item_id}` | Remove line item |

## Configuration

The pricing engine uses settings from `pricing_service`:

| Setting | Default | Description |
|---------|---------|-------------|
| `exchange_rate_usd_cop` | 4200.0 | USD to COP exchange rate |
| `default_margin_percentage` | 20.0 | Default margin percentage |
| `insurance_percentage` | 1.5 | Insurance as % of (FOB + Freight) |
| `inspection_cost_usd` | 150.0 | Fixed inspection cost in USD |
| `nationalization_cost_cop` | 200000.0 | Nationalization cost in COP |

## Testing

```bash
# Run unit tests
cd apps/Server && .venv/bin/pytest tests/services/test_quotation_service.py -v --tb=short

# Run API integration tests
cd apps/Server && .venv/bin/pytest tests/api/test_quotation_routes.py -v --tb=short
```

## Status Workflow

Valid status transitions:

```
draft → sent
sent → viewed, accepted, rejected, expired
viewed → negotiating, accepted, rejected, expired
negotiating → accepted, rejected, expired
accepted → expired
rejected → expired
```

## Notes

- Depends on `pricing_service` from KP-016 (Pricing Configuration Service)
- Uses existing `QuotationRepository` for data access
- Automatic totals recalculation when line items are modified
- Clone creates new quotation number with draft status
