/**
 * CategoriesPage Component
 * Management page for product categories and tags
 */

import React, { useEffect, useState, useCallback } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  TextField,
  InputAdornment,
  Grid,
  Skeleton,
  Alert,
  Snackbar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  IconButton,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import SearchIcon from '@mui/icons-material/Search';
import RefreshIcon from '@mui/icons-material/Refresh';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import { useCategories } from '@/hooks/useCategories';
import { useTags } from '@/hooks/useTags';
import { CategoryTree } from '@/components/kompass/CategoryTree';
import { CategoryDialog } from '@/components/kompass/CategoryDialog';
import { TagChip } from '@/components/kompass/TagChip';
import { TagDialog } from '@/components/kompass/TagDialog';
import type { CategoryTreeNode, CategoryCreate, CategoryUpdate, TagResponse, TagCreate, TagUpdate } from '@/types/kompass';

interface ConfirmDialogState {
  open: boolean;
  title: string;
  message: string;
  onConfirm: () => void;
}

const CategoriesPage: React.FC = () => {
  const {
    categories,
    loading: categoriesLoading,
    error: categoriesError,
    fetchCategories,
    createCategory,
    updateCategory,
    deleteCategory,
    moveCategory,
    clearError: clearCategoriesError,
  } = useCategories();

  const {
    filteredTags,
    loading: tagsLoading,
    error: tagsError,
    searchQuery,
    setSearchQuery,
    fetchTags,
    createTag,
    updateTag,
    deleteTag,
    clearError: clearTagsError,
  } = useTags();

  const [categoryDialogOpen, setCategoryDialogOpen] = useState(false);
  const [editingCategory, setEditingCategory] = useState<CategoryTreeNode | null>(null);
  const [addChildParentId, setAddChildParentId] = useState<string | null>(null);
  const [addChildParentName, setAddChildParentName] = useState<string | null>(null);

  const [tagDialogOpen, setTagDialogOpen] = useState(false);
  const [editingTag, setEditingTag] = useState<TagResponse | null>(null);

  const [confirmDialog, setConfirmDialog] = useState<ConfirmDialogState>({
    open: false,
    title: '',
    message: '',
    onConfirm: () => {},
  });

  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error';
  }>({
    open: false,
    message: '',
    severity: 'success',
  });

  useEffect(() => {
    fetchCategories();
    fetchTags();
  }, [fetchCategories, fetchTags]);

  const showSnackbar = useCallback((message: string, severity: 'success' | 'error') => {
    setSnackbar({ open: true, message, severity });
  }, []);

  const handleCloseSnackbar = () => {
    setSnackbar((prev) => ({ ...prev, open: false }));
  };

  const handleOpenAddRootCategory = () => {
    setEditingCategory(null);
    setAddChildParentId(null);
    setAddChildParentName(null);
    setCategoryDialogOpen(true);
  };

  const handleOpenAddChildCategory = (parentId: string, parentName: string) => {
    setEditingCategory(null);
    setAddChildParentId(parentId);
    setAddChildParentName(parentName);
    setCategoryDialogOpen(true);
  };

  const handleOpenEditCategory = (category: CategoryTreeNode) => {
    setEditingCategory(category);
    setAddChildParentId(null);
    setAddChildParentName(null);
    setCategoryDialogOpen(true);
  };

  const handleCloseCategoryDialog = () => {
    setCategoryDialogOpen(false);
    setEditingCategory(null);
    setAddChildParentId(null);
    setAddChildParentName(null);
  };

  const handleSaveCategory = async (data: CategoryCreate | CategoryUpdate) => {
    try {
      if (editingCategory) {
        await updateCategory(editingCategory.id, data as CategoryUpdate);
        showSnackbar('Category updated successfully', 'success');
      } else {
        await createCategory(data as CategoryCreate);
        showSnackbar('Category created successfully', 'success');
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to save category';
      showSnackbar(message, 'error');
      throw err;
    }
  };

  const handleDeleteCategory = (category: CategoryTreeNode) => {
    const hasChildren = category.children && category.children.length > 0;
    setConfirmDialog({
      open: true,
      title: 'Delete Category',
      message: hasChildren
        ? `Are you sure you want to delete "${category.name}"? This category has children and cannot be deleted unless you first delete or move them.`
        : `Are you sure you want to delete "${category.name}"?`,
      onConfirm: async () => {
        try {
          await deleteCategory(category.id);
          showSnackbar('Category deleted successfully', 'success');
        } catch (err) {
          const message = err instanceof Error ? err.message : 'Failed to delete category';
          showSnackbar(message, 'error');
        }
        setConfirmDialog((prev) => ({ ...prev, open: false }));
      },
    });
  };

  const handleMoveCategory = async (categoryId: string, newParentId: string | null) => {
    try {
      await moveCategory(categoryId, newParentId);
      showSnackbar('Category moved successfully', 'success');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to move category';
      showSnackbar(message, 'error');
    }
  };

  const handleOpenAddTag = () => {
    setEditingTag(null);
    setTagDialogOpen(true);
  };

  const handleOpenEditTag = (tag: TagResponse) => {
    setEditingTag(tag);
    setTagDialogOpen(true);
  };

  const handleCloseTagDialog = () => {
    setTagDialogOpen(false);
    setEditingTag(null);
  };

  const handleSaveTag = async (data: TagCreate | TagUpdate) => {
    try {
      if (editingTag) {
        await updateTag(editingTag.id, data as TagUpdate);
        showSnackbar('Tag updated successfully', 'success');
      } else {
        await createTag(data as TagCreate);
        showSnackbar('Tag created successfully', 'success');
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to save tag';
      showSnackbar(message, 'error');
      throw err;
    }
  };

  const handleDeleteTag = (tag: TagResponse) => {
    setConfirmDialog({
      open: true,
      title: 'Delete Tag',
      message: `Are you sure you want to delete the tag "${tag.name}"? Products using this tag will have it removed.`,
      onConfirm: async () => {
        try {
          await deleteTag(tag.id);
          showSnackbar('Tag deleted successfully', 'success');
        } catch (err) {
          const message = err instanceof Error ? err.message : 'Failed to delete tag';
          showSnackbar(message, 'error');
        }
        setConfirmDialog((prev) => ({ ...prev, open: false }));
      },
    });
  };

  const handleCloseConfirmDialog = () => {
    setConfirmDialog((prev) => ({ ...prev, open: false }));
  };

  const handleRetry = () => {
    clearCategoriesError();
    clearTagsError();
    fetchCategories();
    fetchTags();
  };

  const error = categoriesError || tagsError;

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Categories & Tags
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom>
        Manage product categories and tags for organization
      </Typography>

      {error && (
        <Alert
          severity="error"
          action={
            <Button color="inherit" size="small" onClick={handleRetry}>
              Retry
            </Button>
          }
          sx={{ mb: 3 }}
        >
          {error}
        </Alert>
      )}

      <Grid container spacing={3} sx={{ mt: 1 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: '100%', minHeight: 400 }}>
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                mb: 2,
              }}
            >
              <Typography variant="h6">Categories</Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <IconButton
                  onClick={() => fetchCategories()}
                  disabled={categoriesLoading}
                  size="small"
                >
                  <RefreshIcon />
                </IconButton>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={handleOpenAddRootCategory}
                  disabled={categoriesLoading}
                  size="small"
                >
                  Add Root Category
                </Button>
              </Box>
            </Box>

            {categoriesLoading && categories.length === 0 ? (
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                {[1, 2, 3, 4, 5].map((i) => (
                  <Skeleton key={i} variant="rectangular" height={48} />
                ))}
              </Box>
            ) : (
              <CategoryTree
                categories={categories}
                onAddChild={handleOpenAddChildCategory}
                onEdit={handleOpenEditCategory}
                onDelete={handleDeleteCategory}
                onMove={handleMoveCategory}
              />
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: '100%', minHeight: 400 }}>
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                mb: 2,
              }}
            >
              <Typography variant="h6">Tags</Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <IconButton
                  onClick={() => fetchTags()}
                  disabled={tagsLoading}
                  size="small"
                >
                  <RefreshIcon />
                </IconButton>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={handleOpenAddTag}
                  disabled={tagsLoading}
                  size="small"
                >
                  Add Tag
                </Button>
              </Box>
            </Box>

            <TextField
              fullWidth
              placeholder="Search tags..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              size="small"
              sx={{ mb: 2 }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon color="action" />
                  </InputAdornment>
                ),
              }}
            />

            {tagsLoading && filteredTags.length === 0 ? (
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {[1, 2, 3, 4, 5, 6].map((i) => (
                  <Skeleton key={i} variant="rounded" width={80} height={32} />
                ))}
              </Box>
            ) : filteredTags.length === 0 ? (
              <Box
                sx={{
                  p: 4,
                  textAlign: 'center',
                  color: 'text.secondary',
                }}
              >
                <Typography variant="body1">
                  {searchQuery ? 'No tags match your search' : 'No tags yet'}
                </Typography>
                {!searchQuery && (
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    Click "Add Tag" to create your first tag
                  </Typography>
                )}
              </Box>
            ) : (
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {filteredTags.map((tag) => (
                  <Box
                    key={tag.id}
                    sx={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: 0.5,
                      '&:hover .tag-actions': {
                        opacity: 1,
                      },
                    }}
                  >
                    <TagChip tag={tag} showCount />
                    <Box
                      className="tag-actions"
                      sx={{
                        display: 'flex',
                        opacity: 0,
                        transition: 'opacity 0.2s',
                      }}
                    >
                      <IconButton
                        size="small"
                        onClick={() => handleOpenEditTag(tag)}
                        sx={{ p: 0.25 }}
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleDeleteTag(tag)}
                        sx={{ p: 0.25 }}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Box>
                  </Box>
                ))}
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>

      <CategoryDialog
        open={categoryDialogOpen}
        onClose={handleCloseCategoryDialog}
        onSave={handleSaveCategory}
        category={editingCategory}
        parentId={addChildParentId}
        parentName={addChildParentName}
        loading={categoriesLoading}
      />

      <TagDialog
        open={tagDialogOpen}
        onClose={handleCloseTagDialog}
        onSave={handleSaveTag}
        tag={editingTag}
        loading={tagsLoading}
      />

      <Dialog open={confirmDialog.open} onClose={handleCloseConfirmDialog}>
        <DialogTitle>{confirmDialog.title}</DialogTitle>
        <DialogContent>
          <DialogContentText>{confirmDialog.message}</DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseConfirmDialog}>Cancel</Button>
          <Button onClick={confirmDialog.onConfirm} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={handleCloseSnackbar}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default CategoriesPage;
