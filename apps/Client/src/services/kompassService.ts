/**
 * Kompass Portfolio & Quotation System API Service
 * Provides methods for all Kompass API endpoints
 */

import apiClient from '@/api/clients';
import type {
  // Niche types
  NicheCreate,
  NicheUpdate,
  NicheResponse,
  NicheListResponse,
  // Category types
  CategoryCreate,
  CategoryUpdate,
  CategoryResponse,
  CategoryListResponse,
  CategoryTreeNode,
  // Tag types
  TagCreate,
  TagUpdate,
  TagResponse,
  TagListResponse,
  // HS Code types
  HSCodeCreate,
  HSCodeUpdate,
  HSCodeResponse,
  HSCodeListResponse,
  // Supplier types
  SupplierCreate,
  SupplierUpdate,
  SupplierResponse,
  SupplierListResponse,
  // Product types
  ProductCreate,
  ProductUpdate,
  ProductResponse,
  ProductListResponse,
  ProductFilter,
  ProductImageCreate,
  ProductImageResponse,
  BulkCreateResponse,
  // Portfolio types
  PortfolioCreate,
  PortfolioUpdate,
  PortfolioResponse,
  PortfolioListResponse,
  PortfolioFilter,
  PortfolioShareTokenResponse,
  PortfolioPublicResponse,
  PortfolioAddItemRequest,
  ReorderProductsRequest,
  PortfolioDuplicateRequest,
  PortfolioFromFiltersRequest,
  PortfolioItemResponse,
  // Client types
  ClientCreate,
  ClientUpdate,
  ClientResponse,
  ClientListResponse,
  ClientStatusChange,
  StatusHistoryResponse,
  PipelineResponse,
  TimingFeasibility,
  // Quotation types
  QuotationCreate,
  QuotationUpdate,
  QuotationResponse,
  QuotationListResponse,
  QuotationFilter,
  QuotationPricing,
  QuotationStatusTransition,
  QuotationClone,
  QuotationShareTokenResponse,
  QuotationPublicResponse,
  QuotationSendEmailRequest,
  QuotationSendEmailResponse,
  QuotationItemCreate,
  QuotationItemUpdate,
  QuotationItemResponse,
  // Pricing types
  FreightRateCreate,
  FreightRateUpdate,
  FreightRateResponse,
  FreightRateListResponse,
  PricingSettingUpdate,
  PricingSettingsResponse,
  Incoterm,
  // Extraction types
  ExtractionJobDTO,
  UploadResponseDTO,
  ConfirmImportRequestDTO,
  ConfirmImportResponseDTO,
} from '@/types/kompass';

// =============================================================================
// NICHE SERVICE
// =============================================================================

export const nicheService = {
  async list(page = 1, limit = 20): Promise<NicheListResponse> {
    console.log('INFO [nicheService]: Fetching niches list');
    const response = await apiClient.get<NicheListResponse>('/niches', {
      params: { page, limit },
    });
    return response.data;
  },

  async get(id: string): Promise<NicheResponse> {
    console.log(`INFO [nicheService]: Fetching niche ${id}`);
    const response = await apiClient.get<NicheResponse>(`/niches/${id}`);
    return response.data;
  },

  async create(data: NicheCreate): Promise<NicheResponse> {
    console.log('INFO [nicheService]: Creating niche');
    const response = await apiClient.post<NicheResponse>('/niches', data);
    return response.data;
  },

  async update(id: string, data: NicheUpdate): Promise<NicheResponse> {
    console.log(`INFO [nicheService]: Updating niche ${id}`);
    const response = await apiClient.put<NicheResponse>(`/niches/${id}`, data);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    console.log(`INFO [nicheService]: Deleting niche ${id}`);
    await apiClient.delete(`/niches/${id}`);
  },
};

// =============================================================================
// SUPPLIER SERVICE
// =============================================================================

