/**
 * CategoryDialog Component
 * Dialog for creating and editing categories
 */

import React, { useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControlLabel,
  Switch,
  Box,
} from '@mui/material';
import { useForm, Controller } from 'react-hook-form';
import type { CategoryTreeNode, CategoryCreate, CategoryUpdate } from '@/types/kompass';

interface CategoryFormData {
  name: string;
  description: string;
  is_active: boolean;
}

interface CategoryDialogProps {
  open: boolean;
  onClose: () => void;
  onSave: (data: CategoryCreate | CategoryUpdate) => Promise<void>;
  category?: CategoryTreeNode | null;
  parentId?: string | null;
  parentName?: string | null;
  loading?: boolean;
}

export const CategoryDialog: React.FC<CategoryDialogProps> = ({
  open,
  onClose,
  onSave,
  category,
  parentId,
  parentName,
  loading = false,
}) => {
  const isEditMode = Boolean(category);
  const isAddChild = Boolean(parentId) && !isEditMode;

  const {
    control,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<CategoryFormData>({
    defaultValues: {
      name: '',
      description: '',
      is_active: true,
    },
  });

  useEffect(() => {
    if (open) {
      if (category) {
        reset({
          name: category.name,
          description: category.description || '',
          is_active: category.is_active,
        });
      } else {
        reset({
          name: '',
          description: '',
          is_active: true,
        });
      }
    }
  }, [open, category, reset]);

  const onSubmit = async (data: CategoryFormData) => {
    try {
      const payload: CategoryCreate | CategoryUpdate = {
        name: data.name,
        description: data.description || null,
        is_active: data.is_active,
      };

      if (!isEditMode && parentId) {
        (payload as CategoryCreate).parent_id = parentId;
      }

      await onSave(payload);
      onClose();
    } catch (err) {
      console.log('ERROR [CategoryDialog]: Failed to save category');
    }
  };

  const handleClose = () => {
    if (!isSubmitting && !loading) {
      onClose();
    }
  };

  const getTitle = () => {
    if (isEditMode) return 'Edit Category';
    if (isAddChild) return `Add Child to "${parentName}"`;
    return 'Create Root Category';
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogTitle>{getTitle()}</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <Controller
              name="name"
              control={control}
              rules={{
                required: 'Category name is required',
                minLength: { value: 1, message: 'Name must not be empty' },
                maxLength: { value: 100, message: 'Name must be 100 characters or less' },
              }}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Category Name"
                  fullWidth
                  error={Boolean(errors.name)}
                  helperText={errors.name?.message}
                  disabled={isSubmitting || loading}
                  autoFocus
                />
              )}
            />

            <Controller
              name="description"
              control={control}
              rules={{
                maxLength: { value: 500, message: 'Description must be 500 characters or less' },
              }}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Description"
                  fullWidth
                  multiline
                  rows={3}
                  error={Boolean(errors.description)}
                  helperText={errors.description?.message}
                  disabled={isSubmitting || loading}
                />
              )}
            />

            <Controller
              name="is_active"
              control={control}
              render={({ field }) => (
                <FormControlLabel
                  control={
                    <Switch
                      checked={field.value}
                      onChange={field.onChange}
                      disabled={isSubmitting || loading}
                    />
                  }
                  label="Active"
                />
              )}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} disabled={isSubmitting || loading}>
            Cancel
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={isSubmitting || loading}
          >
            {isEditMode ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};
