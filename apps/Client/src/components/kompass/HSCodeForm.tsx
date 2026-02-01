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
import type { HSCodeCreate, HSCodeUpdate, HSCodeResponse } from '@/types/kompass';
import { pricingService } from '@/services/kompassService';

interface HSCodeFormProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  hsCode?: HSCodeResponse | null;
}

interface FormData {
  code: string;
  description: string;
  duty_rate: string;
  notes: string;
}

const HSCodeForm: React.FC<HSCodeFormProps> = ({ open, onClose, onSuccess, hsCode }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isEditMode = !!hsCode;

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormData>({
    defaultValues: {
      code: '',
      description: '',
      duty_rate: '',
      notes: '',
    },
  });

  useEffect(() => {
    if (open) {
      setError(null);
      if (hsCode) {
        reset({
          code: hsCode.code,
          description: hsCode.description,
          duty_rate: String(hsCode.duty_rate),
          notes: hsCode.notes || '',
        });
      } else {
        reset({
          code: '',
          description: '',
          duty_rate: '',
          notes: '',
        });
      }
    }
  }, [open, hsCode, reset]);

  const onSubmit = async (data: FormData) => {
    setLoading(true);
    setError(null);

    try {
      const dutyRate = parseFloat(data.duty_rate);

      if (isEditMode && hsCode) {
        const payload: HSCodeUpdate = {
          code: data.code,
          description: data.description,
          duty_rate: dutyRate,
          notes: data.notes || null,
        };
        console.log(`INFO [HSCodeForm]: Updating HS code ${hsCode.id}`);
        await pricingService.updateHsCode(hsCode.id, payload);
      } else {
        const payload: HSCodeCreate = {
          code: data.code,
          description: data.description,
          duty_rate: dutyRate,
          notes: data.notes || null,
        };
        console.log('INFO [HSCodeForm]: Creating new HS code');
        await pricingService.createHsCode(payload);
      }

      onSuccess();
      onClose();
    } catch (err) {
      console.log('ERROR [HSCodeForm]: Failed to save HS code', err);
      setError(err instanceof Error ? err.message : 'Failed to save HS code');
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
      <DialogTitle>{isEditMode ? 'Edit HS Code' : 'Add HS Code'}</DialogTitle>
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
              label="Code"
              placeholder="e.g., 0101.21.00.00"
              {...register('code', {
                required: 'Code is required',
                pattern: {
                  value: /^[\d.]+$/,
                  message: 'Code should contain only numbers and dots',
                },
              })}
              error={!!errors.code}
              helperText={errors.code?.message}
              disabled={loading}
              data-testid="hs-code-code-input"
            />
            <TextField
              fullWidth
              label="Description"
              multiline
              rows={2}
              {...register('description', { required: 'Description is required' })}
              error={!!errors.description}
              helperText={errors.description?.message}
              disabled={loading}
              data-testid="hs-code-description-input"
            />
            <TextField
              fullWidth
              label="Duty Rate (%)"
              type="number"
              inputProps={{ step: '0.01', min: 0, max: 100 }}
              {...register('duty_rate', {
                required: 'Duty rate is required',
                min: { value: 0, message: 'Duty rate must be at least 0' },
                max: { value: 100, message: 'Duty rate cannot exceed 100' },
              })}
              error={!!errors.duty_rate}
              helperText={errors.duty_rate?.message || 'Enter the tariff percentage (0-100)'}
              disabled={loading}
              data-testid="hs-code-duty-rate-input"
            />
            <TextField
              fullWidth
              label="Notes"
              multiline
              rows={2}
              {...register('notes')}
              disabled={loading}
              helperText="Optional notes about this HS code"
              data-testid="hs-code-notes-input"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} disabled={loading}>
            Cancel
          </Button>
          <Box sx={{ position: 'relative' }}>
            <Button
              type="submit"
              variant="contained"
              disabled={loading}
              data-testid="hs-code-submit-btn"
            >
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

export default HSCodeForm;
