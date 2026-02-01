import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Tabs,
  Tab,
  TextField,
  InputAdornment,
  Grid,
  Card,
  CardContent,
  CardMedia,
  CardActions,
  Typography,
  Button,
  MenuItem,
  CircularProgress,
  Pagination,
  Chip,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import AddShoppingCartIcon from '@mui/icons-material/AddShoppingCart';
import CheckIcon from '@mui/icons-material/Check';
import ImageNotSupportedIcon from '@mui/icons-material/ImageNotSupported';
import { productService, portfolioService } from '@/services/kompassService';
import type { ProductResponse, PortfolioResponse } from '@/types/kompass';

interface ProductSelectorProps {
  addedProductIds: string[];
  onAddProduct: (product: ProductResponse) => void;
  disabled?: boolean;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => {
  return (
    <div role="tabpanel" hidden={value !== index}>
      {value === index && <Box pt={2}>{children}</Box>}
    </div>
  );
};

const ProductSelector: React.FC<ProductSelectorProps> = ({
  addedProductIds,
  onAddProduct,
  disabled = false,
}) => {
  const [tabValue, setTabValue] = useState(0);

  // Catalog state
  const [catalogSearch, setCatalogSearch] = useState('');
  const [catalogProducts, setCatalogProducts] = useState<ProductResponse[]>([]);
  const [catalogPage, setCatalogPage] = useState(1);
  const [catalogTotalPages, setCatalogTotalPages] = useState(1);
  const [catalogLoading, setCatalogLoading] = useState(false);

  // Portfolio state
  const [portfolios, setPortfolios] = useState<PortfolioResponse[]>([]);
  const [selectedPortfolioId, setSelectedPortfolioId] = useState<string>('');
  const [portfolioProducts, setPortfolioProducts] = useState<ProductResponse[]>([]);
  const [portfoliosLoading, setPortfoliosLoading] = useState(false);
  const [portfolioProductsLoading, setPortfolioProductsLoading] = useState(false);

  // Fetch catalog products
  const fetchCatalogProducts = useCallback(async () => {
    setCatalogLoading(true);
    try {
      const response = await productService.list(catalogPage, 8, {
        search: catalogSearch || undefined,
        status: 'active',
      });
      setCatalogProducts(response.items);
      setCatalogTotalPages(response.pagination.pages);
    } catch (err) {
      console.error('ERROR [ProductSelector]: Failed to fetch products:', err);
      setCatalogProducts([]);
    } finally {
      setCatalogLoading(false);
    }
  }, [catalogPage, catalogSearch]);

  // Fetch portfolios
  const fetchPortfolios = useCallback(async () => {
    setPortfoliosLoading(true);
    try {
      const response = await portfolioService.list(1, 100, { is_active: true });
      setPortfolios(response.items);
    } catch (err) {
      console.error('ERROR [ProductSelector]: Failed to fetch portfolios:', err);
      setPortfolios([]);
    } finally {
      setPortfoliosLoading(false);
    }
  }, []);

  // Fetch portfolio products
  const fetchPortfolioProducts = useCallback(async (portfolioId: string) => {
    if (!portfolioId) {
      setPortfolioProducts([]);
      return;
    }

    setPortfolioProductsLoading(true);
    try {
      const portfolio = await portfolioService.get(portfolioId);
      // Get full product details for each portfolio item
      const products: ProductResponse[] = [];
      for (const item of portfolio.items) {
        if (item.product_id) {
          try {
            const product = await productService.get(item.product_id);
            products.push(product);
          } catch {
            console.warn(`Product ${item.product_id} not found`);
          }
        }
      }
      setPortfolioProducts(products);
    } catch (err) {
      console.error('ERROR [ProductSelector]: Failed to fetch portfolio products:', err);
      setPortfolioProducts([]);
    } finally {
      setPortfolioProductsLoading(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    fetchCatalogProducts();
    fetchPortfolios();
  }, [fetchCatalogProducts, fetchPortfolios]);

  // Search debounce
  useEffect(() => {
    const timer = setTimeout(() => {
      setCatalogPage(1);
      fetchCatalogProducts();
    }, 300);

    return () => clearTimeout(timer);
  }, [catalogSearch, fetchCatalogProducts]);

  // Fetch portfolio products when selection changes
  useEffect(() => {
    fetchPortfolioProducts(selectedPortfolioId);
  }, [selectedPortfolioId, fetchPortfolioProducts]);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleAddProduct = (product: ProductResponse) => {
    if (!addedProductIds.includes(product.id)) {
      onAddProduct(product);
    }
  };

  const isProductAdded = (productId: string) => addedProductIds.includes(productId);

  const formatPrice = (price: number | string): string => {
    const numPrice = typeof price === 'string' ? parseFloat(price) : price;
    return `$${numPrice.toFixed(2)}`;
  };

  const renderProductCard = (product: ProductResponse) => {
    const isAdded = isProductAdded(product.id);
    const primaryImage = product.images?.find((img) => img.is_primary) || product.images?.[0];

    return (
      <Grid item xs={12} sm={6} md={4} lg={3} key={product.id}>
        <Card variant="outlined" sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
          {primaryImage ? (
            <CardMedia
              component="img"
              height="120"
              image={primaryImage.url}
              alt={product.name}
              sx={{ objectFit: 'cover' }}
            />
          ) : (
            <Box
              height={120}
              display="flex"
              alignItems="center"
              justifyContent="center"
              bgcolor="grey.100"
            >
              <ImageNotSupportedIcon color="disabled" fontSize="large" />
            </Box>
          )}

          <CardContent sx={{ flexGrow: 1, pb: 1 }}>
            <Typography variant="subtitle2" noWrap title={product.name}>
              {product.name}
            </Typography>
            <Typography variant="caption" color="text.secondary" display="block">
              SKU: {product.sku}
            </Typography>
            <Box mt={0.5} display="flex" alignItems="center" gap={1}>
              <Typography variant="body2" fontWeight="bold">
                {formatPrice(product.unit_price)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                FOB
              </Typography>
            </Box>
            {product.hs_code && (
              <Chip
                label={`HS: ${product.hs_code}`}
                size="small"
                variant="outlined"
                sx={{ mt: 0.5, fontSize: '0.65rem', height: 20 }}
              />
            )}
          </CardContent>

          <CardActions sx={{ pt: 0 }}>
            <Button
              size="small"
              variant={isAdded ? 'outlined' : 'contained'}
              color={isAdded ? 'success' : 'primary'}
              startIcon={isAdded ? <CheckIcon /> : <AddShoppingCartIcon />}
              onClick={() => handleAddProduct(product)}
              disabled={disabled || isAdded}
              fullWidth
            >
              {isAdded ? 'Added' : 'Add'}
            </Button>
          </CardActions>
        </Card>
      </Grid>
    );
  };

  return (
    <Box>
      <Tabs value={tabValue} onChange={handleTabChange} sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tab label="Biblia General" />
        <Tab label="From Portfolio" />
      </Tabs>

      {/* Catalog Tab */}
      <TabPanel value={tabValue} index={0}>
        <TextField
          fullWidth
          size="small"
          placeholder="Search products by name or SKU..."
          value={catalogSearch}
          onChange={(e) => setCatalogSearch(e.target.value)}
          disabled={disabled}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
          sx={{ mb: 2 }}
        />

        {catalogLoading ? (
          <Box display="flex" justifyContent="center" py={4}>
            <CircularProgress />
          </Box>
        ) : catalogProducts.length === 0 ? (
          <Box textAlign="center" py={4}>
            <Typography color="text.secondary">
              {catalogSearch ? 'No products found matching your search' : 'No products available'}
            </Typography>
          </Box>
        ) : (
          <>
            <Grid container spacing={2}>
              {catalogProducts.map(renderProductCard)}
            </Grid>

            {catalogTotalPages > 1 && (
              <Box display="flex" justifyContent="center" mt={3}>
                <Pagination
                  count={catalogTotalPages}
                  page={catalogPage}
                  onChange={(_, page) => setCatalogPage(page)}
                  color="primary"
                  disabled={disabled}
                />
              </Box>
            )}
          </>
        )}
      </TabPanel>

      {/* Portfolio Tab */}
      <TabPanel value={tabValue} index={1}>
        <TextField
          select
          fullWidth
          size="small"
          label="Select Portfolio"
          value={selectedPortfolioId}
          onChange={(e) => setSelectedPortfolioId(e.target.value)}
          disabled={disabled || portfoliosLoading}
          sx={{ mb: 2 }}
        >
          <MenuItem value="">
            <em>Select a portfolio...</em>
          </MenuItem>
          {portfolios.map((portfolio) => (
            <MenuItem key={portfolio.id} value={portfolio.id}>
              {portfolio.name} ({portfolio.item_count} items)
            </MenuItem>
          ))}
        </TextField>

        {!selectedPortfolioId ? (
          <Box textAlign="center" py={4}>
            <Typography color="text.secondary">
              Select a portfolio to view its products
            </Typography>
          </Box>
        ) : portfolioProductsLoading ? (
          <Box display="flex" justifyContent="center" py={4}>
            <CircularProgress />
          </Box>
        ) : portfolioProducts.length === 0 ? (
          <Box textAlign="center" py={4}>
            <Typography color="text.secondary">
              This portfolio has no products
            </Typography>
          </Box>
        ) : (
          <Grid container spacing={2}>
            {portfolioProducts.map(renderProductCard)}
          </Grid>
        )}
      </TabPanel>
    </Box>
  );
};

export default ProductSelector;
