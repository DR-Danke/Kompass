import React, { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import {
  Box,
  Button,
  TextField,
  Typography,
  Alert,
  CircularProgress,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Snackbar,
  InputAdornment,
  Grid,
} from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import type { PricingSettingResponse } from '@/types/kompass';
import { pricingService } from '@/services/kompassService';

interface FormData {
  default_margin_percentage: string;
  inspection_cost_usd: string;
  insurance_percentage: string;
  nationalization_cost_cop: string;
  exchange_rate_usd_cop: string;
}

const SETTING_LABELS: Record<string, { label: string; description: string; suffix: string }> = {
  default_margin_percentage: {
    label: 'Default Margin',
    description: 'Default profit margin applied to quotations',
    suffix: '%',
  },
  inspection_cost_usd: {
    label: 'Inspection Cost',
    description: 'Standard cost for product inspection',
    suffix: 'USD',
  },
  insurance_percentage: {
    label: 'Insurance',
    description: 'Insurance percentage applied to shipments',
    suffix: '%',
  },
  nationalization_cost_cop: {
    label: 'Nationalization Cost',
    description: 'Cost for customs nationalization process',
    suffix: 'COP',
  },
  exchange_rate_usd_cop: {
    label: 'Exchange Rate (USD/COP)',
    description: 'Current exchange rate from USD to COP',
    suffix: 'COP',
  },
};

const PricingSettingsForm: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [settings, setSettings] = useState<PricingSettingResponse[]>([]);
  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isDirty },
    getValues,
  } = useForm<FormData>({
    defaultValues: {
      default_margin_percentage: '',
      inspection_cost_usd: '',
      insurance_percentage: '',
      nationalization_cost_cop: '',
      exchange_rate_usd_cop: '',
    },
  });

  const fetchSettings = async () => {
    setLoading(true);
    setError(null);

    try {
      console.log('INFO [PricingSettingsForm]: Fetching pricing settings');
      const response = await pricingService.getSettings();
      setSettings(response.settings);

      const formValues: Partial<FormData> = {};
      response.settings.forEach((setting) => {
        const key = setting.setting_key as keyof FormData;
        if (key in SETTING_LABELS) {
          formValues[key] = String(setting.setting_value);
        }
      });

      reset({
        default_margin_percentage: formValues.default_margin_percentage || '',
        inspection_cost_usd: formValues.inspection_cost_usd || '',
        insurance_percentage: formValues.insurance_percentage || '',
        nationalization_cost_cop: formValues.nationalization_cost_cop || '',
        exchange_rate_usd_cop: formValues.exchange_rate_usd_cop || '',
      });

      console.log(`INFO [PricingSettingsForm]: Loaded ${response.settings.length} settings`);
    } catch (err) {
      console.log('ERROR [PricingSettingsForm]: Failed to fetch settings', err);
      setError(err instanceof Error ? err.message : 'Failed to load pricing settings');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSettings();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSaveClick = () => {
    if (isDirty) {
      setConfirmDialogOpen(true);
    }
  };

  const handleConfirmCancel = () => {
    setConfirmDialogOpen(false);
  };

  const handleConfirmSave = () => {
    setConfirmDialogOpen(false);
    handleSubmit(onSubmit)();
  };

  const onSubmit = async (data: FormData) => {
    setSaving(true);
    setError(null);

    try {
      console.log('INFO [PricingSettingsForm]: Saving pricing settings');

      const updates: { key: string; value: number }[] = [];

      const existingKeys = settings.map((s) => s.setting_key);

      for (const [key, value] of Object.entries(data)) {
        if (value && existingKeys.includes(key)) {
          const numValue = parseFloat(value);
          if (!isNaN(numValue)) {
            updates.push({ key, value: numValue });
          }
        }
      }

      for (const update of updates) {
        await pricingService.updateSetting(update.key, { setting_value: update.value });
      }

      setSnackbarMessage('Settings saved successfully');
      setSnackbarOpen(true);
      await fetchSettings();
    } catch (err) {
      console.log('ERROR [PricingSettingsForm]: Failed to save settings', err);
      setError(err instanceof Error ? err.message : 'Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" py={4}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Paper variant="outlined" sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Pricing Settings
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Configure default values used in quotation calculations.
        </Typography>

        <form>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={SETTING_LABELS.default_margin_percentage.label}
                type="number"
                inputProps={{ step: '0.01', min: 0, max: 100 }}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      {SETTING_LABELS.default_margin_percentage.suffix}
                    </InputAdornment>
                  ),
                }}
                {...register('default_margin_percentage', {
                  min: { value: 0, message: 'Must be at least 0' },
                  max: { value: 100, message: 'Cannot exceed 100' },
                })}
                error={!!errors.default_margin_percentage}
                helperText={
                  errors.default_margin_percentage?.message ||
                  SETTING_LABELS.default_margin_percentage.description
                }
                disabled={saving}
                data-testid="settings-default-margin"
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={SETTING_LABELS.inspection_cost_usd.label}
                type="number"
                inputProps={{ step: '0.01', min: 0 }}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      {SETTING_LABELS.inspection_cost_usd.suffix}
                    </InputAdornment>
                  ),
                }}
                {...register('inspection_cost_usd', {
                  min: { value: 0, message: 'Must be at least 0' },
                })}
                error={!!errors.inspection_cost_usd}
                helperText={
                  errors.inspection_cost_usd?.message ||
                  SETTING_LABELS.inspection_cost_usd.description
                }
                disabled={saving}
                data-testid="settings-inspection-cost"
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={SETTING_LABELS.insurance_percentage.label}
                type="number"
                inputProps={{ step: '0.01', min: 0, max: 100 }}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      {SETTING_LABELS.insurance_percentage.suffix}
                    </InputAdornment>
                  ),
                }}
                {...register('insurance_percentage', {
                  min: { value: 0, message: 'Must be at least 0' },
                  max: { value: 100, message: 'Cannot exceed 100' },
                })}
                error={!!errors.insurance_percentage}
                helperText={
                  errors.insurance_percentage?.message ||
                  SETTING_LABELS.insurance_percentage.description
                }
                disabled={saving}
                data-testid="settings-insurance-percentage"
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={SETTING_LABELS.nationalization_cost_cop.label}
                type="number"
                inputProps={{ step: '1', min: 0 }}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      {SETTING_LABELS.nationalization_cost_cop.suffix}
                    </InputAdornment>
                  ),
                }}
                {...register('nationalization_cost_cop', {
                  min: { value: 0, message: 'Must be at least 0' },
                })}
                error={!!errors.nationalization_cost_cop}
                helperText={
                  errors.nationalization_cost_cop?.message ||
                  SETTING_LABELS.nationalization_cost_cop.description
                }
                disabled={saving}
                data-testid="settings-nationalization-cost"
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={SETTING_LABELS.exchange_rate_usd_cop.label}
                type="number"
                inputProps={{ step: '1', min: 0 }}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      {SETTING_LABELS.exchange_rate_usd_cop.suffix}
                    </InputAdornment>
                  ),
                }}
                {...register('exchange_rate_usd_cop', {
                  min: { value: 0, message: 'Must be at least 0' },
                })}
                error={!!errors.exchange_rate_usd_cop}
                helperText={
                  errors.exchange_rate_usd_cop?.message ||
                  SETTING_LABELS.exchange_rate_usd_cop.description
                }
                disabled={saving}
                data-testid="settings-exchange-rate"
              />
            </Grid>
          </Grid>

          <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              variant="contained"
              startIcon={saving ? <CircularProgress size={20} color="inherit" /> : <SaveIcon />}
              onClick={handleSaveClick}
              disabled={saving || !isDirty}
              data-testid="settings-save-btn"
            >
              {saving ? 'Saving...' : 'Save Settings'}
            </Button>
          </Box>
        </form>
      </Paper>

      {/* Confirmation Dialog */}
      <Dialog open={confirmDialogOpen} onClose={handleConfirmCancel}>
        <DialogTitle>Confirm Changes</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to save these pricing settings? This will affect all future
            quotation calculations.
          </DialogContentText>
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Changes to be saved:
            </Typography>
            <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
              {Object.entries(getValues()).map(([key, value]) => {
                const label = SETTING_LABELS[key as keyof typeof SETTING_LABELS];
                if (label && value) {
                  return (
                    <li key={key}>
                      <Typography variant="body2">
                        {label.label}: {value} {label.suffix}
                      </Typography>
                    </li>
                  );
                }
                return null;
              })}
            </ul>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleConfirmCancel}>Cancel</Button>
          <Button onClick={handleConfirmSave} variant="contained" color="primary">
            Confirm
          </Button>
        </DialogActions>
      </Dialog>

      {/* Success Snackbar */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={4000}
        onClose={() => setSnackbarOpen(false)}
        message={snackbarMessage}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      />
    </Box>
  );
};

export default PricingSettingsForm;
