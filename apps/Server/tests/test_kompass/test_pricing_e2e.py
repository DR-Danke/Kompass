"""End-to-end tests for Pricing configuration workflows.

Tests cover:
- HS code management (CRUD for HS codes with tariff rates)
- Freight rates (CRUD with validity dates)
- Pricing settings (get, update, initialize defaults)
- Expired rate detection
- Tariff lookup by HS code
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import patch
from uuid import uuid4

import pytest

from app.models.kompass_dto import (
    FreightRateCreateDTO,
    FreightRateUpdateDTO,
    HSCodeCreateDTO,
    HSCodeUpdateDTO,
    Incoterm,
    PricingSettingCreateDTO,
)
from app.services.pricing_service import (
    DEFAULT_PRICING_SETTINGS,
    PricingService,
)

from .conftest import create_sample_freight_rate, create_sample_hs_code


# =============================================================================
# SERVICE FIXTURES
# =============================================================================


@pytest.fixture
def pricing_service():
    """Create a fresh PricingService instance for each test."""
    return PricingService()


# =============================================================================
# HS CODE MANAGEMENT TESTS
# =============================================================================


class TestHSCodeManagement:
    """Tests for HS code CRUD operations."""

    @patch("app.services.pricing_service.hs_code_repository")
    def test_create_hs_code_success(
        self, mock_repo, pricing_service, sample_hs_code_data
    ):
        """Test creating an HS code successfully."""
        mock_repo.create.return_value = sample_hs_code_data

        request = HSCodeCreateDTO(
            code="8471.30.00",
            description="Portable automatic data processing machines",
            duty_rate=Decimal("5.00"),
            notes="Laptops and tablets",
        )
        result = pricing_service.create_hs_code(request)

        assert result is not None
        assert result.code == "8471.30.00"
        assert result.duty_rate == Decimal("5.00")
        mock_repo.create.assert_called_once()

    @patch("app.services.pricing_service.hs_code_repository")
    def test_create_hs_code_failure(self, mock_repo, pricing_service):
        """Test HS code creation failure."""
        mock_repo.create.return_value = None

        request = HSCodeCreateDTO(
            code="INVALID",
            description="Test",
        )
        result = pricing_service.create_hs_code(request)

        assert result is None

    @patch("app.services.pricing_service.hs_code_repository")
    def test_get_hs_code_success(
        self, mock_repo, pricing_service, sample_hs_code_data
    ):
        """Test getting an HS code by ID."""
        mock_repo.get_by_id.return_value = sample_hs_code_data

        result = pricing_service.get_hs_code(sample_hs_code_data["id"])

        assert result is not None
        assert result.id == sample_hs_code_data["id"]
        assert result.code == "8471.30.00"

    @patch("app.services.pricing_service.hs_code_repository")
    def test_get_hs_code_not_found(self, mock_repo, pricing_service):
        """Test getting a non-existent HS code."""
        mock_repo.get_by_id.return_value = None

        result = pricing_service.get_hs_code(uuid4())

        assert result is None

    @patch("app.services.pricing_service.hs_code_repository")
    def test_list_hs_codes_with_search(self, mock_repo, pricing_service):
        """Test listing HS codes with search."""
        hs_codes = [
            create_sample_hs_code(code="8471.30.00"),
            create_sample_hs_code(code="8471.41.00"),
        ]
        mock_repo.get_all.return_value = (hs_codes, 2)

        result = pricing_service.list_hs_codes(search="8471", page=1, limit=20)

        assert len(result.items) == 2
        assert result.pagination.total == 2
        mock_repo.get_all.assert_called_once_with(page=1, limit=20, search="8471")

    @patch("app.services.pricing_service.hs_code_repository")
    def test_list_hs_codes_empty(self, mock_repo, pricing_service):
        """Test listing HS codes when none exist."""
        mock_repo.get_all.return_value = ([], 0)

        result = pricing_service.list_hs_codes()

        assert result.items == []
        assert result.pagination.total == 0

    @patch("app.services.pricing_service.hs_code_repository")
    def test_update_hs_code_success(
        self, mock_repo, pricing_service, sample_hs_code_data
    ):
        """Test updating an HS code."""
        updated_hs_code = sample_hs_code_data.copy()
        updated_hs_code["duty_rate"] = Decimal("10.00")
        mock_repo.get_by_id.return_value = sample_hs_code_data
        mock_repo.update.return_value = updated_hs_code

        request = HSCodeUpdateDTO(duty_rate=Decimal("10.00"))
        result = pricing_service.update_hs_code(sample_hs_code_data["id"], request)

        assert result is not None
        assert result.duty_rate == Decimal("10.00")

    @patch("app.services.pricing_service.hs_code_repository")
    def test_update_hs_code_not_found(self, mock_repo, pricing_service):
        """Test updating a non-existent HS code."""
        mock_repo.get_by_id.return_value = None

        request = HSCodeUpdateDTO(duty_rate=Decimal("10.00"))
        result = pricing_service.update_hs_code(uuid4(), request)

        assert result is None
        mock_repo.update.assert_not_called()


# =============================================================================
# TARIFF LOOKUP TESTS
# =============================================================================


class TestTariffLookup:
    """Tests for tariff rate lookup by HS code."""

    @patch("app.services.pricing_service.hs_code_repository")
    def test_get_tariff_rate_found(
        self, mock_repo, pricing_service, sample_hs_code_data
    ):
        """Test getting tariff rate for an existing HS code."""
        mock_repo.get_by_code.return_value = sample_hs_code_data

        result = pricing_service.get_tariff_rate("8471.30.00")

        assert result == Decimal("5.00")

    @patch("app.services.pricing_service.hs_code_repository")
    def test_get_tariff_rate_not_found(self, mock_repo, pricing_service):
        """Test getting tariff rate for a non-existent HS code."""
        mock_repo.get_by_code.return_value = None

        result = pricing_service.get_tariff_rate("9999.99.99")

        assert result is None

    @patch("app.services.pricing_service.hs_code_repository")
    def test_search_hs_codes(self, mock_repo, pricing_service):
        """Test searching HS codes."""
        hs_codes = [
            create_sample_hs_code(code="8471.30.00"),
            create_sample_hs_code(code="8471.41.00"),
        ]
        mock_repo.get_all.return_value = (hs_codes, 2)

        result = pricing_service.search_hs_codes("data processing")

        assert len(result) == 2
        mock_repo.get_all.assert_called_once_with(
            page=1, limit=50, search="data processing"
        )

    @patch("app.services.pricing_service.hs_code_repository")
    def test_search_hs_codes_empty_query(self, mock_repo, pricing_service):
        """Test searching with empty query returns empty list."""
        result = pricing_service.search_hs_codes("")

        assert result == []
        mock_repo.get_all.assert_not_called()

    @patch("app.services.pricing_service.hs_code_repository")
    def test_search_hs_codes_whitespace_query(self, mock_repo, pricing_service):
        """Test searching with whitespace-only query returns empty list."""
        result = pricing_service.search_hs_codes("   ")

        assert result == []
        mock_repo.get_all.assert_not_called()


# =============================================================================
# FREIGHT RATES TESTS
# =============================================================================


class TestFreightRates:
    """Tests for freight rate CRUD operations."""

    @patch("app.services.pricing_service.freight_rate_repository")
    def test_create_freight_rate_success(
        self, mock_repo, pricing_service, sample_freight_rate_data
    ):
        """Test creating a freight rate successfully."""
        mock_repo.create.return_value = sample_freight_rate_data

        request = FreightRateCreateDTO(
            origin="Shanghai",
            destination="Buenaventura",
            incoterm=Incoterm.FOB,
            rate_per_kg=Decimal("2.50"),
            rate_per_cbm=Decimal("150.00"),
            minimum_charge=Decimal("100.00"),
            transit_days=30,
        )
        result = pricing_service.create_freight_rate(request)

        assert result is not None
        assert result.origin == "Shanghai"
        assert result.destination == "Buenaventura"
        mock_repo.create.assert_called_once()

    @patch("app.services.pricing_service.freight_rate_repository")
    def test_create_freight_rate_failure(self, mock_repo, pricing_service):
        """Test freight rate creation failure."""
        mock_repo.create.return_value = None

        request = FreightRateCreateDTO(
            origin="Invalid",
            destination="Invalid",
        )
        result = pricing_service.create_freight_rate(request)

        assert result is None

    @patch("app.services.pricing_service.freight_rate_repository")
    def test_list_freight_rates_with_filters(
        self, mock_repo, pricing_service, sample_freight_rate_data
    ):
        """Test listing freight rates with origin/destination filters."""
        mock_repo.get_all.return_value = ([sample_freight_rate_data], 1)

        result = pricing_service.list_freight_rates(
            origin="Shanghai", destination="Buenaventura"
        )

        assert len(result.items) == 1
        assert result.pagination.total == 1
        mock_repo.get_all.assert_called_once_with(
            page=1, limit=20, origin="Shanghai", destination="Buenaventura"
        )

    @patch("app.services.pricing_service.freight_rate_repository")
    def test_list_freight_rates_empty(self, mock_repo, pricing_service):
        """Test listing freight rates when none exist."""
        mock_repo.get_all.return_value = ([], 0)

        result = pricing_service.list_freight_rates()

        assert result.items == []
        assert result.pagination.total == 0

    @patch("app.services.pricing_service.freight_rate_repository")
    def test_get_active_rate_found(
        self, mock_repo, pricing_service, sample_freight_rate_data
    ):
        """Test getting active rate for a route."""
        mock_repo.get_all.return_value = ([sample_freight_rate_data], 1)

        result = pricing_service.get_active_rate("Shanghai", "Buenaventura")

        assert result is not None
        assert result.origin == "Shanghai"
        assert result.destination == "Buenaventura"

    @patch("app.services.pricing_service.freight_rate_repository")
    def test_get_active_rate_not_found(self, mock_repo, pricing_service):
        """Test getting active rate when no route exists."""
        mock_repo.get_all.return_value = ([], 0)

        result = pricing_service.get_active_rate("Unknown", "Unknown")

        assert result is None

    @patch("app.services.pricing_service.freight_rate_repository")
    def test_get_active_rate_expired(self, mock_repo, pricing_service):
        """Test that expired rates are not returned as active."""
        expired_rate = create_sample_freight_rate(
            valid_until=date.today() - timedelta(days=1)
        )
        mock_repo.get_all.return_value = ([expired_rate], 1)

        result = pricing_service.get_active_rate("Shanghai", "Buenaventura")

        assert result is None

    @patch("app.services.pricing_service.freight_rate_repository")
    def test_get_active_rate_with_null_dates(self, mock_repo, pricing_service):
        """Test getting active rate when valid_from and valid_until are None."""
        rate_no_dates = {
            "id": uuid4(),
            "origin": "Shanghai",
            "destination": "Bogota",
            "incoterm": "FOB",
            "rate_per_kg": Decimal("3.00"),
            "rate_per_cbm": Decimal("180.00"),
            "minimum_charge": Decimal("120.00"),
            "transit_days": 35,
            "is_active": True,
            "valid_from": None,
            "valid_until": None,
            "notes": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        mock_repo.get_all.return_value = ([rate_no_dates], 1)

        result = pricing_service.get_active_rate("Shanghai", "Bogota")

        assert result is not None
        assert result.origin == "Shanghai"

    @patch("app.services.pricing_service.freight_rate_repository")
    def test_update_freight_rate_success(
        self, mock_repo, pricing_service, sample_freight_rate_data
    ):
        """Test updating a freight rate."""
        updated_rate = sample_freight_rate_data.copy()
        updated_rate["rate_per_kg"] = Decimal("3.00")
        mock_repo.get_by_id.return_value = sample_freight_rate_data
        mock_repo.update.return_value = updated_rate

        request = FreightRateUpdateDTO(rate_per_kg=Decimal("3.00"))
        result = pricing_service.update_freight_rate(sample_freight_rate_data["id"], request)

        assert result is not None
        assert result.rate_per_kg == Decimal("3.00")

    @patch("app.services.pricing_service.freight_rate_repository")
    def test_update_freight_rate_not_found(self, mock_repo, pricing_service):
        """Test updating a non-existent freight rate."""
        mock_repo.get_by_id.return_value = None

        request = FreightRateUpdateDTO(rate_per_kg=Decimal("3.00"))
        result = pricing_service.update_freight_rate(uuid4(), request)

        assert result is None
        mock_repo.update.assert_not_called()


# =============================================================================
# EXPIRED RATE DETECTION TESTS
# =============================================================================


class TestExpiredRateDetection:
    """Tests for detecting expired freight rates."""

    @patch("app.services.pricing_service.freight_rate_repository")
    def test_check_expired_rates(self, mock_repo, pricing_service):
        """Test checking for expired rates."""
        valid_rate = create_sample_freight_rate(
            valid_until=date.today() + timedelta(days=60)
        )
        expired_rate = create_sample_freight_rate(
            origin="Ningbo",
            valid_until=date.today() - timedelta(days=1)
        )
        mock_repo.get_all.return_value = ([valid_rate, expired_rate], 2)

        result = pricing_service.check_expired_rates()

        assert len(result) == 1
        assert result[0].origin == "Ningbo"

    @patch("app.services.pricing_service.freight_rate_repository")
    def test_check_expired_rates_none_expired(
        self, mock_repo, pricing_service, sample_freight_rate_data
    ):
        """Test checking for expired rates when none are expired."""
        mock_repo.get_all.return_value = ([sample_freight_rate_data], 1)

        result = pricing_service.check_expired_rates()

        assert len(result) == 0


# =============================================================================
# PRICING SETTINGS TESTS
# =============================================================================


class TestPricingSettings:
    """Tests for pricing settings operations."""

    @patch("app.services.pricing_service.pricing_settings_repository")
    def test_get_setting_found(self, mock_repo, pricing_service):
        """Test getting a setting that exists."""
        mock_setting = {
            "id": uuid4(),
            "setting_key": "default_margin_percentage",
            "setting_value": Decimal("20.0"),
            "description": "Default profit margin percentage",
            "is_percentage": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        mock_repo.get_by_key.return_value = mock_setting

        result = pricing_service.get_setting("default_margin_percentage")

        assert result == Decimal("20.0")

    @patch("app.services.pricing_service.pricing_settings_repository")
    def test_get_setting_not_found(self, mock_repo, pricing_service):
        """Test getting a setting that doesn't exist."""
        mock_repo.get_by_key.return_value = None

        result = pricing_service.get_setting("nonexistent_key")

        assert result is None

    @patch("app.services.pricing_service.pricing_settings_repository")
    def test_update_setting_success(self, mock_repo, pricing_service):
        """Test updating a setting."""
        existing = {
            "id": uuid4(),
            "setting_key": "default_margin_percentage",
            "setting_value": Decimal("20.0"),
            "description": "Default profit margin percentage",
            "is_percentage": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        updated = existing.copy()
        updated["setting_value"] = Decimal("25.0")
        mock_repo.get_by_key.return_value = existing
        mock_repo.update.return_value = updated

        result = pricing_service.update_setting(
            "default_margin_percentage", Decimal("25.0")
        )

        assert result is not None
        assert result.setting_value == Decimal("25.0")

    @patch("app.services.pricing_service.pricing_settings_repository")
    def test_update_setting_not_found(self, mock_repo, pricing_service):
        """Test updating a non-existent setting."""
        mock_repo.get_by_key.return_value = None

        result = pricing_service.update_setting("nonexistent_key", Decimal("10.0"))

        assert result is None
        mock_repo.update.assert_not_called()

    @patch("app.services.pricing_service.pricing_settings_repository")
    def test_get_all_settings(self, mock_repo, pricing_service):
        """Test getting all settings."""
        settings_list = [
            {
                "id": uuid4(),
                "setting_key": "default_margin_percentage",
                "setting_value": Decimal("20.0"),
                "description": "Default profit margin percentage",
                "is_percentage": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
            {
                "id": uuid4(),
                "setting_key": "insurance_percentage",
                "setting_value": Decimal("1.5"),
                "description": "Insurance rate",
                "is_percentage": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
        ]
        mock_repo.get_all.return_value = settings_list

        result = pricing_service.get_all_settings()

        assert len(result) == 2
        assert result["default_margin_percentage"] == Decimal("20.0")
        assert result["insurance_percentage"] == Decimal("1.5")

    @patch("app.services.pricing_service.pricing_settings_repository")
    def test_get_all_settings_empty(self, mock_repo, pricing_service):
        """Test getting all settings when none exist."""
        mock_repo.get_all.return_value = []

        result = pricing_service.get_all_settings()

        assert result == {}


# =============================================================================
# INITIALIZE DEFAULT SETTINGS TESTS
# =============================================================================


class TestInitializeDefaultSettings:
    """Tests for initializing default pricing settings."""

    @patch("app.services.pricing_service.pricing_settings_repository")
    def test_initialize_default_settings(self, mock_repo, pricing_service):
        """Test initializing default settings."""
        mock_repo.get_by_key.return_value = None
        mock_repo.create.return_value = {
            "id": uuid4(),
            "setting_key": "test",
            "setting_value": Decimal("0"),
            "description": "test",
            "is_percentage": False,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        result = pricing_service.initialize_default_settings()

        assert result == len(DEFAULT_PRICING_SETTINGS)
        assert mock_repo.create.call_count == len(DEFAULT_PRICING_SETTINGS)

    @patch("app.services.pricing_service.pricing_settings_repository")
    def test_initialize_default_settings_partial(self, mock_repo, pricing_service):
        """Test initializing when some settings already exist."""
        existing_setting = {
            "id": uuid4(),
            "setting_key": "default_margin_percentage",
            "setting_value": Decimal("20.0"),
            "description": "Default profit margin percentage",
            "is_percentage": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        def get_by_key_side_effect(key):
            if key == "default_margin_percentage":
                return existing_setting
            return None

        mock_repo.get_by_key.side_effect = get_by_key_side_effect
        mock_repo.create.return_value = {
            "id": uuid4(),
            "setting_key": "test",
            "setting_value": Decimal("0"),
            "description": "test",
            "is_percentage": False,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        result = pricing_service.initialize_default_settings()

        assert result == len(DEFAULT_PRICING_SETTINGS) - 1

    @patch("app.services.pricing_service.pricing_settings_repository")
    def test_initialize_default_settings_all_exist(self, mock_repo, pricing_service):
        """Test initializing when all settings already exist."""
        existing_setting = {
            "id": uuid4(),
            "setting_key": "test",
            "setting_value": Decimal("0"),
            "description": "test",
            "is_percentage": False,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        mock_repo.get_by_key.return_value = existing_setting

        result = pricing_service.initialize_default_settings()

        assert result == 0
        mock_repo.create.assert_not_called()

    @patch("app.services.pricing_service.pricing_settings_repository")
    def test_create_setting_success(self, mock_repo, pricing_service):
        """Test creating a new setting."""
        new_setting = {
            "id": uuid4(),
            "setting_key": "default_margin_percentage",
            "setting_value": Decimal("20.0"),
            "description": "Default profit margin percentage",
            "is_percentage": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        mock_repo.create.return_value = new_setting

        request = PricingSettingCreateDTO(
            setting_key="default_margin_percentage",
            setting_value=Decimal("20.0"),
            description="Default profit margin percentage",
            is_percentage=True,
        )
        result = pricing_service.create_setting(request)

        assert result is not None
        assert result.setting_key == "default_margin_percentage"
        mock_repo.create.assert_called_once()

    @patch("app.services.pricing_service.pricing_settings_repository")
    def test_create_setting_failure(self, mock_repo, pricing_service):
        """Test setting creation failure."""
        mock_repo.create.return_value = None

        request = PricingSettingCreateDTO(
            setting_key="failed_setting",
            setting_value=Decimal("0"),
        )
        result = pricing_service.create_setting(request)

        assert result is None


# =============================================================================
# PAGINATION TESTS
# =============================================================================


class TestPagination:
    """Tests for pagination logic."""

    @patch("app.services.pricing_service.hs_code_repository")
    def test_list_hs_codes_pagination_first_page(self, mock_repo, pricing_service):
        """Test pagination on first page."""
        hs_codes = [create_sample_hs_code() for _ in range(3)]
        mock_repo.get_all.return_value = (hs_codes, 3)

        result = pricing_service.list_hs_codes(page=1, limit=10)

        assert result.pagination.page == 1
        assert result.pagination.limit == 10
        assert result.pagination.total == 3
        assert result.pagination.pages == 1

    @patch("app.services.pricing_service.hs_code_repository")
    def test_list_hs_codes_pagination_multiple_pages(self, mock_repo, pricing_service):
        """Test pagination with multiple pages."""
        mock_repo.get_all.return_value = ([], 25)

        result = pricing_service.list_hs_codes(page=2, limit=10)

        assert result.pagination.page == 2
        assert result.pagination.total == 25
        assert result.pagination.pages == 3

    @patch("app.services.pricing_service.freight_rate_repository")
    def test_list_freight_rates_pagination(
        self, mock_repo, pricing_service, sample_freight_rate_data
    ):
        """Test freight rate pagination."""
        mock_repo.get_all.return_value = ([sample_freight_rate_data], 50)

        result = pricing_service.list_freight_rates(page=3, limit=20)

        assert result.pagination.page == 3
        assert result.pagination.total == 50
        assert result.pagination.pages == 3
