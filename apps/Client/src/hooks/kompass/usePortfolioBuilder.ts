import { useState, useCallback, useRef } from 'react';
import { portfolioService } from '@/services/kompassService';
import type {
  PortfolioResponse,
  PortfolioItemResponse,
  PortfolioCreate,
  PortfolioUpdate,
} from '@/types/kompass';

export interface PortfolioBuilderItem extends PortfolioItemResponse {
  // Extended item with local-only properties for UI
}

export interface UsePortfolioBuilderState {
  portfolio: PortfolioResponse | null;
  items: PortfolioBuilderItem[];
  isLoading: boolean;
  isSaving: boolean;
  error: string | null;
  isDirty: boolean;
  isNew: boolean;
}

export interface UsePortfolioBuilderReturn extends UsePortfolioBuilderState {
  loadPortfolio: (id: string) => Promise<void>;
  initNewPortfolio: () => void;
  updateMetadata: (data: Partial<PortfolioUpdate>) => void;
  addItem: (productId: string, notes?: string) => Promise<void>;
  removeItem: (itemId: string) => Promise<void>;
  updateItemNotes: (itemId: string, notes: string) => void;
  reorderItems: (productIds: string[]) => Promise<void>;
  savePortfolio: () => Promise<PortfolioResponse>;
  getShareToken: () => Promise<string>;
  exportPdf: () => Promise<void>;
  resetBuilder: () => void;
  isProductInPortfolio: (productId: string) => boolean;
}

