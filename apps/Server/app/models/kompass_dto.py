"""Kompass Portfolio & Quotation System Data Transfer Objects (DTOs)."""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# =============================================================================
# ENUMS
# =============================================================================


class SupplierStatus(str, Enum):
    """Status options for suppliers."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING_REVIEW = "pending_review"


class ProductStatus(str, Enum):
    """Status options for products."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    DISCONTINUED = "discontinued"


class ClientStatus(str, Enum):
    """Status options for clients representing pipeline stages."""

    LEAD = "lead"
    QUALIFIED = "qualified"
    QUOTING = "quoting"
    NEGOTIATING = "negotiating"
    WON = "won"
    LOST = "lost"


class ClientSource(str, Enum):
    """Source options for tracking lead origin."""

    WEBSITE = "website"
    REFERRAL = "referral"
    COLD_CALL = "cold_call"
    TRADE_SHOW = "trade_show"
    LINKEDIN = "linkedin"
    OTHER = "other"


class QuotationStatus(str, Enum):
    """Status options for quotations."""

    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    NEGOTIATING = "negotiating"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class Incoterm(str, Enum):
    """International Commercial Terms for shipping."""

    FOB = "FOB"
    CIF = "CIF"
    EXW = "EXW"
    DDP = "DDP"
    DAP = "DAP"
    CFR = "CFR"
    CPT = "CPT"
    CIP = "CIP"
    DAT = "DAT"
    FCA = "FCA"
    FAS = "FAS"


# =============================================================================
# PAGINATION
# =============================================================================


class PaginationDTO(BaseModel):
    """Pagination metadata for list responses."""

    page: int = Field(ge=1, default=1)
    limit: int = Field(ge=1, le=100, default=20)
    total: int = Field(ge=0, default=0)
    pages: int = Field(ge=0, default=0)


# =============================================================================
# NICHE DTOs
# =============================================================================


class NicheCreateDTO(BaseModel):
    """Request model for creating a niche."""

    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: bool = True


class NicheUpdateDTO(BaseModel):
    """Request model for updating a niche."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class NicheResponseDTO(BaseModel):
    """Response model for niche data."""

    id: UUID
    name: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NicheListResponseDTO(BaseModel):
    """Paginated list response for niches."""

    items: List[NicheResponseDTO]
    pagination: PaginationDTO


class NicheWithClientCountDTO(BaseModel):
    """Response model for niche data with client count."""

    id: UUID
    name: str
    description: Optional[str] = None
    is_active: bool
    client_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# =============================================================================
# CATEGORY DTOs
# =============================================================================


class CategoryCreateDTO(BaseModel):
    """Request model for creating a category."""

    name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    sort_order: int = 0
    is_active: bool = True


class CategoryUpdateDTO(BaseModel):
    """Request model for updating a category."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryResponseDTO(BaseModel):
    """Response model for category data."""

    id: UUID
    name: str
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    parent_name: Optional[str] = None
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CategoryListResponseDTO(BaseModel):
    """Paginated list response for categories."""

    items: List[CategoryResponseDTO]
    pagination: PaginationDTO


class CategoryTreeNode(BaseModel):
    """Tree node for hierarchical category representation."""

    id: UUID
    name: str
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    sort_order: int = 0
    is_active: bool = True
    depth: int = 0
    path: str = ""
    children: List["CategoryTreeNode"] = []

    model_config = {"from_attributes": True}


# =============================================================================
# TAG DTOs
# =============================================================================


class TagCreateDTO(BaseModel):
    """Request model for creating a tag."""

    name: str = Field(min_length=1, max_length=100)
    color: str = Field(default="#000000", pattern=r"^#[0-9A-Fa-f]{6}$")


