# Pricing Configuration Service

**ADW ID:** d2c2988b
**Date:** 2026-01-31
**Specification:** specs/issue-16-adw-d2c2988b-pricing-config-service.md

## Overview

A comprehensive pricing configuration service that manages three key pricing components for the Kompass Portfolio & Quotation system: HS codes with tariff/duty rates, freight rates by origin/destination with validity tracking, and global pricing settings. This service acts as the centralized pricing configuration layer consumed by the quotation calculation engine.

## What Was Built

- **HS Code Management**: CRUD operations, tariff rate lookups, and search by code or description
- **Freight Rate Management**: CRUD operations with origin/destination filtering, active rate lookup with validity date checking, and expired rate detection
- **Pricing Settings Management**: Get/update individual settings, get all settings, default settings initialization with upsert pattern
- **Comprehensive Unit Tests**: Full test coverage for all service methods including edge cases

## Technical Implementation

### Files Modified

- `apps/Server/app/services/__init__.py`: Added export for pricing_service singleton
- `apps/Server/app/services/pricing_service.py`: New pricing configuration service (502 lines)
- `apps/Server/tests/services/test_pricing_service.py`: Unit tests for all service methods (718 lines)

### Key Changes

- **Service Layer Pattern**: Follows existing patterns from `niche_service.py` and `supplier_service.py` with singleton instance export
- **Repository Integration**: Consumes existing `hs_code_repository`, `freight_rate_repository`, and `pricing_settings_repository`
- **Default Settings Initialization**: Seeds 5 default pricing parameters (margin %, inspection cost, insurance %, nationalization cost, exchange rate) when not present
- **Validity Date Logic**: Active freight rate lookup checks both `valid_from` and `valid_until` against current date
- **Expired Rate Detection**: Identifies active rates where `valid_until < today` for data quality alerts

## How to Use

1. **Import the service**:
   ```python
   from app.services.pricing_service import pricing_service
   ```

2. **HS Code Operations**:
   ```python
   # Create HS code
   hs_code = pricing_service.create_hs_code(HSCodeCreateDTO(...))

   # Get tariff rate by code string
   rate = pricing_service.get_tariff_rate("8471.30")  # Returns Decimal or None

   # Search HS codes
   results = pricing_service.search_hs_codes("electronic")  # Max 50 results
   ```

3. **Freight Rate Operations**:
   ```python
   # Get active rate for a route
   rate = pricing_service.get_active_rate("Shanghai", "Bogota")

   # Check for expired rates
   expired = pricing_service.check_expired_rates()
   ```

4. **Pricing Settings**:
   ```python
   # Initialize defaults (call once on startup if needed)
   count = pricing_service.initialize_default_settings()

   # Get all settings as dict
   settings = pricing_service.get_all_settings()
   # Returns: {"default_margin_percentage": Decimal("20.0"), ...}

   # Update a setting
   pricing_service.update_setting("exchange_rate_usd_cop", Decimal("4300.0"))
   ```

## Configuration

Default pricing settings initialized by `initialize_default_settings()`:

| Key | Default Value | Description |
|-----|---------------|-------------|
| `default_margin_percentage` | 20.0 | Default profit margin percentage |
| `inspection_cost_usd` | 150.0 | Standard inspection cost in USD |
| `insurance_percentage` | 1.5 | Insurance rate as % of CIF value |
| `nationalization_cost_cop` | 200,000.0 | Nationalization cost in COP |
| `exchange_rate_usd_cop` | 4,200.0 | USD to COP exchange rate |

## Testing

Run the pricing service tests:

```bash
cd apps/Server
source .venv/bin/activate
.venv/bin/pytest tests/services/test_pricing_service.py -v --tb=short
```

Run linting:

```bash
.venv/bin/ruff check app/services/pricing_service.py
```

## Notes

- The `container_type` parameter in `get_active_rate` is reserved for future use (current schema doesn't have this column)
- The `updated_by` parameter in `update_setting` accepts a UUID for audit trail but is not stored in current schema
- Freight rate expiration check uses `valid_until < current_date` to identify expired rates still marked active
- The service uses an upsert pattern for default settings - only creates settings that don't already exist
