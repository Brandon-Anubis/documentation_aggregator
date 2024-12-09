import { FC } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Button } from '@mui/material';
import Home from './pages/Home';
import Upload from './pages/Upload';
import Results from './pages/Results';
import styled from '@emotion/styled';

const StyledToolbar = styled(Toolbar)`
  display: flex;
  justify-content: space-between;
`;

const App: FC = () => {
  return (
    <Router>
      <AppBar position="static">
        <StyledToolbar>
          <Typography variant="h6">Intelligent Web Clipper</Typography>
          <div>
            <Button color="inherit" component={Link} to="/">Home</Button>
            <Button color="inherit" component={Link} to="/upload">Upload</Button>
            <Button color="inherit" component={Link} to="/results">Results</Button>
          </div>
        </StyledToolbar>
      </AppBar>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/upload" element={<Upload />} />
        <Route path="/results" element={<Results />} />
      </Routes>
    </Router>
  );
};

export default App;