class TagUpdateDTO(BaseModel):
    """Request model for updating a tag."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    color: Optional[str] = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")


class TagResponseDTO(BaseModel):
    """Response model for tag data."""

    id: UUID
    name: str
    color: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TagWithCountDTO(BaseModel):
    """Tag response with product count."""

    id: UUID
    name: str
    color: str
    product_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TagListResponseDTO(BaseModel):
    """Paginated list response for tags."""

    items: List[TagWithCountDTO]
    pagination: PaginationDTO


# =============================================================================
# HS CODE DTOs
# =============================================================================


class HSCodeCreateDTO(BaseModel):
    """Request model for creating an HS code."""

    code: str = Field(min_length=1, max_length=20)
    description: str = Field(min_length=1)
    duty_rate: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)
    notes: Optional[str] = None


class HSCodeUpdateDTO(BaseModel):
    """Request model for updating an HS code."""

    code: Optional[str] = Field(default=None, min_length=1, max_length=20)
    description: Optional[str] = Field(default=None, min_length=1)
    duty_rate: Optional[Decimal] = Field(default=None, ge=0, le=100)
    notes: Optional[str] = None


class HSCodeResponseDTO(BaseModel):
    """Response model for HS code data."""

    id: UUID
    code: str
    description: str
    duty_rate: Decimal
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class HSCodeListResponseDTO(BaseModel):
    """Paginated list response for HS codes."""

    items: List[HSCodeResponseDTO]
    pagination: PaginationDTO


# =============================================================================
# SUPPLIER DTOs
# =============================================================================


class SupplierCreateDTO(BaseModel):
    """Request model for creating a supplier."""

    name: str = Field(min_length=1, max_length=255)
    code: Optional[str] = Field(default=None, max_length=50)
    status: SupplierStatus = SupplierStatus.ACTIVE
    contact_name: Optional[str] = Field(default=None, max_length=200)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(default=None, max_length=50)
    address: Optional[str] = None
    city: Optional[str] = Field(default=None, max_length=100)
    country: str = Field(default="China", max_length=100)
    website: Optional[str] = Field(default=None, max_length=500)
    notes: Optional[str] = None


class SupplierUpdateDTO(BaseModel):
    """Request model for updating a supplier."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    code: Optional[str] = Field(default=None, max_length=50)
    status: Optional[SupplierStatus] = None
    contact_name: Optional[str] = Field(default=None, max_length=200)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(default=None, max_length=50)
    address: Optional[str] = None
    city: Optional[str] = Field(default=None, max_length=100)
    country: Optional[str] = Field(default=None, max_length=100)
    website: Optional[str] = Field(default=None, max_length=500)
    notes: Optional[str] = None


class SupplierResponseDTO(BaseModel):
    """Response model for supplier data."""

    id: UUID
    name: str
    code: Optional[str] = None
    status: SupplierStatus
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: str
    website: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SupplierListResponseDTO(BaseModel):
    """Paginated list response for suppliers."""

    items: List[SupplierResponseDTO]
    pagination: PaginationDTO


# =============================================================================
# PRODUCT IMAGE DTOs
# =============================================================================


class ProductImageCreateDTO(BaseModel):
    """Request model for creating a product image."""

    url: str = Field(min_length=1, max_length=1000)
    alt_text: Optional[str] = Field(default=None, max_length=500)
    sort_order: int = 0
    is_primary: bool = False


class ProductImageResponseDTO(BaseModel):
    """Response model for product image data."""

    id: UUID
    product_id: UUID
    url: str
    alt_text: Optional[str] = None
    sort_order: int
    is_primary: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# =============================================================================
# PRODUCT DTOs
# =============================================================================


class ProductFilterDTO(BaseModel):
    """Filtering parameters for product queries."""

    category_id: Optional[UUID] = None
    supplier_id: Optional[UUID] = None
    status: Optional[ProductStatus] = None
    min_price: Optional[Decimal] = Field(default=None, ge=0)
    max_price: Optional[Decimal] = Field(default=None, ge=0)
    search: Optional[str] = None
    tag_ids: Optional[List[UUID]] = None


