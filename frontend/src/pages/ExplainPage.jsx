import React from 'react';
import PageHeader from '../components/PageHeader';
import ExplainabilityPanel from '../components/ExplainabilityPanel';
import { useDashboard } from '../context/DashboardContext';

export default function ExplainPage() {
  const { explanation } = useDashboard();
  return (
    <div className="page-enter space-y-3">
      <PageHeader
        kicker="ROOT CAUSE ATTRIBUTION · SHAP"
        title="Root Cause"
        subtitle="Operational feature contributions for forecasted production shortfall. Attributed model drivers, not verified physical causation."
      />
      <ExplainabilityPanel explanation={explanation} />
    </div>
  );
}


