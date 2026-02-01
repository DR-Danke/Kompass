import React, { useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Paper,
  Grid,
  TextField,
  MenuItem,
  Breadcrumbs,
  Link,
  Alert,
  CircularProgress,
  IconButton,
  Chip,
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { useQuotationCreator } from '@/hooks/kompass/useQuotationCreator';
import ClientSelector from '@/components/kompass/ClientSelector';
import ProductSelector from '@/components/kompass/ProductSelector';
import QuotationLineItemsTable from '@/components/kompass/QuotationLineItemsTable';
import QuotationPricingPanel from '@/components/kompass/QuotationPricingPanel';
import QuotationActions from '@/components/kompass/QuotationActions';
import type { Incoterm } from '@/types/kompass';

const INCOTERM_OPTIONS: Incoterm[] = [
  'FOB', 'CIF', 'EXW', 'DDP', 'DAP', 'CFR', 'CPT', 'CIP', 'DAT', 'FCA', 'FAS'
];

const QuotationCreatorPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const {
    quotationId,
    quotationNumber,
    selectedClient,
    lineItems,
    settings,
    pricing,
    isLoading,
    isSaving,
    isCalculating,
    error,
    isDirty,
    setClient,
    addItem,
    updateItem,
    removeItem,
    updateSettings,
    calculatePricing,
    saveQuotation,
    exportPdf,
    sendEmail,
    getShareToken,
    canSave,
    canCalculate,
  } = useQuotationCreator(id);

  const isEditMode = !!id;

  // Warn on unsaved changes
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (isDirty) {
        e.preventDefault();
        e.returnValue = '';
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [isDirty]);

  const handleSave = useCallback(async () => {
    const result = await saveQuotation();
    // Update URL to edit mode if it was a new quotation
    if (!id && result.id) {
      navigate(`/quotations/${result.id}`, { replace: true });
    }
  }, [saveQuotation, id, navigate]);

  const handleGetShareLink = useCallback(async (): Promise<string> => {
    const tokenResponse = await getShareToken();
    const baseUrl = window.location.origin;
    return `${baseUrl}/share/quotation/${tokenResponse.token}`;
  }, [getShareToken]);

  const addedProductIds = lineItems.map((item) => item.product_id).filter(Boolean) as string[];

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" alignItems="center" gap={2} mb={2}>
        <IconButton onClick={() => navigate('/quotations')}>
          <ArrowBackIcon />
        </IconButton>
        <Box flex={1}>
          <Breadcrumbs>
            <Link
              component="button"
              variant="body2"
              onClick={() => navigate('/quotations')}
              underline="hover"
              color="inherit"
            >
              Quotations
            </Link>
            <Typography color="text.primary">
              {isEditMode ? `Edit ${quotationNumber || 'Quotation'}` : 'New Quotation'}
            </Typography>
          </Breadcrumbs>
          <Box display="flex" alignItems="center" gap={1} mt={0.5}>
            <Typography variant="h5">
              {isEditMode ? quotationNumber : 'New Quotation'}
            </Typography>
            {isDirty && (
              <Chip label="Unsaved changes" size="small" color="warning" variant="outlined" />
            )}
          </Box>
        </Box>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Actions Bar */}
      <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
        <QuotationActions
          canSave={canSave}
          canCalculate={canCalculate}
          isSaving={isSaving}
          isCalculating={isCalculating}
          quotationId={quotationId}
          onSave={handleSave}
          onCalculate={calculatePricing}
          onExportPdf={exportPdf}
          onSendEmail={sendEmail}
          onGetShareLink={handleGetShareLink}
        />
      </Paper>

      {/* Main Content */}
      <Grid container spacing={3}>
        {/* Left Column - Main Content */}
        <Grid item xs={12} md={8} lg={9}>
          {/* Client Selection Section */}
          <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              1. Select Client
            </Typography>
            <ClientSelector
              selectedClient={selectedClient}
              onClientSelect={setClient}
              disabled={isSaving}
            />
          </Paper>

          {/* Product Selection Section */}
          <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              2. Add Products
            </Typography>
            <ProductSelector
              addedProductIds={addedProductIds}
              onAddProduct={addItem}
              disabled={isSaving}
            />
          </Paper>

          {/* Line Items Section */}
          <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">
                3. Line Items
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {lineItems.length} item{lineItems.length !== 1 ? 's' : ''}
              </Typography>
            </Box>
            <QuotationLineItemsTable
              items={lineItems}
              onUpdateItem={updateItem}
              onRemoveItem={removeItem}
              disabled={isSaving}
            />
          </Paper>

          {/* Summary Section */}
          <Paper variant="outlined" sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              4. Quote Details
            </Typography>

            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  select
                  label="Incoterm"
                  value={settings.incoterm}
                  onChange={(e) => updateSettings({ incoterm: e.target.value as Incoterm })}
                  fullWidth
                  disabled={isSaving}
                >
                  {INCOTERM_OPTIONS.map((incoterm) => (
                    <MenuItem key={incoterm} value={incoterm}>
                      {incoterm}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  label="Currency"
                  value={settings.currency}
                  onChange={(e) => updateSettings({ currency: e.target.value })}
                  fullWidth
                  disabled={isSaving}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  type="number"
                  label="Discount %"
                  value={settings.discount_percent}
                  onChange={(e) => {
                    const value = parseFloat(e.target.value);
                    if (!isNaN(value) && value >= 0 && value <= 100) {
                      updateSettings({ discount_percent: value });
                    }
                  }}
                  fullWidth
                  disabled={isSaving}
                  inputProps={{ min: 0, max: 100, step: 0.5 }}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  type="number"
                  label="Validity (days)"
                  value={settings.valid_days}
                  onChange={(e) => {
                    const value = parseInt(e.target.value, 10);
                    if (!isNaN(value) && value >= 1) {
                      updateSettings({ valid_days: value });
                    }
                  }}
                  fullWidth
                  disabled={isSaving}
                  inputProps={{ min: 1, max: 365 }}
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  label="Notes"
                  value={settings.notes}
                  onChange={(e) => updateSettings({ notes: e.target.value })}
                  fullWidth
                  multiline
                  rows={3}
                  disabled={isSaving}
                  placeholder="Add internal notes or comments..."
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  label="Terms & Conditions"
                  value={settings.terms_and_conditions}
                  onChange={(e) => updateSettings({ terms_and_conditions: e.target.value })}
                  fullWidth
                  multiline
                  rows={3}
                  disabled={isSaving}
                  placeholder="Payment terms, delivery conditions, etc..."
                />
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Right Column - Pricing Panel */}
        <Grid item xs={12} md={4} lg={3}>
          <QuotationPricingPanel
            items={lineItems}
            settings={settings}
            pricing={pricing}
            isCalculating={isCalculating}
            onSettingsChange={updateSettings}
            disabled={isSaving}
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default QuotationCreatorPage;
