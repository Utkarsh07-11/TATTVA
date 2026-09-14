import React, { createContext, useContext, useEffect, useMemo, useState, useCallback } from 'react';
import { api } from '../services/api';

import {
  getFallbackForecast,
  getFallbackMineOverview,
  getFallbackExplanation,
  getFallbackRecommendations,
  getFallbackEquipment,
  getFallbackMineBlocks,
  getFallbackDrillholes,
  getFallbackProspectivityMap,
} from '../services/fallbackData';

const DashboardContext = createContext(null);

export function DashboardProvider({ children }) {
  const [selectedBlock, setSelectedBlock] = useState('BLOCK_A');
  const [horizonDays, setHorizonDays] = useState(30);
  const [showWatermark, setShowWatermark] = useState(true);
  const [activePreset, setActivePreset] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [overview, setOverview] = useState(() => getFallbackMineOverview('BLOCK_A'));
  const [forecast, setForecast] = useState(() => getFallbackForecast('BLOCK_A', 30));
  const [explanation, setExplanation] = useState(() => getFallbackExplanation('BLOCK_A', 30));
  const [recommendations, setRecommendations] = useState(() => getFallbackRecommendations('BLOCK_A', 30));
  const [prospectivityGeoJson, setProspectivityGeoJson] = useState(() => getFallbackProspectivityMap());
  const [drillholesGeoJson, setDrillholesGeoJson] = useState(() => getFallbackDrillholes());
  const [blocksGeoJson, setBlocksGeoJson] = useState(() => getFallbackMineBlocks());
  const [equipmentList, setEquipmentList] = useState(() => getFallbackEquipment().fleet || []);

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
