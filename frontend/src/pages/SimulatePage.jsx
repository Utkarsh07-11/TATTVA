import React from 'react';
import PageHeader from '../components/PageHeader';
import WhatIfSandbox from '../components/WhatIfSandbox';
import { useDashboard } from '../context/DashboardContext';

export default function SimulatePage() {
  const { selectedBlock, horizonDays, forecast, activePreset, setActivePreset } = useDashboard();
  return (
    <div className="page-enter">
      <PageHeader
        kicker="Simulate"
        title="What-if operations sandbox"
        subtitle="Perturb availability, blasting delay, and rainfall, then re-score the trained production model."
      />
      <WhatIfSandbox
        selectedBlock={selectedBlock}
        horizonDays={horizonDays}
        baselineForecast={forecast}
        activePreset={activePreset}
        onClearPreset={() => setActivePreset(null)}
      />
    </div>
  );
}
