import { useState, useCallback, useEffect } from 'react';
import { businessCardService } from '@/services/kompassService';
import type {
  BusinessCardCapture,
  BusinessCardCaptureStatus,
  SupplierFromCardResult,
} from '@/types/kompass';

export interface UseCardReviewState {
  captures: BusinessCardCapture[];
  total: number;
  statusFilter: BusinessCardCaptureStatus | null;
  selectedIds: Set<string>;
  isLoading: boolean;
  isProcessing: boolean;
  error: string | null;
}

export interface UseCardReviewReturn extends UseCardReviewState {
  fetchCaptures: (statusFilter?: BusinessCardCaptureStatus | null) => Promise<void>;
  updateField: (captureId: string, fieldName: string, value: string) => Promise<void>;
  approveCard: (captureId: string) => Promise<SupplierFromCardResult>;
  rejectCard: (captureId: string, reason?: string) => Promise<void>;
  batchApprove: (captureIds: string[]) => Promise<void>;
  batchReject: (captureIds: string[], reason?: string) => Promise<void>;
  createSupplierFromCard: (captureId: string) => Promise<SupplierFromCardResult>;
  creatingSupplierIds: Set<string>;
  toggleSelection: (captureId: string) => void;
  toggleSelectAll: () => void;
  setStatusFilter: (status: BusinessCardCaptureStatus | null) => void;
  clearError: () => void;
}

