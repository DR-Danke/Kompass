import React from 'react';
import {
  Card,
  CardMedia,
  CardContent,
  CardActions,
  Typography,
  Box,
  IconButton,
  Chip,
  Checkbox,
  Tooltip,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import ImageNotSupportedIcon from '@mui/icons-material/ImageNotSupported';
import ProductStatusBadge from './ProductStatusBadge';
import type { ProductResponse } from '@/types/kompass';

interface ProductCardProps {
  product: ProductResponse;
  selected?: boolean;
  onSelect?: (id: string) => void;
  onEdit?: (product: ProductResponse) => void;
  onDelete?: (product: ProductResponse) => void;
}

const formatPrice = (price: number | string, currency: string): string => {
  const numPrice = typeof price === 'string' ? parseFloat(price) : price;
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency || 'USD',
  }).format(numPrice);
};

const ProductCard: React.FC<ProductCardProps> = ({
  product,
  selected = false,
  onSelect,
  onEdit,
  onDelete,
}) => {
  const primaryImage = product.images?.find((img) => img.is_primary) || product.images?.[0];
  const displayTags = product.tags?.slice(0, 3) || [];
  const hasMoreTags = (product.tags?.length || 0) > 3;

  return (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
        transition: 'box-shadow 0.2s',
        '&:hover': {
          boxShadow: 4,
        },
        ...(selected && {
          outline: '2px solid',
          outlineColor: 'primary.main',
        }),
      }}
    >
      {onSelect && (
        <Checkbox
          checked={selected}
          onChange={() => onSelect(product.id)}
          sx={{
            position: 'absolute',
            top: 4,
            left: 4,
            zIndex: 1,
            backgroundColor: 'rgba(255, 255, 255, 0.8)',
            borderRadius: 1,
            '&:hover': {
              backgroundColor: 'rgba(255, 255, 255, 0.9)',
            },
          }}
        />
      )}

      {primaryImage ? (
        <CardMedia
          component="img"
          height="160"
          image={primaryImage.url}
          alt={primaryImage.alt_text || product.name}
          sx={{ objectFit: 'cover' }}
        />
      ) : (
        <Box
          sx={{
            height: 160,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: 'grey.200',
          }}
        >
          <ImageNotSupportedIcon sx={{ fontSize: 48, color: 'grey.400' }} />
        </Box>
      )}

      <CardContent sx={{ flexGrow: 1, pb: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
          <Typography
            variant="subtitle1"
            component="h3"
            sx={{
              fontWeight: 600,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
              flex: 1,
              mr: 1,
            }}
          >
            {product.name}
          </Typography>
          <ProductStatusBadge status={product.status} />
        </Box>

        <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
          SKU: {product.sku}
        </Typography>

        <Typography variant="h6" color="primary" sx={{ mb: 1 }}>
          {formatPrice(product.unit_price, product.currency)}
        </Typography>

        {product.supplier_name && (
          <Chip
            label={product.supplier_name}
            size="small"
            variant="outlined"
            sx={{ mb: 1 }}
          />
        )}

        {displayTags.length > 0 && (
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 1 }}>
            {displayTags.map((tag) => (
              <Chip
                key={tag.id}
                label={tag.name}
                size="small"
                sx={{
                  backgroundColor: tag.color,
                  color: 'white',
                  fontSize: '0.7rem',
                }}
              />
            ))}
            {hasMoreTags && (
              <Chip
                label={`+${(product.tags?.length || 0) - 3}`}
                size="small"
                variant="outlined"
                sx={{ fontSize: '0.7rem' }}
              />
            )}
          </Box>
        )}

        <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1 }}>
          MOQ: {product.minimum_order_qty} {product.unit_of_measure}
        </Typography>
      </CardContent>

      <CardActions sx={{ justifyContent: 'flex-end', pt: 0 }}>
        <Tooltip title="Edit">
          <IconButton
            size="small"
            onClick={() => onEdit?.(product)}
            color="primary"
          >
            <EditIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        <Tooltip title="Delete">
          <IconButton
            size="small"
            onClick={() => onDelete?.(product)}
            color="error"
          >
            <DeleteIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </CardActions>
    </Card>
  );
};

export default ProductCard;
