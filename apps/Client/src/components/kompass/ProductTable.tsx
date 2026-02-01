import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TableSortLabel,
  Paper,
  IconButton,
  Checkbox,
  Avatar,
  Box,
  Tooltip,
  Typography,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import ImageNotSupportedIcon from '@mui/icons-material/ImageNotSupported';
import ProductStatusBadge from './ProductStatusBadge';
import type { ProductResponse } from '@/types/kompass';
import type { SortField, SortOrder } from '@/hooks/kompass/useProducts';

interface ProductTableProps {
  products: ProductResponse[];
  sortBy: SortField;
  sortOrder: SortOrder;
  onSortChange: (field: SortField) => void;
  selectedIds: string[];
  onSelect: (id: string) => void;
  onSelectAll: () => void;
  onEdit: (product: ProductResponse) => void;
  onDelete: (product: ProductResponse) => void;
}

interface HeadCell {
  id: SortField | 'image' | 'supplier' | 'category' | 'status' | 'actions';
  label: string;
  sortable: boolean;
  width?: number | string;
  align?: 'left' | 'center' | 'right';
}

const headCells: HeadCell[] = [
  { id: 'image', label: '', sortable: false, width: 60 },
  { id: 'name', label: 'Name', sortable: true },
  { id: 'supplier', label: 'Supplier', sortable: false },
  { id: 'category', label: 'Category', sortable: false },
  { id: 'unit_price', label: 'Price', sortable: true, align: 'right', width: 100 },
  { id: 'minimum_order_qty', label: 'MOQ', sortable: true, align: 'right', width: 80 },
  { id: 'status', label: 'Status', sortable: false, width: 120, align: 'center' },
  { id: 'created_at', label: 'Created', sortable: true, width: 110 },
  { id: 'actions', label: 'Actions', sortable: false, width: 100, align: 'center' },
];

const formatPrice = (price: number | string, currency: string): string => {
  const numPrice = typeof price === 'string' ? parseFloat(price) : price;
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency || 'USD',
  }).format(numPrice);
};

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

const ProductTable: React.FC<ProductTableProps> = ({
  products,
  sortBy,
  sortOrder,
  onSortChange,
  selectedIds,
  onSelect,
  onSelectAll,
  onEdit,
  onDelete,
}) => {
  const allSelected = products.length > 0 && selectedIds.length === products.length;
  const someSelected = selectedIds.length > 0 && selectedIds.length < products.length;

  const handleSort = (field: SortField) => {
    onSortChange(field);
  };

  return (
    <TableContainer component={Paper} sx={{ maxHeight: 'calc(100vh - 300px)' }}>
      <Table stickyHeader size="small">
        <TableHead>
          <TableRow>
            <TableCell padding="checkbox">
              <Checkbox
                indeterminate={someSelected}
                checked={allSelected}
                onChange={onSelectAll}
              />
            </TableCell>
            {headCells.map((cell) => (
              <TableCell
                key={cell.id}
                align={cell.align || 'left'}
                sx={{ width: cell.width, fontWeight: 600 }}
              >
                {cell.sortable ? (
                  <TableSortLabel
                    active={sortBy === cell.id}
                    direction={sortBy === cell.id ? sortOrder : 'asc'}
                    onClick={() => handleSort(cell.id as SortField)}
                  >
                    {cell.label}
                  </TableSortLabel>
                ) : (
                  cell.label
                )}
              </TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {products.map((product) => {
            const isSelected = selectedIds.includes(product.id);
            const primaryImage = product.images?.find((img) => img.is_primary) || product.images?.[0];

            return (
              <TableRow
                key={product.id}
                hover
                selected={isSelected}
                sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
              >
                <TableCell padding="checkbox">
                  <Checkbox
                    checked={isSelected}
                    onChange={() => onSelect(product.id)}
                  />
                </TableCell>

                <TableCell>
                  {primaryImage ? (
                    <Avatar
                      src={primaryImage.url}
                      alt={product.name}
                      variant="rounded"
                      sx={{ width: 40, height: 40 }}
                    />
                  ) : (
                    <Avatar variant="rounded" sx={{ width: 40, height: 40, bgcolor: 'grey.200' }}>
                      <ImageNotSupportedIcon sx={{ color: 'grey.400' }} />
                    </Avatar>
                  )}
                </TableCell>

                <TableCell>
                  <Box>
                    <Typography
                      variant="body2"
                      fontWeight={500}
                      sx={{
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                        maxWidth: 200,
                      }}
                    >
                      {product.name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {product.sku}
                    </Typography>
                  </Box>
                </TableCell>

                <TableCell>
                  <Typography
                    variant="body2"
                    sx={{
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                      maxWidth: 150,
                    }}
                  >
                    {product.supplier_name || '-'}
                  </Typography>
                </TableCell>

                <TableCell>
                  <Typography
                    variant="body2"
                    sx={{
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                      maxWidth: 120,
                    }}
                  >
                    {product.category_name || '-'}
                  </Typography>
                </TableCell>

                <TableCell align="right">
                  <Typography variant="body2" fontWeight={500}>
                    {formatPrice(product.unit_price, product.currency)}
                  </Typography>
                </TableCell>

                <TableCell align="right">
                  <Typography variant="body2">
                    {product.minimum_order_qty}
                  </Typography>
                </TableCell>

                <TableCell align="center">
                  <ProductStatusBadge status={product.status} />
                </TableCell>

                <TableCell>
                  <Typography variant="caption">
                    {formatDate(product.created_at)}
                  </Typography>
                </TableCell>

                <TableCell align="center">
                  <Box sx={{ display: 'flex', justifyContent: 'center', gap: 0.5 }}>
                    <Tooltip title="Edit">
                      <IconButton
                        size="small"
                        onClick={() => onEdit(product)}
                        color="primary"
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton
                        size="small"
                        onClick={() => onDelete(product)}
                        color="error"
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
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

export default ProductTable;
