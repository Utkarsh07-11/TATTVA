import React, { createContext, useContext, useEffect, useMemo, useState, useCallback } from 'react';
import { api } from '../services/api';

const DashboardContext = createContext(null);

export function DashboardProvider({ children }) {
  const [selectedBlock, setSelectedBlock] = useState('BLOCK_A');
  const [horizonDays, setHorizonDays] = useState(30);
  const [showWatermark, setShowWatermark] = useState(true);
  const [activePreset, setActivePreset] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [overview, setOverview] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [prospectivityGeoJson, setProspectivityGeoJson] = useState(null);
  const [drillholesGeoJson, setDrillholesGeoJson] = useState(null);
  const [blocksGeoJson, setBlocksGeoJson] = useState(null);
  const [equipmentList, setEquipmentList] = useState([]);

  const loadDashboardData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [
        overviewRes,
        forecastRes,
        explainRes,
        recommendRes,
        prospectRes,
        drillholesRes,
        blocksRes,
        equipmentRes,
      ] = await Promise.all([
        api.getMineOverview(selectedBlock),
        api.getForecast(selectedBlock, horizonDays),
        api.getShortfallExplanation(selectedBlock, horizonDays),
        api.getRecommendations(selectedBlock, horizonDays),
        api.getProspectivityMap(),
        api.getDrillholes(),
        api.getMineBlocks(),
        api.getEquipment(),
      ]);

      setOverview(overviewRes);
      setForecast(forecastRes);
      setExplanation(explainRes);
      setRecommendations(recommendRes);
      setProspectivityGeoJson(prospectRes);
      setDrillholesGeoJson(drillholesRes);
      setBlocksGeoJson(blocksRes);
      setEquipmentList(equipmentRes.fleet || []);
    } catch (err) {
      setError(err.message || 'Failed to connect to the inference server.');
    } finally {
      setLoading(false);
    }
  }, [selectedBlock, horizonDays]);

  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  const value = useMemo(
    () => ({
      selectedBlock,
      setSelectedBlock,
      horizonDays,
      setHorizonDays,
      showWatermark,
      setShowWatermark,
      activePreset,
      setActivePreset,
      loading,
      error,
      overview,
      forecast,
      explanation,
      recommendations,
      prospectivityGeoJson,
      drillholesGeoJson,
      blocksGeoJson,
      equipmentList,
      loadDashboardData,
    }),
    [
      selectedBlock,
      horizonDays,
      showWatermark,
      activePreset,
      loading,
      error,
      overview,
      forecast,
      explanation,
      recommendations,
      prospectivityGeoJson,
      drillholesGeoJson,
      blocksGeoJson,
      equipmentList,
      loadDashboardData,
    ]
  );

  return <DashboardContext.Provider value={value}>{children}</DashboardContext.Provider>;
}

export function useDashboard() {
  const ctx = useContext(DashboardContext);
  if (!ctx) throw new Error('useDashboard must be used within DashboardProvider');
  return ctx;
}
