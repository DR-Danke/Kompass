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
    """Status options for clients."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    PROSPECT = "prospect"


class QuotationStatus(str, Enum):
    """Status options for quotations."""

    DRAFT = "draft"
    SENT = "sent"
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


class TagListResponseDTO(BaseModel):
    """Paginated list response for tags."""

    items: List[TagResponseDTO]
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
    """Request model for creating a product."""

    sku: str = Field(min_length=1, max_length=100)
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


# =============================================================================
# CLIENT DTOs
# =============================================================================


class ClientCreateDTO(BaseModel):
    """Request model for creating a client."""

    company_name: str = Field(min_length=1, max_length=255)
    contact_name: Optional[str] = Field(default=None, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    address: Optional[str] = None
    city: Optional[str] = Field(default=None, max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)
    country: Optional[str] = Field(default=None, max_length=100)
    postal_code: Optional[str] = Field(default=None, max_length=20)
    niche_id: Optional[UUID] = None
    status: ClientStatus = ClientStatus.PROSPECT
    notes: Optional[str] = None


class ClientUpdateDTO(BaseModel):
    """Request model for updating a client."""

    company_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    contact_name: Optional[str] = Field(default=None, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    address: Optional[str] = None
    city: Optional[str] = Field(default=None, max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)
    country: Optional[str] = Field(default=None, max_length=100)
    postal_code: Optional[str] = Field(default=None, max_length=20)
    niche_id: Optional[UUID] = None
    status: Optional[ClientStatus] = None
    notes: Optional[str] = None


class ClientResponseDTO(BaseModel):
    """Response model for client data."""

    id: UUID
    company_name: str
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    niche_id: Optional[UUID] = None
    niche_name: Optional[str] = None
    status: ClientStatus
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ClientListResponseDTO(BaseModel):
    """Paginated list response for clients."""

    items: List[ClientResponseDTO]
    pagination: PaginationDTO


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