export const supplierService = {
  async list(
    page = 1,
    limit = 20,
    filters?: { status?: string; search?: string }
  ): Promise<SupplierListResponse> {
    console.log('INFO [supplierService]: Fetching suppliers list');
    const response = await apiClient.get<SupplierListResponse>('/suppliers', {
      params: { page, limit, ...filters },
    });
    return response.data;
  },

  async get(id: string): Promise<SupplierResponse> {
    console.log(`INFO [supplierService]: Fetching supplier ${id}`);
    const response = await apiClient.get<SupplierResponse>(`/suppliers/${id}`);
    return response.data;
  },

  async create(data: SupplierCreate): Promise<SupplierResponse> {
    console.log('INFO [supplierService]: Creating supplier');
    const response = await apiClient.post<SupplierResponse>('/suppliers', data);
    return response.data;
  },

  async update(id: string, data: SupplierUpdate): Promise<SupplierResponse> {
    console.log(`INFO [supplierService]: Updating supplier ${id}`);
    const response = await apiClient.put<SupplierResponse>(`/suppliers/${id}`, data);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    console.log(`INFO [supplierService]: Deleting supplier ${id}`);
    await apiClient.delete(`/suppliers/${id}`);
  },

  async search(query: string): Promise<SupplierResponse[]> {
    console.log(`INFO [supplierService]: Searching suppliers with query: ${query}`);
    const response = await apiClient.get<SupplierResponse[]>('/suppliers/search', {
      params: { q: query },
    });
    return response.data;
  },
};

// =============================================================================
// PRODUCT SERVICE
// =============================================================================

export const productService = {
  async list(
    page = 1,
    limit = 20,
    filters?: ProductFilter
  ): Promise<ProductListResponse> {
    console.log('INFO [productService]: Fetching products list');
    const response = await apiClient.get<ProductListResponse>('/products', {
      params: { page, limit, ...filters },
    });
    return response.data;
  },

  async get(id: string): Promise<ProductResponse> {
    console.log(`INFO [productService]: Fetching product ${id}`);
    const response = await apiClient.get<ProductResponse>(`/products/${id}`);
    return response.data;
  },

  async create(data: ProductCreate): Promise<ProductResponse> {
    console.log('INFO [productService]: Creating product');
    const response = await apiClient.post<ProductResponse>('/products', data);
    return response.data;
  },

  async update(id: string, data: ProductUpdate): Promise<ProductResponse> {
    console.log(`INFO [productService]: Updating product ${id}`);
    const response = await apiClient.put<ProductResponse>(`/products/${id}`, data);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    console.log(`INFO [productService]: Deleting product ${id}`);
    await apiClient.delete(`/products/${id}`);
  },

  async search(query: string): Promise<ProductResponse[]> {
    console.log(`INFO [productService]: Searching products with query: ${query}`);
    const response = await apiClient.get<ProductResponse[]>('/products/search', {
      params: { q: query },
    });
    return response.data;
  },

  async bulkCreate(products: ProductCreate[]): Promise<BulkCreateResponse> {
    console.log(`INFO [productService]: Bulk creating ${products.length} products`);
    const response = await apiClient.post<BulkCreateResponse>('/products/bulk', { products });
    return response.data;
  },

  async addImage(productId: string, image: ProductImageCreate): Promise<ProductImageResponse> {
    console.log(`INFO [productService]: Adding image to product ${productId}`);
    const response = await apiClient.post<ProductImageResponse>(
      `/products/${productId}/images`,
      image
    );
    return response.data;
  },

  async removeImage(productId: string, imageId: string): Promise<void> {
    console.log(`INFO [productService]: Removing image ${imageId} from product ${productId}`);
    await apiClient.delete(`/products/${productId}/images/${imageId}`);
  },

  async setPrimaryImage(productId: string, imageId: string): Promise<ProductImageResponse> {
    console.log(`INFO [productService]: Setting primary image ${imageId} for product ${productId}`);
    const response = await apiClient.put<ProductImageResponse>(
      `/products/${productId}/images/${imageId}/primary`
    );
    return response.data;
  },

  async addTag(productId: string, tagId: string): Promise<void> {
    console.log(`INFO [productService]: Adding tag ${tagId} to product ${productId}`);
    await apiClient.post(`/products/${productId}/tags/${tagId}`);
  },

  async removeTag(productId: string, tagId: string): Promise<void> {
    console.log(`INFO [productService]: Removing tag ${tagId} from product ${productId}`);
    await apiClient.delete(`/products/${productId}/tags/${tagId}`);
  },
};

