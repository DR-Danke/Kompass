import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Checkbox,
  TextField,
  Chip,
  Tooltip,
  Box,
  Avatar,
} from '@mui/material';
import type { ExtractedProduct } from '@/types/kompass';

interface ValidationError {
  field: string;
  message: string;
}

interface ProductValidationErrors {
  [productIndex: number]: ValidationError[];
}

interface ExtractedProductTableProps {
  products: ExtractedProduct[];
  selectedIndices: Set<number>;
  onProductChange: (index: number, field: keyof ExtractedProduct, value: string | number | null) => void;
  onProductSelect: (index: number, selected: boolean) => void;
  onSelectAll: (selected: boolean) => void;
  validationErrors: ProductValidationErrors;
}

function getConfidenceColor(score: number): 'success' | 'warning' | 'error' {
  if (score >= 0.8) return 'success';
  if (score >= 0.5) return 'warning';
  return 'error';
}

function getFieldError(errors: ValidationError[] | undefined, field: string): string | undefined {
  return errors?.find((e) => e.field === field)?.message;
}

export const ExtractedProductTable: React.FC<ExtractedProductTableProps> = ({
  products,
  selectedIndices,
  onProductChange,
  onProductSelect,
  onSelectAll,
  validationErrors,
}) => {
  const allSelected = products.length > 0 && selectedIndices.size === products.length;
  const someSelected = selectedIndices.size > 0 && selectedIndices.size < products.length;

  const handleSelectAll = (event: React.ChangeEvent<HTMLInputElement>) => {
    onSelectAll(event.target.checked);
  };

  const handleProductSelect = (index: number) => (event: React.ChangeEvent<HTMLInputElement>) => {
    onProductSelect(index, event.target.checked);
  };

  const handleFieldChange = (index: number, field: keyof ExtractedProduct) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = event.target.value;
    if (field === 'moq') {
      const numValue = value === '' ? null : parseInt(value, 10);
      onProductChange(index, field, isNaN(numValue as number) ? null : numValue);
    } else if (field === 'price_fob_usd') {
      const numValue = value === '' ? null : parseFloat(value);
      onProductChange(index, field, isNaN(numValue as number) ? null : numValue);
    } else {
      onProductChange(index, field, value || null);
    }
  };

  return (
    <TableContainer component={Paper} sx={{ maxHeight: 500 }}>
      <Table stickyHeader size="small">
        <TableHead>
          <TableRow>
            <TableCell padding="checkbox">
              <Checkbox
                indeterminate={someSelected}
                checked={allSelected}
                onChange={handleSelectAll}
              />
            </TableCell>
            <TableCell sx={{ minWidth: 60 }}>Image</TableCell>
            <TableCell sx={{ minWidth: 100 }}>SKU</TableCell>
            <TableCell sx={{ minWidth: 150 }}>Name</TableCell>
            <TableCell sx={{ minWidth: 200 }}>Description</TableCell>
            <TableCell sx={{ minWidth: 100 }}>Price (USD)</TableCell>
            <TableCell sx={{ minWidth: 80 }}>MOQ</TableCell>
            <TableCell sx={{ minWidth: 100 }}>Confidence</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {products.map((product, index) => {
            const errors = validationErrors[index];
            const hasErrors = errors && errors.length > 0;
            const isSelected = selectedIndices.has(index);

            return (
              <TableRow
                key={index}
                sx={{
                  backgroundColor: hasErrors ? 'rgba(244, 67, 54, 0.08)' : undefined,
                  '&:hover': {
                    backgroundColor: hasErrors ? 'rgba(244, 67, 54, 0.12)' : undefined,
                  },
                }}
              >
                <TableCell padding="checkbox">
                  <Checkbox checked={isSelected} onChange={handleProductSelect(index)} />
                </TableCell>
                <TableCell>
                  {product.image_urls.length > 0 ? (
                    <Avatar
                      src={product.image_urls[0]}
                      variant="rounded"
                      sx={{ width: 40, height: 40 }}
                    />
                  ) : (
                    <Avatar variant="rounded" sx={{ width: 40, height: 40 }}>
                      -
                    </Avatar>
                  )}
                </TableCell>
                <TableCell>
                  <Tooltip title={getFieldError(errors, 'sku') || ''} open={!!getFieldError(errors, 'sku')}>
                    <TextField
                      size="small"
                      value={product.sku || ''}
                      onChange={handleFieldChange(index, 'sku')}
                      error={!!getFieldError(errors, 'sku')}
                      sx={{ width: '100%' }}
                      inputProps={{ style: { fontSize: '0.875rem' } }}
                    />
                  </Tooltip>
                </TableCell>
                <TableCell>
                  <Tooltip title={getFieldError(errors, 'name') || ''} open={!!getFieldError(errors, 'name')}>
                    <TextField
                      size="small"
                      value={product.name || ''}
                      onChange={handleFieldChange(index, 'name')}
                      error={!!getFieldError(errors, 'name')}
                      sx={{ width: '100%' }}
                      inputProps={{ style: { fontSize: '0.875rem' } }}
                    />
                  </Tooltip>
                </TableCell>
                <TableCell>
                  <TextField
                    size="small"
                    value={product.description || ''}
                    onChange={handleFieldChange(index, 'description')}
                    multiline
                    maxRows={2}
                    sx={{ width: '100%' }}
                    inputProps={{ style: { fontSize: '0.875rem' } }}
                  />
                </TableCell>
                <TableCell>
                  <Tooltip title={getFieldError(errors, 'price_fob_usd') || ''} open={!!getFieldError(errors, 'price_fob_usd')}>
                    <TextField
                      size="small"
                      type="number"
                      value={product.price_fob_usd ?? ''}
                      onChange={handleFieldChange(index, 'price_fob_usd')}
                      error={!!getFieldError(errors, 'price_fob_usd')}
                      sx={{ width: '100%' }}
                      inputProps={{ style: { fontSize: '0.875rem' }, min: 0, step: 0.01 }}
                    />
                  </Tooltip>
                </TableCell>
                <TableCell>
                  <Tooltip title={getFieldError(errors, 'moq') || ''} open={!!getFieldError(errors, 'moq')}>
                    <TextField
                      size="small"
                      type="number"
                      value={product.moq ?? ''}
                      onChange={handleFieldChange(index, 'moq')}
                      error={!!getFieldError(errors, 'moq')}
                      sx={{ width: '100%' }}
                      inputProps={{ style: { fontSize: '0.875rem' }, min: 1 }}
                    />
                  </Tooltip>
                </TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Chip
                      label={`${Math.round(product.confidence_score * 100)}%`}
                      size="small"
                      color={getConfidenceColor(product.confidence_score)}
                    />
                  </Box>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </TableContainer>
  );
};
