import React from 'react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import {
  Card,
  CardContent,
  Typography,
  Chip,
  Box,
  Tooltip,
} from '@mui/material';
import BusinessIcon from '@mui/icons-material/Business';
import PersonIcon from '@mui/icons-material/Person';
import PublicIcon from '@mui/icons-material/Public';
import InventoryIcon from '@mui/icons-material/Inventory';
import VerifiedIcon from '@mui/icons-material/Verified';
import type { SupplierWithProductCount, CertificationStatus } from '@/types/kompass';

interface SupplierCardProps {
  supplier: SupplierWithProductCount;
  onClick?: (supplier: SupplierWithProductCount) => void;
  isDragging?: boolean;
}

const getCertificationColor = (status: CertificationStatus): string => {
  switch (status) {
    case 'certified_a':
      return '#1b5e20';
    case 'certified_b':
      return '#388e3c';
    case 'certified_c':
      return '#66bb6a';
    case 'pending_review':
      return '#f57c00';
    default:
      return '#9e9e9e';
  }
};

const getCertificationLabel = (status: CertificationStatus): string => {
  switch (status) {
    case 'certified_a':
      return 'Grade A';
    case 'certified_b':
      return 'Grade B';
    case 'certified_c':
      return 'Grade C';
    case 'pending_review':
      return 'Pending';
    default:
      return '';
  }
};

const formatLastActivity = (updatedAt: string): string => {
  const date = new Date(updatedAt);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) {
    return 'Today';
  } else if (diffDays === 1) {
    return 'Yesterday';
  } else if (diffDays < 7) {
    return `${diffDays}d ago`;
  } else {
    return date.toLocaleDateString();
  }
};

const SupplierCard: React.FC<SupplierCardProps> = ({ supplier, onClick, isDragging }) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging: isSortableDragging,
  } = useSortable({ id: supplier.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isSortableDragging || isDragging ? 0.5 : 1,
  };

  const certificationLabel = getCertificationLabel(supplier.certification_status);
  const certificationColor = getCertificationColor(supplier.certification_status);
  const isCertified = supplier.certification_status.startsWith('certified_');

  const handleClick = () => {
    if (!isSortableDragging && onClick) {
      onClick(supplier);
    }
  };

  return (
    <Card
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      sx={{
        mb: 1,
        cursor: 'grab',
        '&:hover': {
          boxShadow: 3,
        },
        '&:active': {
          cursor: 'grabbing',
        },
        bgcolor: 'background.paper',
        borderLeft: 4,
        borderLeftColor: isCertified ? certificationColor : 'grey.300',
      }}
      onClick={handleClick}
    >
      <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
        {/* Supplier Name */}
        <Box display="flex" alignItems="flex-start" gap={0.5} mb={0.5}>
          <BusinessIcon fontSize="small" color="action" sx={{ mt: 0.3 }} />
          <Typography
            variant="subtitle2"
            fontWeight="bold"
            sx={{
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              flex: 1,
            }}
          >
            {supplier.name}
          </Typography>
        </Box>

        {/* Supplier Code */}
        {supplier.code && (
          <Typography
            variant="caption"
            color="text.secondary"
            sx={{
              display: 'block',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              mb: 0.5,
              fontFamily: 'monospace',
            }}
          >
            {supplier.code}
          </Typography>
        )}

        {/* Contact Name */}
        {supplier.contact_name && (
          <Box display="flex" alignItems="center" gap={0.5} mb={0.5}>
            <PersonIcon fontSize="small" color="action" sx={{ fontSize: 14 }} />
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
                fontSize: '0.75rem',
              }}
            >
              {supplier.contact_name}
            </Typography>
          </Box>
        )}

        {/* Country */}
        <Box display="flex" alignItems="center" gap={0.5} mb={0.5}>
          <PublicIcon fontSize="small" color="action" sx={{ fontSize: 14 }} />
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{ fontSize: '0.75rem' }}
          >
            {supplier.country}
          </Typography>
        </Box>

        {/* Bottom row: Product count + Certification badge */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mt={1} gap={0.5}>
          <Tooltip title={`${supplier.product_count} products from this supplier`}>
            <Chip
              icon={<InventoryIcon sx={{ fontSize: 14 }} />}
              label={supplier.product_count}
              size="small"
              variant="outlined"
              sx={{
                fontSize: '0.65rem',
                height: 20,
                '& .MuiChip-icon': {
                  marginLeft: '4px',
                },
              }}
            />
          </Tooltip>

          {certificationLabel && (
            <Tooltip title={`Certification: ${certificationLabel}`}>
              <Chip
                icon={<VerifiedIcon sx={{ fontSize: 14 }} />}
                label={certificationLabel}
                size="small"
                sx={{
                  bgcolor: certificationColor,
                  color: 'white',
                  fontSize: '0.65rem',
                  height: 20,
                  '& .MuiChip-icon': {
                    marginLeft: '4px',
                    color: 'white',
                  },
                }}
              />
            </Tooltip>
          )}
        </Box>

        {/* Last activity */}
        <Typography
          variant="caption"
          color="text.disabled"
          sx={{ display: 'block', mt: 0.5, textAlign: 'right' }}
        >
          {formatLastActivity(supplier.updated_at)}
        </Typography>
      </CardContent>
    </Card>
  );
};

export default React.memo(SupplierCard);
