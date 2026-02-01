import { useState, useCallback, useEffect } from 'react';
import { portfolioService } from '@/services/kompassService';
import type {
  PortfolioResponse,
  PortfolioFilter,
  Pagination,
} from '@/types/kompass';

export interface PortfolioFilters extends PortfolioFilter {
  // Additional filter options can be added here
}

export interface UsePortfoliosState {
  portfolios: PortfolioResponse[];
  pagination: Pagination;
  filters: PortfolioFilters;
  isLoading: boolean;
  error: string | null;
}

export interface UsePortfoliosReturn extends UsePortfoliosState {
  fetchPortfolios: () => Promise<void>;
  setFilter: <K extends keyof PortfolioFilters>(key: K, value: PortfolioFilters[K]) => void;
  setFilters: (filters: Partial<PortfolioFilters>) => void;
  clearFilters: () => void;
  setPage: (page: number) => void;
  setPageSize: (size: number) => void;
  deletePortfolio: (id: string) => Promise<void>;
  duplicatePortfolio: (id: string, newName: string) => Promise<PortfolioResponse>;
  getShareToken: (id: string) => Promise<string>;
  refreshPortfolios: () => Promise<void>;
}

const DEFAULT_FILTERS: PortfolioFilters = {
  niche_id: null,
  is_active: null,
  search: null,
};

const DEFAULT_PAGINATION: Pagination = {
  page: 1,
  limit: 12,
  total: 0,
  pages: 0,
};

export function usePortfolios(initialPageSize = 12): UsePortfoliosReturn {
  const [portfolios, setPortfolios] = useState<PortfolioResponse[]>([]);
  const [pagination, setPagination] = useState<Pagination>({
    ...DEFAULT_PAGINATION,
    limit: initialPageSize,
  });
  const [filters, setFiltersState] = useState<PortfolioFilters>(DEFAULT_FILTERS);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPortfolios = useCallback(async () => {
    console.log('INFO [usePortfolios]: Fetching portfolios');
    setIsLoading(true);
    setError(null);

    try {
      const apiFilters: PortfolioFilter = {
        niche_id: filters.niche_id,
        is_active: filters.is_active,
        search: filters.search,
      };

      const response = await portfolioService.list(
        pagination.page,
        pagination.limit,
        apiFilters
      );

      const items = response.items || [];
      setPortfolios(items);
      setPagination(response.pagination);
      console.log(`INFO [usePortfolios]: Fetched ${items.length} portfolios`);
    } catch (err) {
      console.error('ERROR [usePortfolios]: Failed to fetch portfolios:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch portfolios');
      setPortfolios([]);
    } finally {
      setIsLoading(false);
    }
  }, [pagination.page, pagination.limit, filters]);

  useEffect(() => {
    fetchPortfolios();
  }, [fetchPortfolios]);

  const setFilter = useCallback(<K extends keyof PortfolioFilters>(key: K, value: PortfolioFilters[K]) => {
    setFiltersState((prev) => ({ ...prev, [key]: value }));
    setPagination((prev) => ({ ...prev, page: 1 }));
  }, []);

  const setFilters = useCallback((newFilters: Partial<PortfolioFilters>) => {
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

  const deletePortfolio = useCallback(async (id: string) => {
    console.log(`INFO [usePortfolios]: Deleting portfolio ${id}`);
    try {
      await portfolioService.delete(id);
      await fetchPortfolios();
    } catch (err) {
      console.error('ERROR [usePortfolios]: Failed to delete portfolio:', err);
      throw err;
    }
  }, [fetchPortfolios]);

  const duplicatePortfolio = useCallback(async (id: string, newName: string) => {
    console.log(`INFO [usePortfolios]: Duplicating portfolio ${id}`);
    try {
      const duplicated = await portfolioService.duplicate(id, { new_name: newName });
      await fetchPortfolios();
      return duplicated;
    } catch (err) {
      console.error('ERROR [usePortfolios]: Failed to duplicate portfolio:', err);
      throw err;
    }
  }, [fetchPortfolios]);

  const getShareToken = useCallback(async (id: string) => {
    console.log(`INFO [usePortfolios]: Getting share token for portfolio ${id}`);
    try {
      const response = await portfolioService.getShareToken(id);
      return response.token;
    } catch (err) {
      console.error('ERROR [usePortfolios]: Failed to get share token:', err);
      throw err;
    }
  }, []);

  const refreshPortfolios = useCallback(async () => {
    await fetchPortfolios();
  }, [fetchPortfolios]);

  return {
    portfolios,
    pagination,
    filters,
    isLoading,
    error,
    fetchPortfolios,
    setFilter,
    setFilters,
    clearFilters,
    setPage,
    setPageSize,
    deletePortfolio,
    duplicatePortfolio,
    getShareToken,
    refreshPortfolios,
  };
}
