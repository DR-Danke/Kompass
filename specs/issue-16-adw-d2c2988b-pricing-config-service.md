# Feature: Pricing Configuration Service

## Metadata
issue_number: `16`
adw_id: `d2c2988b`
issue_json: `{"number":16,"title":"[Kompass] Phase 6A: Pricing Configuration Service","body":"Implement pricing configuration service for HS codes, freight rates, and settings."}`

## Feature Description
Implement a comprehensive pricing configuration service that manages three key pricing components for the Kompass Portfolio & Quotation system:

1. **HS Codes Management**: Create, read, update, and search harmonized system codes with their associated tariff/duty rates for import classification
2. **Freight Rates Management**: Create, list, filter, and update freight rates by origin/destination with validity period tracking and expiration alerting
3. **Pricing Settings Management**: Get, update, and manage global pricing parameters with default values initialization

This service acts as the centralized pricing configuration layer that will be consumed by the quotation calculation engine in Phase 6B.

## User Story
As a Kompass system administrator
I want to configure and manage pricing components (HS codes, freight rates, and global settings)
So that the quotation system can accurately calculate costs, tariffs, and prices for client quotations

## Problem Statement
The quotation system needs access to:
- HS code tariff rates for calculating import duties
- Freight rates for shipping cost estimation between origins and destinations
- Global pricing settings (margins, inspection costs, insurance rates, exchange rates)

Without a centralized service to manage these pricing components, quotation calculations would be inconsistent, difficult to maintain, and prone to errors.

## Solution Statement
Create a `PricingService` class that consolidates all pricing configuration operations into a single service layer. The service will:
- Leverage existing repository classes (`HSCodeRepository`, `FreightRateRepository`, `PricingSettingsRepository`)
- Provide business logic for tariff lookups, freight rate matching, and settings management
- Initialize default pricing settings on first use
- Alert on expired freight rates to maintain data quality

## Relevant Files
Use these files to implement the feature:

- `apps/Server/app/repository/kompass_repository.py` - Contains existing `HSCodeRepository` (line 937), `FreightRateRepository` (line 3312), and `PricingSettingsRepository` (line 3587) that the service will consume
- `apps/Server/app/models/kompass_dto.py` - Contains existing DTOs: `HSCodeCreateDTO`, `HSCodeUpdateDTO`, `HSCodeResponseDTO`, `FreightRateCreateDTO`, `FreightRateUpdateDTO`, `FreightRateResponseDTO`, `PricingSettingCreateDTO`, `PricingSettingUpdateDTO`, `PricingSettingResponseDTO`
- `apps/Server/app/services/niche_service.py` - Reference for service layer pattern (singleton instance, repository usage, logging)
- `apps/Server/app/services/supplier_service.py` - Reference for comprehensive service with validation and filtering
- `apps/Server/tests/services/test_niche_service.py` - Reference for unit test structure with mocking
- `apps/Server/app/services/__init__.py` - Export the new service singleton

### New Files
- `apps/Server/app/services/pricing_service.py` - Main pricing configuration service
- `apps/Server/tests/services/test_pricing_service.py` - Unit tests for pricing service

## Implementation Plan

### Phase 1: Foundation
- Review existing repository implementations for HS codes, freight rates, and pricing settings
- Understand the DTO structure already defined in `kompass_dto.py`
- Ensure repository singleton exports are available in `kompass_repository.py`

### Phase 2: Core Implementation
- Create `PricingService` class with three logical sections:
  1. HS Code Methods (CRUD + search + tariff lookup)
  2. Freight Rate Methods (CRUD + filtering + active rate lookup + expiry check)
  3. Pricing Settings Methods (get/update single + get all + default initialization)
- Implement default settings initialization with predefined values
- Add proper error handling and logging

### Phase 3: Integration
- Export service singleton from `pricing_service.py`
- Add export to `__init__.py` for easy importing
- Write comprehensive unit tests with mocked repositories

## Step by Step Tasks

