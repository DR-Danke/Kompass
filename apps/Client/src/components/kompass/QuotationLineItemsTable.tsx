import React, { useCallback } from 'react';
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TextField,
  IconButton,
  Typography,
  Tooltip,
  Avatar,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import ImageNotSupportedIcon from '@mui/icons-material/ImageNotSupported';
import EditIcon from '@mui/icons-material/Edit';
import type { LineItem } from '@/hooks/kompass/useQuotationCreator';

interface QuotationLineItemsTableProps {
  items: LineItem[];
  onUpdateItem: (tempId: string, updates: Partial<LineItem>) => void;
  onRemoveItem: (tempId: string) => void;
  disabled?: boolean;
}

const QuotationLineItemsTable: React.FC<QuotationLineItemsTableProps> = ({
  items,
  onUpdateItem,
  onRemoveItem,
  disabled = false,
}) => {
  const handleQuantityChange = useCallback(
    (tempId: string, value: string) => {
      const quantity = parseInt(value, 10);
      if (!isNaN(quantity) && quantity >= 0) {
        onUpdateItem(tempId, { quantity });
      }
    },
    [onUpdateItem]
  );

  const handlePriceOverrideChange = useCallback(
    (tempId: string, value: string) => {
      const price = parseFloat(value);
      if (!isNaN(price) && price >= 0) {
        onUpdateItem(tempId, { unit_price_override: price });
      } else if (value === '') {
        onUpdateItem(tempId, { unit_price_override: null });
      }
    },
    [onUpdateItem]
  );

  const formatCurrency = (value: number | string, currency = 'USD'): string => {
    const num = typeof value === 'string' ? parseFloat(value) : value;
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
    }).format(num);
  };

  if (items.length === 0) {
    return (
      <Box
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        py={6}
        bgcolor="grey.50"
        borderRadius={1}
      >
        <Typography variant="body1" color="text.secondary" gutterBottom>
          No items added yet
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Use the product selector above to add items to your quotation
        </Typography>
      </Box>
    );
  }

  return (
    <TableContainer component={Paper} variant="outlined">
      <Table size="small">
        <TableHead>
          <TableRow sx={{ bgcolor: 'grey.50' }}>
            <TableCell width={60}></TableCell>
            <TableCell>Product</TableCell>
            <TableCell width={100}>Quantity</TableCell>
            <TableCell width={130}>Unit Price (FOB)</TableCell>
            <TableCell width={100}>HS Code</TableCell>
            <TableCell width={120} align="right">Line Total</TableCell>
            <TableCell width={50}></TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {items.map((item) => {
            const primaryImage = item.product?.images?.find((img) => img.is_primary) ||
              item.product?.images?.[0];
            const effectivePrice = item.unit_price_override ?? item.unit_price;
            const hasOverride = item.unit_price_override !== null;

            return (
              <TableRow key={item.tempId} hover>
                {/* Thumbnail */}
                <TableCell>
                  {primaryImage ? (
                    <Avatar
                      variant="rounded"
                      src={primaryImage.url}
                      alt={item.product_name}
                      sx={{ width: 48, height: 48 }}
                    />
                  ) : (
                    <Avatar
                      variant="rounded"
                      sx={{ width: 48, height: 48, bgcolor: 'grey.200' }}
                    >
                      <ImageNotSupportedIcon fontSize="small" color="disabled" />
                    </Avatar>
                  )}
                </TableCell>

                {/* Product Info */}
                <TableCell>
                  <Typography variant="body2" fontWeight="medium">
                    {item.product_name}
                  </Typography>
                  {item.sku && (
                    <Typography variant="caption" color="text.secondary">
                      SKU: {item.sku}
                    </Typography>
                  )}
                </TableCell>

                {/* Quantity */}
                <TableCell>
                  <TextField
                    type="number"
                    size="small"
                    value={item.quantity}
                    onChange={(e) => handleQuantityChange(item.tempId, e.target.value)}
                    disabled={disabled}
                    inputProps={{ min: 1, step: 1 }}
                    sx={{ width: 80 }}
                  />
                </TableCell>

                {/* Unit Price */}
                <TableCell>
                  <Box display="flex" alignItems="center" gap={0.5}>
                    <TextField
                      type="number"
                      size="small"
                      value={item.unit_price_override ?? item.unit_price}
                      onChange={(e) => handlePriceOverrideChange(item.tempId, e.target.value)}
                      disabled={disabled}
                      inputProps={{ min: 0, step: 0.01 }}
                      sx={{
                        width: 100,
                        '& .MuiOutlinedInput-root': hasOverride
                          ? { bgcolor: 'warning.lighter', borderColor: 'warning.main' }
                          : {},
                      }}
                    />
                    {hasOverride && (
                      <Tooltip title="Price has been overridden">
                        <EditIcon fontSize="small" color="warning" />
                      </Tooltip>
                    )}
                  </Box>
                  {hasOverride && (
                    <Typography variant="caption" color="text.secondary" sx={{ textDecoration: 'line-through' }}>
                      {formatCurrency(item.unit_price)}
                    </Typography>
                  )}
                </TableCell>

                {/* HS Code */}
                <TableCell>
                  <Typography variant="body2" color="text.secondary">
                    {item.hs_code || '-'}
                  </Typography>
                </TableCell>

                {/* Line Total */}
                <TableCell align="right">
                  <Typography variant="body2" fontWeight="medium">
                    {formatCurrency(item.quantity * effectivePrice)}
                  </Typography>
                </TableCell>

                {/* Actions */}
                <TableCell>
                  <Tooltip title="Remove item">
                    <IconButton
                      size="small"
                      onClick={() => onRemoveItem(item.tempId)}
                      disabled={disabled}
                      color="error"
                    >
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default QuotationLineItemsTable;
