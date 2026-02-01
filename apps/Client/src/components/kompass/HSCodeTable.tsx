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
  InputAdornment,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import SearchIcon from '@mui/icons-material/Search';
import type { HSCodeResponse } from '@/types/kompass';

interface HSCodeTableProps {
  hsCodes: HSCodeResponse[];
  loading: boolean;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  onAdd: () => void;
  onEdit: (hsCode: HSCodeResponse) => void;
  onDelete: (hsCode: HSCodeResponse) => void;
}

const HSCodeTable: React.FC<HSCodeTableProps> = ({
  hsCodes,
  loading,
  searchQuery,
  onSearchChange,
  onAdd,
  onEdit,
  onDelete,
}) => {
  const formatDutyRate = (rate: number | string): string => {
    const numRate = typeof rate === 'string' ? parseFloat(rate) : rate;
    return isNaN(numRate) ? '0' : numRate.toFixed(2);
  };

  return (
    <Box>
      {/* Search and Add Button */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <TextField
          placeholder="Search by code or description..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          size="small"
          sx={{ width: 350 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon color="action" />
              </InputAdornment>
            ),
          }}
          data-testid="hs-code-search"
        />
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={onAdd}
          data-testid="add-hs-code-btn"
        >
          Add HS Code
        </Button>
      </Box>

      {/* Loading State */}
      {loading && (
        <Box display="flex" justifyContent="center" py={4}>
          <CircularProgress />
        </Box>
      )}

      {/* Empty State */}
      {!loading && hsCodes.length === 0 && (
        <Box textAlign="center" py={4}>
          <Typography color="text.secondary">
            {searchQuery
              ? 'No HS codes found matching your search.'
              : 'No HS codes found. Click "Add HS Code" to create one.'}
          </Typography>
        </Box>
      )}

      {/* Table */}
      {!loading && hsCodes.length > 0 && (
        <TableContainer component={Paper} variant="outlined">
          <Table data-testid="hs-codes-table">
            <TableHead>
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold' }}>Code</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Description</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }} align="right">
                  Duty Rate (%)
                </TableCell>
                <TableCell sx={{ fontWeight: 'bold' }} align="center">
                  Actions
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {hsCodes.map((hsCode) => (
                <TableRow key={hsCode.id} hover>
                  <TableCell>
                    <Typography variant="body2" fontFamily="monospace">
                      {hsCode.code}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography
                      variant="body2"
                      sx={{
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                        maxWidth: 400,
                      }}
                      title={hsCode.description}
                    >
                      {hsCode.description}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2">{formatDutyRate(hsCode.duty_rate)}%</Typography>
                  </TableCell>
                  <TableCell align="center">
                    <IconButton
                      size="small"
                      onClick={() => onEdit(hsCode)}
                      aria-label="edit"
                      data-testid={`edit-hs-code-${hsCode.id}`}
                    >
                      <EditIcon fontSize="small" />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => onDelete(hsCode)}
                      aria-label="delete"
                      color="error"
                      data-testid={`delete-hs-code-${hsCode.id}`}
                    >
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
};

export default HSCodeTable;
