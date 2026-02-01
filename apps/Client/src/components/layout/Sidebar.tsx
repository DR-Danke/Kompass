import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  IconButton,
  Typography,
  Divider,
  Avatar,
  Tooltip,
} from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import SettingsIcon from '@mui/icons-material/Settings';
import LogoutIcon from '@mui/icons-material/Logout';
import MenuIcon from '@mui/icons-material/Menu';
import MenuOpenIcon from '@mui/icons-material/MenuOpen';
import FactoryIcon from '@mui/icons-material/Factory';
import InventoryIcon from '@mui/icons-material/Inventory';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import CollectionsIcon from '@mui/icons-material/Collections';
import PeopleIcon from '@mui/icons-material/People';
import DescriptionIcon from '@mui/icons-material/Description';
import CategoryIcon from '@mui/icons-material/Category';
import LabelIcon from '@mui/icons-material/Label';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import { useAuth } from '@/hooks/useAuth';

const SIDEBAR_BG = '#1a1d21';
const ACCENT_COLOR = '#2196f3';

interface NavItem {
  title: string;
  icon: React.ReactElement;
  path: string;
}

const navItems: NavItem[] = [
  { title: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
  { title: 'Suppliers', icon: <FactoryIcon />, path: '/suppliers' },
  { title: 'Biblia General', icon: <InventoryIcon />, path: '/products' },
  { title: 'Import Wizard', icon: <CloudUploadIcon />, path: '/import-wizard' },
  { title: 'Categories', icon: <CategoryIcon />, path: '/categories' },
  { title: 'Portfolios', icon: <CollectionsIcon />, path: '/portfolios' },
  { title: 'Clients', icon: <PeopleIcon />, path: '/clients' },
  { title: 'Quotations', icon: <DescriptionIcon />, path: '/quotations' },
  { title: 'Niches', icon: <LabelIcon />, path: '/niches' },
  { title: 'Pricing', icon: <AttachMoneyIcon />, path: '/pricing' },
  { title: 'Settings', icon: <SettingsIcon />, path: '/settings' },
  { title: 'Help & Docs', icon: <HelpOutlineIcon />, path: '/docs' },
];

interface SidebarProps {
  isCollapsed: boolean;
  onToggle: () => void;
  width: number;
}

export const Sidebar: React.FC<SidebarProps> = ({ isCollapsed, onToggle, width }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();

  const handleNavigate = (path: string) => {
    navigate(path);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <Drawer
      variant="permanent"
      sx={{
        width,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width,
          boxSizing: 'border-box',
          backgroundColor: SIDEBAR_BG,
          color: 'white',
          borderRight: 'none',
          transition: 'width 0.3s ease',
          overflowX: 'hidden',
        },
      }}
    >
      {/* Header */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: isCollapsed ? 'center' : 'space-between',
          p: 2,
          minHeight: 64,
        }}
      >
        {!isCollapsed && (
          <Typography variant="h6" noWrap sx={{ fontWeight: 'bold' }}>
            Your App
          </Typography>
        )}
        <IconButton onClick={onToggle} sx={{ color: 'white' }}>
          {isCollapsed ? <MenuIcon /> : <MenuOpenIcon />}
        </IconButton>
      </Box>

      <Divider sx={{ borderColor: 'rgba(255,255,255,0.12)' }} />

      {/* Navigation */}
      <List sx={{ flexGrow: 1, py: 2 }}>
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;

          return (
            <ListItem key={item.path} disablePadding sx={{ mb: 0.5 }}>
              <Tooltip title={isCollapsed ? item.title : ''} placement="right">
                <ListItemButton
                  onClick={() => handleNavigate(item.path)}
                  sx={{
                    mx: 1,
                    borderRadius: 2,
                    backgroundColor: isActive ? `${ACCENT_COLOR}20` : 'transparent',
                    borderLeft: isActive ? `3px solid ${ACCENT_COLOR}` : '3px solid transparent',
                    '&:hover': {
                      backgroundColor: isActive ? `${ACCENT_COLOR}30` : 'rgba(255,255,255,0.08)',
                    },
                  }}
                >
                  <ListItemIcon
                    sx={{
                      color: isActive ? ACCENT_COLOR : 'rgba(255,255,255,0.7)',
                      minWidth: 40,
                    }}
                  >
                    {item.icon}
                  </ListItemIcon>
                  {!isCollapsed && (
                    <ListItemText
                      primary={item.title}
                      primaryTypographyProps={{
                        fontWeight: isActive ? 600 : 400,
                        color: isActive ? 'white' : 'rgba(255,255,255,0.7)',
                      }}
                    />
                  )}
                </ListItemButton>
              </Tooltip>
            </ListItem>
          );
        })}
      </List>

      <Divider sx={{ borderColor: 'rgba(255,255,255,0.12)' }} />

      {/* User Section */}
      <Box sx={{ p: 2 }}>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            mb: 2,
          }}
        >
          <Avatar sx={{ width: 32, height: 32, bgcolor: ACCENT_COLOR }}>
            {user?.first_name?.[0] || user?.email?.[0]?.toUpperCase() || 'U'}
          </Avatar>
          {!isCollapsed && (
            <Box sx={{ ml: 1.5, overflow: 'hidden' }}>
              <Typography variant="body2" noWrap sx={{ fontWeight: 500 }}>
                {user?.first_name || user?.email}
              </Typography>
              <Typography variant="caption" noWrap sx={{ color: 'rgba(255,255,255,0.5)' }}>
                {user?.role}
              </Typography>
            </Box>
          )}
        </Box>

        <Tooltip title={isCollapsed ? 'Logout' : ''} placement="right">
          <ListItemButton
            onClick={handleLogout}
            sx={{
              borderRadius: 2,
              '&:hover': {
                backgroundColor: 'rgba(255,255,255,0.08)',
              },
            }}
          >
            <ListItemIcon sx={{ color: 'rgba(255,255,255,0.7)', minWidth: 40 }}>
              <LogoutIcon />
            </ListItemIcon>
            {!isCollapsed && (
              <ListItemText
                primary="Logout"
                primaryTypographyProps={{ color: 'rgba(255,255,255,0.7)' }}
              />
            )}
          </ListItemButton>
        </Tooltip>
      </Box>
    </Drawer>
  );
};
