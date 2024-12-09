import { FC, useState, ChangeEvent, DragEvent } from "react";
import {
  Box,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  Divider,
  Alert,
  CircularProgress,
  Stack,
  Chip,
  IconButton,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
} from "@mui/material";
import {
  CloudUpload,
  Link as LinkIcon,
  Delete,
  ContentPaste,
} from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import { API_BASE_URL } from "../config";

interface ClipResult {
  title: string;
  url: string;
  status: "completed" | "failed";
  preview?: string;
  error?: string;
  markdown_path?: string;
  pdf_path?: string;
}

const Upload: FC = () => {
  const navigate = useNavigate();
  const [url, setUrl] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);
  const [organization, setOrganization] = useState("");
  const [tags, setTags] = useState<string[]>([]);
  const [newTag, setNewTag] = useState("");
  const [clipResult, setClipResult] = useState<ClipResult | null>(null);
  const [showPreview, setShowPreview] = useState(false);
  const [processingMessage, setProcessingMessage] = useState("");

  const handleClip = async () => {
    if (!url.trim()) {
      setMessage({ type: "error", text: "Please enter a URL" });
      return;
    }

    setLoading(true);
    setClipResult(null);
    setMessage(null);
    setProcessingMessage(
      url.endsWith("sitemap.xml")
        ? "Processing sitemap URLs... This may take a few minutes"
        : "Fetching and processing content..."
    );

    try {
      const response = await fetch(`${API_BASE_URL}/clip`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          input: url,
          organization,
          tags,
        }),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || "Failed to process URL");
      }

      setClipResult(result);

      if (result.status === "completed") {
        setMessage({
          type: "success",
          text: `Successfully clipped: ${result.title}`,
        });
        setShowPreview(true);
      } else {
        throw new Error(result.error || "Failed to process content");
      }
    } catch (error) {
      setMessage({
        type: "error",
        text: error instanceof Error ? error.message : "Error processing URL",
      });
    } finally {
      setLoading(false);
      setProcessingMessage("");
    }
  };

  const handleDrop = (e: DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    if (e.dataTransfer.files?.length) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleAddTag = () => {
    if (newTag && !tags.includes(newTag)) {
      setTags([...tags, newTag]);
      setNewTag("");
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter((tag) => tag !== tagToRemove));
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Upload Content
      </Typography>

      {message && (
        <Alert
          severity={message.type}
          sx={{ mb: 3 }}
          onClose={() => setMessage(null)}
        >
          {message.text}
        </Alert>
      )}

      {/* Preview Dialog */}
      <Dialog
        open={showPreview}
        onClose={() => setShowPreview(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {clipResult?.title}
          <Typography variant="subtitle2" color="text.secondary">
            {clipResult?.url}
          </Typography>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ whiteSpace: "pre-wrap", my: 2 }}>
            {clipResult?.preview}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowPreview(false)}>Close</Button>
          <Button
            variant="contained"
            onClick={() => {
              setShowPreview(false);
              navigate("/results");
            }}
          >
            Go to Results
          </Button>
        </DialogActions>
      </Dialog>

      <Stack spacing={3}>
        {/* URL Input Section */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <LinkIcon sx={{ mr: 1, verticalAlign: "middle" }} />
              Clip from URL
            </Typography>
            <TextField
              fullWidth
              label="Enter URL or Sitemap URL"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              sx={{ mb: 2 }}
            />
            <Button
              variant="contained"
              onClick={handleClip}
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : null}
            >
              {loading ? "Processing..." : "Clip Now"}
            </Button>
            {loading && (
              <Box sx={{ width: "100%", mt: 2 }}>
                <LinearProgress />
                <Typography variant="caption" sx={{ mt: 1, display: "block" }}>
                  {processingMessage}
                </Typography>
              </Box>
            )}
          </CardContent>
        </Card>

        {/* File Upload Section */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <CloudUpload sx={{ mr: 1, verticalAlign: "middle" }} />
              Upload File
            </Typography>
            <Box
              sx={{
                border: "2px dashed",
                borderColor: isDragging ? "primary.main" : "grey.300",
                borderRadius: 2,
                p: 3,
                textAlign: "center",
                bgcolor: isDragging ? "action.hover" : "background.paper",
                cursor: "pointer",
              }}
              onDragOver={(e) => {
                e.preventDefault();
                setIsDragging(true);
              }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
              onClick={() => document.getElementById("file-input")?.click()}
            >
              <input
                id="file-input"
                type="file"
                hidden
                onChange={(e) => e.target.files && setFile(e.target.files[0])}
              />
              <CloudUpload
                sx={{ fontSize: 48, color: "primary.main", mb: 2 }}
              />
              <Typography>
                Drag and drop your file here or click to browse
              </Typography>
              {file && (
                <Chip
                  label={file.name}
                  onDelete={() => setFile(null)}
                  sx={{ mt: 2 }}
                />
              )}
            </Box>
          </CardContent>
        </Card>

        {/* Organization and Tags */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Organization
            </Typography>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Select Organization</InputLabel>
              <Select
                value={organization}
                label="Select Organization"
                onChange={(e) => setOrganization(e.target.value)}
              >
                <MenuItem value="personal">Personal</MenuItem>
                <MenuItem value="work">Work</MenuItem>
                <MenuItem value="research">Research</MenuItem>
              </Select>
            </FormControl>

            <Typography variant="h6" gutterBottom>
              Tags
            </Typography>
            <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
              {tags.map((tag) => (
                <Chip
                  key={tag}
                  label={tag}
                  onDelete={() => handleRemoveTag(tag)}
                />
              ))}
            </Stack>
            <Box sx={{ display: "flex", gap: 1 }}>
              <TextField
                size="small"
                label="Add tag"
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleAddTag()}
              />
              <Button
                variant="outlined"
                onClick={handleAddTag}
                disabled={!newTag}
              >
                Add
              </Button>
            </Box>
          </CardContent>
        </Card>
      </Stack>
    </Box>
  );
};

export default Upload;
