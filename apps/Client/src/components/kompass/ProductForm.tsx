import React, { useState, useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Stepper,
  Step,
  StepLabel,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
  Box,
  Typography,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Chip,
  Autocomplete,
  CircularProgress,
  Alert,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import DeleteIcon from '@mui/icons-material/Delete';
import StarIcon from '@mui/icons-material/Star';
import StarBorderIcon from '@mui/icons-material/StarBorder';
import AddIcon from '@mui/icons-material/Add';
import {
  productService,
  supplierService,
  categoryService,
  tagService,
} from '@/services/kompassService';
import type {
  ProductResponse,
  ProductCreate,
  ProductUpdate,
  ProductStatus,
  SupplierResponse,
  CategoryTreeNode,
  TagResponse,
  ProductImageCreate,
  ProductImageResponse,
} from '@/types/kompass';

interface ProductFormProps {
  open: boolean;
  onClose: () => void;
  product?: ProductResponse | null;
  onSave: () => void;
}

interface FormData {
  name: string;
  sku: string;
  description: string;
  supplier_id: string;
  category_id: string;
  status: ProductStatus;
  unit_cost: string;
  unit_price: string;
  currency: string;
  unit_of_measure: string;
  minimum_order_qty: number;
  lead_time_days: number | null;
  weight_kg: string;
  dimensions: string;
  origin_country: string;
  hs_code_id: string;
}

const STEPS = ['Basic Info', 'Pricing', 'Details', 'Images', 'Tags'];

const PRODUCT_STATUSES: { value: ProductStatus; label: string }[] = [
  { value: 'active', label: 'Active' },
  { value: 'inactive', label: 'Inactive' },
  { value: 'draft', label: 'Draft' },
  { value: 'discontinued', label: 'Discontinued' },
];

const CURRENCIES = ['USD', 'EUR', 'GBP', 'CNY', 'JPY'];

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

const ProductForm: React.FC<ProductFormProps> = ({
  open,
  onClose,
  product,
  onSave,
}) => {
  const [activeStep, setActiveStep] = useState(0);
  const [suppliers, setSuppliers] = useState<SupplierResponse[]>([]);
  const [categories, setCategories] = useState<{ id: string; name: string; depth: number }[]>([]);
  const [tags, setTags] = useState<TagResponse[]>([]);
  const [selectedTags, setSelectedTags] = useState<TagResponse[]>([]);
  const [images, setImages] = useState<ProductImageResponse[]>([]);
  const [newImageUrl, setNewImageUrl] = useState('');
  const [newImageAlt, setNewImageAlt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isEditMode = !!product;

  const {
    control,
    handleSubmit,
    reset,
    formState: { errors },
    trigger,
  } = useForm<FormData>({
    defaultValues: {
      name: '',
      sku: '',
      description: '',
      supplier_id: '',
      category_id: '',
      status: 'draft',
      unit_cost: '0',
      unit_price: '0',
      currency: 'USD',
      unit_of_measure: 'pcs',
      minimum_order_qty: 1,
      lead_time_days: null,
      weight_kg: '',
      dimensions: '',
      origin_country: 'CN',
      hs_code_id: '',
    },
  });

  useEffect(() => {
    if (open) {
      setIsLoading(true);
      setError(null);
      setActiveStep(0);

      const loadData = async () => {
        try {
          const [suppliersRes, categoriesTree, tagsRes] = await Promise.all([
            supplierService.list(1, 100),
            categoryService.getTree(),
            tagService.list(1, 100),
          ]);

          setSuppliers(suppliersRes.items);
          setCategories(flattenCategories(categoriesTree));
          setTags(tagsRes.items);

          if (product) {
            reset({
              name: product.name,
              sku: product.sku,
              description: product.description || '',
              supplier_id: product.supplier_id,
              category_id: product.category_id || '',
              status: product.status,
              unit_cost: String(product.unit_cost),
              unit_price: String(product.unit_price),
              currency: product.currency,
              unit_of_measure: product.unit_of_measure,
              minimum_order_qty: product.minimum_order_qty,
              lead_time_days: product.lead_time_days,
              weight_kg: product.weight_kg ? String(product.weight_kg) : '',
              dimensions: product.dimensions || '',
              origin_country: product.origin_country,
              hs_code_id: product.hs_code_id || '',
            });
            setSelectedTags(product.tags || []);
            setImages(product.images || []);
          } else {
            reset({
              name: '',
              sku: '',
              description: '',
              supplier_id: '',
              category_id: '',
              status: 'draft',
              unit_cost: '0',
              unit_price: '0',
              currency: 'USD',
              unit_of_measure: 'pcs',
              minimum_order_qty: 1,
              lead_time_days: null,
              weight_kg: '',
              dimensions: '',
              origin_country: 'CN',
              hs_code_id: '',
            });
            setSelectedTags([]);
            setImages([]);
          }
        } catch (err) {
          console.error('ERROR [ProductForm]: Failed to load form data:', err);
          setError('Failed to load form data');
        } finally {
          setIsLoading(false);
        }
      };

      loadData();
    }
  }, [open, product, reset]);

  const handleNext = async () => {
    const fieldsToValidate = getFieldsForStep(activeStep);
    const isValid = await trigger(fieldsToValidate);
    if (isValid) {
      setActiveStep((prev) => prev + 1);
    }
  };

  const handleBack = () => {
    setActiveStep((prev) => prev - 1);
  };

  const getFieldsForStep = (step: number): (keyof FormData)[] => {
    switch (step) {
      case 0:
        return ['name', 'supplier_id'];
      case 1:
        return ['unit_cost', 'unit_price', 'currency'];
      case 2:
        return [];
      default:
        return [];
    }
  };

  const handleAddImage = async () => {
    if (!newImageUrl.trim()) return;

    if (isEditMode && product) {
      try {
        const imageData: ProductImageCreate = {
          url: newImageUrl.trim(),
          alt_text: newImageAlt.trim() || null,
          is_primary: images.length === 0,
        };
        const newImage = await productService.addImage(product.id, imageData);
        setImages((prev) => [...prev, newImage]);
        setNewImageUrl('');
        setNewImageAlt('');
      } catch (err) {
        console.error('ERROR [ProductForm]: Failed to add image:', err);
        setError('Failed to add image');
      }
    } else {
      const tempImage: ProductImageResponse = {
        id: `temp-${Date.now()}`,
        product_id: '',
        url: newImageUrl.trim(),
        alt_text: newImageAlt.trim() || null,
        sort_order: images.length,
        is_primary: images.length === 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      setImages((prev) => [...prev, tempImage]);
      setNewImageUrl('');
      setNewImageAlt('');
    }
  };

  const handleRemoveImage = async (imageId: string) => {
    if (isEditMode && product && !imageId.startsWith('temp-')) {
      try {
        await productService.removeImage(product.id, imageId);
        setImages((prev) => prev.filter((img) => img.id !== imageId));
      } catch (err) {
        console.error('ERROR [ProductForm]: Failed to remove image:', err);
        setError('Failed to remove image');
      }
    } else {
      setImages((prev) => prev.filter((img) => img.id !== imageId));
    }
  };

  const handleSetPrimaryImage = async (imageId: string) => {
    if (isEditMode && product && !imageId.startsWith('temp-')) {
      try {
        await productService.setPrimaryImage(product.id, imageId);
        setImages((prev) =>
          prev.map((img) => ({
            ...img,
            is_primary: img.id === imageId,
          }))
        );
      } catch (err) {
        console.error('ERROR [ProductForm]: Failed to set primary image:', err);
        setError('Failed to set primary image');
      }
    } else {
      setImages((prev) =>
        prev.map((img) => ({
          ...img,
          is_primary: img.id === imageId,
        }))
      );
    }
  };

  const onSubmit = async (data: FormData) => {
    setIsSaving(true);
    setError(null);

    try {
      if (isEditMode && product) {
        const updateData: ProductUpdate = {
          name: data.name,
          sku: data.sku || null,
          description: data.description || null,
          supplier_id: data.supplier_id,
          category_id: data.category_id || null,
          status: data.status,
          unit_cost: parseFloat(data.unit_cost),
          unit_price: parseFloat(data.unit_price),
          currency: data.currency,
          unit_of_measure: data.unit_of_measure,
          minimum_order_qty: data.minimum_order_qty,
          lead_time_days: data.lead_time_days,
          weight_kg: data.weight_kg ? parseFloat(data.weight_kg) : null,
          dimensions: data.dimensions || null,
          origin_country: data.origin_country,
          hs_code_id: data.hs_code_id || null,
        };

        await productService.update(product.id, updateData);

        const existingTagIds = new Set(product.tags?.map((t) => t.id) || []);
        const newTagIds = new Set(selectedTags.map((t) => t.id));

        for (const tagId of existingTagIds) {
          if (!newTagIds.has(tagId)) {
            await productService.removeTag(product.id, tagId);
          }
        }

        for (const tagId of newTagIds) {
          if (!existingTagIds.has(tagId)) {
            await productService.addTag(product.id, tagId);
          }
        }
      } else {
        const createData: ProductCreate = {
          name: data.name,
          sku: data.sku || null,
          description: data.description || null,
          supplier_id: data.supplier_id,
          category_id: data.category_id || null,
          status: data.status,
          unit_cost: parseFloat(data.unit_cost),
          unit_price: parseFloat(data.unit_price),
          currency: data.currency,
          unit_of_measure: data.unit_of_measure,
          minimum_order_qty: data.minimum_order_qty,
          lead_time_days: data.lead_time_days,
          weight_kg: data.weight_kg ? parseFloat(data.weight_kg) : null,
          dimensions: data.dimensions || null,
          origin_country: data.origin_country,
          hs_code_id: data.hs_code_id || null,
          images: images.map((img) => ({
            url: img.url,
            alt_text: img.alt_text,
            is_primary: img.is_primary,
          })),
          tag_ids: selectedTags.map((t) => t.id),
        };

        await productService.create(createData);
      }

      onSave();
      onClose();
    } catch (err) {
      console.error('ERROR [ProductForm]: Failed to save product:', err);
      setError('Failed to save product');
    } finally {
      setIsSaving(false);
    }
  };

  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Controller
              name="name"
              control={control}
              rules={{ required: 'Product name is required' }}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Product Name"
                  fullWidth
                  required
                  error={!!errors.name}
                  helperText={errors.name?.message}
                />
              )}
            />

            <Controller
              name="sku"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="SKU"
                  fullWidth
                  helperText="Leave blank to auto-generate"
                />
              )}
            />

            <Controller
              name="description"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  label="Description"
                  fullWidth
                  multiline
                  rows={3}
                />
              )}
            />

            <Controller
              name="supplier_id"
              control={control}
              rules={{ required: 'Supplier is required' }}
              render={({ field }) => (
                <FormControl fullWidth required error={!!errors.supplier_id}>
                  <InputLabel>Supplier</InputLabel>
                  <Select {...field} label="Supplier">
                    {suppliers.map((supplier) => (
                      <MenuItem key={supplier.id} value={supplier.id}>
                        {supplier.name}
                      </MenuItem>
                    ))}
                  </Select>
                  {errors.supplier_id && (
                    <FormHelperText>{errors.supplier_id.message}</FormHelperText>
                  )}
                </FormControl>
              )}
            />

            <Controller
              name="category_id"
              control={control}
              render={({ field }) => (
                <FormControl fullWidth>
                  <InputLabel>Category</InputLabel>
                  <Select {...field} label="Category">
                    <MenuItem value="">
                      <em>None</em>
                    </MenuItem>
                    {categories.map((category) => (
                      <MenuItem key={category.id} value={category.id}>
                        {'—'.repeat(category.depth)} {category.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              )}
            />

            <Controller
              name="status"
              control={control}
              render={({ field }) => (
                <FormControl fullWidth>
                  <InputLabel>Status</InputLabel>
                  <Select {...field} label="Status">
                    {PRODUCT_STATUSES.map((status) => (
                      <MenuItem key={status.value} value={status.value}>
                        {status.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              )}
            />
          </Box>
        );

      case 1:
        return (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Controller
                name="unit_cost"
                control={control}
                rules={{ required: 'Unit cost is required' }}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Unit Cost"
                    type="number"
                    fullWidth
                    required
                    error={!!errors.unit_cost}
                    helperText={errors.unit_cost?.message}
                    InputProps={{ inputProps: { min: 0, step: 0.01 } }}
                  />
                )}
              />

              <Controller
                name="unit_price"
                control={control}
                rules={{ required: 'Unit price is required' }}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Unit Price"
                    type="number"
                    fullWidth
                    required
                    error={!!errors.unit_price}
                    helperText={errors.unit_price?.message}
                    InputProps={{ inputProps: { min: 0, step: 0.01 } }}
                  />
                )}
              />
            </Box>

            <Box sx={{ display: 'flex', gap: 2 }}>
              <Controller
                name="currency"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth>
                    <InputLabel>Currency</InputLabel>
                    <Select {...field} label="Currency">
                      {CURRENCIES.map((curr) => (
                        <MenuItem key={curr} value={curr}>
                          {curr}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                )}
              />

              <Controller
                name="unit_of_measure"
                control={control}
                render={({ field }) => (
                  <TextField {...field} label="Unit of Measure" fullWidth />
                )}
              />
            </Box>
          </Box>
        );

      case 2:
        return (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Controller
                name="minimum_order_qty"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Minimum Order Qty"
                    type="number"
                    fullWidth
                    InputProps={{ inputProps: { min: 1 } }}
                    onChange={(e) => field.onChange(parseInt(e.target.value) || 1)}
                  />
                )}
              />

              <Controller
                name="lead_time_days"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Lead Time (days)"
                    type="number"
                    fullWidth
                    InputProps={{ inputProps: { min: 0 } }}
                    onChange={(e) => field.onChange(e.target.value ? parseInt(e.target.value) : null)}
                    value={field.value ?? ''}
                  />
                )}
              />
            </Box>

            <Box sx={{ display: 'flex', gap: 2 }}>
              <Controller
                name="weight_kg"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Weight (kg)"
                    type="number"
                    fullWidth
                    InputProps={{ inputProps: { min: 0, step: 0.01 } }}
                  />
                )}
              />

              <Controller
                name="dimensions"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Dimensions (L x W x H)"
                    fullWidth
                    placeholder="e.g., 10x5x3 cm"
                  />
                )}
              />
            </Box>

            <Controller
              name="origin_country"
              control={control}
              render={({ field }) => (
                <TextField {...field} label="Origin Country" fullWidth />
              )}
            />
          </Box>
        );

      case 3:
        return (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Typography variant="subtitle2">Product Images</Typography>

            <Box sx={{ display: 'flex', gap: 1 }}>
              <TextField
                size="small"
                label="Image URL"
                value={newImageUrl}
                onChange={(e) => setNewImageUrl(e.target.value)}
                fullWidth
                placeholder="https://example.com/image.jpg"
              />
              <TextField
                size="small"
                label="Alt Text"
                value={newImageAlt}
                onChange={(e) => setNewImageAlt(e.target.value)}
                sx={{ width: 200 }}
              />
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={handleAddImage}
                disabled={!newImageUrl.trim()}
              >
                Add
              </Button>
            </Box>

            {images.length > 0 ? (
              <List>
                {images.map((image) => (
                  <ListItem key={image.id} divider>
                    <Box
                      component="img"
                      src={image.url}
                      alt={image.alt_text || 'Product image'}
                      sx={{
                        width: 50,
                        height: 50,
                        objectFit: 'cover',
                        borderRadius: 1,
                        mr: 2,
                      }}
                      onError={(e) => {
                        (e.target as HTMLImageElement).src = '/placeholder.png';
                      }}
                    />
                    <ListItemText
                      primary={image.alt_text || 'No description'}
                      secondary={image.url}
                      secondaryTypographyProps={{
                        sx: {
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                          maxWidth: 300,
                        },
                      }}
                    />
                    <ListItemSecondaryAction>
                      <IconButton
                        edge="end"
                        onClick={() => handleSetPrimaryImage(image.id)}
                        color={image.is_primary ? 'primary' : 'default'}
                      >
                        {image.is_primary ? <StarIcon /> : <StarBorderIcon />}
                      </IconButton>
                      <IconButton
                        edge="end"
                        onClick={() => handleRemoveImage(image.id)}
                        color="error"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            ) : (
              <Typography color="text.secondary" sx={{ py: 2, textAlign: 'center' }}>
                No images added yet
              </Typography>
            )}
          </Box>
        );

      case 4:
        return (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Typography variant="subtitle2">Product Tags</Typography>

            <Autocomplete
              multiple
              options={tags}
              getOptionLabel={(option) => option.name}
              value={selectedTags}
              onChange={(_, newValue) => setSelectedTags(newValue)}
              renderInput={(params) => (
                <TextField {...params} label="Select Tags" placeholder="Add tags..." />
              )}
              renderTags={(value, getTagProps) =>
                value.map((option, index) => (
                  <Chip
                    {...getTagProps({ index })}
                    key={option.id}
                    label={option.name}
                    sx={{ backgroundColor: option.color }}
                  />
                ))
              }
            />

            {selectedTags.length > 0 && (
              <Box sx={{ mt: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  Selected: {selectedTags.length} tag(s)
                </Typography>
              </Box>
            )}
          </Box>
        );

      default:
        return null;
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">
            {isEditMode ? 'Edit Product' : 'Add New Product'}
          </Typography>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent>
        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            {error && (
              <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
                {error}
              </Alert>
            )}

            <Stepper activeStep={activeStep} sx={{ mb: 3 }}>
              {STEPS.map((label) => (
                <Step key={label}>
                  <StepLabel>{label}</StepLabel>
                </Step>
              ))}
            </Stepper>

            <Box sx={{ minHeight: 300 }}>
              {renderStepContent(activeStep)}
            </Box>
          </>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button onClick={onClose} disabled={isSaving}>
          Cancel
        </Button>
        <Box sx={{ flex: 1 }} />
        <Button
          onClick={handleBack}
          disabled={activeStep === 0 || isSaving}
        >
          Back
        </Button>
        {activeStep === STEPS.length - 1 ? (
          <Button
            variant="contained"
            onClick={handleSubmit(onSubmit)}
            disabled={isSaving}
          >
            {isSaving ? <CircularProgress size={24} /> : isEditMode ? 'Update' : 'Create'}
          </Button>
        ) : (
          <Button variant="contained" onClick={handleNext} disabled={isSaving}>
            Next
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default ProductForm;