export function useCardReview(): UseCardReviewReturn {
  const [captures, setCaptures] = useState<BusinessCardCapture[]>([]);
  const [total, setTotal] = useState(0);
  const [statusFilter, setStatusFilterState] = useState<BusinessCardCaptureStatus | null>(null);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [isLoading, setIsLoading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [creatingSupplierIds, setCreatingSupplierIds] = useState<Set<string>>(new Set());

  const fetchCaptures = useCallback(async (filter?: BusinessCardCaptureStatus | null) => {
    console.log('INFO [useCardReview]: Fetching captures');
    setIsLoading(true);
    setError(null);

    try {
      const response = await businessCardService.listCaptures(
        filter ?? undefined,
        200,
        0
      );
      setCaptures(response.captures);
      setTotal(response.total);
      setSelectedIds(new Set());
      console.log(`INFO [useCardReview]: Fetched ${response.captures.length} captures`);
    } catch (err) {
      console.error('ERROR [useCardReview]: Failed to fetch captures:', err);
      setError(err instanceof Error ? err.message : 'Error al cargar las capturas');
      setCaptures([]);
      setTotal(0);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updateField = useCallback(async (captureId: string, fieldName: string, value: string) => {
    console.log(`INFO [useCardReview]: Updating field ${fieldName} on ${captureId}`);
    setError(null);

    // Optimistic update
    setCaptures(prev =>
      prev.map(c =>
        c.id === captureId ? { ...c, [fieldName]: value } : c
      )
    );

    try {
      await businessCardService.updateCapture(captureId, { [fieldName]: value } as Partial<BusinessCardCapture>);
      console.log(`INFO [useCardReview]: Field ${fieldName} updated successfully`);
    } catch (err) {
      console.error('ERROR [useCardReview]: Failed to update field:', err);
      setError(err instanceof Error ? err.message : 'Error al actualizar el campo');
      // Rollback
      await fetchCaptures(statusFilter);
    }
  }, [statusFilter, fetchCaptures]);

  const approveCard = useCallback(async (captureId: string): Promise<SupplierFromCardResult> => {
    console.log(`INFO [useCardReview]: Approving card ${captureId}`);
    setIsProcessing(true);
    setError(null);

    try {
      const result = await businessCardService.approveCard(captureId);

      // Update local state based on result
      setCaptures(prev =>
        prev.map(c => {
          if (c.id !== captureId) return c;
          if (result.is_duplicate) {
            return { ...c, status: 'rejected' as BusinessCardCaptureStatus };
          }
          return {
            ...c,
            status: 'confirmed' as BusinessCardCaptureStatus,
            supplier_id: result.supplier_id ?? null,
          };
        })
      );

      console.log(`INFO [useCardReview]: Card approved successfully`);
      return result;
    } catch (err) {
      console.error('ERROR [useCardReview]: Failed to approve card:', err);
      setError(err instanceof Error ? err.message : 'Error al aprobar la tarjeta');
      throw err;
    } finally {
      setIsProcessing(false);
    }
  }, []);

  const rejectCard = useCallback(async (captureId: string, reason?: string) => {
    console.log(`INFO [useCardReview]: Rejecting card ${captureId}`);
    setIsProcessing(true);
    setError(null);

    try {
      const updated = await businessCardService.rejectCard(captureId, reason);

      setCaptures(prev =>
        prev.map(c => (c.id === captureId ? updated : c))
      );

      console.log(`INFO [useCardReview]: Card rejected successfully`);
    } catch (err) {
      console.error('ERROR [useCardReview]: Failed to reject card:', err);
      setError(err instanceof Error ? err.message : 'Error al rechazar la tarjeta');
      throw err;
    } finally {
      setIsProcessing(false);
    }
  }, []);

  const batchApprove = useCallback(async (captureIds: string[]) => {
    console.log(`INFO [useCardReview]: Batch approving ${captureIds.length} cards`);
    setIsProcessing(true);
    setError(null);

    try {
      for (const id of captureIds) {
        try {
          await approveCard(id);
        } catch {
          // Individual failures are logged in approveCard
        }
      }
      setSelectedIds(new Set());
    } finally {
      setIsProcessing(false);
    }
  }, [approveCard]);

  const batchReject = useCallback(async (captureIds: string[], reason?: string) => {
    console.log(`INFO [useCardReview]: Batch rejecting ${captureIds.length} cards`);
    setIsProcessing(true);
    setError(null);

    try {
      for (const id of captureIds) {
        try {
          await rejectCard(id, reason);
        } catch {
          // Individual failures are logged in rejectCard
        }
      }
      setSelectedIds(new Set());
    } finally {
      setIsProcessing(false);
    }
  }, [rejectCard]);

  const createSupplierFromCard = useCallback(async (captureId: string): Promise<SupplierFromCardResult> => {
    console.log(`INFO [useCardReview]: Creating supplier from card ${captureId}`);
    setCreatingSupplierIds(prev => new Set(prev).add(captureId));

    try {
      const result = await businessCardService.createSupplierFromCard(captureId);

      setCaptures(prev =>
        prev.map(c => {
          if (c.id !== captureId) return c;
          if (result.is_duplicate) {
            return { ...c, status: 'rejected' as BusinessCardCaptureStatus };
          }
          return {
            ...c,
            status: 'confirmed' as BusinessCardCaptureStatus,
            supplier_id: result.supplier_id ?? null,
          };
        })
      );

      console.log(`INFO [useCardReview]: Supplier created successfully from card ${captureId}`);
      return result;
    } catch (err) {
      console.error('ERROR [useCardReview]: Failed to create supplier from card:', err);
      throw err;
    } finally {
      setCreatingSupplierIds(prev => {
        const next = new Set(prev);
        next.delete(captureId);
        return next;
      });
    }
  }, []);

  const toggleSelection = useCallback((captureId: string) => {
    setSelectedIds(prev => {
      const next = new Set(prev);
      if (next.has(captureId)) {
        next.delete(captureId);
      } else {
        next.add(captureId);
      }
      return next;
    });
  }, []);

  const toggleSelectAll = useCallback(() => {
    setSelectedIds(prev => {
      if (prev.size === captures.length && captures.length > 0) {
        return new Set();
      }
      return new Set(captures.map(c => c.id));
    });
  }, [captures]);

  const setStatusFilter = useCallback((status: BusinessCardCaptureStatus | null) => {
    setStatusFilterState(status);
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Fetch captures on mount and when statusFilter changes
  useEffect(() => {
    fetchCaptures(statusFilter);
  }, [statusFilter, fetchCaptures]);

  return {
    captures,
    total,
    statusFilter,
    selectedIds,
    isLoading,
    isProcessing,
    error,
    fetchCaptures,
    updateField,
    approveCard,
    rejectCard,
    batchApprove,
    batchReject,
    createSupplierFromCard,
    creatingSupplierIds,
    toggleSelection,
    toggleSelectAll,
    setStatusFilter,
    clearError,
  };
}
