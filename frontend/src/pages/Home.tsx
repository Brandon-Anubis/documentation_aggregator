import { FC } from 'react';
import { Typography } from '@mui/material';
import styled from '@emotion/styled';

const Container = styled('div')`
  margin: 2rem;
`;

const Home: FC = () => {
  return (
    <Container>
      <Typography variant="h4" gutterBottom>Welcome to Intelligent Web Clipper</Typography>
      <Typography paragraph>
        This tool scrapes documentation pages from a URL, a sitemap, or from uploaded markdown files.
        It then processes and cleans the content, outputting Markdown and PDF files that can be integrated 
        into an external knowledge base or any other system you choose.
      </Typography>
      <Typography variant="h6">How to Use:</Typography>
      <ul>
        <li>Go to <strong>Upload</strong> to provide a URL or upload a file.</li>
        <li>Click "Clip Now" to start scraping and processing.</li>
        <li>Check <strong>Results</strong> to download your processed Markdown or PDF.</li>
      </ul>
    </Container>
  );
};

export default Home;