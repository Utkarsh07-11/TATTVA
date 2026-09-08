import React from 'react';
import PageHeader from '../components/PageHeader';
import WhatIfSandbox from '../components/WhatIfSandbox';
import { useDashboard } from '../context/DashboardContext';

export default function SimulatePage() {
  const { selectedBlock, horizonDays, forecast, activePreset, setActivePreset } = useDashboard();
  return (
    <div className="page-enter space-y-3">
      <PageHeader
        kicker="SCENARIO SIMULATOR"
        title="Simulator"
        subtitle="Perturb equipment availability, blasting delays, and rainfall to simulate LightGBM model responses."
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


