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
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import PersonIcon from '@mui/icons-material/Person';
import BusinessIcon from '@mui/icons-material/Business';
import type { ClientResponse } from '@/types/kompass';

interface ClientCardProps {
  client: ClientResponse;
  onClick?: (client: ClientResponse) => void;
  isDragging?: boolean;
}

const getNicheColor = (nicheName: string | null): string => {
  if (!nicheName) return '#9e9e9e';

  // Generate a consistent color based on niche name hash
  let hash = 0;
  for (let i = 0; i < nicheName.length; i++) {
    hash = nicheName.charCodeAt(i) + ((hash << 5) - hash);
  }

  const colors = [
    '#1976d2', // blue
    '#388e3c', // green
    '#f57c00', // orange
    '#7b1fa2', // purple
    '#c2185b', // pink
    '#00796b', // teal
    '#5d4037', // brown
    '#455a64', // blue-grey
  ];

  return colors[Math.abs(hash) % colors.length];
};

const getDeadlineInfo = (deadline: string | null): { label: string; color: 'default' | 'warning' | 'error' | 'success' } => {
  if (!deadline) {
    return { label: 'No deadline', color: 'default' };
  }

  const deadlineDate = new Date(deadline);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  deadlineDate.setHours(0, 0, 0, 0);

  const diffDays = Math.ceil((deadlineDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));

  if (diffDays < 0) {
    return { label: `${Math.abs(diffDays)}d overdue`, color: 'error' };
  } else if (diffDays === 0) {
    return { label: 'Due today', color: 'error' };
  } else if (diffDays <= 7) {
    return { label: `${diffDays}d left`, color: 'warning' };
  } else if (diffDays <= 30) {
    return { label: `${diffDays}d left`, color: 'success' };
  } else {
    return { label: new Date(deadline).toLocaleDateString(), color: 'default' };
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

const ClientCard: React.FC<ClientCardProps> = ({ client, onClick, isDragging }) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging: isSortableDragging,
  } = useSortable({ id: client.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isSortableDragging || isDragging ? 0.5 : 1,
  };

  const deadlineInfo = getDeadlineInfo(client.project_deadline);
  const nicheColor = getNicheColor(client.niche_name);

  const handleClick = () => {
    // Only trigger click if not dragging
    if (!isSortableDragging && onClick) {
      onClick(client);
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
        borderLeftColor: nicheColor,
      }}
      onClick={handleClick}
    >
      <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
        {/* Company Name */}
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
            {client.company_name}
          </Typography>
        </Box>

        {/* Contact Name */}
        {client.contact_name && (
          <Box display="flex" alignItems="center" gap={0.5} mb={0.5}>
            <PersonIcon fontSize="small" color="action" />
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
            >
              {client.contact_name}
            </Typography>
          </Box>
        )}

        {/* Project Name */}
        {client.project_name && (
          <Typography
            variant="caption"
            color="text.secondary"
            sx={{
              display: 'block',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              mb: 0.5,
              fontStyle: 'italic',
            }}
          >
            {client.project_name}
          </Typography>
        )}

        {/* Bottom row: Niche badge + deadline */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mt={1} gap={0.5}>
          {client.niche_name ? (
            <Chip
              label={client.niche_name}
              size="small"
              sx={{
                bgcolor: nicheColor,
                color: 'white',
                fontSize: '0.65rem',
                height: 20,
                maxWidth: 100,
                '& .MuiChip-label': {
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                },
              }}
            />
          ) : (
            <Box />
          )}

          <Tooltip title={`Deadline: ${client.project_deadline || 'Not set'}`}>
            <Chip
              icon={<AccessTimeIcon sx={{ fontSize: 14 }} />}
              label={deadlineInfo.label}
              size="small"
              color={deadlineInfo.color}
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
        </Box>

        {/* Last activity */}
        <Typography
          variant="caption"
          color="text.disabled"
          sx={{ display: 'block', mt: 0.5, textAlign: 'right' }}
        >
          {formatLastActivity(client.updated_at)}
        </Typography>
      </CardContent>
    </Card>
  );
};

export default React.memo(ClientCard);
