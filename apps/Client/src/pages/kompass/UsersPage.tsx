import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Button,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Chip,
  TextField,
  MenuItem,
  TablePagination,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  InputAdornment,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import SearchIcon from '@mui/icons-material/Search';
import type { UserAdminResponse, UserRole } from '@/types/kompass';
import { userService } from '@/services/kompassService';
import { useAuth } from '@/hooks/useAuth';
import UserForm from '@/components/kompass/UserForm';
import axios from 'axios';

const ROLE_COLORS: Record<UserRole, 'error' | 'warning' | 'primary' | 'default'> = {
  admin: 'error',
  manager: 'warning',
  user: 'primary',
  viewer: 'default',
};

const UsersPage: React.FC = () => {
  const { user: currentUser } = useAuth();

  // Data state
  const [users, setUsers] = useState<UserAdminResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  // Pagination
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(20);

  // Filters
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState<string>('');
  const [activeFilter, setActiveFilter] = useState<string>('');

  // Dialog state
  const [formOpen, setFormOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<UserAdminResponse | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [userToDelete, setUserToDelete] = useState<UserAdminResponse | null>(null);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      console.log('INFO [UsersPage]: Fetching users');
      const filters: { search?: string; role?: string; is_active?: boolean } = {};
      if (search) filters.search = search;
      if (roleFilter) filters.role = roleFilter;
      if (activeFilter !== '') filters.is_active = activeFilter === 'true';

      const response = await userService.list(page + 1, rowsPerPage, filters);
      setUsers(response.items);
      setTotal(response.total);
      console.log(`INFO [UsersPage]: Fetched ${response.items.length} users`);
    } catch (err) {
      console.log('ERROR [UsersPage]: Failed to fetch users', err);
      setError(err instanceof Error ? err.message : 'Failed to load users');
    } finally {
      setLoading(false);
    }
  }, [page, rowsPerPage, search, roleFilter, activeFilter]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  // Handlers
  const handleAddClick = () => {
    setSelectedUser(null);
    setFormOpen(true);
  };

  const handleEditClick = (user: UserAdminResponse) => {
    setSelectedUser(user);
    setFormOpen(true);
  };

  const handleFormClose = () => {
    setFormOpen(false);
    setSelectedUser(null);
  };

  const handleFormSuccess = () => {
    fetchUsers();
  };

  const handleDeleteClick = (user: UserAdminResponse) => {
    setUserToDelete(user);
    setDeleteError(null);
    setDeleteDialogOpen(true);
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setUserToDelete(null);
    setDeleteError(null);
  };

  const handleDeleteConfirm = async () => {
    if (!userToDelete) return;

    setDeleteLoading(true);
    setDeleteError(null);

    try {
      console.log(`INFO [UsersPage]: Deleting user ${userToDelete.id}`);
      await userService.delete(userToDelete.id);
      setDeleteDialogOpen(false);
      setUserToDelete(null);
      fetchUsers();
    } catch (err) {
      console.log('ERROR [UsersPage]: Failed to delete user', err);
      if (axios.isAxiosError(err) && err.response?.status === 409) {
        setDeleteError(
          err.response.data?.detail ||
            'Cannot delete user because they have associated records. Consider deactivating instead.'
        );
      } else if (axios.isAxiosError(err) && err.response?.data?.detail) {
        setDeleteError(err.response.data.detail);
      } else {
        setDeleteError(err instanceof Error ? err.message : 'Failed to delete user');
      }
    } finally {
      setDeleteLoading(false);
    }
  };

  const handleChangePage = (_: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">User Management</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={handleAddClick}>
          Add User
        </Button>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Filters */}
      <Box display="flex" gap={2} mb={3} flexWrap="wrap">
        <TextField
          size="small"
          placeholder="Search by email or name..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(0);
          }}
          sx={{ minWidth: 280 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />
        <TextField
          size="small"
          select
          label="Role"
          value={roleFilter}
          onChange={(e) => {
            setRoleFilter(e.target.value);
            setPage(0);
          }}
          sx={{ minWidth: 140 }}
        >
          <MenuItem value="">All Roles</MenuItem>
          <MenuItem value="admin">Admin</MenuItem>
          <MenuItem value="manager">Manager</MenuItem>
          <MenuItem value="user">User</MenuItem>
          <MenuItem value="viewer">Viewer</MenuItem>
        </TextField>
        <TextField
          size="small"
          select
          label="Status"
          value={activeFilter}
          onChange={(e) => {
            setActiveFilter(e.target.value);
            setPage(0);
          }}
          sx={{ minWidth: 140 }}
        >
          <MenuItem value="">All</MenuItem>
          <MenuItem value="true">Active</MenuItem>
          <MenuItem value="false">Inactive</MenuItem>
        </TextField>
      </Box>

      {/* Loading State */}
      {loading && (
        <Box display="flex" justifyContent="center" py={4}>
          <CircularProgress />
        </Box>
      )}

      {/* Empty State */}
      {!loading && users.length === 0 && (
        <Box textAlign="center" py={4}>
          <Typography color="text.secondary">
            No users found. {search || roleFilter || activeFilter ? 'Try adjusting your filters.' : 'Click "Add User" to create one.'}
          </Typography>
        </Box>
      )}

      {/* Users Table */}
      {!loading && users.length > 0 && (
        <>
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Email</TableCell>
                  <TableCell>Name</TableCell>
                  <TableCell>Role</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {users.map((u) => {
                  const isSelf = currentUser?.id === u.id;
                  const fullName = [u.first_name, u.last_name].filter(Boolean).join(' ') || '-';

                  return (
                    <TableRow key={u.id} hover>
                      <TableCell>{u.email}</TableCell>
                      <TableCell>{fullName}</TableCell>
                      <TableCell>
                        <Chip
                          label={u.role.charAt(0).toUpperCase() + u.role.slice(1)}
                          size="small"
                          color={ROLE_COLORS[u.role]}
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={u.is_active ? 'Active' : 'Inactive'}
                          size="small"
                          color={u.is_active ? 'success' : 'default'}
                          variant={u.is_active ? 'filled' : 'outlined'}
                        />
                      </TableCell>
                      <TableCell>{formatDate(u.created_at)}</TableCell>
                      <TableCell align="right">
                        <IconButton
                          size="small"
                          onClick={() => handleEditClick(u)}
                          aria-label="edit"
                        >
                          <EditIcon fontSize="small" />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => handleDeleteClick(u)}
                          aria-label="delete"
                          color="error"
                          disabled={isSelf}
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            component="div"
            count={total}
            page={page}
            onPageChange={handleChangePage}
            rowsPerPage={rowsPerPage}
            onRowsPerPageChange={handleChangeRowsPerPage}
            rowsPerPageOptions={[10, 20, 50]}
          />
        </>
      )}

      {/* User Form Dialog */}
      <UserForm
        open={formOpen}
        onClose={handleFormClose}
        onSuccess={handleFormSuccess}
        user={selectedUser}
        currentUserId={currentUser?.id}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={handleDeleteCancel}>
        <DialogTitle>Delete User</DialogTitle>
        <DialogContent>
          {deleteError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {deleteError}
            </Alert>
          )}
          <DialogContentText>
            Are you sure you want to delete the user "{userToDelete?.email}"? This action cannot be
            undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteCancel} disabled={deleteLoading}>
            Cancel
          </Button>
          <Button
            onClick={handleDeleteConfirm}
            color="error"
            variant="contained"
            disabled={deleteLoading}
          >
            {deleteLoading ? <CircularProgress size={20} /> : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default UsersPage;
