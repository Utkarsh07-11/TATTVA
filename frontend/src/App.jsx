import React from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { DashboardProvider } from './context/DashboardContext';
import AppShell from './layout/AppShell';
import OverviewPage from './pages/OverviewPage';
import MapPage from './pages/MapPage';
import ForecastPage from './pages/ForecastPage';
import ExplainPage from './pages/ExplainPage';
import ActionsPage from './pages/ActionsPage';
import SimulatePage from './pages/SimulatePage';
import ResourcesPage from './pages/ResourcesPage';

export default function App() {
  return (
    <DashboardProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<AppShell />}>
            <Route path="/" element={<OverviewPage />} />
            <Route path="/mine-map" element={<MapPage />} />
            <Route path="/forecast" element={<ForecastPage />} />
            <Route path="/explain" element={<ExplainPage />} />
            <Route path="/actions" element={<ActionsPage />} />
            <Route path="/simulate" element={<SimulatePage />} />
            <Route path="/resources" element={<ResourcesPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </DashboardProvider>
  );
}
