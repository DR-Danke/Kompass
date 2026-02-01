import React, { useEffect, useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  MenuItem,
  Grid,
  CircularProgress,
} from '@mui/material';
import type {
  ClientCreate,
  ClientUpdate,
  ClientResponse,
  ClientStatus,
  ClientSource,
  Incoterm,
  NicheResponse,
} from '@/types/kompass';
import { nicheService } from '@/services/kompassService';

interface ClientFormProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  client?: ClientResponse | null;
  onCreate: (data: ClientCreate) => Promise<ClientResponse>;
  onUpdate: (id: string, data: ClientUpdate) => Promise<ClientResponse>;
}

interface FormData {
  company_name: string;
  contact_name: string;
  email: string;
  phone: string;
  whatsapp: string;
  address: string;
  city: string;
  state: string;
  country: string;
  postal_code: string;
  niche_id: string;
  status: ClientStatus;
  source: ClientSource | '';
  project_name: string;
  project_deadline: string;
  incoterm_preference: Incoterm | '';
  notes: string;
}

const STATUS_OPTIONS: { value: ClientStatus; label: string }[] = [
  { value: 'lead', label: 'Lead' },
  { value: 'qualified', label: 'Qualified' },
  { value: 'quoting', label: 'Quoting' },
  { value: 'negotiating', label: 'Negotiating' },
  { value: 'won', label: 'Won' },
  { value: 'lost', label: 'Lost' },
];

const SOURCE_OPTIONS: { value: ClientSource; label: string }[] = [
  { value: 'website', label: 'Website' },
  { value: 'referral', label: 'Referral' },
  { value: 'cold_call', label: 'Cold Call' },
  { value: 'trade_show', label: 'Trade Show' },
  { value: 'linkedin', label: 'LinkedIn' },
  { value: 'other', label: 'Other' },
];

const INCOTERM_OPTIONS: Incoterm[] = [
  'FOB', 'CIF', 'EXW', 'DDP', 'DAP', 'CFR', 'CPT', 'CIP', 'DAT', 'FCA', 'FAS'
];

