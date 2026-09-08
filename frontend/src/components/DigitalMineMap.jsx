import React, { useEffect, useRef, useState, useCallback, useMemo } from 'react';
import L from 'leaflet';
import {
  MapPin,
  Sliders,
  Eye,
  EyeOff,
  Info,
  ShieldCheck,
  Database,
  Layers,
  CheckCircle2,
  XCircle,
  ChevronDown,
  AlertTriangle,
  Sparkles,
  Flame,
  Activity,
  Compass,
  FileText,
  Target,
  Globe,
  Radio
} from 'lucide-react';
import BasemapSelector from './BasemapSelector';
import { BASEMAP_OPTIONS, DEFAULT_BASEMAP_ID } from '../config/basemaps';
import { api } from '../services/api';

// India administrative boundary reference geometry based on Survey of India data.
import indiaBoundaryRaw from '../assets/india_soi_boundary.geojson?raw';

const indiaBoundaryGeoJson = typeof indiaBoundaryRaw === 'string' ? JSON.parse(indiaBoundaryRaw) : indiaBoundaryRaw;

// Available real prospectivity models/layers (Phase 9B)
const REAL_PROSPECTIVITY_LAYERS = [
  {
    id: 'exploration_priority_score',
    name: 'Real Exploration Priority',
    shortName: 'Priority Ranking',
    description: 'Ensemble multi-method ranking heuristic combining anomaly, robust distance, and anchor similarity.',
    badgeColor: 'bg-red-950 text-red-300 border-red-700',
    accentColor: '#dc2626'
  },
  {
    id: 'anomaly_score',
    name: 'Spectral/Terrain Anomaly',
    shortName: 'Isolation Forest Anomaly',
    description: 'Unsupervised tree-isolation multi-spectral and terrain anomaly score.',
    badgeColor: 'bg-purple-950 text-purple-300 border-purple-700',
    accentColor: '#a855f7'
  },
  {
    id: 'robust_distance_score',
    name: 'Robust Multivariate Distance',
    shortName: 'Mahalanobis Distance',
    description: 'PCA-decorrelated robust covariance Mahalanobis distance from AOI centroid.',
    badgeColor: 'bg-orange-950 text-orange-300 border-orange-700',
    accentColor: '#f97316'
  },
  {
    id: 'positive_anchor_similarity',
    name: 'Bharweli Anchor Similarity',
    shortName: 'One-Class Similarity',
    description: 'Standardized Euclidean / exponential similarity to verified Bharweli shaft portal (GRID-13860).',
    badgeColor: 'bg-emerald-950 text-emerald-300 border-emerald-700',
    accentColor: '#10b981'
  }
];

export default function DigitalMineMap({
  prospectivityGeoJson,
  drillholesGeoJson,
  blocksGeoJson,
  equipmentList,
  selectedBlock,
  defaultBasemap = DEFAULT_BASEMAP_ID,
}) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const layersRef = useRef({
    baseLayers: null,
    blocks: null,
    prospectivity: null,
    drillholes: null,
    equipment: null,
    realMines: null,
    indiaBoundary: null,
    realProspectivity: null,
    realEvidence: null,
  });

  const [currentBasemap, setCurrentBasemap] = useState(defaultBasemap);

  // Map View Mode: 'mine_detail' (focused on active mine) | 'global_belt' (all 10 MOIL mines overview)
  const [mapViewMode, setMapViewMode] = useState('mine_detail');

  // Synthetic Layers State (TATTVA Operational Simulation)
  const [probCutoff, setProbCutoff] = useState(0.40);
  const [showHeatmap, setShowHeatmap] = useState(false);
  const [showDrillholes, setShowDrillholes] = useState(false);
  const [showFleet, setShowFleet] = useState(false);
  const [showRealMines, setShowRealMines] = useState(true);

  // Real Data & Multi-Mine States (Phase 11)
  const [realMines, setRealMines] = useState([]);
  const [selectedRealMineId, setSelectedRealMineId] = useState('MOIL_BALAGHAT');
  const [mineDashboard, setMineDashboard] = useState(null);
  const [showOverviewCard, setShowOverviewCard] = useState(false);
  const [showLimitationsDrawer, setShowLimitationsDrawer] = useState(false);

  // Phase 9B/10 Real Prospectivity Layer State (Balaghat Only)
  const [showRealProspectivity, setShowRealProspectivity] = useState(true);
  const [showEvidenceLayer, setShowEvidenceLayer] = useState(true);
  const [activeScoreLayer, setActiveScoreLayer] = useState('exploration_priority_score');
  const [realScoreCutoff, setRealScoreCutoff] = useState(0.00);
  const [realProspectivityData, setRealProspectivityData] = useState(null);
  const [realProspectivityMeta, setRealProspectivityMeta] = useState(null);
  const [realEvidenceData, setRealEvidenceData] = useState(null);
  const [isLoadingProspectivity, setIsLoadingProspectivity] = useState(false);
  const [perfMetrics, setPerfMetrics] = useState({ loadTimeMs: 0, renderTimeMs: 0, cellCount: 0 });

  // Selected cell / entity inspection details
  const [selectedEntity, setSelectedEntity] = useState(null);

  // Dynamic Color Mapping for Real Prospectivity Layers
  const getRealScoreColor = (score, layerId) => {
    if (layerId === 'exploration_priority_score') {
      if (score >= 0.80) return '#dc2626'; // Vivid Red (Top exploration priority)
      if (score >= 0.65) return '#f97316'; // Amber / Orange
      if (score >= 0.50) return '#eab308'; // Gold / Yellow
      if (score >= 0.35) return '#06b6d4'; // Cyan
      return '#334155';                   // Background Slate
    }
    if (layerId === 'anomaly_score') {
      if (score >= 0.40) return '#ec4899'; // Pink/Magenta
      if (score >= 0.25) return '#a855f7'; // Purple
      if (score >= 0.15) return '#3b82f6'; // Blue
      return '#1e293b';
    }
    if (layerId === 'robust_distance_score') {
      if (score >= 0.10) return '#f43f5e'; // Rose
      if (score >= 0.03) return '#fb923c'; // Orange
      if (score >= 0.01) return '#0284c7'; // Sky Blue
      return '#0f172a';
    }
    if (layerId === 'positive_anchor_similarity') {
      if (score >= 0.85) return '#10b981'; // Emerald (Close to Bharweli portal)
      if (score >= 0.70) return '#14b8a6'; // Teal
      if (score >= 0.55) return '#0284c7'; // Light Blue
      return '#1e293b';
    }
    return '#64748b';
  };

  // Helper color for synthetic prospectivity probability
  const getProspectivityColor = (prob) => {
    if (prob >= 0.70) return '#7c3aed';
    if (prob >= 0.55) return '#a855f7';
    if (prob >= 0.40) return '#f59e0b';
    if (prob >= 0.25) return '#3b82f6';
    return '#10b981';
  };

  // Helper color for drillhole Mn grade
  const getGradeColor = (grade) => {
    if (grade >= 35.0) return '#ec4899';
    if (grade >= 25.0) return '#f59e0b';
    if (grade >= 15.0) return '#3b82f6';
    return '#94a3b8';
  };

  // Helper for coordinate quality styling on MOIL mine markers
  const getCoordinateQualityColor = (quality) => {
    const q = (quality || '').toLowerCase();
    if (q.includes('surveyed') || q.includes('statutory')) return '#10b981'; // Emerald
    if (q.includes('centroid') || q.includes('lease')) return '#06b6d4';   // Cyan
    return '#f59e0b'; // Amber / Map-derived approximate
  };

  // 1. Fetch Real MOIL Mines Registry on Mount + URL state synchronization
  useEffect(() => {
    let isMounted = true;
    api.getRealMines()
      .then((res) => {
        if (isMounted && res && res.mines) {
          setRealMines(res.mines);

          // Parse URL search params (?mine=MOIL_BALAGHAT)
          const urlParams = new URLSearchParams(window.location.search);
          const mineParam = urlParams.get('mine');
          if (mineParam) {
            const match = res.mines.find((m) => m.mine_id.toUpperCase() === mineParam.toUpperCase());
            if (match) {
              setSelectedRealMineId(match.mine_id);
            } else {
              // Safe fallback for invalid URL parameter
              setSelectedRealMineId('MOIL_BALAGHAT');
            }
          }
        }
      })
      .catch((err) => {
        console.warn('Could not fetch real MOIL mines registry:', err);
      });
    return () => { isMounted = false; };
  }, []);

  // 2. Fetch Consolidated Mine Dashboard and Layers when selected mine changes
  useEffect(() => {
    let isMounted = true;
    if (!selectedRealMineId) return;

    // Synchronize URL search params safely
    try {
      const url = new URL(window.location.href);
      url.searchParams.set('mine', selectedRealMineId);
      window.history.replaceState({}, '', url.toString());
    } catch (e) {
      // Non-critical URL update failure
    }

    // Purge stale layers and popups immediately on mine switch
    const map = mapInstanceRef.current;
    if (map) {
      map.closePopup();
      if (layersRef.current.realProspectivity) {
        map.removeLayer(layersRef.current.realProspectivity);
        layersRef.current.realProspectivity = null;
      }
      if (layersRef.current.realEvidence) {
        map.removeLayer(layersRef.current.realEvidence);
        layersRef.current.realEvidence = null;
      }
    }
    setSelectedEntity(null);

    // Fetch consolidated mine dashboard summary
    api.getRealMineDashboard(selectedRealMineId)
      .then((res) => {
        if (isMounted && res) {
          setMineDashboard(res);
        }
      })
      .catch((err) => {
        console.warn(`Could not fetch dashboard summary for ${selectedRealMineId}:`, err);
      });

    // Balaghat-Specific Real Exploration Intelligence Data
    if (selectedRealMineId === 'MOIL_BALAGHAT') {
      setIsLoadingProspectivity(true);
      const t0 = performance.now();

      Promise.all([
        api.getRealProspectivityMeta(selectedRealMineId),
        api.getRealProspectivityGeoJson(selectedRealMineId),
        api.getRealMineralizationEvidence(selectedRealMineId),
      ])
        .then(([meta, geojson, evidence]) => {
          if (isMounted) {
            const t1 = performance.now();
            setRealProspectivityMeta(meta);
            setRealProspectivityData(geojson);
            setRealEvidenceData(evidence);
            setPerfMetrics((prev) => ({
              ...prev,
              loadTimeMs: Math.round(t1 - t0),
              cellCount: geojson?.features?.length || 0,
            }));
            setIsLoadingProspectivity(false);
          }
        })
        .catch((err) => {
          console.warn('Could not load real prospectivity dataset:', err);
          if (isMounted) setIsLoadingProspectivity(false);
        });
    } else {
      // Non-Balaghat isolation: strictly reset all Balaghat exploration datasets
      setRealProspectivityData(null);
      setRealProspectivityMeta(null);
      setRealEvidenceData(null);
      setIsLoadingProspectivity(false);
    }

    return () => { isMounted = false; };
  }, [selectedRealMineId]);

  // Dynamic grouping of real mines by State
  const minesByState = useMemo(() => {
    const groups = {};
    realMines.forEach((m) => {
      const state = m.state || 'Other';
      if (!groups[state]) groups[state] = [];
      groups[state].push(m);
    });
    return groups;
  }, [realMines]);

  // Switch / Apply Basemap Tile Layer
  const applyBasemap = useCallback((basemapId) => {
    const map = mapInstanceRef.current;
    if (!map) return;

    if (layersRef.current.baseLayers) {
      map.removeLayer(layersRef.current.baseLayers);
      layersRef.current.baseLayers = null;
    }

    const config = BASEMAP_OPTIONS.find((b) => b.id === basemapId) || BASEMAP_OPTIONS[0];
    const tileLayers = config.layers.map((layerDef) =>
      L.tileLayer(layerDef.url, {
        ...layerDef.options,
      })
    );

    const layerGroup = L.layerGroup(tileLayers).addTo(map);
    if (layerGroup.bringToBack) {
      layerGroup.bringToBack();
    }
    layersRef.current.baseLayers = layerGroup;
  }, []);

  // Handle Mine Selection
  const handleSelectRealMine = (mineId) => {
    setSelectedRealMineId(mineId);
    setMapViewMode('mine_detail');
    setSelectedEntity(null);

    const mine = realMines.find((m) => m.mine_id === mineId);
    if (mine && mine.latitude && mine.longitude && mapInstanceRef.current) {
      mapInstanceRef.current.flyTo([mine.latitude, mine.longitude], mineId === 'MOIL_BALAGHAT' ? 14 : 13, {
        duration: 1.2,
      });
    }
  };

  // Handle Global Sausar Belt Overview View
  const handleFitGlobalBelt = () => {
    setMapViewMode('global_belt');
    const map = mapInstanceRef.current;
    if (!map || realMines.length === 0) return;

    const latLngs = realMines
      .filter((m) => m.latitude && m.longitude)
      .map((m) => [m.latitude, m.longitude]);

    if (latLngs.length > 0) {
      const bounds = L.latLngBounds(latLngs);
      map.fitBounds(bounds, { padding: [50, 50], maxZoom: 10, duration: 1.2 });
    }
  };

  // Initialize Leaflet Map
  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (!mapInstanceRef.current) {
      const map = L.map(mapContainerRef.current, {
        center: [21.8464, 80.2281], // Centered at Balaghat Bharweli audited portal
        zoom: 13,
        zoomControl: true,
        preferCanvas: true, // Hardware-accelerated canvas rendering
      });

      mapInstanceRef.current = map;

      // Survey of India Sovereign Boundary Vector Layer
      const indiaLayer = L.geoJSON(indiaBoundaryGeoJson, {
        style: {
          color: '#818cf8',
          weight: 1.8,
          opacity: 0.9,
          fillColor: '#818cf8',
          fillOpacity: 0.02,
          dashArray: 'none',
        },
        interactive: false,
      }).addTo(map);

      layersRef.current.indiaBoundary = indiaLayer;
    }
  }, []);

  // Update Basemap when state changes
  useEffect(() => {
    if (mapInstanceRef.current) {
      applyBasemap(currentBasemap);
    }
  }, [currentBasemap, applyBasemap]);

  // -------------------------------------------------------------------------
  // Render Phase 9B/10 Real Prospectivity Grid Heatmap (Canvas-Rendered, Balaghat Only)
  // -------------------------------------------------------------------------
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    if (layersRef.current.realProspectivity) {
      map.removeLayer(layersRef.current.realProspectivity);
      layersRef.current.realProspectivity = null;
    }

    if (!showRealProspectivity || !realProspectivityData || selectedRealMineId !== 'MOIL_BALAGHAT') {
      return;
    }

    const t0 = performance.now();
    const canvasRenderer = L.canvas({ padding: 0.5 });

    const filteredFeatures = realProspectivityData.features.filter((f) => {
      const score = f.properties[activeScoreLayer];
      return typeof score === 'number' && score >= realScoreCutoff;
    });

    const activeLayerConfig = REAL_PROSPECTIVITY_LAYERS.find((l) => l.id === activeScoreLayer) || REAL_PROSPECTIVITY_LAYERS[0];

    const layer = L.geoJSON(
      { type: 'FeatureCollection', features: filteredFeatures },
      {
        renderer: canvasRenderer,
        style: (feature) => {
          const score = feature.properties[activeScoreLayer];
          const color = getRealScoreColor(score, activeScoreLayer);
          return {
            color: color,
            weight: 0.5,
            fillColor: color,
            fillOpacity: Math.min(0.80, Math.max(0.15, score * 0.85)),
          };
        },
        onEachFeature: (feature, featureLayer) => {
          const p = feature.properties;
          const scoreVal = typeof p[activeScoreLayer] === 'number' ? p[activeScoreLayer].toFixed(3) : 'N/A';
          const priorityVal = typeof p.exploration_priority_score === 'number' ? p.exploration_priority_score.toFixed(3) : 'N/A';
          const anomVal = typeof p.anomaly_score === 'number' ? p.anomaly_score.toFixed(3) : 'N/A';
          const robVal = typeof p.robust_distance_score === 'number' ? p.robust_distance_score.toFixed(3) : 'N/A';
          const simVal = typeof p.positive_anchor_similarity === 'number' ? p.positive_anchor_similarity.toFixed(3) : 'N/A';

          featureLayer.bindPopup(`
            <div class="p-2 text-xs font-sans max-w-xs">
              <div class="flex items-center justify-between gap-1.5 mb-1.5 pb-1 border-b border-slate-700">
                <span class="px-1.5 py-0.5 rounded bg-red-950/80 border border-red-600/70 text-red-300 font-bold text-[10px]">
                  REAL EXPLORATION CANDIDATE
                </span>
                <span class="text-slate-400 text-[10px] font-mono">${p.cell_id}</span>
              </div>
              <div class="font-bold text-sm text-white mb-1.5">${activeLayerConfig.name}: <span class="text-amber-400">${scoreVal}</span></div>
              
              <div class="grid grid-cols-2 gap-1 my-1.5 p-1.5 rounded bg-slate-950 border border-slate-800 text-[11px]">
                <div><span class="text-slate-400">Priority Score:</span> <strong class="text-red-300">${priorityVal}</strong></div>
                <div><span class="text-slate-400">Anomaly:</span> <strong class="text-purple-300">${anomVal}</strong></div>
                <div><span class="text-slate-400">Robust Dist:</span> <strong class="text-orange-300">${robVal}</strong></div>
                <div><span class="text-slate-400">Anchor Sim:</span> <strong class="text-emerald-300">${simVal}</strong></div>
              </div>

              <div class="text-[11px] mb-1">
                <strong>Data Quality:</strong> <span class="${p.feature_quality === 'valid' ? 'text-emerald-400 font-semibold' : 'text-amber-400 font-semibold'} capitalize">${p.feature_quality}</span> (30m Sentinel-2 + DEM)
              </div>

              <div class="mt-2 pt-1.5 border-t border-slate-700 text-slate-300 text-[10px] leading-relaxed">
                <strong>Interpretation:</strong> Relative exploration priority within the Balaghat AOI based on combined multi-spectral anomaly, robust distance, and anchor similarity ranking.
                <div class="mt-1 text-amber-300 font-medium">⚠️ Relative ranking heuristic, not probability. No independent negative drillholes available.</div>
              </div>
            </div>
          `);

          featureLayer.on('click', () => {
            setSelectedEntity({ type: 'real_cell', data: p });
          });
        },
      }
    ).addTo(map);

    const t1 = performance.now();
    setPerfMetrics((prev) => ({ ...prev, renderTimeMs: Math.round(t1 - t0) }));
    layersRef.current.realProspectivity = layer;
  }, [realProspectivityData, showRealProspectivity, activeScoreLayer, realScoreCutoff, selectedRealMineId]);

  // -------------------------------------------------------------------------
  // Render Authoritative Mineralization & Site Evidence Layer (Balaghat Only)
  // -------------------------------------------------------------------------
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    if (layersRef.current.realEvidence) {
      map.removeLayer(layersRef.current.realEvidence);
      layersRef.current.realEvidence = null;
    }

    if (!showEvidenceLayer || !realEvidenceData || selectedRealMineId !== 'MOIL_BALAGHAT') {
      return;
    }

    const markers = [];
    realEvidenceData.features.forEach((feat) => {
      const [lon, lat] = feat.geometry.coordinates;
      const p = feat.properties;
      const isShaftAnchor = p.evidence_id === 'EVID_MOIL_BALAGHAT_BHARWELI_01';
      const isOutcrop = p.evidence_id === 'EVID_GSI_BHARWELI_OUTCROP_02';

      const customIcon = L.divIcon({
        className: 'custom-evidence-icon',
        html: `
          <div style="
            background: ${isShaftAnchor ? '#fbbf24' : isOutcrop ? '#f97316' : '#38bdf8'};
            border: 2px solid #ffffff;
            box-shadow: 0 0 ${isShaftAnchor ? '14px #fbbf24' : '8px #f97316'};
            width: ${isShaftAnchor ? 22 : 16}px;
            height: ${isShaftAnchor ? 22 : 16}px;
            border-radius: ${isShaftAnchor ? '3px' : '50%'};
            transform: translate(-50%, -50%) ${isShaftAnchor ? 'rotate(45deg)' : ''};
            display: flex;
            align-items: center;
            justify-content: center;
          ">
            <div style="background: #0f172a; width: ${isShaftAnchor ? 8 : 6}px; height: ${isShaftAnchor ? 8 : 6}px; border-radius: 50%;"></div>
          </div>
        `,
        iconSize: [22, 22],
      });

      const marker = L.marker([lat, lon], { icon: customIcon, zIndexOffset: isShaftAnchor ? 1000 : 500 });

      marker.bindPopup(`
        <div class="p-2 text-xs font-sans max-w-xs">
          <div class="flex items-center gap-1.5 mb-1.5">
            <span class="px-1.5 py-0.5 rounded ${isShaftAnchor ? 'bg-amber-950 border border-amber-500 text-amber-300' : 'bg-indigo-950 border border-indigo-500 text-indigo-300'} font-bold text-[10px]">
              ${isShaftAnchor ? 'PRIMARY POSITIVE ANCHOR' : 'AUTHORITATIVE EVIDENCE'}
            </span>
            <span class="text-slate-400 text-[10px] font-mono">${p.evidence_id}</span>
          </div>
          <div class="font-bold text-sm text-amber-400 mb-1">${p.mine_or_occurrence_name}</div>
          <div><strong>Evidence Type:</strong> ${p.evidence_type}</div>
          <div><strong>Source Organization:</strong> ${p.source_organization}</div>
          <div><strong>Source Reference:</strong> ${p.source_title}</div>
          <div><strong>Coordinates:</strong> ${lat.toFixed(4)}°N, ${lon.toFixed(4)}°E (${p.coordinate_precision})</div>
          <div><strong>Role in Phase 9B:</strong> <span class="text-emerald-400 font-semibold">${p.role_in_experiment}</span></div>
          <div class="mt-2 pt-1.5 border-t border-slate-700 text-slate-400 text-[10px] leading-relaxed">
            ${p.scientific_caveat}
          </div>
        </div>
      `);

      marker.on('click', () => {
        setSelectedEntity({ type: 'evidence', data: p });
      });

      markers.push(marker);
    });

    const evidenceGroup = L.layerGroup(markers).addTo(map);
    layersRef.current.realEvidence = evidenceGroup;
  }, [realEvidenceData, showEvidenceLayer, selectedRealMineId]);

  // -------------------------------------------------------------------------
  // Render MOIL 10-Mines Markers (Global Central India Belt)
  // -------------------------------------------------------------------------
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map || !realMines || realMines.length === 0) return;

    if (layersRef.current.realMines) {
      map.removeLayer(layersRef.current.realMines);
    }

    if (!showRealMines) return;

    const markers = [];
    realMines.forEach((mine) => {
      if (!mine.latitude || !mine.longitude) return;

      const isSelected = mine.mine_id === selectedRealMineId;
      const isBalaghat = mine.mine_id === 'MOIL_BALAGHAT';
      const qColor = getCoordinateQualityColor(mine.coordinate_precision || mine.verification_status);

      const customIcon = L.divIcon({
        className: 'custom-real-mine-icon',
        html: `
          <div style="
            background: ${isSelected ? '#f59e0b' : qColor};
            border: 2px solid #ffffff;
            box-shadow: 0 0 ${isSelected ? '14px #f59e0b' : '8px ' + qColor};
            width: ${isSelected ? 22 : 16}px;
            height: ${isSelected ? 22 : 16}px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            transform: translate(-50%, -50%);
            transition: all 0.2s ease;
          ">
            <div style="background: #0f172a; width: 6px; height: 6px; border-radius: 50%;"></div>
          </div>
        `,
        iconSize: [22, 22],
      });

      const marker = L.marker([mine.latitude, mine.longitude], {
        icon: customIcon,
        zIndexOffset: isSelected ? 1200 : 800
      });

      marker.bindPopup(`
        <div class="p-2 text-xs font-sans max-w-xs">
          <div class="flex items-center justify-between gap-1.5 mb-1.5">
            <span class="px-1.5 py-0.5 rounded bg-emerald-950/80 border border-emerald-500/60 text-emerald-400 font-bold text-[10px]">
              MOIL STATUTORY MINE
            </span>
            <span class="text-slate-400 text-[10px] font-mono">${mine.mine_id}</span>
          </div>
          <div class="font-bold text-sm text-amber-400 mb-1">${mine.mine_name} Mine</div>
          <div><strong>State / District:</strong> ${mine.state}${mine.district ? `, ${mine.district}` : ''}</div>
          <div><strong>Coordinates:</strong> ${mine.latitude.toFixed(4)}°N, ${mine.longitude.toFixed(4)}°E</div>
          <div><strong>Coordinate Precision:</strong> <span class="text-emerald-400 font-semibold">${mine.coordinate_precision || 'Mine site point'}</span></div>
          <div><strong>Verification:</strong> <span class="text-indigo-300 font-mono text-[10px]">${mine.verification_status}</span></div>
          <div class="mt-1.5 pt-1.5 border-t border-slate-700 text-slate-300 text-[10px] leading-relaxed">
            <strong>Source:</strong> ${mine.source_title || 'MOIL Statutory Filings'}
          </div>
          ${isBalaghat
            ? '<div class="mt-2 p-1.5 rounded bg-red-950/60 border border-red-800/60 text-red-300 font-semibold text-[10px]">★ Phase 9B Real Exploration Priority Grid Active (27,720 cells)</div>'
            : '<div class="mt-2 text-slate-400 italic text-[10px]">Real exploration experiment not yet available for this mine.</div>'
          }
          <div class="mt-2 pt-1 border-t border-slate-800 text-center">
            <span class="text-[10px] text-amber-400 font-semibold">Click to focus on this mine</span>
          </div>
        </div>
      `);

      marker.on('click', () => {
        handleSelectRealMine(mine.mine_id);
      });

      markers.push(marker);
    });

    const realMineGroup = L.layerGroup(markers).addTo(map);
    layersRef.current.realMines = realMineGroup;
  }, [realMines, showRealMines, selectedRealMineId]);

  // Render Synthetic Mine Blocks Polygons (TATTVA Operational Simulation)
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
        layer.bindTooltip(`<strong>${p.name}</strong><br/>Target: ${p.target_monthly_tonnes} t/mo (Simulation)`, {
          className: 'leaflet-tooltip-dark',
        });
        layer.on('click', () => {
          setSelectedEntity({ type: 'block', data: p });
        });
      },
    }).addTo(map);

    layersRef.current.blocks = blocksLayer;
  }, [blocksGeoJson, selectedBlock]);

  // Render Synthetic Prospectivity Heatmap
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
              <div class="font-bold text-sm text-purple-400 mb-1">TATTVA Operational Simulation Cell</div>
              <div><strong>Grid ID:</strong> ${p.grid_id}</div>
              <div><strong>Simulated Probability:</strong> ${(p.prospectivity_prob * 100).toFixed(1)}%</div>
              <div><strong>Model Uncertainty:</strong> ${(p.uncertainty * 100).toFixed(1)}%</div>
              <div><strong>Classification:</strong> ${p.prospectivity_class}</div>
            </div>
          `);
        },
      }
    ).addTo(map);

    layersRef.current.prospectivity = prospectivityLayer;
  }, [prospectivityGeoJson, probCutoff, showHeatmap]);

  // Render Synthetic Drillholes
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
          <div><strong>Host Lithology:</strong> <span class="text-amber-300 font-mono">${p.lithology_code}</span></div>
          <div class="text-[10px] text-slate-400 mt-1 italic">TATTVA Operational Simulation</div>
        </div>
      `);

      markers.push(marker);
    });

    const dhLayerGroup = L.layerGroup(markers).addTo(map);
    layersRef.current.drillholes = dhLayerGroup;
  }, [drillholesGeoJson, showDrillholes]);

  // Render Synthetic Equipment Fleet
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
        html: `<div style="background-color: ${eqColor}; width: 14px; height: 14px; border-radius: 3px; border: 2px solid white; box-shadow: 0 0 6px ${eqColor};"></div>`,
        iconSize: [14, 14],
      });

      const marker = L.marker([eq.lat, eq.lon], { icon: customIcon });
      marker.bindPopup(`
        <div class="p-1 text-xs">
          <div class="font-bold text-white">${eq.id} (${eq.type})</div>
          <div>Block: ${eq.block} | Status: <span style="color:${eqColor}">${eq.status}</span></div>
          <div class="text-[10px] text-slate-400 mt-1 italic">TATTVA Operational Simulation</div>
        </div>
      `);
      fleetMarkers.push(marker);
    });

    const fleetGroup = L.layerGroup(fleetMarkers).addTo(map);
    layersRef.current.equipment = fleetGroup;
  }, [equipmentList, showFleet]);

  const selectedMineObj = realMines.find((m) => m.mine_id === selectedRealMineId);
  const isBalaghatSelected = selectedRealMineId === 'MOIL_BALAGHAT';
  const activeModelConfig = REAL_PROSPECTIVITY_LAYERS.find((l) => l.id === activeScoreLayer) || REAL_PROSPECTIVITY_LAYERS[0];

  return (
    <div className="panel overflow-hidden flex flex-col h-[calc(100vh-170px)] min-h-[580px]">
      {/* Top Map Control Bar */}
      <div className="bg-[#0a0d14] border-b border-technical px-3 py-1.5 flex flex-wrap items-center justify-between gap-2 text-xs">
        {/* Left: Mine Selector & View Mode */}
        <div className="flex items-center flex-wrap gap-2">
          {/* State-Grouped Mine Selector */}
          <div className="flex items-center gap-1.5 bg-[#0f141f] px-2.5 py-1 rounded border border-technical">
            <span className="text-slate-400 font-mono text-[11px]">MINE:</span>
            <select
              value={selectedRealMineId}
              onChange={(e) => handleSelectRealMine(e.target.value)}
              className="bg-transparent text-industrial-amber font-mono font-bold text-xs focus:outline-none cursor-pointer"
            >
              {Object.keys(minesByState).length > 0 ? (
                Object.entries(minesByState).map(([stateName, minesList]) => (
                  <optgroup key={stateName} label={stateName} className="bg-[#0a0d14] text-slate-400 font-bold">
                    {minesList.map((m) => (
                      <option key={m.mine_id} value={m.mine_id} className="bg-[#0a0d14] text-slate-100">
                        {m.mine_name} {m.mine_id === 'MOIL_BALAGHAT' ? '★ (Exploration AOI)' : ''}
                      </option>
                    ))}
                  </optgroup>
                ))
              ) : (
                <option value="MOIL_BALAGHAT">Balaghat (Madhya Pradesh)</option>
              )}
            </select>
          </div>

          {/* View Mode Switcher */}
          <div className="flex items-center bg-[#07090d] p-0.5 rounded border border-technical">
            <button
              onClick={() => {
                setMapViewMode('mine_detail');
                if (selectedMineObj && mapInstanceRef.current) {
                  mapInstanceRef.current.flyTo([selectedMineObj.latitude, selectedMineObj.longitude], isBalaghatSelected ? 14 : 13, { duration: 1 });
                }
              }}
              className={`px-2 py-0.5 rounded text-[11px] font-mono transition-colors ${
                mapViewMode === 'mine_detail'
                  ? 'bg-industrial-amber text-black font-bold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Mine View
            </button>
            <button
              onClick={handleFitGlobalBelt}
              className={`px-2 py-0.5 rounded text-[11px] font-mono transition-colors ${
                mapViewMode === 'global_belt'
                  ? 'bg-industrial-amber text-black font-bold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Belt View
            </button>
          </div>
        </div>

        {/* Right: Layer Toggles & Basemap Selector */}
        <div className="flex flex-wrap items-center gap-1.5 font-mono text-[11px]">
          <BasemapSelector
            currentBasemap={currentBasemap}
            onSelectBasemap={setCurrentBasemap}
          />

          {/* Toggle: Exploration (30m Grid) */}
          <button
            onClick={() => setShowRealProspectivity(!showRealProspectivity)}
            disabled={!isBalaghatSelected}
            className={`px-2 py-1 rounded border transition-colors cursor-pointer ${
              !isBalaghatSelected
                ? 'opacity-30 cursor-not-allowed bg-[#0b0e14] border-technical text-slate-600'
                : showRealProspectivity
                ? 'bg-[#1a1212] border-rose-900 text-rose-300'
                : 'bg-[#0b0e14] border-technical text-slate-400 hover:text-slate-200'
            }`}
          >
            Exploration (30m)
          </button>

          {/* Toggle: Site Anchors */}
          <button
            onClick={() => setShowEvidenceLayer(!showEvidenceLayer)}
            disabled={!isBalaghatSelected}
            className={`px-2 py-1 rounded border transition-colors cursor-pointer ${
              !isBalaghatSelected
                ? 'opacity-30 cursor-not-allowed bg-[#0b0e14] border-technical text-slate-600'
                : showEvidenceLayer
                ? 'bg-[#1a1710] border-amber-900 text-amber-300'
                : 'bg-[#0b0e14] border-technical text-slate-400 hover:text-slate-200'
            }`}
          >
            Site Anchors
          </button>

          {/* Toggle: 10-Mines */}
          <button
            onClick={() => setShowRealMines(!showRealMines)}
            className={`px-2 py-1 rounded border transition-colors cursor-pointer ${
              showRealMines
                ? 'bg-[#101720] border-cyan-900 text-cyan-300'
                : 'bg-[#0b0e14] border-technical text-slate-400 hover:text-slate-200'
            }`}
          >
            10 Mines
          </button>

          {/* Mine Overview Drawer Toggle */}
          <button
            onClick={() => setShowOverviewCard(!showOverviewCard)}
            className={`px-2 py-1 rounded border transition-colors cursor-pointer ${
              showOverviewCard
                ? 'bg-[#161c28] border-slate-600 text-white'
                : 'bg-[#0b0e14] border-technical text-slate-400 hover:text-slate-200'
            }`}
          >
            Overview
          </button>
        </div>
      </div>

      {/* Real Exploration Sub-Bar (Active for Balaghat) */}
      {isBalaghatSelected ? (
        <div className="bg-slate-950 border-b border-red-950/60 px-3 py-1 flex flex-wrap items-center justify-between gap-2 text-xs text-slate-300">
          {/* Left: Model Dimension Tabs */}
          <div className="flex items-center flex-wrap gap-1.5">
            <span className="text-[10px] font-bold text-slate-400 flex items-center gap-1 uppercase tracking-wider font-mono">
              <Target className="w-3 h-3 text-red-400" />
              Layer:
            </span>

            {REAL_PROSPECTIVITY_LAYERS.map((layer) => {
              const isActive = activeScoreLayer === layer.id;
              return (
                <button
                  key={layer.id}
                  onClick={() => setActiveScoreLayer(layer.id)}
                  className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold transition-all border ${
                    isActive
                      ? 'bg-red-950/90 border-red-500 text-white shadow-md shadow-red-950/40'
                      : 'bg-slate-900 border-technical text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                  }`}
                  title={layer.description}
                >
                  {layer.shortName}
                </button>
              );
            })}
          </div>

          {/* Right: Score Cutoff Filter & Metadata Drawer Toggle */}
          <div className="flex items-center flex-wrap gap-2">
            {/* Cutoff Slider */}
            <div className="flex items-center gap-1.5 bg-slate-900 px-2 py-0.5 rounded border border-technical">
              <Sliders className="w-3 h-3 text-red-400" />
              <span className="text-slate-300 font-medium text-[11px]">Cutoff:</span>
              <input
                type="range"
                min="0.00"
                max="0.90"
                step="0.05"
                value={realScoreCutoff}
                onChange={(e) => setRealScoreCutoff(parseFloat(e.target.value))}
                className="w-20 accent-red-500 cursor-pointer"
              />
              <span className="font-mono text-red-300 font-bold w-10 text-right">
                {realScoreCutoff > 0 ? `≥ ${realScoreCutoff.toFixed(2)}` : 'ALL'}
              </span>
            </div>

            {/* Scientific Limitations & Provenance Drawer Toggle */}
            <button
              onClick={() => setShowLimitationsDrawer(!showLimitationsDrawer)}
              className="flex items-center gap-1.5 px-2.5 py-1 bg-slate-900 hover:bg-slate-800 rounded-lg border border-slate-700 text-amber-300 text-[11px] font-medium transition-all"
            >
              <FileText className="w-3.5 h-3.5 text-amber-400" />
              <span>Methodology & Limitations</span>
              <ChevronDown className={`w-3 h-3 transition-transform ${showLimitationsDrawer ? 'rotate-180' : ''}`} />
            </button>
          </div>
        </div>
      ) : (
        /* Non-Balaghat Status Banner */
        <div className="bg-slate-950 border-b border-slate-800 px-4 py-1.5 flex items-center justify-between text-xs text-slate-400">
          <div className="flex items-center gap-2">
            <Info className="w-3.5 h-3.5 text-slate-500" />
            <span>Real exploration-priority experiment is currently available only for <strong className="text-slate-300">{selectedMineObj?.mine_name || 'Balaghat'}</strong>.</span>
          </div>
          <span className="text-[10px] text-slate-500 italic">Data Availability Status: Statutory Registry Active (10 MOIL Mines)</span>
        </div>
      )}

      {/* Expandable Scientific Limitations & Provenance Drawer */}
      {showLimitationsDrawer && realProspectivityMeta && (
        <div className="bg-slate-900/98 border-b border-amber-900/50 p-4 text-xs text-slate-300 animate-in fade-in duration-200">
          <div className="flex items-start justify-between gap-4 mb-3">
            <div>
              <div className="font-bold text-white text-sm flex items-center gap-2 mb-1">
                <ShieldCheck className="w-4 h-4 text-amber-400" />
                <span>Phase 9B Real-Data Prospectivity Experiment — Scientific Governance</span>
                <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-700 text-[10px] font-mono font-bold">
                  DERIVED FROM REAL DATA
                </span>
              </div>
              <p className="text-slate-400 text-[11px] leading-relaxed">
                27,720 real 30m Sentinel-2 & DEM cells covering the Balaghat mining lease AOI (5.03 km × 4.96 km).
                Prioritizes candidate exploration targets through unsupervised anomaly detection and positive-anchor similarity.
              </p>
            </div>
            <button
              onClick={() => setShowLimitationsDrawer(false)}
              className="text-slate-400 hover:text-white text-xs px-2 py-1 rounded bg-slate-800 border border-slate-700"
            >
              Close
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Left: Scientific Limitations */}
            <div className="p-3 rounded-lg bg-slate-950/80 border border-amber-900/40">
              <div className="font-bold text-amber-300 mb-2 flex items-center gap-1.5 text-[11px] uppercase tracking-wide">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                Critical Scientific Limitations
              </div>
              <ul className="space-y-1.5 text-[11px] text-slate-300 list-disc list-inside leading-relaxed">
                <li><strong>No Confirmed Negative Labels:</strong> In mineral exploration, negative labels require published barren drillhole assay logs, which are not public. Background is strictly unlabeled.</li>
                <li><strong>Single Positive Spatial Anchor:</strong> Only ONE verified spatial positive deposit anchor exists inside the AOI (Bharweli shaft portal, <code>GRID-13860</code>).</li>
                <li><strong>Heuristic Ranking, Not Probability:</strong> Exploration priority is a multi-method ranking heuristic. It is NOT a calibrated probability of manganese mineralization.</li>
                <li><strong>Shaft Proximity ≠ Orebody Extent:</strong> Surface shaft coordinates reflect infrastructure portals, not subsurface orebody geometry.</li>
                <li><strong>Requires Ground Validation:</strong> Spectral and terrain anomalies require field geological mapping and drilling before reserve estimation.</li>
              </ul>
            </div>

            {/* Right: Data Provenance & Anchor Role */}
            <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800">
              <div className="font-bold text-indigo-300 mb-2 flex items-center gap-1.5 text-[11px] uppercase tracking-wide">
                <Database className="w-3.5 h-3.5 text-indigo-400" />
                Data Provenance & Anchor Role
              </div>
              <div className="space-y-2 text-[11px] text-slate-300">
                <div>
                  <strong>Remote Sensing:</strong> Sentinel-2A Level-2A (B02-B12, NDVI, NDWI, band ratios; 2024-04-17).
                </div>
                <div>
                  <strong>Terrain Topography:</strong> Copernicus DEM GLO-30 (Elevation, slope, cyclic aspect sin/cos, hillshade; 30m).
                </div>
                <div>
                  <strong>Positive Anchor Interpretation:</strong> The Bharweli haulage portal (<code>GRID-13860</code>) receives Anchor Similarity = 1.000 by mathematical construction as the reference vector, not as independent model validation.
                </div>
                <div>
                  <strong>Sensitivity Analysis:</strong> 35 proximal pit cells evaluated under Configuration B show 97.2% rank correlation with single-anchor results.
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Map Canvas & Overlay Panels */}
      <div className="relative flex-1 w-full bg-slate-950">
        <div ref={mapContainerRef} className="w-full h-full" />

        {/* Loading Spinner Overlay */}
        {isLoadingProspectivity && (
          <div className="absolute inset-0 bg-slate-950/60 backdrop-blur-sm z-[1500] flex items-center justify-center">
            <div className="flex flex-col items-center gap-2 p-4 rounded-xl bg-slate-900 border border-slate-700 shadow-2xl">
              <div className="w-6 h-6 border-2 border-red-500 border-t-transparent rounded-full animate-spin"></div>
              <span className="text-xs font-semibold text-white">Loading Real Prospectivity Grid (27,720 cells)...</span>
            </div>
          </div>
        )}

        {/* Floating Basemap Selector (Top-Right Map Overlay) */}
        <div className="absolute top-3 right-3 z-[1000] pointer-events-auto">
          <BasemapSelector
            currentBasemap={currentBasemap}
            onSelectBasemap={setCurrentBasemap}
            variant="pills"
          />
        </div>

        {/* MINE OVERVIEW & DATA AVAILABILITY STATUS PANEL (Top-Left / Floating) */}
        {showOverviewCard && mineDashboard && (
          <div className="absolute top-3 left-3 bg-[#07090d]/95 backdrop-blur-md border border-technical p-4 rounded shadow-2xl text-xs z-[1000] max-w-sm pointer-events-auto animate-in fade-in duration-200">
            {/* Header */}
            <div className="flex items-center justify-between pb-2 mb-2 border-b border-technical">
              <div>
                <div className="flex items-center gap-1.5">
                  <h3 className="font-bold uppercase font-condensed tracking-wider text-white text-base">{mineDashboard.mine_name} Mine</h3>
                  <span className="text-[10px] px-1.5 py-0.2 rounded bg-[#101726] text-industrial-amber border border-technical font-mono">
                    {mineDashboard.mine_id}
                  </span>
                </div>
                <div className="text-[11px] font-mono text-slate-400">
                  {mineDashboard.district ? `${mineDashboard.district}, ` : ''}{mineDashboard.state} · {mineDashboard.mineral}
                </div>
              </div>
              <button
                onClick={() => setShowOverviewCard(false)}
                className="text-slate-400 hover:text-white p-1 rounded hover:bg-slate-800"
                title="Hide Overview"
              >
                ✕
              </button>
            </div>

            {/* Mine Coordinates & Precision */}
            <div className="space-y-1 text-[11px] text-slate-300 mb-3 p-2.5 rounded bg-[#0b0f17] border border-technical font-mono">
              <div className="flex justify-between">
                <span className="text-slate-500">COORDINATES:</span>
                <span className="text-industrial-amber font-bold">{mineDashboard.latitude?.toFixed(4)}°N, {mineDashboard.longitude?.toFixed(4)}°E</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">PRECISION:</span>
                <span className="text-emerald-400 font-bold">{mineDashboard.coordinate_precision}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">VERIFICATION:</span>
                <span className="text-slate-300">{mineDashboard.verification_status}</span>
              </div>
            </div>

            {/* 5-Category Data Availability Framework */}
            <div className="mb-2.5 space-y-1.5">
              <div className="font-bold font-condensed text-slate-300 text-xs uppercase tracking-widest flex items-center gap-1">
                <Layers className="w-3.5 h-3.5 text-industrial-amber" />
                <span>Data Availability Framework</span>
              </div>

              <div className="space-y-1 text-[10px] font-mono">
                {/* 1. Real Data */}
                <div className="flex items-center justify-between p-1.5 rounded bg-[#0b0f17] border border-technical">
                  <span className="text-slate-300">Satellite Multispectral & DEM</span>
                  <span className={`px-1.5 py-0.2 rounded font-bold uppercase ${
                    mineDashboard.exploration_available
                      ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-800'
                      : 'bg-slate-900 text-slate-500 border border-slate-800'
                  }`}>
                    {mineDashboard.exploration_available ? 'REAL DATA' : 'UNAVAILABLE'}
                  </span>
                </div>

                {/* 2. Reported Data */}
                <div className="flex items-center justify-between p-1.5 rounded bg-[#0b0f17] border border-technical">
                  <span className="text-slate-300">MOIL Statutory Production</span>
                  <span className="px-1.5 py-0.2 rounded bg-amber-950/80 text-amber-300 border border-amber-800 font-bold uppercase">
                    REPORTED DATA
                  </span>
                </div>

                {/* 3. Experimental */}
                <div className="flex items-center justify-between p-1.5 rounded bg-[#0b0f17] border border-technical">
                  <span className="text-slate-300">Exploration Priority (30m)</span>
                  <span className={`px-1.5 py-0.2 rounded font-bold uppercase ${
                    mineDashboard.exploration_available
                      ? 'bg-rose-950/80 text-rose-300 border border-rose-800'
                      : 'bg-slate-900 text-slate-500 border border-slate-800'
                  }`}>
                    {mineDashboard.exploration_available ? 'EXPERIMENTAL' : 'UNAVAILABLE'}
                  </span>
                </div>

                {/* 4. Simulation */}
                <div className="flex items-center justify-between p-1.5 rounded bg-[#0b0f17] border border-technical">
                  <span className="text-slate-300">TATTVA Operational Sim</span>
                  <span className="px-1.5 py-0.2 rounded bg-purple-950/80 text-purple-300 border border-purple-800 font-bold uppercase">
                    SIMULATION
                  </span>
                </div>

                {/* 5. Unavailable */}
                <div className="flex items-center justify-between p-1.5 rounded bg-[#0b0f17] border border-technical">
                  <span className="text-slate-500">Vector Geological Lithology</span>
                  <span className="px-1.5 py-0.2 rounded bg-slate-900 text-slate-500 border border-slate-800 font-bold uppercase">
                    UNAVAILABLE
                  </span>
                </div>
              </div>
            </div>

            {/* Provenance Citation */}
            <div className="text-[10px] font-mono text-slate-500 pt-2 border-t border-technical">
              <strong>Source:</strong> {mineDashboard.source_title}
            </div>
          </div>
        )}

        {/* Global Sausar Belt Coordinate Quality Legend (Bottom-Left) */}
        {mapViewMode === 'global_belt' && (
          <div className="absolute bottom-4 left-4 bg-[#07090d]/95 backdrop-blur-md border border-technical p-3.5 rounded shadow-xl text-xs z-[1000] max-w-xs pointer-events-auto font-mono">
            <div className="font-bold text-white mb-1.5 flex items-center justify-between font-condensed text-sm uppercase">
              <span>MOIL 10-Mine Registry</span>
              <span className="text-[10px] text-emerald-400">Central India Belt</span>
            </div>
            <div className="space-y-1.5 text-slate-300 text-[11px]">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-emerald-500 border border-white"></span>
                <span>Surveyed / statutory point (~10-50m)</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-cyan-500 border border-white"></span>
                <span>Lease centroid (~500m)</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-amber-500 border border-white"></span>
                <span>Map-derived reference (~1-2km)</span>
              </div>
            </div>
            <div className="mt-2 pt-1.5 border-t border-technical text-[10px] text-slate-500 leading-tight">
              Click any mine marker to focus and view Data Availability Framework.
            </div>
          </div>
        )}

        {/* Real Exploration Legend (Bottom-Left in Mine Detail View for Balaghat) */}
        {mapViewMode === 'mine_detail' && isBalaghatSelected && showRealProspectivity && (
          <div className="absolute bottom-4 left-4 bg-[#07090d]/95 backdrop-blur-md border border-technical p-3.5 rounded shadow-xl text-xs z-[1000] max-w-xs pointer-events-auto font-mono">
            <div className="font-bold text-white mb-1 flex items-center justify-between font-condensed text-sm uppercase">
              <span className="text-industrial-amber">{activeModelConfig.name}</span>
              <span className="text-[10px] text-slate-500">30m Cell</span>
            </div>

            {/* Gradient Colorbar */}
            <div className="my-2">
              <div
                className="h-2.5 w-full rounded-none border border-technical"
                style={{
                  background: activeScoreLayer === 'exploration_priority_score'
                    ? 'linear-gradient(to right, #334155 0%, #06b6d4 35%, #eab308 50%, #f97316 65%, #dc2626 100%)'
                    : activeScoreLayer === 'anomaly_score'
                    ? 'linear-gradient(to right, #1e293b 0%, #3b82f6 30%, #a855f7 60%, #ec4899 100%)'
                    : activeScoreLayer === 'robust_distance_score'
                    ? 'linear-gradient(to right, #0f172a 0%, #0284c7 20%, #fb923c 50%, #f43f5e 100%)'
                    : 'linear-gradient(to right, #1e293b 0%, #0284c7 40%, #14b8a6 70%, #10b981 100%)'
                }}
              />
              <div className="flex justify-between text-[10px] text-slate-500 mt-1">
                <span>0.0 (Low Target)</span>
                <span>0.50</span>
                <span>1.0 (High Target)</span>
              </div>
            </div>

            {/* Legend Indicators */}
            <div className="space-y-1.5 text-slate-300 text-[11px] pt-1 border-t border-technical">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-none bg-red-600 border border-white/40"></span>
                <span>High Exploration Priority (&ge;0.80)</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 bg-amber-400 rotate-45 border border-white"></span>
                <span className="font-bold text-amber-300">Bharweli Shaft Portal (Anchor)</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-orange-500 border border-white"></span>
                <span>Mansar Manganese Reef Outcrop</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-0.5 bg-indigo-400"></span>
                <span className="text-slate-500 text-[10px]">India Boundary (Survey of India)</span>
              </div>
            </div>

            {/* Mandatory Scientific Disclaimer */}
            <div className="mt-2 pt-2 border-t border-technical text-[10px] text-amber-300/90 font-medium leading-tight font-sans">
              ⚠️ Relative ranking heuristic, not probability. No independent negative drillholes available.
            </div>
          </div>
        )}

        {/* Selected Cell Inspection Card (Bottom-Right) */}
        {selectedEntity && selectedEntity.type === 'real_cell' && (
          <div className="absolute bottom-4 right-4 bg-[#07090d]/95 backdrop-blur-md border border-rose-800/80 p-3.5 rounded shadow-2xl text-xs z-[1000] max-w-sm pointer-events-auto animate-in slide-in-from-bottom-2 duration-200 font-mono">
            <div className="flex items-center justify-between pb-1.5 mb-2 border-b border-technical">
              <span className="font-bold uppercase font-condensed tracking-wider text-white text-sm flex items-center gap-1.5">
                <Target className="w-4 h-4 text-rose-400" />
                CELL: <span className="text-industrial-amber">{selectedEntity.data.cell_id}</span>
              </span>
              <button
                onClick={() => setSelectedEntity(null)}
                className="text-slate-400 hover:text-white p-0.5"
              >
                ✕
              </button>
            </div>

            <div className="grid grid-cols-2 gap-2 text-[11px] mb-2">
              <div className="p-2 rounded bg-[#0b0f17] border border-technical">
                <span className="text-slate-500 block text-[10px]">Exploration Priority:</span>
                <strong className="text-rose-400 text-sm">{selectedEntity.data.exploration_priority_score?.toFixed(3)}</strong>
              </div>
              <div className="p-2 rounded bg-[#0b0f17] border border-technical">
                <span className="text-slate-500 block text-[10px]">Anomaly Score:</span>
                <strong className="text-purple-400 text-sm">{selectedEntity.data.anomaly_score?.toFixed(3)}</strong>
              </div>
              <div className="p-2 rounded bg-[#0b0f17] border border-technical">
                <span className="text-slate-500 block text-[10px]">Robust Distance:</span>
                <strong className="text-amber-400 text-sm">{selectedEntity.data.robust_distance_score?.toFixed(3)}</strong>
              </div>
              <div className="p-2 rounded bg-[#0b0f17] border border-technical">
                <span className="text-slate-500 block text-[10px]">Anchor Similarity:</span>
                <strong className="text-emerald-400 text-sm">{selectedEntity.data.positive_anchor_similarity?.toFixed(3)}</strong>
              </div>
            </div>

            <div className="text-[11px] text-slate-300 leading-relaxed bg-[#0b0f17] p-2 rounded border border-technical font-sans">
              <strong>Interpretation:</strong> High relative exploration priority within Balaghat AOI based on combined anomaly, distance, and similarity ranking.
              <div className="mt-1 text-amber-300 font-medium">⚠️ Relative ranking heuristic, not probability. No independent negative drillholes available.</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
