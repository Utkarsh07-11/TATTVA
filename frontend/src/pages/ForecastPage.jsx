import React from 'react';
import PageHeader from '../components/PageHeader';
import ProductionAnalytics from '../components/ProductionAnalytics';
import OverviewCards from '../components/OverviewCards';
import { useDashboard } from '../context/DashboardContext';

export default function ForecastPage() {
  const { forecast, overview, selectedBlock } = useDashboard();
  return (
    <div className="page-enter space-y-5">
      <PageHeader
        kicker="Predict"
        title="Probabilistic production forecast"
        subtitle="LightGBM quantile regression (P10 / P50 / P90) with rolling-origin validation and exogenous equipment, blast, and weather features."
      />
      <OverviewCards forecast={forecast} overview={overview} selectedBlock={selectedBlock} />
      <ProductionAnalytics forecast={forecast} selectedBlock={selectedBlock} />
    </div>
  );
}
