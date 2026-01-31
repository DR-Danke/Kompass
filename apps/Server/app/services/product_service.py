"""Product service for Biblia General (master product database) management.

This service provides business logic operations for product management, including:
- Auto-generated SKU when not provided
- Full-text search across name, description, and SKU
- Bulk import with validation and error reporting
- Image and tag management
- Advanced filtering and sorting
"""

import math
import secrets
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from app.models.kompass_dto import (
    BulkCreateErrorDTO,
    BulkCreateResponseDTO,
    PaginationDTO,
    ProductCreateDTO,
    ProductFilterDTO,
    ProductImageResponseDTO,
    ProductListResponseDTO,
    ProductResponseDTO,
    ProductStatus,
    ProductUpdateDTO,
    TagResponseDTO,
)
from app.repository.kompass_repository import (
    ProductRepository,
    product_repository,
)


class ProductService:
    """Service layer for product management operations.

    This service wraps the ProductRepository with business logic for:
    - SKU auto-generation
    - Full-text search
    - Bulk operations
    - Image and tag management
    - DTO mapping
    """

    def __init__(
        self,
        repository: Optional[ProductRepository] = None,
    ) -> None:
        """Initialize the ProductService.

        Args:
            repository: ProductRepository instance (uses singleton if not provided)
        """
        self._repository = repository or product_repository

    def _generate_sku(self) -> str:
        """Generate a unique SKU for a product.

        Format: PRD-{YYYYMMDD}-{6_random_alphanum}

        Returns:
            Generated SKU string
        """
        date_part = datetime.now().strftime("%Y%m%d")
        random_part = secrets.token_hex(3).upper()
        return f"PRD-{date_part}-{random_part}"

    def _map_to_response_dto(self, product_dict: dict) -> ProductResponseDTO:
        """Map a product dictionary from repository to ProductResponseDTO.

        Args:
            product_dict: Product dictionary from repository

        Returns:
            ProductResponseDTO instance
        """
        images = [
            ProductImageResponseDTO(
                id=img["id"],
                product_id=img["product_id"],
                url=img["url"],
                alt_text=img.get("alt_text"),
                sort_order=img.get("sort_order", 0),
                is_primary=img.get("is_primary", False),
                created_at=img["created_at"],
                updated_at=img["updated_at"],
            )
            for img in product_dict.get("images", [])
        ]

        tags = [
            TagResponseDTO(
                id=tag["id"],
                name=tag["name"],
                color=tag.get("color", "#000000"),
                created_at=tag["created_at"],
                updated_at=tag["updated_at"],
            )
            for tag in product_dict.get("tags", [])
        ]

        return ProductResponseDTO(
            id=product_dict["id"],
            sku=product_dict["sku"],
            name=product_dict["name"],
            description=product_dict.get("description"),
            supplier_id=product_dict["supplier_id"],
            supplier_name=product_dict.get("supplier_name"),
            category_id=product_dict.get("category_id"),
            category_name=product_dict.get("category_name"),
            hs_code_id=product_dict.get("hs_code_id"),
            hs_code=product_dict.get("hs_code"),
            status=ProductStatus(product_dict["status"]),
            unit_cost=Decimal(str(product_dict.get("unit_cost", 0))),
            unit_price=Decimal(str(product_dict.get("unit_price", 0))),
            currency=product_dict.get("currency", "USD"),
            unit_of_measure=product_dict.get("unit_of_measure", "piece"),
            minimum_order_qty=product_dict.get("minimum_order_qty", 1),
            lead_time_days=product_dict.get("lead_time_days"),
            weight_kg=(
                Decimal(str(product_dict["weight_kg"]))
                if product_dict.get("weight_kg") is not None
                else None
            ),
            dimensions=product_dict.get("dimensions"),
            origin_country=product_dict.get("origin_country", "China"),
            images=images,
            tags=tags,
            created_at=product_dict["created_at"],
            updated_at=product_dict["updated_at"],
        )

    def create_product(self, request: ProductCreateDTO) -> Optional[ProductResponseDTO]:
        """Create a new product.

        If SKU is not provided, auto-generates one using the format PRD-{YYYYMMDD}-{random}.

        Args:
            request: ProductCreateDTO with product details

        Returns:
            ProductResponseDTO if created successfully, None otherwise
        """
        # Auto-generate SKU if not provided or empty
        sku = request.sku if request.sku else self._generate_sku()

        # Create the product
        product = self._repository.create(
            sku=sku,
            name=request.name,
            description=request.description,
            supplier_id=request.supplier_id,
            category_id=request.category_id,
            hs_code_id=request.hs_code_id,
            status=request.status.value,
            unit_cost=request.unit_cost,
            unit_price=request.unit_price,
            currency=request.currency,
            unit_of_measure=request.unit_of_measure,
            minimum_order_qty=request.minimum_order_qty,
            lead_time_days=request.lead_time_days,
            weight_kg=request.weight_kg,
            dimensions=request.dimensions,
            origin_country=request.origin_country,
        )

        if not product:
            print("ERROR [ProductService]: Failed to create product")
            return None

        product_id = product["id"]

        # Handle images if provided
        if request.images:
            for img in request.images:
                self._repository.add_image(
                    product_id=product_id,
                    url=img.url,
                    alt_text=img.alt_text,
                    sort_order=img.sort_order,
                    is_primary=img.is_primary,
                )

        # Handle tags if provided
        if request.tag_ids:
            for tag_id in request.tag_ids:
                self._repository.add_tag(product_id=product_id, tag_id=tag_id)

        # Fetch the full product with images and tags
        full_product = self._repository.get_by_id(product_id)
        if not full_product:
            print("ERROR [ProductService]: Failed to fetch created product")
            return None

        return self._map_to_response_dto(full_product)

    def get_product(self, product_id: UUID) -> Optional[ProductResponseDTO]:
        """Get a product by ID.

        Args:
            product_id: Product UUID

        Returns:
            ProductResponseDTO if found, None otherwise
        """
        product = self._repository.get_by_id(product_id)
        if not product:
            return None
        return self._map_to_response_dto(product)

    def list_products(
        self,
        filters: Optional[ProductFilterDTO] = None,
        page: int = 1,
        limit: int = 20,
        has_images: Optional[bool] = None,
        min_moq: Optional[int] = None,
        max_moq: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> ProductListResponseDTO:
        """List products with filtering, pagination, and sorting.

        Args:
            filters: ProductFilterDTO with filter parameters
            page: Page number (1-indexed)
            limit: Number of items per page
            has_images: Filter products with/without images
            min_moq: Minimum order quantity filter
            max_moq: Maximum order quantity filter
            sort_by: Sort field (name, unit_price, created_at, minimum_order_qty)
            sort_order: Sort order (asc or desc)

        Returns:
            ProductListResponseDTO with items and pagination
        """
        filters = filters or ProductFilterDTO()

        items, total = self._repository.get_all(
            page=page,
            limit=limit,
            category_id=filters.category_id,
            supplier_id=filters.supplier_id,
            status=filters.status.value if filters.status else None,
            min_price=filters.min_price,
            max_price=filters.max_price,
            search=filters.search,
            tag_ids=filters.tag_ids,
            has_images=has_images,
            min_moq=min_moq,
            max_moq=max_moq,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        products = [self._map_to_response_dto(item) for item in items]
        pages = math.ceil(total / limit) if limit > 0 else 0

        pagination = PaginationDTO(
            page=page,
            limit=limit,
            total=total,
            pages=pages,
        )

        return ProductListResponseDTO(
            items=products,
            pagination=pagination,
            filters=filters,
        )

    def update_product(
        self, product_id: UUID, request: ProductUpdateDTO
    ) -> Optional[ProductResponseDTO]:
        """Update a product.

        Args:
            product_id: Product UUID
            request: ProductUpdateDTO with fields to update

        Returns:
            Updated ProductResponseDTO if successful, None if not found
        """
        # Build kwargs only for non-None fields
        update_kwargs = {}
        if request.sku is not None:
            update_kwargs["sku"] = request.sku
        if request.name is not None:
            update_kwargs["name"] = request.name
        if request.description is not None:
            update_kwargs["description"] = request.description
        if request.supplier_id is not None:
            update_kwargs["supplier_id"] = request.supplier_id
        if request.category_id is not None:
            update_kwargs["category_id"] = request.category_id
        if request.hs_code_id is not None:
            update_kwargs["hs_code_id"] = request.hs_code_id
        if request.status is not None:
            update_kwargs["status"] = request.status.value
        if request.unit_cost is not None:
            update_kwargs["unit_cost"] = request.unit_cost
        if request.unit_price is not None:
            update_kwargs["unit_price"] = request.unit_price
        if request.currency is not None:
            update_kwargs["currency"] = request.currency
        if request.unit_of_measure is not None:
            update_kwargs["unit_of_measure"] = request.unit_of_measure
        if request.minimum_order_qty is not None:
            update_kwargs["minimum_order_qty"] = request.minimum_order_qty
        if request.lead_time_days is not None:
            update_kwargs["lead_time_days"] = request.lead_time_days
        if request.weight_kg is not None:
            update_kwargs["weight_kg"] = request.weight_kg
        if request.dimensions is not None:
            update_kwargs["dimensions"] = request.dimensions
        if request.origin_country is not None:
            update_kwargs["origin_country"] = request.origin_country

        product = self._repository.update(product_id, **update_kwargs)
        if not product:
            return None

        return self._map_to_response_dto(product)

    def delete_product(self, product_id: UUID) -> bool:
        """Delete a product (soft delete by setting status to inactive).

        Args:
            product_id: Product UUID

        Returns:
            True if deleted successfully, False otherwise
        """
        return self._repository.delete(product_id)

    def search_products(
        self, query: str, limit: int = 50
    ) -> List[ProductResponseDTO]:
        """Search products by full-text search on name, description, and SKU.

        Args:
            query: Search query string
            limit: Maximum number of results to return

        Returns:
            List of matching ProductResponseDTO
        """
        if not query or not query.strip():
            return []

        items, _ = self._repository.get_all(
            page=1,
            limit=limit,
            search=query.strip(),
        )

        return [self._map_to_response_dto(item) for item in items]

    def bulk_create_products(
        self, products: List[ProductCreateDTO]
    ) -> BulkCreateResponseDTO:
        """Bulk create multiple products with validation and error reporting.

        Each product is created individually to allow partial success.
        Failed products are reported with their index and error message.

        Args:
            products: List of ProductCreateDTO to create

        Returns:
            BulkCreateResponseDTO with successful and failed items
        """
        successful: List[ProductResponseDTO] = []
        failed: List[BulkCreateErrorDTO] = []

        for index, product_request in enumerate(products):
            try:
                result = self.create_product(product_request)
                if result:
                    successful.append(result)
                else:
                    failed.append(
                        BulkCreateErrorDTO(
                            index=index,
                            sku=product_request.sku or None,
                            error="Failed to create product",
                        )
                    )
            except Exception as e:
                print(f"ERROR [ProductService]: Bulk create failed for index {index}: {e}")
                failed.append(
                    BulkCreateErrorDTO(
                        index=index,
                        sku=product_request.sku or None,
                        error=str(e),
                    )
                )

        return BulkCreateResponseDTO(
            successful=successful,
            failed=failed,
            total_count=len(products),
            success_count=len(successful),
            failure_count=len(failed),
        )

    def add_product_image(
        self,
        product_id: UUID,
        image_url: str,
        is_primary: bool = False,
        alt_text: Optional[str] = None,
        sort_order: int = 0,
    ) -> Optional[ProductImageResponseDTO]:
        """Add an image to a product.

        Args:
            product_id: Product UUID
            image_url: URL of the image
            is_primary: Whether this is the primary image
            alt_text: Alternative text for the image
            sort_order: Sort order for image display

        Returns:
            ProductImageResponseDTO if added successfully, None otherwise
        """
        result = self._repository.add_image(
            product_id=product_id,
            url=image_url,
            alt_text=alt_text,
            sort_order=sort_order,
            is_primary=is_primary,
        )

        if not result:
            return None

        return ProductImageResponseDTO(
            id=result["id"],
            product_id=result["product_id"],
            url=result["url"],
            alt_text=result.get("alt_text"),
            sort_order=result.get("sort_order", 0),
            is_primary=result.get("is_primary", False),
            created_at=result["created_at"],
            updated_at=result["updated_at"],
        )

    def remove_product_image(self, product_id: UUID, image_id: UUID) -> bool:
        """Remove an image from a product.

        Args:
            product_id: Product UUID (for validation purposes)
            image_id: Image UUID to remove

        Returns:
            True if removed successfully, False otherwise
        """
        # Note: product_id is included for potential future validation
        # Currently the repository only needs image_id
        return self._repository.remove_image(image_id)

    def set_primary_image(self, product_id: UUID, image_id: UUID) -> bool:
        """Set a specific image as the primary image for a product.

        Args:
            product_id: Product UUID
            image_id: Image UUID to set as primary

        Returns:
            True if successful, False otherwise
        """
        return self._repository.set_primary_image(product_id, image_id)

    def add_tag_to_product(self, product_id: UUID, tag_id: UUID) -> bool:
        """Add a tag to a product.

        Args:
            product_id: Product UUID
            tag_id: Tag UUID to add

        Returns:
            True if successful, False otherwise
        """
        return self._repository.add_tag(product_id, tag_id)

    def remove_tag_from_product(self, product_id: UUID, tag_id: UUID) -> bool:
        """Remove a tag from a product.

        Args:
            product_id: Product UUID
            tag_id: Tag UUID to remove

        Returns:
            True if successful, False otherwise
        """
        return self._repository.remove_tag(product_id, tag_id)

    def get_products_by_tag(self, tag_id: UUID) -> List[ProductResponseDTO]:
        """Get all products with a specific tag.

        Args:
            tag_id: Tag UUID

        Returns:
            List of ProductResponseDTO with the specified tag
        """
        items, _ = self._repository.get_all(
            page=1,
            limit=1000,  # High limit to get all products with this tag
            tag_ids=[tag_id],
        )

        return [self._map_to_response_dto(item) for item in items]


# Singleton instance
product_service = ProductService()
