"""Shared fixtures for Kompass E2E tests.

Provides reusable fixtures for:
- Authentication (mock users with different roles)
- Sample data factories (suppliers, products, portfolios, quotations)
- Test clients (authenticated, admin, viewer)
- Cleanup utilities
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, Optional
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest

from app.models.kompass_dto import PaginationDTO


# =============================================================================
# AUTHENTICATION FIXTURES
# =============================================================================


@pytest.fixture
def mock_user_id() -> UUID:
    """Generate a consistent mock user ID."""
    return uuid4()


@pytest.fixture
def mock_auth_user(mock_user_id) -> Dict[str, Any]:
    """Create a mock authenticated user with 'user' role."""
    return {
        "id": str(mock_user_id),
        "email": "test@example.com",
        "role": "user",
        "is_active": True,
    }


@pytest.fixture
def mock_admin_user() -> Dict[str, Any]:
    """Create a mock admin user for RBAC tests."""
    return {
        "id": str(uuid4()),
        "email": "admin@example.com",
        "role": "admin",
        "is_active": True,
    }


@pytest.fixture
def mock_manager_user() -> Dict[str, Any]:
    """Create a mock manager user for RBAC tests."""
    return {
        "id": str(uuid4()),
        "email": "manager@example.com",
        "role": "manager",
        "is_active": True,
    }


@pytest.fixture
def mock_viewer_user() -> Dict[str, Any]:
    """Create a mock viewer (read-only) user."""
    return {
        "id": str(uuid4()),
        "email": "viewer@example.com",
        "role": "viewer",
        "is_active": True,
    }


# =============================================================================
# SUPPLIER FIXTURES
# =============================================================================


def create_sample_supplier(
    supplier_id: Optional[UUID] = None,
    name: str = "Test Supplier",
    code: str = "TS001",
    status: str = "active",
    country: str = "China",
) -> Dict[str, Any]:
    """Factory function to create sample supplier data."""
    now = datetime.now()
    supplier_id = supplier_id or uuid4()
    return {
        "id": supplier_id,
        "name": name,
        "code": code,
        "status": status,
        "contact_name": "John Doe",
        "contact_email": "john@example.com",
        "contact_phone": "123456789",
        "address": "123 Test Street",
        "city": "Shanghai",
        "country": country,
        "website": "https://example.com",
        "notes": "Test notes",
        "created_at": now,
        "updated_at": now,
    }


@pytest.fixture
def sample_supplier_data() -> Dict[str, Any]:
    """Sample supplier data for testing."""
    return create_sample_supplier()


@pytest.fixture
def sample_supplier_list() -> list:
    """List of sample suppliers for testing."""
    return [
        create_sample_supplier(name=f"Supplier {i}", code=f"SUP{i:03d}")
        for i in range(5)
    ]


# =============================================================================
# PRODUCT FIXTURES
# =============================================================================


def create_sample_product(
    product_id: Optional[UUID] = None,
    sku: str = "PRD-20250101-ABC123",
    name: str = "Test Product",
    supplier_id: Optional[UUID] = None,
    status: str = "active",
    with_images: bool = False,
    with_tags: bool = False,
) -> Dict[str, Any]:
    """Factory function to create sample product data."""
    now = datetime.now()
    product_id = product_id or uuid4()
    supplier_id = supplier_id or uuid4()

    product = {
        "id": product_id,
        "sku": sku,
        "name": name,
        "description": "Test description",
        "supplier_id": supplier_id,
        "supplier_name": "Test Supplier",
        "category_id": uuid4(),
        "category_name": "Test Category",
        "hs_code_id": uuid4(),
        "hs_code": "1234.56.78",
        "status": status,
        "unit_cost": Decimal("10.00"),
        "unit_price": Decimal("20.00"),
        "currency": "USD",
        "unit_of_measure": "piece",
        "minimum_order_qty": 10,
        "lead_time_days": 14,
        "weight_kg": Decimal("0.5"),
        "dimensions": "10x10x10",
        "origin_country": "China",
        "created_at": now,
        "updated_at": now,
        "images": [],
        "tags": [],
    }

    if with_images:
        product["images"] = [
            {
                "id": uuid4(),
                "product_id": product_id,
                "url": "https://example.com/image1.jpg",
                "alt_text": "Primary image",
                "sort_order": 0,
                "is_primary": True,
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": uuid4(),
                "product_id": product_id,
                "url": "https://example.com/image2.jpg",
                "alt_text": "Secondary image",
                "sort_order": 1,
                "is_primary": False,
                "created_at": now,
                "updated_at": now,
            },
        ]

    if with_tags:
        product["tags"] = [
            {
                "id": uuid4(),
                "name": "Tag1",
                "color": "#FF0000",
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": uuid4(),
                "name": "Tag2",
                "color": "#00FF00",
                "created_at": now,
                "updated_at": now,
            },
        ]

    return product


@pytest.fixture
def sample_product_data() -> Dict[str, Any]:
    """Sample product data for testing."""
    return create_sample_product()


@pytest.fixture
def sample_product_with_images() -> Dict[str, Any]:
    """Sample product data with images."""
    return create_sample_product(with_images=True)


@pytest.fixture
def sample_product_with_tags() -> Dict[str, Any]:
    """Sample product data with tags."""
    return create_sample_product(with_tags=True)


@pytest.fixture
def sample_product_list() -> list:
    """List of sample products for testing."""
    return [
        create_sample_product(name=f"Product {i}", sku=f"PRD-{i:04d}")
        for i in range(5)
    ]


# =============================================================================
# PORTFOLIO FIXTURES
# =============================================================================


def create_sample_portfolio(
    portfolio_id: Optional[UUID] = None,
    name: str = "Test Portfolio",
    niche_id: Optional[UUID] = None,
    is_active: bool = True,
    with_items: bool = False,
) -> Dict[str, Any]:
    """Factory function to create sample portfolio data."""
    now = datetime.now()
    portfolio_id = portfolio_id or uuid4()
    niche_id = niche_id or uuid4()

    portfolio = {
        "id": portfolio_id,
        "name": name,
        "description": "Test description",
        "niche_id": niche_id,
        "niche_name": "Test Niche",
        "is_active": is_active,
        "items": [],
        "item_count": 0,
        "created_at": now,
        "updated_at": now,
    }

    if with_items:
        portfolio["items"] = [
            {
                "id": uuid4(),
                "portfolio_id": portfolio_id,
                "product_id": uuid4(),
                "product_name": f"Product {i}",
                "product_sku": f"PRD-{i:04d}",
                "sort_order": i,
                "notes": f"Notes for item {i}",
                "created_at": now,
                "updated_at": now,
            }
            for i in range(3)
        ]
        portfolio["item_count"] = 3

    return portfolio


@pytest.fixture
def sample_portfolio_data() -> Dict[str, Any]:
    """Sample portfolio data for testing."""
    return create_sample_portfolio()


@pytest.fixture
def sample_portfolio_with_items() -> Dict[str, Any]:
    """Sample portfolio data with items."""
    return create_sample_portfolio(with_items=True)


# =============================================================================
# QUOTATION FIXTURES
# =============================================================================


def create_sample_quotation(
    quotation_id: Optional[UUID] = None,
    quotation_number: str = "QT-000001",
    client_id: Optional[UUID] = None,
    status: str = "draft",
    with_items: bool = False,
) -> Dict[str, Any]:
    """Factory function to create sample quotation data."""
    now = datetime.now()
    quotation_id = quotation_id or uuid4()
    client_id = client_id or uuid4()

    quotation = {
        "id": quotation_id,
        "quotation_number": quotation_number,
        "client_id": client_id,
        "client_name": "Test Client Inc",
        "status": status,
        "incoterm": "FOB",
        "currency": "USD",
        "subtotal": Decimal("1000.00"),
        "freight_cost": Decimal("100.00"),
        "insurance_cost": Decimal("50.00"),
        "other_costs": Decimal("200000.00"),
        "total": Decimal("1150.00"),
        "discount_percent": Decimal("0.00"),
        "discount_amount": Decimal("0.00"),
        "grand_total": Decimal("1150.00"),
        "notes": "Test quotation",
        "terms_and_conditions": "Standard terms",
        "valid_from": date.today(),
        "valid_until": date.today() + timedelta(days=30),
        "created_by": uuid4(),
        "items": [],
        "item_count": 0,
        "created_at": now,
        "updated_at": now,
    }

    if with_items:
        quotation["items"] = [
            {
                "id": uuid4(),
                "quotation_id": quotation_id,
                "product_id": None,
                "sku": f"SKU{i:03d}",
                "product_name": f"Widget {chr(65 + i)}",
                "description": f"A great widget {i}",
                "quantity": 10,
                "unit_of_measure": "piece",
                "unit_cost": Decimal("50.00"),
                "unit_price": Decimal("100.00"),
                "markup_percent": Decimal("100.00"),
                "tariff_percent": Decimal("10.00"),
                "tariff_amount": Decimal("100.00"),
                "freight_amount": Decimal("0.00"),
                "line_total": Decimal("1100.00"),
                "sort_order": i,
                "notes": None,
                "created_at": now,
                "updated_at": now,
            }
            for i in range(2)
        ]
        quotation["item_count"] = 2
        quotation["subtotal"] = Decimal("2200.00")

    return quotation


@pytest.fixture
def sample_quotation_data() -> Dict[str, Any]:
    """Sample quotation data for testing."""
    return create_sample_quotation()


@pytest.fixture
def sample_quotation_with_items() -> Dict[str, Any]:
    """Sample quotation data with items."""
    return create_sample_quotation(with_items=True)


# =============================================================================
# PRICING FIXTURES
# =============================================================================


def create_sample_hs_code(
    hs_code_id: Optional[UUID] = None,
    code: str = "8471.30.00",
    duty_rate: Decimal = Decimal("5.00"),
) -> Dict[str, Any]:
    """Factory function to create sample HS code data."""
    now = datetime.now()
    return {
        "id": hs_code_id or uuid4(),
        "code": code,
        "description": "Portable automatic data processing machines",
        "duty_rate": duty_rate,
        "notes": "Laptops and tablets",
        "created_at": now,
        "updated_at": now,
    }


def create_sample_freight_rate(
    rate_id: Optional[UUID] = None,
    origin: str = "Shanghai",
    destination: str = "Buenaventura",
    is_active: bool = True,
    valid_until: Optional[date] = None,
) -> Dict[str, Any]:
    """Factory function to create sample freight rate data."""
    now = datetime.now()
    return {
        "id": rate_id or uuid4(),
        "origin": origin,
        "destination": destination,
        "incoterm": "FOB",
        "rate_per_kg": Decimal("2.50"),
        "rate_per_cbm": Decimal("150.00"),
        "minimum_charge": Decimal("100.00"),
        "transit_days": 30,
        "is_active": is_active,
        "valid_from": date.today() - timedelta(days=30),
        "valid_until": valid_until or (date.today() + timedelta(days=60)),
        "notes": "Standard sea freight",
        "created_at": now,
        "updated_at": now,
    }


@pytest.fixture
def sample_hs_code_data() -> Dict[str, Any]:
    """Sample HS code data for testing."""
    return create_sample_hs_code()


@pytest.fixture
def sample_freight_rate_data() -> Dict[str, Any]:
    """Sample freight rate data for testing."""
    return create_sample_freight_rate()


@pytest.fixture
def mock_pricing_settings() -> Dict[str, Decimal]:
    """Standard pricing configuration for testing."""
    return {
        "exchange_rate_usd_cop": Decimal("4200.0"),
        "default_margin_percentage": Decimal("20.0"),
        "insurance_percentage": Decimal("1.5"),
        "inspection_cost_usd": Decimal("150.0"),
        "nationalization_cost_cop": Decimal("200000.0"),
    }


# =============================================================================
# PAGINATION FIXTURES
# =============================================================================


@pytest.fixture
def sample_pagination() -> PaginationDTO:
    """Sample pagination data for testing."""
    return PaginationDTO(page=1, limit=20, total=100, pages=5)


# =============================================================================
# MOCK REPOSITORY FIXTURE
# =============================================================================


@pytest.fixture
def mock_repository():
    """Create a generic mock repository."""
    return MagicMock()


# =============================================================================
# TEST MARKERS
# =============================================================================


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )
