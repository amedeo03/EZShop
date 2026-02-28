import { Outlet, useNavigate } from "react-router-dom";
import {
  AppBar,
  Toolbar,
  Typography,
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Box,
} from "@mui/material";
import DashboardIcon from "@mui/icons-material/Dashboard";
import ShoppingCartIcon from "@mui/icons-material/ShoppingCart";
import InventoryIcon from "@mui/icons-material/Inventory2";
import PeopleIcon from "@mui/icons-material/People";
import ReceiptLongIcon from "@mui/icons-material/ReceiptLong";
import BarChartIcon from "@mui/icons-material/BarChart";
import StorefrontIcon from "@mui/icons-material/Storefront";

const drawerWidth = 240;

export default function Layout() {
  const navigate = useNavigate();

  return (
    <Box sx={{ display: "flex" }}>
      {/* Top App Bar */}
      <AppBar
        position="fixed"
        sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}
      >
        <Toolbar>
          <Typography variant="h6" noWrap component="div">
            EZShop
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Sidebar */}
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          [`& .MuiDrawer-paper`]: {
            width: drawerWidth,
            boxSizing: "border-box",
          },
        }}
      >
        <Toolbar />
        <List>
          <ListItemButton onClick={() => navigate("/Overview")}>
            <ListItemIcon>
              <DashboardIcon />
            </ListItemIcon>
            <ListItemText primary="Overview" />
          </ListItemButton>

          <ListItemButton onClick={() => navigate("/Sales")}>
            <ListItemIcon>
              <ShoppingCartIcon />
            </ListItemIcon>
            <ListItemText primary="Sales" />
          </ListItemButton>

          <ListItemButton onClick={() => navigate("/Inventory")}>
            <ListItemIcon>
              <InventoryIcon />
            </ListItemIcon>
            <ListItemText primary="Inventory" />
          </ListItemButton>

          <ListItemButton onClick={() => navigate("/Suppliers")}>
            <ListItemIcon>
              <PeopleIcon />
            </ListItemIcon>
            <ListItemText primary="Suppliers" />
          </ListItemButton>

          <ListItemButton onClick={() => navigate("/Orders")}>
            <ListItemIcon>
              <ReceiptLongIcon />
            </ListItemIcon>
            <ListItemText primary="Orders" />
          </ListItemButton>

          <ListItemButton onClick={() => navigate("/Analytics")}>
            <ListItemIcon>
              <BarChartIcon />
            </ListItemIcon>
            <ListItemText primary="Analytics" />
          </ListItemButton>
        </List>
      </Drawer>

      {/* Page Content */}
      <Box
        component="main"
        sx={{ flexGrow: 1, bgcolor: "#f5f5f5", p: 3 }}
      >
        <Toolbar />
        <Outlet />
      </Box>
    </Box>
  );
}