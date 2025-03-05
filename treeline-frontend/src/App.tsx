import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import VisualizationPage from './page/VisualizationPage';
import NodeDetailsPage from './page/NodeDetailsPage';
import MetricsDashboardPage from './components/MetricsDashboard';

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<VisualizationPage />} />
        <Route path="/node/:nodeId" element={<NodeDetailsPage />} />
        <Route path="/project-metrics" element={<MetricsDashboardPage />} />
        <Route path="*" element={<div>Not Found</div>} />
      </Routes>
    </Router>
  );
};

export default App;