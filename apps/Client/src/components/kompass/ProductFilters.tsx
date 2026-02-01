import React, { useState, useEffect } from 'react';
import {
  Box,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Slider,
  Checkbox,
  FormControlLabel,
  Button,
  Autocomplete,
  Chip,
  CircularProgress,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import FilterListIcon from '@mui/icons-material/FilterList';
import ClearIcon from '@mui/icons-material/Clear';
import { supplierService, categoryService, tagService } from '@/services/kompassService';
import type {
  SupplierResponse,
  CategoryTreeNode,
  TagResponse,
  ProductStatus,
} from '@/types/kompass';
import type { ProductFilters as ProductFiltersType } from '@/hooks/kompass/useProducts';

interface ProductFiltersProps {
  filters: ProductFiltersType;
  onFilterChange: <K extends keyof ProductFiltersType>(key: K, value: ProductFiltersType[K]) => void;
  onClearFilters: () => void;
}

const PRODUCT_STATUSES: { value: ProductStatus; label: string }[] = [
  { value: 'active', label: 'Active' },
  { value: 'inactive', label: 'Inactive' },
  { value: 'draft', label: 'Draft' },
  { value: 'discontinued', label: 'Discontinued' },
];

const flattenCategories = (nodes: CategoryTreeNode[], depth = 0): { id: string; name: string; depth: number }[] => {
  const result: { id: string; name: string; depth: number }[] = [];
  for (const node of nodes) {
    result.push({ id: node.id, name: node.name, depth });
    if (node.children && node.children.length > 0) {
      result.push(...flattenCategories(node.children, depth + 1));
    }
  }
  return result;
};

const ProductFilters: React.FC<ProductFiltersProps> = ({
  filters,
  onFilterChange,
  onClearFilters,
}) => {
  const [suppliers, setSuppliers] = useState<SupplierResponse[]>([]);
  const [categories, setCategories] = useState<{ id: string; name: string; depth: number }[]>([]);
  const [tags, setTags] = useState<TagResponse[]>([]);
  const [loadingSuppliers, setLoadingSuppliers] = useState(false);
  const [loadingCategories, setLoadingCategories] = useState(false);
  const [loadingTags, setLoadingTags] = useState(false);
  const [expanded, setExpanded] = useState(true);
  const [priceRange, setPriceRange] = useState<[number, number]>([0, 10000]);

  useEffect(() => {
    const fetchSuppliers = async () => {
      setLoadingSuppliers(true);
      try {
        const response = await supplierService.list(1, 100);
        setSuppliers(response.items);
      } catch (err) {
        console.error('ERROR [ProductFilters]: Failed to fetch suppliers:', err);
      } finally {
        setLoadingSuppliers(false);
      }
    };

    const fetchCategories = async () => {
      setLoadingCategories(true);
      try {
        const tree = await categoryService.getTree();
        setCategories(flattenCategories(tree));
      } catch (err) {
        console.error('ERROR [ProductFilters]: Failed to fetch categories:', err);
      } finally {
        setLoadingCategories(false);
      }
    };

    const fetchTags = async () => {
      setLoadingTags(true);
      try {
        const response = await tagService.list(1, 100);
        setTags(response.items);
      } catch (err) {
        console.error('ERROR [ProductFilters]: Failed to fetch tags:', err);
      } finally {
        setLoadingTags(false);
      }
    };

    fetchSuppliers();
    fetchCategories();
    fetchTags();
  }, []);

  const handlePriceRangeChange = (_event: Event, newValue: number | number[]) => {
    const [min, max] = newValue as number[];
    setPriceRange([min, max]);
  };

  const handlePriceRangeCommit = () => {
    onFilterChange('min_price', priceRange[0] > 0 ? priceRange[0] : null);
    onFilterChange('max_price', priceRange[1] < 10000 ? priceRange[1] : null);
  };

  const selectedTags = tags.filter((t) => filters.tag_ids?.includes(t.id));

  const hasActiveFilters =
    filters.supplier_id ||
    filters.category_id ||
    filters.status ||
    filters.min_price ||
    filters.max_price ||
    filters.min_moq ||
    filters.max_moq ||
    (filters.tag_ids && filters.tag_ids.length > 0) ||
    filters.has_images !== null;

  return (
    <Accordion expanded={expanded} onChange={() => setExpanded(!expanded)}>
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <FilterListIcon />
          <Typography>Filters</Typography>
          {hasActiveFilters && (
            <Chip label="Active" size="small" color="primary" />
          )}
        </Box>
      </AccordionSummary>
      <AccordionDetails>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {/* Supplier */}
          <FormControl fullWidth size="small">
            <InputLabel>Supplier</InputLabel>
            <Select
              value={filters.supplier_id || ''}
              label="Supplier"
              onChange={(e) => onFilterChange('supplier_id', e.target.value || null)}
              disabled={loadingSuppliers}
            >
              <MenuItem value="">
                <em>All Suppliers</em>
              </MenuItem>
              {suppliers.map((supplier) => (
                <MenuItem key={supplier.id} value={supplier.id}>
                  {supplier.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* Category */}
          <FormControl fullWidth size="small">
            <InputLabel>Category</InputLabel>
            <Select
              value={filters.category_id || ''}
              label="Category"
              onChange={(e) => onFilterChange('category_id', e.target.value || null)}
              disabled={loadingCategories}
            >
              <MenuItem value="">
                <em>All Categories</em>
              </MenuItem>
              {categories.map((category) => (
                <MenuItem key={category.id} value={category.id}>
                  {'—'.repeat(category.depth)} {category.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* Status */}
          <FormControl fullWidth size="small">
            <InputLabel>Status</InputLabel>
            <Select
              value={filters.status || ''}
              label="Status"
              onChange={(e) => onFilterChange('status', (e.target.value as ProductStatus) || null)}
            >
              <MenuItem value="">
                <em>All Statuses</em>
              </MenuItem>
              {PRODUCT_STATUSES.map((status) => (
                <MenuItem key={status.value} value={status.value}>
                  {status.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* Price Range */}
          <Box>
            <Typography variant="body2" gutterBottom>
              Price Range (USD)
            </Typography>
            <Box sx={{ px: 1 }}>
              <Slider
                value={priceRange}
                onChange={handlePriceRangeChange}
                onChangeCommitted={handlePriceRangeCommit}
                valueLabelDisplay="auto"
                min={0}
                max={10000}
                step={100}
              />
            </Box>
            <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
              <TextField
                size="small"
                type="number"
                label="Min"
                value={priceRange[0]}
                onChange={(e) => {
                  const val = parseInt(e.target.value) || 0;
                  setPriceRange([val, priceRange[1]]);
                }}
                onBlur={handlePriceRangeCommit}
                InputProps={{ inputProps: { min: 0 } }}
              />
              <TextField
                size="small"
                type="number"
                label="Max"
                value={priceRange[1]}
                onChange={(e) => {
                  const val = parseInt(e.target.value) || 10000;
                  setPriceRange([priceRange[0], val]);
                }}
                onBlur={handlePriceRangeCommit}
                InputProps={{ inputProps: { min: 0 } }}
              />
            </Box>
          </Box>

          {/* MOQ Range */}
          <Box>
            <Typography variant="body2" gutterBottom>
              Minimum Order Quantity
            </Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <TextField
                size="small"
                type="number"
                label="Min MOQ"
                value={filters.min_moq ?? ''}
                onChange={(e) => onFilterChange('min_moq', e.target.value ? parseInt(e.target.value) : null)}
                InputProps={{ inputProps: { min: 0 } }}
              />
              <TextField
                size="small"
                type="number"
                label="Max MOQ"
                value={filters.max_moq ?? ''}
                onChange={(e) => onFilterChange('max_moq', e.target.value ? parseInt(e.target.value) : null)}
                InputProps={{ inputProps: { min: 0 } }}
              />
            </Box>
          </Box>

          {/* Tags */}
          <Autocomplete
            multiple
            size="small"
            options={tags}
            loading={loadingTags}
            getOptionLabel={(option) => option.name}
            value={selectedTags}
            onChange={(_, newValue) => {
              onFilterChange('tag_ids', newValue.length > 0 ? newValue.map((t) => t.id) : null);
            }}
            renderInput={(params) => (
              <TextField
                {...params}
                label="Tags"
                InputProps={{
                  ...params.InputProps,
                  endAdornment: (
                    <>
                      {loadingTags ? <CircularProgress color="inherit" size={20} /> : null}
                      {params.InputProps.endAdornment}
                    </>
                  ),
                }}
              />
            )}
            renderTags={(value, getTagProps) =>
              value.map((option, index) => (
                <Chip
                  {...getTagProps({ index })}
                  key={option.id}
                  label={option.name}
                  size="small"
                  sx={{ backgroundColor: option.color }}
                />
              ))
            }
          />

          {/* Has Images */}
          <FormControlLabel
            control={
              <Checkbox
                checked={filters.has_images === true}
                indeterminate={filters.has_images === null}
                onChange={() => {
                  if (filters.has_images === null) {
                    onFilterChange('has_images', true);
                  } else if (filters.has_images === true) {
                    onFilterChange('has_images', false);
                  } else {
                    onFilterChange('has_images', null);
                  }
                }}
              />
            }
            label={
              filters.has_images === null
                ? 'Has Images (Any)'
                : filters.has_images
                  ? 'Has Images (Yes)'
                  : 'Has Images (No)'
            }
          />

          {/* Clear Filters */}
          <Button
            variant="outlined"
            color="secondary"
            startIcon={<ClearIcon />}
            onClick={onClearFilters}
            disabled={!hasActiveFilters}
            fullWidth
          >
            Clear Filters
          </Button>
        </Box>
      </AccordionDetails>
    </Accordion>
  );
};

export default ProductFilters;
