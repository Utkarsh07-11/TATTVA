import React from 'react';
import PageHeader from '../components/PageHeader';
import ResourceExplorer from '../components/ResourceExplorer';

export default function ResourcesPage() {
  return (
    <div className="page-enter space-y-3">
      <PageHeader
        kicker="GEOSTATISTICAL MODEL"
        title="Resources"
        subtitle="Inverse Distance Weighting (IDW) interpolation from collar assays. Experimental demonstration."
      />
      <ResourceExplorer />
    </div>
  );
}


