import { FC, useEffect, useState } from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Paper,
  Stack,
  CircularProgress,
} from "@mui/material";
import { CloudUpload, Article, Folder, TrendingUp } from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import { API_BASE_URL } from "../config";

interface Stats {
  total_clips: number;
  total_organizations: number;
  active_projects: number;
  storage_used: number;
}

const StatCard: FC<{ title: string; value: string }> = ({ title, value }) => (
  <Paper elevation={0} sx={{ p: 2, bgcolor: "background.default" }}>
    <Typography color="text.secondary" variant="subtitle2">
      {title}
    </Typography>
    <Typography variant="h4" sx={{ mt: 1, fontWeight: "bold" }}>
      {value}
    </Typography>
  </Paper>
);

const FeatureCard: FC<{
  icon: React.ReactNode;
  title: string;
  description: string;
}> = ({ icon, title, description }) => (
  <Card sx={{ height: "100%" }}>
    <CardContent>
      <Box sx={{ display: "flex", mb: 2 }}>
        <Box
          sx={{
            p: 1,
            borderRadius: 1,
            bgcolor: "primary.light",
            color: "white",
          }}
        >
          {icon}
        </Box>
      </Box>
      <Typography variant="h6" gutterBottom>
        {title}
      </Typography>
      <Typography variant="body2" color="text.secondary">
        {description}
      </Typography>
    </CardContent>
  </Card>
);

const Home: FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/stats`);
        const data = await response.json();
        setStats(data);
      } catch (error) {
        console.error("Error fetching stats:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  return (
    <Box>
      {/* Hero Section */}
      <Box sx={{ mb: 6 }}>
        <Typography variant="h1" gutterBottom>
          Welcome to Web Clipper
        </Typography>
        <Typography variant="h5" color="text.secondary" sx={{ mb: 4 }}>
          Transform web content into organized, searchable knowledge
        </Typography>
        <Stack direction="row" spacing={2}>
          <Button
            variant="contained"
            size="large"
            onClick={() => navigate("/upload")}
          >
            Start Clipping
          </Button>
          <Button
            variant="outlined"
            size="large"
            onClick={() => navigate("/results")}
          >
            View Results
          </Button>
        </Stack>
      </Box>

      {/* Stats Section */}
      <Grid container spacing={3} sx={{ mb: 6 }}>
        {loading ? (
          <Box
            sx={{
              display: "flex",
              justifyContent: "center",
              width: "100%",
              py: 3,
            }}
          >
            <CircularProgress />
          </Box>
        ) : (
          <>
            <Grid item xs={12} sm={6} md={3}>
              <StatCard
                title="Total Clips"
                value={stats?.total_clips.toLocaleString() || "0"}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <StatCard
                title="Organizations"
                value={stats?.total_organizations.toLocaleString() || "0"}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <StatCard
                title="Active Projects"
                value={stats?.active_projects.toLocaleString() || "0"}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <StatCard
                title="Storage Used"
                value={`${stats?.storage_used || 0} GB`}
              />
            </Grid>
          </>
        )}
      </Grid>

      {/* Features Section */}
      <Typography variant="h4" sx={{ mb: 4 }}>
        Key Features
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <FeatureCard
            icon={<CloudUpload />}
            title="Easy Upload"
            description="Clip content from any webpage or upload local files with a single click"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <FeatureCard
            icon={<Article />}
            title="Smart Processing"
            description="Automatically extract and clean content, maintaining formatting"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <FeatureCard
            icon={<Folder />}
            title="Organization"
            description="Keep your clips organized with projects and tags"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <FeatureCard
            icon={<TrendingUp />}
            title="Analytics"
            description="Track your content collection and usage patterns"
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default Home;
