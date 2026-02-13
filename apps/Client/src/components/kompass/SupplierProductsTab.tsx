import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Alert,
  CircularProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Avatar,
} from '@mui/material';
import ImageNotSupportedIcon from '@mui/icons-material/ImageNotSupported';
import ProductStatusBadge from './ProductStatusBadge';
import { supplierService } from '@/services/kompassService';
import type { ProductResponse } from '@/types/kompass';

interface SupplierProductsTabProps {
  supplierId: string;
  supplierName: string;
}

const formatPrice = (price: number | string, currency: string): string => {
  const numPrice = typeof price === 'string' ? parseFloat(price) : price;
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency || 'USD',
  }).format(numPrice);
};

const SupplierProductsTab: React.FC<SupplierProductsTabProps> = ({
  supplierId,
}) => {
  const [products, setProducts] = useState<ProductResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [total, setTotal] = useState(0);

  const fetchProducts = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      console.log(`INFO [SupplierProductsTab]: Fetching products for supplier ${supplierId}`);
      const response = await supplierService.getProducts(supplierId, page + 1, rowsPerPage);
      setProducts(response.items);
      setTotal(response.pagination.total);
    } catch (err) {
      console.log('ERROR [SupplierProductsTab]: Failed to fetch products', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch products');
    } finally {
      setLoading(false);
    }
  }, [supplierId, page, rowsPerPage]);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {products.length === 0 && !error ? (
        <Paper variant="outlined" sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="body1" color="text.secondary">
            No products associated with this supplier.
          </Typography>
        </Paper>
      ) : (
        <>
          <TableContainer component={Paper} variant="outlined">
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell sx={{ width: 60 }}>Image</TableCell>
                  <TableCell>Name</TableCell>
                  <TableCell>Category</TableCell>
                  <TableCell align="right" sx={{ width: 100 }}>Price</TableCell>
                  <TableCell align="right" sx={{ width: 80 }}>MOQ</TableCell>
                  <TableCell align="center" sx={{ width: 120 }}>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {products.map((product) => {
                  const primaryImage = product.images?.find((img) => img.is_primary) || product.images?.[0];

                  return (
                    <TableRow key={product.id} hover>
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
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>

          <TablePagination
            component="div"
            count={total}
            page={page}
            onPageChange={handleChangePage}
            rowsPerPage={rowsPerPage}
            onRowsPerPageChange={handleChangeRowsPerPage}
            rowsPerPageOptions={[5, 10, 20]}
          />
        </>
      )}
    </Box>
  );
};

export default SupplierProductsTab;
