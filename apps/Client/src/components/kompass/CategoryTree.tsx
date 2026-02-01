/**
 * CategoryTree Component
 * Recursive tree component for displaying and managing categories
 * Supports expand/collapse, drag-and-drop reparenting, and CRUD actions
 */

import React, { useState, useCallback } from 'react';
import {
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  IconButton,
  Collapse,
  Typography,
  Tooltip,
  Chip,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import FolderIcon from '@mui/icons-material/Folder';
import FolderOpenIcon from '@mui/icons-material/FolderOpen';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import DragIndicatorIcon from '@mui/icons-material/DragIndicator';
import type { CategoryTreeNode } from '@/types/kompass';

interface CategoryTreeProps {
  categories: CategoryTreeNode[];
  onAddChild: (parentId: string, parentName: string) => void;
  onEdit: (category: CategoryTreeNode) => void;
  onDelete: (category: CategoryTreeNode) => void;
  onMove: (categoryId: string, newParentId: string | null) => void;
}

interface TreeNodeProps {
  node: CategoryTreeNode;
  depth: number;
  expandedNodes: Set<string>;
  onToggle: (id: string) => void;
  onAddChild: (parentId: string, parentName: string) => void;
  onEdit: (category: CategoryTreeNode) => void;
  onDelete: (category: CategoryTreeNode) => void;
  onMove: (categoryId: string, newParentId: string | null) => void;
  draggedId: string | null;
  setDraggedId: (id: string | null) => void;
  dropTargetId: string | null;
  setDropTargetId: (id: string | null) => void;
}

const TreeNode: React.FC<TreeNodeProps> = ({
  node,
  depth,
  expandedNodes,
  onToggle,
  onAddChild,
  onEdit,
  onDelete,
  onMove,
  draggedId,
  setDraggedId,
  dropTargetId,
  setDropTargetId,
}) => {
  const isExpanded = expandedNodes.has(node.id);
  const hasChildren = node.children && node.children.length > 0;
  const isDragging = draggedId === node.id;
  const isDropTarget = dropTargetId === node.id && draggedId !== node.id;

  const handleDragStart = (e: React.DragEvent) => {
    e.stopPropagation();
    setDraggedId(node.id);
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', node.id);
  };

  const handleDragEnd = () => {
    setDraggedId(null);
    setDropTargetId(null);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (draggedId && draggedId !== node.id) {
      setDropTargetId(node.id);
    }
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    if (dropTargetId === node.id) {
      setDropTargetId(null);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    const droppedId = e.dataTransfer.getData('text/plain');
    if (droppedId && droppedId !== node.id) {
      onMove(droppedId, node.id);
    }
    setDraggedId(null);
    setDropTargetId(null);
  };

  const handleToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    onToggle(node.id);
  };

  return (
    <>
      <ListItem
        disablePadding
        draggable
        onDragStart={handleDragStart}
        onDragEnd={handleDragEnd}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        sx={{
          opacity: isDragging ? 0.5 : 1,
          backgroundColor: isDropTarget ? 'action.hover' : 'transparent',
          borderLeft: isDropTarget ? '3px solid primary.main' : '3px solid transparent',
          transition: 'background-color 0.2s, border-color 0.2s',
        }}
      >
        <ListItemButton
          sx={{
            pl: 2 + depth * 2,
            pr: 1,
            '&:hover .action-buttons': {
              opacity: 1,
            },
          }}
        >
          <ListItemIcon sx={{ minWidth: 28, cursor: 'grab' }}>
            <DragIndicatorIcon fontSize="small" sx={{ color: 'text.secondary' }} />
          </ListItemIcon>

          {hasChildren ? (
            <ListItemIcon
              sx={{ minWidth: 28, cursor: 'pointer' }}
              onClick={handleToggle}
            >
              {isExpanded ? (
                <ExpandMoreIcon fontSize="small" />
              ) : (
                <ChevronRightIcon fontSize="small" />
              )}
            </ListItemIcon>
          ) : (
            <ListItemIcon sx={{ minWidth: 28 }} />
          )}

          <ListItemIcon sx={{ minWidth: 32 }}>
            {isExpanded && hasChildren ? (
              <FolderOpenIcon color="primary" fontSize="small" />
            ) : (
              <FolderIcon color={node.is_active ? 'primary' : 'disabled'} fontSize="small" />
            )}
          </ListItemIcon>

          <ListItemText
            primary={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography
                  variant="body2"
                  sx={{
                    fontWeight: hasChildren ? 500 : 400,
                    color: node.is_active ? 'text.primary' : 'text.disabled',
                  }}
                >
                  {node.name}
                </Typography>
                {!node.is_active && (
                  <Chip label="Inactive" size="small" variant="outlined" color="default" />
                )}
              </Box>
            }
            secondary={node.description}
            secondaryTypographyProps={{
              noWrap: true,
              sx: { maxWidth: 200 },
            }}
          />

          <Box
            className="action-buttons"
            sx={{
              display: 'flex',
              gap: 0.5,
              opacity: 0,
              transition: 'opacity 0.2s',
            }}
          >
            <Tooltip title="Add child category">
              <IconButton
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  onAddChild(node.id, node.name);
                }}
              >
                <AddIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            <Tooltip title="Edit category">
              <IconButton
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  onEdit(node);
                }}
              >
                <EditIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            <Tooltip title="Delete category">
              <IconButton
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(node);
                }}
              >
                <DeleteIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
        </ListItemButton>
      </ListItem>

      {hasChildren && (
        <Collapse in={isExpanded} timeout="auto" unmountOnExit>
          <List disablePadding>
            {node.children.map((child) => (
              <TreeNode
                key={child.id}
                node={child}
                depth={depth + 1}
                expandedNodes={expandedNodes}
                onToggle={onToggle}
                onAddChild={onAddChild}
                onEdit={onEdit}
                onDelete={onDelete}
                onMove={onMove}
                draggedId={draggedId}
                setDraggedId={setDraggedId}
                dropTargetId={dropTargetId}
                setDropTargetId={setDropTargetId}
              />
            ))}
          </List>
        </Collapse>
      )}
    </>
  );
};

