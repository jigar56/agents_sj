import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Box } from '@chakra-ui/react';
import Navbar from './components/Navbar';
import LaunchDashboard from './pages/LaunchDashboard';
import LaunchDetail from './pages/LaunchDetail';
import CreateLaunch from './pages/CreateLaunch';

function App() {
  return (
    <Router>
      <Box minH="100vh" bg="gray.50">
        <Navbar />
        <Routes>
          <Route path="/" element={<LaunchDashboard />} />
          <Route path="/launches/new" element={<CreateLaunch />} />
          <Route path="/launches/:id" element={<LaunchDetail />} />
        </Routes>
      </Box>
    </Router>
  );
}

export default App;
