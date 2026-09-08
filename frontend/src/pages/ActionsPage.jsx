import React from 'react';
import { useNavigate } from 'react-router-dom';
import PageHeader from '../components/PageHeader';
import RecommendationsPanel from '../components/RecommendationsPanel';
import { useDashboard } from '../context/DashboardContext';

export default function ActionsPage() {
  const { recommendations, setActivePreset } = useDashboard();
  const navigate = useNavigate();

  return (
    <div className="page-enter space-y-3">
      <PageHeader
        kicker="DECISION OPTIMIZATION · MILP"
        title="Actions"
        subtitle="Constrained optimization ranking operational interventions by expected recovery, cost, and feasibility."
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


