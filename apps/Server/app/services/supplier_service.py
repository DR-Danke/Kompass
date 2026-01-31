"""Supplier service for managing Chinese supplier business logic.

This service provides the business logic layer between API routes and the
repository layer for supplier CRUD operations, filtering, search, and
business rule enforcement.
"""

import math
import re
from typing import List, Optional
from uuid import UUID

from app.models.kompass_dto import (
    PaginationDTO,
    SupplierCreateDTO,
    SupplierListResponseDTO,
    SupplierResponseDTO,
    SupplierStatus,
    SupplierUpdateDTO,
)
from app.repository.kompass_repository import product_repository, supplier_repository


class SupplierService:
    """Handles supplier business logic including validation and CRUD operations."""

    # Email validation regex pattern
    EMAIL_PATTERN = re.compile(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )

    def _validate_email(self, email: str) -> bool:
        """Validate email format.

        Args:
            email: Email address to validate

        Returns:
            True if valid, False otherwise
        """
        if not email:
            return True  # Empty email is allowed (optional field)
        return bool(self.EMAIL_PATTERN.match(email))

    def _normalize_wechat_id(self, wechat_id: Optional[str]) -> Optional[str]:
        """Normalize WeChat ID by converting to lowercase and stripping whitespace.

        Note: contact_phone field can be used to store WeChat IDs.

        Args:
            wechat_id: WeChat ID to normalize

        Returns:
            Normalized WeChat ID or None
        """
        if not wechat_id:
            return wechat_id
        return wechat_id.strip().lower()

    def create_supplier(self, request: SupplierCreateDTO) -> SupplierResponseDTO:
        """Create a new supplier with validation.

        Args:
            request: Supplier creation data

        Returns:
            Created supplier response

        Raises:
            ValueError: If validation fails or creation fails
        """
        # Validate email format (Pydantic EmailStr already validates,
        # but we add extra validation for safety)
        if request.contact_email and not self._validate_email(
            str(request.contact_email)
        ):
            raise ValueError("Invalid email format")

        # Normalize contact_phone (can be used for WeChat ID)
        contact_phone = self._normalize_wechat_id(request.contact_phone)

        # Create supplier via repository
        result = supplier_repository.create(
            name=request.name,
            code=request.code,
            status=request.status.value,
            contact_name=request.contact_name,
            contact_email=str(request.contact_email) if request.contact_email else None,
            contact_phone=contact_phone,
            address=request.address,
            city=request.city,
            country=request.country,
            website=request.website,
            notes=request.notes,
        )

        if not result:
            print("ERROR [SupplierService]: Failed to create supplier")
            raise ValueError("Failed to create supplier")

        print(f"INFO [SupplierService]: Created supplier {result['id']}")
        return SupplierResponseDTO(**result)

    def get_supplier(self, supplier_id: UUID) -> Optional[SupplierResponseDTO]:
        """Get a supplier by ID with product count.

        Args:
            supplier_id: UUID of the supplier

        Returns:
            Supplier response with product count, or None if not found
        """
        result = supplier_repository.get_by_id(supplier_id)

        if not result:
            print(f"INFO [SupplierService]: Supplier {supplier_id} not found")
            return None

        print(f"INFO [SupplierService]: Retrieved supplier {supplier_id}")
        return SupplierResponseDTO(**result)

    def get_supplier_with_product_count(
        self, supplier_id: UUID
    ) -> Optional[dict]:
        """Get a supplier by ID with product count.

        Args:
            supplier_id: UUID of the supplier

        Returns:
            Supplier dict with product_count field, or None if not found
        """
        result = supplier_repository.get_by_id(supplier_id)

        if not result:
            print(f"INFO [SupplierService]: Supplier {supplier_id} not found")
            return None

        # Get product count for this supplier
        product_count = supplier_repository.count_products_by_supplier(supplier_id)
        result["product_count"] = product_count

        print(f"INFO [SupplierService]: Retrieved supplier {supplier_id}")
        return result

    def list_suppliers(
        self,
        status: Optional[SupplierStatus] = None,
        country: Optional[str] = None,
        has_products: Optional[bool] = None,
        sort_by: str = "name",
        page: int = 1,
        limit: int = 20,
    ) -> SupplierListResponseDTO:
        """List suppliers with filtering and pagination.

        Args:
            status: Filter by supplier status
            country: Filter by country
            has_products: Filter by whether supplier has products
            sort_by: Field to sort by (default: name)
            page: Page number (1-indexed)
            limit: Items per page

        Returns:
            Paginated list of suppliers
        """
        # Use extended get_all with filters
        items, total = supplier_repository.get_all_with_filters(
            page=page,
            limit=limit,
            status=status.value if status else None,
            country=country,
            has_products=has_products,
        )

        pages = math.ceil(total / limit) if total > 0 else 0

        supplier_responses = [SupplierResponseDTO(**item) for item in items]

        print(
            f"INFO [SupplierService]: Listed {len(supplier_responses)} suppliers "
            f"(page {page}/{pages})"
        )

        return SupplierListResponseDTO(
            items=supplier_responses,
            pagination=PaginationDTO(
                page=page,
                limit=limit,
                total=total,
                pages=pages,
            ),
        )

    def update_supplier(
        self, supplier_id: UUID, request: SupplierUpdateDTO
    ) -> Optional[SupplierResponseDTO]:
        """Update a supplier with validation.

        Args:
            supplier_id: UUID of the supplier to update
            request: Update data

        Returns:
            Updated supplier response, or None if not found

        Raises:
            ValueError: If validation fails
        """
        # Check if supplier exists
        existing = supplier_repository.get_by_id(supplier_id)
        if not existing:
            return None

        # Validate email format if provided
        if request.contact_email and not self._validate_email(
            str(request.contact_email)
        ):
            raise ValueError("Invalid email format")

        # Normalize contact_phone if provided
        contact_phone = self._normalize_wechat_id(request.contact_phone)

        # Build update kwargs, only including non-None values
        update_kwargs = {}
        if request.name is not None:
            update_kwargs["name"] = request.name
        if request.code is not None:
            update_kwargs["code"] = request.code
        if request.status is not None:
            update_kwargs["status"] = request.status.value
        if request.contact_name is not None:
            update_kwargs["contact_name"] = request.contact_name
        if request.contact_email is not None:
            update_kwargs["contact_email"] = str(request.contact_email)
        if contact_phone is not None:
            update_kwargs["contact_phone"] = contact_phone
        if request.address is not None:
            update_kwargs["address"] = request.address
        if request.city is not None:
            update_kwargs["city"] = request.city
        if request.country is not None:
            update_kwargs["country"] = request.country
        if request.website is not None:
            update_kwargs["website"] = request.website
        if request.notes is not None:
            update_kwargs["notes"] = request.notes

        result = supplier_repository.update(supplier_id, **update_kwargs)

        if not result:
            print(f"ERROR [SupplierService]: Failed to update supplier {supplier_id}")
            raise ValueError("Failed to update supplier")

        print(f"INFO [SupplierService]: Updated supplier {supplier_id}")
        return SupplierResponseDTO(**result)

    def delete_supplier(self, supplier_id: UUID) -> bool:
        """Soft delete a supplier (set status to inactive).

        Cannot delete suppliers that have active products.

        Args:
            supplier_id: UUID of the supplier to delete

        Returns:
            True if deleted, False if supplier not found

        Raises:
            ValueError: If supplier has active products
        """
        # Check if supplier exists
        existing = supplier_repository.get_by_id(supplier_id)
        if not existing:
            return False

        # Check for active products
        products, product_count = product_repository.get_all(
            supplier_id=supplier_id,
            status="active",
            page=1,
            limit=1,
        )

        if product_count > 0:
            print(
                f"WARN [SupplierService]: Blocked deletion of supplier {supplier_id} "
                "- has active products"
            )
            raise ValueError("Cannot delete supplier with active products")

        success = supplier_repository.delete(supplier_id)

        if success:
            print(f"INFO [SupplierService]: Deleted supplier {supplier_id}")

        return success

    def search_suppliers(self, query: str) -> List[SupplierResponseDTO]:
        """Search suppliers by name, email, or contact phone (WeChat).

        Args:
            query: Search query string

        Returns:
            List of matching suppliers (max 50)
        """
        # Skip if query is empty or too short
        if not query or len(query.strip()) < 2:
            return []

        query = query.strip()

        # Use repository search with extended fields
        items = supplier_repository.search(query=query, limit=50)

        print(f"INFO [SupplierService]: Search for '{query}' returned {len(items)} results")

        return [SupplierResponseDTO(**item) for item in items]


# Singleton instance
supplier_service = SupplierService()
