# Feature: Kompass End-to-End Test Suite

## Metadata
issue_number: `32`
adw_id: `0be6430f`
issue_json: `{"number":32,"title":"[Kompass] Phase 13A: End-to-End Test Suite","body":"Create comprehensive E2E test suite for Kompass module covering Supplier, Product, Portfolio, Quotation, and Pricing flows."}`

## Feature Description
Create a comprehensive end-to-end test suite for the Kompass module that validates all critical user flows. The test suite will cover the complete lifecycle of suppliers, products, portfolios, quotations, and pricing configurations through both API integration tests and browser-based E2E tests using Playwright.

This test suite ensures that all Kompass features work correctly together, validating CRUD operations, business logic, calculations, PDF generation, and email functionality. The suite is designed for >80% coverage with test execution time under 5 minutes.

## User Story
As a Kompass developer or QA engineer
I want to have a comprehensive E2E test suite that validates all critical user flows
So that I can confidently deploy changes knowing the system works correctly end-to-end

## Problem Statement
The Kompass module currently has unit tests for individual services, but lacks comprehensive end-to-end tests that validate:
1. Complete user workflows from start to finish
2. Integration between services (e.g., supplier deletion affecting products)
3. API route behavior with proper authentication and authorization
4. Browser-based interactions for critical UI flows
5. Complex business logic like pricing calculations across the full stack

Without E2E tests, regression bugs can slip through when changes are made to one part of the system that affect other parts.

## Solution Statement
Implement a comprehensive E2E test suite organized into:
1. **API Integration Tests** - Test API routes with authentication, covering full CRUD workflows
2. **Service Integration Tests** - Test cross-service interactions and business logic
3. **Browser E2E Tests** - Playwright-based tests for critical UI workflows

The test suite will follow existing patterns in the codebase, using pytest with mocking for unit tests and actual API calls for integration tests.

## Relevant Files
Use these files to implement the feature:

### Existing Test Structure
- `apps/Server/tests/services/test_supplier_service.py` - Reference for service test patterns (mocking, fixtures, test organization)
- `apps/Server/tests/services/test_product_service.py` - Reference for complex service tests with images/tags
- `apps/Server/tests/services/test_portfolio_service.py` - Reference for portfolio workflow tests
- `apps/Server/tests/services/test_quotation_service.py` - Reference for quotation tests including PDF/email
- `apps/Server/tests/services/test_pricing_service.py` - Reference for pricing configuration tests
- `apps/Server/tests/api/test_supplier_routes.py` - Reference for API route test patterns with auth

### Services Under Test
- `apps/Server/app/services/supplier_service.py` - Supplier business logic
- `apps/Server/app/services/product_service.py` - Product business logic including bulk operations
- `apps/Server/app/services/portfolio_service.py` - Portfolio builder logic
- `apps/Server/app/services/quotation_service.py` - Quotation pricing and workflows
- `apps/Server/app/services/pricing_service.py` - Pricing settings and calculations

### API Routes Under Test
- `apps/Server/app/api/supplier_routes.py` - Supplier API endpoints
- `apps/Server/app/api/product_routes.py` - Product API endpoints
- `apps/Server/app/api/portfolio_routes.py` - Portfolio API endpoints
- `apps/Server/app/api/quotation_routes.py` - Quotation API endpoints
- `apps/Server/app/api/pricing_routes.py` - Pricing API endpoints

### E2E Test References
- `.claude/commands/test_e2e.md` - E2E test runner instructions
- `.claude/commands/e2e/test_suppliers_page.md` - Example E2E test for suppliers
- `.claude/commands/e2e/test_products_catalog.md` - Example E2E test for products
- `.claude/commands/e2e/test_portfolio_builder.md` - Example E2E test for portfolios
- `.claude/commands/e2e/test_quotation_creator.md` - Example E2E test for quotations
- `.claude/commands/e2e/test_pricing_config.md` - Example E2E test for pricing

### New Files

#### Test Directory Structure
- `apps/Server/tests/test_kompass/` - New directory for Kompass E2E tests
  - `__init__.py` - Package init
  - `conftest.py` - Shared fixtures for Kompass tests
  - `test_supplier_e2e.py` - Supplier workflow E2E tests
  - `test_product_e2e.py` - Product workflow E2E tests
  - `test_portfolio_e2e.py` - Portfolio workflow E2E tests
  - `test_quotation_e2e.py` - Quotation workflow E2E tests
  - `test_pricing_e2e.py` - Pricing configuration E2E tests
  - `test_api_integration.py` - Cross-service API integration tests