export const CategoryTree: React.FC<CategoryTreeProps> = ({
  categories,
  onAddChild,
  onEdit,
  onDelete,
  onMove,
}) => {
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());
  const [draggedId, setDraggedId] = useState<string | null>(null);
  const [dropTargetId, setDropTargetId] = useState<string | null>(null);

  const handleToggle = useCallback((id: string) => {
    setExpandedNodes((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }, []);

  const handleRootDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const droppedId = e.dataTransfer.getData('text/plain');
    if (droppedId) {
      onMove(droppedId, null);
    }
    setDraggedId(null);
    setDropTargetId(null);
  };

  const handleRootDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    if (draggedId) {
      setDropTargetId('root');
    }
  };

  const handleRootDragLeave = () => {
    if (dropTargetId === 'root') {
      setDropTargetId(null);
    }
  };

  if (categories.length === 0) {
    return (
      <Box
        sx={{
          p: 4,
          textAlign: 'center',
          color: 'text.secondary',
        }}
      >
        <Typography variant="body1">No categories yet</Typography>
        <Typography variant="body2" sx={{ mt: 1 }}>
          Click "Add Root Category" to create your first category
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <List
        sx={{
          '& .MuiListItem-root': {
            borderRadius: 1,
          },
        }}
      >
        {categories.map((category) => (
          <TreeNode
            key={category.id}
            node={category}
            depth={0}
            expandedNodes={expandedNodes}
            onToggle={handleToggle}
            onAddChild={onAddChild}
            onEdit={onEdit}
            onDelete={onDelete}
            onMove={onMove}
            draggedId={draggedId}
            setDraggedId={setDraggedId}
            dropTargetId={dropTargetId}
            setDropTargetId={setDropTargetId}
          />
        ))}
      </List>

      <Box
        onDrop={handleRootDrop}
        onDragOver={handleRootDragOver}
        onDragLeave={handleRootDragLeave}
        sx={{
          p: 2,
          mt: 1,
          border: '2px dashed',
          borderColor: dropTargetId === 'root' ? 'primary.main' : 'divider',
          borderRadius: 1,
          textAlign: 'center',
          color: dropTargetId === 'root' ? 'primary.main' : 'text.secondary',
          transition: 'border-color 0.2s, color 0.2s',
        }}
      >
        <Typography variant="body2">
          Drop here to move to root level
        </Typography>
      </Box>
    </Box>
  );
};
