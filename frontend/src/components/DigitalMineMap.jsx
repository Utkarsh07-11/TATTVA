import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import { MapPin, Sliders, Layers, Eye, EyeOff, Info } from 'lucide-react';

export default function DigitalMineMap({
  prospectivityGeoJson,
  drillholesGeoJson,
  blocksGeoJson,
  equipmentList,
  selectedBlock
}) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const layersRef = useRef({
    blocks: null,
    prospectivity: null,
    drillholes: null,
    equipment: null,
  });

  const [probCutoff, setProbCutoff] = useState(0.40);
  const [showHeatmap, setShowHeatmap] = useState(true);
  const [showDrillholes, setShowDrillholes] = useState(true);
  const [showFleet, setShowFleet] = useState(true);
  const [selectedEntity, setSelectedEntity] = useState(null);

  // Helper color for prospectivity probability
  const getProspectivityColor = (prob) => {
    if (prob >= 0.70) return '#7c3aed'; // Deep purple (High prospectivity)
    if (prob >= 0.55) return '#a855f7'; // Purple
    if (prob >= 0.40) return '#f59e0b'; // Amber
    if (prob >= 0.25) return '#3b82f6'; // Blue
    return '#10b981';                   // Low / Barren green
  };

  // Helper color for drillhole Mn grade
  const getGradeColor = (grade) => {
    if (grade >= 35.0) return '#ec4899'; // High grade pink/purple
    if (grade >= 25.0) return '#f59e0b'; // Medium grade amber
    if (grade >= 15.0) return '#3b82f6'; // Low grade blue
    return '#94a3b8';                   // Barren slate
  };

  // Initialize Leaflet Map
  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (!mapInstanceRef.current) {
      const map = L.map(mapContainerRef.current, {
        center: [21.8715, 80.1843],
        zoom: 14,
        zoomControl: true,
      });

      // CartoDB Dark Basemap
      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
        maxZoom: 19,
      }).addTo(map);

      mapInstanceRef.current = map;
    }

    return () => {
      // Keep map instance mounted across component lifecycle
    };
  }, []);

  // Render Mine Blocks Polygons
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map || !blocksGeoJson) return;

    if (layersRef.current.blocks) {
      map.removeLayer(layersRef.current.blocks);
    }

    const blocksLayer = L.geoJSON(blocksGeoJson, {
      style: (feature) => {
        const isSelected = feature.properties.block_id === selectedBlock;
        return {
          color: isSelected ? '#a855f7' : '#38bdf8',
          weight: isSelected ? 3.5 : 2,
          opacity: 0.9,
          fillColor: isSelected ? '#a855f7' : '#38bdf8',
          fillOpacity: isSelected ? 0.25 : 0.08,
          dashArray: isSelected ? null : '4, 4',
        };
      },
      onEachFeature: (feature, layer) => {
        const p = feature.properties;
        layer.bindTooltip(`<strong>${p.name}</strong><br/>Target: ${p.target_monthly_tonnes} t/mo`, {
          className: 'leaflet-tooltip-dark',
        });
        layer.on('click', () => {
          setSelectedEntity({ type: 'block', data: p });
        });
      },
    }).addTo(map);

    layersRef.current.blocks = blocksLayer;
  }, [blocksGeoJson, selectedBlock]);

  // Render Prospectivity Grid Heatmap Cells
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map || !prospectivityGeoJson) return;

    if (layersRef.current.prospectivity) {
      map.removeLayer(layersRef.current.prospectivity);
    }

    if (!showHeatmap) return;

    const filteredFeatures = prospectivityGeoJson.features.filter(
      (f) => f.properties.prospectivity_prob >= probCutoff
    );

    const prospectivityLayer = L.geoJSON(
      { type: 'FeatureCollection', features: filteredFeatures },
      {
        style: (feature) => {
          const prob = feature.properties.prospectivity_prob;
          return {
            color: getProspectivityColor(prob),
            weight: 0.5,
            fillColor: getProspectivityColor(prob),
            fillOpacity: Math.min(0.65, prob * 0.8),
          };
        },
        onEachFeature: (feature, layer) => {
          const p = feature.properties;
          layer.bindPopup(`
            <div class="p-1 text-xs">
              <div class="font-bold text-sm text-purple-400 mb-1">Manganese Prospectivity Cell</div>
              <div><strong>Grid ID:</strong> ${p.grid_id}</div>
              <div><strong>Occurrence Probability:</strong> ${(p.prospectivity_prob * 100).toFixed(1)}%</div>
              <div><strong>Model Uncertainty:</strong> ${(p.uncertainty * 100).toFixed(1)}%</div>
              <div><strong>Classification:</strong> ${p.prospectivity_class}</div>
              <div class="mt-1 pt-1 border-t border-slate-700 text-slate-400">
                Satellite Proxy (Iron Oxide B4/B2): ${p.iron_oxide_index.toFixed(2)}<br/>
                Elevation: ${p.elevation_m.toFixed(0)}m | Slope: ${p.slope_deg.toFixed(1)}°
              </div>
            </div>
          `);
          layer.on('click', () => {
            setSelectedEntity({ type: 'prospectivity', data: p });
          });
        },
      }
    ).addTo(map);

    layersRef.current.prospectivity = prospectivityLayer;
  }, [prospectivityGeoJson, probCutoff, showHeatmap]);

  // Render Drillhole Assays
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map || !drillholesGeoJson) return;

    if (layersRef.current.drillholes) {
      map.removeLayer(layersRef.current.drillholes);
    }

    if (!showDrillholes) return;

    const markers = [];
    drillholesGeoJson.features.forEach((f) => {
      const [lon, lat] = f.geometry.coordinates;
      const p = f.properties;
      const marker = L.circleMarker([lat, lon], {
        radius: 5,
        fillColor: getGradeColor(p.mn_grade_pct),
        color: '#ffffff',
        weight: 1,
        opacity: 0.9,
        fillOpacity: 0.85,
      });

      marker.bindPopup(`
        <div class="p-1 text-xs font-sans">
          <div class="font-bold text-sm text-pink-400 mb-1">Assay Collar: ${p.hole_id}</div>
          <div><strong>Mn Grade:</strong> <span class="font-bold text-white">${p.mn_grade_pct}% Mn</span></div>
          <div><strong>Fe Grade:</strong> ${p.fe_grade_pct}% Fe | <strong>SiO2:</strong> ${p.sio2_pct}%</div>
          <div><strong>Interval:</strong> ${p.depth_from_m}m - ${p.depth_to_m}m (${p.thickness_m}m thick)</div>
          <div><strong>Host Lithology:</strong> <span class="text-amber-300 font-mono">${p.lithology_code}</span></div>
          <div><strong>Collar Elevation:</strong> ${p.collar_elevation_m}m</div>
          <div class="mt-1 pt-1 border-t border-slate-700 text-slate-400">
            Domain: ${p.structural_domain} (${p.sample_date})
          </div>
        </div>
      `);

      marker.on('click', () => {
        setSelectedEntity({ type: 'drillhole', data: p });
      });

      markers.push(marker);
    });

    const dhLayerGroup = L.layerGroup(markers).addTo(map);
    layersRef.current.drillholes = dhLayerGroup;
  }, [drillholesGeoJson, showDrillholes]);

  // Render Equipment GPS Markers
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map || !equipmentList) return;

    if (layersRef.current.equipment) {
      map.removeLayer(layersRef.current.equipment);
    }

    if (!showFleet) return;

    const fleetMarkers = [];
    equipmentList.forEach((eq) => {
      const isDown = eq.status === 'UNDER_MAINTENANCE';
      const isStandby = eq.status === 'STANDBY';
      const eqColor = isDown ? '#ef4444' : isStandby ? '#f59e0b' : '#10b981';

      const customIcon = L.divIcon({
        className: 'custom-eq-icon',
        html: `
          <div style="background-color: ${eqColor}; width: 14px; height: 14px; border-radius: 3px; border: 2px solid white; box-shadow: 0 0 6px ${eqColor};"></div>
        `,
        iconSize: [14, 14],
      });

      const marker = L.marker([eq.lat, eq.lon], { icon: customIcon });
      marker.bindPopup(`
        <div class="p-1 text-xs">
          <div class="font-bold text-white">${eq.id} (${eq.type})</div>
          <div>Block: ${eq.block}</div>
          <div>Status: <span class="font-bold" style="color:${eqColor}">${eq.status}</span></div>
          <div>Mechanical Health: ${eq.health_pct}%</div>
        </div>
      `);
      fleetMarkers.push(marker);
    });

    const fleetGroup = L.layerGroup(fleetMarkers).addTo(map);
    layersRef.current.equipment = fleetGroup;
  }, [equipmentList, showFleet]);

  return (
    <div className="panel overflow-hidden flex flex-col h-[620px]">
      {/* Map Control Bar */}
      <div className="bg-slate-900/95 border-b border-slate-800 px-4 py-2.5 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2">
          <MapPin className="w-4 h-4 text-purple-400" />
          <span className="font-bold text-white text-sm">
            Digital Mine Geospatial Intelligence
          </span>
          <span className="text-slate-400 hidden sm:inline">
            (Balaghat Manganese Belt • UTM Zone 44N)
          </span>
        </div>

        {/* Layer Toggles & Probability Slider */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Probability Cutoff Slider */}
          <div className="flex items-center gap-2 bg-slate-800 px-2.5 py-1 rounded-lg border border-slate-700">
            <Sliders className="w-3.5 h-3.5 text-purple-400" />
            <span className="text-slate-300 font-medium">Cutoff:</span>
            <input
              type="range"
              min="0.10"
              max="0.85"
              step="0.05"
              value={probCutoff}
              onChange={(e) => setProbCutoff(parseFloat(e.target.value))}
              className="w-20 accent-purple-500 cursor-pointer"
            />
            <span className="font-mono text-purple-300 font-bold w-9 text-right">
              {(probCutoff * 100).toFixed(0)}%
            </span>
          </div>

          {/* Toggle Buttons */}
          <button
            onClick={() => setShowHeatmap(!showHeatmap)}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg border font-medium transition-all ${
              showHeatmap
                ? 'bg-purple-950/70 border-purple-700 text-purple-300'
                : 'bg-slate-800 border-slate-700 text-slate-400'
            }`}
          >
            {showHeatmap ? <Eye className="w-3.5 h-3.5" /> : <EyeOff className="w-3.5 h-3.5" />}
            Prospectivity Surface
          </button>

          <button
            onClick={() => setShowDrillholes(!showDrillholes)}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg border font-medium transition-all ${
              showDrillholes
                ? 'bg-pink-950/70 border-pink-700 text-pink-300'
                : 'bg-slate-800 border-slate-700 text-slate-400'
            }`}
          >
            {showDrillholes ? <Eye className="w-3.5 h-3.5" /> : <EyeOff className="w-3.5 h-3.5" />}
            Assay Collars
          </button>

          <button
            onClick={() => setShowFleet(!showFleet)}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg border font-medium transition-all ${
              showFleet
                ? 'bg-emerald-950/70 border-emerald-700 text-emerald-300'
                : 'bg-slate-800 border-slate-700 text-slate-400'
            }`}
          >
            {showFleet ? <Eye className="w-3.5 h-3.5" /> : <EyeOff className="w-3.5 h-3.5" />}
            Fleet GPS
          </button>
        </div>
      </div>

      {/* Map Canvas */}
      <div className="relative flex-1 w-full">
        <div ref={mapContainerRef} className="w-full h-full" />

        {/* Floating Map Legend */}
        <div className="absolute bottom-4 left-4 bg-slate-900/90 backdrop-blur-md border border-slate-700 p-3 rounded-lg shadow-xl text-xs z-[1000] max-w-xs pointer-events-auto">
          <div className="font-bold text-white mb-1.5 flex items-center justify-between">
            <span>Map Layers & Ground Truth</span>
          </div>

          <div className="space-y-1.5 text-slate-300">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-pink-500"></span>
              <span>High-Grade Assay (&gt;35% Mn)</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-amber-500"></span>
              <span>Medium-Grade Assay (25-35% Mn)</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded bg-purple-600"></span>
              <span>ML Prospectivity Likelihood (&ge;70%)</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded bg-blue-500"></span>
              <span>Moderate Prospectivity (&ge;40%)</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 bg-emerald-500 rounded-sm"></span>
              <span>Excavator / Drill Operational</span>
            </div>
          </div>

          <div className="mt-2 pt-2 border-t border-slate-700 text-[10px] text-slate-400 flex items-start gap-1">
            <Info className="w-3.5 h-3.5 shrink-0 text-indigo-400 mt-0.5" />
            <span>
              Satellite proxies (Sentinel-2 band ratios + DEM) provide surface alteration context, weighted below point drillhole assay evidence.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
