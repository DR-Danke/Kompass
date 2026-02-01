import React from 'react';
import {
  Box,
  Button,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Typography,
  CircularProgress,
  Chip,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import WarningIcon from '@mui/icons-material/Warning';
import type { FreightRateResponse } from '@/types/kompass';

interface FreightRateFilters {
  origin: string;
  destination: string;
}

interface FreightRateTableProps {
  freightRates: FreightRateResponse[];
  loading: boolean;
  filters: FreightRateFilters;
  onFilterChange: (filters: FreightRateFilters) => void;
  onAdd: () => void;
  onEdit: (freightRate: FreightRateResponse) => void;
  onDelete: (freightRate: FreightRateResponse) => void;
}

const FreightRateTable: React.FC<FreightRateTableProps> = ({
  freightRates,
  loading,
  filters,
  onFilterChange,
  onAdd,
  onEdit,
  onDelete,
}) => {
  const isExpired = (validUntil: string | null): boolean => {
    if (!validUntil) return false;
    const expirationDate = new Date(validUntil);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return expirationDate < today;
  };

  const formatDate = (dateString: string | null): string => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  const formatRate = (rate: number | string | null): string => {
    if (rate === null || rate === undefined) return '-';
    const numRate = typeof rate === 'string' ? parseFloat(rate) : rate;
    return isNaN(numRate) ? '-' : `$${numRate.toFixed(2)}`;
  };

  const handleOriginChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onFilterChange({ ...filters, origin: e.target.value });
  };

  const handleDestinationChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onFilterChange({ ...filters, destination: e.target.value });
  };

  return (
    <Box>
      {/* Filters and Add Button */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2} gap={2}>
        <Box display="flex" gap={2}>
          <TextField
            placeholder="Filter by origin..."
            value={filters.origin}
            onChange={handleOriginChange}
            size="small"
            sx={{ width: 200 }}
            data-testid="freight-rate-origin-filter"
          />
          <TextField
            placeholder="Filter by destination..."
            value={filters.destination}
            onChange={handleDestinationChange}
            size="small"
            sx={{ width: 200 }}
            data-testid="freight-rate-destination-filter"
          />
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={onAdd}
          data-testid="add-freight-rate-btn"
        >
          Add Freight Rate
        </Button>
      </Box>

      {/* Loading State */}
      {loading && (
        <Box display="flex" justifyContent="center" py={4}>
          <CircularProgress />
        </Box>
      )}

      {/* Empty State */}
      {!loading && freightRates.length === 0 && (
        <Box textAlign="center" py={4}>
          <Typography color="text.secondary">
            {filters.origin || filters.destination
              ? 'No freight rates found matching your filters.'
              : 'No freight rates found. Click "Add Freight Rate" to create one.'}
          </Typography>
        </Box>
      )}

      {/* Table */}
      {!loading && freightRates.length > 0 && (
        <TableContainer component={Paper} variant="outlined">
          <Table data-testid="freight-rates-table" size="small">
            <TableHead>
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold' }}>Origin</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Destination</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Incoterm</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }} align="right">
                  Rate/kg
                </TableCell>
                <TableCell sx={{ fontWeight: 'bold' }} align="right">
                  Rate/cbm
                </TableCell>
                <TableCell sx={{ fontWeight: 'bold' }} align="right">
                  Min Charge
                </TableCell>
                <TableCell sx={{ fontWeight: 'bold' }} align="center">
                  Transit Days
                </TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Valid From</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Valid Until</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }} align="center">
                  Status
                </TableCell>
                <TableCell sx={{ fontWeight: 'bold' }} align="center">
                  Actions
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {freightRates.map((rate) => {
                const expired = isExpired(rate.valid_until);
                return (
                  <TableRow
                    key={rate.id}
                    hover
                    sx={{
                      backgroundColor: expired ? 'rgba(255, 152, 0, 0.08)' : 'inherit',
                    }}
                  >
                    <TableCell>
                      <Typography variant="body2">{rate.origin}</Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">{rate.destination}</Typography>
                    </TableCell>
                    <TableCell>
                      <Chip label={rate.incoterm} size="small" variant="outlined" />
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2">{formatRate(rate.rate_per_kg)}</Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2">{formatRate(rate.rate_per_cbm)}</Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2">{formatRate(rate.minimum_charge)}</Typography>
                    </TableCell>
                    <TableCell align="center">
                      <Typography variant="body2">{rate.transit_days ?? '-'}</Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">{formatDate(rate.valid_from)}</Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">{formatDate(rate.valid_until)}</Typography>
                    </TableCell>
                    <TableCell align="center">
                      {expired ? (
                        <Chip
                          icon={<WarningIcon />}
                          label="Expired"
                          size="small"
                          color="warning"
                          data-testid={`freight-rate-expired-${rate.id}`}
                        />
                      ) : rate.is_active ? (
                        <Chip label="Active" size="small" color="success" variant="outlined" />
                      ) : (
                        <Chip label="Inactive" size="small" color="default" variant="outlined" />
                      )}
                    </TableCell>
                    <TableCell align="center">
                      <IconButton
                        size="small"
                        onClick={() => onEdit(rate)}
                        aria-label="edit"
                        data-testid={`edit-freight-rate-${rate.id}`}
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => onDelete(rate)}
                        aria-label="delete"
                        color="error"
                        data-testid={`delete-freight-rate-${rate.id}`}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
};

export default FreightRateTable;
