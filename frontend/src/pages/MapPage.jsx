import React from 'react';
import PageHeader from '../components/PageHeader';
import DigitalMineMap from '../components/DigitalMineMap';
import { useDashboard } from '../context/DashboardContext';

export default function MapPage() {
  const { prospectivityGeoJson, drillholesGeoJson, blocksGeoJson, equipmentList, selectedBlock } = useDashboard();
  return (
    <div className="page-enter space-y-3">
      <PageHeader
        kicker="GEOSPATIAL WORKSPACE · BALAGHAT"
        title="Digital Mine"
        subtitle="Sentinel-2 multispectral rasters, Copernicus DEM topography, and unsupervised exploration priority heuristic."
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


