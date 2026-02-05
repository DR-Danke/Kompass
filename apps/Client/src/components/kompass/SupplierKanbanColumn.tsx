import React from 'react';
import { useDroppable } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { Box, Typography, Paper, Chip } from '@mui/material';
import type { SupplierWithProductCount, SupplierPipelineStatus } from '@/types/kompass';
import SupplierCard from './SupplierCard';

interface SupplierKanbanColumnProps {
  status: SupplierPipelineStatus;
  title: string;
  suppliers: SupplierWithProductCount[];
  onSupplierClick: (supplier: SupplierWithProductCount) => void;
  color: string;
}

const SupplierKanbanColumn: React.FC<SupplierKanbanColumnProps> = ({
  status,
  title,
  suppliers,
  onSupplierClick,
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
          label={suppliers.length}
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
          items={suppliers.map(s => s.id)}
          strategy={verticalListSortingStrategy}
        >
          {suppliers.length === 0 ? (
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
                No suppliers
              </Typography>
            </Box>
          ) : (
            suppliers.map(supplier => (
              <SupplierCard
                key={supplier.id}
                supplier={supplier}
                onClick={onSupplierClick}
              />
            ))
          )}
        </SortableContext>
      </Box>
    </Paper>
  );
};

export default React.memo(SupplierKanbanColumn);