// =============================================================================
// CATEGORY SERVICE
// =============================================================================

export const categoryService = {
  async list(page = 1, limit = 20): Promise<CategoryListResponse> {
    console.log('INFO [categoryService]: Fetching categories list');
    const response = await apiClient.get<CategoryListResponse>('/categories', {
      params: { page, limit },
    });
    return response.data;
  },

  async getTree(): Promise<CategoryTreeNode[]> {
    console.log('INFO [categoryService]: Fetching category tree');
    const response = await apiClient.get<CategoryTreeNode[]>('/categories/tree');
    return response.data;
  },

  async get(id: string): Promise<CategoryResponse> {
    console.log(`INFO [categoryService]: Fetching category ${id}`);
    const response = await apiClient.get<CategoryResponse>(`/categories/${id}`);
    return response.data;
  },

  async create(data: CategoryCreate): Promise<CategoryResponse> {
    console.log('INFO [categoryService]: Creating category');
    const response = await apiClient.post<CategoryResponse>('/categories', data);
    return response.data;
  },

  async update(id: string, data: CategoryUpdate): Promise<CategoryResponse> {
    console.log(`INFO [categoryService]: Updating category ${id}`);
    const response = await apiClient.put<CategoryResponse>(`/categories/${id}`, data);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    console.log(`INFO [categoryService]: Deleting category ${id}`);
    await apiClient.delete(`/categories/${id}`);
  },

  async move(id: string, parentId: string | null): Promise<CategoryResponse> {
    console.log(`INFO [categoryService]: Moving category ${id} to parent ${parentId}`);
    const response = await apiClient.put<CategoryResponse>(`/categories/${id}/move`, {
      parent_id: parentId,
    });
    return response.data;
  },
};

// =============================================================================
// TAG SERVICE
// =============================================================================

export const tagService = {
  async list(page = 1, limit = 20): Promise<TagListResponse> {
    console.log('INFO [tagService]: Fetching tags list');
    const response = await apiClient.get<TagListResponse>('/tags', {
      params: { page, limit },
    });
    return response.data;
  },

  async get(id: string): Promise<TagResponse> {
    console.log(`INFO [tagService]: Fetching tag ${id}`);
    const response = await apiClient.get<TagResponse>(`/tags/${id}`);
    return response.data;
  },

  async create(data: TagCreate): Promise<TagResponse> {
    console.log('INFO [tagService]: Creating tag');
    const response = await apiClient.post<TagResponse>('/tags', data);
    return response.data;
  },

  async update(id: string, data: TagUpdate): Promise<TagResponse> {
    console.log(`INFO [tagService]: Updating tag ${id}`);
    const response = await apiClient.put<TagResponse>(`/tags/${id}`, data);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    console.log(`INFO [tagService]: Deleting tag ${id}`);
    await apiClient.delete(`/tags/${id}`);
  },

  async search(query: string): Promise<TagResponse[]> {
    console.log(`INFO [tagService]: Searching tags with query: ${query}`);
    const response = await apiClient.get<TagResponse[]>('/tags/search', {
      params: { q: query },
    });
    return response.data;
  },
};

// =============================================================================
// PORTFOLIO SERVICE
// =============================================================================

