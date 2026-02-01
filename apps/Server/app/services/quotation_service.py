"""Quotation service for managing quotations with integrated pricing engine.

This service provides business logic for managing quotations throughout their lifecycle,
including CRUD operations, pricing calculations, line item management, status workflow
transitions, and quotation cloning functionality.
"""

import math
from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID

from app.models.kompass_dto import (
    Incoterm,
    PaginationDTO,
    QuotationCloneDTO,
    QuotationCreateDTO,
    QuotationFilterDTO,
    QuotationItemCreateDTO,
    QuotationItemResponseDTO,
    QuotationItemUpdateDTO,
    QuotationListResponseDTO,
    QuotationPricingDTO,
    QuotationResponseDTO,
    QuotationStatus,
    QuotationStatusTransitionDTO,
    QuotationUpdateDTO,
)
from app.repository.kompass_repository import quotation_repository
from app.services.pricing_service import pricing_service


# Valid status transitions map
# Key: current status, Value: list of valid next statuses
STATUS_TRANSITIONS: Dict[str, List[str]] = {
    "draft": ["sent"],
    "sent": ["viewed", "accepted", "rejected", "expired"],
    "viewed": ["negotiating", "accepted", "rejected", "expired"],
    "negotiating": ["accepted", "rejected", "expired"],
    "accepted": ["expired"],
    "rejected": ["expired"],
    "expired": [],
}


