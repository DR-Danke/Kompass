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
import type { SupplierWithProductCount, SupplierPipelineStatus, SupplierPipelineResponse } from '@/types/kompass';
import SupplierKanbanColumn from './SupplierKanbanColumn';
import SupplierCard from './SupplierCard';

interface SupplierPipelineKanbanProps {
  pipeline: SupplierPipelineResponse;
  onSupplierClick: (supplier: SupplierWithProductCount) => void;
  onStatusChange: (supplierId: string, newStatus: SupplierPipelineStatus) => Promise<void>;
  isUpdating?: boolean;
}

interface ColumnConfig {
  status: SupplierPipelineStatus;
  title: string;
  color: string;
}

const COLUMNS: ColumnConfig[] = [
  { status: 'contacted', title: 'Contacted', color: '#f5f5f5' },
  { status: 'potential', title: 'Potential', color: '#e3f2fd' },
  { status: 'quoted', title: 'Quoted', color: '#fff8e1' },
  { status: 'certified', title: 'Certified', color: '#e8f5e9' },
  { status: 'active', title: 'Active', color: '#c8e6c9' },
  { status: 'inactive', title: 'Inactive', color: '#ffebee' },
];

const SupplierPipelineKanban: React.FC<SupplierPipelineKanbanProps> = ({
  pipeline,
  onSupplierClick,
  onStatusChange,
  isUpdating = false,
}) => {
  const [activeSupplier, setActiveSupplier] = useState<SupplierWithProductCount | null>(null);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    })
  );

  const findSupplierById = (id: string): SupplierWithProductCount | null => {
    const allSuppliers = [
      ...pipeline.contacted,
      ...pipeline.potential,
      ...pipeline.quoted,
      ...pipeline.certified,
      ...pipeline.active,
      ...pipeline.inactive,
    ];
    return allSuppliers.find(s => s.id === id) || null;
  };

  const handleDragStart = (event: DragStartEvent) => {
    const { active } = event;
    const supplier = findSupplierById(active.id as string);
    setActiveSupplier(supplier);
  };

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveSupplier(null);

    if (!over) return;

    const supplierId = active.id as string;
    const supplier = findSupplierById(supplierId);
    if (!supplier) return;

    let targetStatus: SupplierPipelineStatus;

    if (COLUMNS.some(col => col.status === over.id)) {
      targetStatus = over.id as SupplierPipelineStatus;
    } else {
      const targetSupplier = findSupplierById(over.id as string);
      if (targetSupplier) {
        targetStatus = targetSupplier.pipeline_status;
      } else {
        return;
      }
    }

    if (supplier.pipeline_status !== targetStatus) {
      await onStatusChange(supplierId, targetStatus);
    }
  };

  const handleDragOver = (_event: DragOverEvent) => {
    // Visual feedback during drag
  };

  return (
    <Box sx={{ position: 'relative' }}>
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
            <SupplierKanbanColumn
              key={column.status}
              status={column.status}
              title={column.title}
              suppliers={pipeline[column.status]}
              onSupplierClick={onSupplierClick}
              color={column.color}
            />
          ))}
        </Box>

        <DragOverlay>
          {activeSupplier ? (
            <Box sx={{ width: 280 }}>
              <SupplierCard supplier={activeSupplier} isDragging />
            </Box>
          ) : null}
        </DragOverlay>
      </DndContext>
    </Box>
  );
};

export default SupplierPipelineKanban;
