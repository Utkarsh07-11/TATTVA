import React from 'react';
import PageHeader from '../components/PageHeader';
import ResourceExplorer from '../components/ResourceExplorer';

export default function ResourcesPage() {
  return (
    <div className="page-enter">
      <PageHeader
        kicker="Reserve intelligence"
        title="Illustrative resource estimate"
        subtitle="IDW grade interpolation from collar assays. Explicitly a toy geostatistical model — not JORC or UNFC compliant."
      />
      <ResourceExplorer />
    </div>
  );
}
