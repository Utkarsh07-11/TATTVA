import React from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { DashboardProvider } from './context/DashboardContext';
import StoryWorksShell from './layout/StoryWorksShell';
import StoryOverviewPage from './pages/StoryOverviewPage';
import DigitalMinePage from './pages/DigitalMinePage';
import ProductionRealityPage from './pages/ProductionRealityPage';
import OperationsSandboxPage from './pages/OperationsSandboxPage';
import ContactUsPage from './pages/ContactUsPage';

export default function App() {
  return (
    <DashboardProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<StoryWorksShell />}>
            {/* 5-Page Editorial Structure */}
            <Route path="/" element={<StoryOverviewPage />} />
            <Route path="/digital-mine" element={<DigitalMinePage />} />
            <Route path="/production" element={<ProductionRealityPage />} />
            <Route path="/operations" element={<OperationsSandboxPage />} />
            <Route path="/contact" element={<ContactUsPage />} />

            {/* Backward Compatibility Redirects */}
            <Route path="/mine-map" element={<Navigate to="/digital-mine" replace />} />
            <Route path="/forecast" element={<Navigate to="/production" replace />} />
            <Route path="/reality-check" element={<Navigate to="/production" replace />} />
            <Route path="/explain" element={<Navigate to="/operations" replace />} />
            <Route path="/actions" element={<Navigate to="/operations" replace />} />
            <Route path="/simulate" element={<Navigate to="/operations" replace />} />
            <Route path="/resources" element={<Navigate to="/digital-mine" replace />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </DashboardProvider>
  );
}
