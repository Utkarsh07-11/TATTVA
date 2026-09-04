import React from 'react';
import { useNavigate } from 'react-router-dom';
import PageHeader from '../components/PageHeader';
import RecommendationsPanel from '../components/RecommendationsPanel';
import { useDashboard } from '../context/DashboardContext';

export default function ActionsPage() {
  const { recommendations, setActivePreset } = useDashboard();
  const navigate = useNavigate();

  return (
    <div className="page-enter">
      <PageHeader
        kicker="Recommend"
        title="Constrained intervention plan"
        subtitle="PuLP ranks feasible actions by recovery, cost, risk, and feasibility. Simulate a card to see the forecast move."
      />
      <RecommendationsPanel
        recommendations={recommendations}
        onApplyAction={(opt) => {
          setActivePreset(opt);
          navigate('/simulate');
        }}
      />
    </div>
  );
}
