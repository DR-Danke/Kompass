/**
 * TagChip Component
 * Displays a colored chip for a tag with optional delete and edit actions
 */

import React from 'react';
import { Chip, Box, Typography } from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import type { TagResponse, TagWithCount } from '@/types/kompass';

interface TagChipProps {
  tag: TagResponse | TagWithCount;
  onEdit?: (tag: TagResponse | TagWithCount) => void;
  onDelete?: (tag: TagResponse | TagWithCount) => void;
  showCount?: boolean;
}

/**
 * Calculate contrasting text color based on background color
 * Returns white for dark backgrounds and black for light backgrounds
 */
function getContrastColor(hexColor: string): string {
  const hex = hexColor.replace('#', '');
  const r = parseInt(hex.substring(0, 2), 16);
  const g = parseInt(hex.substring(2, 4), 16);
  const b = parseInt(hex.substring(4, 6), 16);
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
  return luminance > 0.5 ? '#000000' : '#ffffff';
}

export const TagChip: React.FC<TagChipProps> = ({
  tag,
  onEdit,
  onDelete,
  showCount = false,
}) => {
  const textColor = getContrastColor(tag.color);
  const productCount = 'product_count' in tag ? tag.product_count : undefined;

  const handleEdit = (e: React.MouseEvent) => {
    e.stopPropagation();
    onEdit?.(tag);
  };

  const handleDelete = () => {
    onDelete?.(tag);
  };

  const label = (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
      <Typography variant="body2" sx={{ color: textColor }}>
        {tag.name}
      </Typography>
      {showCount && productCount !== undefined && (
        <Typography
          variant="caption"
          sx={{
            color: textColor,
            opacity: 0.7,
            ml: 0.5,
          }}
        >
          ({productCount})
        </Typography>
      )}
    </Box>
  );

  return (
    <Chip
      label={label}
      onDelete={onDelete ? handleDelete : undefined}
      deleteIcon={
        onEdit ? (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <EditIcon
              sx={{
                fontSize: 16,
                color: textColor,
                opacity: 0.7,
                cursor: 'pointer',
                '&:hover': { opacity: 1 },
              }}
              onClick={handleEdit}
            />
          </Box>
        ) : undefined
      }
      sx={{
        backgroundColor: tag.color,
        color: textColor,
        '& .MuiChip-deleteIcon': {
          color: textColor,
          opacity: 0.7,
          '&:hover': {
            color: textColor,
            opacity: 1,
          },
        },
        '&:hover': {
          backgroundColor: tag.color,
          filter: 'brightness(0.9)',
        },
      }}
    />
  );
};