class QuotationService:
    """Handles quotation business logic including pricing calculations."""

    def __init__(self, repository=None):
        """Initialize service with optional repository injection for testing."""
        self.repository = repository or quotation_repository

    # =========================================================================
    # CRUD OPERATIONS
    # =========================================================================

    def create_quotation(
        self, request: QuotationCreateDTO, created_by: UUID
    ) -> Optional[QuotationResponseDTO]:
        """Create a new quotation with optional initial items.

        Args:
            request: Quotation creation data
            created_by: UUID of the user creating the quotation

        Returns:
            Created quotation response or None if creation failed
        """
        # Create the quotation
        result = self.repository.create(
            client_id=request.client_id,
            quotation_number=request.quotation_number,
            status=request.status.value,
            incoterm=request.incoterm.value,
            currency=request.currency,
            freight_cost=request.freight_cost,
            insurance_cost=request.insurance_cost,
            other_costs=request.other_costs,
            discount_percent=request.discount_percent,
            notes=request.notes,
            terms_and_conditions=request.terms_and_conditions,
            valid_from=str(request.valid_from) if request.valid_from else None,
            valid_until=str(request.valid_until) if request.valid_until else None,
            created_by=created_by,
        )

        if not result:
            print("ERROR [QuotationService]: Failed to create quotation")
            return None

        quotation_id = result["id"]
        print(f"INFO [QuotationService]: Created quotation {result['quotation_number']}")

        # Add initial items if provided
        if request.items:
            for item in request.items:
                self.add_item(quotation_id, item)

            # Refresh quotation data after adding items
            result = self.repository.get_by_id(quotation_id)

        return self._map_to_response_dto(result) if result else None

    def get_quotation(self, quotation_id: UUID) -> Optional[QuotationResponseDTO]:
        """Get a quotation by ID.

        Args:
            quotation_id: UUID of the quotation

        Returns:
            Quotation response or None if not found
        """
        result = self.repository.get_by_id(quotation_id)

        if not result:
            print(f"INFO [QuotationService]: Quotation {quotation_id} not found")
            return None

        print(f"INFO [QuotationService]: Retrieved quotation {quotation_id}")
        return self._map_to_response_dto(result)

    def list_quotations(
        self,
        filters: Optional[QuotationFilterDTO] = None,
        page: int = 1,
        limit: int = 20,
    ) -> QuotationListResponseDTO:
        """List quotations with filtering and pagination.

        Args:
            filters: Optional filter parameters
            page: Page number (1-indexed)
            limit: Items per page

        Returns:
            Paginated list of quotations
        """
        # Extract filter values
        client_id = filters.client_id if filters else None
        status = filters.status.value if filters and filters.status else None
        created_by = filters.created_by if filters else None
        date_from = str(filters.date_from) if filters and filters.date_from else None
        date_to = str(filters.date_to) if filters and filters.date_to else None
        search = filters.search if filters else None

        items, total = self.repository.get_all(
            page=page,
            limit=limit,
            client_id=client_id,
            status=status,
            created_by=created_by,
            date_from=date_from,
            date_to=date_to,
            search=search,
        )

        pages = math.ceil(total / limit) if total > 0 else 0
        quotation_responses = [self._map_to_response_dto(item) for item in items]

        print(
            f"INFO [QuotationService]: Listed {len(quotation_responses)} quotations "
            f"(page {page}/{pages})"
        )

        return QuotationListResponseDTO(
            items=quotation_responses,
            pagination=PaginationDTO(
                page=page,
                limit=limit,
                total=total,
                pages=pages,
            ),
            filters=filters,
        )

    def update_quotation(
        self, quotation_id: UUID, request: QuotationUpdateDTO
    ) -> Optional[QuotationResponseDTO]:
        """Update a quotation.

        Args:
            quotation_id: UUID of the quotation to update
            request: Update data

        Returns:
            Updated quotation response or None if not found
        """
        # Check if quotation exists
        existing = self.repository.get_by_id(quotation_id)
        if not existing:
            return None

        # Build update kwargs
        update_kwargs: Dict = {}
        if request.status is not None:
            update_kwargs["status"] = request.status.value
        if request.incoterm is not None:
            update_kwargs["incoterm"] = request.incoterm.value
        if request.currency is not None:
            update_kwargs["currency"] = request.currency
        if request.freight_cost is not None:
            update_kwargs["freight_cost"] = request.freight_cost
        if request.insurance_cost is not None:
            update_kwargs["insurance_cost"] = request.insurance_cost
        if request.other_costs is not None:
            update_kwargs["other_costs"] = request.other_costs
        if request.discount_percent is not None:
            update_kwargs["discount_percent"] = request.discount_percent
        if request.notes is not None:
            update_kwargs["notes"] = request.notes
        if request.terms_and_conditions is not None:
            update_kwargs["terms_and_conditions"] = request.terms_and_conditions
        if request.valid_from is not None:
            update_kwargs["valid_from"] = str(request.valid_from)
        if request.valid_until is not None:
            update_kwargs["valid_until"] = str(request.valid_until)

        result = self._update_quotation_fields(quotation_id, update_kwargs)

        if result:
            # Recalculate totals if costs changed
            if any(
                k in update_kwargs
                for k in ["freight_cost", "insurance_cost", "other_costs", "discount_percent"]
            ):
                result = self.repository.recalculate_totals(quotation_id)

            print(f"INFO [QuotationService]: Updated quotation {quotation_id}")
            return self._map_to_response_dto(result) if result else None

        print(f"ERROR [QuotationService]: Failed to update quotation {quotation_id}")
        return None

    def delete_quotation(self, quotation_id: UUID) -> bool:
        """Delete a quotation.

        Args:
            quotation_id: UUID of the quotation to delete

        Returns:
            True if deleted, False if not found
        """
        existing = self.repository.get_by_id(quotation_id)
        if not existing:
            return False

        success = self._delete_quotation(quotation_id)

        if success:
            print(f"INFO [QuotationService]: Deleted quotation {quotation_id}")
        else:
            print(f"ERROR [QuotationService]: Failed to delete quotation {quotation_id}")

        return success

    def clone_quotation(
        self, quotation_id: UUID, created_by: UUID, clone_request: Optional[QuotationCloneDTO] = None
    ) -> Optional[QuotationResponseDTO]:
        """Clone a quotation creating a new version.

        Creates a copy of the quotation with:
        - New quotation number
        - Status set to draft
        - New created_by
        - All line items copied

        Args:
            quotation_id: UUID of the quotation to clone
            created_by: UUID of the user creating the clone
            clone_request: Optional clone parameters

        Returns:
            Cloned quotation response or None if source not found
        """
        # Get source quotation
        source = self.repository.get_by_id(quotation_id)
        if not source:
            print(f"WARN [QuotationService]: Quotation {quotation_id} not found for cloning")
            return None

        # Create new quotation with cloned data
        notes = clone_request.notes if clone_request and clone_request.notes else source.get("notes")
        if notes:
            notes = f"Cloned from {source['quotation_number']}. {notes}"
        else:
            notes = f"Cloned from {source['quotation_number']}"

        result = self.repository.create(
            client_id=source["client_id"],
            quotation_number=None,  # Auto-generate new number
            status="draft",
            incoterm=source["incoterm"],
            currency=source["currency"],
            freight_cost=source["freight_cost"],
            insurance_cost=source["insurance_cost"],
            other_costs=source["other_costs"],
            discount_percent=source["discount_percent"],
            notes=notes,
            terms_and_conditions=source.get("terms_and_conditions"),
            valid_from=None,  # Reset validity dates
            valid_until=None,
            created_by=created_by,
        )

        if not result:
            print(f"ERROR [QuotationService]: Failed to clone quotation {quotation_id}")
            return None

        new_quotation_id = result["id"]

        # Clone items
        for item in source.get("items", []):
            self.repository.add_item(
                quotation_id=new_quotation_id,
                product_name=item["product_name"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                product_id=item.get("product_id"),
                sku=item.get("sku"),
                description=item.get("description"),
                unit_of_measure=item.get("unit_of_measure", "piece"),
                unit_cost=item.get("unit_cost", Decimal("0.00")),
                markup_percent=item.get("markup_percent", Decimal("0.00")),
                tariff_percent=item.get("tariff_percent", Decimal("0.00")),
                tariff_amount=item.get("tariff_amount", Decimal("0.00")),
                freight_amount=item.get("freight_amount", Decimal("0.00")),
                sort_order=item.get("sort_order", 0),
                notes=item.get("notes"),
            )

        # Get final result with items
        result = self.repository.get_by_id(new_quotation_id)

        print(
            f"INFO [QuotationService]: Cloned quotation {source['quotation_number']} "
            f"to {result['quotation_number']}"
        )

        return self._map_to_response_dto(result) if result else None

    # =========================================================================
    # PRICING ENGINE
    # =========================================================================

    def calculate_pricing(self, quotation_id: UUID) -> Optional[QuotationPricingDTO]:
        """Calculate comprehensive pricing for a quotation.

        Implements the formula:
        Total COP = (FOB + Tariffs + Int'l Freight + Inspection + Insurance) × Exchange Rate
                    + National Freight COP + Nationalization COP + Margin

        Args:
            quotation_id: UUID of the quotation

        Returns:
            Pricing calculation results or None if quotation not found
        """
        # Get quotation with items
        quotation = self.repository.get_by_id(quotation_id)
        if not quotation:
            print(f"WARN [QuotationService]: Quotation {quotation_id} not found for pricing")
            return None

        items = quotation.get("items", [])

        # Get pricing settings
        settings = pricing_service.get_all_settings()

        # Initialize default settings if needed
        if not settings:
            pricing_service.initialize_default_settings()
            settings = pricing_service.get_all_settings()

        exchange_rate = settings.get("exchange_rate_usd_cop", Decimal("4200.0"))
        margin_percentage = settings.get("default_margin_percentage", Decimal("20.0"))
        insurance_percentage = settings.get("insurance_percentage", Decimal("1.5"))
        inspection_cost_usd = settings.get("inspection_cost_usd", Decimal("150.0"))
        nationalization_cost_cop = settings.get("nationalization_cost_cop", Decimal("200000.0"))

        # Calculate subtotal FOB (sum of line items)
        subtotal_fob_usd = Decimal("0.00")
        tariff_total_usd = Decimal("0.00")

        for item in items:
            line_fob = Decimal(str(item.get("unit_price", 0))) * Decimal(str(item.get("quantity", 0)))
            subtotal_fob_usd += line_fob

            # Calculate tariff for this item
            tariff_percent = Decimal(str(item.get("tariff_percent", 0)))
            tariff_total_usd += line_fob * tariff_percent / Decimal("100")

        # Get freight rates (international)
        # Use quotation's freight_cost if set, otherwise calculate from settings
        freight_intl_usd = Decimal(str(quotation.get("freight_cost", 0)))

        # Calculate insurance (percentage of FOB + Freight)
        insurance_base = subtotal_fob_usd + freight_intl_usd
        insurance_usd = insurance_base * insurance_percentage / Decimal("100")

        # Use quotation's insurance_cost if explicitly set, otherwise use calculated
        if quotation.get("insurance_cost", Decimal("0.00")) > Decimal("0.00"):
            insurance_usd = Decimal(str(quotation.get("insurance_cost", 0)))

        # Inspection cost (from settings)
        inspection_usd = inspection_cost_usd

        # Calculate USD subtotal
        subtotal_usd = (
            subtotal_fob_usd
            + tariff_total_usd
            + freight_intl_usd
            + inspection_usd
            + insurance_usd
        )

        # Convert to COP
        subtotal_cop = subtotal_usd * exchange_rate

        # Add national freight (from other_costs or default)
        freight_national_cop = Decimal(str(quotation.get("other_costs", 0)))

        # Add nationalization cost
        nationalization_cop = nationalization_cost_cop

        # Calculate subtotal before margin
        subtotal_before_margin_cop = subtotal_cop + freight_national_cop + nationalization_cop

        # Apply margin
        margin_cop = subtotal_before_margin_cop * margin_percentage / Decimal("100")

        # Calculate final total
        total_cop = subtotal_before_margin_cop + margin_cop

        print(
            f"INFO [QuotationService]: Calculated pricing for quotation {quotation_id}: "
            f"FOB={subtotal_fob_usd} USD, Total={total_cop} COP"
        )

        return QuotationPricingDTO(
            quotation_id=quotation_id,
            subtotal_fob_usd=subtotal_fob_usd,
            tariff_total_usd=tariff_total_usd,
            freight_intl_usd=freight_intl_usd,
            freight_national_cop=freight_national_cop,
            inspection_usd=inspection_usd,
            insurance_usd=insurance_usd,
            nationalization_cop=nationalization_cop,
            subtotal_before_margin_cop=subtotal_before_margin_cop,
            margin_percentage=margin_percentage,
            margin_cop=margin_cop,
            total_cop=total_cop,
            exchange_rate=exchange_rate,
        )

    def recalculate_quotation(self, quotation_id: UUID) -> Optional[QuotationResponseDTO]:
        """Recalculate quotation totals based on line items.

        Args:
            quotation_id: UUID of the quotation

        Returns:
            Updated quotation or None if not found
        """
        result = self.repository.recalculate_totals(quotation_id)

        if result:
            print(f"INFO [QuotationService]: Recalculated totals for quotation {quotation_id}")
            return self._map_to_response_dto(result)

        return None

    # =========================================================================
    # LINE ITEM MANAGEMENT
    # =========================================================================

    def add_item(
        self, quotation_id: UUID, item: QuotationItemCreateDTO
    ) -> Optional[QuotationItemResponseDTO]:
        """Add a line item to a quotation.

        Args:
            quotation_id: UUID of the quotation
            item: Item creation data

        Returns:
            Created item response or None if quotation not found
        """
        # Verify quotation exists
        quotation = self.repository.get_by_id(quotation_id)
        if not quotation:
            print(f"WARN [QuotationService]: Quotation {quotation_id} not found for adding item")
            return None

        # Look up tariff rate if HS code is provided via product
        tariff_percent = item.tariff_percent

        result = self.repository.add_item(
            quotation_id=quotation_id,
            product_name=item.product_name,
            quantity=item.quantity,
            unit_price=item.unit_price,
            product_id=item.product_id,
            sku=item.sku,
            description=item.description,
            unit_of_measure=item.unit_of_measure,
            unit_cost=item.unit_cost,
            markup_percent=item.markup_percent,
            tariff_percent=tariff_percent,
            tariff_amount=item.tariff_amount,
            freight_amount=item.freight_amount,
            sort_order=item.sort_order,
            notes=item.notes,
        )

        if result:
            print(f"INFO [QuotationService]: Added item to quotation {quotation_id}")
            return self._map_to_item_response_dto(result)

        print(f"ERROR [QuotationService]: Failed to add item to quotation {quotation_id}")
        return None

    def update_item(
        self, item_id: UUID, request: QuotationItemUpdateDTO
    ) -> Optional[QuotationItemResponseDTO]:
        """Update a quotation line item.

        Args:
            item_id: UUID of the item to update
            request: Update data

        Returns:
            Updated item response or None if not found
        """
        result = self._update_quotation_item(item_id, request)

        if result:
            print(f"INFO [QuotationService]: Updated item {item_id}")
            return self._map_to_item_response_dto(result)

        print(f"ERROR [QuotationService]: Failed to update item {item_id}")
        return None

    def remove_item(self, item_id: UUID) -> bool:
        """Remove a line item from a quotation.

        Args:
            item_id: UUID of the item to remove

        Returns:
            True if removed, False if not found
        """
        success = self.repository.remove_item(item_id)

        if success:
            print(f"INFO [QuotationService]: Removed item {item_id}")
        else:
            print(f"WARN [QuotationService]: Item {item_id} not found for removal")

        return success

    # =========================================================================
    # STATUS WORKFLOW
    # =========================================================================

    def validate_status_transition(
        self, current_status: str, new_status: str
    ) -> bool:
        """Validate if a status transition is allowed.

        Args:
            current_status: Current quotation status
            new_status: Proposed new status

        Returns:
            True if transition is valid, False otherwise
        """
        valid_transitions = STATUS_TRANSITIONS.get(current_status, [])
        return new_status in valid_transitions

    def update_status(
        self, quotation_id: UUID, transition: QuotationStatusTransitionDTO
    ) -> Optional[QuotationResponseDTO]:
        """Update quotation status with validation.

        Args:
            quotation_id: UUID of the quotation
            transition: Status transition request

        Returns:
            Updated quotation or None if not found

        Raises:
            ValueError: If status transition is not valid
        """
        # Get current quotation
        quotation = self.repository.get_by_id(quotation_id)
        if not quotation:
            return None

        current_status = quotation["status"]
        new_status = transition.new_status.value

        # Validate transition
        if not self.validate_status_transition(current_status, new_status):
            print(
                f"WARN [QuotationService]: Invalid status transition "
                f"{current_status} -> {new_status} for quotation {quotation_id}"
            )
            raise ValueError(
                f"Invalid status transition from '{current_status}' to '{new_status}'. "
                f"Valid transitions: {STATUS_TRANSITIONS.get(current_status, [])}"
            )

        # Update status
        result = self.repository.update_status(quotation_id, new_status)

        if result:
            print(
                f"INFO [QuotationService]: Updated quotation {quotation_id} status "
                f"from {current_status} to {new_status}"
            )
            return self._map_to_response_dto(result)

        print(f"ERROR [QuotationService]: Failed to update status for quotation {quotation_id}")
        return None

    # =========================================================================
    # PRIVATE HELPER METHODS
    # =========================================================================

    def _update_quotation_fields(
        self, quotation_id: UUID, update_kwargs: Dict
    ) -> Optional[Dict]:
        """Update quotation fields via direct SQL.

        This is a temporary implementation until the repository has a proper update method.
        """
        from app.config.database import close_database_connection, get_database_connection

        if not update_kwargs:
            return self.repository.get_by_id(quotation_id)

        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                set_clauses = []
                params = []

                for key, value in update_kwargs.items():
                    set_clauses.append(f"{key} = %s")
                    params.append(value)

                params.append(str(quotation_id))

                cur.execute(
                    f"""
                    UPDATE quotations
                    SET {", ".join(set_clauses)}, updated_at = NOW()
                    WHERE id = %s
                    RETURNING id
                    """,
                    params,
                )
                conn.commit()
                row = cur.fetchone()

                if row:
                    return self.repository.get_by_id(quotation_id)
                return None
        except Exception as e:
            print(f"ERROR [QuotationService]: Failed to update quotation: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def _delete_quotation(self, quotation_id: UUID) -> bool:
        """Delete a quotation and its items."""
        from app.config.database import close_database_connection, get_database_connection

        conn = get_database_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cur:
                # Delete items first
                cur.execute(
                    "DELETE FROM quotation_items WHERE quotation_id = %s",
                    (str(quotation_id),),
                )
                # Delete quotation
                cur.execute(
                    "DELETE FROM quotations WHERE id = %s RETURNING id",
                    (str(quotation_id),),
                )
                conn.commit()
                return cur.fetchone() is not None
        except Exception as e:
            print(f"ERROR [QuotationService]: Failed to delete quotation: {e}")
            conn.rollback()
            return False
        finally:
            close_database_connection(conn)

    def _update_quotation_item(
        self, item_id: UUID, request: QuotationItemUpdateDTO
    ) -> Optional[Dict]:
        """Update a quotation item."""
        from app.config.database import close_database_connection, get_database_connection

        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                # First get the quotation_id for recalculation
                cur.execute(
                    "SELECT quotation_id FROM quotation_items WHERE id = %s",
                    (str(item_id),),
                )
                row = cur.fetchone()
                if not row:
                    return None

                quotation_id = row[0]

                # Build update
                update_kwargs: Dict = {}
                if request.product_id is not None:
                    update_kwargs["product_id"] = str(request.product_id) if request.product_id else None
                if request.sku is not None:
                    update_kwargs["sku"] = request.sku
                if request.product_name is not None:
                    update_kwargs["product_name"] = request.product_name
                if request.description is not None:
                    update_kwargs["description"] = request.description
                if request.quantity is not None:
                    update_kwargs["quantity"] = request.quantity
                if request.unit_of_measure is not None:
                    update_kwargs["unit_of_measure"] = request.unit_of_measure
                if request.unit_cost is not None:
                    update_kwargs["unit_cost"] = request.unit_cost
                if request.unit_price is not None:
                    update_kwargs["unit_price"] = request.unit_price
                if request.markup_percent is not None:
                    update_kwargs["markup_percent"] = request.markup_percent
                if request.tariff_percent is not None:
                    update_kwargs["tariff_percent"] = request.tariff_percent
                if request.tariff_amount is not None:
                    update_kwargs["tariff_amount"] = request.tariff_amount
                if request.freight_amount is not None:
                    update_kwargs["freight_amount"] = request.freight_amount
                if request.sort_order is not None:
                    update_kwargs["sort_order"] = request.sort_order
                if request.notes is not None:
                    update_kwargs["notes"] = request.notes

                if not update_kwargs:
                    # Nothing to update, return current item
                    cur.execute(
                        """
                        SELECT id, quotation_id, product_id, sku, product_name, description,
                               quantity, unit_of_measure, unit_cost, unit_price, markup_percent,
                               tariff_percent, tariff_amount, freight_amount, line_total,
                               sort_order, notes, created_at, updated_at
                        FROM quotation_items WHERE id = %s
                        """,
                        (str(item_id),),
                    )
                    row = cur.fetchone()
                    if row:
                        return self._item_row_to_dict(row)
                    return None

                # Calculate new line_total if quantity or prices changed
                cur.execute(
                    """
                    SELECT quantity, unit_price, tariff_amount, freight_amount
                    FROM quotation_items WHERE id = %s
                    """,
                    (str(item_id),),
                )
                current = cur.fetchone()
                if current:
                    quantity = update_kwargs.get("quantity", current[0])
                    unit_price = update_kwargs.get("unit_price", current[1])
                    tariff_amount = update_kwargs.get("tariff_amount", current[2])
                    freight_amount = update_kwargs.get("freight_amount", current[3])
                    line_total = quantity * unit_price + tariff_amount + freight_amount
                    update_kwargs["line_total"] = line_total

                set_clauses = []
                params = []
                for key, value in update_kwargs.items():
                    set_clauses.append(f"{key} = %s")
                    params.append(value)

                params.append(str(item_id))

                cur.execute(
                    f"""
                    UPDATE quotation_items
                    SET {", ".join(set_clauses)}, updated_at = NOW()
                    WHERE id = %s
                    RETURNING id, quotation_id, product_id, sku, product_name, description,
                              quantity, unit_of_measure, unit_cost, unit_price, markup_percent,
                              tariff_percent, tariff_amount, freight_amount, line_total,
                              sort_order, notes, created_at, updated_at
                    """,
                    params,
                )
                conn.commit()
                result_row = cur.fetchone()

                if result_row:
                    # Recalculate quotation totals
                    self.repository.recalculate_totals(quotation_id)
                    return self._item_row_to_dict(result_row)
                return None
        except Exception as e:
            print(f"ERROR [QuotationService]: Failed to update item: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def _item_row_to_dict(self, row: tuple) -> Dict:
        """Convert item row tuple to dictionary."""
        return {
            "id": row[0],
            "quotation_id": row[1],
            "product_id": row[2],
            "sku": row[3],
            "product_name": row[4],
            "description": row[5],
            "quantity": row[6],
            "unit_of_measure": row[7],
            "unit_cost": row[8],
            "unit_price": row[9],
            "markup_percent": row[10],
            "tariff_percent": row[11],
            "tariff_amount": row[12],
            "freight_amount": row[13],
            "line_total": row[14],
            "sort_order": row[15],
            "notes": row[16],
            "created_at": row[17],
            "updated_at": row[18],
        }

    def _map_to_response_dto(self, data: Dict) -> QuotationResponseDTO:
        """Map repository data to response DTO."""
        items = [
            self._map_to_item_response_dto(item) for item in data.get("items", [])
        ]

        return QuotationResponseDTO(
            id=data["id"],
            quotation_number=data["quotation_number"],
            client_id=data["client_id"],
            client_name=data.get("client_name"),
            status=QuotationStatus(data["status"]),
            incoterm=Incoterm(data["incoterm"]),
            currency=data["currency"],
            subtotal=data.get("subtotal", Decimal("0.00")),
            freight_cost=data.get("freight_cost", Decimal("0.00")),
            insurance_cost=data.get("insurance_cost", Decimal("0.00")),
            other_costs=data.get("other_costs", Decimal("0.00")),
            total=data.get("total", Decimal("0.00")),
            discount_percent=data.get("discount_percent", Decimal("0.00")),
            discount_amount=data.get("discount_amount", Decimal("0.00")),
            grand_total=data.get("grand_total", Decimal("0.00")),
            notes=data.get("notes"),
            terms_and_conditions=data.get("terms_and_conditions"),
            valid_from=data.get("valid_from"),
            valid_until=data.get("valid_until"),
            created_by=data.get("created_by"),
            items=items,
            item_count=len(items),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )

    def _map_to_item_response_dto(self, data: Dict) -> QuotationItemResponseDTO:
        """Map item data to response DTO."""
        return QuotationItemResponseDTO(
            id=data["id"],
            quotation_id=data["quotation_id"],
            product_id=data.get("product_id"),
            sku=data.get("sku"),
            product_name=data["product_name"],
            description=data.get("description"),
            quantity=data["quantity"],
            unit_of_measure=data.get("unit_of_measure", "piece"),
            unit_cost=data.get("unit_cost", Decimal("0.00")),
            unit_price=data.get("unit_price", Decimal("0.00")),
            markup_percent=data.get("markup_percent", Decimal("0.00")),
            tariff_percent=data.get("tariff_percent", Decimal("0.00")),
            tariff_amount=data.get("tariff_amount", Decimal("0.00")),
            freight_amount=data.get("freight_amount", Decimal("0.00")),
            line_total=data.get("line_total", Decimal("0.00")),
            sort_order=data.get("sort_order", 0),
            notes=data.get("notes"),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )


# Singleton instance
quotation_service = QuotationService()
