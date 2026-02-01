import { useState, useCallback, useEffect } from 'react';
import { quotationService } from '@/services/kompassService';
import type {
  QuotationResponse,
  QuotationFilter,
  QuotationStatus,
  Pagination,
  QuotationShareTokenResponse,
} from '@/types/kompass';

export interface UseQuotationsFilters extends QuotationFilter {
  date_from?: string | null;
  date_to?: string | null;
}

export interface UseQuotationsState {
  quotations: QuotationResponse[];
  pagination: Pagination;
  filters: UseQuotationsFilters;
  isLoading: boolean;
  error: string | null;
}

export interface UseQuotationsReturn extends UseQuotationsState {
  fetchQuotations: () => Promise<void>;
  setFilter: <K extends keyof UseQuotationsFilters>(key: K, value: UseQuotationsFilters[K]) => void;
  setFilters: (filters: Partial<UseQuotationsFilters>) => void;
  clearFilters: () => void;
  setPage: (page: number) => void;
  setPageSize: (size: number) => void;
  deleteQuotation: (id: string) => Promise<void>;
  cloneQuotation: (id: string) => Promise<QuotationResponse>;
  getShareToken: (id: string) => Promise<QuotationShareTokenResponse>;
  updateStatus: (id: string, newStatus: QuotationStatus, notes?: string) => Promise<QuotationResponse>;
  refreshQuotations: () => Promise<void>;
}

const DEFAULT_FILTERS: UseQuotationsFilters = {
  client_id: null,
  status: null,
  created_by: null,
  date_from: null,
  date_to: null,
  search: null,
};

const DEFAULT_PAGINATION: Pagination = {
  page: 1,
  limit: 20,
  total: 0,
  pages: 0,
};

export function useQuotations(initialPageSize = 20): UseQuotationsReturn {
  const [quotations, setQuotations] = useState<QuotationResponse[]>([]);
  const [pagination, setPagination] = useState<Pagination>({
    ...DEFAULT_PAGINATION,
    limit: initialPageSize,
  });
  const [filters, setFiltersState] = useState<UseQuotationsFilters>(DEFAULT_FILTERS);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchQuotations = useCallback(async () => {
    console.log('INFO [useQuotations]: Fetching quotations');
    setIsLoading(true);
    setError(null);

    try {
      const apiFilters: QuotationFilter = {
        client_id: filters.client_id,
        status: filters.status,
        created_by: filters.created_by,
        date_from: filters.date_from,
        date_to: filters.date_to,
        search: filters.search,
      };

      const response = await quotationService.list(
        pagination.page,
        pagination.limit,
        apiFilters
      );

      const items = response.items || [];
      setQuotations(items);
      setPagination(response.pagination);
      console.log(`INFO [useQuotations]: Fetched ${items.length} quotations`);
    } catch (err) {
      console.error('ERROR [useQuotations]: Failed to fetch quotations:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch quotations');
      setQuotations([]);
    } finally {
      setIsLoading(false);
    }
  }, [pagination.page, pagination.limit, filters]);

  useEffect(() => {
    fetchQuotations();
  }, [fetchQuotations]);

  const setFilter = useCallback(<K extends keyof UseQuotationsFilters>(
    key: K,
    value: UseQuotationsFilters[K]
  ) => {
    setFiltersState((prev) => ({ ...prev, [key]: value }));
    setPagination((prev) => ({ ...prev, page: 1 }));
  }, []);

  const setFilters = useCallback((newFilters: Partial<UseQuotationsFilters>) => {
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

  const deleteQuotation = useCallback(async (id: string) => {
    console.log(`INFO [useQuotations]: Deleting quotation ${id}`);
    try {
      await quotationService.delete(id);
      await fetchQuotations();
    } catch (err) {
      console.error('ERROR [useQuotations]: Failed to delete quotation:', err);
      throw err;
    }
  }, [fetchQuotations]);

  const cloneQuotation = useCallback(async (id: string): Promise<QuotationResponse> => {
    console.log(`INFO [useQuotations]: Cloning quotation ${id}`);
    try {
      const cloned = await quotationService.clone(id);
      await fetchQuotations();
      return cloned;
    } catch (err) {
      console.error('ERROR [useQuotations]: Failed to clone quotation:', err);
      throw err;
    }
  }, [fetchQuotations]);

  const getShareToken = useCallback(async (id: string): Promise<QuotationShareTokenResponse> => {
    console.log(`INFO [useQuotations]: Getting share token for quotation ${id}`);
    try {
      return await quotationService.getShareToken(id);
    } catch (err) {
      console.error('ERROR [useQuotations]: Failed to get share token:', err);
      throw err;
    }
  }, []);

  const updateStatus = useCallback(async (
    id: string,
    newStatus: QuotationStatus,
    notes?: string
  ): Promise<QuotationResponse> => {
    console.log(`INFO [useQuotations]: Updating quotation ${id} status to ${newStatus}`);
    try {
      const updated = await quotationService.updateStatus(id, {
        new_status: newStatus,
        notes: notes || null,
      });
      await fetchQuotations();
      return updated;
    } catch (err) {
      console.error('ERROR [useQuotations]: Failed to update quotation status:', err);
      throw err;
    }
  }, [fetchQuotations]);

  const refreshQuotations = useCallback(async () => {
    await fetchQuotations();
  }, [fetchQuotations]);

  return {
    quotations,
    pagination,
    filters,
    isLoading,
    error,
    fetchQuotations,
    setFilter,
    setFilters,
    clearFilters,
    setPage,
    setPageSize,
    deleteQuotation,
    cloneQuotation,
    getShareToken,
    updateStatus,
    refreshQuotations,
  };
}
