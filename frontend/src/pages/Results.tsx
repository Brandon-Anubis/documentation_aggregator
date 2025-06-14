import { FC, useEffect, useState } from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  IconButton,
  TextField,
  Menu,
  MenuItem,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  InputAdornment,
  Select,
  FormControl,
  InputLabel,
  Tooltip,
  Pagination,
  SelectChangeEvent,
} from "@mui/material";
import {
  MoreVert,
  Download,
  Delete,
  Edit,
  Search,
  FilterList,
  Description as MarkdownIcon,
  PictureAsPdf as PdfIcon,
  Visibility,
} from "@mui/icons-material";
import { format } from "date-fns";
import { API_BASE_URL } from "../config";
import { CircularProgress } from "@mui/material";

interface Result {
  id: string;
  title: string;
  url: string;
  timestamp: string;
  markdown_path: string;
  pdf_path: string;
  organization?: string;
  tags?: string[];
}

interface ResultsResponse {
  items: Result[];
  total_pages: number;
  page: number;
  per_page: number;
}

const Results: FC = () => {
  const [results, setResults] = useState<Result[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [organization, setOrganization] = useState("all");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedResult, setSelectedResult] = useState<Result | null>(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editTitle, setEditTitle] = useState("");
  const [editTags, setEditTags] = useState<string[]>([]);
  const [organizations, setOrganizations] = useState<string[]>([]);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [previewHtml, setPreviewHtml] = useState<string | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);

  useEffect(() => {
    fetchResults();
    fetchOrganizations();
  }, [page, searchTerm, organization]);

  const fetchResults = async () => {
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        per_page: "10",
        ...(searchTerm && { search: searchTerm }),
        ...(organization !== "all" && { organization }),
      });

      const response = await fetch(`${API_BASE_URL}/results?${params}`);
      const data: ResultsResponse = await response.json();
      setResults(data.items);
      setTotalPages(data.total_pages);
    } catch (error) {
      console.error("Error fetching results:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchOrganizations = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/organizations`);
      const data = await response.json();
      setOrganizations(data.map((org: any) => org.name));
    } catch (error) {
      console.error("Error fetching organizations:", error);
    }
  };

  const handleDelete = async () => {
    if (!selectedResult) return;

    try {
      await fetch(`${API_BASE_URL}/results/${selectedResult.id}`, {
        method: "DELETE",
      });
      fetchResults();
    } catch (error) {
      console.error("Error deleting result:", error);
    }
    handleMenuClose();
  };

  const handleSaveEdit = async () => {
    if (!selectedResult) return;

    try {
      await fetch(`${API_BASE_URL}/results/${selectedResult.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: editTitle,
          tags: editTags,
        }),
      });
      fetchResults();
      setEditDialogOpen(false);
    } catch (error) {
      console.error("Error updating result:", error);
    }
  };

  const handleMenuOpen = (
    event: React.MouseEvent<HTMLElement>,
    result: Result
  ) => {
    setAnchorEl(event.currentTarget);
    setSelectedResult(result);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedResult(null);
  };

  const handleOrganizationChange = (event: SelectChangeEvent) => {
    setOrganization(event.target.value);
    setPage(1);
  };

  const handlePreview = async (result: Result) => {
    setPreviewOpen(true);
    setPreviewLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/preview/${result.id}`);
      const data = await res.json();
      setPreviewHtml(data.html || "<p>No preview available</p>");
    } catch (e) {
      setPreviewHtml("<p>Error loading preview</p>");
    } finally {
      setPreviewLoading(false);
    }
  };

  const handlePreviewClose = () => {
    setPreviewOpen(false);
    setPreviewHtml(null);
  };

  return (
    <Box>
      {/* Header and Filters */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Clipped Content
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              placeholder="Search clips..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Organization</InputLabel>
              <Select
                value={organization}
                label="Organization"
                onChange={handleOrganizationChange}
              >
                <MenuItem value="all">All Organizations</MenuItem>
                {organizations.map((org) => (
                  <MenuItem key={org} value={org}>
                    {org}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Box>

      {/* Results Grid */}
      <Grid container spacing={3}>
        {results.map((result) => (
          <Grid item xs={12} key={result.id}>
            <Card>
              <CardContent>
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "flex-start",
                  }}
                >
                  <Box>
                    <Typography variant="h6">{result.title}</Typography>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      gutterBottom
                    >
                      {result.url}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {format(new Date(result.timestamp), "PPP")}
                    </Typography>
                    {result.organization && (
                      <Chip
                        label={result.organization}
                        size="small"
                        sx={{ mt: 1, mr: 1 }}
                      />
                    )}
                    {result.tags?.map((tag) => (
                      <Chip
                        key={tag}
                        label={tag}
                        size="small"
                        sx={{ mt: 1, mr: 1 }}
                      />
                    ))}
                  </Box>
                  <Box>
                    <Tooltip title="Download as Markdown">
                      <IconButton
                        href={`${API_BASE_URL}/download/${result.id}/markdown`}
                        sx={{
                          display: "flex",
                          flexDirection: "column",
                          alignItems: "center",
                          gap: "4px",
                        }}
                      >
                        <MarkdownIcon />
                        <Typography variant="caption">MD</Typography>
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Download as PDF">
                      <IconButton
                        href={`${API_BASE_URL}/download/${result.id}/pdf`}
                        sx={{
                          display: "flex",
                          flexDirection: "column",
                          alignItems: "center",
                          gap: "4px",
                        }}
                      >
                        <PdfIcon />
                        <Typography variant="caption">PDF</Typography>
                      </IconButton>
                    </Tooltip>
                    <IconButton onClick={(e) => handleMenuOpen(e, result)}>
                      <MoreVert />
                    </IconButton>
                    <Tooltip title="Preview">
                      <IconButton onClick={() => handlePreview(result)}>
                        <Visibility />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Pagination */}
      <Box sx={{ mt: 4, display: "flex", justifyContent: "center" }}>
        <Pagination
          count={totalPages}
          page={page}
          onChange={(_, value) => setPage(value)}
          color="primary"
        />
      </Box>

      {/* Context Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem
          onClick={() => {
            setEditDialogOpen(true);
            handleMenuClose();
          }}
        >
          <Edit sx={{ mr: 1 }} /> Edit
        </MenuItem>
        <MenuItem onClick={handleDelete}>
          <Delete sx={{ mr: 1 }} /> Delete
        </MenuItem>
      </Menu>

      {/* Edit Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)}>
        <DialogTitle>Edit Clip</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Title"
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            sx={{ mt: 2 }}
          />
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Tags
            </Typography>
            {editTags.map((tag) => (
              <Chip
                key={tag}
                label={tag}
                onDelete={() => setEditTags(editTags.filter((t) => t !== tag))}
                sx={{ mr: 1, mb: 1 }}
              />
            ))}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSaveEdit} variant="contained">
            Save
          </Button>
        </DialogActions>
      </Dialog>

      {/* Preview Dialog */}
      <Dialog open={previewOpen} onClose={handlePreviewClose} maxWidth="md" fullWidth>
        <DialogTitle>Preview</DialogTitle>
        <DialogContent dividers>
          {previewLoading ? (
            <Box sx={{ display: "flex", justifyContent: "center", p: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            <div dangerouslySetInnerHTML={{ __html: previewHtml || "" }} />
          )}
        </DialogContent>
      </Dialog>
    </Box>
  );
};

export default Results;
