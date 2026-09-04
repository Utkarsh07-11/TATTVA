import React from 'react';
import PageHeader from '../components/PageHeader';
import DigitalMineMap from '../components/DigitalMineMap';
import { useDashboard } from '../context/DashboardContext';

export default function MapPage() {
  const { prospectivityGeoJson, drillholesGeoJson, blocksGeoJson, equipmentList, selectedBlock } = useDashboard();
  return (
    <div className="page-enter">
      <PageHeader
        kicker="Visualize"
        title="Digital mine map"
        subtitle="Prospectivity surface, collar assays, block boundaries, and fleet positions on the Balaghat manganese belt."
      />
      <DigitalMineMap
        prospectivityGeoJson={prospectivityGeoJson}
        drillholesGeoJson={drillholesGeoJson}
        blocksGeoJson={blocksGeoJson}
        equipmentList={equipmentList}
        selectedBlock={selectedBlock}
      />
    </div>
  );
}
