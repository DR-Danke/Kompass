import React, { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  MenuItem,
  Box,
  Alert,
  CircularProgress,
  Grid,
  Tabs,
  Tab,
} from '@mui/material';
import type { SupplierCreate, SupplierUpdate, SupplierResponse, SupplierStatus } from '@/types/kompass';
import { supplierService } from '@/services/kompassService';
import SupplierCertificationTab from './SupplierCertificationTab';
import SupplierProductsTab from './SupplierProductsTab';

interface SupplierFormProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  supplier?: SupplierResponse | null;
}

interface FormData {
  name: string;
  code: string;
  status: SupplierStatus;
  contact_name: string;
  contact_email: string;
  contact_phone: string;
  country: string;
  city: string;
  address: string;
  website: string;
  notes: string;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`supplier-tabpanel-${index}`}
      aria-labelledby={`supplier-tab-${index}`}
    >
      {value === index && <Box sx={{ pt: 2 }}>{children}</Box>}
    </div>
  );
};

const statusOptions: { value: SupplierStatus; label: string }[] = [
  { value: 'active', label: 'Active' },
  { value: 'inactive', label: 'Inactive' },
  { value: 'pending_review', label: 'Pending Review' },
];

const SupplierForm: React.FC<SupplierFormProps> = ({ open, onClose, onSuccess, supplier }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState(0);

  const isEditMode = !!supplier;

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormData>({
    defaultValues: {
      name: '',
      code: '',
      status: 'active',
      contact_name: '',
      contact_email: '',
      contact_phone: '',
      country: 'CN',
      city: '',
      address: '',
      website: '',
      notes: '',
    },
  });

  useEffect(() => {
    if (open) {
      setError(null);
      setActiveTab(0);
      if (supplier) {
        reset({
          name: supplier.name,
          code: supplier.code || '',
          status: supplier.status,
          contact_name: supplier.contact_name || '',
          contact_email: supplier.contact_email || '',
          contact_phone: supplier.contact_phone || '',
          country: supplier.country,
          city: supplier.city || '',
          address: supplier.address || '',
          website: supplier.website || '',
          notes: supplier.notes || '',
        });
      } else {
        reset({
          name: '',
          code: '',
          status: 'active',
          contact_name: '',
          contact_email: '',
          contact_phone: '',
          country: 'CN',
          city: '',
          address: '',
          website: '',
          notes: '',
        });
      }
    }
  }, [open, supplier, reset]);

  const onSubmit = async (data: FormData) => {
    setLoading(true);
    setError(null);

    try {
      const payload: SupplierCreate | SupplierUpdate = {
        name: data.name,
        code: data.code || null,
        status: data.status,
        contact_name: data.contact_name || null,
        contact_email: data.contact_email || null,
        contact_phone: data.contact_phone || null,
        country: data.country,
        city: data.city || null,
        address: data.address || null,
        website: data.website || null,
        notes: data.notes || null,
      };

      if (isEditMode && supplier) {
        console.log(`INFO [SupplierForm]: Updating supplier ${supplier.id}`);
        await supplierService.update(supplier.id, payload as SupplierUpdate);
      } else {
        console.log('INFO [SupplierForm]: Creating new supplier');
        await supplierService.create(payload as SupplierCreate);
      }

      onSuccess();
      onClose();
    } catch (err) {
      console.log('ERROR [SupplierForm]: Failed to save supplier', err);
      setError(err instanceof Error ? err.message : 'Failed to save supplier');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      onClose();
    }
  };

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const dialogTitle = isEditMode
    ? `Edit Supplier${activeTab === 1 ? ' - Certification' : activeTab === 2 ? ' - Products' : ''}`
    : 'Add Supplier';

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>{dialogTitle}</DialogTitle>

      {/* Tabs - only show for edit mode */}
      {isEditMode && (
        <Box sx={{ borderBottom: 1, borderColor: 'divider', px: 3 }}>
          <Tabs value={activeTab} onChange={handleTabChange} aria-label="supplier dialog tabs">
            <Tab label="General" id="supplier-tab-0" aria-controls="supplier-tabpanel-0" />
            <Tab label="Certification" id="supplier-tab-1" aria-controls="supplier-tabpanel-1" />
            <Tab label="Products" id="supplier-tab-2" aria-controls="supplier-tabpanel-2" />
          </Tabs>
        </Box>
      )}

      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {/* General Tab */}
          <TabPanel value={activeTab} index={0}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Name"
                  {...register('name', { required: 'Name is required' })}
                  error={!!errors.name}
                  helperText={errors.name?.message}
                  disabled={loading}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Code"
                  {...register('code')}
                  disabled={loading}
                  helperText="Optional internal code"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  select
                  label="Status"
                  defaultValue="active"
                  {...register('status')}
                  disabled={loading}
                >
                  {statusOptions.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Country"
                  {...register('country', { required: 'Country is required' })}
                  error={!!errors.country}
                  helperText={errors.country?.message}
                  disabled={loading}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="City"
                  {...register('city')}
                  disabled={loading}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Contact Name"
                  {...register('contact_name')}
                  disabled={loading}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Contact Email"
                  type="email"
                  {...register('contact_email', {
                    pattern: {
                      value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                      message: 'Invalid email address',
                    },
                  })}
                  error={!!errors.contact_email}
                  helperText={errors.contact_email?.message}
                  disabled={loading}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Contact Phone"
                  {...register('contact_phone')}
                  disabled={loading}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Address"
                  multiline
                  rows={2}
                  {...register('address')}
                  disabled={loading}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Website"
                  {...register('website', {
                    pattern: {
                      value: /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*\/?$/,
                      message: 'Invalid URL format',
                    },
                  })}
                  error={!!errors.website}
                  helperText={errors.website?.message || 'e.g., https://example.com'}
                  disabled={loading}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Notes"
                  multiline
                  rows={3}
                  {...register('notes')}
                  disabled={loading}
                />
              </Grid>
            </Grid>
          </TabPanel>

          {/* Certification Tab - only visible in edit mode */}
          {isEditMode && supplier && (
            <TabPanel value={activeTab} index={1}>
              <SupplierCertificationTab
                supplierId={supplier.id}
                supplierName={supplier.name}
              />
            </TabPanel>
          )}

          {/* Products Tab - only visible in edit mode */}
          {isEditMode && supplier && (
            <TabPanel value={activeTab} index={2}>
              <SupplierProductsTab
                supplierId={supplier.id}
                supplierName={supplier.name}
              />
            </TabPanel>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} disabled={loading}>
            Cancel
          </Button>
          {activeTab === 0 && (
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
          )}
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default SupplierForm;