## Implementation Plan

### Phase 1: Foundation
1. Create the `test_kompass/` directory structure
2. Create `conftest.py` with shared fixtures for:
   - Test database connection (mock or test DB)
   - Sample data factories (suppliers, products, portfolios, quotations)
   - Authentication fixtures (mock users with different roles)
   - Test cleanup utilities
3. Establish test naming conventions and organization patterns

### Phase 2: Core Implementation
1. Implement supplier E2E tests covering full CRUD workflow
2. Implement product E2E tests including bulk import and tag management
3. Implement portfolio E2E tests with product management and PDF generation
4. Implement quotation E2E tests with pricing calculations and email
5. Implement pricing E2E tests for settings and HS codes

### Phase 3: Integration
1. Create cross-service integration tests (e.g., supplier deletion cascade)
2. Implement API route integration tests with authentication
3. Add performance assertions (test execution time < 5 minutes)
4. Ensure proper test isolation (no test dependencies)

## Step by Step Tasks

### Step 1: Create Test Directory Structure
- Create `apps/Server/tests/test_kompass/` directory
- Create `apps/Server/tests/test_kompass/__init__.py`
- Create `apps/Server/tests/test_kompass/conftest.py` with shared fixtures:
  - `mock_user_factory` - Create users with different roles
  - `sample_supplier_factory` - Generate supplier test data
  - `sample_product_factory` - Generate product test data with images/tags
  - `sample_portfolio_factory` - Generate portfolio test data
  - `sample_quotation_factory` - Generate quotation test data with items
  - `mock_pricing_settings` - Standard pricing configuration
  - `cleanup_fixtures` - Clean up test data after tests

### Step 2: Implement Supplier E2E Tests
- Create `apps/Server/tests/test_kompass/test_supplier_e2e.py`
- Test scenarios:
  - **TestSupplierCRUDWorkflow**: Create → Read → Update → Delete flow
  - **TestSupplierValidation**: Email validation, required fields, duplicate code handling
  - **TestSupplierFiltering**: List with status filter, country filter, has_products filter
  - **TestSupplierSearch**: Full-text search functionality
  - **TestSupplierWithProducts**: Verify delete blocked when products exist
- Follow pattern from `test_supplier_service.py` with mocked repositories

### Step 3: Implement Product E2E Tests
- Create `apps/Server/tests/test_kompass/test_product_e2e.py`
- Test scenarios:
  - **TestProductCRUDWorkflow**: Create → Read → Update → Delete flow
  - **TestProductWithImages**: Add, remove, set primary image
  - **TestProductWithTags**: Add, remove tags from products
  - **TestBulkImport**: Bulk create products with partial failure handling
  - **TestProductFiltering**: Filter by category, price range, status, tags
  - **TestProductSearch**: Full-text search across name, SKU, description

### Step 4: Implement Portfolio E2E Tests
- Create `apps/Server/tests/test_kompass/test_portfolio_e2e.py`
- Test scenarios:
  - **TestPortfolioCRUDWorkflow**: Create → Read → Update → Delete flow
  - **TestPortfolioProducts**: Add, remove, reorder products
  - **TestPortfolioDuplication**: Duplicate portfolio with all items
  - **TestCreateFromFilters**: Create portfolio from product filters
  - **TestShareToken**: Generate and validate share tokens
  - **TestPDFGeneration**: Generate portfolio PDF (mock PDF service)

### Step 5: Implement Quotation E2E Tests
- Create `apps/Server/tests/test_kompass/test_quotation_e2e.py`
- Test scenarios:
  - **TestQuotationCRUDWorkflow**: Create → Read → Update → Delete flow
  - **TestQuotationItems**: Add, remove, update line items
  - **TestQuotationCloning**: Clone quotation with items
  - **TestPricingCalculation**: Full pricing formula validation
  - **TestStatusWorkflow**: Draft → Sent → Viewed → Negotiating → Accepted/Rejected
  - **TestPDFGeneration**: Generate proforma PDF
  - **TestEmailSending**: Send quotation via email (mock mode)
  - **TestShareToken**: Generate and validate share tokens

