import React, { useState, useCallback, useEffect } from 'react';
import {
  Box,
  TextField,
  InputAdornment,
  List,
  ListItem,
  ListItemButton,
  ListItemAvatar,
  ListItemText,
  Avatar,
  Typography,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Divider,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import AddIcon from '@mui/icons-material/Add';
import CheckIcon from '@mui/icons-material/Check';
import ImageNotSupportedIcon from '@mui/icons-material/ImageNotSupported';
import { productService, categoryService } from '@/services/kompassService';
import type { ProductResponse, CategoryResponse } from '@/types/kompass';

interface ProductCatalogMiniProps {
  onAddProduct: (productId: string) => void;
  isProductInPortfolio: (productId: string) => boolean;
}

const formatPrice = (price: number | string, currency: string): string => {
  const numPrice = typeof price === 'string' ? parseFloat(price) : price;
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency || 'USD',
  }).format(numPrice);
};

const ProductCatalogMini: React.FC<ProductCatalogMiniProps> = ({
  onAddProduct,
  isProductInPortfolio,
}) => {
  const [products, setProducts] = useState<ProductResponse[]>([]);
  const [categories, setCategories] = useState<CategoryResponse[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchValue, setSearchValue] = useState('');
  const [searchTimeout, setSearchTimeoutState] = useState<ReturnType<typeof setTimeout> | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  const fetchProducts = useCallback(async (search: string, categoryId: string, pageNum: number, append = false) => {
    setIsLoading(true);
    try {
      const response = await productService.list(pageNum, 20, {
        search: search || null,
        category_id: categoryId || null,
        status: 'active',
      });

      if (append) {
        setProducts(prev => [...prev, ...response.items]);
      } else {
        setProducts(response.items);
      }
      setHasMore(pageNum < response.pagination.pages);
    } catch (err) {
      console.error('ERROR [ProductCatalogMini]: Failed to fetch products:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProducts(searchValue, selectedCategory, 1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await categoryService.list(1, 100);
        setCategories(response.items);
      } catch (err) {
        console.error('ERROR [ProductCatalogMini]: Failed to fetch categories:', err);
      }
    };
    fetchCategories();
  }, []);

  const handleSearchChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const value = event.target.value;
      setSearchValue(value);

      if (searchTimeout) {
        clearTimeout(searchTimeout);
      }

      const timeout = setTimeout(() => {
        setPage(1);
        fetchProducts(value, selectedCategory, 1);
      }, 300);

      setSearchTimeoutState(timeout);
    },
    [searchTimeout, selectedCategory, fetchProducts]
  );

  const handleCategoryChange = (event: { target: { value: string } }) => {
    const value = event.target.value;
    setSelectedCategory(value);
    setPage(1);
    fetchProducts(searchValue, value, 1);
  };

  const handleScroll = (event: React.UIEvent<HTMLDivElement>) => {
    const target = event.target as HTMLDivElement;
    const isNearBottom = target.scrollHeight - target.scrollTop - target.clientHeight < 50;

    if (isNearBottom && !isLoading && hasMore) {
      const nextPage = page + 1;
      setPage(nextPage);
      fetchProducts(searchValue, selectedCategory, nextPage, true);
    }
  };

  const handleProductClick = (product: ProductResponse) => {
    if (!isProductInPortfolio(product.id)) {
      onAddProduct(product.id);
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="h6" sx={{ mb: 2, px: 1 }}>
        Product Catalog
      </Typography>

      {/* Search and Filter */}
      <Box sx={{ px: 1, mb: 2 }}>
        <TextField
          fullWidth
          placeholder="Search products..."
          value={searchValue}
          onChange={handleSearchChange}
          size="small"
          sx={{ mb: 1 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon fontSize="small" />
              </InputAdornment>
            ),
          }}
        />

        <FormControl fullWidth size="small">
          <InputLabel>Category</InputLabel>
          <Select
            value={selectedCategory}
            label="Category"
            onChange={handleCategoryChange}
          >
            <MenuItem value="">All Categories</MenuItem>
            {categories.map((category) => (
              <MenuItem key={category.id} value={category.id}>
                {category.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      <Divider />

      {/* Product List */}
      <Box
        sx={{
          flex: 1,
          overflow: 'auto',
          minHeight: 0,
        }}
        onScroll={handleScroll}
      >
        {products.length === 0 && !isLoading ? (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              py: 4,
              px: 2,
            }}
          >
            <Typography variant="body2" color="text.secondary" textAlign="center">
              No products found. Try adjusting your search or filters.
            </Typography>
          </Box>
        ) : (
          <List dense disablePadding>
            {products.map((product) => {
              const primaryImage = product.images?.find((img) => img.is_primary) || product.images?.[0];
              const inPortfolio = isProductInPortfolio(product.id);

              return (
                <ListItem
                  key={product.id}
                  disablePadding
                  secondaryAction={
                    inPortfolio ? (
                      <Chip
                        label="Added"
                        size="small"
                        color="success"
                        icon={<CheckIcon />}
                        sx={{ mr: 1 }}
                      />
                    ) : null
                  }
                >
                  <ListItemButton
                    onClick={() => handleProductClick(product)}
                    disabled={inPortfolio}
                    sx={{
                      opacity: inPortfolio ? 0.6 : 1,
                      '&:hover': {
                        backgroundColor: inPortfolio ? 'inherit' : 'action.hover',
                      },
                    }}
                  >
                    <ListItemAvatar>
                      {primaryImage ? (
                        <Avatar
                          variant="rounded"
                          src={primaryImage.url}
                          alt={product.name}
                          sx={{ width: 48, height: 48 }}
                        />
                      ) : (
                        <Avatar
                          variant="rounded"
                          sx={{ width: 48, height: 48, bgcolor: 'grey.200' }}
                        >
                          <ImageNotSupportedIcon sx={{ color: 'grey.400' }} />
                        </Avatar>
                      )}
                    </ListItemAvatar>
                    <ListItemText
                      primary={
                        <Typography
                          variant="body2"
                          sx={{
                            fontWeight: 500,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                            maxWidth: 180,
                          }}
                        >
                          {product.name}
                        </Typography>
                      }
                      secondary={
                        <Box component="span">
                          <Typography variant="caption" color="text.secondary" component="span">
                            {product.sku}
                          </Typography>
                          <Typography
                            variant="caption"
                            color="primary"
                            component="span"
                            sx={{ display: 'block' }}
                          >
                            {formatPrice(product.unit_price, product.currency)}
                          </Typography>
                        </Box>
                      }
                    />
                    {!inPortfolio && (
                      <AddIcon color="action" sx={{ ml: 1 }} />
                    )}
                  </ListItemButton>
                </ListItem>
              );
            })}
          </List>
        )}

        {isLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
            <CircularProgress size={24} />
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default ProductCatalogMini;