### Step 1: Review Existing Repository Implementations
- Read `apps/Server/app/repository/kompass_repository.py` (lines 937-1140 for HSCode, 3312-3580 for FreightRate, 3587-3760 for PricingSettings)
- Verify all required repository methods exist and understand their signatures
- Note any missing repository methods that may need to be added

### Step 2: Verify DTOs Are Complete
- Read `apps/Server/app/models/kompass_dto.py` (FreightRate DTOs at lines 813-870, PricingSettings DTOs at lines 878-912)
- Verify existing DTOs cover all required request/response models
- No new DTOs should be needed as they already exist

### Step 3: Create Pricing Service File
Create `apps/Server/app/services/pricing_service.py` with the following structure:
- Import statements (UUID, Decimal, typing, datetime, DTOs, repositories)
- Define default pricing settings constants
- `PricingService` class with:
  - HS Code methods: `create_hs_code`, `get_hs_code`, `list_hs_codes`, `update_hs_code`, `get_tariff_rate`, `search_hs_codes`
  - Freight Rate methods: `create_freight_rate`, `list_freight_rates`, `get_active_rate`, `update_freight_rate`, `check_expired_rates`
  - Pricing Settings methods: `get_setting`, `update_setting`, `get_all_settings`, `_initialize_default_settings`
- Singleton instance export

### Step 4: Implement HS Code Methods
- `create_hs_code(request: HSCodeCreateDTO) -> HSCodeResponseDTO`: Create new HS code via repository
- `get_hs_code(hs_code_id: UUID) -> Optional[HSCodeResponseDTO]`: Get HS code by ID
- `list_hs_codes(search: Optional[str] = None, page: int = 1, limit: int = 20) -> HSCodeListResponseDTO`: List with search and pagination
- `update_hs_code(hs_code_id: UUID, request: HSCodeUpdateDTO) -> Optional[HSCodeResponseDTO]`: Update existing HS code
- `get_tariff_rate(hs_code: str) -> Optional[Decimal]`: Get duty rate for a specific HS code string
- `search_hs_codes(query: str) -> List[HSCodeResponseDTO]`: Search by code or description (max 50 results)

### Step 5: Implement Freight Rate Methods
- `create_freight_rate(request: FreightRateCreateDTO) -> FreightRateResponseDTO`: Create new freight rate
- `list_freight_rates(origin: Optional[str] = None, destination: Optional[str] = None, page: int = 1, limit: int = 20) -> FreightRateListResponseDTO`: List with origin/destination filtering
- `get_active_rate(origin: str, destination: str, container_type: Optional[str] = None) -> Optional[FreightRateResponseDTO]`: Get currently active rate for a route (checks validity dates)
- `update_freight_rate(rate_id: UUID, request: FreightRateUpdateDTO) -> Optional[FreightRateResponseDTO]`: Update existing rate
- `check_expired_rates() -> List[FreightRateResponseDTO]`: Return list of rates with expired `valid_until` dates

### Step 6: Implement Pricing Settings Methods
- `get_setting(key: str) -> Optional[Decimal]`: Get single setting value by key
- `update_setting(key: str, value: Decimal, updated_by: UUID) -> Optional[PricingSettingResponseDTO]`: Update setting value
- `get_all_settings() -> Dict[str, Decimal]`: Get all settings as key-value dict
- `_initialize_default_settings()`: Private method to seed defaults if not present

### Step 7: Implement Default Settings Initialization
Define constants for default settings:
```python
DEFAULT_PRICING_SETTINGS = {
    "default_margin_percentage": Decimal("20.0"),
    "inspection_cost_usd": Decimal("150.0"),
    "insurance_percentage": Decimal("1.5"),
    "nationalization_cost_cop": Decimal("200000.0"),
    "exchange_rate_usd_cop": Decimal("4200.0"),
}
```
Implement `_initialize_default_settings()` to create missing settings on first access

### Step 8: Update Services __init__.py
- Add import for `pricing_service` singleton from `pricing_service.py`
- Export for easy access: `from app.services.pricing_service import pricing_service`

