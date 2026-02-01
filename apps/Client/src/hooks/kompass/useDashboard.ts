import { useState, useCallback, useEffect } from 'react';
import { dashboardService } from '@/services/kompassService';
import type { DashboardStats } from '@/types/kompass';

export interface UseDashboardReturn {
  stats: DashboardStats | null;
  isLoading: boolean;
  error: string | null;
  refreshStats: () => Promise<void>;
}

const defaultStats: DashboardStats = {
  kpis: {
    totalProducts: 0,
    productsAddedThisMonth: 0,
    activeSuppliers: 0,
    quotationsSentThisWeek: 0,
    pipelineValue: 0,
  },
  quotationsByStatus: {
    draft: 0,
    sent: 0,
    viewed: 0,
    negotiating: 0,
    accepted: 0,
    rejected: 0,
    expired: 0,
  },
  quotationTrend: [],
  topQuotedProducts: [],
  recentProducts: [],
  recentQuotations: [],
  recentClients: [],
};

export function useDashboard(): UseDashboardReturn {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = useCallback(async () => {
    console.log('INFO [useDashboard]: Fetching dashboard stats');
    setIsLoading(true);
    setError(null);

    try {
      const data = await dashboardService.getStats();
      setStats(data);
      console.log('INFO [useDashboard]: Dashboard stats loaded successfully');
    } catch (err) {
      console.error('ERROR [useDashboard]: Failed to fetch dashboard stats:', err);
      setError(err instanceof Error ? err.message : 'Failed to load dashboard');
      setStats(defaultStats);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  const refreshStats = useCallback(async () => {
    await fetchStats();
  }, [fetchStats]);

  return {
    stats,
    isLoading,
    error,
    refreshStats,
  };
}
