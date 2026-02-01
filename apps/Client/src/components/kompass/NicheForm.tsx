import React, { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Alert,
  CircularProgress,
} from '@mui/material';
import type { NicheCreate, NicheUpdate, NicheResponse } from '@/types/kompass';
import { nicheService } from '@/services/kompassService';

interface NicheFormProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  niche?: NicheResponse | null;
}

interface FormData {
  name: string;
  description: string;
}

const NicheForm: React.FC<NicheFormProps> = ({ open, onClose, onSuccess, niche }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isEditMode = !!niche;

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormData>({
    defaultValues: {
      name: '',
      description: '',
    },
  });

  useEffect(() => {
    if (open) {
      setError(null);
      if (niche) {
        reset({
          name: niche.name,
          description: niche.description || '',
        });
      } else {
        reset({
          name: '',
          description: '',
        });
      }
    }
  }, [open, niche, reset]);

  const onSubmit = async (data: FormData) => {
    setLoading(true);
    setError(null);

    try {
      const payload: NicheCreate | NicheUpdate = {
        name: data.name,
        description: data.description || null,
      };

      if (isEditMode && niche) {
        console.log(`INFO [NicheForm]: Updating niche ${niche.id}`);
        await nicheService.update(niche.id, payload as NicheUpdate);
      } else {
        console.log('INFO [NicheForm]: Creating new niche');
        await nicheService.create(payload as NicheCreate);
      }

      onSuccess();
      onClose();
    } catch (err) {
      console.log('ERROR [NicheForm]: Failed to save niche', err);
      setError(err instanceof Error ? err.message : 'Failed to save niche');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      onClose();
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>{isEditMode ? 'Edit Niche' : 'Add Niche'}</DialogTitle>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              fullWidth
              label="Name"
              {...register('name', { required: 'Name is required' })}
              error={!!errors.name}
              helperText={errors.name?.message}
              disabled={loading}
            />
            <TextField
              fullWidth
              label="Description"
              multiline
              rows={3}
              {...register('description')}
              disabled={loading}
              helperText="Optional description for this niche"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} disabled={loading}>
            Cancel
          </Button>
          <Box sx={{ position: 'relative' }}>
            <Button type="submit" variant="contained" disabled={loading}>
              {isEditMode ? 'Update' : 'Create'}
            </Button>
            {loading && (
              <CircularProgress
                size={24}
                sx={{
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  marginTop: '-12px',
                  marginLeft: '-12px',
                }}
              />
            )}
          </Box>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default NicheForm;
