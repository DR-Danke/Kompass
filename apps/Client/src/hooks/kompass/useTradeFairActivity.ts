import { useState, useCallback, useEffect, useRef } from 'react';
import { tradeFairService } from '@/services/kompassService';
import type { TradeFairActivity } from '@/types/kompass';

const AUTO_REFRESH_INTERVAL = 60_000; // 60 seconds

export interface UseTradeFairActivityReturn {
  activity: TradeFairActivity | null;
  isLoading: boolean;
  error: string | null;
  refreshActivity: () => Promise<void>;
}

export function useTradeFairActivity(): UseTradeFairActivityReturn {
  const [activity, setActivity] = useState<TradeFairActivity | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchActivity = useCallback(async () => {
    console.log('INFO [useTradeFairActivity]: Fetching trade fair activity');
    setIsLoading(true);
    setError(null);

    try {
      const data = await tradeFairService.getActivity();
      setActivity(data);
      console.log('INFO [useTradeFairActivity]: Trade fair activity loaded');
    } catch (err) {
      console.error('ERROR [useTradeFairActivity]: Failed to fetch trade fair activity:', err);
      setError(err instanceof Error ? err.message : 'Failed to load trade fair activity');
      setActivity(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchActivity();

    intervalRef.current = setInterval(fetchActivity, AUTO_REFRESH_INTERVAL);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [fetchActivity]);

  const refreshActivity = useCallback(async () => {
    await fetchActivity();
  }, [fetchActivity]);

  return {
    activity,
    isLoading,
    error,
    refreshActivity,
  };
}
