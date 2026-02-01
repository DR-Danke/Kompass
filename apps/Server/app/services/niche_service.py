"""Niche service for managing client type classifications."""

from typing import List, Optional
from uuid import UUID

from app.models.kompass_dto import (
    NicheCreateDTO,
    NicheResponseDTO,
    NicheUpdateDTO,
    NicheWithClientCountDTO,
)
from app.repository.kompass_repository import niche_repository


class NicheService:
    """Handles niche CRUD operations with client count tracking."""

    def create_niche(self, request: NicheCreateDTO) -> Optional[NicheResponseDTO]:
        """Create a new niche.

        Args:
            request: Niche creation data

        Returns:
            Created niche DTO or None if creation failed
        """
        result = niche_repository.create(
            name=request.name,
            description=request.description,
            is_active=request.is_active,
        )

        if result:
            return NicheResponseDTO(**result)
        return None

    def get_niche(self, niche_id: UUID) -> Optional[NicheWithClientCountDTO]:
        """Get niche by ID with client count.

        Args:
            niche_id: UUID of the niche

        Returns:
            Niche DTO with client count or None if not found
        """
        result = niche_repository.get_by_id(niche_id)
        if result:
            client_count = niche_repository.count_clients_by_niche(niche_id)
            return NicheWithClientCountDTO(
                id=result["id"],
                name=result["name"],
                description=result["description"],
                is_active=result["is_active"],
                client_count=client_count,
                created_at=result["created_at"],
                updated_at=result["updated_at"],
            )
        return None

    def list_niches(self) -> List[NicheWithClientCountDTO]:
        """Get all niches with client counts.

        Returns:
            List of niche DTOs with client counts
        """
        results = niche_repository.get_all_with_client_counts()
        return [
            NicheWithClientCountDTO(
                id=r["id"],
                name=r["name"],
                description=r["description"],
                is_active=r["is_active"],
                client_count=r["client_count"],
                created_at=r["created_at"],
                updated_at=r["updated_at"],
            )
            for r in results
        ]

    def update_niche(
        self, niche_id: UUID, request: NicheUpdateDTO
    ) -> Optional[NicheResponseDTO]:
        """Update a niche.

        Args:
            niche_id: UUID of the niche to update
            request: Update data

        Returns:
            Updated niche DTO or None if update failed
        """
        existing = niche_repository.get_by_id(niche_id)
        if not existing:
            return None

        result = niche_repository.update(
            niche_id=niche_id,
            name=request.name,
            description=request.description,
            is_active=request.is_active,
        )

        if result:
            return NicheResponseDTO(**result)
        return None

    def delete_niche(self, niche_id: UUID) -> bool:
        """Delete a niche (soft delete).

        Fails if the niche has associated clients.

        Args:
            niche_id: UUID of the niche to delete

        Returns:
            True if deleted, False otherwise

        Raises:
            ValueError: If niche has associated clients
        """
        existing = niche_repository.get_by_id(niche_id)
        if not existing:
            print(f"WARN [NicheService]: Niche not found: {niche_id}")
            return False

        if niche_repository.has_clients(niche_id):
            print(f"WARN [NicheService]: Cannot delete niche with clients: {niche_id}")
            raise ValueError("Cannot delete niche with associated clients")

        return niche_repository.delete(niche_id)


# Singleton instance
niche_service = NicheService()
