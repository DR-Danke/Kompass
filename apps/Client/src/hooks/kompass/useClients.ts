import { useState, useCallback, useEffect } from 'react';
import { clientService } from '@/services/kompassService';
import type {
  ClientResponse,
  ClientCreate,
  ClientUpdate,
  ClientStatus,
  ClientStatusChange,
  PipelineResponse,
  StatusHistoryResponse,
  ClientWithQuotations,
} from '@/types/kompass';

export type ViewMode = 'kanban' | 'list';

export interface UseClientsState {
  pipeline: PipelineResponse | null;
  clients: ClientResponse[];
  selectedClient: ClientResponse | null;
  clientWithQuotations: ClientWithQuotations | null;
  statusHistory: StatusHistoryResponse[];
  viewMode: ViewMode;
  isLoading: boolean;
  isUpdating: boolean;
  error: string | null;
  searchQuery: string;
}

export interface UseClientsReturn extends UseClientsState {
  fetchPipeline: () => Promise<void>;
  fetchClients: (filters?: { status?: string; niche_id?: string; search?: string }) => Promise<void>;
  setSelectedClient: (client: ClientResponse | null) => void;
  fetchClientWithQuotations: (clientId: string) => Promise<void>;
  fetchStatusHistory: (clientId: string) => Promise<void>;
  updateClientStatus: (clientId: string, newStatus: ClientStatus, notes?: string) => Promise<void>;
  createClient: (data: ClientCreate) => Promise<ClientResponse>;
  updateClient: (clientId: string, data: ClientUpdate) => Promise<ClientResponse>;
  deleteClient: (clientId: string) => Promise<void>;
  setViewMode: (mode: ViewMode) => void;
  setSearchQuery: (query: string) => void;
  clearError: () => void;
  refreshData: () => Promise<void>;
}

const INITIAL_PIPELINE: PipelineResponse = {
  lead: [],
  qualified: [],
  quoting: [],
  negotiating: [],
  won: [],
  lost: [],
};

