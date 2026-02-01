/**
 * Custom hook for category state management
 * Provides CRUD operations and tree management for categories
 */

import { useState, useCallback } from 'react';
import { categoryService } from '@/services/kompassService';
import type {
  CategoryTreeNode,
  CategoryCreate,
  CategoryUpdate,
  CategoryResponse,
} from '@/types/kompass';

interface UseCategoriesReturn {
  categories: CategoryTreeNode[];
  loading: boolean;
  error: string | null;
  fetchCategories: () => Promise<void>;
  createCategory: (data: CategoryCreate) => Promise<CategoryResponse>;
  updateCategory: (id: string, data: CategoryUpdate) => Promise<CategoryResponse>;
  deleteCategory: (id: string) => Promise<void>;
  moveCategory: (id: string, newParentId: string | null) => Promise<CategoryResponse>;
  clearError: () => void;
}

export function useCategories(): UseCategoriesReturn {
  const [categories, setCategories] = useState<CategoryTreeNode[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchCategories = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      console.log('INFO [useCategories]: Fetching category tree');
      const tree = await categoryService.getTree();
      setCategories(tree);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch categories';
      console.log(`ERROR [useCategories]: ${message}`);
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  const createCategory = useCallback(async (data: CategoryCreate): Promise<CategoryResponse> => {
    setLoading(true);
    setError(null);
    try {
      console.log('INFO [useCategories]: Creating category');
      const response = await categoryService.create(data);
      await fetchCategories();
      return response;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to create category';
      console.log(`ERROR [useCategories]: ${message}`);
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [fetchCategories]);

  const updateCategory = useCallback(async (id: string, data: CategoryUpdate): Promise<CategoryResponse> => {
    setLoading(true);
    setError(null);
    try {
      console.log(`INFO [useCategories]: Updating category ${id}`);
      const response = await categoryService.update(id, data);
      await fetchCategories();
      return response;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to update category';
      console.log(`ERROR [useCategories]: ${message}`);
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [fetchCategories]);

  const deleteCategory = useCallback(async (id: string): Promise<void> => {
    setLoading(true);
    setError(null);
    try {
      console.log(`INFO [useCategories]: Deleting category ${id}`);
      await categoryService.delete(id);
      await fetchCategories();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to delete category';
      console.log(`ERROR [useCategories]: ${message}`);
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [fetchCategories]);

  const moveCategory = useCallback(async (id: string, newParentId: string | null): Promise<CategoryResponse> => {
    setLoading(true);
    setError(null);
    try {
      console.log(`INFO [useCategories]: Moving category ${id} to parent ${newParentId}`);
      const response = await categoryService.move(id, newParentId);
      await fetchCategories();
      return response;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to move category';
      console.log(`ERROR [useCategories]: ${message}`);
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [fetchCategories]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    categories,
    loading,
    error,
    fetchCategories,
    createCategory,
    updateCategory,
    deleteCategory,
    moveCategory,
    clearError,
  };
}
