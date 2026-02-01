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
  Tooltip,
} from '@mui/material';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import DeleteIcon from '@mui/icons-material/Delete';
import LinkIcon from '@mui/icons-material/Link';
import CollectionsIcon from '@mui/icons-material/Collections';
import PortfolioStatusBadge from './PortfolioStatusBadge';
import type { PortfolioResponse } from '@/types/kompass';

interface PortfolioCardProps {
  portfolio: PortfolioResponse;
  coverImageUrl?: string | null;
  onOpen?: (portfolio: PortfolioResponse) => void;
  onDuplicate?: (portfolio: PortfolioResponse) => void;
  onDelete?: (portfolio: PortfolioResponse) => void;
  onCopyShareLink?: (portfolio: PortfolioResponse) => void;
}

const PortfolioCard: React.FC<PortfolioCardProps> = ({
  portfolio,
  coverImageUrl,
  onOpen,
  onDuplicate,
  onDelete,
  onCopyShareLink,
}) => {
  return (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        transition: 'box-shadow 0.2s',
        '&:hover': {
          boxShadow: 4,
        },
      }}
    >
      {coverImageUrl ? (
        <CardMedia
          component="img"
          height="140"
          image={coverImageUrl}
          alt={portfolio.name}
          sx={{ objectFit: 'cover' }}
        />
      ) : (
        <Box
          sx={{
            height: 140,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: 'grey.200',
          }}
        >
          <CollectionsIcon sx={{ fontSize: 48, color: 'grey.400' }} />
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
            {portfolio.name}
          </Typography>
          <PortfolioStatusBadge isActive={portfolio.is_active} />
        </Box>

        {portfolio.niche_name && (
          <Chip
            label={portfolio.niche_name}
            size="small"
            variant="outlined"
            sx={{ mb: 1 }}
          />
        )}

        <Typography variant="body2" color="text.secondary">
          {portfolio.item_count} {portfolio.item_count === 1 ? 'product' : 'products'}
        </Typography>

        {portfolio.description && (
          <Typography
            variant="caption"
            color="text.secondary"
            sx={{
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden',
              mt: 0.5,
            }}
          >
            {portfolio.description}
          </Typography>
        )}
      </CardContent>

      <CardActions sx={{ justifyContent: 'flex-end', pt: 0 }}>
        <Tooltip title="Open">
          <IconButton
            size="small"
            onClick={() => onOpen?.(portfolio)}
            color="primary"
          >
            <OpenInNewIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        <Tooltip title="Copy Share Link">
          <IconButton
            size="small"
            onClick={() => onCopyShareLink?.(portfolio)}
            color="default"
          >
            <LinkIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        <Tooltip title="Duplicate">
          <IconButton
            size="small"
            onClick={() => onDuplicate?.(portfolio)}
            color="default"
          >
            <ContentCopyIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        <Tooltip title="Delete">
          <IconButton
            size="small"
            onClick={() => onDelete?.(portfolio)}
            color="error"
          >
            <DeleteIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </CardActions>
    </Card>
  );
};

export default PortfolioCard;
