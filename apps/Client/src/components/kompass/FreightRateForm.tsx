import React, { useEffect, useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
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
  MenuItem,
  Grid,
} from '@mui/material';
import type { FreightRateCreate, FreightRateUpdate, FreightRateResponse, Incoterm } from '@/types/kompass';
import { pricingService } from '@/services/kompassService';

interface FreightRateFormProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  freightRate?: FreightRateResponse | null;
}

interface FormData {
  origin: string;
  destination: string;
  incoterm: Incoterm;
  rate_per_kg: string;
  rate_per_cbm: string;
  minimum_charge: string;
  transit_days: string;
  valid_from: string;
  valid_until: string;
  notes: string;
}

const INCOTERMS: Incoterm[] = ['FOB', 'CIF', 'EXW', 'DDP', 'DAP', 'CFR', 'CPT', 'CIP', 'DAT', 'FCA', 'FAS'];

const formatDateForInput = (dateString: string | null): string => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toISOString().split('T')[0];
};

const FreightRateForm: React.FC<FreightRateFormProps> = ({ open, onClose, onSuccess, freightRate }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isEditMode = !!freightRate;

  const {
    register,
    handleSubmit,
    reset,
    control,
    watch,
    formState: { errors },
  } = useForm<FormData>({
    defaultValues: {
      origin: '',
      destination: '',
      incoterm: 'FOB',
      rate_per_kg: '',
      rate_per_cbm: '',
      minimum_charge: '',
      transit_days: '',
      valid_from: '',
      valid_until: '',
      notes: '',
    },
  });

  const validFrom = watch('valid_from');

  useEffect(() => {
    if (open) {
      setError(null);
      if (freightRate) {
        reset({
          origin: freightRate.origin,
          destination: freightRate.destination,
          incoterm: freightRate.incoterm,
          rate_per_kg: freightRate.rate_per_kg ? String(freightRate.rate_per_kg) : '',
          rate_per_cbm: freightRate.rate_per_cbm ? String(freightRate.rate_per_cbm) : '',
          minimum_charge: String(freightRate.minimum_charge),
          transit_days: freightRate.transit_days ? String(freightRate.transit_days) : '',
          valid_from: formatDateForInput(freightRate.valid_from),
          valid_until: formatDateForInput(freightRate.valid_until),
          notes: freightRate.notes || '',
        });
      } else {
        reset({
          origin: '',
          destination: '',
          incoterm: 'FOB',
          rate_per_kg: '',
          rate_per_cbm: '',
          minimum_charge: '',
          transit_days: '',
          valid_from: '',
          valid_until: '',
          notes: '',
        });
      }
    }
  }, [open, freightRate, reset]);

  const onSubmit = async (data: FormData) => {
    setLoading(true);
    setError(null);

    try {
      const payload = {
        origin: data.origin,
        destination: data.destination,
        incoterm: data.incoterm,
        rate_per_kg: data.rate_per_kg ? parseFloat(data.rate_per_kg) : null,
        rate_per_cbm: data.rate_per_cbm ? parseFloat(data.rate_per_cbm) : null,
        minimum_charge: data.minimum_charge ? parseFloat(data.minimum_charge) : 0,
        transit_days: data.transit_days ? parseInt(data.transit_days, 10) : null,
        valid_from: data.valid_from || null,
        valid_until: data.valid_until || null,
        notes: data.notes || null,
        is_active: true,
      };

      if (isEditMode && freightRate) {
        console.log(`INFO [FreightRateForm]: Updating freight rate ${freightRate.id}`);
        await pricingService.updateFreightRate(freightRate.id, payload as FreightRateUpdate);
      } else {
        console.log('INFO [FreightRateForm]: Creating new freight rate');
        await pricingService.createFreightRate(payload as FreightRateCreate);
      }

      onSuccess();
      onClose();
    } catch (err) {
      console.log('ERROR [FreightRateForm]: Failed to save freight rate', err);
      setError(err instanceof Error ? err.message : 'Failed to save freight rate');
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
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>{isEditMode ? 'Edit Freight Rate' : 'Add Freight Rate'}</DialogTitle>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Origin"
                placeholder="e.g., Shanghai, China"
                {...register('origin', { required: 'Origin is required' })}
                error={!!errors.origin}
                helperText={errors.origin?.message}
                disabled={loading}
                data-testid="freight-rate-origin-input"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Destination"
                placeholder="e.g., Cartagena, Colombia"
                {...register('destination', { required: 'Destination is required' })}
                error={!!errors.destination}
                helperText={errors.destination?.message}
                disabled={loading}
                data-testid="freight-rate-destination-input"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <Controller
                name="incoterm"
                control={control}
                rules={{ required: 'Incoterm is required' }}
                render={({ field }) => (
                  <TextField
                    {...field}
                    select
                    fullWidth
                    label="Incoterm"
                    error={!!errors.incoterm}
                    helperText={errors.incoterm?.message}
                    disabled={loading}
                    data-testid="freight-rate-incoterm-select"
                  >
                    {INCOTERMS.map((term) => (
                      <MenuItem key={term} value={term}>
                        {term}
                      </MenuItem>
                    ))}
                  </TextField>
                )}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Transit Days"
                type="number"
                inputProps={{ min: 0 }}
                {...register('transit_days', {
                  min: { value: 0, message: 'Transit days must be positive' },
                })}
                error={!!errors.transit_days}
                helperText={errors.transit_days?.message || 'Number of days for shipping'}
                disabled={loading}
                data-testid="freight-rate-transit-days-input"
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Rate per kg (USD)"
                type="number"
                inputProps={{ step: '0.01', min: 0 }}
                {...register('rate_per_kg', {
                  min: { value: 0, message: 'Rate must be positive' },
                })}
                error={!!errors.rate_per_kg}
                helperText={errors.rate_per_kg?.message}
                disabled={loading}
                data-testid="freight-rate-rate-per-kg-input"
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Rate per cbm (USD)"
                type="number"
                inputProps={{ step: '0.01', min: 0 }}
                {...register('rate_per_cbm', {
                  min: { value: 0, message: 'Rate must be positive' },
                })}
                error={!!errors.rate_per_cbm}
                helperText={errors.rate_per_cbm?.message}
                disabled={loading}
                data-testid="freight-rate-rate-per-cbm-input"
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Minimum Charge (USD)"
                type="number"
                inputProps={{ step: '0.01', min: 0 }}
                {...register('minimum_charge', {
                  min: { value: 0, message: 'Minimum charge must be positive' },
                })}
                error={!!errors.minimum_charge}
                helperText={errors.minimum_charge?.message}
                disabled={loading}
                data-testid="freight-rate-minimum-charge-input"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Valid From"
                type="date"
                InputLabelProps={{ shrink: true }}
                {...register('valid_from')}
                disabled={loading}
                data-testid="freight-rate-valid-from-input"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Valid Until"
                type="date"
                InputLabelProps={{ shrink: true }}
                {...register('valid_until', {
                  validate: (value) => {
                    if (value && validFrom && value < validFrom) {
                      return 'Valid until must be after valid from';
                    }
                    return true;
                  },
                })}
                error={!!errors.valid_until}
                helperText={errors.valid_until?.message}
                disabled={loading}
                data-testid="freight-rate-valid-until-input"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Notes"
                multiline
                rows={2}
                {...register('notes')}
                disabled={loading}
                helperText="Optional notes about this freight rate"
                data-testid="freight-rate-notes-input"
              />
            </Grid>
          </Grid>
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
              data-testid="freight-rate-submit-btn"
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

export default FreightRateForm;
