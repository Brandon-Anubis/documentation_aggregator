import { FC, useEffect, useState } from "react";
import {
  Typography,
  List,
  ListItem,
  ListItemText,
  Button,
} from "@mui/material";
import styled from "@emotion/styled";

interface ListedResult {
  id: string;
  title: string;
  url: string;
  timestamp: string;
  markdown_path?: string;
  pdf_path?: string;
  website_name?: string;
}

const API_BASE_URL = "http://localhost:8000";

const Container = styled("div")`
  margin: 2rem;
`;

const Results: FC = () => {
  const [results, setResults] = useState<ListedResult[]>([]);

  const fetchResults = async () => {
    try {
      const resp = await fetch(`${API_BASE_URL}/results`);
      const data: ListedResult[] = await resp.json();
      setResults(data);
    } catch (error: unknown) {
      console.error("Error fetching results:", error);
    }
  };

  useEffect(() => {
    fetchResults();
  }, []);

  return (
    <Container>
      <Typography variant="h4" gutterBottom>
        Results
      </Typography>
      {results.length === 0 && (
        <Typography>No results found. Try clipping first.</Typography>
      )}
      <List>
        {results.map((r) => (
          <ListItem
            key={r.id}
            sx={{ flexDirection: "column", alignItems: "start" }}
          >
            <ListItemText
              primary={r.website_name || r.title}
              secondary={
                <>
                  <Typography component="span" display="block">
                    URL: {r.url}
                  </Typography>
                  <Typography component="span" display="block">
                    Timestamp: {r.timestamp}
                  </Typography>
                </>
              }
            />
            <Button
              href={`${API_BASE_URL}/download/${r.markdown_path}`}
              target="_blank"
              sx={{ mr: 2, mt: 1 }}
            >
              Download Markdown
            </Button>
            <Button
              href={`${API_BASE_URL}/download/${r.pdf_path}`}
              target="_blank"
              sx={{ mt: 1 }}
            >
              Download PDF
            </Button>
          </ListItem>
        ))}
      </List>
    </Container>
  );
};

export default Results;