export const portfolioService = {
  async list(
    page = 1,
    limit = 20,
    filters?: PortfolioFilter
  ): Promise<PortfolioListResponse> {
    console.log('INFO [portfolioService]: Fetching portfolios list');
    const response = await apiClient.get<PortfolioListResponse>('/portfolios', {
      params: { page, limit, ...filters },
    });
    return response.data;
  },

  async get(id: string): Promise<PortfolioResponse> {
    console.log(`INFO [portfolioService]: Fetching portfolio ${id}`);
    const response = await apiClient.get<PortfolioResponse>(`/portfolios/${id}`);
    return response.data;
  },

  async create(data: PortfolioCreate): Promise<PortfolioResponse> {
    console.log('INFO [portfolioService]: Creating portfolio');
    const response = await apiClient.post<PortfolioResponse>('/portfolios', data);
    return response.data;
  },

  async update(id: string, data: PortfolioUpdate): Promise<PortfolioResponse> {
    console.log(`INFO [portfolioService]: Updating portfolio ${id}`);
    const response = await apiClient.put<PortfolioResponse>(`/portfolios/${id}`, data);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    console.log(`INFO [portfolioService]: Deleting portfolio ${id}`);
    await apiClient.delete(`/portfolios/${id}`);
  },

  async addItem(portfolioId: string, data: PortfolioAddItemRequest): Promise<PortfolioItemResponse> {
    console.log(`INFO [portfolioService]: Adding item to portfolio ${portfolioId}`);
    const response = await apiClient.post<PortfolioItemResponse>(
      `/portfolios/${portfolioId}/items`,
      data
    );
    return response.data;
  },

  async removeItem(portfolioId: string, itemId: string): Promise<void> {
    console.log(`INFO [portfolioService]: Removing item ${itemId} from portfolio ${portfolioId}`);
    await apiClient.delete(`/portfolios/${portfolioId}/items/${itemId}`);
  },

  async reorderItems(portfolioId: string, data: ReorderProductsRequest): Promise<PortfolioResponse> {
    console.log(`INFO [portfolioService]: Reordering items in portfolio ${portfolioId}`);
    const response = await apiClient.put<PortfolioResponse>(
      `/portfolios/${portfolioId}/reorder`,
      data
    );
    return response.data;
  },

  async duplicate(portfolioId: string, data: PortfolioDuplicateRequest): Promise<PortfolioResponse> {
    console.log(`INFO [portfolioService]: Duplicating portfolio ${portfolioId}`);
    const response = await apiClient.post<PortfolioResponse>(
      `/portfolios/${portfolioId}/duplicate`,
      data
    );
    return response.data;
  },

  async getShareToken(portfolioId: string): Promise<PortfolioShareTokenResponse> {
    console.log(`INFO [portfolioService]: Getting share token for portfolio ${portfolioId}`);
    const response = await apiClient.post<PortfolioShareTokenResponse>(
      `/portfolios/${portfolioId}/share`
    );
    return response.data;
  },

  async getByShareToken(token: string): Promise<PortfolioPublicResponse> {
    console.log('INFO [portfolioService]: Fetching portfolio by share token');
    const response = await apiClient.get<PortfolioPublicResponse>(`/portfolios/share/${token}`);
    return response.data;
  },

  async exportPdf(portfolioId: string): Promise<Blob> {
    console.log(`INFO [portfolioService]: Exporting portfolio ${portfolioId} as PDF`);
    const response = await apiClient.get(`/portfolios/${portfolioId}/export/pdf`, {
      responseType: 'blob',
    });
    return response.data;
  },

  async createFromFilters(data: PortfolioFromFiltersRequest): Promise<PortfolioResponse> {
    console.log('INFO [portfolioService]: Creating portfolio from filters');
    const response = await apiClient.post<PortfolioResponse>('/portfolios/from-filters', data);
    return response.data;
  },
};

// =============================================================================
// CLIENT SERVICE
// =============================================================================

