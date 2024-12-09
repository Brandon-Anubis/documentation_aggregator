import { FC, useState, ChangeEvent, FormEvent } from "react";
import { TextField, Button, Typography } from "@mui/material";
import styled from "@emotion/styled";

const API_BASE_URL = "http://localhost:8000";

const Container = styled("div")`
  margin: 2rem;
  display: flex;
  flex-direction: column;
  max-width: 600px;
`;

const Upload: FC = () => {
  const [inputVal, setInputVal] = useState<string>("");
  const [message, setMessage] = useState<string>("");
  const [file, setFile] = useState<File | null>(null);

  const handleClip = async () => {
    if (!inputVal.trim()) {
      setMessage("Please enter a URL or input.");
      return;
    }
    setMessage("Processing...");
    try {
      const resp = await fetch(`${API_BASE_URL}/clip`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input: inputVal }),
      });

      if (!resp.ok) {
        const errData = await resp.json();
        setMessage(`Error: ${errData.detail}`);
        return;
      }

      const data = await resp.json();
      if (data.id) {
        setMessage(`Clipping done. Result ID: ${data.id}`);
      } else {
        setMessage("No results returned");
      }
    } catch (error: unknown) {
      setMessage(`Error: ${String(error)}`);
    }
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleFileUpload = async (e: FormEvent) => {
    e.preventDefault();
    if (!file) {
      setMessage("No file selected.");
      return;
    }
    setMessage("Uploading file...");
    const formData = new FormData();
    formData.append("file", file);

    try {
      const resp = await fetch(`${API_BASE_URL}/upload_file`, {
        method: "POST",
        body: formData,
      });
      const data = await resp.json();
      setMessage(`File uploaded as: ${data.filename}`);
    } catch (error: unknown) {
      setMessage(`Error: ${String(error)}`);
    }
  };

  return (
    <Container>
      <Typography variant="h5" gutterBottom>
        Start a New Clipping Process
      </Typography>
      <TextField
        fullWidth
        label="Enter URL or Sitemap URL"
        value={inputVal}
        onChange={(e) => setInputVal(e.target.value)}
        sx={{ my: 2 }}
      />
      <Button variant="contained" onClick={handleClip}>
        Clip Now
      </Button>

      <Typography variant="h6" sx={{ mt: 4 }}>
        Upload a Local File (markdown or sitemap.xml)
      </Typography>
      <form onSubmit={handleFileUpload} style={{ marginTop: "1rem" }}>
        <input type="file" onChange={handleFileChange} />
        <Button variant="contained" type="submit" sx={{ ml: 2 }}>
          Upload File
        </Button>
      </form>

      {message && (
        <Typography
          sx={{ mt: 2 }}
          color={message.startsWith("Error") ? "error" : "primary"}
        >
          {message}
        </Typography>
      )}
    </Container>
  );
};

export default Upload;
