import { useState, useCallback, useEffect } from 'react';
import { supplierService } from '@/services/kompassService';
import type {
  SupplierWithProductCount,
  SupplierPipelineResponse,
  SupplierPipelineSummary,
  SupplierPipelineStatus,
} from '@/types/kompass';

export type ViewMode = 'kanban' | 'list';

export interface UseSupplierPipelineState {
  pipeline: SupplierPipelineResponse | null;
  summary: SupplierPipelineSummary | null;
  selectedSupplier: SupplierWithProductCount | null;
  viewMode: ViewMode;
  isLoading: boolean;
  isUpdating: boolean;
  error: string | null;
  searchQuery: string;
}

export interface UseSupplierPipelineReturn extends UseSupplierPipelineState {
  fetchPipeline: () => Promise<void>;
  fetchSummary: () => Promise<void>;
  setSelectedSupplier: (supplier: SupplierWithProductCount | null) => void;
  updatePipelineStatus: (supplierId: string, newStatus: SupplierPipelineStatus) => Promise<void>;
  setViewMode: (mode: ViewMode) => void;
  setSearchQuery: (query: string) => void;
  clearError: () => void;
  refreshData: () => Promise<void>;
  getFilteredPipeline: () => SupplierPipelineResponse | null;
}

const INITIAL_PIPELINE: SupplierPipelineResponse = {
  contacted: [],
  potential: [],
  quoted: [],
  certified: [],
  active: [],
  inactive: [],
};

const INITIAL_SUMMARY: SupplierPipelineSummary = {
  contacted: 0,
  potential: 0,
  quoted: 0,
  certified: 0,
  active: 0,
  inactive: 0,
};

export function useSupplierPipeline(): UseSupplierPipelineReturn {
  const [pipeline, setPipeline] = useState<SupplierPipelineResponse | null>(null);
  const [summary, setSummary] = useState<SupplierPipelineSummary | null>(null);
  const [selectedSupplier, setSelectedSupplier] = useState<SupplierWithProductCount | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>('list');
  const [isLoading, setIsLoading] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const fetchPipeline = useCallback(async () => {
    console.log('INFO [useSupplierPipeline]: Fetching pipeline');
    setIsLoading(true);
    setError(null);

    try {
      const response = await supplierService.getPipeline();
      setPipeline(response);
      console.log('INFO [useSupplierPipeline]: Pipeline fetched successfully');
    } catch (err) {
      console.error('ERROR [useSupplierPipeline]: Failed to fetch pipeline:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch pipeline');
      setPipeline(INITIAL_PIPELINE);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchSummary = useCallback(async () => {
    console.log('INFO [useSupplierPipeline]: Fetching summary');

    try {
      const response = await supplierService.getPipelineSummary();
      setSummary(response);
      console.log('INFO [useSupplierPipeline]: Summary fetched successfully');
    } catch (err) {
      console.error('ERROR [useSupplierPipeline]: Failed to fetch summary:', err);
      setSummary(INITIAL_SUMMARY);
    }
  }, []);

  const updatePipelineStatus = useCallback(async (
    supplierId: string,
    newStatus: SupplierPipelineStatus
  ) => {
    console.log(`INFO [useSupplierPipeline]: Updating supplier ${supplierId} status to ${newStatus}`);
    setIsUpdating(true);
    setError(null);

    // Optimistic update for pipeline
    if (pipeline) {
      const allSuppliers = [
        ...pipeline.contacted,
        ...pipeline.potential,
        ...pipeline.quoted,
        ...pipeline.certified,
        ...pipeline.active,
        ...pipeline.inactive,
      ];
      const supplier = allSuppliers.find(s => s.id === supplierId);

      if (supplier) {
        const updatedSupplier = { ...supplier, pipeline_status: newStatus };
        const newPipeline = { ...pipeline };

        // Remove from current column
        (Object.keys(newPipeline) as SupplierPipelineStatus[]).forEach(status => {
          newPipeline[status] = newPipeline[status].filter(s => s.id !== supplierId);
        });

        // Add to new column
        newPipeline[newStatus] = [...newPipeline[newStatus], updatedSupplier];
        setPipeline(newPipeline);
      }
    }

    try {
      await supplierService.updatePipelineStatus(supplierId, newStatus);
      console.log('INFO [useSupplierPipeline]: Supplier status updated successfully');
      // Update summary counts
      await fetchSummary();
    } catch (err) {
      console.error('ERROR [useSupplierPipeline]: Failed to update supplier status:', err);
      setError(err instanceof Error ? err.message : 'Failed to update status');
      // Rollback - refetch pipeline
      await fetchPipeline();
    } finally {
      setIsUpdating(false);
    }
  }, [pipeline, fetchPipeline, fetchSummary]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const refreshData = useCallback(async () => {
    await Promise.all([fetchPipeline(), fetchSummary()]);
  }, [fetchPipeline, fetchSummary]);

  // Filter pipeline by search query
  const getFilteredPipeline = useCallback((): SupplierPipelineResponse | null => {
    if (!pipeline) return null;
    if (!searchQuery.trim()) return pipeline;

    const query = searchQuery.toLowerCase().trim();
    const filterSuppliers = (suppliers: SupplierWithProductCount[]) =>
      suppliers.filter(
        s =>
          s.name.toLowerCase().includes(query) ||
          s.code?.toLowerCase().includes(query) ||
          s.contact_name?.toLowerCase().includes(query) ||
          s.country.toLowerCase().includes(query)
      );

    return {
      contacted: filterSuppliers(pipeline.contacted),
      potential: filterSuppliers(pipeline.potential),
      quoted: filterSuppliers(pipeline.quoted),
      certified: filterSuppliers(pipeline.certified),
      active: filterSuppliers(pipeline.active),
      inactive: filterSuppliers(pipeline.inactive),
    };
  }, [pipeline, searchQuery]);

  // Initial fetch when switching to kanban mode
  useEffect(() => {
    if (viewMode === 'kanban' && !pipeline) {
      fetchPipeline();
      fetchSummary();
    }
  }, [viewMode, pipeline, fetchPipeline, fetchSummary]);

  return {
    pipeline,
    summary,
    selectedSupplier,
    viewMode,
    isLoading,
    isUpdating,
    error,
    searchQuery,
    fetchPipeline,
    fetchSummary,
    setSelectedSupplier,
    updatePipelineStatus,
    setViewMode,
    setSearchQuery,
    clearError,
    refreshData,
    getFilteredPipeline,
  };
}
