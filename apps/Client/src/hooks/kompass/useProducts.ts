import { useState, useCallback, useEffect } from 'react';
import { productService } from '@/services/kompassService';
import type {
  ProductResponse,
  ProductFilter,
  Pagination,
} from '@/types/kompass';

export type ViewMode = 'grid' | 'table';
export type SortOrder = 'asc' | 'desc';
export type SortField = 'name' | 'unit_price' | 'minimum_order_qty' | 'created_at' | 'updated_at';

export interface ProductFilters extends ProductFilter {
  min_moq?: number | null;
  max_moq?: number | null;
  has_images?: boolean | null;
}

export interface UseProductsState {
  products: ProductResponse[];
  pagination: Pagination;
  filters: ProductFilters;
  sortBy: SortField;
  sortOrder: SortOrder;
  viewMode: ViewMode;
  isLoading: boolean;
  error: string | null;
  selectedIds: string[];
}

export interface UseProductsReturn extends UseProductsState {
  fetchProducts: () => Promise<void>;
  setFilter: <K extends keyof ProductFilters>(key: K, value: ProductFilters[K]) => void;
  setFilters: (filters: Partial<ProductFilters>) => void;
  clearFilters: () => void;
  setPage: (page: number) => void;
  setPageSize: (size: number) => void;
  setSort: (field: SortField, order?: SortOrder) => void;
  toggleViewMode: () => void;
  setViewMode: (mode: ViewMode) => void;
  toggleSelection: (id: string) => void;
  selectAll: () => void;
  clearSelection: () => void;
  isSelected: (id: string) => boolean;
  deleteProduct: (id: string) => Promise<void>;
  bulkDelete: (ids: string[]) => Promise<void>;
  refreshProducts: () => Promise<void>;
}

const DEFAULT_FILTERS: ProductFilters = {
  category_id: null,
  supplier_id: null,
  status: null,
  min_price: null,
  max_price: null,
  search: null,
  tag_ids: null,
  min_moq: null,
  max_moq: null,
  has_images: null,
};

const DEFAULT_PAGINATION: Pagination = {
  page: 1,
  limit: 12,
  total: 0,
  pages: 0,
};

