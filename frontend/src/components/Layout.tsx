import { FC, ReactNode } from "react";
import { Box } from "@mui/material";
import Sidebar from "./Sidebar";

interface LayoutProps {
  children: ReactNode;
}

const DRAWER_WIDTH = 240;

const Layout: FC<LayoutProps> = ({ children }) => {
  return (
    <Box sx={{ display: "flex" }}>
      <Sidebar />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${DRAWER_WIDTH}px)` },
          ml: { sm: `${DRAWER_WIDTH}px` },
        }}
      >
        {children}
      </Box>
    </Box>
  );
};

export default Layout;
