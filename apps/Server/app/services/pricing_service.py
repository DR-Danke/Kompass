"""Pricing configuration service for managing HS codes, freight rates, and settings."""

from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID

from app.models.kompass_dto import (
    FreightRateCreateDTO,
    FreightRateListResponseDTO,
    FreightRateResponseDTO,
    FreightRateUpdateDTO,
    HSCodeCreateDTO,
    HSCodeListResponseDTO,
    HSCodeResponseDTO,
    HSCodeUpdateDTO,
    PaginationDTO,
    PricingSettingCreateDTO,
    PricingSettingResponseDTO,
)
from app.repository.kompass_repository import (
    freight_rate_repository,
    hs_code_repository,
    pricing_settings_repository,
)


# Default pricing settings to seed on first access
DEFAULT_PRICING_SETTINGS = {
    "default_margin_percentage": {
        "value": Decimal("20.0"),
        "description": "Default profit margin percentage",
        "is_percentage": True,
    },
    "inspection_cost_usd": {
        "value": Decimal("150.0"),
        "description": "Standard inspection cost in USD",
        "is_percentage": False,
    },
    "insurance_percentage": {
        "value": Decimal("1.5"),
        "description": "Insurance rate as percentage of CIF value",
        "is_percentage": True,
    },
    "nationalization_cost_cop": {
        "value": Decimal("200000.0"),
        "description": "Nationalization cost in Colombian Pesos",
        "is_percentage": False,
    },
    "exchange_rate_usd_cop": {
        "value": Decimal("4200.0"),
        "description": "USD to COP exchange rate",
        "is_percentage": False,
    },
}