class ProductCreateDTO(BaseModel):
    """Request model for creating a product.

    Note: SKU is optional. If not provided, the service will auto-generate one.
    """

    sku: Optional[str] = Field(default=None, max_length=100)
    name: str = Field(min_length=1, max_length=500)
    description: Optional[str] = None
    supplier_id: UUID
    category_id: Optional[UUID] = None
    hs_code_id: Optional[UUID] = None
    status: ProductStatus = ProductStatus.DRAFT
    unit_cost: Decimal = Field(default=Decimal("0.00"), ge=0)
    unit_price: Decimal = Field(default=Decimal("0.00"), ge=0)
    currency: str = Field(default="USD", max_length=3)
    unit_of_measure: str = Field(default="piece", max_length=50)
    minimum_order_qty: int = Field(default=1, ge=1)
    lead_time_days: Optional[int] = Field(default=None, ge=0)
    weight_kg: Optional[Decimal] = Field(default=None, ge=0)
    dimensions: Optional[str] = Field(default=None, max_length=100)
    origin_country: str = Field(default="China", max_length=100)
    images: Optional[List[ProductImageCreateDTO]] = None
    tag_ids: Optional[List[UUID]] = None


class ProductUpdateDTO(BaseModel):
    """Request model for updating a product."""

    sku: Optional[str] = Field(default=None, min_length=1, max_length=100)
    name: Optional[str] = Field(default=None, min_length=1, max_length=500)
    description: Optional[str] = None
    supplier_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    hs_code_id: Optional[UUID] = None
    status: Optional[ProductStatus] = None
    unit_cost: Optional[Decimal] = Field(default=None, ge=0)
    unit_price: Optional[Decimal] = Field(default=None, ge=0)
    currency: Optional[str] = Field(default=None, max_length=3)
    unit_of_measure: Optional[str] = Field(default=None, max_length=50)
    minimum_order_qty: Optional[int] = Field(default=None, ge=1)
    lead_time_days: Optional[int] = Field(default=None, ge=0)
    weight_kg: Optional[Decimal] = Field(default=None, ge=0)
    dimensions: Optional[str] = Field(default=None, max_length=100)
    origin_country: Optional[str] = Field(default=None, max_length=100)


class ProductResponseDTO(BaseModel):
    """Response model for product data."""

    id: UUID
    sku: str
    name: str
    description: Optional[str] = None
    supplier_id: UUID
    supplier_name: Optional[str] = None
    category_id: Optional[UUID] = None
    category_name: Optional[str] = None
    hs_code_id: Optional[UUID] = None
    hs_code: Optional[str] = None
    status: ProductStatus
    unit_cost: Decimal
    unit_price: Decimal
    currency: str
    unit_of_measure: str
    minimum_order_qty: int
    lead_time_days: Optional[int] = None
    weight_kg: Optional[Decimal] = None
    dimensions: Optional[str] = None
    origin_country: str
    images: List[ProductImageResponseDTO] = []
    tags: List[TagResponseDTO] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductListResponseDTO(BaseModel):
    """Paginated list response for products."""

    items: List[ProductResponseDTO]
    pagination: PaginationDTO
    filters: Optional[ProductFilterDTO] = None


# =============================================================================
# PORTFOLIO DTOs
# =============================================================================


class PortfolioItemCreateDTO(BaseModel):
    """Request model for adding an item to a portfolio."""

    product_id: UUID
    sort_order: int = 0
    notes: Optional[str] = None


class PortfolioItemResponseDTO(BaseModel):
    """Response model for portfolio item data."""

    id: UUID
    portfolio_id: UUID
    product_id: UUID
    product_name: Optional[str] = None
    product_sku: Optional[str] = None
    sort_order: int
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PortfolioCreateDTO(BaseModel):
    """Request model for creating a portfolio."""

    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    niche_id: Optional[UUID] = None
    is_active: bool = True
    items: Optional[List[PortfolioItemCreateDTO]] = None


