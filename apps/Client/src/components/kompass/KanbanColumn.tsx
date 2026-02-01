import React from 'react';
import { useDroppable } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { Box, Typography, Paper, Chip } from '@mui/material';
import type { ClientResponse, ClientStatus } from '@/types/kompass';
import ClientCard from './ClientCard';

interface KanbanColumnProps {
  status: ClientStatus;
  title: string;
  clients: ClientResponse[];
  onClientClick: (client: ClientResponse) => void;
  color: string;
}

const KanbanColumn: React.FC<KanbanColumnProps> = ({
  status,
  title,
  clients,
  onClientClick,
  color,
}) => {
  const { setNodeRef, isOver } = useDroppable({
    id: status,
  });

  return (
    <Paper
      sx={{
        width: 280,
        minWidth: 280,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: color,
        borderRadius: 2,
        overflow: 'hidden',
      }}
    >
      {/* Column Header */}
      <Box
        sx={{
          p: 1.5,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: 1,
          borderColor: 'divider',
          bgcolor: 'background.paper',
        }}
      >
        <Typography variant="subtitle1" fontWeight="bold">
          {title}
        </Typography>
        <Chip
          label={clients.length}
          size="small"
          sx={{
            bgcolor: 'grey.200',
            fontWeight: 'bold',
            minWidth: 32,
          }}
        />
      </Box>

      {/* Cards Container */}
      <Box
        ref={setNodeRef}
        sx={{
          flex: 1,
          p: 1,
          overflow: 'auto',
          minHeight: 200,
          transition: 'background-color 0.2s ease',
          bgcolor: isOver ? 'action.hover' : 'transparent',
        }}
      >
        <SortableContext
          items={clients.map(c => c.id)}
          strategy={verticalListSortingStrategy}
        >
          {clients.length === 0 ? (
            <Box
              sx={{
                height: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                minHeight: 100,
              }}
            >
              <Typography variant="body2" color="text.secondary" textAlign="center">
                No clients
              </Typography>
            </Box>
          ) : (
            clients.map(client => (
              <ClientCard
                key={client.id}
                client={client}
                onClick={onClientClick}
              />
            ))
          )}
        </SortableContext>
      </Box>
    </Paper>
  );
};

export default React.memo(KanbanColumn);
