import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Tabs,
  Tab,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
  CircularProgress,
} from '@mui/material';
import type {
  HSCodeResponse,
  FreightRateResponse,
} from '@/types/kompass';
import { pricingService } from '@/services/kompassService';
import HSCodeTable from '@/components/kompass/HSCodeTable';
import HSCodeForm from '@/components/kompass/HSCodeForm';
import FreightRateTable from '@/components/kompass/FreightRateTable';
import FreightRateForm from '@/components/kompass/FreightRateForm';
import PricingSettingsForm from '@/components/kompass/PricingSettingsForm';
import axios from 'axios';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`pricing-tabpanel-${index}`}
      aria-labelledby={`pricing-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

function a11yProps(index: number) {
  return {
    id: `pricing-tab-${index}`,
    'aria-controls': `pricing-tabpanel-${index}`,
  };
}

const PricingConfigPage: React.FC = () => {
  // Tab state
  const [tabValue, setTabValue] = useState(0);

  // HS Codes state
  const [hsCodes, setHsCodes] = useState<HSCodeResponse[]>([]);
  const [hsCodesLoading, setHsCodesLoading] = useState(true);
  const [hsCodesError, setHsCodesError] = useState<string | null>(null);
  const [hsCodeSearch, setHsCodeSearch] = useState('');
  const [hsCodeFormOpen, setHsCodeFormOpen] = useState(false);
  const [selectedHsCode, setSelectedHsCode] = useState<HSCodeResponse | null>(null);
  const [hsCodeDeleteDialogOpen, setHsCodeDeleteDialogOpen] = useState(false);
  const [hsCodeToDelete, setHsCodeToDelete] = useState<HSCodeResponse | null>(null);
  const [hsCodeDeleteLoading, setHsCodeDeleteLoading] = useState(false);
  const [hsCodeDeleteError, setHsCodeDeleteError] = useState<string | null>(null);

  // Freight Rates state
  const [freightRates, setFreightRates] = useState<FreightRateResponse[]>([]);
  const [freightRatesLoading, setFreightRatesLoading] = useState(true);
  const [freightRatesError, setFreightRatesError] = useState<string | null>(null);
  const [freightRateFilters, setFreightRateFilters] = useState({ origin: '', destination: '' });
  const [freightRateFormOpen, setFreightRateFormOpen] = useState(false);
  const [selectedFreightRate, setSelectedFreightRate] = useState<FreightRateResponse | null>(null);
  const [freightRateDeleteDialogOpen, setFreightRateDeleteDialogOpen] = useState(false);
  const [freightRateToDelete, setFreightRateToDelete] = useState<FreightRateResponse | null>(null);
  const [freightRateDeleteLoading, setFreightRateDeleteLoading] = useState(false);
  const [freightRateDeleteError, setFreightRateDeleteError] = useState<string | null>(null);

  // Fetch HS Codes
  const fetchHsCodes = useCallback(async () => {
    setHsCodesLoading(true);
    setHsCodesError(null);

    try {
      console.log('INFO [PricingConfigPage]: Fetching HS codes');
      const response = await pricingService.listHsCodes(1, 1000);
      setHsCodes(response.items);
      console.log(`INFO [PricingConfigPage]: Fetched ${response.items.length} HS codes`);
    } catch (err) {
      console.log('ERROR [PricingConfigPage]: Failed to fetch HS codes', err);
      setHsCodesError(err instanceof Error ? err.message : 'Failed to load HS codes');
    } finally {
      setHsCodesLoading(false);
    }
  }, []);

  // Fetch Freight Rates
  const fetchFreightRates = useCallback(async () => {
    setFreightRatesLoading(true);
    setFreightRatesError(null);

    try {
      console.log('INFO [PricingConfigPage]: Fetching freight rates');
      const response = await pricingService.listFreightRates(1, 1000);
      setFreightRates(response.items);
      console.log(`INFO [PricingConfigPage]: Fetched ${response.items.length} freight rates`);
    } catch (err) {
      console.log('ERROR [PricingConfigPage]: Failed to fetch freight rates', err);
      setFreightRatesError(err instanceof Error ? err.message : 'Failed to load freight rates');
    } finally {
      setFreightRatesLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHsCodes();
    fetchFreightRates();
  }, [fetchHsCodes, fetchFreightRates]);

  // Tab change handler
  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // HS Code handlers
  const handleHsCodeAdd = () => {
    setSelectedHsCode(null);
    setHsCodeFormOpen(true);
  };

  const handleHsCodeEdit = (hsCode: HSCodeResponse) => {
    setSelectedHsCode(hsCode);
    setHsCodeFormOpen(true);
  };

  const handleHsCodeFormClose = () => {
    setHsCodeFormOpen(false);
    setSelectedHsCode(null);
  };

  const handleHsCodeFormSuccess = () => {
    fetchHsCodes();
  };

  const handleHsCodeDeleteClick = (hsCode: HSCodeResponse) => {
    setHsCodeToDelete(hsCode);
    setHsCodeDeleteError(null);
    setHsCodeDeleteDialogOpen(true);
  };

  const handleHsCodeDeleteCancel = () => {
    setHsCodeDeleteDialogOpen(false);
    setHsCodeToDelete(null);
    setHsCodeDeleteError(null);
  };

  const handleHsCodeDeleteConfirm = async () => {
    if (!hsCodeToDelete) return;

    setHsCodeDeleteLoading(true);
    setHsCodeDeleteError(null);

    try {
      console.log(`INFO [PricingConfigPage]: Deleting HS code ${hsCodeToDelete.id}`);
      await pricingService.deleteHsCode(hsCodeToDelete.id);
      setHsCodeDeleteDialogOpen(false);
      setHsCodeToDelete(null);
      fetchHsCodes();
    } catch (err) {
      console.log('ERROR [PricingConfigPage]: Failed to delete HS code', err);
      if (axios.isAxiosError(err) && err.response?.status === 409) {
        setHsCodeDeleteError(
          'This HS code cannot be deleted because it is in use by products. Please reassign products first.'
        );
      } else {
        setHsCodeDeleteError(err instanceof Error ? err.message : 'Failed to delete HS code');
      }
    } finally {
      setHsCodeDeleteLoading(false);
    }
  };

  // Freight Rate handlers
  const handleFreightRateAdd = () => {
    setSelectedFreightRate(null);
    setFreightRateFormOpen(true);
  };

  const handleFreightRateEdit = (freightRate: FreightRateResponse) => {
    setSelectedFreightRate(freightRate);
    setFreightRateFormOpen(true);
  };

  const handleFreightRateFormClose = () => {
    setFreightRateFormOpen(false);
    setSelectedFreightRate(null);
  };

  const handleFreightRateFormSuccess = () => {
    fetchFreightRates();
  };

  const handleFreightRateDeleteClick = (freightRate: FreightRateResponse) => {
    setFreightRateToDelete(freightRate);
    setFreightRateDeleteError(null);
    setFreightRateDeleteDialogOpen(true);
  };

  const handleFreightRateDeleteCancel = () => {
    setFreightRateDeleteDialogOpen(false);
    setFreightRateToDelete(null);
    setFreightRateDeleteError(null);
  };

  const handleFreightRateDeleteConfirm = async () => {
    if (!freightRateToDelete) return;

    setFreightRateDeleteLoading(true);
    setFreightRateDeleteError(null);

    try {
      console.log(`INFO [PricingConfigPage]: Deleting freight rate ${freightRateToDelete.id}`);
      await pricingService.deleteFreightRate(freightRateToDelete.id);
      setFreightRateDeleteDialogOpen(false);
      setFreightRateToDelete(null);
      fetchFreightRates();
    } catch (err) {
      console.log('ERROR [PricingConfigPage]: Failed to delete freight rate', err);
      if (axios.isAxiosError(err) && err.response?.status === 409) {
        setFreightRateDeleteError(
          'This freight rate cannot be deleted because it is in use. Please remove references first.'
        );
      } else {
        setFreightRateDeleteError(err instanceof Error ? err.message : 'Failed to delete freight rate');
      }
    } finally {
      setFreightRateDeleteLoading(false);
    }
  };

  // Filter HS codes by search
  const filteredHsCodes = hsCodes.filter((hsCode) => {
    if (!hsCodeSearch) return true;
    const searchLower = hsCodeSearch.toLowerCase();
    return (
      hsCode.code.toLowerCase().includes(searchLower) ||
      hsCode.description.toLowerCase().includes(searchLower)
    );
  });

  // Filter freight rates by origin and destination
  const filteredFreightRates = freightRates.filter((rate) => {
    const matchesOrigin = !freightRateFilters.origin ||
      rate.origin.toLowerCase().includes(freightRateFilters.origin.toLowerCase());
    const matchesDestination = !freightRateFilters.destination ||
      rate.destination.toLowerCase().includes(freightRateFilters.destination.toLowerCase());
    return matchesOrigin && matchesDestination;
  });

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Pricing Configuration</Typography>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="pricing configuration tabs">
          <Tab label="HS Codes" {...a11yProps(0)} data-testid="hs-codes-tab" />
          <Tab label="Freight Rates" {...a11yProps(1)} data-testid="freight-rates-tab" />
          <Tab label="Settings" {...a11yProps(2)} data-testid="settings-tab" />
        </Tabs>
      </Box>

      {/* HS Codes Tab */}
      <TabPanel value={tabValue} index={0}>
        {hsCodesError && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setHsCodesError(null)}>
            {hsCodesError}
          </Alert>
        )}
        <HSCodeTable
          hsCodes={filteredHsCodes}
          loading={hsCodesLoading}
          searchQuery={hsCodeSearch}
          onSearchChange={setHsCodeSearch}
          onAdd={handleHsCodeAdd}
          onEdit={handleHsCodeEdit}
          onDelete={handleHsCodeDeleteClick}
        />
      </TabPanel>

      {/* Freight Rates Tab */}
      <TabPanel value={tabValue} index={1}>
        {freightRatesError && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setFreightRatesError(null)}>
            {freightRatesError}
          </Alert>
        )}
        <FreightRateTable
          freightRates={filteredFreightRates}
          loading={freightRatesLoading}
          filters={freightRateFilters}
          onFilterChange={setFreightRateFilters}
          onAdd={handleFreightRateAdd}
          onEdit={handleFreightRateEdit}
          onDelete={handleFreightRateDeleteClick}
        />
      </TabPanel>

      {/* Settings Tab */}
      <TabPanel value={tabValue} index={2}>
        <PricingSettingsForm />
      </TabPanel>

      {/* HS Code Form Dialog */}
      <HSCodeForm
        open={hsCodeFormOpen}
        onClose={handleHsCodeFormClose}
        onSuccess={handleHsCodeFormSuccess}
        hsCode={selectedHsCode}
      />

      {/* HS Code Delete Confirmation Dialog */}
      <Dialog open={hsCodeDeleteDialogOpen} onClose={handleHsCodeDeleteCancel}>
        <DialogTitle>Delete HS Code</DialogTitle>
        <DialogContent>
          {hsCodeDeleteError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {hsCodeDeleteError}
            </Alert>
          )}
          <DialogContentText>
            Are you sure you want to delete the HS code "{hsCodeToDelete?.code}"? This action cannot be
            undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleHsCodeDeleteCancel} disabled={hsCodeDeleteLoading}>
            Cancel
          </Button>
          <Button
            onClick={handleHsCodeDeleteConfirm}
            color="error"
            variant="contained"
            disabled={hsCodeDeleteLoading}
          >
            {hsCodeDeleteLoading ? <CircularProgress size={20} /> : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Freight Rate Form Dialog */}
      <FreightRateForm
        open={freightRateFormOpen}
        onClose={handleFreightRateFormClose}
        onSuccess={handleFreightRateFormSuccess}
        freightRate={selectedFreightRate}
      />

      {/* Freight Rate Delete Confirmation Dialog */}
      <Dialog open={freightRateDeleteDialogOpen} onClose={handleFreightRateDeleteCancel}>
        <DialogTitle>Delete Freight Rate</DialogTitle>
        <DialogContent>
          {freightRateDeleteError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {freightRateDeleteError}
            </Alert>
          )}
          <DialogContentText>
            Are you sure you want to delete the freight rate from "{freightRateToDelete?.origin}" to "
            {freightRateToDelete?.destination}"? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleFreightRateDeleteCancel} disabled={freightRateDeleteLoading}>
            Cancel
          </Button>
          <Button
            onClick={handleFreightRateDeleteConfirm}
            color="error"
            variant="contained"
            disabled={freightRateDeleteLoading}
          >
            {freightRateDeleteLoading ? <CircularProgress size={20} /> : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PricingConfigPage;