export const clientService = {
  async list(
    page = 1,
    limit = 20,
    filters?: { status?: string; niche_id?: string; search?: string }
  ): Promise<ClientListResponse> {
    console.log('INFO [clientService]: Fetching clients list');
    const response = await apiClient.get<ClientListResponse>('/clients', {
      params: { page, limit, ...filters },
    });
    return response.data;
  },

  async get(id: string): Promise<ClientResponse> {
    console.log(`INFO [clientService]: Fetching client ${id}`);
    const response = await apiClient.get<ClientResponse>(`/clients/${id}`);
    return response.data;
  },

  async create(data: ClientCreate): Promise<ClientResponse> {
    console.log('INFO [clientService]: Creating client');
    const response = await apiClient.post<ClientResponse>('/clients', data);
    return response.data;
  },

  async update(id: string, data: ClientUpdate): Promise<ClientResponse> {
    console.log(`INFO [clientService]: Updating client ${id}`);
    const response = await apiClient.put<ClientResponse>(`/clients/${id}`, data);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    console.log(`INFO [clientService]: Deleting client ${id}`);
    await apiClient.delete(`/clients/${id}`);
  },

  async search(query: string): Promise<ClientResponse[]> {
    console.log(`INFO [clientService]: Searching clients with query: ${query}`);
    const response = await apiClient.get<ClientResponse[]>('/clients/search', {
      params: { q: query },
    });
    return response.data;
  },

  async updateStatus(id: string, data: ClientStatusChange): Promise<ClientResponse> {
    console.log(`INFO [clientService]: Updating status for client ${id}`);
    const response = await apiClient.put<ClientResponse>(`/clients/${id}/status`, data);
    return response.data;
  },

  async getStatusHistory(id: string): Promise<StatusHistoryResponse[]> {
    console.log(`INFO [clientService]: Fetching status history for client ${id}`);
    const response = await apiClient.get<StatusHistoryResponse[]>(`/clients/${id}/status-history`);
    return response.data;
  },

  async getPipeline(): Promise<PipelineResponse> {
    console.log('INFO [clientService]: Fetching pipeline view');
    const response = await apiClient.get<PipelineResponse>('/clients/pipeline');
    return response.data;
  },

  async checkTimingFeasibility(id: string): Promise<TimingFeasibility> {
    console.log(`INFO [clientService]: Checking timing feasibility for client ${id}`);
    const response = await apiClient.get<TimingFeasibility>(`/clients/${id}/timing-feasibility`);
    return response.data;
  },
};

// =============================================================================
// QUOTATION SERVICE
// =============================================================================

