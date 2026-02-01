import React from 'react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import {
  Card,
  CardContent,
  Box,
  Typography,
  TextField,
  IconButton,
  Avatar,
  Tooltip,
} from '@mui/material';
import DragIndicatorIcon from '@mui/icons-material/DragIndicator';
import DeleteIcon from '@mui/icons-material/Delete';
import ImageNotSupportedIcon from '@mui/icons-material/ImageNotSupported';
import type { PortfolioItemResponse, ProductResponse } from '@/types/kompass';

interface PortfolioItemCardProps {
  item: PortfolioItemResponse;
  product?: ProductResponse;
  onRemove: (itemId: string) => void;
  onNotesChange: (itemId: string, notes: string) => void;
}

const formatPrice = (price: number | string, currency: string): string => {
  const numPrice = typeof price === 'string' ? parseFloat(price) : price;
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency || 'USD',
  }).format(numPrice);
};

const PortfolioItemCard: React.FC<PortfolioItemCardProps> = ({
  item,
  product,
  onRemove,
  onNotesChange,
}) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: item.product_id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  const primaryImage = product?.images?.find((img) => img.is_primary) || product?.images?.[0];

  return (
    <Card
      ref={setNodeRef}
      style={style}
      sx={{
        mb: 1,
        border: isDragging ? '2px dashed' : '1px solid',
        borderColor: isDragging ? 'primary.main' : 'divider',
        backgroundColor: isDragging ? 'action.hover' : 'background.paper',
      }}
    >
      <CardContent sx={{ py: 1.5, px: 2, '&:last-child': { pb: 1.5 } }}>
        <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.5 }}>
          {/* Drag Handle */}
          <Box
            {...attributes}
            {...listeners}
            sx={{
              cursor: 'grab',
              display: 'flex',
              alignItems: 'center',
              color: 'text.secondary',
              '&:active': { cursor: 'grabbing' },
            }}
          >
            <DragIndicatorIcon />
          </Box>

          {/* Product Image */}
          {primaryImage ? (
            <Avatar
              variant="rounded"
              src={primaryImage.url}
              alt={product?.name || item.product_name || ''}
              sx={{ width: 56, height: 56 }}
            />
          ) : (
            <Avatar
              variant="rounded"
              sx={{ width: 56, height: 56, bgcolor: 'grey.200' }}
            >
              <ImageNotSupportedIcon sx={{ color: 'grey.400' }} />
            </Avatar>
          )}

          {/* Product Info */}
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography
              variant="subtitle2"
              sx={{
                fontWeight: 600,
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
            >
              {product?.name || item.product_name || 'Unknown Product'}
            </Typography>
            <Typography variant="caption" color="text.secondary" display="block">
              SKU: {product?.sku || item.product_sku || 'N/A'}
            </Typography>
            {product && (
              <Typography variant="body2" color="primary" sx={{ mt: 0.5 }}>
                {formatPrice(product.unit_price, product.currency)}
              </Typography>
            )}
          </Box>

          {/* Remove Button */}
          <Tooltip title="Remove from portfolio">
            <IconButton
              size="small"
              onClick={() => onRemove(item.id)}
              color="error"
              sx={{ mt: -0.5 }}
            >
              <DeleteIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>

        {/* Curator Notes */}
        <Box sx={{ mt: 1.5, pl: 4 }}>
          <TextField
            fullWidth
            size="small"
            placeholder="Add curator notes..."
            value={item.notes || ''}
            onChange={(e) => onNotesChange(item.id, e.target.value)}
            multiline
            maxRows={2}
            sx={{
              '& .MuiOutlinedInput-root': {
                backgroundColor: 'grey.50',
              },
            }}
          />
        </Box>
      </CardContent>
    </Card>
  );
};

export default PortfolioItemCard;