const ClientForm: React.FC<ClientFormProps> = ({
  open,
  onClose,
  onSuccess,
  client,
  onCreate,
  onUpdate,
}) => {
  const [niches, setNiches] = useState<NicheResponse[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const isEditMode = !!client;

  const {
    control,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormData>({
    defaultValues: {
      company_name: '',
      contact_name: '',
      email: '',
      phone: '',
      whatsapp: '',
      address: '',
      city: '',
      state: '',
      country: '',
      postal_code: '',
      niche_id: '',
      status: 'lead',
      source: '',
      project_name: '',
      project_deadline: '',
      incoterm_preference: '',
      notes: '',
    },
  });

  // Fetch niches
  useEffect(() => {
    const fetchNiches = async () => {
      try {
        const response = await nicheService.list(1, 100);
        setNiches(response.items);
      } catch (err) {
        console.error('ERROR [ClientForm]: Failed to fetch niches:', err);
      }
    };

    if (open) {
      fetchNiches();
    }
  }, [open]);

  // Reset form when client changes or dialog opens
  useEffect(() => {
    if (open) {
      if (client) {
        reset({
          company_name: client.company_name,
          contact_name: client.contact_name || '',
          email: client.email || '',
          phone: client.phone || '',
          whatsapp: client.whatsapp || '',
          address: client.address || '',
          city: client.city || '',
          state: client.state || '',
          country: client.country || '',
          postal_code: client.postal_code || '',
          niche_id: client.niche_id || '',
          status: client.status,
          source: client.source || '',
          project_name: client.project_name || '',
          project_deadline: client.project_deadline || '',
          incoterm_preference: client.incoterm_preference || '',
          notes: client.notes || '',
        });
      } else {
        reset({
          company_name: '',
          contact_name: '',
          email: '',
          phone: '',
          whatsapp: '',
          address: '',
          city: '',
          state: '',
          country: '',
          postal_code: '',
          niche_id: '',
          status: 'lead',
          source: '',
          project_name: '',
          project_deadline: '',
          incoterm_preference: '',
          notes: '',
        });
      }
    }
  }, [open, client, reset]);

  const onSubmit = async (data: FormData) => {
    setIsSubmitting(true);

    try {
      const payload: ClientCreate | ClientUpdate = {
        company_name: data.company_name,
        contact_name: data.contact_name || null,
        email: data.email || null,
        phone: data.phone || null,
        whatsapp: data.whatsapp || null,
        address: data.address || null,
        city: data.city || null,
        state: data.state || null,
        country: data.country || null,
        postal_code: data.postal_code || null,
        niche_id: data.niche_id || null,
        status: data.status,
        source: (data.source as ClientSource) || null,
        project_name: data.project_name || null,
        project_deadline: data.project_deadline || null,
        incoterm_preference: (data.incoterm_preference as Incoterm) || null,
        notes: data.notes || null,
      };

      if (isEditMode && client) {
        await onUpdate(client.id, payload);
      } else {
        await onCreate(payload as ClientCreate);
      }

      onSuccess();
      onClose();
    } catch (err) {
      console.error('ERROR [ClientForm]: Failed to save client:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      onClose();
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>{isEditMode ? 'Edit Client' : 'Add Client'}</DialogTitle>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogContent>
          <Grid container spacing={2}>
            {/* Company Info */}
            <Grid item xs={12}>
              <Controller
                name="company_name"
                control={control}
                rules={{ required: 'Company name is required' }}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Company Name"
                    fullWidth
                    required
                    error={!!errors.company_name}
                    helperText={errors.company_name?.message}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <Controller
                name="contact_name"
                control={control}
                render={({ field }) => (
                  <TextField {...field} label="Contact Name" fullWidth />
                )}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <Controller
                name="email"
                control={control}
                rules={{
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: 'Invalid email address',
                  },
                }}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Email"
                    fullWidth
                    type="email"
                    error={!!errors.email}
                    helperText={errors.email?.message}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <Controller
                name="phone"
                control={control}
                render={({ field }) => (
                  <TextField {...field} label="Phone" fullWidth />
                )}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <Controller
                name="whatsapp"
                control={control}
                render={({ field }) => (
                  <TextField {...field} label="WhatsApp" fullWidth />
                )}
              />
            </Grid>

            {/* Address */}
            <Grid item xs={12}>
              <Controller
                name="address"
                control={control}
                render={({ field }) => (
                  <TextField {...field} label="Address" fullWidth />
                )}
              />
            </Grid>

            <Grid item xs={12} sm={4}>
              <Controller
                name="city"
                control={control}
                render={({ field }) => (
                  <TextField {...field} label="City" fullWidth />
                )}
              />
            </Grid>

            <Grid item xs={12} sm={4}>
              <Controller
                name="state"
                control={control}
                render={({ field }) => (
                  <TextField {...field} label="State/Province" fullWidth />
                )}
              />
            </Grid>

            <Grid item xs={12} sm={4}>
              <Controller
                name="country"
                control={control}
                render={({ field }) => (
                  <TextField {...field} label="Country" fullWidth />
                )}
              />
            </Grid>

            {/* Status & Source */}
            <Grid item xs={12} sm={4}>
              <Controller
                name="status"
                control={control}
                render={({ field }) => (
                  <TextField {...field} select label="Status" fullWidth>
                    {STATUS_OPTIONS.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </TextField>
                )}
              />
            </Grid>

            <Grid item xs={12} sm={4}>
              <Controller
                name="source"
                control={control}
                render={({ field }) => (
                  <TextField {...field} select label="Source" fullWidth>
                    <MenuItem value="">
                      <em>None</em>
                    </MenuItem>
                    {SOURCE_OPTIONS.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </TextField>
                )}
              />
            </Grid>

            <Grid item xs={12} sm={4}>
              <Controller
                name="niche_id"
                control={control}
                render={({ field }) => (
                  <TextField {...field} select label="Niche" fullWidth>
                    <MenuItem value="">
                      <em>None</em>
                    </MenuItem>
                    {niches.map((niche) => (
                      <MenuItem key={niche.id} value={niche.id}>
                        {niche.name}
                      </MenuItem>
                    ))}
                  </TextField>
                )}
              />
            </Grid>

            {/* Project Info */}
            <Grid item xs={12} sm={6}>
              <Controller
                name="project_name"
                control={control}
                render={({ field }) => (
                  <TextField {...field} label="Project Name" fullWidth />
                )}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <Controller
                name="project_deadline"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Project Deadline"
                    type="date"
                    fullWidth
                    InputLabelProps={{ shrink: true }}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <Controller
                name="incoterm_preference"
                control={control}
                render={({ field }) => (
                  <TextField {...field} select label="Incoterm Preference" fullWidth>
                    <MenuItem value="">
                      <em>None</em>
                    </MenuItem>
                    {INCOTERM_OPTIONS.map((incoterm) => (
                      <MenuItem key={incoterm} value={incoterm}>
                        {incoterm}
                      </MenuItem>
                    ))}
                  </TextField>
                )}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <Controller
                name="postal_code"
                control={control}
                render={({ field }) => (
                  <TextField {...field} label="Postal Code" fullWidth />
                )}
              />
            </Grid>

            {/* Notes */}
            <Grid item xs={12}>
              <Controller
                name="notes"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Notes"
                    fullWidth
                    multiline
                    rows={3}
                  />
                )}
              />
            </Grid>
          </Grid>
        </DialogContent>

        <DialogActions>
          <Button onClick={handleClose} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <CircularProgress size={20} />
            ) : isEditMode ? (
              'Update'
            ) : (
              'Create'
            )}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default ClientForm;
