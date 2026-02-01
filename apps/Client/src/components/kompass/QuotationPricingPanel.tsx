import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Divider,
  TextField,
  CircularProgress,
  Skeleton,
} from '@mui/material';
import type { QuotationSettings, LineItem } from '@/hooks/kompass/useQuotationCreator';
import type { QuotationPricing } from '@/types/kompass';

interface QuotationPricingPanelProps {
  items: LineItem[];
  settings: QuotationSettings;
  pricing: QuotationPricing | null;
  isCalculating: boolean;
  onSettingsChange: (updates: Partial<QuotationSettings>) => void;
  disabled?: boolean;
}

const QuotationPricingPanel: React.FC<QuotationPricingPanelProps> = ({
  items,
  settings,
  pricing,
  isCalculating,
  onSettingsChange,
  disabled = false,
}) => {
  const formatCurrency = (value: number | string, currency = 'USD'): string => {
    const num = typeof value === 'string' ? parseFloat(value) : value;
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
    }).format(num);
  };

  const formatCOP = (value: number | string): string => {
    const num = typeof value === 'string' ? parseFloat(value) : value;
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(num);
  };

  // Calculate local subtotal from line items
  const localSubtotal = items.reduce((sum, item) => {
    const price = item.unit_price_override ?? item.unit_price;
    return sum + item.quantity * price;
  }, 0);

  const PricingRow: React.FC<{
    label: string;
    value: string;
    highlight?: boolean;
    bold?: boolean;
  }> = ({ label, value, highlight, bold }) => (
    <Box
      display="flex"
      justifyContent="space-between"
      alignItems="center"
      py={0.75}
      px={highlight ? 1 : 0}
      bgcolor={highlight ? 'primary.main' : 'transparent'}
      borderRadius={highlight ? 1 : 0}
    >
      <Typography
        variant={highlight ? 'subtitle1' : 'body2'}
        color={highlight ? 'white' : 'text.secondary'}
        fontWeight={bold || highlight ? 'bold' : 'normal'}
      >
        {label}
      </Typography>
      <Typography
        variant={highlight ? 'h6' : 'body2'}
        color={highlight ? 'white' : 'text.primary'}
        fontWeight={bold || highlight ? 'bold' : 'normal'}
      >
        {isCalculating && !highlight ? <Skeleton width={80} /> : value}
      </Typography>
    </Box>
  );

  return (
    <Paper elevation={2} sx={{ p: 2, position: 'sticky', top: 16 }}>
      <Typography variant="h6" gutterBottom>
        Pricing Breakdown
      </Typography>

      {isCalculating && (
        <Box display="flex" alignItems="center" gap={1} mb={2}>
          <CircularProgress size={16} />
          <Typography variant="body2" color="text.secondary">
            Calculating...
          </Typography>
        </Box>
      )}

      {/* Subtotal FOB */}
      <PricingRow
        label="Subtotal FOB (USD)"
        value={pricing ? formatCurrency(pricing.subtotal_fob_usd) : formatCurrency(localSubtotal)}
        bold
      />

      <Divider sx={{ my: 1.5 }} />

      {/* Cost Components */}
      <Typography variant="caption" color="text.secondary" gutterBottom display="block">
        Cost Components
      </Typography>

      <PricingRow
        label="Tariffs"
        value={pricing ? formatCurrency(pricing.tariff_total_usd) : '-'}
      />

      <PricingRow
        label="Int'l Freight"
        value={pricing ? formatCurrency(pricing.freight_intl_usd) : '-'}
      />

      <PricingRow
        label="Inspection"
        value={pricing ? formatCurrency(pricing.inspection_usd) : '-'}
      />

      <PricingRow
        label="Insurance"
        value={pricing ? formatCurrency(pricing.insurance_usd) : '-'}
      />

      <Divider sx={{ my: 1.5 }} />

      {/* COP Components */}
      <Typography variant="caption" color="text.secondary" gutterBottom display="block">
        National Costs (COP)
      </Typography>

      <PricingRow
        label="National Freight"
        value={pricing ? formatCOP(pricing.freight_national_cop) : '-'}
      />

      <PricingRow
        label="Nationalization"
        value={pricing ? formatCOP(pricing.nationalization_cop) : '-'}
      />

      <Divider sx={{ my: 1.5 }} />

      {/* Margin */}
      <Box display="flex" alignItems="center" justifyContent="space-between" py={0.75}>
        <Typography variant="body2" color="text.secondary">
          Margin %
        </Typography>
        <TextField
          type="number"
          size="small"
          value={settings.margin_percent}
          onChange={(e) => {
            const value = parseFloat(e.target.value);
            if (!isNaN(value) && value >= 0 && value <= 100) {
              onSettingsChange({ margin_percent: value });
            }
          }}
          disabled={disabled}
          inputProps={{ min: 0, max: 100, step: 0.5 }}
          sx={{ width: 80 }}
        />
      </Box>

      {pricing && (
        <PricingRow
          label="Margin Amount"
          value={formatCOP(pricing.margin_cop)}
        />
      )}

      <Divider sx={{ my: 1.5 }} />

      {/* Exchange Rate */}
      {pricing && (
        <Box py={0.5}>
          <Typography variant="caption" color="text.secondary">
            Exchange Rate: 1 USD = {formatCOP(pricing.exchange_rate).replace('COP', '').trim()} COP
          </Typography>
        </Box>
      )}

      {/* Subtotal before margin */}
      {pricing && (
        <PricingRow
          label="Subtotal (before margin)"
          value={formatCOP(pricing.subtotal_before_margin_cop)}
        />
      )}

      {/* Grand Total */}
      <Box mt={2}>
        <PricingRow
          label="TOTAL COP"
          value={pricing ? formatCOP(pricing.total_cop) : '-'}
          highlight
        />
      </Box>

      {/* Validity Settings */}
      <Divider sx={{ my: 2 }} />

      <Typography variant="caption" color="text.secondary" gutterBottom display="block">
        Quote Settings
      </Typography>

      <Box display="flex" alignItems="center" justifyContent="space-between" py={0.75}>
        <Typography variant="body2" color="text.secondary">
          Valid for (days)
        </Typography>
        <TextField
          type="number"
          size="small"
          value={settings.valid_days}
          onChange={(e) => {
            const value = parseInt(e.target.value, 10);
            if (!isNaN(value) && value >= 1) {
              onSettingsChange({ valid_days: value });
            }
          }}
          disabled={disabled}
          inputProps={{ min: 1, max: 365, step: 1 }}
          sx={{ width: 80 }}
        />
      </Box>

      {/* Summary */}
      <Box mt={2} p={1.5} bgcolor="grey.50" borderRadius={1}>
        <Typography variant="caption" color="text.secondary">
          {items.length} item{items.length !== 1 ? 's' : ''} in quotation
        </Typography>
        {!pricing && items.length > 0 && (
          <Typography variant="caption" color="warning.main" display="block" mt={0.5}>
            Save and calculate to see full pricing
          </Typography>
        )}
      </Box>
    </Paper>
  );
};

export default QuotationPricingPanel;
