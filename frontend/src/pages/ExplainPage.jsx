import React from 'react';
import PageHeader from '../components/PageHeader';
import ExplainabilityPanel from '../components/ExplainabilityPanel';
import { useDashboard } from '../context/DashboardContext';

export default function ExplainPage() {
  const { explanation } = useDashboard();
  return (
    <div className="page-enter">
      <PageHeader
        kicker="Explain"
        title="Shortfall root-cause attribution"
        subtitle="SHAP TreeExplainer groups model drivers into operational factors. Attribution is not physical causation."
      />
      <ExplainabilityPanel explanation={explanation} />
    </div>
  );
}
