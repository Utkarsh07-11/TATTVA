import React from 'react';
import PageHeader from '../components/PageHeader';
import ProductionAnalytics from '../components/ProductionAnalytics';
import { useDashboard } from '../context/DashboardContext';

export default function ForecastPage() {
  const { forecast, selectedBlock } = useDashboard();
  return (
    <div className="page-enter space-y-3">
      <PageHeader
        kicker="PRODUCTION INTELLIGENCE & RECONCILIATION"
        title="Production"
        subtitle="Operational forecast (LightGBM quantile regression) and statutory company reported production (FY16–FY26)."
      />
      <ProductionAnalytics forecast={forecast} selectedBlock={selectedBlock} />
    </div>
  );
}


