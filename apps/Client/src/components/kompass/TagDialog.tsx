/**
 * TagDialog Component
 * Dialog for creating and editing tags with color picker
 */

import React, { useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
} from '@mui/material';
import { useForm, Controller } from 'react-hook-form';
import type { TagResponse, TagCreate, TagUpdate } from '@/types/kompass';

interface TagFormData {
  name: string;
  color: string;
}

interface TagDialogProps {
  open: boolean;
  onClose: () => void;
  onSave: (data: TagCreate | TagUpdate) => Promise<void>;
  tag?: TagResponse | null;
  loading?: boolean;
}

const DEFAULT_COLOR = '#2196f3';

export const TagDialog: React.FC<TagDialogProps> = ({
  open,
  onClose,
  onSave,
  tag,
  loading = false,
}) => {
  const isEditMode = Boolean(tag);

  const {
    control,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<TagFormData>({
    defaultValues: {
      name: '',
      color: DEFAULT_COLOR,
    },
  });

  useEffect(() => {
    if (open) {
      if (tag) {
        reset({
          name: tag.name,
          color: tag.color || DEFAULT_COLOR,
        });
      } else {
        reset({
          name: '',
          color: DEFAULT_COLOR,
        });
      }
    }
  }, [open, tag, reset]);

  const onSubmit = async (data: TagFormData) => {
    try {
      await onSave(data);
      onClose();
    } catch (err) {
      console.log('ERROR [TagDialog]: Failed to save tag');
    }
  };

  const handleClose = () => {
    if (!isSubmitting && !loading) {
      onClose();
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogTitle>{isEditMode ? 'Edit Tag' : 'Create Tag'}</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <Controller
              name="name"
              control={control}
              rules={{
                required: 'Tag name is required',
                minLength: { value: 1, message: 'Name must not be empty' },
                maxLength: { value: 50, message: 'Name must be 50 characters or less' },
              }}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Tag Name"
                  fullWidth
                  error={Boolean(errors.name)}
                  helperText={errors.name?.message}
                  disabled={isSubmitting || loading}
                  autoFocus
                />
              )}
            />

            <Controller
              name="color"
              control={control}
              rules={{ required: 'Color is required' }}
              render={({ field }) => (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <TextField
                    label="Color"
                    type="color"
                    value={field.value}
                    onChange={field.onChange}
                    disabled={isSubmitting || loading}
                    sx={{
                      width: 100,
                      '& input[type="color"]': {
                        height: 40,
                        cursor: 'pointer',
                      },
                    }}
                  />
                  <TextField
                    value={field.value}
                    onChange={field.onChange}
                    disabled={isSubmitting || loading}
                    placeholder="#000000"
                    sx={{ flex: 1 }}
                    inputProps={{ maxLength: 7 }}
                  />
                  <Box
                    sx={{
                      width: 40,
                      height: 40,
                      borderRadius: 1,
                      backgroundColor: field.value,
                      border: '1px solid rgba(0,0,0,0.23)',
                    }}
                  />
                </Box>
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
