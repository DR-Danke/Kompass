import React, { useState } from 'react';
import {
  DndContext,
  DragOverlay,
  closestCorners,
  PointerSensor,
  useSensor,
  useSensors,
  DragStartEvent,
  DragEndEvent,
  DragOverEvent,
} from '@dnd-kit/core';
import { Box, CircularProgress, Backdrop } from '@mui/material';
import type { ClientResponse, ClientStatus, PipelineResponse } from '@/types/kompass';
import KanbanColumn from './KanbanColumn';
import ClientCard from './ClientCard';

interface ClientKanbanBoardProps {
  pipeline: PipelineResponse;
  onClientClick: (client: ClientResponse) => void;
  onStatusChange: (clientId: string, newStatus: ClientStatus) => Promise<void>;
  isUpdating?: boolean;
}

interface ColumnConfig {
  status: ClientStatus;
  title: string;
  color: string;
}

const COLUMNS: ColumnConfig[] = [
  { status: 'lead', title: 'Lead', color: '#f5f5f5' },
  { status: 'qualified', title: 'Qualified', color: '#e3f2fd' },
  { status: 'quoting', title: 'Quoting', color: '#fff8e1' },
  { status: 'negotiating', title: 'Negotiating', color: '#fff3e0' },
  { status: 'won', title: 'Won', color: '#e8f5e9' },
  { status: 'lost', title: 'Lost', color: '#ffebee' },
];

const ClientKanbanBoard: React.FC<ClientKanbanBoardProps> = ({
  pipeline,
  onClientClick,
  onStatusChange,
  isUpdating = false,
}) => {
  const [activeClient, setActiveClient] = useState<ClientResponse | null>(null);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8, // 8px of movement required before drag starts
      },
    })
  );

  const findClientById = (id: string): ClientResponse | null => {
    const allClients = [
      ...pipeline.lead,
      ...pipeline.qualified,
      ...pipeline.quoting,
      ...pipeline.negotiating,
      ...pipeline.won,
      ...pipeline.lost,
    ];
    return allClients.find(c => c.id === id) || null;
  };

  const handleDragStart = (event: DragStartEvent) => {
    const { active } = event;
    const client = findClientById(active.id as string);
    setActiveClient(client);
  };

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveClient(null);

    if (!over) return;

    const clientId = active.id as string;
    const client = findClientById(clientId);
    if (!client) return;

    // Determine target column - over.id could be a column or another card
    let targetStatus: ClientStatus;

    // Check if dropped over a column directly
    if (COLUMNS.some(col => col.status === over.id)) {
      targetStatus = over.id as ClientStatus;
    } else {
      // Dropped over another card - find which column the card is in
      const targetClient = findClientById(over.id as string);
      if (targetClient) {
        targetStatus = targetClient.status;
      } else {
        return;
      }
    }

    // Only update if status actually changed
    if (client.status !== targetStatus) {
      await onStatusChange(clientId, targetStatus);
    }
  };

  const handleDragOver = (_event: DragOverEvent) => {
    // Can be used for visual feedback during drag
  };

  return (
    <Box sx={{ position: 'relative' }}>
      {/* Loading overlay */}
      <Backdrop
        open={isUpdating}
        sx={{
          position: 'absolute',
          zIndex: 1,
          bgcolor: 'rgba(255, 255, 255, 0.7)',
        }}
      >
        <CircularProgress />
      </Backdrop>

      <DndContext
        sensors={sensors}
        collisionDetection={closestCorners}
        onDragStart={handleDragStart}
        onDragEnd={handleDragEnd}
        onDragOver={handleDragOver}
      >
        <Box
          sx={{
            display: 'flex',
            gap: 2,
            overflowX: 'auto',
            pb: 2,
            height: 'calc(100vh - 250px)',
            minHeight: 400,
          }}
        >
          {COLUMNS.map(column => (
            <KanbanColumn
              key={column.status}
              status={column.status}
              title={column.title}
              clients={pipeline[column.status]}
              onClientClick={onClientClick}
              color={column.color}
            />
          ))}
        </Box>

        <DragOverlay>
          {activeClient ? (
            <Box sx={{ width: 280 }}>
              <ClientCard client={activeClient} isDragging />
            </Box>
          ) : null}
        </DragOverlay>
      </DndContext>
    </Box>
  );
};

export default ClientKanbanBoard;
