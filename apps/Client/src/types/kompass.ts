/**
 * Kompass Portfolio & Quotation System TypeScript Types
 * Matches backend DTOs from apps/Server/app/models/kompass_dto.py
 */

// =============================================================================
// USER ADMIN DTOs
// =============================================================================

export type UserRole = 'admin' | 'manager' | 'user' | 'viewer';

export interface UserAdminResponse {
  id: string;
  email: string;
  first_name: string | null;
  last_name: string | null;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserAdminCreate {
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
  role: UserRole;
}

export interface UserAdminUpdate {
  first_name?: string;
  last_name?: string;
  role?: UserRole;
  is_active?: boolean;
}

export interface UserListResponse {
  items: UserAdminResponse[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface UserChangePassword {
  new_password: string;
}

// =============================================================================
// ENUMS / STATUS TYPES
// =============================================================================

export type SupplierStatus = 'active' | 'inactive' | 'pending_review';

export type SupplierPipelineStatus = 'contacted' | 'potential' | 'quoted' | 'certified' | 'active' | 'inactive';

export type CertificationStatus = 'uncertified' | 'pending_review' | 'certified_a' | 'certified_b' | 'certified_c';

export type ProductStatus = 'active' | 'inactive' | 'draft' | 'discontinued';

export type ClientStatus = 'lead' | 'qualified' | 'quoting' | 'negotiating' | 'won' | 'lost';

export type ClientSource = 'website' | 'referral' | 'cold_call' | 'trade_show' | 'linkedin' | 'other';

export type QuotationStatus = 'draft' | 'sent' | 'viewed' | 'negotiating' | 'accepted' | 'rejected' | 'expired';

export type Incoterm = 'FOB' | 'CIF' | 'EXW' | 'DDP' | 'DAP' | 'CFR' | 'CPT' | 'CIP' | 'DAT' | 'FCA' | 'FAS';

// =============================================================================
// PAGINATION
// =============================================================================

export interface Pagination {
  page: number;
  limit: number;
  total: number;
  pages: number;
}

// =============================================================================
// NICHE DTOs
// =============================================================================

export interface NicheCreate {
  name: string;
  description?: string | null;
  is_active?: boolean;
}

export interface NicheUpdate {
  name?: string | null;
  description?: string | null;
  is_active?: boolean | null;
}

export interface NicheResponse {
  id: string;
  name: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface NicheListResponse {
  items: NicheResponse[];
  pagination: Pagination;
}

export interface NicheWithClientCount extends NicheResponse {
  client_count: number;
}

// =============================================================================
// CATEGORY DTOs
// =============================================================================

export interface CategoryCreate {
  name: string;
  description?: string | null;
  parent_id?: string | null;
  sort_order?: number;
  is_active?: boolean;
}

export interface CategoryUpdate {
  name?: string | null;
  description?: string | null;
  parent_id?: string | null;
  sort_order?: number | null;
  is_active?: boolean | null;
}

export interface CategoryResponse {
  id: string;
  name: string;
  description: string | null;
  parent_id: string | null;
  parent_name: string | null;
  sort_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CategoryListResponse {
  items: CategoryResponse[];
  pagination: Pagination;
}

export interface CategoryTreeNode {
  id: string;
  name: string;
  description: string | null;
  parent_id: string | null;
  sort_order: number;
  is_active: boolean;
  depth: number;
  path: string;
  children: CategoryTreeNode[];
}

// =============================================================================
// TAG DTOs
// =============================================================================

export interface TagCreate {
  name: string;
  color?: string;
}

export interface TagUpdate {
  name?: string | null;
  color?: string | null;
}

export interface TagResponse {
  id: string;
  name: string;
  color: string;
  created_at: string;
  updated_at: string;
}

export interface TagListResponse {
  items: TagResponse[];
  pagination: Pagination;
}

export interface TagWithCount extends TagResponse {
  product_count: number;
}

// =============================================================================
// HS CODE DTOs
// =============================================================================

export interface HSCodeCreate {
  code: string;
  description: string;
  duty_rate?: number | string;
  notes?: string | null;
}

export interface HSCodeUpdate {
  code?: string | null;
  description?: string | null;
  duty_rate?: number | string | null;
  notes?: string | null;
}

export interface HSCodeResponse {
  id: string;
  code: string;
  description: string;
  duty_rate: number | string;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface HSCodeListResponse {
  items: HSCodeResponse[];
  pagination: Pagination;
}

// =============================================================================
// SUPPLIER DTOs
// =============================================================================

export interface SupplierCreate {
  name: string;
  code?: string | null;
  status?: SupplierStatus;
  contact_name?: string | null;
  contact_email?: string | null;
  contact_phone?: string | null;
  address?: string | null;
  city?: string | null;
  country?: string;
  website?: string | null;
  notes?: string | null;
}

export interface SupplierUpdate {
  name?: string | null;
  code?: string | null;
  status?: SupplierStatus | null;
  contact_name?: string | null;
  contact_email?: string | null;
  contact_phone?: string | null;
  address?: string | null;
  city?: string | null;
  country?: string | null;
  website?: string | null;
  notes?: string | null;
}

export interface SupplierResponse {
  id: string;
  name: string;
  code: string | null;
  status: SupplierStatus;
  contact_name: string | null;
  contact_email: string | null;
  contact_phone: string | null;
  address: string | null;
  city: string | null;
  country: string;
  website: string | null;
  notes: string | null;
  certification_status: CertificationStatus;
  pipeline_status: SupplierPipelineStatus;
  latest_audit_id: string | null;
  certified_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface SupplierListResponse {
  items: SupplierResponse[];
  pagination: Pagination;
}

export interface SupplierDeletePreview {
  supplier_name: string;
  products_count: number;
  audits_count: number;
}

export interface SupplierDeleteResponse {
  message: string;
  products_deleted: number;
  audits_deleted: number;
}

export interface SupplierPipelineSummary {
  contacted: number;
  potential: number;
  quoted: number;
  certified: number;
  active: number;
  inactive: number;
}

export interface SupplierWithProductCount extends SupplierResponse {
  product_count: number;
}

export interface SupplierPipelineResponse {
  contacted: SupplierWithProductCount[];
  potential: SupplierWithProductCount[];
  quoted: SupplierWithProductCount[];
  certified: SupplierWithProductCount[];
  active: SupplierWithProductCount[];
  inactive: SupplierWithProductCount[];
}

export interface SupplierCertificationSummary {
  id: string;
  name: string;
  code: string | null;
  status: SupplierStatus;
  country: string;
  certification_status: CertificationStatus;
  pipeline_status: SupplierPipelineStatus;
  certified_at: string | null;
  latest_audit_id: string | null;
  latest_audit_date: string | null;
  ai_classification: string | null;
  manual_classification: string | null;
}

// =============================================================================
// PRODUCT IMAGE DTOs
// =============================================================================

export interface ProductImageCreate {
  url: string;
  alt_text?: string | null;
  sort_order?: number;
  is_primary?: boolean;
}

export interface ProductImageResponse {
  id: string;
  product_id: string;
  url: string;
  alt_text: string | null;
  sort_order: number;
  is_primary: boolean;
  created_at: string;
  updated_at: string;
}

// =============================================================================
// PRODUCT DTOs
// =============================================================================

export interface ProductFilter {
  category_id?: string | null;
  supplier_id?: string | null;
  status?: ProductStatus | null;
  min_price?: number | string | null;
  max_price?: number | string | null;
  search?: string | null;
  tag_ids?: string[] | null;
}

export interface ProductCreate {
  sku?: string | null;
  name: string;
  description?: string | null;
  supplier_id: string;
  category_id?: string | null;
  hs_code_id?: string | null;
  status?: ProductStatus;
  unit_cost?: number | string;
  unit_price?: number | string;
  currency?: string;
  unit_of_measure?: string;
  minimum_order_qty?: number;
  lead_time_days?: number | null;
  weight_kg?: number | string | null;
  dimensions?: string | null;
  origin_country?: string;
  images?: ProductImageCreate[] | null;
  tag_ids?: string[] | null;
}

export interface ProductUpdate {
  sku?: string | null;
  name?: string | null;
  description?: string | null;
  supplier_id?: string | null;
  category_id?: string | null;
  hs_code_id?: string | null;
  status?: ProductStatus | null;
  unit_cost?: number | string | null;
  unit_price?: number | string | null;
  currency?: string | null;
  unit_of_measure?: string | null;
  minimum_order_qty?: number | null;
  lead_time_days?: number | null;
  weight_kg?: number | string | null;
  dimensions?: string | null;
  origin_country?: string | null;
}

export interface ProductResponse {
  id: string;
  sku: string;
  name: string;
  description: string | null;
  supplier_id: string;
  supplier_name: string | null;
  category_id: string | null;
  category_name: string | null;
  hs_code_id: string | null;
  hs_code: string | null;
  status: ProductStatus;
  unit_cost: number | string;
  unit_price: number | string;
  currency: string;
  unit_of_measure: string;
  minimum_order_qty: number;
  lead_time_days: number | null;
  weight_kg: number | string | null;
  dimensions: string | null;
  origin_country: string;
  images: ProductImageResponse[];
  tags: TagResponse[];
  created_at: string;
  updated_at: string;
}

export interface ProductListResponse {
  items: ProductResponse[];
  pagination: Pagination;
  filters?: ProductFilter | null;
}

// =============================================================================
// PORTFOLIO DTOs
// =============================================================================

export interface PortfolioItemCreate {
  product_id: string;
  sort_order?: number;
  notes?: string | null;
}

export interface PortfolioItemResponse {
  id: string;
  portfolio_id: string;
  product_id: string;
  product_name: string | null;
  product_sku: string | null;
  sort_order: number;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface PortfolioCreate {
  name: string;
  description?: string | null;
  niche_id?: string | null;
  is_active?: boolean;
  items?: PortfolioItemCreate[] | null;
}

export interface PortfolioUpdate {
  name?: string | null;
  description?: string | null;
  niche_id?: string | null;
  is_active?: boolean | null;
}

export interface PortfolioResponse {
  id: string;
  name: string;
  description: string | null;
  niche_id: string | null;
  niche_name: string | null;
  is_active: boolean;
  items: PortfolioItemResponse[];
  item_count: number;
  created_at: string;
  updated_at: string;
}

export interface PortfolioListResponse {
  items: PortfolioResponse[];
  pagination: Pagination;
}

export interface PortfolioFilter {
  niche_id?: string | null;
  is_active?: boolean | null;
  search?: string | null;
}

export interface PortfolioShareTokenResponse {
  token: string;
  portfolio_id: string;
  expires_at: string | null;
}

export interface PortfolioPublicResponse {
  id: string;
  name: string;
  description: string | null;
  niche_name: string | null;
  items: PortfolioItemResponse[];
  item_count: number;
  created_at: string;
}

export interface ReorderProductsRequest {
  product_ids: string[];
}

export interface PortfolioDuplicateRequest {
  new_name: string;
}

export interface PortfolioAddProductRequest {
  curator_notes?: string | null;
}

export interface PortfolioAddItemRequest {
  product_id: string;
  curator_notes?: string | null;
}

export interface PortfolioFromFiltersRequest {
  name: string;
  description?: string | null;
  niche_id?: string | null;
  filters: ProductFilter;
}

// =============================================================================
// CLIENT DTOs
// =============================================================================

export interface ClientCreate {
  company_name: string;
  contact_name?: string | null;
  email?: string | null;
  phone?: string | null;
  whatsapp?: string | null;
  address?: string | null;
  city?: string | null;
  state?: string | null;
  country?: string | null;
  postal_code?: string | null;
  niche_id?: string | null;
  status?: ClientStatus;
  notes?: string | null;
  assigned_to?: string | null;
  source?: ClientSource | null;
  project_deadline?: string | null;
  project_name?: string | null;
  incoterm_preference?: Incoterm | null;
}

export interface ClientUpdate {
  company_name?: string | null;
  contact_name?: string | null;
  email?: string | null;
  phone?: string | null;
  whatsapp?: string | null;
  address?: string | null;
  city?: string | null;
  state?: string | null;
  country?: string | null;
  postal_code?: string | null;
  niche_id?: string | null;
  status?: ClientStatus | null;
  notes?: string | null;
  assigned_to?: string | null;
  source?: ClientSource | null;
  project_deadline?: string | null;
  project_name?: string | null;
  incoterm_preference?: Incoterm | null;
}

export interface ClientResponse {
  id: string;
  company_name: string;
  contact_name: string | null;
  email: string | null;
  phone: string | null;
  whatsapp: string | null;
  address: string | null;
  city: string | null;
  state: string | null;
  country: string | null;
  postal_code: string | null;
  niche_id: string | null;
  niche_name: string | null;
  status: ClientStatus;
  notes: string | null;
  assigned_to: string | null;
  assigned_to_name: string | null;
  source: ClientSource | null;
  project_deadline: string | null;
  project_name: string | null;
  incoterm_preference: Incoterm | null;
  created_at: string;
  updated_at: string;
}

export interface ClientListResponse {
  items: ClientResponse[];
  pagination: Pagination;
}

export interface ClientStatusChange {
  new_status: ClientStatus;
  notes?: string | null;
}

export interface StatusHistoryResponse {
  id: string;
  client_id: string;
  old_status: ClientStatus | null;
  new_status: ClientStatus;
  notes: string | null;
  changed_by: string | null;
  changed_by_name: string | null;
  created_at: string;
}

export interface QuotationSummary {
  total_quotations: number;
  draft_count: number;
  sent_count: number;
  accepted_count: number;
  rejected_count: number;
  expired_count: number;
  total_value: number | string;
}

export interface ClientWithQuotations extends ClientResponse {
  quotation_summary: QuotationSummary;
}

export interface PipelineResponse {
  lead: ClientResponse[];
  qualified: ClientResponse[];
  quoting: ClientResponse[];
  negotiating: ClientResponse[];
  won: ClientResponse[];
  lost: ClientResponse[];
}

export interface TimingFeasibility {
  is_feasible: boolean;
  project_deadline: string | null;
  production_lead_time_days: number;
  shipping_transit_days: number;
  total_lead_time_days: number;
  days_until_deadline: number | null;
  buffer_days: number | null;
  message: string;
}

// =============================================================================
// FREIGHT RATE DTOs
// =============================================================================

export interface FreightRateCreate {
  origin: string;
  destination: string;
  incoterm?: Incoterm;
  rate_per_kg?: number | string | null;
  rate_per_cbm?: number | string | null;
  minimum_charge?: number | string;
  transit_days?: number | null;
  is_active?: boolean;
  valid_from?: string | null;
  valid_until?: string | null;
  notes?: string | null;
}

export interface FreightRateUpdate {
  origin?: string | null;
  destination?: string | null;
  incoterm?: Incoterm | null;
  rate_per_kg?: number | string | null;
  rate_per_cbm?: number | string | null;
  minimum_charge?: number | string | null;
  transit_days?: number | null;
  is_active?: boolean | null;
  valid_from?: string | null;
  valid_until?: string | null;
  notes?: string | null;
}

export interface FreightRateResponse {
  id: string;
  origin: string;
  destination: string;
  incoterm: Incoterm;
  rate_per_kg: number | string | null;
  rate_per_cbm: number | string | null;
  minimum_charge: number | string;
  transit_days: number | null;
  is_active: boolean;
  valid_from: string | null;
  valid_until: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface FreightRateListResponse {
  items: FreightRateResponse[];
  pagination: Pagination;
}

// =============================================================================
// PRICING SETTINGS DTOs
// =============================================================================

export interface PricingSettingCreate {
  setting_key: string;
  setting_value: number | string;
  description?: string | null;
  is_percentage?: boolean;
}

export interface PricingSettingUpdate {
  setting_value?: number | string | null;
  description?: string | null;
  is_percentage?: boolean | null;
}

export interface PricingSettingResponse {
  id: string;
  setting_key: string;
  setting_value: number | string;
  description: string | null;
  is_percentage: boolean;
  created_at: string;
  updated_at: string;
}

export interface PricingSettingsResponse {
  settings: PricingSettingResponse[];
}

// =============================================================================
// QUOTATION ITEM DTOs
// =============================================================================

export interface QuotationItemCreate {
  product_id?: string | null;
  sku?: string | null;
  product_name: string;
  description?: string | null;
  quantity?: number;
  unit_of_measure?: string;
  unit_cost?: number | string;
  unit_price?: number | string;
  markup_percent?: number | string;
  tariff_percent?: number | string;
  tariff_amount?: number | string;
  freight_amount?: number | string;
  sort_order?: number;
  notes?: string | null;
}

export interface QuotationItemUpdate {
  product_id?: string | null;
  sku?: string | null;
  product_name?: string | null;
  description?: string | null;
  quantity?: number | null;
  unit_of_measure?: string | null;
  unit_cost?: number | string | null;
  unit_price?: number | string | null;
  markup_percent?: number | string | null;
  tariff_percent?: number | string | null;
  tariff_amount?: number | string | null;
  freight_amount?: number | string | null;
  sort_order?: number | null;
  notes?: string | null;
}

export interface QuotationItemResponse {
  id: string;
  quotation_id: string;
  product_id: string | null;
  sku: string | null;
  product_name: string;
  description: string | null;
  quantity: number;
  unit_of_measure: string;
  unit_cost: number | string;
  unit_price: number | string;
  markup_percent: number | string;
  tariff_percent: number | string;
  tariff_amount: number | string;
  freight_amount: number | string;
  line_total: number | string;
  sort_order: number;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

// =============================================================================
// QUOTATION DTOs
// =============================================================================

export interface QuotationFilter {
  client_id?: string | null;
  status?: QuotationStatus | null;
  created_by?: string | null;
  date_from?: string | null;
  date_to?: string | null;
  search?: string | null;
}

export interface QuotationCreate {
  quotation_number?: string | null;
  client_id: string;
  status?: QuotationStatus;
  incoterm?: Incoterm;
  currency?: string;
  freight_cost?: number | string;
  insurance_cost?: number | string;
  other_costs?: number | string;
  discount_percent?: number | string;
  notes?: string | null;
  terms_and_conditions?: string | null;
  valid_from?: string | null;
  valid_until?: string | null;
  items?: QuotationItemCreate[] | null;
}

export interface QuotationUpdate {
  status?: QuotationStatus | null;
  incoterm?: Incoterm | null;
  currency?: string | null;
  freight_cost?: number | string | null;
  insurance_cost?: number | string | null;
  other_costs?: number | string | null;
  discount_percent?: number | string | null;
  notes?: string | null;
  terms_and_conditions?: string | null;
  valid_from?: string | null;
  valid_until?: string | null;
}

export interface QuotationResponse {
  id: string;
  quotation_number: string;
  client_id: string;
  client_name: string | null;
  status: QuotationStatus;
  incoterm: Incoterm;
  currency: string;
  subtotal: number | string;
  freight_cost: number | string;
  insurance_cost: number | string;
  other_costs: number | string;
  total: number | string;
  discount_percent: number | string;
  discount_amount: number | string;
  grand_total: number | string;
  notes: string | null;
  terms_and_conditions: string | null;
  valid_from: string | null;
  valid_until: string | null;
  created_by: string | null;
  items: QuotationItemResponse[];
  item_count: number;
  created_at: string;
  updated_at: string;
}

export interface QuotationListResponse {
  items: QuotationResponse[];
  pagination: Pagination;
  filters?: QuotationFilter | null;
}

export interface QuotationPricing {
  quotation_id: string;
  subtotal_fob_usd: number | string;
  tariff_total_usd: number | string;
  freight_intl_usd: number | string;
  freight_national_cop: number | string;
  inspection_usd: number | string;
  insurance_usd: number | string;
  nationalization_cop: number | string;
  subtotal_before_margin_cop: number | string;
  margin_percentage: number | string;
  margin_cop: number | string;
  total_cop: number | string;
  exchange_rate: number | string;
}

export interface QuotationStatusTransition {
  new_status: QuotationStatus;
  notes?: string | null;
}

export interface QuotationClone {
  notes?: string | null;
}

export interface QuotationShareTokenResponse {
  token: string;
  quotation_id: string;
  expires_at: string | null;
}

export interface QuotationPublicItem {
  product_name: string;
  description: string | null;
  quantity: number;
  unit_of_measure: string;
  unit_price: number | string;
  line_total: number | string;
}

export interface QuotationPublicResponse {
  id: string;
  quotation_number: string;
  client_name: string | null;
  status: QuotationStatus;
  incoterm: Incoterm;
  currency: string;
  subtotal: number | string;
  freight_cost: number | string;
  insurance_cost: number | string;
  other_costs: number | string;
  total: number | string;
  discount_percent: number | string;
  grand_total: number | string;
  notes: string | null;
  terms_and_conditions: string | null;
  valid_from: string | null;
  valid_until: string | null;
  items: QuotationPublicItem[];
  item_count: number;
  created_at: string;
}

export interface QuotationSendEmailRequest {
  recipient_email: string;
  recipient_name?: string | null;
  subject?: string | null;
  message?: string | null;
  include_pdf?: boolean;
}

export interface QuotationSendEmailResponse {
  success: boolean;
  message: string;
  sent_at: string | null;
  recipient_email: string;
  mock_mode: boolean;
}

// =============================================================================
// BULK OPERATION DTOs
// =============================================================================

export interface BulkCreateError {
  index: number;
  sku: string | null;
  error: string;
}

export interface BulkCreateResponse {
  successful: ProductResponse[];
  failed: BulkCreateError[];
  total_count: number;
  success_count: number;
  failure_count: number;
}

// =============================================================================
// EXTRACTION DTOs
// =============================================================================

export type ExtractionJobStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface ExtractedProduct {
  sku: string | null;
  name: string | null;
  description: string | null;
  price_fob_usd: number | string | null;
  moq: number | null;
  dimensions: string | null;
  material: string | null;
  suggested_category: string | null;
  image_urls: string[];
  confidence_score: number;
  raw_text: string | null;
  source_page: number | null;
  unit_of_measure: string | null;
}

export interface ExtractionJobDTO {
  job_id: string;
  status: ExtractionJobStatus;
  progress: number;
  total_files: number;
  processed_files: number;
  extracted_products: ExtractedProduct[];
  errors: string[];
  created_at: string;
  updated_at: string;
}

export interface UploadResponseDTO {
  job_id: string;
}

export interface ConfirmImportRequestDTO {
  job_id: string;
  product_indices: number[] | null;
  supplier_id: string;
  category_id?: string;
}

export interface ConfirmImportResponseDTO {
  imported_count: number;
  failed_count: number;
  errors: string[];
}

// =============================================================================
// DASHBOARD DTOs
// =============================================================================

export interface DashboardKPIs {
  totalProducts: number;
  productsAddedThisMonth: number;
  activeSuppliers: number;
  quotationsSentThisWeek: number;
  pipelineValue: number | string;
}

export interface QuotationsByStatus {
  draft: number;
  sent: number;
  viewed: number;
  negotiating: number;
  accepted: number;
  rejected: number;
  expired: number;
}

export interface QuotationTrendPoint {
  date: string;
  sent: number;
  accepted: number;
}

export interface TopQuotedProduct {
  id: string;
  name: string;
  sku: string;
  quoteCount: number;
}

export interface RecentProduct {
  id: string;
  name: string;
  sku: string;
  supplierName: string | null;
  createdAt: string;
}

export interface RecentQuotation {
  id: string;
  quotationNumber: string;
  clientName: string | null;
  status: QuotationStatus;
  grandTotal: number | string;
  createdAt: string;
}

export interface RecentClient {
  id: string;
  companyName: string;
  status: ClientStatus;
  createdAt: string;
}

export interface DashboardStats {
  kpis: DashboardKPIs;
  quotationsByStatus: QuotationsByStatus;
  quotationTrend: QuotationTrendPoint[];
  topQuotedProducts: TopQuotedProduct[];
  recentProducts: RecentProduct[];
  recentQuotations: RecentQuotation[];
  recentClients: RecentClient[];
}

// =============================================================================
// SUPPLIER AUDIT DTOs
// =============================================================================

export type AuditType = 'factory_audit' | 'container_inspection';
export type SupplierType = 'manufacturer' | 'trader' | 'unknown';
export type AuditExtractionStatus = 'pending' | 'processing' | 'completed' | 'failed';
export type ClassificationGrade = 'A' | 'B' | 'C';

export interface MarketsServed {
  south_america?: number;
  north_america?: number;
  europe?: number;
  asia?: number;
  other?: number;
}

export interface SupplierAuditCreate {
  supplier_id: string;
  audit_type?: AuditType;
  document_url: string;
  document_name?: string | null;
  file_size_bytes?: number | null;
  audit_date?: string | null;
  inspector_name?: string | null;
}

export interface SupplierAuditResponse {
  id: string;
  supplier_id: string;
  audit_type: AuditType;
  document_url: string;
  document_name: string | null;
  file_size_bytes: number | null;

  // Extracted data
  supplier_type: SupplierType | null;
  employee_count: number | null;
  factory_area_sqm: number | null;
  production_lines_count: number | null;
  markets_served: MarketsServed | null;
  certifications: string[] | null;
  has_machinery_photos: boolean;
  positive_points: string[] | null;
  negative_points: string[] | null;
  products_verified: string[] | null;

  // Audit metadata
  audit_date: string | null;
  inspector_name: string | null;

  // Processing
  extraction_status: AuditExtractionStatus;
  extraction_raw_response: Record<string, unknown> | null;
  extracted_at: string | null;

  // Classification
  ai_classification: ClassificationGrade | null;
  ai_classification_reason: string | null;
  manual_classification: ClassificationGrade | null;
  classification_notes: string | null;

  // Timestamps
  created_at: string;
  updated_at: string;
}

export interface SupplierAuditListResponse {
  items: SupplierAuditResponse[];
  pagination: Pagination;
}

export interface ClassificationOverride {
  classification: ClassificationGrade;
  notes: string;
}