class PricingService:
    """Handles pricing configuration for HS codes, freight rates, and settings."""

    # =========================================================================
    # HS CODE METHODS
    # =========================================================================

    def create_hs_code(self, request: HSCodeCreateDTO) -> Optional[HSCodeResponseDTO]:
        """Create a new HS code.

        Args:
            request: HS code creation data

        Returns:
            Created HS code DTO or None if creation failed
        """
        result = hs_code_repository.create(
            code=request.code,
            description=request.description,
            duty_rate=request.duty_rate,
            notes=request.notes,
        )

        if result:
            print(f"INFO [PricingService]: Created HS code {request.code}")
            return HSCodeResponseDTO(**result)
        print(f"ERROR [PricingService]: Failed to create HS code {request.code}")
        return None

    def get_hs_code(self, hs_code_id: UUID) -> Optional[HSCodeResponseDTO]:
        """Get HS code by ID.

        Args:
            hs_code_id: UUID of the HS code

        Returns:
            HS code DTO or None if not found
        """
        result = hs_code_repository.get_by_id(hs_code_id)
        if result:
            return HSCodeResponseDTO(**result)
        return None

    def list_hs_codes(
        self,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> HSCodeListResponseDTO:
        """List HS codes with search and pagination.

        Args:
            search: Optional search term for code or description
            page: Page number (1-indexed)
            limit: Items per page

        Returns:
            Paginated list of HS codes
        """
        items, total = hs_code_repository.get_all(
            page=page,
            limit=limit,
            search=search,
        )

        pages = (total + limit - 1) // limit if limit > 0 else 0

        return HSCodeListResponseDTO(
            items=[HSCodeResponseDTO(**item) for item in items],
            pagination=PaginationDTO(
                page=page,
                limit=limit,
                total=total,
                pages=pages,
            ),
        )

    def update_hs_code(
        self, hs_code_id: UUID, request: HSCodeUpdateDTO
    ) -> Optional[HSCodeResponseDTO]:
        """Update an existing HS code.

        Args:
            hs_code_id: UUID of the HS code to update
            request: Update data

        Returns:
            Updated HS code DTO or None if update failed
        """
        existing = hs_code_repository.get_by_id(hs_code_id)
        if not existing:
            print(f"WARN [PricingService]: HS code not found: {hs_code_id}")
            return None

        result = hs_code_repository.update(
            hs_code_id=hs_code_id,
            code=request.code,
            description=request.description,
            duty_rate=request.duty_rate,
            notes=request.notes,
        )

        if result:
            print(f"INFO [PricingService]: Updated HS code {hs_code_id}")
            return HSCodeResponseDTO(**result)
        return None

    def get_tariff_rate(self, hs_code: str) -> Optional[Decimal]:
        """Get the duty/tariff rate for a specific HS code string.

        Args:
            hs_code: The HS code string to look up

        Returns:
            Duty rate as Decimal or None if code not found
        """
        result = hs_code_repository.get_by_code(hs_code)
        if result:
            return result.get("duty_rate")
        return None

    def search_hs_codes(self, query: str) -> List[HSCodeResponseDTO]:
        """Search HS codes by code or description.

        Args:
            query: Search query string

        Returns:
            List of matching HS codes (max 50 results)
        """
        if not query or not query.strip():
            return []

        items, _ = hs_code_repository.get_all(
            page=1,
            limit=50,
            search=query.strip(),
        )

        return [HSCodeResponseDTO(**item) for item in items]

    # =========================================================================
    # FREIGHT RATE METHODS
    # =========================================================================

    def create_freight_rate(
        self, request: FreightRateCreateDTO
    ) -> Optional[FreightRateResponseDTO]:
        """Create a new freight rate.

        Args:
            request: Freight rate creation data

        Returns:
            Created freight rate DTO or None if creation failed
        """
        result = freight_rate_repository.create(
            origin=request.origin,
            destination=request.destination,
            incoterm=request.incoterm.value,
            rate_per_kg=request.rate_per_kg,
            rate_per_cbm=request.rate_per_cbm,
            minimum_charge=request.minimum_charge,
            transit_days=request.transit_days,
            is_active=request.is_active,
            valid_from=str(request.valid_from) if request.valid_from else None,
            valid_until=str(request.valid_until) if request.valid_until else None,
            notes=request.notes,
        )

        if result:
            print(
                f"INFO [PricingService]: Created freight rate "
                f"{request.origin} -> {request.destination}"
            )
            return FreightRateResponseDTO(**result)
        print(
            f"ERROR [PricingService]: Failed to create freight rate "
            f"{request.origin} -> {request.destination}"
        )
        return None

    def list_freight_rates(
        self,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> FreightRateListResponseDTO:
        """List freight rates with origin/destination filtering.

        Args:
            origin: Optional origin filter
            destination: Optional destination filter
            page: Page number (1-indexed)
            limit: Items per page

        Returns:
            Paginated list of freight rates
        """
        items, total = freight_rate_repository.get_all(
            page=page,
            limit=limit,
            origin=origin,
            destination=destination,
        )

        pages = (total + limit - 1) // limit if limit > 0 else 0

        return FreightRateListResponseDTO(
            items=[FreightRateResponseDTO(**item) for item in items],
            pagination=PaginationDTO(
                page=page,
                limit=limit,
                total=total,
                pages=pages,
            ),
        )

    def get_active_rate(
        self,
        origin: str,
        destination: str,
        container_type: Optional[str] = None,
    ) -> Optional[FreightRateResponseDTO]:
        """Get currently active freight rate for a route.

        Finds an active freight rate matching origin/destination where:
        - is_active is True
        - valid_from is None or <= today
        - valid_until is None or >= today

        Args:
            origin: Origin location
            destination: Destination location
            container_type: Optional container type filter (reserved for future use)

        Returns:
            Active freight rate DTO or None if no active rate found
        """
        items, _ = freight_rate_repository.get_all(
            page=1,
            limit=100,
            origin=origin,
            destination=destination,
            is_active=True,
        )

        today = date.today()

        for item in items:
            valid_from = item.get("valid_from")
            valid_until = item.get("valid_until")

            # Check if rate is valid for today's date
            from_valid = valid_from is None or valid_from <= today
            until_valid = valid_until is None or valid_until >= today

            if from_valid and until_valid:
                return FreightRateResponseDTO(**item)

        return None

    def update_freight_rate(
        self, rate_id: UUID, request: FreightRateUpdateDTO
    ) -> Optional[FreightRateResponseDTO]:
        """Update an existing freight rate.

        Args:
            rate_id: UUID of the freight rate to update
            request: Update data

        Returns:
            Updated freight rate DTO or None if update failed
        """
        existing = freight_rate_repository.get_by_id(rate_id)
        if not existing:
            print(f"WARN [PricingService]: Freight rate not found: {rate_id}")
            return None

        result = freight_rate_repository.update(
            freight_rate_id=rate_id,
            origin=request.origin,
            destination=request.destination,
            incoterm=request.incoterm.value if request.incoterm else None,
            rate_per_kg=request.rate_per_kg,
            rate_per_cbm=request.rate_per_cbm,
            minimum_charge=request.minimum_charge,
            transit_days=request.transit_days,
            is_active=request.is_active,
            valid_from=str(request.valid_from) if request.valid_from else None,
            valid_until=str(request.valid_until) if request.valid_until else None,
            notes=request.notes,
        )

        if result:
            print(f"INFO [PricingService]: Updated freight rate {rate_id}")
            return FreightRateResponseDTO(**result)
        return None

    def check_expired_rates(self) -> List[FreightRateResponseDTO]:
        """Get all freight rates with expired valid_until dates.

        Returns rates where:
        - is_active is True
        - valid_until is not None and valid_until < today

        Returns:
            List of expired freight rates
        """
        items, _ = freight_rate_repository.get_all(
            page=1,
            limit=1000,
            is_active=True,
        )

        today = date.today()
        expired = []

        for item in items:
            valid_until = item.get("valid_until")
            if valid_until is not None and valid_until < today:
                expired.append(FreightRateResponseDTO(**item))

        if expired:
            print(f"WARN [PricingService]: Found {len(expired)} expired freight rates")

        return expired

    # =========================================================================
    # PRICING SETTINGS METHODS
    # =========================================================================

    def get_setting(self, key: str) -> Optional[Decimal]:
        """Get a single pricing setting value by key.

        Args:
            key: Setting key name

        Returns:
            Setting value as Decimal or None if not found
        """
        result = pricing_settings_repository.get_by_key(key)
        if result:
            return result.get("setting_value")
        return None

    def update_setting(
        self, key: str, value: Decimal, updated_by: Optional[UUID] = None
    ) -> Optional[PricingSettingResponseDTO]:
        """Update a pricing setting value.

        Args:
            key: Setting key name
            value: New setting value
            updated_by: UUID of user making the update (for audit trail)

        Returns:
            Updated setting DTO or None if setting not found
        """
        existing = pricing_settings_repository.get_by_key(key)
        if not existing:
            print(f"WARN [PricingService]: Setting not found: {key}")
            return None

        result = pricing_settings_repository.update(
            setting_key=key,
            setting_value=value,
        )

        if result:
            print(f"INFO [PricingService]: Updated setting {key} = {value}")
            return PricingSettingResponseDTO(**result)
        return None

    def get_all_settings(self) -> Dict[str, Decimal]:
        """Get all pricing settings as a key-value dictionary.

        Returns:
            Dictionary mapping setting keys to their Decimal values
        """
        items = pricing_settings_repository.get_all()
        return {item["setting_key"]: item["setting_value"] for item in items}

    def initialize_default_settings(self) -> int:
        """Initialize default pricing settings if they don't exist.

        Seeds the pricing_settings table with DEFAULT_PRICING_SETTINGS
        for any keys that are not already present.

        Returns:
            Number of settings created
        """
        created_count = 0

        for key, config in DEFAULT_PRICING_SETTINGS.items():
            existing = pricing_settings_repository.get_by_key(key)
            if existing is None:
                result = pricing_settings_repository.create(
                    setting_key=key,
                    setting_value=config["value"],
                    description=config["description"],
                    is_percentage=config["is_percentage"],
                )
                if result:
                    created_count += 1
                    print(
                        f"INFO [PricingService]: Created default setting "
                        f"{key} = {config['value']}"
                    )

        if created_count > 0:
            print(
                f"INFO [PricingService]: Initialized {created_count} default settings"
            )

        return created_count

    def create_setting(
        self, request: PricingSettingCreateDTO
    ) -> Optional[PricingSettingResponseDTO]:
        """Create a new pricing setting.

        Args:
            request: Pricing setting creation data

        Returns:
            Created setting DTO or None if creation failed
        """
        result = pricing_settings_repository.create(
            setting_key=request.setting_key,
            setting_value=request.setting_value,
            description=request.description,
            is_percentage=request.is_percentage,
        )

        if result:
            print(f"INFO [PricingService]: Created setting {request.setting_key}")
            return PricingSettingResponseDTO(**result)
        print(f"ERROR [PricingService]: Failed to create setting {request.setting_key}")
        return None


# Singleton instance
pricing_service = PricingService()
