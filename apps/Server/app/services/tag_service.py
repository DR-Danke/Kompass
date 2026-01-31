"""Tag service for managing product tags."""

from typing import List, Optional
from uuid import UUID

from app.models.kompass_dto import (
    TagCreateDTO,
    TagResponseDTO,
    TagUpdateDTO,
    TagWithCountDTO,
)
from app.repository.kompass_repository import tag_repository


class TagService:
    """Handles tag CRUD operations with product count tracking."""

    def create_tag(self, request: TagCreateDTO) -> Optional[TagResponseDTO]:
        """Create a new tag.

        Args:
            request: Tag creation data

        Returns:
            Created tag DTO or None if creation failed
        """
        result = tag_repository.create(
            name=request.name,
            color=request.color,
        )

        if result:
            return TagResponseDTO(**result)
        return None

    def get_tag(self, tag_id: UUID) -> Optional[TagWithCountDTO]:
        """Get tag by ID with product count.

        Args:
            tag_id: UUID of the tag

        Returns:
            Tag DTO with product count or None if not found
        """
        result = tag_repository.get_by_id(tag_id)
        if result:
            product_count = tag_repository.get_product_count(tag_id)
            return TagWithCountDTO(
                id=result["id"],
                name=result["name"],
                color=result["color"],
                product_count=product_count,
                created_at=result["created_at"],
                updated_at=result["updated_at"],
            )
        return None

    def list_tags(self) -> List[TagWithCountDTO]:
        """Get all tags with product counts.

        Returns:
            List of tag DTOs with product counts
        """
        results = tag_repository.get_all_with_counts()
        return [
            TagWithCountDTO(
                id=r["id"],
                name=r["name"],
                color=r["color"],
                product_count=r["product_count"],
                created_at=r["created_at"],
                updated_at=r["updated_at"],
            )
            for r in results
        ]

    def update_tag(
        self, tag_id: UUID, request: TagUpdateDTO
    ) -> Optional[TagResponseDTO]:
        """Update a tag.

        Args:
            tag_id: UUID of the tag to update
            request: Update data

        Returns:
            Updated tag DTO or None if update failed
        """
        existing = tag_repository.get_by_id(tag_id)
        if not existing:
            return None

        result = tag_repository.update(
            tag_id=tag_id,
            name=request.name,
            color=request.color,
        )

        if result:
            return TagResponseDTO(**result)
        return None

    def delete_tag(self, tag_id: UUID) -> bool:
        """Delete a tag (hard delete, cascade removes product associations).

        Args:
            tag_id: UUID of the tag to delete

        Returns:
            True if deleted, False otherwise
        """
        existing = tag_repository.get_by_id(tag_id)
        if not existing:
            print(f"WARN [TagService]: Tag not found: {tag_id}")
            return False

        return tag_repository.delete(tag_id)

    def search_tags(self, query: str, limit: int = 20) -> List[TagResponseDTO]:
        """Search tags by name for autocomplete.

        Args:
            query: Search query string
            limit: Maximum number of results

        Returns:
            List of matching tag DTOs
        """
        if not query or not query.strip():
            return []

        results = tag_repository.search(query.strip(), limit)
        return [TagResponseDTO(**r) for r in results]


# Singleton instance
tag_service = TagService()