export const quotationService = {
  async list(
    page = 1,
    limit = 20,
    filters?: QuotationFilter
  ): Promise<QuotationListResponse> {
    console.log('INFO [quotationService]: Fetching quotations list');
    const response = await apiClient.get<QuotationListResponse>('/quotations', {
      params: { page, limit, ...filters },
    });
    return response.data;
  },

  async get(id: string): Promise<QuotationResponse> {
    console.log(`INFO [quotationService]: Fetching quotation ${id}`);
    const response = await apiClient.get<QuotationResponse>(`/quotations/${id}`);
    return response.data;
  },

  async create(data: QuotationCreate): Promise<QuotationResponse> {
    console.log('INFO [quotationService]: Creating quotation');
    const response = await apiClient.post<QuotationResponse>('/quotations', data);
    return response.data;
  },

  async update(id: string, data: QuotationUpdate): Promise<QuotationResponse> {
    console.log(`INFO [quotationService]: Updating quotation ${id}`);
    const response = await apiClient.put<QuotationResponse>(`/quotations/${id}`, data);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    console.log(`INFO [quotationService]: Deleting quotation ${id}`);
    await apiClient.delete(`/quotations/${id}`);
  },

  async calculate(id: string): Promise<QuotationPricing> {
    console.log(`INFO [quotationService]: Calculating pricing for quotation ${id}`);
    const response = await apiClient.post<QuotationPricing>(`/quotations/${id}/calculate`);
    return response.data;
  },

  async updateStatus(id: string, data: QuotationStatusTransition): Promise<QuotationResponse> {
    console.log(`INFO [quotationService]: Updating status for quotation ${id}`);
    const response = await apiClient.put<QuotationResponse>(`/quotations/${id}/status`, data);
    return response.data;
  },

  async clone(id: string, data?: QuotationClone): Promise<QuotationResponse> {
    console.log(`INFO [quotationService]: Cloning quotation ${id}`);
    const response = await apiClient.post<QuotationResponse>(`/quotations/${id}/clone`, data || {});
    return response.data;
  },

  async getShareToken(id: string): Promise<QuotationShareTokenResponse> {
    console.log(`INFO [quotationService]: Getting share token for quotation ${id}`);
    const response = await apiClient.post<QuotationShareTokenResponse>(`/quotations/${id}/share`);
    return response.data;
  },

  async getByShareToken(token: string): Promise<QuotationPublicResponse> {
    console.log('INFO [quotationService]: Fetching quotation by share token');
    const response = await apiClient.get<QuotationPublicResponse>(`/quotations/share/${token}`);
    return response.data;
  },

  async exportPdf(id: string): Promise<Blob> {
    console.log(`INFO [quotationService]: Exporting quotation ${id} as PDF`);
    const response = await apiClient.get(`/quotations/${id}/export/pdf`, {
      responseType: 'blob',
    });
    return response.data;
  },

  async sendEmail(id: string, data: QuotationSendEmailRequest): Promise<QuotationSendEmailResponse> {
    console.log(`INFO [quotationService]: Sending quotation ${id} via email`);
    const response = await apiClient.post<QuotationSendEmailResponse>(
      `/quotations/${id}/send`,
      data
    );
    return response.data;
  },

  async addItem(quotationId: string, item: QuotationItemCreate): Promise<QuotationItemResponse> {
    console.log(`INFO [quotationService]: Adding item to quotation ${quotationId}`);
    const response = await apiClient.post<QuotationItemResponse>(
      `/quotations/${quotationId}/items`,
      item
    );
    return response.data;
  },

  async updateItem(
    quotationId: string,
    itemId: string,
    item: QuotationItemUpdate
  ): Promise<QuotationItemResponse> {
    console.log(`INFO [quotationService]: Updating item ${itemId} in quotation ${quotationId}`);
    const response = await apiClient.put<QuotationItemResponse>(
      `/quotations/${quotationId}/items/${itemId}`,
      item
    );
    return response.data;
  },

  async deleteItem(quotationId: string, itemId: string): Promise<void> {
    console.log(`INFO [quotationService]: Deleting item ${itemId} from quotation ${quotationId}`);
    await apiClient.delete(`/quotations/${quotationId}/items/${itemId}`);
  },
};

// =============================================================================
// PRICING SERVICE
// =============================================================================

