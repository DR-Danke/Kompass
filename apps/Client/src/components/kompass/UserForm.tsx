import React, { useEffect, useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Alert,
  CircularProgress,
  MenuItem,
  FormControlLabel,
  Switch,
  InputAdornment,
  IconButton,
} from '@mui/material';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import type { UserAdminResponse, UserAdminCreate, UserAdminUpdate, UserRole } from '@/types/kompass';
import { userService } from '@/services/kompassService';

const ROLE_OPTIONS: { value: UserRole; label: string }[] = [
  { value: 'admin', label: 'Admin' },
  { value: 'manager', label: 'Manager' },
  { value: 'user', label: 'User' },
  { value: 'viewer', label: 'Viewer' },
];

interface UserFormProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  user?: UserAdminResponse | null;
  currentUserId?: string;
}

interface CreateFormData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  role: UserRole;
}

interface EditFormData {
  first_name: string;
  last_name: string;
  role: UserRole;
  is_active: boolean;
}

const UserForm: React.FC<UserFormProps> = ({ open, onClose, onSuccess, user, currentUserId }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);

  // Password change state
  const [passwordDialogOpen, setPasswordDialogOpen] = useState(false);
  const [newPassword, setNewPassword] = useState('');
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [showNewPassword, setShowNewPassword] = useState(false);

  const isEditMode = !!user;
  const isSelf = user && currentUserId && user.id === currentUserId;

  const createForm = useForm<CreateFormData>({
    defaultValues: {
      email: '',
      password: '',
      first_name: '',
      last_name: '',
      role: 'user',
    },
  });

  const editForm = useForm<EditFormData>({
    defaultValues: {
      first_name: '',
      last_name: '',
      role: 'user',
      is_active: true,
    },
  });

  useEffect(() => {
    if (open) {
      setError(null);
      setShowPassword(false);
      if (user) {
        editForm.reset({
          first_name: user.first_name || '',
          last_name: user.last_name || '',
          role: user.role,
          is_active: user.is_active,
        });
      } else {
        createForm.reset({
          email: '',
          password: '',
          first_name: '',
          last_name: '',
          role: 'user',
        });
      }
    }
  }, [open, user, createForm, editForm]);

  const onCreateSubmit = async (data: CreateFormData) => {
    setLoading(true);
    setError(null);

    try {
      const payload: UserAdminCreate = {
        email: data.email,
        password: data.password,
        first_name: data.first_name || undefined,
        last_name: data.last_name || undefined,
        role: data.role,
      };

      console.log('INFO [UserForm]: Creating new user');
      await userService.create(payload);
      onSuccess();
      onClose();
    } catch (err) {
      console.log('ERROR [UserForm]: Failed to create user', err);
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosErr = err as { response?: { data?: { detail?: string } } };
        setError(axiosErr.response?.data?.detail || 'Failed to create user');
      } else {
        setError(err instanceof Error ? err.message : 'Failed to create user');
      }
    } finally {
      setLoading(false);
    }
  };

  const onEditSubmit = async (data: EditFormData) => {
    if (!user) return;

    setLoading(true);
    setError(null);

    try {
      const payload: UserAdminUpdate = {
        first_name: data.first_name || undefined,
        last_name: data.last_name || undefined,
        role: data.role,
        is_active: data.is_active,
      };

      console.log(`INFO [UserForm]: Updating user ${user.id}`);
      await userService.update(user.id, payload);
      onSuccess();
      onClose();
    } catch (err) {
      console.log('ERROR [UserForm]: Failed to update user', err);
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosErr = err as { response?: { data?: { detail?: string } } };
        setError(axiosErr.response?.data?.detail || 'Failed to update user');
      } else {
        setError(err instanceof Error ? err.message : 'Failed to update user');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async () => {
    if (!user || newPassword.length < 8) return;

    setPasswordLoading(true);
    setPasswordError(null);

    try {
      console.log(`INFO [UserForm]: Changing password for user ${user.id}`);
      await userService.changePassword(user.id, { new_password: newPassword });
      setPasswordDialogOpen(false);
      setNewPassword('');
    } catch (err) {
      console.log('ERROR [UserForm]: Failed to change password', err);
      setPasswordError(err instanceof Error ? err.message : 'Failed to change password');
    } finally {
      setPasswordLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      onClose();
    }
  };

  return (
    <>
      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>{isEditMode ? 'Edit User' : 'Add User'}</DialogTitle>

        {/* CREATE FORM */}
        {!isEditMode && (
          <form onSubmit={createForm.handleSubmit(onCreateSubmit)}>
            <DialogContent>
              {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <TextField
                  fullWidth
                  label="Email"
                  type="email"
                  {...createForm.register('email', {
                    required: 'Email is required',
                    pattern: {
                      value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                      message: 'Invalid email address',
                    },
                  })}
                  error={!!createForm.formState.errors.email}
                  helperText={createForm.formState.errors.email?.message}
                  disabled={loading}
                />
                <TextField
                  fullWidth
                  label="Password"
                  type={showPassword ? 'text' : 'password'}
                  {...createForm.register('password', {
                    required: 'Password is required',
                    minLength: {
                      value: 8,
                      message: 'Password must be at least 8 characters',
                    },
                  })}
                  error={!!createForm.formState.errors.password}
                  helperText={createForm.formState.errors.password?.message}
                  disabled={loading}
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={() => setShowPassword(!showPassword)}
                          edge="end"
                          size="small"
                        >
                          {showPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />
                <TextField
                  fullWidth
                  label="First Name"
                  {...createForm.register('first_name')}
                  disabled={loading}
                />
                <TextField
                  fullWidth
                  label="Last Name"
                  {...createForm.register('last_name')}
                  disabled={loading}
                />
                <Controller
                  name="role"
                  control={createForm.control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      select
                      label="Role"
                      disabled={loading}
                    >
                      {ROLE_OPTIONS.map((opt) => (
                        <MenuItem key={opt.value} value={opt.value}>
                          {opt.label}
                        </MenuItem>
                      ))}
                    </TextField>
                  )}
                />
              </Box>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleClose} disabled={loading}>
                Cancel
              </Button>
              <Box sx={{ position: 'relative' }}>
                <Button type="submit" variant="contained" disabled={loading}>
                  Create
                </Button>
                {loading && (
                  <CircularProgress
                    size={24}
                    sx={{
                      position: 'absolute',
                      top: '50%',
                      left: '50%',
                      marginTop: '-12px',
                      marginLeft: '-12px',
                    }}
                  />
                )}
              </Box>
            </DialogActions>
          </form>
        )}

        {/* EDIT FORM */}
        {isEditMode && (
          <form onSubmit={editForm.handleSubmit(onEditSubmit)}>
            <DialogContent>
              {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <TextField
                  fullWidth
                  label="Email"
                  value={user?.email || ''}
                  disabled
                  helperText="Email cannot be changed"
                />
                <TextField
                  fullWidth
                  label="First Name"
                  {...editForm.register('first_name')}
                  disabled={loading}
                />
                <TextField
                  fullWidth
                  label="Last Name"
                  {...editForm.register('last_name')}
                  disabled={loading}
                />
                <Controller
                  name="role"
                  control={editForm.control}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      select
                      label="Role"
                      disabled={loading || !!isSelf}
                      helperText={isSelf ? 'Cannot change your own role' : ''}
                    >
                      {ROLE_OPTIONS.map((opt) => (
                        <MenuItem key={opt.value} value={opt.value}>
                          {opt.label}
                        </MenuItem>
                      ))}
                    </TextField>
                  )}
                />
                <Controller
                  name="is_active"
                  control={editForm.control}
                  render={({ field }) => (
                    <FormControlLabel
                      control={
                        <Switch
                          checked={field.value}
                          onChange={field.onChange}
                          disabled={loading || !!isSelf}
                        />
                      }
                      label="Active"
                    />
                  )}
                />
                {isSelf && (
                  <Alert severity="info" variant="outlined">
                    You cannot change your own role or deactivate your own account.
                  </Alert>
                )}
                <Button
                  variant="outlined"
                  onClick={() => {
                    setNewPassword('');
                    setPasswordError(null);
                    setShowNewPassword(false);
                    setPasswordDialogOpen(true);
                  }}
                  disabled={loading}
                >
                  Change Password
                </Button>
              </Box>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleClose} disabled={loading}>
                Cancel
              </Button>
              <Box sx={{ position: 'relative' }}>
                <Button type="submit" variant="contained" disabled={loading}>
                  Update
                </Button>
                {loading && (
                  <CircularProgress
                    size={24}
                    sx={{
                      position: 'absolute',
                      top: '50%',
                      left: '50%',
                      marginTop: '-12px',
                      marginLeft: '-12px',
                    }}
                  />
                )}
              </Box>
            </DialogActions>
          </form>
        )}
      </Dialog>

      {/* Change Password Dialog */}
      <Dialog
        open={passwordDialogOpen}
        onClose={() => !passwordLoading && setPasswordDialogOpen(false)}
        maxWidth="xs"
        fullWidth
      >
        <DialogTitle>Change Password</DialogTitle>
        <DialogContent>
          {passwordError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {passwordError}
            </Alert>
          )}
          <TextField
            fullWidth
            label="New Password"
            type={showNewPassword ? 'text' : 'password'}
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            disabled={passwordLoading}
            helperText="Minimum 8 characters"
            sx={{ mt: 1 }}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    onClick={() => setShowNewPassword(!showNewPassword)}
                    edge="end"
                    size="small"
                  >
                    {showNewPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => setPasswordDialogOpen(false)}
            disabled={passwordLoading}
          >
            Cancel
          </Button>
          <Button
            onClick={handleChangePassword}
            variant="contained"
            disabled={passwordLoading || newPassword.length < 8}
          >
            {passwordLoading ? <CircularProgress size={20} /> : 'Change Password'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default UserForm;