export function usePortfolioBuilder(): UsePortfolioBuilderReturn {
  const [portfolio, setPortfolio] = useState<PortfolioResponse | null>(null);
  const [items, setItems] = useState<PortfolioBuilderItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isDirty, setIsDirty] = useState(false);
  const [isNew, setIsNew] = useState(false);

  // Track pending metadata changes
  const pendingMetadata = useRef<Partial<PortfolioUpdate>>({});
  // Track pending notes changes
  const pendingNotes = useRef<Map<string, string>>(new Map());

  const loadPortfolio = useCallback(async (id: string) => {
    console.log(`INFO [usePortfolioBuilder]: Loading portfolio ${id}`);
    setIsLoading(true);
    setError(null);
    setIsNew(false);

    try {
      const data = await portfolioService.get(id);
      setPortfolio(data);
      setItems(data.items);
      pendingMetadata.current = {};
      pendingNotes.current = new Map();
      setIsDirty(false);
      console.log(`INFO [usePortfolioBuilder]: Loaded portfolio with ${data.items.length} items`);
    } catch (err) {
      console.error('ERROR [usePortfolioBuilder]: Failed to load portfolio:', err);
      setError(err instanceof Error ? err.message : 'Failed to load portfolio');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const initNewPortfolio = useCallback(() => {
    console.log('INFO [usePortfolioBuilder]: Initializing new portfolio');
    const newPortfolio: PortfolioResponse = {
      id: '',
      name: 'New Portfolio',
      description: null,
      niche_id: null,
      niche_name: null,
      is_active: true,
      items: [],
      item_count: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    setPortfolio(newPortfolio);
    setItems([]);
    pendingMetadata.current = {};
    pendingNotes.current = new Map();
    setIsDirty(true);
    setIsNew(true);
    setError(null);
  }, []);

  const updateMetadata = useCallback((data: Partial<PortfolioUpdate>) => {
    if (!portfolio) return;

    pendingMetadata.current = { ...pendingMetadata.current, ...data };
    setPortfolio((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        name: data.name !== undefined ? (data.name || prev.name) : prev.name,
        description: data.description !== undefined ? data.description : prev.description,
        niche_id: data.niche_id !== undefined ? data.niche_id : prev.niche_id,
        is_active: data.is_active !== undefined ? (data.is_active ?? prev.is_active) : prev.is_active,
      };
    });
    setIsDirty(true);
    console.log('INFO [usePortfolioBuilder]: Metadata updated');
  }, [portfolio]);

  const addItem = useCallback(async (productId: string, notes?: string) => {
    if (!portfolio) return;

    console.log(`INFO [usePortfolioBuilder]: Adding product ${productId} to portfolio`);

    // Check if already in portfolio
    if (items.some(item => item.product_id === productId)) {
      console.log('INFO [usePortfolioBuilder]: Product already in portfolio');
      return;
    }

    try {
      if (isNew) {
        // For new portfolios, just add locally
        const localItem: PortfolioBuilderItem = {
          id: `temp-${Date.now()}`,
          portfolio_id: portfolio.id,
          product_id: productId,
          product_name: null,
          product_sku: null,
          sort_order: items.length,
          notes: notes || null,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };
        setItems(prev => [...prev, localItem]);
        setIsDirty(true);
      } else {
        // For existing portfolios, call API
        const newItem = await portfolioService.addItem(portfolio.id, {
          product_id: productId,
          curator_notes: notes || null,
        });
        setItems(prev => [...prev, newItem]);
        setPortfolio(prev => prev ? { ...prev, item_count: prev.item_count + 1 } : prev);
      }
    } catch (err) {
      console.error('ERROR [usePortfolioBuilder]: Failed to add item:', err);
      throw err;
    }
  }, [portfolio, items, isNew]);

  const removeItem = useCallback(async (itemId: string) => {
    if (!portfolio) return;

    console.log(`INFO [usePortfolioBuilder]: Removing item ${itemId}`);

    try {
      if (isNew || itemId.startsWith('temp-')) {
        // For new portfolios or temp items, just remove locally
        setItems(prev => prev.filter(item => item.id !== itemId));
        setIsDirty(true);
      } else {
        // For existing portfolios, call API
        await portfolioService.removeItem(portfolio.id, itemId);
        setItems(prev => prev.filter(item => item.id !== itemId));
        setPortfolio(prev => prev ? { ...prev, item_count: prev.item_count - 1 } : prev);
      }
    } catch (err) {
      console.error('ERROR [usePortfolioBuilder]: Failed to remove item:', err);
      throw err;
    }
  }, [portfolio, isNew]);

  const updateItemNotes = useCallback((itemId: string, notes: string) => {
    pendingNotes.current.set(itemId, notes);
    setItems(prev => prev.map(item =>
      item.id === itemId ? { ...item, notes } : item
    ));
    setIsDirty(true);
    console.log(`INFO [usePortfolioBuilder]: Updated notes for item ${itemId}`);
  }, []);

  const reorderItems = useCallback(async (productIds: string[]) => {
    if (!portfolio) return;

    console.log('INFO [usePortfolioBuilder]: Reordering items');

    // Optimistically update local state
    const reorderedItems = productIds
      .map((pid, index) => {
        const item = items.find(i => i.product_id === pid);
        return item ? { ...item, sort_order: index } : null;
      })
      .filter((item): item is PortfolioBuilderItem => item !== null);

    setItems(reorderedItems);

    if (!isNew && portfolio.id) {
      try {
        await portfolioService.reorderItems(portfolio.id, { product_ids: productIds });
      } catch (err) {
        console.error('ERROR [usePortfolioBuilder]: Failed to reorder items:', err);
        // Revert on error - reload portfolio
        if (portfolio.id) {
          await loadPortfolio(portfolio.id);
        }
        throw err;
      }
    } else {
      setIsDirty(true);
    }
  }, [portfolio, items, isNew, loadPortfolio]);

  const savePortfolio = useCallback(async () => {
    if (!portfolio) throw new Error('No portfolio to save');

    console.log('INFO [usePortfolioBuilder]: Saving portfolio');
    setIsSaving(true);

    try {
      let savedPortfolio: PortfolioResponse;

      if (isNew) {
        // Create new portfolio
        const createData: PortfolioCreate = {
          name: portfolio.name,
          description: portfolio.description,
          niche_id: portfolio.niche_id,
          is_active: portfolio.is_active,
          items: items.map((item, index) => ({
            product_id: item.product_id,
            sort_order: index,
            notes: item.notes,
          })),
        };
        savedPortfolio = await portfolioService.create(createData);
        setIsNew(false);
      } else {
        // Update existing portfolio
        if (Object.keys(pendingMetadata.current).length > 0) {
          savedPortfolio = await portfolioService.update(portfolio.id, pendingMetadata.current);
        } else {
          savedPortfolio = portfolio;
        }

        // Update item notes if needed
        // Note: In a real app, you might want a batch update endpoint
        // For now, we reload to get updated data
        savedPortfolio = await portfolioService.get(portfolio.id);
      }

      setPortfolio(savedPortfolio);
      setItems(savedPortfolio.items);
      pendingMetadata.current = {};
      pendingNotes.current = new Map();
      setIsDirty(false);

      console.log('INFO [usePortfolioBuilder]: Portfolio saved successfully');
      return savedPortfolio;
    } catch (err) {
      console.error('ERROR [usePortfolioBuilder]: Failed to save portfolio:', err);
      throw err;
    } finally {
      setIsSaving(false);
    }
  }, [portfolio, items, isNew]);

  const getShareToken = useCallback(async () => {
    if (!portfolio || !portfolio.id) throw new Error('No portfolio to share');

    console.log('INFO [usePortfolioBuilder]: Getting share token');
    try {
      const response = await portfolioService.getShareToken(portfolio.id);
      return response.token;
    } catch (err) {
      console.error('ERROR [usePortfolioBuilder]: Failed to get share token:', err);
      throw err;
    }
  }, [portfolio]);

  const exportPdf = useCallback(async () => {
    if (!portfolio || !portfolio.id) throw new Error('No portfolio to export');

    console.log('INFO [usePortfolioBuilder]: Exporting PDF');
    try {
      const blob = await portfolioService.exportPdf(portfolio.id);
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${portfolio.name.replace(/[^a-z0-9]/gi, '_')}_portfolio.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      console.log('INFO [usePortfolioBuilder]: PDF exported successfully');
    } catch (err) {
      console.error('ERROR [usePortfolioBuilder]: Failed to export PDF:', err);
      throw err;
    }
  }, [portfolio]);

  const resetBuilder = useCallback(() => {
    setPortfolio(null);
    setItems([]);
    setIsDirty(false);
    setIsNew(false);
    setError(null);
    pendingMetadata.current = {};
    pendingNotes.current = new Map();
    console.log('INFO [usePortfolioBuilder]: Builder reset');
  }, []);

  const isProductInPortfolio = useCallback((productId: string) => {
    return items.some(item => item.product_id === productId);
  }, [items]);

  return {
    portfolio,
    items,
    isLoading,
    isSaving,
    error,
    isDirty,
    isNew,
    loadPortfolio,
    initNewPortfolio,
    updateMetadata,
    addItem,
    removeItem,
    updateItemNotes,
    reorderItems,
    savePortfolio,
    getShareToken,
    exportPdf,
    resetBuilder,
    isProductInPortfolio,
  };
}