### Step 9: Create Unit Tests for HS Code Methods
Create `apps/Server/tests/services/test_pricing_service.py`:
- Test fixtures for mock HS code data
- `TestHsCodeMethods` class with tests for:
  - `test_create_hs_code_success`
  - `test_get_hs_code_success`
  - `test_get_hs_code_not_found`
  - `test_list_hs_codes_with_search`
  - `test_list_hs_codes_empty`
  - `test_update_hs_code_success`
  - `test_update_hs_code_not_found`
  - `test_get_tariff_rate_found`
  - `test_get_tariff_rate_not_found`
  - `test_search_hs_codes`

### Step 10: Create Unit Tests for Freight Rate Methods
Add to `test_pricing_service.py`:
- Test fixtures for mock freight rate data
- `TestFreightRateMethods` class with tests for:
  - `test_create_freight_rate_success`
  - `test_list_freight_rates_with_filters`
  - `test_list_freight_rates_empty`
  - `test_get_active_rate_found`
  - `test_get_active_rate_not_found`
  - `test_get_active_rate_expired`
  - `test_update_freight_rate_success`
  - `test_update_freight_rate_not_found`
  - `test_check_expired_rates`

### Step 11: Create Unit Tests for Pricing Settings Methods
Add to `test_pricing_service.py`:
- Test fixtures for mock settings data
- `TestPricingSettingsMethods` class with tests for:
  - `test_get_setting_found`
  - `test_get_setting_not_found`
  - `test_update_setting_success`
  - `test_update_setting_not_found`
  - `test_get_all_settings`
  - `test_get_all_settings_empty`
  - `test_initialize_default_settings`

### Step 12: Run Validation Commands
Execute all validation commands to ensure zero regressions:
- Run pytest for the new service tests
- Run ruff check for linting
- Run full test suite
- Verify type hints are correct

## Testing Strategy

### Unit Tests
- Mock all repository calls using `unittest.mock.patch`
- Test success paths for all CRUD operations
- Test error paths (not found, creation failures)
- Test search and filtering logic
- Test date-based logic (expired rates detection)
- Test default settings initialization

### Edge Cases
- HS code lookup with invalid/malformed code string
- Freight rate search with no matching routes
- Get active rate when all rates are expired
- Update setting that doesn't exist (should fail gracefully)
- Empty search query handling
- Pagination edge cases (page 0, negative limit)
- Decimal precision for tariff rates and pricing values

## Acceptance Criteria
- [ ] HS code CRUD operations working via service layer
- [ ] HS code search by code or description functional
- [ ] Tariff rate lookup by HS code string returns Decimal value
- [ ] Freight rate CRUD operations working via service layer
- [ ] Freight rate filtering by origin/destination functional
- [ ] Active rate lookup considers validity dates
- [ ] Expired rates detection returns correct list
- [ ] Pricing settings get/update working
- [ ] Default settings initialized when accessing empty table
- [ ] All unit tests passing with >90% coverage
- [ ] No ruff linting errors
- [ ] Type hints on all public methods

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && source .venv/bin/activate && .venv/bin/pytest tests/services/test_pricing_service.py -v --tb=short` - Run pricing service tests
- `cd apps/Server && source .venv/bin/activate && .venv/bin/ruff check app/services/pricing_service.py` - Lint the new service file
- `cd apps/Server && source .venv/bin/activate && .venv/bin/pytest tests/ -v --tb=short` - Run all Server tests to validate zero regressions
- `cd apps/Server && source .venv/bin/activate && .venv/bin/ruff check .` - Full lint check

## Notes
- The repository layer already exists with CRUD operations - this service adds business logic on top
- DTOs for HS codes, freight rates, and pricing settings are already defined in `kompass_dto.py`
- The `container_type` parameter in `get_active_rate` is optional since the current freight_rates schema doesn't have a container_type column - it can be used for future extensibility or filtered differently
- The `updated_by` parameter in `update_setting` should be a user UUID for audit trail, but the current schema doesn't store this - it's included in the method signature for future tracking
- Default settings initialization uses an upsert pattern - only creates settings that don't already exist
- Freight rate expiration check uses `valid_until < current_date` to identify expired rates that are still marked active
