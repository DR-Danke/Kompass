import React, { useState, useEffect, useCallback } from 'react';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import {
  Box,
  Typography,
  Paper,
  CircularProgress,
} from '@mui/material';
import InventoryIcon from '@mui/icons-material/Inventory';
import PortfolioItemCard from './PortfolioItemCard';
import { productService } from '@/services/kompassService';
import type { PortfolioItemResponse, ProductResponse } from '@/types/kompass';

interface PortfolioBuilderProps {
  items: PortfolioItemResponse[];
  isLoading?: boolean;
  onReorder: (productIds: string[]) => void;
  onRemoveItem: (itemId: string) => void;
  onUpdateNotes: (itemId: string, notes: string) => void;
}

const PortfolioBuilder: React.FC<PortfolioBuilderProps> = ({
  items,
  isLoading = false,
  onReorder,
  onRemoveItem,
  onUpdateNotes,
}) => {
  const [products, setProducts] = useState<Map<string, ProductResponse>>(new Map());
  const [loadingProducts, setLoadingProducts] = useState(false);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  // Fetch product details for items
  useEffect(() => {
    const fetchProductDetails = async () => {
      const productIds = items
        .map(item => item.product_id)
        .filter(id => !products.has(id));

      if (productIds.length === 0) return;

      setLoadingProducts(true);
      try {
        const fetchPromises = productIds.map(async (id) => {
          try {
            const product = await productService.get(id);
            return { id, product };
          } catch (err) {
            console.error(`ERROR [PortfolioBuilder]: Failed to fetch product ${id}:`, err);
            return { id, product: null };
          }
        });

        const results = await Promise.all(fetchPromises);
        setProducts(prev => {
          const newMap = new Map(prev);
          results.forEach(({ id, product }) => {
            if (product) {
              newMap.set(id, product);
            }
          });
          return newMap;
        });
      } finally {
        setLoadingProducts(false);
      }
    };

    fetchProductDetails();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [items]);

  const handleDragEnd = useCallback((event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      const oldIndex = items.findIndex(item => item.product_id === active.id);
      const newIndex = items.findIndex(item => item.product_id === over.id);

      if (oldIndex !== -1 && newIndex !== -1) {
        const newItems = arrayMove(items, oldIndex, newIndex);
        const productIds = newItems.map(item => item.product_id);
        onReorder(productIds);
      }
    }
  }, [items, onReorder]);

  if (isLoading) {
    return (
      <Box
        sx={{
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  if (items.length === 0) {
    return (
      <Box
        sx={{
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'text.secondary',
        }}
      >
        <InventoryIcon sx={{ fontSize: 64, mb: 2, color: 'grey.300' }} />
        <Typography variant="h6" color="text.secondary" gutterBottom>
          No products in portfolio
        </Typography>
        <Typography variant="body2" color="text.secondary" textAlign="center">
          Click on products in the catalog to add them to your portfolio
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2, px: 1 }}>
        <Typography variant="h6">
          Portfolio Items
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {items.length} {items.length === 1 ? 'product' : 'products'}
        </Typography>
      </Box>

      <Paper
        variant="outlined"
        sx={{
          flex: 1,
          overflow: 'auto',
          p: 1,
          backgroundColor: 'grey.50',
          minHeight: 0,
        }}
      >
        {loadingProducts && (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
            <CircularProgress size={20} />
          </Box>
        )}

        <DndContext
          sensors={sensors}
          collisionDetection={closestCenter}
          onDragEnd={handleDragEnd}
        >
          <SortableContext
            items={items.map(item => item.product_id)}
            strategy={verticalListSortingStrategy}
          >
            {items.map((item) => (
              <PortfolioItemCard
                key={item.id}
                item={item}
                product={products.get(item.product_id)}
                onRemove={onRemoveItem}
                onNotesChange={onUpdateNotes}
              />
            ))}
          </SortableContext>
        </DndContext>
      </Paper>
    </Box>
  );
};

export default PortfolioBuilder;
