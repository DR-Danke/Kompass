import React, { useState, useCallback, useEffect } from 'react';
import {
  Box,
  Typography,
  TextField,
  Autocomplete,
  Card,
  CardContent,
  Button,
  CircularProgress,
  Chip,
  Alert,
} from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import BusinessIcon from '@mui/icons-material/Business';
import EmailIcon from '@mui/icons-material/Email';
import PhoneIcon from '@mui/icons-material/Phone';
import AddIcon from '@mui/icons-material/Add';
import WarningIcon from '@mui/icons-material/Warning';
import { clientService } from '@/services/kompassService';
import type { ClientResponse, ClientCreate, ClientUpdate } from '@/types/kompass';
import ClientForm from './ClientForm';

interface ClientSelectorProps {
  selectedClient: ClientResponse | null;
  onClientSelect: (client: ClientResponse | null) => void;
  disabled?: boolean;
}

const ClientSelector: React.FC<ClientSelectorProps> = ({
  selectedClient,
  onClientSelect,
  disabled = false,
}) => {
  const [inputValue, setInputValue] = useState('');
  const [options, setOptions] = useState<ClientResponse[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [formOpen, setFormOpen] = useState(false);

  // Debounced search
  useEffect(() => {
    if (!inputValue || inputValue.length < 2) {
      setOptions([]);
      return;
    }

    const timer = setTimeout(async () => {
      setIsLoading(true);
      try {
        const results = await clientService.search(inputValue);
        setOptions(results);
      } catch (err) {
        console.error('ERROR [ClientSelector]: Failed to search clients:', err);
        setOptions([]);
      } finally {
        setIsLoading(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [inputValue]);

  const handleCreateClient = useCallback(async (data: ClientCreate): Promise<ClientResponse> => {
    console.log('INFO [ClientSelector]: Creating new client');
    const newClient = await clientService.create(data);
    onClientSelect(newClient);
    return newClient;
  }, [onClientSelect]);

  const handleUpdateClient = useCallback(async (
    id: string,
    data: ClientUpdate
  ): Promise<ClientResponse> => {
    console.log(`INFO [ClientSelector]: Updating client ${id}`);
    const updatedClient = await clientService.update(id, data);
    onClientSelect(updatedClient);
    return updatedClient;
  }, [onClientSelect]);

  const handleFormSuccess = useCallback(() => {
    setFormOpen(false);
  }, []);

  const handleClearSelection = useCallback(() => {
    onClientSelect(null);
    setInputValue('');
  }, [onClientSelect]);

  const isProjectDeadlineNear = useCallback((deadline: string | null): boolean => {
    if (!deadline) return false;
    const deadlineDate = new Date(deadline);
    const today = new Date();
    const daysUntilDeadline = Math.ceil((deadlineDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
    return daysUntilDeadline <= 30 && daysUntilDeadline >= 0;
  }, []);

  const formatDeadlineWarning = useCallback((deadline: string | null): string => {
    if (!deadline) return '';
    const deadlineDate = new Date(deadline);
    const today = new Date();
    const daysUntilDeadline = Math.ceil((deadlineDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
    if (daysUntilDeadline < 0) return 'Project deadline has passed';
    if (daysUntilDeadline === 0) return 'Project deadline is today';
    return `${daysUntilDeadline} days until project deadline`;
  }, []);

  if (selectedClient) {
    return (
      <Card variant="outlined">
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
            <Typography variant="subtitle1" fontWeight="bold">
              Selected Client
            </Typography>
            <Button
              size="small"
              onClick={handleClearSelection}
              disabled={disabled}
            >
              Change
            </Button>
          </Box>

          <Box display="flex" alignItems="center" gap={1} mb={1}>
            <BusinessIcon fontSize="small" color="action" />
            <Typography variant="body1" fontWeight="medium">
              {selectedClient.company_name}
            </Typography>
            <Chip
              size="small"
              label={selectedClient.status}
              color={selectedClient.status === 'won' ? 'success' : 'default'}
            />
          </Box>

          {selectedClient.contact_name && (
            <Box display="flex" alignItems="center" gap={1} mb={0.5}>
              <PersonIcon fontSize="small" color="action" />
              <Typography variant="body2" color="text.secondary">
                {selectedClient.contact_name}
              </Typography>
            </Box>
          )}

          {selectedClient.email && (
            <Box display="flex" alignItems="center" gap={1} mb={0.5}>
              <EmailIcon fontSize="small" color="action" />
              <Typography variant="body2" color="text.secondary">
                {selectedClient.email}
              </Typography>
            </Box>
          )}

          {selectedClient.phone && (
            <Box display="flex" alignItems="center" gap={1} mb={0.5}>
              <PhoneIcon fontSize="small" color="action" />
              <Typography variant="body2" color="text.secondary">
                {selectedClient.phone}
              </Typography>
            </Box>
          )}

          {selectedClient.project_name && (
            <Box mt={1}>
              <Typography variant="body2" color="text.secondary">
                Project: {selectedClient.project_name}
              </Typography>
            </Box>
          )}

          {selectedClient.project_deadline && (
            <Box mt={1}>
              {isProjectDeadlineNear(selectedClient.project_deadline) ? (
                <Alert severity="warning" icon={<WarningIcon />} sx={{ py: 0 }}>
                  {formatDeadlineWarning(selectedClient.project_deadline)}
                </Alert>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  Deadline: {new Date(selectedClient.project_deadline).toLocaleDateString()}
                </Typography>
              )}
            </Box>
          )}
        </CardContent>
      </Card>
    );
  }

  return (
    <Box>
      <Autocomplete
        freeSolo
        options={options}
        getOptionLabel={(option) =>
          typeof option === 'string' ? option : option.company_name
        }
        inputValue={inputValue}
        onInputChange={(_, newValue) => setInputValue(newValue)}
        onChange={(_, newValue) => {
          if (newValue && typeof newValue !== 'string') {
            onClientSelect(newValue);
          }
        }}
        loading={isLoading}
        disabled={disabled}
        renderInput={(params) => (
          <TextField
            {...params}
            label="Search Client"
            placeholder="Type at least 2 characters to search..."
            InputProps={{
              ...params.InputProps,
              endAdornment: (
                <>
                  {isLoading && <CircularProgress color="inherit" size={20} />}
                  {params.InputProps.endAdornment}
                </>
              ),
            }}
          />
        )}
        renderOption={(props, option) => {
          const { key, ...otherProps } = props;
          return (
            <li key={key} {...otherProps}>
              <Box>
                <Typography variant="body1">{option.company_name}</Typography>
                {option.contact_name && (
                  <Typography variant="body2" color="text.secondary">
                    {option.contact_name}
                  </Typography>
                )}
                {option.project_deadline && isProjectDeadlineNear(option.project_deadline) && (
                  <Typography variant="caption" color="warning.main">
                    {formatDeadlineWarning(option.project_deadline)}
                  </Typography>
                )}
              </Box>
            </li>
          );
        }}
        noOptionsText={
          inputValue.length < 2
            ? 'Type at least 2 characters to search'
            : 'No clients found'
        }
      />

      <Box mt={1}>
        <Button
          startIcon={<AddIcon />}
          onClick={() => setFormOpen(true)}
          size="small"
          disabled={disabled}
        >
          Create New Client
        </Button>
      </Box>

      <ClientForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
        onSuccess={handleFormSuccess}
        client={null}
        onCreate={handleCreateClient}
        onUpdate={handleUpdateClient}
      />
    </Box>
  );
};

export default ClientSelector;