### Step 6: Implement Pricing E2E Tests
- Create `apps/Server/tests/test_kompass/test_pricing_e2e.py`
- Test scenarios:
  - **TestHSCodeManagement**: CRUD for HS codes with tariff rates
  - **TestFreightRates**: CRUD for freight rates with validity dates
  - **TestPricingSettings**: Get, update, initialize default settings
  - **TestExpiredRateDetection**: Check for expired freight rates
  - **TestTariffLookup**: Get tariff rate by HS code

### Step 7: Implement API Integration Tests
- Create `apps/Server/tests/test_kompass/test_api_integration.py`
- Test scenarios:
  - **TestAuthenticatedEndpoints**: All endpoints require authentication
  - **TestRBACEnforcement**: Admin-only endpoints (delete operations)
  - **TestCrossServiceIntegration**:
    - Delete supplier fails when products exist
    - Delete portfolio succeeds and removes items
    - Quotation status transitions enforce workflow rules
  - **TestPaginationAcrossEndpoints**: Consistent pagination behavior
  - **TestErrorHandling**: Proper error responses with correct status codes

### Step 8: Add conftest.py Improvements
- Add fixtures for test performance tracking
- Add fixtures for test isolation verification
- Add markers for slow tests vs fast tests
- Add markers for integration tests vs unit tests

### Step 9: Run Validation Commands
Execute the validation commands to ensure all tests pass and no regressions are introduced.

## Testing Strategy

### Unit Tests
The existing service tests (`test_supplier_service.py`, `test_product_service.py`, etc.) cover unit-level testing with mocked dependencies. The new E2E tests complement these by testing:
- Full workflow integration
- Cross-service interactions
- API layer behavior
- Authentication/authorization

### Edge Cases
1. **Empty states**: Empty lists, no items, zero values
2. **Boundary conditions**: Pagination limits, max items, very long strings
3. **Concurrent operations**: Duplicate creates, race conditions
4. **Invalid data**: Malformed requests, invalid UUIDs, missing required fields
5. **Authorization failures**: Wrong role, expired token, missing token
6. **Cascade effects**: Deleting entities with dependencies
7. **Calculation edge cases**: Zero quantities, maximum values, currency precision

## Acceptance Criteria
- [ ] All test scenarios passing (100% pass rate)
- [ ] Test coverage > 80% for Kompass services
- [ ] Tests run in < 5 minutes total
- [ ] No flaky tests (consistent results across runs)
- [ ] Tests are isolated (can run in any order)
- [ ] Proper test naming and documentation
- [ ] Shared fixtures reduce code duplication
- [ ] Integration tests cover cross-service interactions
- [ ] API tests validate authentication and authorization

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

```bash
# Navigate to Server directory
cd apps/Server

# Activate virtual environment (if not already active)
source .venv/bin/activate

# Run all Kompass E2E tests
.venv/bin/pytest tests/test_kompass/ -v --tb=short

# Run all tests with coverage
.venv/bin/pytest tests/ -v --tb=short --cov=app --cov-report=term-missing

# Run only the new E2E tests
.venv/bin/pytest tests/test_kompass/ -v --tb=short -x

# Run tests with time reporting (ensure < 5 minutes)
.venv/bin/pytest tests/ -v --tb=short --durations=10

# Run ruff linter on test files
.venv/bin/ruff check tests/test_kompass/

# Run type check on Server codebase
cd ../Client && npm run typecheck

# Run Client build
cd ../Client && npm run build
```

## Notes

### Test Organization
- Each test file focuses on one domain (supplier, product, etc.)
- Test classes group related scenarios
- Fixtures are shared via `conftest.py` at appropriate levels
- Tests are marked with pytest markers for selective execution

### Mocking Strategy
- Repository layer is mocked for unit tests
- Service layer is tested with mocked repositories
- API layer uses FastAPI TestClient with mocked services
- External services (email, PDF) are always mocked

### Performance Considerations
- Use `pytest-xdist` for parallel test execution if needed
- Lazy fixture initialization where possible
- Minimal database operations (mock where appropriate)
- Cache frequently used test data

### Future Enhancements
- Add pytest-cov for coverage reporting
- Add pytest-benchmark for performance regression testing
- Add hypothesis for property-based testing
- Consider adding contract tests for API responses
