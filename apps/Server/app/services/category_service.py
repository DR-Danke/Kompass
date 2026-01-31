"""Category service for managing hierarchical product categories."""

from typing import Dict, List, Optional
from uuid import UUID

from app.models.kompass_dto import (
    CategoryCreateDTO,
    CategoryResponseDTO,
    CategoryTreeNode,
    CategoryUpdateDTO,
)
from app.repository.kompass_repository import category_repository


class CategoryService:
    """Handles category CRUD and hierarchical tree operations."""

    def create_category(self, request: CategoryCreateDTO) -> Optional[CategoryResponseDTO]:
        """Create a new category.

        Args:
            request: Category creation data

        Returns:
            Created category DTO or None if creation failed
        """
        if request.parent_id:
            parent = category_repository.get_by_id(request.parent_id)
            if not parent:
                print(f"WARN [CategoryService]: Parent category not found: {request.parent_id}")
                return None

        result = category_repository.create(
            name=request.name,
            description=request.description,
            parent_id=request.parent_id,
            sort_order=request.sort_order,
            is_active=request.is_active,
        )

        if result:
            return CategoryResponseDTO(**result)
        return None

    def get_category(self, category_id: UUID) -> Optional[CategoryResponseDTO]:
        """Get category by ID.

        Args:
            category_id: UUID of the category

        Returns:
            Category DTO or None if not found
        """
        result = category_repository.get_by_id(category_id)
        if result:
            return CategoryResponseDTO(**result)
        return None

    def list_categories(self) -> List[CategoryTreeNode]:
        """Get all categories as a nested tree structure.

        Returns:
            List of root-level CategoryTreeNode with nested children
        """
        items, _ = category_repository.get_all(page=1, limit=10000, is_active=True)
        return self._build_tree(items)

    def update_category(
        self, category_id: UUID, request: CategoryUpdateDTO
    ) -> Optional[CategoryResponseDTO]:
        """Update a category.

        Args:
            category_id: UUID of the category to update
            request: Update data

        Returns:
            Updated category DTO or None if update failed
        """
        existing = category_repository.get_by_id(category_id)
        if not existing:
            return None

        if request.parent_id is not None:
            if request.parent_id == category_id:
                print(f"WARN [CategoryService]: Cannot set category as its own parent: {category_id}")
                return None

            if request.parent_id:
                parent = category_repository.get_by_id(request.parent_id)
                if not parent:
                    print(f"WARN [CategoryService]: Parent category not found: {request.parent_id}")
                    return None

                if self._is_descendant(request.parent_id, category_id):
                    print("WARN [CategoryService]: Cannot move category to its descendant")
                    return None

        update_data: Dict[str, object] = {}
        if request.name is not None:
            update_data["name"] = request.name
        if request.description is not None:
            update_data["description"] = request.description
        if request.parent_id is not None:
            update_data["parent_id"] = request.parent_id
        if request.sort_order is not None:
            update_data["sort_order"] = request.sort_order
        if request.is_active is not None:
            update_data["is_active"] = request.is_active

        result = category_repository.update(category_id, **update_data)
        if result:
            return CategoryResponseDTO(**result)
        return None

    def delete_category(self, category_id: UUID) -> bool:
        """Delete a category (soft delete).

        Args:
            category_id: UUID of the category to delete

        Returns:
            True if deleted, False otherwise
        """
        existing = category_repository.get_by_id(category_id)
        if not existing:
            print(f"WARN [CategoryService]: Category not found: {category_id}")
            return False

        if category_repository.has_children(category_id):
            print(f"WARN [CategoryService]: Cannot delete category with children: {category_id}")
            return False

        if category_repository.has_products(category_id):
            print(f"WARN [CategoryService]: Cannot delete category with products: {category_id}")
            return False

        return category_repository.delete(category_id)

    def move_category(
        self, category_id: UUID, new_parent_id: Optional[UUID]
    ) -> Optional[CategoryResponseDTO]:
        """Move a category to a new parent.

        Args:
            category_id: UUID of the category to move
            new_parent_id: UUID of the new parent or None for root level

        Returns:
            Updated category DTO or None if move failed
        """
        existing = category_repository.get_by_id(category_id)
        if not existing:
            return None

        if new_parent_id == category_id:
            print("WARN [CategoryService]: Cannot move category to itself")
            return None

        if new_parent_id:
            parent = category_repository.get_by_id(new_parent_id)
            if not parent:
                print(f"WARN [CategoryService]: New parent not found: {new_parent_id}")
                return None

            if self._is_descendant(new_parent_id, category_id):
                print("WARN [CategoryService]: Cannot move category to its descendant")
                return None

        result = category_repository.set_parent(category_id, new_parent_id)
        if result:
            return CategoryResponseDTO(**result)
        return None

    def get_descendants(self, category_id: UUID) -> List[CategoryResponseDTO]:
        """Get all descendants of a category.

        Args:
            category_id: UUID of the parent category

        Returns:
            List of all descendant category DTOs
        """
        existing = category_repository.get_by_id(category_id)
        if not existing:
            return []

        descendants: List[CategoryResponseDTO] = []
        self._collect_descendants(category_id, descendants)
        return descendants

    def _collect_descendants(
        self, category_id: UUID, result: List[CategoryResponseDTO]
    ) -> None:
        """Recursively collect all descendants."""
        children = category_repository.get_children(category_id)
        for child in children:
            result.append(CategoryResponseDTO(**child))
            self._collect_descendants(child["id"], result)

    def _is_descendant(self, category_id: UUID, potential_ancestor_id: UUID) -> bool:
        """Check if category_id is a descendant of potential_ancestor_id."""
        descendants = self.get_descendants(potential_ancestor_id)
        return any(d.id == category_id for d in descendants)

    def _build_tree(
        self,
        categories: List[Dict],
        parent_id: Optional[UUID] = None,
        depth: int = 0,
        path: str = "",
    ) -> List[CategoryTreeNode]:
        """Build nested tree structure from flat list.

        Args:
            categories: Flat list of category dicts
            parent_id: Parent ID to filter by (None for root)
            depth: Current depth in tree
            path: Current path string

        Returns:
            List of CategoryTreeNode with nested children
        """
        result = []
        for cat in categories:
            if cat.get("parent_id") == parent_id:
                node_path = f"{path}/{cat['name']}" if path else cat["name"]
                children = self._build_tree(categories, cat["id"], depth + 1, node_path)
                result.append(
                    CategoryTreeNode(
                        id=cat["id"],
                        name=cat["name"],
                        description=cat.get("description"),
                        parent_id=cat.get("parent_id"),
                        sort_order=cat.get("sort_order", 0),
                        is_active=cat.get("is_active", True),
                        depth=depth,
                        path=node_path,
                        children=children,
                    )
                )
        return sorted(result, key=lambda x: (x.sort_order, x.name))


# Singleton instance
category_service = CategoryService()