class PortfolioUpdateDTO(BaseModel):
    """Request model for updating a portfolio."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    niche_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class PortfolioResponseDTO(BaseModel):
    """Response model for portfolio data."""

    id: UUID
    name: str
    description: Optional[str] = None
    niche_id: Optional[UUID] = None
    niche_name: Optional[str] = None
    is_active: bool
    items: List[PortfolioItemResponseDTO] = []
    item_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PortfolioListResponseDTO(BaseModel):
    """Paginated list response for portfolios."""

    items: List[PortfolioResponseDTO]
    pagination: PaginationDTO


class PortfolioFilterDTO(BaseModel):
    """Filtering parameters for portfolio queries."""

    niche_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    search: Optional[str] = None


class PortfolioShareTokenResponseDTO(BaseModel):
    """Response model for portfolio share token."""

    token: str
    portfolio_id: UUID
    expires_at: Optional[datetime] = None


class PortfolioPublicResponseDTO(BaseModel):
    """Response model for public portfolio access via share token.

    Omits sensitive internal fields like is_active for public viewing.
    """

    id: UUID
    name: str
    description: Optional[str] = None
    niche_name: Optional[str] = None
    items: List[PortfolioItemResponseDTO] = []
    item_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class ReorderProductsRequestDTO(BaseModel):
    """Request model for reordering products in a portfolio."""

    product_ids: List[UUID] = Field(min_length=1)


class PortfolioDuplicateRequestDTO(BaseModel):
    """Request model for duplicating a portfolio."""

    new_name: str = Field(min_length=1, max_length=255)


class PortfolioAddProductRequestDTO(BaseModel):
    """Request model for adding a product to a portfolio."""

    curator_notes: Optional[str] = None


class PortfolioAddItemRequestDTO(BaseModel):
    """Request model for adding an item to a portfolio via /items endpoint."""

    product_id: UUID = Field(description="The product UUID to add to the portfolio")
    curator_notes: Optional[str] = None


class PortfolioFromFiltersRequestDTO(BaseModel):
    """Request model for creating a portfolio from product filters."""

    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    niche_id: Optional[UUID] = None
    filters: ProductFilterDTO


# =============================================================================
# CLIENT DTOs
# =============================================================================


class ClientCreateDTO(BaseModel):
    """Request model for creating a client."""

    company_name: str = Field(min_length=1, max_length=255)
    contact_name: Optional[str] = Field(default=None, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    whatsapp: Optional[str] = Field(default=None, max_length=50)
    address: Optional[str] = None
    city: Optional[str] = Field(default=None, max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)
    country: Optional[str] = Field(default=None, max_length=100)
    postal_code: Optional[str] = Field(default=None, max_length=20)
    niche_id: Optional[UUID] = None
    status: ClientStatus = ClientStatus.LEAD
    notes: Optional[str] = None
    # CRM-specific fields
    assigned_to: Optional[UUID] = None
    source: Optional[ClientSource] = None
    project_deadline: Optional[date] = None
    project_name: Optional[str] = Field(default=None, max_length=255)
    incoterm_preference: Optional[Incoterm] = None


class ClientUpdateDTO(BaseModel):
    """Request model for updating a client."""

    company_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    contact_name: Optional[str] = Field(default=None, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    whatsapp: Optional[str] = Field(default=None, max_length=50)
    address: Optional[str] = None
    city: Optional[str] = Field(default=None, max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)
    country: Optional[str] = Field(default=None, max_length=100)
    postal_code: Optional[str] = Field(default=None, max_length=20)
    niche_id: Optional[UUID] = None
    status: Optional[ClientStatus] = None
    notes: Optional[str] = None
    # CRM-specific fields
    assigned_to: Optional[UUID] = None
    source: Optional[ClientSource] = None
    project_deadline: Optional[date] = None
    project_name: Optional[str] = Field(default=None, max_length=255)
    incoterm_preference: Optional[Incoterm] = None


class ClientResponseDTO(BaseModel):
    """Response model for client data."""

    id: UUID
    company_name: str
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    niche_id: Optional[UUID] = None
    niche_name: Optional[str] = None
    status: ClientStatus
    notes: Optional[str] = None
    # CRM-specific fields
    assigned_to: Optional[UUID] = None
    assigned_to_name: Optional[str] = None
    source: Optional[ClientSource] = None
    project_deadline: Optional[date] = None
    project_name: Optional[str] = None
    incoterm_preference: Optional[Incoterm] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ClientListResponseDTO(BaseModel):
    """Paginated list response for clients."""

    items: List[ClientResponseDTO]
    pagination: PaginationDTO


class ClientStatusChangeDTO(BaseModel):
    """Request model for changing client status with notes."""

    new_status: ClientStatus
    notes: Optional[str] = None


class StatusHistoryResponseDTO(BaseModel):
    """Response model for status history entry."""

    id: UUID
    client_id: UUID
    old_status: Optional[ClientStatus] = None
    new_status: ClientStatus
    notes: Optional[str] = None
    changed_by: Optional[UUID] = None
    changed_by_name: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class QuotationSummaryDTO(BaseModel):
    """Summary of quotations for a client."""

    total_quotations: int = 0
    draft_count: int = 0
    sent_count: int = 0
    accepted_count: int = 0
    rejected_count: int = 0
    expired_count: int = 0
    total_value: Decimal = Decimal("0.00")


class ClientWithQuotationsDTO(BaseModel):
    """Client response with quotation history summary."""

    id: UUID
    company_name: str
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    niche_id: Optional[UUID] = None
    niche_name: Optional[str] = None
    status: ClientStatus
    notes: Optional[str] = None
    assigned_to: Optional[UUID] = None
    assigned_to_name: Optional[str] = None
    source: Optional[ClientSource] = None
    project_deadline: Optional[date] = None
    project_name: Optional[str] = None
    incoterm_preference: Optional[Incoterm] = None
    created_at: datetime
    updated_at: datetime
    quotation_summary: QuotationSummaryDTO

    model_config = {"from_attributes": True}


class PipelineResponseDTO(BaseModel):
    """Response for pipeline view grouped by status (Kanban columns)."""

    lead: List[ClientResponseDTO] = []
    qualified: List[ClientResponseDTO] = []
    quoting: List[ClientResponseDTO] = []
    negotiating: List[ClientResponseDTO] = []
    won: List[ClientResponseDTO] = []
    lost: List[ClientResponseDTO] = []


class TimingFeasibilityDTO(BaseModel):
    """Response for timing feasibility calculation."""

    is_feasible: bool
    project_deadline: Optional[date] = None
    production_lead_time_days: int = 0
    shipping_transit_days: int = 0
    total_lead_time_days: int = 0
    days_until_deadline: Optional[int] = None
    buffer_days: Optional[int] = None
    message: str = ""


# =============================================================================
# FREIGHT RATE DTOs
# =============================================================================


class FreightRateCreateDTO(BaseModel):
    """Request model for creating a freight rate."""

    origin: str = Field(min_length=1, max_length=200)
    destination: str = Field(min_length=1, max_length=200)
    incoterm: Incoterm = Incoterm.FOB
    rate_per_kg: Optional[Decimal] = Field(default=None, ge=0)
    rate_per_cbm: Optional[Decimal] = Field(default=None, ge=0)
    minimum_charge: Decimal = Field(default=Decimal("0.00"), ge=0)
    transit_days: Optional[int] = Field(default=None, ge=0)
    is_active: bool = True
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    notes: Optional[str] = None


class FreightRateUpdateDTO(BaseModel):
    """Request model for updating a freight rate."""

    origin: Optional[str] = Field(default=None, min_length=1, max_length=200)
    destination: Optional[str] = Field(default=None, min_length=1, max_length=200)
    incoterm: Optional[Incoterm] = None
    rate_per_kg: Optional[Decimal] = Field(default=None, ge=0)
    rate_per_cbm: Optional[Decimal] = Field(default=None, ge=0)
    minimum_charge: Optional[Decimal] = Field(default=None, ge=0)
    transit_days: Optional[int] = Field(default=None, ge=0)
    is_active: Optional[bool] = None
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    notes: Optional[str] = None


class FreightRateResponseDTO(BaseModel):
    """Response model for freight rate data."""

    id: UUID
    origin: str
    destination: str
    incoterm: Incoterm
    rate_per_kg: Optional[Decimal] = None
    rate_per_cbm: Optional[Decimal] = None
    minimum_charge: Decimal
    transit_days: Optional[int] = None
    is_active: bool
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FreightRateListResponseDTO(BaseModel):
    """Paginated list response for freight rates."""

    items: List[FreightRateResponseDTO]
    pagination: PaginationDTO


# =============================================================================
# PRICING SETTINGS DTOs
# =============================================================================


class PricingSettingCreateDTO(BaseModel):
    """Request model for creating a pricing setting."""

    setting_key: str = Field(min_length=1, max_length=100)
    setting_value: Decimal
    description: Optional[str] = None
    is_percentage: bool = False


class PricingSettingUpdateDTO(BaseModel):
    """Request model for updating a pricing setting."""

    setting_value: Optional[Decimal] = None
    description: Optional[str] = None
    is_percentage: Optional[bool] = None


class PricingSettingResponseDTO(BaseModel):
    """Response model for pricing setting data."""

    id: UUID
    setting_key: str
    setting_value: Decimal
    description: Optional[str] = None
    is_percentage: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PricingSettingsResponseDTO(BaseModel):
    """Response model for all pricing settings."""

    settings: List[PricingSettingResponseDTO]


# =============================================================================
# QUOTATION ITEM DTOs
# =============================================================================


class QuotationItemCreateDTO(BaseModel):
    """Request model for creating a quotation item."""

    product_id: Optional[UUID] = None
    sku: Optional[str] = Field(default=None, max_length=100)
    product_name: str = Field(min_length=1, max_length=500)
    description: Optional[str] = None
    quantity: int = Field(default=1, ge=1)
    unit_of_measure: str = Field(default="piece", max_length=50)
    unit_cost: Decimal = Field(default=Decimal("0.00"), ge=0)
    unit_price: Decimal = Field(default=Decimal("0.00"), ge=0)
    markup_percent: Decimal = Field(default=Decimal("0.00"), ge=0)
    tariff_percent: Decimal = Field(default=Decimal("0.00"), ge=0)
    tariff_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    freight_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    sort_order: int = 0
    notes: Optional[str] = None


class QuotationItemUpdateDTO(BaseModel):
    """Request model for updating a quotation item."""

    product_id: Optional[UUID] = None
    sku: Optional[str] = Field(default=None, max_length=100)
    product_name: Optional[str] = Field(default=None, min_length=1, max_length=500)
    description: Optional[str] = None
    quantity: Optional[int] = Field(default=None, ge=1)
    unit_of_measure: Optional[str] = Field(default=None, max_length=50)
    unit_cost: Optional[Decimal] = Field(default=None, ge=0)
    unit_price: Optional[Decimal] = Field(default=None, ge=0)
    markup_percent: Optional[Decimal] = Field(default=None, ge=0)
    tariff_percent: Optional[Decimal] = Field(default=None, ge=0)
    tariff_amount: Optional[Decimal] = Field(default=None, ge=0)
    freight_amount: Optional[Decimal] = Field(default=None, ge=0)
    sort_order: Optional[int] = None
    notes: Optional[str] = None


class QuotationItemResponseDTO(BaseModel):
    """Response model for quotation item data."""

    id: UUID
    quotation_id: UUID
    product_id: Optional[UUID] = None
    sku: Optional[str] = None
    product_name: str
    description: Optional[str] = None
    quantity: int
    unit_of_measure: str
    unit_cost: Decimal
    unit_price: Decimal
    markup_percent: Decimal
    tariff_percent: Decimal
    tariff_amount: Decimal
    freight_amount: Decimal
    line_total: Decimal
    sort_order: int
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# =============================================================================
# QUOTATION DTOs
# =============================================================================


class QuotationFilterDTO(BaseModel):
    """Filtering parameters for quotation queries."""

    client_id: Optional[UUID] = None
    status: Optional[QuotationStatus] = None
    created_by: Optional[UUID] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    search: Optional[str] = None


class QuotationCreateDTO(BaseModel):
    """Request model for creating a quotation."""

    quotation_number: Optional[str] = Field(default=None, max_length=50)
    client_id: UUID
    status: QuotationStatus = QuotationStatus.DRAFT
    incoterm: Incoterm = Incoterm.FOB
    currency: str = Field(default="USD", max_length=3)
    freight_cost: Decimal = Field(default=Decimal("0.00"), ge=0)
    insurance_cost: Decimal = Field(default=Decimal("0.00"), ge=0)
    other_costs: Decimal = Field(default=Decimal("0.00"), ge=0)
    discount_percent: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)
    notes: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    items: Optional[List[QuotationItemCreateDTO]] = None


class QuotationUpdateDTO(BaseModel):
    """Request model for updating a quotation."""

    status: Optional[QuotationStatus] = None
    incoterm: Optional[Incoterm] = None
    currency: Optional[str] = Field(default=None, max_length=3)
    freight_cost: Optional[Decimal] = Field(default=None, ge=0)
    insurance_cost: Optional[Decimal] = Field(default=None, ge=0)
    other_costs: Optional[Decimal] = Field(default=None, ge=0)
    discount_percent: Optional[Decimal] = Field(default=None, ge=0, le=100)
    notes: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None


class QuotationResponseDTO(BaseModel):
    """Response model for quotation data."""

    id: UUID
    quotation_number: str
    client_id: UUID
    client_name: Optional[str] = None
    status: QuotationStatus
    incoterm: Incoterm
    currency: str
    subtotal: Decimal
    freight_cost: Decimal
    insurance_cost: Decimal
    other_costs: Decimal
    total: Decimal
    discount_percent: Decimal
    discount_amount: Decimal
    grand_total: Decimal
    notes: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    created_by: Optional[UUID] = None
    items: List[QuotationItemResponseDTO] = []
    item_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class QuotationListResponseDTO(BaseModel):
    """Paginated list response for quotations."""

    items: List[QuotationResponseDTO]
    pagination: PaginationDTO
    filters: Optional[QuotationFilterDTO] = None


class QuotationPricingDTO(BaseModel):
    """Response model for quotation pricing calculation results."""

    quotation_id: UUID
    subtotal_fob_usd: Decimal = Field(
        default=Decimal("0.00"), description="Sum of line items FOB"
    )
    tariff_total_usd: Decimal = Field(
        default=Decimal("0.00"), description="Total tariff amount"
    )
    freight_intl_usd: Decimal = Field(
        default=Decimal("0.00"), description="International freight cost"
    )
    freight_national_cop: Decimal = Field(
        default=Decimal("0.00"), description="National freight in COP"
    )
    inspection_usd: Decimal = Field(
        default=Decimal("0.00"), description="Inspection cost"
    )
    insurance_usd: Decimal = Field(
        default=Decimal("0.00"), description="Insurance cost"
    )
    nationalization_cop: Decimal = Field(
        default=Decimal("0.00"), description="Nationalization cost"
    )
    subtotal_before_margin_cop: Decimal = Field(
        default=Decimal("0.00"), description="Subtotal before margin"
    )
    margin_percentage: Decimal = Field(
        default=Decimal("0.00"), description="Applied margin percentage"
    )
    margin_cop: Decimal = Field(
        default=Decimal("0.00"), description="Margin amount in COP"
    )
    total_cop: Decimal = Field(
        default=Decimal("0.00"), description="Final total in COP"
    )
    exchange_rate: Decimal = Field(
        default=Decimal("1.00"), description="Exchange rate used"
    )

    model_config = {"from_attributes": True}


class QuotationStatusTransitionDTO(BaseModel):
    """Request model for quotation status change."""

    new_status: QuotationStatus
    notes: Optional[str] = None


class QuotationCloneDTO(BaseModel):
    """Request model for cloning a quotation."""

    notes: Optional[str] = Field(
        default=None, description="Notes for the cloned quotation"
    )


class QuotationShareTokenResponseDTO(BaseModel):
    """Response model for quotation share token generation."""

    token: str
    quotation_id: UUID
    expires_at: Optional[datetime] = None


class QuotationPublicItemDTO(BaseModel):
    """Response model for public quotation item data (limited fields)."""

    product_name: str
    description: Optional[str] = None
    quantity: int
    unit_of_measure: str
    unit_price: Decimal
    line_total: Decimal

    model_config = {"from_attributes": True}


class QuotationPublicResponseDTO(BaseModel):
    """Response model for public quotation access via share token.

    Omits sensitive internal fields for public viewing.
    """

    id: UUID
    quotation_number: str
    client_name: Optional[str] = None
    status: QuotationStatus
    incoterm: Incoterm
    currency: str
    subtotal: Decimal
    freight_cost: Decimal
    insurance_cost: Decimal
    other_costs: Decimal
    total: Decimal
    discount_percent: Decimal
    grand_total: Decimal
    notes: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    items: List[QuotationPublicItemDTO] = []
    item_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class QuotationSendEmailRequestDTO(BaseModel):
    """Request model for sending quotation via email."""

    recipient_email: EmailStr = Field(description="Email address of the recipient")
    recipient_name: Optional[str] = Field(
        default=None, max_length=200, description="Name of the recipient"
    )
    subject: Optional[str] = Field(
        default=None, max_length=255, description="Email subject line"
    )
    message: Optional[str] = Field(
        default=None, description="Custom message to include in the email body"
    )
    include_pdf: bool = Field(
        default=True, description="Whether to attach the PDF proforma"
    )


class QuotationSendEmailResponseDTO(BaseModel):
    """Response model for quotation email sending result."""

    success: bool
    message: str
    sent_at: Optional[datetime] = None
    recipient_email: str
    mock_mode: bool = Field(
        default=False, description="Whether email was sent in mock mode"
    )


# =============================================================================
# BULK OPERATION DTOs
# =============================================================================


class BulkCreateErrorDTO(BaseModel):
    """Error details for a failed bulk create item."""

    index: int
    sku: Optional[str] = None
    error: str


class BulkCreateResponseDTO(BaseModel):
    """Response for bulk create operations."""

    successful: List[ProductResponseDTO] = []
    failed: List[BulkCreateErrorDTO] = []
    total_count: int = 0
    success_count: int = 0
    failure_count: int = 0


# =============================================================================
# DASHBOARD DTOs
# =============================================================================


class DashboardKPIsDTO(BaseModel):
    """KPI metrics for the dashboard."""

    total_products: int = 0
    products_added_this_month: int = 0
    active_suppliers: int = 0
    quotations_sent_this_week: int = 0
    pipeline_value: Decimal = Decimal("0.00")


class QuotationsByStatusDTO(BaseModel):
    """Quotation counts by status."""

    draft: int = 0
    sent: int = 0
    viewed: int = 0
    negotiating: int = 0
    accepted: int = 0
    rejected: int = 0
    expired: int = 0


class QuotationTrendPointDTO(BaseModel):
    """A single data point in the quotation trend chart."""

    date: str
    sent: int = 0
    accepted: int = 0


class TopQuotedProductDTO(BaseModel):
    """Top quoted product for the dashboard chart."""

    id: UUID
    name: str
    sku: str
    quote_count: int = 0


class RecentProductDTO(BaseModel):
    """Recent product for the dashboard activity feed."""

    id: UUID
    name: str
    sku: str
    supplier_name: Optional[str] = None
    created_at: datetime


class RecentQuotationDTO(BaseModel):
    """Recent quotation for the dashboard activity feed."""

    id: UUID
    quotation_number: str
    client_name: Optional[str] = None
    status: QuotationStatus
    grand_total: Decimal = Decimal("0.00")
    created_at: datetime


class RecentClientDTO(BaseModel):
    """Recent client for the dashboard activity feed."""

    id: UUID
    company_name: str
    status: ClientStatus
    created_at: datetime


class DashboardStatsDTO(BaseModel):
    """Complete dashboard statistics response."""

    kpis: DashboardKPIsDTO
    quotations_by_status: QuotationsByStatusDTO
    quotation_trend: List[QuotationTrendPointDTO] = []
    top_quoted_products: List[TopQuotedProductDTO] = []
    recent_products: List[RecentProductDTO] = []
    recent_quotations: List[RecentQuotationDTO] = []
    recent_clients: List[RecentClientDTO] = []