export const pricingService = {
  // HS Codes
  async listHsCodes(page = 1, limit = 20): Promise<HSCodeListResponse> {
    console.log('INFO [pricingService]: Fetching HS codes list');
    const response = await apiClient.get<HSCodeListResponse>('/pricing/hs-codes', {
      params: { page, limit },
    });
    return response.data;
  },

  async getHsCode(id: string): Promise<HSCodeResponse> {
    console.log(`INFO [pricingService]: Fetching HS code ${id}`);
    const response = await apiClient.get<HSCodeResponse>(`/pricing/hs-codes/${id}`);
    return response.data;
  },

  async createHsCode(data: HSCodeCreate): Promise<HSCodeResponse> {
    console.log('INFO [pricingService]: Creating HS code');
    const response = await apiClient.post<HSCodeResponse>('/pricing/hs-codes', data);
    return response.data;
  },

  async updateHsCode(id: string, data: HSCodeUpdate): Promise<HSCodeResponse> {
    console.log(`INFO [pricingService]: Updating HS code ${id}`);
    const response = await apiClient.put<HSCodeResponse>(`/pricing/hs-codes/${id}`, data);
    return response.data;
  },

  async deleteHsCode(id: string): Promise<void> {
    console.log(`INFO [pricingService]: Deleting HS code ${id}`);
    await apiClient.delete(`/pricing/hs-codes/${id}`);
  },

  async searchHsCodes(query: string): Promise<HSCodeResponse[]> {
    console.log(`INFO [pricingService]: Searching HS codes with query: ${query}`);
    const response = await apiClient.get<HSCodeResponse[]>('/pricing/hs-codes/search', {
      params: { q: query },
    });
    return response.data;
  },

  // Freight Rates
  async listFreightRates(page = 1, limit = 20): Promise<FreightRateListResponse> {
    console.log('INFO [pricingService]: Fetching freight rates list');
    const response = await apiClient.get<FreightRateListResponse>('/pricing/freight-rates', {
      params: { page, limit },
    });
    return response.data;
  },

  async getFreightRate(id: string): Promise<FreightRateResponse> {
    console.log(`INFO [pricingService]: Fetching freight rate ${id}`);
    const response = await apiClient.get<FreightRateResponse>(`/pricing/freight-rates/${id}`);
    return response.data;
  },

  async createFreightRate(data: FreightRateCreate): Promise<FreightRateResponse> {
    console.log('INFO [pricingService]: Creating freight rate');
    const response = await apiClient.post<FreightRateResponse>('/pricing/freight-rates', data);
    return response.data;
  },

  async updateFreightRate(id: string, data: FreightRateUpdate): Promise<FreightRateResponse> {
    console.log(`INFO [pricingService]: Updating freight rate ${id}`);
    const response = await apiClient.put<FreightRateResponse>(`/pricing/freight-rates/${id}`, data);
    return response.data;
  },

  async deleteFreightRate(id: string): Promise<void> {
    console.log(`INFO [pricingService]: Deleting freight rate ${id}`);
    await apiClient.delete(`/pricing/freight-rates/${id}`);
  },

  async getActiveFreightRate(
    origin: string,
    destination: string,
    incoterm: Incoterm
  ): Promise<FreightRateResponse | null> {
    console.log(`INFO [pricingService]: Getting active freight rate for ${origin} -> ${destination}`);
    const response = await apiClient.get<FreightRateResponse>('/pricing/freight-rates/active', {
      params: { origin, destination, incoterm },
    });
    return response.data;
  },

  // Pricing Settings
  async getSettings(): Promise<PricingSettingsResponse> {
    console.log('INFO [pricingService]: Fetching pricing settings');
    const response = await apiClient.get<PricingSettingsResponse>('/pricing/settings');
    return response.data;
  },

  async updateSetting(key: string, data: PricingSettingUpdate): Promise<void> {
    console.log(`INFO [pricingService]: Updating pricing setting ${key}`);
    await apiClient.put(`/pricing/settings/${key}`, data);
  },
};

// =============================================================================
// EXTRACTION SERVICE
// =============================================================================

export const extractionService = {
  async uploadFiles(files: FileList): Promise<UploadResponseDTO> {
    console.log(`INFO [extractionService]: Uploading ${files.length} files for extraction`);
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }
    const response = await apiClient.post<UploadResponseDTO>('/extract/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async getJobStatus(jobId: string): Promise<ExtractionJobDTO> {
    console.log(`INFO [extractionService]: Fetching job status for ${jobId}`);
    const response = await apiClient.get<ExtractionJobDTO>(`/extract/${jobId}`);
    return response.data;
  },

  async getJobResults(jobId: string): Promise<ExtractionJobDTO> {
    console.log(`INFO [extractionService]: Fetching job results for ${jobId}`);
    const response = await apiClient.get<ExtractionJobDTO>(`/extract/${jobId}/results`);
    return response.data;
  },

  async confirmImport(request: ConfirmImportRequestDTO): Promise<ConfirmImportResponseDTO> {
    console.log(`INFO [extractionService]: Confirming import for job ${request.job_id}`);
    const response = await apiClient.post<ConfirmImportResponseDTO>(
      `/extract/${request.job_id}/confirm`,
      request
    );
    return response.data;
  },
};