export function useClients(): UseClientsReturn {
  const [pipeline, setPipeline] = useState<PipelineResponse | null>(null);
  const [clients, setClients] = useState<ClientResponse[]>([]);
  const [selectedClient, setSelectedClient] = useState<ClientResponse | null>(null);
  const [clientWithQuotations, setClientWithQuotations] = useState<ClientWithQuotations | null>(null);
  const [statusHistory, setStatusHistory] = useState<StatusHistoryResponse[]>([]);
  const [viewMode, setViewMode] = useState<ViewMode>('kanban');
  const [isLoading, setIsLoading] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const fetchPipeline = useCallback(async () => {
    console.log('INFO [useClients]: Fetching pipeline');
    setIsLoading(true);
    setError(null);

    try {
      const response = await clientService.getPipeline();
      setPipeline(response);
      console.log('INFO [useClients]: Pipeline fetched successfully');
    } catch (err) {
      console.error('ERROR [useClients]: Failed to fetch pipeline:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch pipeline');
      setPipeline(INITIAL_PIPELINE);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchClients = useCallback(async (
    filters?: { status?: string; niche_id?: string; search?: string }
  ) => {
    console.log('INFO [useClients]: Fetching clients list');
    setIsLoading(true);
    setError(null);

    try {
      const response = await clientService.list(1, 100, filters);
      setClients(response.items);
      console.log(`INFO [useClients]: Fetched ${response.items.length} clients`);
    } catch (err) {
      console.error('ERROR [useClients]: Failed to fetch clients:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch clients');
      setClients([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchClientWithQuotations = useCallback(async (clientId: string) => {
    console.log(`INFO [useClients]: Fetching client ${clientId} with quotations`);

    try {
      const response = await clientService.getClientWithQuotations(clientId);
      setClientWithQuotations(response);
    } catch (err) {
      console.error('ERROR [useClients]: Failed to fetch client with quotations:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch client details');
    }
  }, []);

  const fetchStatusHistory = useCallback(async (clientId: string) => {
    console.log(`INFO [useClients]: Fetching status history for client ${clientId}`);

    try {
      const response = await clientService.getStatusHistory(clientId);
      setStatusHistory(response);
    } catch (err) {
      console.error('ERROR [useClients]: Failed to fetch status history:', err);
      setStatusHistory([]);
    }
  }, []);

  const updateClientStatus = useCallback(async (
    clientId: string,
    newStatus: ClientStatus,
    notes?: string
  ) => {
    console.log(`INFO [useClients]: Updating client ${clientId} status to ${newStatus}`);
    setIsUpdating(true);
    setError(null);

    // Optimistic update for pipeline
    if (pipeline) {
      const allClients = [
        ...pipeline.lead,
        ...pipeline.qualified,
        ...pipeline.quoting,
        ...pipeline.negotiating,
        ...pipeline.won,
        ...pipeline.lost,
      ];
      const client = allClients.find(c => c.id === clientId);

      if (client) {
        const updatedClient = { ...client, status: newStatus };
        const newPipeline = { ...pipeline };

        // Remove from current column
        Object.keys(newPipeline).forEach(key => {
          const status = key as ClientStatus;
          newPipeline[status] = newPipeline[status].filter(c => c.id !== clientId);
        });

        // Add to new column
        newPipeline[newStatus] = [...newPipeline[newStatus], updatedClient];
        setPipeline(newPipeline);
      }
    }

    try {
      const statusChange: ClientStatusChange = {
        new_status: newStatus,
        notes: notes || null,
      };
      await clientService.updateStatus(clientId, statusChange);
      console.log(`INFO [useClients]: Client status updated successfully`);
    } catch (err) {
      console.error('ERROR [useClients]: Failed to update client status:', err);
      setError(err instanceof Error ? err.message : 'Failed to update status');
      // Rollback - refetch pipeline
      await fetchPipeline();
    } finally {
      setIsUpdating(false);
    }
  }, [pipeline, fetchPipeline]);

  const createClient = useCallback(async (data: ClientCreate): Promise<ClientResponse> => {
    console.log('INFO [useClients]: Creating new client');
    setError(null);

    try {
      const response = await clientService.create(data);
      console.log(`INFO [useClients]: Client created with ID ${response.id}`);
      // Refresh data
      await fetchPipeline();
      return response;
    } catch (err) {
      console.error('ERROR [useClients]: Failed to create client:', err);
      const message = err instanceof Error ? err.message : 'Failed to create client';
      setError(message);
      throw err;
    }
  }, [fetchPipeline]);

  const updateClient = useCallback(async (
    clientId: string,
    data: ClientUpdate
  ): Promise<ClientResponse> => {
    console.log(`INFO [useClients]: Updating client ${clientId}`);
    setError(null);

    try {
      const response = await clientService.update(clientId, data);
      console.log(`INFO [useClients]: Client ${clientId} updated successfully`);
      // Refresh data
      await fetchPipeline();
      return response;
    } catch (err) {
      console.error('ERROR [useClients]: Failed to update client:', err);
      const message = err instanceof Error ? err.message : 'Failed to update client';
      setError(message);
      throw err;
    }
  }, [fetchPipeline]);

  const deleteClient = useCallback(async (clientId: string) => {
    console.log(`INFO [useClients]: Deleting client ${clientId}`);
    setError(null);

    try {
      await clientService.delete(clientId);
      console.log(`INFO [useClients]: Client ${clientId} deleted successfully`);
      // Refresh data
      await fetchPipeline();
    } catch (err) {
      console.error('ERROR [useClients]: Failed to delete client:', err);
      const message = err instanceof Error ? err.message : 'Failed to delete client';
      setError(message);
      throw err;
    }
  }, [fetchPipeline]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const refreshData = useCallback(async () => {
    if (viewMode === 'kanban') {
      await fetchPipeline();
    } else {
      await fetchClients({ search: searchQuery || undefined });
    }
  }, [viewMode, searchQuery, fetchPipeline, fetchClients]);

  // Initial fetch
  useEffect(() => {
    fetchPipeline();
  }, [fetchPipeline]);

  // Refetch when view mode changes
  useEffect(() => {
    if (viewMode === 'list') {
      fetchClients({ search: searchQuery || undefined });
    }
  }, [viewMode, fetchClients, searchQuery]);

  return {
    pipeline,
    clients,
    selectedClient,
    clientWithQuotations,
    statusHistory,
    viewMode,
    isLoading,
    isUpdating,
    error,
    searchQuery,
    fetchPipeline,
    fetchClients,
    setSelectedClient,
    fetchClientWithQuotations,
    fetchStatusHistory,
    updateClientStatus,
    createClient,
    updateClient,
    deleteClient,
    setViewMode,
    setSearchQuery,
    clearError,
    refreshData,
  };
}