export function useProducts(initialPageSize = 12): UseProductsReturn {
  const [products, setProducts] = useState<ProductResponse[]>([]);
  const [pagination, setPagination] = useState<Pagination>({
    ...DEFAULT_PAGINATION,
    limit: initialPageSize,
  });
  const [filters, setFiltersState] = useState<ProductFilters>(DEFAULT_FILTERS);
  const [sortBy, setSortBy] = useState<SortField>('created_at');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [viewMode, setViewModeState] = useState<ViewMode>('grid');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  const fetchProducts = useCallback(async () => {
    console.log('INFO [useProducts]: Fetching products');
    setIsLoading(true);
    setError(null);

    try {
      const apiFilters: ProductFilter = {
        category_id: filters.category_id,
        supplier_id: filters.supplier_id,
        status: filters.status,
        min_price: filters.min_price,
        max_price: filters.max_price,
        search: filters.search,
        tag_ids: filters.tag_ids,
      };

      const response = await productService.list(
        pagination.page,
        pagination.limit,
        apiFilters
      );

      let sortedProducts = [...response.items];

      if (sortBy) {
        sortedProducts.sort((a, b) => {
          let aVal: string | number;
          let bVal: string | number;

          switch (sortBy) {
            case 'name':
              aVal = a.name.toLowerCase();
              bVal = b.name.toLowerCase();
              break;
            case 'unit_price':
              aVal = typeof a.unit_price === 'string' ? parseFloat(a.unit_price) : a.unit_price;
              bVal = typeof b.unit_price === 'string' ? parseFloat(b.unit_price) : b.unit_price;
              break;
            case 'minimum_order_qty':
              aVal = a.minimum_order_qty;
              bVal = b.minimum_order_qty;
              break;
            case 'created_at':
            case 'updated_at':
              aVal = new Date(a[sortBy]).getTime();
              bVal = new Date(b[sortBy]).getTime();
              break;
            default:
              return 0;
          }

          if (typeof aVal === 'string' && typeof bVal === 'string') {
            return sortOrder === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
          }
          return sortOrder === 'asc' ? (aVal as number) - (bVal as number) : (bVal as number) - (aVal as number);
        });
      }

      if (filters.min_moq !== null && filters.min_moq !== undefined) {
        sortedProducts = sortedProducts.filter((p) => p.minimum_order_qty >= (filters.min_moq as number));
      }
      if (filters.max_moq !== null && filters.max_moq !== undefined) {
        sortedProducts = sortedProducts.filter((p) => p.minimum_order_qty <= (filters.max_moq as number));
      }
      if (filters.has_images === true) {
        sortedProducts = sortedProducts.filter((p) => p.images && p.images.length > 0);
      } else if (filters.has_images === false) {
        sortedProducts = sortedProducts.filter((p) => !p.images || p.images.length === 0);
      }

      setProducts(sortedProducts);
      setPagination(response.pagination);
      console.log(`INFO [useProducts]: Fetched ${sortedProducts.length} products`);
    } catch (err) {
      console.error('ERROR [useProducts]: Failed to fetch products:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch products');
      setProducts([]);
    } finally {
      setIsLoading(false);
    }
  }, [pagination.page, pagination.limit, filters, sortBy, sortOrder]);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  const setFilter = useCallback(<K extends keyof ProductFilters>(key: K, value: ProductFilters[K]) => {
    setFiltersState((prev) => ({ ...prev, [key]: value }));
    setPagination((prev) => ({ ...prev, page: 1 }));
  }, []);

  const setFilters = useCallback((newFilters: Partial<ProductFilters>) => {
    setFiltersState((prev) => ({ ...prev, ...newFilters }));
    setPagination((prev) => ({ ...prev, page: 1 }));
  }, []);

  const clearFilters = useCallback(() => {
    setFiltersState(DEFAULT_FILTERS);
    setPagination((prev) => ({ ...prev, page: 1 }));
  }, []);

  const setPage = useCallback((page: number) => {
    setPagination((prev) => ({ ...prev, page }));
  }, []);

  const setPageSize = useCallback((limit: number) => {
    setPagination((prev) => ({ ...prev, limit, page: 1 }));
  }, []);

  const setSort = useCallback((field: SortField, order?: SortOrder) => {
    if (order) {
      setSortOrder(order);
    } else if (sortBy === field) {
      setSortOrder((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortOrder('asc');
    }
    setSortBy(field);
  }, [sortBy]);

  const toggleViewMode = useCallback(() => {
    setViewModeState((prev) => (prev === 'grid' ? 'table' : 'grid'));
  }, []);

  const setViewMode = useCallback((mode: ViewMode) => {
    setViewModeState(mode);
  }, []);

  const toggleSelection = useCallback((id: string) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  }, []);

  const selectAll = useCallback(() => {
    setSelectedIds(products.map((p) => p.id));
  }, [products]);

  const clearSelection = useCallback(() => {
    setSelectedIds([]);
  }, []);

  const isSelected = useCallback(
    (id: string) => selectedIds.includes(id),
    [selectedIds]
  );

  const deleteProduct = useCallback(async (id: string) => {
    console.log(`INFO [useProducts]: Deleting product ${id}`);
    try {
      await productService.delete(id);
      setSelectedIds((prev) => prev.filter((i) => i !== id));
      await fetchProducts();
    } catch (err) {
      console.error('ERROR [useProducts]: Failed to delete product:', err);
      throw err;
    }
  }, [fetchProducts]);

  const bulkDelete = useCallback(async (ids: string[]) => {
    console.log(`INFO [useProducts]: Bulk deleting ${ids.length} products`);
    try {
      await Promise.all(ids.map((id) => productService.delete(id)));
      setSelectedIds([]);
      await fetchProducts();
    } catch (err) {
      console.error('ERROR [useProducts]: Failed to bulk delete products:', err);
      throw err;
    }
  }, [fetchProducts]);

  const refreshProducts = useCallback(async () => {
    await fetchProducts();
  }, [fetchProducts]);

  return {
    products,
    pagination,
    filters,
    sortBy,
    sortOrder,
    viewMode,
    isLoading,
    error,
    selectedIds,
    fetchProducts,
    setFilter,
    setFilters,
    clearFilters,
    setPage,
    setPageSize,
    setSort,
    toggleViewMode,
    setViewMode,
    toggleSelection,
    selectAll,
    clearSelection,
    isSelected,
    deleteProduct,
    bulkDelete,
    refreshProducts,
  };
}
