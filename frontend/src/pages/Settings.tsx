import { FC, useState } from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  Switch,
  FormControlLabel,
  Divider,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  Grid,
} from "@mui/material";
import { API_BASE_URL } from "../config";

interface SettingsData {
  darkMode: boolean;
  defaultOrganization: string;
  defaultFormat: "markdown" | "pdf" | "both";
  autoDownload: boolean;
  apiKey: string;
  notificationsEnabled: boolean;
  storageLocation: string;
}

const Settings: FC = () => {
  const [settings, setSettings] = useState<SettingsData>({
    darkMode: false,
    defaultOrganization: "personal",
    defaultFormat: "both",
    autoDownload: false,
    apiKey: "**********************",
    notificationsEnabled: true,
    storageLocation: "/default/path",
  });
  const [saved, setSaved] = useState(false);

  const handleSave = async () => {
    try {
      // API call to save settings
      await fetch(`${API_BASE_URL}/settings`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(settings),
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (error) {
      console.error("Error saving settings:", error);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>

      {saved && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Settings saved successfully!
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Appearance
              </Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.darkMode}
                    onChange={(e) =>
                      setSettings({ ...settings, darkMode: e.target.checked })
                    }
                  />
                }
                label="Dark Mode"
              />

              <Divider sx={{ my: 3 }} />

              <Typography variant="h6" gutterBottom>
                Default Settings
              </Typography>
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Default Organization</InputLabel>
                <Select
                  value={settings.defaultOrganization}
                  label="Default Organization"
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      defaultOrganization: e.target.value,
                    })
                  }
                >
                  <MenuItem value="personal">Personal</MenuItem>
                  <MenuItem value="work">Work</MenuItem>
                  <MenuItem value="research">Research</MenuItem>
                </Select>
              </FormControl>

              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Default Format</InputLabel>
                <Select
                  value={settings.defaultFormat}
                  label="Default Format"
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      defaultFormat: e.target.value as
                        | "markdown"
                        | "pdf"
                        | "both",
                    })
                  }
                >
                  <MenuItem value="markdown">Markdown</MenuItem>
                  <MenuItem value="pdf">PDF</MenuItem>
                  <MenuItem value="both">Both</MenuItem>
                </Select>
              </FormControl>

              <FormControlLabel
                control={
                  <Switch
                    checked={settings.autoDownload}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        autoDownload: e.target.checked,
                      })
                    }
                  />
                }
                label="Auto-download after clipping"
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                API Settings
              </Typography>
              <TextField
                fullWidth
                label="API Key"
                type="password"
                value={settings.apiKey}
                onChange={(e) =>
                  setSettings({ ...settings, apiKey: e.target.value })
                }
                sx={{ mb: 2 }}
              />
              <Button variant="outlined" size="small">
                Generate New Key
              </Button>

              <Divider sx={{ my: 3 }} />

              <Typography variant="h6" gutterBottom>
                Storage
              </Typography>
              <TextField
                fullWidth
                label="Storage Location"
                value={settings.storageLocation}
                onChange={(e) =>
                  setSettings({ ...settings, storageLocation: e.target.value })
                }
                sx={{ mb: 2 }}
              />

              <Divider sx={{ my: 3 }} />

              <Typography variant="h6" gutterBottom>
                Notifications
              </Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.notificationsEnabled}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        notificationsEnabled: e.target.checked,
                      })
                    }
                  />
                }
                label="Enable Notifications"
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Box sx={{ mt: 3, display: "flex", justifyContent: "flex-end" }}>
        <Button variant="contained" onClick={handleSave}>
          Save Settings
        </Button>
      </Box>
    </Box>
  );
};

export default Settings;
