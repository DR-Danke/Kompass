"""Client service for CRM functionality.

This service provides business logic for managing clients throughout their lifecycle,
including CRUD operations, pipeline management, status history tracking, and timing
feasibility calculations.
"""

import math
import re
from datetime import date, datetime
from typing import Dict, List, Optional
from uuid import UUID

from app.models.kompass_dto import (
    ClientCreateDTO,
    ClientListResponseDTO,
    ClientResponseDTO,
    ClientSource,
    ClientStatus,
    ClientStatusChangeDTO,
    ClientUpdateDTO,
    ClientWithQuotationsDTO,
    Incoterm,
    PaginationDTO,
    PipelineResponseDTO,
    QuotationSummaryDTO,
    StatusHistoryResponseDTO,
    TimingFeasibilityDTO,
)
from app.repository.kompass_repository import client_repository, freight_rate_repository


class ClientService:
    """Handles client business logic including CRM operations."""

    # Email validation regex pattern
    EMAIL_PATTERN = re.compile(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )

    def __init__(self, repository=None):
        """Initialize service with optional repository injection for testing."""
        self.repository = repository or client_repository

    def _validate_email(self, email: str) -> bool:
        """Validate email format."""
        if not email:
            return True
        return bool(self.EMAIL_PATTERN.match(email))

    def _validate_project_deadline(self, deadline: Optional[date]) -> None:
        """Validate that project deadline is in the future."""
        if deadline is not None:
            today = date.today()
            if deadline <= today:
                raise ValueError("Project deadline must be in the future")

    def create_client(self, request: ClientCreateDTO) -> ClientResponseDTO:
        """Create a new client with validation.

        Args:
            request: Client creation data

        Returns:
            Created client response

        Raises:
            ValueError: If validation fails or creation fails
        """
        # Validate email format
        if request.email and not self._validate_email(str(request.email)):
            raise ValueError("Invalid email format")

        # Validate project deadline
        self._validate_project_deadline(request.project_deadline)

        # Create client via repository
        result = self.repository.create(
            company_name=request.company_name,
            contact_name=request.contact_name,
            email=str(request.email) if request.email else None,
            phone=request.phone,
            whatsapp=request.whatsapp,
            address=request.address,
            city=request.city,
            state=request.state,
            country=request.country,
            postal_code=request.postal_code,
            niche_id=request.niche_id,
            status=request.status.value,
            notes=request.notes,
            assigned_to=request.assigned_to,
            source=request.source.value if request.source else None,
            project_deadline=str(request.project_deadline) if request.project_deadline else None,
            project_name=request.project_name,
            incoterm_preference=request.incoterm_preference.value if request.incoterm_preference else None,
        )

        if not result:
            print("ERROR [ClientService]: Failed to create client")
            raise ValueError("Failed to create client")

        print(f"INFO [ClientService]: Created client {result['id']}")
        return self._map_to_response_dto(result)

    def get_client(self, client_id: UUID) -> Optional[ClientResponseDTO]:
        """Get a client by ID.

        Args:
            client_id: UUID of the client

        Returns:
            Client response, or None if not found
        """
        result = self.repository.get_by_id(client_id)

        if not result:
            print(f"INFO [ClientService]: Client {client_id} not found")
            return None

        print(f"INFO [ClientService]: Retrieved client {client_id}")
        return self._map_to_response_dto(result)

    def get_client_with_quotations(
        self, client_id: UUID
    ) -> Optional[ClientWithQuotationsDTO]:
        """Get a client by ID with quotation summary.

        Args:
            client_id: UUID of the client

        Returns:
            Client with quotation summary, or None if not found
        """
        result = self.repository.get_by_id(client_id)

        if not result:
            print(f"INFO [ClientService]: Client {client_id} not found")
            return None

        # Get quotation summary
        summary_data = self.repository.get_quotation_summary(client_id)
        quotation_summary = QuotationSummaryDTO(**summary_data)

        print(f"INFO [ClientService]: Retrieved client {client_id} with quotations")
        return ClientWithQuotationsDTO(
            id=result["id"],
            company_name=result["company_name"],
            contact_name=result.get("contact_name"),
            email=result.get("email"),
            phone=result.get("phone"),
            whatsapp=result.get("whatsapp"),
            address=result.get("address"),
            city=result.get("city"),
            state=result.get("state"),
            country=result.get("country"),
            postal_code=result.get("postal_code"),
            niche_id=result.get("niche_id"),
            niche_name=result.get("niche_name"),
            status=ClientStatus(result["status"]),
            notes=result.get("notes"),
            assigned_to=result.get("assigned_to"),
            assigned_to_name=result.get("assigned_to_name"),
            source=ClientSource(result["source"]) if result.get("source") else None,
            project_deadline=result.get("project_deadline"),
            project_name=result.get("project_name"),
            incoterm_preference=Incoterm(result["incoterm_preference"]) if result.get("incoterm_preference") else None,
            created_at=result["created_at"],
            updated_at=result["updated_at"],
            quotation_summary=quotation_summary,
        )

    def list_clients(
        self,
        status: Optional[ClientStatus] = None,
        niche_id: Optional[UUID] = None,
        assigned_to: Optional[UUID] = None,
        source: Optional[ClientSource] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        search: Optional[str] = None,
        sort_by: str = "company_name",
        page: int = 1,
        limit: int = 20,
    ) -> ClientListResponseDTO:
        """List clients with filtering and pagination.

        Args:
            status: Filter by client status
            niche_id: Filter by niche
            assigned_to: Filter by assigned user
            source: Filter by lead source
            date_from: Filter by created_at start date
            date_to: Filter by created_at end date
            search: Search query for company/contact/email
            sort_by: Field to sort by (company_name, created_at, project_deadline)
            page: Page number (1-indexed)
            limit: Items per page

        Returns:
            Paginated list of clients
        """
        items, total = self.repository.get_all(
            page=page,
            limit=limit,
            status=status.value if status else None,
            niche_id=niche_id,
            search=search,
            assigned_to=assigned_to,
            source=source.value if source else None,
            date_from=str(date_from) if date_from else None,
            date_to=str(date_to) if date_to else None,
            sort_by=sort_by,
        )

        pages = math.ceil(total / limit) if total > 0 else 0
        client_responses = [self._map_to_response_dto(item) for item in items]

        print(
            f"INFO [ClientService]: Listed {len(client_responses)} clients "
            f"(page {page}/{pages})"
        )

        return ClientListResponseDTO(
            items=client_responses,
            pagination=PaginationDTO(
                page=page,
                limit=limit,
                total=total,
                pages=pages,
            ),
        )

    def update_client(
        self, client_id: UUID, request: ClientUpdateDTO
    ) -> Optional[ClientResponseDTO]:
        """Update a client with validation.

        Args:
            client_id: UUID of the client to update
            request: Update data

        Returns:
            Updated client response, or None if not found

        Raises:
            ValueError: If validation fails
        """
        # Check if client exists
        existing = self.repository.get_by_id(client_id)
        if not existing:
            return None

        # Validate email format if provided
        if request.email and not self._validate_email(str(request.email)):
            raise ValueError("Invalid email format")

        # Validate project deadline if provided
        self._validate_project_deadline(request.project_deadline)

        # Build update kwargs
        update_kwargs: Dict = {}
        if request.company_name is not None:
            update_kwargs["company_name"] = request.company_name
        if request.contact_name is not None:
            update_kwargs["contact_name"] = request.contact_name
        if request.email is not None:
            update_kwargs["email"] = str(request.email)
        if request.phone is not None:
            update_kwargs["phone"] = request.phone
        if request.whatsapp is not None:
            update_kwargs["whatsapp"] = request.whatsapp
        if request.address is not None:
            update_kwargs["address"] = request.address
        if request.city is not None:
            update_kwargs["city"] = request.city
        if request.state is not None:
            update_kwargs["state"] = request.state
        if request.country is not None:
            update_kwargs["country"] = request.country
        if request.postal_code is not None:
            update_kwargs["postal_code"] = request.postal_code
        if request.niche_id is not None:
            update_kwargs["niche_id"] = request.niche_id
        if request.status is not None:
            update_kwargs["status"] = request.status.value
        if request.notes is not None:
            update_kwargs["notes"] = request.notes
        if request.assigned_to is not None:
            update_kwargs["assigned_to"] = request.assigned_to
        if request.source is not None:
            update_kwargs["source"] = request.source.value
        if request.project_deadline is not None:
            update_kwargs["project_deadline"] = str(request.project_deadline)
        if request.project_name is not None:
            update_kwargs["project_name"] = request.project_name
        if request.incoterm_preference is not None:
            update_kwargs["incoterm_preference"] = request.incoterm_preference.value

        result = self.repository.update(client_id, **update_kwargs)

        if not result:
            print(f"ERROR [ClientService]: Failed to update client {client_id}")
            raise ValueError("Failed to update client")

        print(f"INFO [ClientService]: Updated client {client_id}")
        return self._map_to_response_dto(result)

    def delete_client(self, client_id: UUID) -> bool:
        """Soft delete a client (set status to inactive).

        Cannot delete clients with active quotations.

        Args:
            client_id: UUID of the client to delete

        Returns:
            True if deleted, False if client not found

        Raises:
            ValueError: If client has active quotations
        """
        # Check if client exists
        existing = self.repository.get_by_id(client_id)
        if not existing:
            return False

        # Check for active quotations
        if self.repository.has_active_quotations(client_id):
            print(
                f"WARN [ClientService]: Blocked deletion of client {client_id} "
                "- has active quotations"
            )
            raise ValueError("Cannot delete client with active quotations")

        success = self.repository.delete(client_id)

        if success:
            print(f"INFO [ClientService]: Deleted client {client_id}")

        return success

    def search_clients(self, query: str) -> List[ClientResponseDTO]:
        """Search clients by company name, contact name, or email.

        Args:
            query: Search query string

        Returns:
            List of matching clients (max 50)
        """
        if not query or len(query.strip()) < 2:
            return []

        query = query.strip()
        items = self.repository.search(query=query, limit=50)

        print(f"INFO [ClientService]: Search for '{query}' returned {len(items)} results")

        return [self._map_to_response_dto(item) for item in items]

    def get_pipeline(self) -> PipelineResponseDTO:
        """Get clients grouped by status for pipeline view (Kanban columns).

        Returns:
            Pipeline response with clients grouped by status (6 columns)
        """
        lead_clients = self.repository.get_by_status("lead")
        qualified_clients = self.repository.get_by_status("qualified")
        quoting_clients = self.repository.get_by_status("quoting")
        negotiating_clients = self.repository.get_by_status("negotiating")
        won_clients = self.repository.get_by_status("won")
        lost_clients = self.repository.get_by_status("lost")

        print(
            f"INFO [ClientService]: Pipeline - lead: {len(lead_clients)}, "
            f"qualified: {len(qualified_clients)}, quoting: {len(quoting_clients)}, "
            f"negotiating: {len(negotiating_clients)}, won: {len(won_clients)}, "
            f"lost: {len(lost_clients)}"
        )

        return PipelineResponseDTO(
            lead=[self._map_to_response_dto(c) for c in lead_clients],
            qualified=[self._map_to_response_dto(c) for c in qualified_clients],
            quoting=[self._map_to_response_dto(c) for c in quoting_clients],
            negotiating=[self._map_to_response_dto(c) for c in negotiating_clients],
            won=[self._map_to_response_dto(c) for c in won_clients],
            lost=[self._map_to_response_dto(c) for c in lost_clients],
        )

    def update_status(
        self,
        client_id: UUID,
        status_change: ClientStatusChangeDTO,
        changed_by: UUID,
    ) -> Optional[ClientResponseDTO]:
        """Update client status and record history.

        Args:
            client_id: UUID of the client
            status_change: Status change request with new status and notes
            changed_by: UUID of the user making the change

        Returns:
            Updated client response, or None if not found
        """
        # Get existing client
        existing = self.repository.get_by_id(client_id)
        if not existing:
            return None

        old_status = existing["status"]
        new_status = status_change.new_status.value

        # Update client status
        result = self.repository.update(client_id, status=new_status)
        if not result:
            print(f"ERROR [ClientService]: Failed to update status for client {client_id}")
            raise ValueError("Failed to update client status")

        # Record status history
        self.repository.create_status_history(
            client_id=client_id,
            old_status=old_status,
            new_status=new_status,
            notes=status_change.notes,
            changed_by=changed_by,
        )

        print(
            f"INFO [ClientService]: Updated client {client_id} status "
            f"from {old_status} to {new_status}"
        )

        return self._map_to_response_dto(result)

    def get_status_history(self, client_id: UUID) -> List[StatusHistoryResponseDTO]:
        """Get status change history for a client.

        Args:
            client_id: UUID of the client

        Returns:
            List of status history entries
        """
        # Verify client exists
        existing = self.repository.get_by_id(client_id)
        if not existing:
            return []

        history = self.repository.get_status_history(client_id)

        print(f"INFO [ClientService]: Retrieved {len(history)} status history entries")

        return [
            StatusHistoryResponseDTO(
                id=h["id"],
                client_id=h["client_id"],
                old_status=ClientStatus(h["old_status"]) if h.get("old_status") else None,
                new_status=ClientStatus(h["new_status"]),
                notes=h.get("notes"),
                changed_by=h.get("changed_by"),
                changed_by_name=h.get("changed_by_name"),
                created_at=h["created_at"],
            )
            for h in history
        ]

    def calculate_timing_feasibility(
        self,
        client_id: UUID,
        product_lead_time_days: int,
    ) -> Optional[TimingFeasibilityDTO]:
        """Calculate whether project deadline is achievable.

        Args:
            client_id: UUID of the client
            product_lead_time_days: Production lead time in days

        Returns:
            Timing feasibility result, or None if client not found
        """
        # Get client
        client = self.repository.get_by_id(client_id)
        if not client:
            return None

        project_deadline = client.get("project_deadline")
        if not project_deadline:
            return TimingFeasibilityDTO(
                is_feasible=True,
                production_lead_time_days=product_lead_time_days,
                shipping_transit_days=0,
                total_lead_time_days=product_lead_time_days,
                message="No project deadline set - timing is flexible",
            )

        # Get shipping transit days based on client location
        shipping_transit_days = self._get_shipping_transit_days(client)

        # Calculate total lead time
        total_lead_time = product_lead_time_days + shipping_transit_days

        # Calculate days until deadline
        today = date.today()
        if isinstance(project_deadline, str):
            project_deadline = datetime.strptime(project_deadline, "%Y-%m-%d").date()

        days_until_deadline = (project_deadline - today).days
        buffer_days = days_until_deadline - total_lead_time
        is_feasible = buffer_days >= 0

        if is_feasible:
            message = f"Feasible with {buffer_days} days buffer"
        else:
            message = f"Not feasible - {abs(buffer_days)} days short"

        print(
            f"INFO [ClientService]: Timing feasibility for client {client_id}: "
            f"{message}"
        )

        return TimingFeasibilityDTO(
            is_feasible=is_feasible,
            project_deadline=project_deadline,
            production_lead_time_days=product_lead_time_days,
            shipping_transit_days=shipping_transit_days,
            total_lead_time_days=total_lead_time,
            days_until_deadline=days_until_deadline,
            buffer_days=buffer_days,
            message=message,
        )

    def _get_shipping_transit_days(self, client: Dict) -> int:
        """Get shipping transit days based on client location.

        Args:
            client: Client dict with location info

        Returns:
            Transit days (defaults to 30 if not found)
        """
        # Try to find freight rate based on client's country/city
        destination = client.get("country") or client.get("city")
        if not destination:
            return 30  # Default transit days

        # Get freight rates for China -> destination
        rates, _ = freight_rate_repository.get_all(
            destination=destination,
            is_active=True,
            page=1,
            limit=1,
        )

        if rates and rates[0].get("transit_days"):
            return rates[0]["transit_days"]

        return 30  # Default transit days

    def _map_to_response_dto(self, data: Dict) -> ClientResponseDTO:
        """Map repository data to response DTO."""
        return ClientResponseDTO(
            id=data["id"],
            company_name=data["company_name"],
            contact_name=data.get("contact_name"),
            email=data.get("email"),
            phone=data.get("phone"),
            whatsapp=data.get("whatsapp"),
            address=data.get("address"),
            city=data.get("city"),
            state=data.get("state"),
            country=data.get("country"),
            postal_code=data.get("postal_code"),
            niche_id=data.get("niche_id"),
            niche_name=data.get("niche_name"),
            status=ClientStatus(data["status"]),
            notes=data.get("notes"),
            assigned_to=data.get("assigned_to"),
            assigned_to_name=data.get("assigned_to_name"),
            source=ClientSource(data["source"]) if data.get("source") else None,
            project_deadline=data.get("project_deadline"),
            project_name=data.get("project_name"),
            incoterm_preference=Incoterm(data["incoterm_preference"]) if data.get("incoterm_preference") else None,
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )


# Singleton instance
client_service = ClientService()
