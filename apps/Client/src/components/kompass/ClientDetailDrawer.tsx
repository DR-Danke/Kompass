import React, { useEffect, useState } from 'react';
import {
  Drawer,
  Box,
  Typography,
  IconButton,
  Tabs,
  Tab,
  Divider,
  Button,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  TextField,
  MenuItem,
  CircularProgress,
  Alert,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import EditIcon from '@mui/icons-material/Edit';
import EmailIcon from '@mui/icons-material/Email';
import PhoneIcon from '@mui/icons-material/Phone';
import WhatsAppIcon from '@mui/icons-material/WhatsApp';
import BusinessIcon from '@mui/icons-material/Business';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import PersonIcon from '@mui/icons-material/Person';
import CategoryIcon from '@mui/icons-material/Category';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import DescriptionIcon from '@mui/icons-material/Description';
import TimelineIcon from '@mui/icons-material/Timeline';
import ReceiptIcon from '@mui/icons-material/Receipt';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import type {
  ClientResponse,
  ClientStatus,
  StatusHistoryResponse,
  ClientWithQuotations,
} from '@/types/kompass';

interface ClientDetailDrawerProps {
  open: boolean;
  client: ClientResponse | null;
  clientWithQuotations: ClientWithQuotations | null;
  statusHistory: StatusHistoryResponse[];
  onClose: () => void;
  onEdit: (client: ClientResponse) => void;
  onStatusChange: (clientId: string, newStatus: ClientStatus, notes?: string) => Promise<void>;
  isLoading?: boolean;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <Box
    role="tabpanel"
    hidden={value !== index}
    sx={{ py: 2 }}
  >
    {value === index && children}
  </Box>
);

const STATUS_OPTIONS: { value: ClientStatus; label: string }[] = [
  { value: 'lead', label: 'Lead' },
  { value: 'qualified', label: 'Qualified' },
  { value: 'quoting', label: 'Quoting' },
  { value: 'negotiating', label: 'Negotiating' },
  { value: 'won', label: 'Won' },
  { value: 'lost', label: 'Lost' },
];

const getStatusColor = (status: ClientStatus): 'default' | 'primary' | 'warning' | 'success' | 'error' | 'info' => {
  switch (status) {
    case 'lead':
      return 'default';
    case 'qualified':
      return 'info';
    case 'quoting':
      return 'warning';
    case 'negotiating':
      return 'warning';
    case 'won':
      return 'success';
    case 'lost':
      return 'error';
    default:
      return 'default';
  }
};

const formatDate = (dateStr: string): string => {
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

const ClientDetailDrawer: React.FC<ClientDetailDrawerProps> = ({
  open,
  client,
  clientWithQuotations,
  statusHistory,
  onClose,
  onEdit,
  onStatusChange,
  isLoading = false,
}) => {
  const [tabValue, setTabValue] = useState(0);
  const [newStatus, setNewStatus] = useState<ClientStatus | ''>('');
  const [statusNotes, setStatusNotes] = useState('');
  const [isChangingStatus, setIsChangingStatus] = useState(false);

  useEffect(() => {
    if (client) {
      setNewStatus(client.status);
    }
  }, [client]);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleStatusChange = async () => {
    if (!client || !newStatus || newStatus === client.status) return;

    setIsChangingStatus(true);
    try {
      await onStatusChange(client.id, newStatus, statusNotes || undefined);
      setStatusNotes('');
    } finally {
      setIsChangingStatus(false);
    }
  };

  if (!client) return null;

  const quotationSummary = clientWithQuotations?.quotation_summary;

  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
      PaperProps={{
        sx: { width: 400, maxWidth: '100%' },
      }}
    >
      <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Box display="flex" justifyContent="space-between" alignItems="flex-start">
            <Box flex={1}>
              <Typography variant="h6" noWrap>
                {client.company_name}
              </Typography>
              {client.contact_name && (
                <Typography variant="body2" color="text.secondary">
                  {client.contact_name}
                </Typography>
              )}
            </Box>
            <Box display="flex" gap={0.5}>
              <IconButton size="small" onClick={() => onEdit(client)}>
                <EditIcon fontSize="small" />
              </IconButton>
              <IconButton size="small" onClick={onClose}>
                <CloseIcon fontSize="small" />
              </IconButton>
            </Box>
          </Box>

          <Box mt={1}>
            <Chip
              label={STATUS_OPTIONS.find(s => s.value === client.status)?.label || client.status}
              color={getStatusColor(client.status)}
              size="small"
            />
          </Box>
        </Box>

        {/* Tabs */}
        <Tabs value={tabValue} onChange={handleTabChange} sx={{ px: 2 }}>
          <Tab label="Info" />
          <Tab label="History" />
          <Tab label="Quotations" />
        </Tabs>

        {/* Tab Content */}
        <Box sx={{ flex: 1, overflow: 'auto', px: 2 }}>
          {/* Info Tab */}
          <TabPanel value={tabValue} index={0}>
            {isLoading ? (
              <Box display="flex" justifyContent="center" py={4}>
                <CircularProgress />
              </Box>
            ) : (
              <>
                {/* Contact Info */}
                <Typography variant="subtitle2" color="text.secondary" mb={1}>
                  Contact Information
                </Typography>
                <List dense disablePadding>
                  {client.email && (
                    <ListItem disableGutters>
                      <ListItemIcon sx={{ minWidth: 36 }}>
                        <EmailIcon fontSize="small" />
                      </ListItemIcon>
                      <ListItemText primary={client.email} />
                    </ListItem>
                  )}
                  {client.phone && (
                    <ListItem disableGutters>
                      <ListItemIcon sx={{ minWidth: 36 }}>
                        <PhoneIcon fontSize="small" />
                      </ListItemIcon>
                      <ListItemText primary={client.phone} />
                    </ListItem>
                  )}
                  {client.whatsapp && (
                    <ListItem disableGutters>
                      <ListItemIcon sx={{ minWidth: 36 }}>
                        <WhatsAppIcon fontSize="small" color="success" />
                      </ListItemIcon>
                      <ListItemText primary={client.whatsapp} />
                    </ListItem>
                  )}
                </List>

                <Divider sx={{ my: 2 }} />

                {/* Location */}
                <Typography variant="subtitle2" color="text.secondary" mb={1}>
                  Location
                </Typography>
                <List dense disablePadding>
                  {(client.address || client.city || client.country) && (
                    <ListItem disableGutters>
                      <ListItemIcon sx={{ minWidth: 36 }}>
                        <LocationOnIcon fontSize="small" />
                      </ListItemIcon>
                      <ListItemText
                        primary={[client.address, client.city, client.state, client.country]
                          .filter(Boolean)
                          .join(', ')}
                      />
                    </ListItem>
                  )}
                </List>

                <Divider sx={{ my: 2 }} />

                {/* Project Info */}
                <Typography variant="subtitle2" color="text.secondary" mb={1}>
                  Project Details
                </Typography>
                <List dense disablePadding>
                  {client.project_name && (
                    <ListItem disableGutters>
                      <ListItemIcon sx={{ minWidth: 36 }}>
                        <DescriptionIcon fontSize="small" />
                      </ListItemIcon>
                      <ListItemText primary={client.project_name} secondary="Project Name" />
                    </ListItem>
                  )}
                  {client.project_deadline && (
                    <ListItem disableGutters>
                      <ListItemIcon sx={{ minWidth: 36 }}>
                        <AccessTimeIcon fontSize="small" />
                      </ListItemIcon>
                      <ListItemText
                        primary={new Date(client.project_deadline).toLocaleDateString()}
                        secondary="Deadline"
                      />
                    </ListItem>
                  )}
                  {client.niche_name && (
                    <ListItem disableGutters>
                      <ListItemIcon sx={{ minWidth: 36 }}>
                        <CategoryIcon fontSize="small" />
                      </ListItemIcon>
                      <ListItemText primary={client.niche_name} secondary="Niche" />
                    </ListItem>
                  )}
                  {client.incoterm_preference && (
                    <ListItem disableGutters>
                      <ListItemIcon sx={{ minWidth: 36 }}>
                        <BusinessIcon fontSize="small" />
                      </ListItemIcon>
                      <ListItemText primary={client.incoterm_preference} secondary="Incoterm Preference" />
                    </ListItem>
                  )}
                  {client.source && (
                    <ListItem disableGutters>
                      <ListItemIcon sx={{ minWidth: 36 }}>
                        <PersonIcon fontSize="small" />
                      </ListItemIcon>
                      <ListItemText primary={client.source} secondary="Source" />
                    </ListItem>
                  )}
                </List>

                {client.notes && (
                  <>
                    <Divider sx={{ my: 2 }} />
                    <Typography variant="subtitle2" color="text.secondary" mb={1}>
                      Notes
                    </Typography>
                    <Typography variant="body2">{client.notes}</Typography>
                  </>
                )}

                <Divider sx={{ my: 2 }} />

                {/* Status Change */}
                <Typography variant="subtitle2" color="text.secondary" mb={1}>
                  Change Status
                </Typography>
                <Box display="flex" flexDirection="column" gap={1}>
                  <TextField
                    select
                    size="small"
                    label="New Status"
                    value={newStatus}
                    onChange={(e) => setNewStatus(e.target.value as ClientStatus)}
                    fullWidth
                  >
                    {STATUS_OPTIONS.map(option => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </TextField>
                  <TextField
                    size="small"
                    label="Notes (optional)"
                    value={statusNotes}
                    onChange={(e) => setStatusNotes(e.target.value)}
                    multiline
                    rows={2}
                    fullWidth
                  />
                  <Button
                    variant="contained"
                    onClick={handleStatusChange}
                    disabled={isChangingStatus || newStatus === client.status || !newStatus}
                    size="small"
                  >
                    {isChangingStatus ? <CircularProgress size={20} /> : 'Update Status'}
                  </Button>
                </Box>
              </>
            )}
          </TabPanel>

          {/* History Tab */}
          <TabPanel value={tabValue} index={1}>
            <Typography variant="subtitle2" color="text.secondary" mb={2}>
              Status History
            </Typography>
            {statusHistory.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                No status changes recorded
              </Typography>
            ) : (
              <List dense disablePadding>
                {statusHistory.map((entry) => (
                  <ListItem key={entry.id} disableGutters sx={{ alignItems: 'flex-start', mb: 1.5 }}>
                    <ListItemIcon sx={{ minWidth: 36, mt: 0.5 }}>
                      <TimelineIcon fontSize="small" color="action" />
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box display="flex" alignItems="center" gap={1}>
                          {entry.old_status && (
                            <>
                              <Chip
                                label={entry.old_status}
                                size="small"
                                variant="outlined"
                                sx={{ fontSize: '0.7rem' }}
                              />
                              <ArrowForwardIcon fontSize="small" color="action" />
                            </>
                          )}
                          <Chip
                            label={entry.new_status}
                            size="small"
                            color={getStatusColor(entry.new_status)}
                            sx={{ fontSize: '0.7rem' }}
                          />
                        </Box>
                      }
                      secondary={
                        <>
                          <Typography variant="caption" display="block">
                            {formatDate(entry.created_at)}
                            {entry.changed_by_name && ` by ${entry.changed_by_name}`}
                          </Typography>
                          {entry.notes && (
                            <Typography variant="caption" color="text.secondary" display="block">
                              {entry.notes}
                            </Typography>
                          )}
                        </>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            )}
          </TabPanel>

          {/* Quotations Tab */}
          <TabPanel value={tabValue} index={2}>
            <Typography variant="subtitle2" color="text.secondary" mb={2}>
              Quotation Summary
            </Typography>
            {!quotationSummary ? (
              <Box display="flex" justifyContent="center" py={4}>
                <CircularProgress size={24} />
              </Box>
            ) : quotationSummary.total_quotations === 0 ? (
              <Alert severity="info">
                No quotations for this client yet
              </Alert>
            ) : (
              <List dense disablePadding>
                <ListItem disableGutters>
                  <ListItemIcon sx={{ minWidth: 36 }}>
                    <ReceiptIcon fontSize="small" />
                  </ListItemIcon>
                  <ListItemText
                    primary={quotationSummary.total_quotations}
                    secondary="Total Quotations"
                  />
                </ListItem>
                <ListItem disableGutters>
                  <ListItemText
                    primary={
                      <Box display="flex" flexWrap="wrap" gap={0.5}>
                        <Chip label={`Draft: ${quotationSummary.draft_count}`} size="small" variant="outlined" />
                        <Chip label={`Sent: ${quotationSummary.sent_count}`} size="small" variant="outlined" />
                        <Chip label={`Accepted: ${quotationSummary.accepted_count}`} size="small" color="success" variant="outlined" />
                        <Chip label={`Rejected: ${quotationSummary.rejected_count}`} size="small" color="error" variant="outlined" />
                        <Chip label={`Expired: ${quotationSummary.expired_count}`} size="small" variant="outlined" />
                      </Box>
                    }
                  />
                </ListItem>
                <ListItem disableGutters>
                  <ListItemText
                    primary={`$${Number(quotationSummary.total_value).toLocaleString()}`}
                    secondary="Total Value"
                  />
                </ListItem>
              </List>
            )}
          </TabPanel>
        </Box>

        {/* Footer */}
        <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
          <Typography variant="caption" color="text.secondary">
            Created: {formatDate(client.created_at)}
          </Typography>
          <Typography variant="caption" color="text.secondary" display="block">
            Updated: {formatDate(client.updated_at)}
          </Typography>
        </Box>
      </Box>
    </Drawer>
  );
};

export default ClientDetailDrawer;
