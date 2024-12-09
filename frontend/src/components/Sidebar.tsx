import { FC } from "react";
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Box,
  Typography,
  Divider,
} from "@mui/material";
import {
  Home as HomeIcon,
  Upload as UploadIcon,
  FormatListBulleted as ResultsIcon,
  Settings as SettingsIcon,
  Folder as OrganizeIcon,
} from "@mui/icons-material";
import { useLocation, useNavigate } from "react-router-dom";

const DRAWER_WIDTH = 240;

const menuItems = [
  { text: "Home", icon: <HomeIcon />, path: "/" },
  { text: "Upload", icon: <UploadIcon />, path: "/upload" },
  { text: "Results", icon: <ResultsIcon />, path: "/results" },
  { text: "Organizations", icon: <OrganizeIcon />, path: "/organizations" },
  { text: "Settings", icon: <SettingsIcon />, path: "/settings" },
];

const Sidebar: FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: DRAWER_WIDTH,
        flexShrink: 0,
        "& .MuiDrawer-paper": {
          width: DRAWER_WIDTH,
          boxSizing: "border-box",
          borderRight: "1px solid rgba(0, 0, 0, 0.12)",
        },
      }}
    >
      <Box sx={{ p: 2, pt: 4 }}>
        <Typography variant="h6" sx={{ fontWeight: 600 }}>
          Web Clipper
        </Typography>
      </Box>
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => navigate(item.path)}
              sx={{
                my: 0.5,
                mx: 1,
                borderRadius: 1,
                "&.Mui-selected": {
                  bgcolor: "primary.light",
                  color: "white",
                  "&:hover": {
                    bgcolor: "primary.main",
                  },
                },
              }}
            >
              <ListItemIcon sx={{ color: "inherit" }}>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Drawer>
  );
};

export default Sidebar;
