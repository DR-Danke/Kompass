/**
 * Custom hook for tag state management
 * Provides CRUD operations and search for tags
 */

import { useState, useCallback, useMemo } from 'react';
import { tagService } from '@/services/kompassService';
import type {
  TagResponse,
  TagCreate,
  TagUpdate,
} from '@/types/kompass';

interface UseTagsReturn {
  tags: TagResponse[];
  filteredTags: TagResponse[];
  loading: boolean;
  error: string | null;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  fetchTags: () => Promise<void>;
  createTag: (data: TagCreate) => Promise<TagResponse>;
  updateTag: (id: string, data: TagUpdate) => Promise<TagResponse>;
  deleteTag: (id: string) => Promise<void>;
  clearError: () => void;
}

export function useTags(): UseTagsReturn {
  const [tags, setTags] = useState<TagResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const filteredTags = useMemo(() => {
    if (!searchQuery.trim()) {
      return tags;
    }
    const query = searchQuery.toLowerCase();
    return tags.filter((tag) => tag.name.toLowerCase().includes(query));
  }, [tags, searchQuery]);

  const fetchTags = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      console.log('INFO [useTags]: Fetching tags list');
      const response = await tagService.list(1, 1000);
      setTags(response.items);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch tags';
      console.log(`ERROR [useTags]: ${message}`);
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  const createTag = useCallback(async (data: TagCreate): Promise<TagResponse> => {
    setLoading(true);
    setError(null);
    try {
      console.log('INFO [useTags]: Creating tag');
      const response = await tagService.create(data);
      await fetchTags();
      return response;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to create tag';
      console.log(`ERROR [useTags]: ${message}`);
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [fetchTags]);

  const updateTag = useCallback(async (id: string, data: TagUpdate): Promise<TagResponse> => {
    setLoading(true);
    setError(null);
    try {
      console.log(`INFO [useTags]: Updating tag ${id}`);
      const response = await tagService.update(id, data);
      await fetchTags();
      return response;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to update tag';
      console.log(`ERROR [useTags]: ${message}`);
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [fetchTags]);

  const deleteTag = useCallback(async (id: string): Promise<void> => {
    setLoading(true);
    setError(null);
    try {
      console.log(`INFO [useTags]: Deleting tag ${id}`);
      await tagService.delete(id);
      await fetchTags();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to delete tag';
      console.log(`ERROR [useTags]: ${message}`);
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [fetchTags]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    tags,
    filteredTags,
    loading,
    error,
    searchQuery,
    setSearchQuery,
    fetchTags,
    createTag,
    updateTag,
    deleteTag,
    clearError,
  };
}
