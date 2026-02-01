import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Typography,
  Box,
  CircularProgress,
  Tooltip,
} from '@mui/material';
import VisibilityIcon from '@mui/icons-material/Visibility';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import type { ClientResponse, ClientStatus } from '@/types/kompass';

interface ClientListViewProps {
  clients: ClientResponse[];
  isLoading?: boolean;
  onClientClick: (client: ClientResponse) => void;
  onEditClick: (client: ClientResponse) => void;
  onDeleteClick: (client: ClientResponse) => void;
}

const getStatusColor = (status: ClientStatus): 'default' | 'primary' | 'warning' | 'success' | 'error' | 'info' => {
  switch (status) {
    case 'lead':
      return 'default';
    case 'qualified':
      return 'info';
    case 'quoting':
      return 'warning';
    case 'negotiating':
      return 'warning';
    case 'won':
      return 'success';
    case 'lost':
      return 'error';
    default:
      return 'default';
  }
};

const getStatusLabel = (status: ClientStatus): string => {
  const labels: Record<ClientStatus, string> = {
    lead: 'Lead',
    qualified: 'Qualified',
    quoting: 'Quoting',
    negotiating: 'Negotiating',
    won: 'Won',
    lost: 'Lost',
  };
  return labels[status] || status;
};

const getSourceLabel = (source: string | null): string => {
  if (!source) return '-';
  const labels: Record<string, string> = {
    website: 'Website',
    referral: 'Referral',
    cold_call: 'Cold Call',
    trade_show: 'Trade Show',
    linkedin: 'LinkedIn',
    other: 'Other',
  };
  return labels[source] || source;
};

const formatDeadline = (deadline: string | null): { text: string; color?: 'error' | 'warning' | 'success' } => {
  if (!deadline) return { text: '-' };

  const deadlineDate = new Date(deadline);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  deadlineDate.setHours(0, 0, 0, 0);

  const diffDays = Math.ceil((deadlineDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
  const formattedDate = deadlineDate.toLocaleDateString();

  if (diffDays < 0) {
    return { text: `${formattedDate} (overdue)`, color: 'error' };
  } else if (diffDays <= 7) {
    return { text: formattedDate, color: 'warning' };
  } else if (diffDays <= 30) {
    return { text: formattedDate, color: 'success' };
  }

  return { text: formattedDate };
};

const ClientListView: React.FC<ClientListViewProps> = ({
  clients,
  isLoading = false,
  onClientClick,
  onEditClick,
  onDeleteClick,
}) => {
  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" py={4}>
        <CircularProgress />
      </Box>
    );
  }

  if (clients.length === 0) {
    return (
      <Box display="flex" justifyContent="center" py={4}>
        <Typography color="text.secondary">
          No clients found. Click "Add Client" to create one.
        </Typography>
      </Box>
    );
  }

  return (
    <TableContainer component={Paper}>
      <Table size="medium">
        <TableHead>
          <TableRow>
            <TableCell>Company</TableCell>
            <TableCell>Contact</TableCell>
            <TableCell>Email</TableCell>
            <TableCell>Phone</TableCell>
            <TableCell>Niche</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Deadline</TableCell>
            <TableCell>Source</TableCell>
            <TableCell align="right">Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {clients.map((client) => {
            const deadlineInfo = formatDeadline(client.project_deadline);

            return (
              <TableRow
                key={client.id}
                hover
                sx={{ cursor: 'pointer' }}
                onClick={() => onClientClick(client)}
              >
                <TableCell>
                  <Typography
                    variant="body2"
                    fontWeight="medium"
                    sx={{
                      maxWidth: 200,
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {client.company_name}
                  </Typography>
                  {client.project_name && (
                    <Typography variant="caption" color="text.secondary" display="block">
                      {client.project_name}
                    </Typography>
                  )}
                </TableCell>
                <TableCell>
                  {client.contact_name || '-'}
                </TableCell>
                <TableCell>
                  <Typography
                    variant="body2"
                    sx={{
                      maxWidth: 180,
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {client.email || '-'}
                  </Typography>
                </TableCell>
                <TableCell>{client.phone || '-'}</TableCell>
                <TableCell>
                  {client.niche_name ? (
                    <Chip label={client.niche_name} size="small" variant="outlined" />
                  ) : (
                    '-'
                  )}
                </TableCell>
                <TableCell>
                  <Chip
                    label={getStatusLabel(client.status)}
                    color={getStatusColor(client.status)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Typography
                    variant="body2"
                    color={deadlineInfo.color ? `${deadlineInfo.color}.main` : 'text.primary'}
                  >
                    {deadlineInfo.text}
                  </Typography>
                </TableCell>
                <TableCell>{getSourceLabel(client.source)}</TableCell>
                <TableCell align="right">
                  <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'flex-end' }}>
                    <Tooltip title="View details">
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          onClientClick(client);
                        }}
                      >
                        <VisibilityIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Edit">
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          onEditClick(client);
                        }}
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton
                        size="small"
                        color="error"
                        onClick={(e) => {
                          e.stopPropagation();
                          onDeleteClick(client);
                        }}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default ClientListView;
