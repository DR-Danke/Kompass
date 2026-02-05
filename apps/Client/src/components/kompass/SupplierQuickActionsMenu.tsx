import React, { useState } from 'react';
import {
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Divider,
  CircularProgress,
} from '@mui/material';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import AssignmentIcon from '@mui/icons-material/Assignment';
import ArrowRightIcon from '@mui/icons-material/ArrowRight';
import type { SupplierResponse, SupplierPipelineStatus } from '@/types/kompass';

interface SupplierQuickActionsMenuProps {
  supplier: SupplierResponse;
  onEdit: (supplier: SupplierResponse) => void;
  onDelete: (supplier: SupplierResponse) => void;
  onUploadAudit: (supplier: SupplierResponse) => void;
  onViewCertification: (supplier: SupplierResponse) => void;
  onChangePipelineStatus: (supplier: SupplierResponse, status: SupplierPipelineStatus) => void;
  isUpdating?: boolean;
}

const PIPELINE_STATUS_OPTIONS: { value: SupplierPipelineStatus; label: string }[] = [
  { value: 'contacted', label: 'Contacted' },
  { value: 'potential', label: 'Potential' },
  { value: 'quoted', label: 'Quoted' },
  { value: 'certified', label: 'Certified' },
  { value: 'active', label: 'Active' },
  { value: 'inactive', label: 'Inactive' },
];

const SupplierQuickActionsMenu: React.FC<SupplierQuickActionsMenuProps> = ({
  supplier,
  onEdit,
  onDelete,
  onUploadAudit,
  onViewCertification,
  onChangePipelineStatus,
  isUpdating = false,
}) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [statusMenuAnchor, setStatusMenuAnchor] = useState<null | HTMLElement>(null);

  const open = Boolean(anchorEl);
  const statusMenuOpen = Boolean(statusMenuAnchor);

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
    setStatusMenuAnchor(null);
  };

  const handleStatusMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    event.stopPropagation();
    setStatusMenuAnchor(event.currentTarget);
  };

  const handleStatusMenuClose = () => {
    setStatusMenuAnchor(null);
  };

  const handleEdit = () => {
    handleClose();
    onEdit(supplier);
  };

  const handleDelete = () => {
    handleClose();
    onDelete(supplier);
  };

  const handleUploadAudit = () => {
    handleClose();
    onUploadAudit(supplier);
  };

  const handleViewCertification = () => {
    handleClose();
    onViewCertification(supplier);
  };

  const handlePipelineStatusChange = (status: SupplierPipelineStatus) => {
    handleClose();
    onChangePipelineStatus(supplier, status);
  };

  const hasAudits = !!supplier.latest_audit_id;

  return (
    <>
      <IconButton
        aria-label="more actions"
        aria-controls={open ? 'supplier-actions-menu' : undefined}
        aria-haspopup="true"
        aria-expanded={open ? 'true' : undefined}
        onClick={handleClick}
        size="small"
        disabled={isUpdating}
      >
        {isUpdating ? <CircularProgress size={20} /> : <MoreVertIcon fontSize="small" />}
      </IconButton>

      <Menu
        id="supplier-actions-menu"
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <MenuItem onClick={handleEdit}>
          <ListItemIcon>
            <EditIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>View/Edit Supplier</ListItemText>
        </MenuItem>

        <MenuItem onClick={handleUploadAudit}>
          <ListItemIcon>
            <UploadFileIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Upload Audit</ListItemText>
        </MenuItem>

        <MenuItem onClick={handleViewCertification} disabled={!hasAudits}>
          <ListItemIcon>
            <AssignmentIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>View Certification Summary</ListItemText>
        </MenuItem>

        <MenuItem onClick={handleStatusMenuOpen}>
          <ListItemIcon>
            <ArrowRightIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Change Pipeline Status</ListItemText>
        </MenuItem>

        <Divider />

        <MenuItem onClick={handleDelete} sx={{ color: 'error.main' }}>
          <ListItemIcon>
            <DeleteIcon fontSize="small" color="error" />
          </ListItemIcon>
          <ListItemText>Delete Supplier</ListItemText>
        </MenuItem>
      </Menu>

      {/* Pipeline Status Submenu */}
      <Menu
        id="pipeline-status-menu"
        anchorEl={statusMenuAnchor}
        open={statusMenuOpen}
        onClose={handleStatusMenuClose}
        transformOrigin={{ horizontal: 'left', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'top' }}
      >
        {PIPELINE_STATUS_OPTIONS.map((option) => (
          <MenuItem
            key={option.value}
            onClick={() => handlePipelineStatusChange(option.value)}
            selected={supplier.pipeline_status === option.value}
          >
            {option.label}
          </MenuItem>
        ))}
      </Menu>
    </>
  );
};

export default SupplierQuickActionsMenu;
