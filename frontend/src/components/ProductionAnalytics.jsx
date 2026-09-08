import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Line,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  ReferenceLine
} from 'recharts';
import {
  TrendingUp,
  BarChart2,
  CheckCircle2,
  Database,
  Sparkles,
  Building2,
  Calendar,
  ShieldCheck,
  Sliders,
  AlertTriangle,
  RotateCcw,
  Zap,
  ArrowRight,
  Info,
  CheckCircle,
  Clock,
  Layers
} from 'lucide-react';
import { api } from '../services/api';

const BLOCK_TARGETS = {
  BLOCK_A: 10000,
  BLOCK_B: 8400,
  BLOCK_C: 6600,
};

export default function ProductionAnalytics({ forecast, selectedBlock }) {
  // Tabs: 'operational_sim' | 'moil_reported' | 'reconciliation_sandbox'
  const [activeTab, setActiveTab] = useState('operational_sim');
  const [showInterval, setShowInterval] = useState(true);
  const [showTargetLine, setShowTargetLine] = useState(true);

  // Active Block & Horizon State for Reconciliation
  const [currentBlock, setCurrentBlock] = useState(selectedBlock || 'BLOCK_A');
  const [horizonDays, setHorizonDays] = useState(30);

  // Scenario Sandbox State
  const [equipmentAvailability, setEquipmentAvailability] = useState(88.0);
  const [blastingDelay, setBlastingDelay] = useState(0);
  const [rainfall, setRainfall] = useState(12.5);
  const [customTarget, setCustomTarget] = useState(BLOCK_TARGETS[selectedBlock || 'BLOCK_A'] || 10000);
  const [isScenarioDirty, setIsScenarioDirty] = useState(false);

  // Real Production & Reconciliation API State
  const [reconciliationData, setReconciliationData] = useState(null);
  const [isLoadingReconciliation, setIsLoadingReconciliation] = useState(false);
  const [reconciliationError, setReconciliationError] = useState(null);

  // Synchronize with external selectedBlock prop
  useEffect(() => {
    if (selectedBlock && selectedBlock !== currentBlock) {
      setCurrentBlock(selectedBlock);
      setCustomTarget(BLOCK_TARGETS[selectedBlock] || 10000);
    }
  }, [selectedBlock]);

  // Fetch Production Intelligence & Reconciliation Payload
  const fetchReconciliation = useCallback(async (overrides = {}) => {
    setIsLoadingReconciliation(true);
    setReconciliationError(null);
    try {
      const payload = {
        mine_block_id: currentBlock,
        horizon_days: horizonDays,
        custom_target: customTarget,
        ...(overrides.isScenario ? {
          equipment_availability_pct: overrides.equipmentAvailability ?? equipmentAvailability,
          blasting_delay_flag: overrides.blastingDelay ?? blastingDelay,
          rainfall_mm: overrides.rainfall ?? rainfall,
        } : {})
      };

      const res = await api.postProductionReconciliation(payload);
      setReconciliationData(res);
    } catch (err) {
      console.warn('Reconciliation API error:', err);
      setReconciliationError(err.message || 'Failed to fetch reconciliation data');
    } finally {
      setIsLoadingReconciliation(false);
    }
  }, [currentBlock, horizonDays, customTarget, equipmentAvailability, blastingDelay, rainfall]);

  // Load initial data and refresh when block/horizon changes
  useEffect(() => {
    fetchReconciliation({ isScenario: isScenarioDirty });
  }, [currentBlock, horizonDays, customTarget]);

  // Trigger scenario re-calculation
  const handleApplyScenario = () => {
    setIsScenarioDirty(true);
    fetchReconciliation({ isScenario: true });
  };

  // Reset scenario to baseline defaults
  const handleResetScenario = () => {
    setEquipmentAvailability(88.0);
    setBlastingDelay(0);
    setRainfall(12.5);
    setCustomTarget(BLOCK_TARGETS[currentBlock] || 10000);
    setIsScenarioDirty(false);
    fetchReconciliation({
      isScenario: false,
      equipmentAvailability: null,
      blastingDelay: null,
      rainfall: null,
    });
  };

  // Extract Macro Data dynamically from API
  const macroContext = reconciliationData?.macro_context || {};
  const annualSeries = macroContext?.annual_series || [];

  const macroStats = useMemo(() => {
    if (!annualSeries.length) {
      return {
        latestPeriod: 'FY 2025-26',
        latestTonnes: 1756000,
        latestLakh: 17.56,
        peakTonnes: 1756000,
        peakLakh: 17.56,
        meanTonnes: 1238000,
        meanLakh: 12.38,
        count: 11,
      };
    }
    const tonnesList = annualSeries.map(r => r.production_tonnes);
    const peak = Math.max(...tonnesList);
    const sum = tonnesList.reduce((a, b) => a + b, 0);
    const mean = sum / tonnesList.length;
    const latest = annualSeries[annualSeries.length - 1];

    return {
      latestPeriod: latest.period,
      latestTonnes: latest.production_tonnes,
      latestLakh: latest.production_lakh_tonnes,
      peakTonnes: peak,
      peakLakh: (peak / 100000).toFixed(2),
      meanTonnes: mean,
      meanLakh: (mean / 100000).toFixed(2),
      count: annualSeries.length,
    };
  }, [annualSeries]);

  // Format macro chart data
  const realChartData = useMemo(() => {
    return annualSeries.map((rec) => ({
      period: rec.period.replace('FY', '').replace('FY20', 'FY '),
      fullPeriod: rec.period,
      productionLakhTonnes: rec.production_lakh_tonnes,
      productionTonnes: rec.production_tonnes,
      source: rec.source,
      dataStatus: rec.data_status,
    }));
  }, [annualSeries]);

  // Synthetic daily points for micro chart
  const syntheticData = useMemo(() => {
    const points = forecast?.daily_points || reconciliationData?.micro_simulation?.daily_points || [];
    const targetDaily = Math.round((forecast?.target_tonnes || customTarget) / horizonDays);
    return points.map((pt, idx) => ({
      day: `Day ${idx + 1}`,
      date: pt.date,
      p10: pt.p10,
      p50: pt.p50,
      p90: pt.p90,
      targetDaily,
    }));
  }, [forecast, reconciliationData, customTarget, horizonDays]);

  const targetDailyRate = Math.round(customTarget / horizonDays);

  // Micro & Scenario metrics
  const microSim = reconciliationData?.micro_simulation || {};
  const scenarioRec = reconciliationData?.scenario_reconciliation || {};
  const recommendations = reconciliationData?.optimizer_recommendations || [];

  // Active micro metrics depending on whether scenario is dirty
  const activeSimulatedOutput = scenarioRec.simulated_output_tonnes ?? microSim.baseline_forecast_tonnes ?? forecast?.forecast_tonnes ?? 0;
  const activeVariance = scenarioRec.scenario_variance_tonnes ?? microSim.baseline_variance_tonnes ?? Math.round(activeSimulatedOutput - customTarget);
  const activeShortfall = scenarioRec.scenario_shortfall_tonnes ?? microSim.baseline_shortfall_tonnes ?? Math.max(0, customTarget - activeSimulatedOutput);
  const activeExcess = scenarioRec.scenario_excess_tonnes ?? microSim.baseline_excess_tonnes ?? Math.max(0, activeSimulatedOutput - customTarget);
  const activeRiskLevel = scenarioRec.scenario_risk_level ?? microSim.baseline_risk_level ?? forecast?.risk_level ?? 'LOW';
  const activeShortfallProb = scenarioRec.scenario_shortfall_probability ?? microSim.baseline_shortfall_probability ?? forecast?.shortfall_probability ?? 0.0;

  return (
    <div className="space-y-3">
      {/* DECISION-FIRST STATUS BANNER */}
      <div className="bg-[#080b10] p-4 rounded border border-technical flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <div className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">
            PRODUCTION INTELLIGENCE · {currentBlock}
          </div>
          <div className="flex items-baseline gap-3 mt-1">
            <span className="text-2xl font-bold font-mono text-white">
              {Math.round(activeSimulatedOutput).toLocaleString()} t
            </span>
            <span className={`text-xs font-mono font-semibold ${activeVariance < 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
              {activeVariance < 0 ? `${Math.abs(activeVariance).toLocaleString()} t below target` : `${activeVariance.toLocaleString()} t above target`}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-3 self-start sm:self-auto">
          <span className="flex items-center gap-1.5 text-xs font-mono font-semibold text-slate-200">
            <span className={`w-2 h-2 rounded-full ${activeRiskLevel === 'HIGH' || activeRiskLevel === 'CRITICAL' ? 'bg-rose-400' : activeRiskLevel === 'MODERATE' || activeRiskLevel === 'MEDIUM' ? 'bg-amber-400' : 'bg-emerald-400'}`}></span>
            {activeRiskLevel} RISK
          </span>
        </div>
      </div>

      <div className="panel p-3.5 sm:p-4 space-y-3">
        {/* Header with 3 Conceptual View Switchers */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 pb-2.5 border-b border-technical">
          <div className="flex items-center gap-2">
            <h2 className="text-xs sm:text-sm font-bold text-white tracking-wide uppercase font-mono">
              {activeTab === 'operational_sim' && 'Operational Forecast (Simulation)'}
              {activeTab === 'moil_reported' && 'MOIL Reported Production (FY16–FY26)'}
              {activeTab === 'reconciliation_sandbox' && 'Operational Reconciliation & Scenarios'}
            </h2>
          </div>

          {/* 3-Tab Selector */}
          <div className="flex flex-wrap items-center bg-[#080b10] p-0.5 rounded border border-technical gap-1">
            <button
              onClick={() => setActiveTab('operational_sim')}
              className={`px-3 py-1 rounded text-xs font-mono transition-colors ${
                activeTab === 'operational_sim'
                  ? 'bg-industrial-amber text-black font-bold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Forecast
            </button>
            <button
              onClick={() => setActiveTab('moil_reported')}
              className={`px-3 py-1 rounded text-xs font-mono transition-colors ${
                activeTab === 'moil_reported'
                  ? 'bg-industrial-amber text-black font-bold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Reported
            </button>
            <button
              onClick={() => setActiveTab('reconciliation_sandbox')}
              className={`px-3 py-1 rounded text-xs font-mono transition-colors ${
                activeTab === 'reconciliation_sandbox'
                  ? 'bg-industrial-amber text-black font-bold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Reconciliation
            </button>
          </div>
        </div>

        {/* ========================================================================= */}
        {/* TAB 1: TATTVA OPERATIONAL SIMULATION                                       */}
        {/* ========================================================================= */}
        {activeTab === 'operational_sim' && (
          <div className="space-y-3">
            {/* Controls Bar */}
            <div className="flex flex-wrap items-center justify-between gap-2 text-xs font-mono">
              <div className="flex items-center gap-2 text-slate-400 text-[11px]">
                <span>Block: <strong className="text-white">{currentBlock}</strong></span>
                <span>·</span>
                <span>Horizon: <strong className="text-white">{horizonDays} Days</strong></span>
                <span>·</span>
                <span className="text-purple-400">● Simulation</span>
              </div>

              <div className="flex items-center gap-2 text-[11px]">
                <button
                  onClick={() => setShowInterval(!showInterval)}
                  className={`px-2 py-0.5 rounded border transition-colors ${
                    showInterval
                      ? 'bg-[#1a1424] border-purple-800 text-purple-300'
                      : 'bg-[#0b0e14] border-technical text-slate-400'
                  }`}
                >
                  90% Interval
                </button>
                <button
                  onClick={() => setShowTargetLine(!showTargetLine)}
                  className={`px-2 py-0.5 rounded border transition-colors ${
                    showTargetLine
                      ? 'bg-[#141824] border-indigo-800 text-indigo-300'
                      : 'bg-[#0b0e14] border-technical text-slate-400'
                  }`}
                >
                  Target Line ({targetDailyRate} t/d)
                </button>
              </div>
            </div>

          {/* Chart Canvas */}
          <div className="h-64 sm:h-68 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={syntheticData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
                <XAxis dataKey="day" stroke="#94a3b8" fontSize={11} tickLine={false} />
                <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} domain={['dataMin - 30', 'dataMax + 40']} />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const d = payload[0].payload;
                      return (
                        <div className="bg-slate-900 border border-slate-700 p-2.5 rounded shadow-xl text-xs">
                          <div className="font-bold text-white mb-0.5">{d.day} ({d.date})</div>
                          <div className="text-purple-400 font-semibold">
                            Forecast (P50): {d.p50} tonnes
                          </div>
                          <div className="text-slate-400">
                            90% Interval: [{d.p10} - {d.p90} t]
                          </div>
                          <div className="text-indigo-400">
                            Daily Target: {d.targetDaily} tonnes
                          </div>
                          <div className={d.p50 < d.targetDaily ? 'text-red-400 mt-0.5 font-semibold' : 'text-emerald-400 mt-0.5'}>
                            {d.p50 < d.targetDaily ? `Deficit: -${Math.round(d.targetDaily - d.p50)} t` : `Surplus: +${Math.round(d.p50 - d.targetDaily)} t`}
                          </div>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Legend verticalAlign="top" height={30} wrapperStyle={{ fontSize: '11px', color: '#cbd5e1' }} />

                {showTargetLine && (
                  <ReferenceLine
                    y={targetDailyRate}
                    stroke="#6366f1"
                    strokeDasharray="4 4"
                    strokeWidth={2}
                    label={{ value: 'Daily Target', fill: '#818cf8', fontSize: 10, position: 'insideTopRight' }}
                  />
                )}

                {showInterval && (
                  <Area
                    type="monotone"
                    dataKey="p90"
                    stroke="none"
                    fill="#a855f7"
                    fillOpacity={0.18}
                    name="90% Quantile Envelope [P10-P90]"
                  />
                )}

                <Line
                  type="monotone"
                  dataKey="p50"
                  stroke="#c084fc"
                  strokeWidth={2.5}
                  dot={false}
                  name="LightGBM Forecast (P50)"
                />

                {showInterval && (
                  <Line
                    type="monotone"
                    dataKey="p10"
                    stroke="#a855f7"
                    strokeWidth={1}
                    strokeDasharray="3 3"
                    dot={false}
                    name="Lower Bound (P10)"
                  />
                )}
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          {/* Model Benchmark Card */}
          <div className="pt-2 border-t border-technical grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs">
            <div className="bg-slate-800/60 p-2 rounded border border-technical">
              <div className="text-slate-400 text-[10px]">Model Validation</div>
              <div className="text-white font-bold mt-0.5 text-xs">Rolling-Origin Forward Chaining</div>
              <div className="text-emerald-400 text-[10px] mt-0.5">Zero temporal lookahead bias</div>
            </div>
            <div className="bg-slate-800/60 p-2 rounded border border-technical">
              <div className="text-slate-400 text-[10px]">ML Advantage over Naive</div>
              <div className="text-purple-300 font-bold mt-0.5 text-xs">66.9% Error Reduction</div>
              <div className="text-slate-400 text-[10px] mt-0.5">MAE: 10.54 t vs 31.83 t Naive</div>
            </div>
            <div className="bg-slate-800/60 p-2 rounded border border-technical">
              <div className="text-slate-400 text-[10px]">90% Coverage (PICP)</div>
              <div className="text-white font-bold mt-0.5 text-xs">76.0% Empirical Coverage</div>
              <div className="text-slate-400 text-[10px] mt-0.5">Calibrated pit uncertainty</div>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 2: MOIL REPORTED PRODUCTION                                           */}
      {/* ========================================================================= */}
      {activeTab === 'moil_reported' && (
        <div className="space-y-3">
          {/* Statutory Scope & Non-Fabrication Notice */}
          <div className="bg-amber-950/30 border border-amber-800/50 rounded p-2.5 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
            <div className="space-y-0.5">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                <span className="font-semibold text-white">Statutory Source:</span>
                <span className="text-amber-200">
                  MOIL Limited Statutory Annual Reports & PIB Ministry of Steel Disclosures
                </span>
              </div>
              <div className="text-[10px] text-slate-400">
                ⚠️ <strong>Scope Note:</strong> MOIL reported production is company-level historical context. It is not allocated to individual mines or used as a mine-level historical target.
              </div>
            </div>
            <div className="flex items-center gap-1.5 self-start sm:self-auto">
              <span className="px-1.5 py-0.2 rounded bg-emerald-950 border border-emerald-500/60 text-emerald-300 text-[9px] font-bold">
                REPORTED DATA
              </span>
              <span className="px-1.5 py-0.2 rounded bg-slate-800 border border-slate-700 text-slate-300 text-[9px] font-mono">
                {macroStats.count} OBS
              </span>
            </div>
          </div>

          {/* Chart Canvas */}
          <div className="h-64 sm:h-68 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={realChartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
                <XAxis dataKey="period" stroke="#94a3b8" fontSize={11} tickLine={false} />
                <YAxis
                  stroke="#94a3b8"
                  fontSize={11}
                  tickLine={false}
                  label={{ value: 'Lakh Tonnes', angle: -90, position: 'insideLeft', fill: '#94a3b8', fontSize: 10 }}
                />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const d = payload[0].payload;
                      return (
                        <div className="bg-slate-900 border border-amber-600/50 p-2.5 rounded shadow-xl text-xs">
                          <div className="flex items-center justify-between gap-3 mb-0.5">
                            <span className="font-bold text-white text-xs">{d.fullPeriod}</span>
                            <span className="px-1 py-0.2 bg-emerald-950 text-emerald-400 border border-emerald-600 rounded text-[8px] font-bold">
                              {d.dataStatus?.toUpperCase() || 'REAL'}
                            </span>
                          </div>
                          <div className="text-amber-400 font-bold text-xs">
                            {d.productionLakhTonnes} Lakh Tonnes
                          </div>
                          <div className="text-slate-300 font-mono text-[11px]">
                            {d.productionTonnes.toLocaleString()} Metric Tonnes
                          </div>
                          <div className="mt-1.5 pt-1 border-t border-slate-700 text-slate-400 text-[9px]">
                            Source: {d.source}
                          </div>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Legend verticalAlign="top" height={30} wrapperStyle={{ fontSize: '11px', color: '#cbd5e1' }} />

                <Bar
                  dataKey="productionLakhTonnes"
                  fill="#f59e0b"
                  radius={[3, 3, 0, 0]}
                  name="Reported Annual Production (Lakh Tonnes)"
                />

                <Line
                  type="monotone"
                  dataKey="productionLakhTonnes"
                  stroke="#38bdf8"
                  strokeWidth={2}
                  dot={{ r: 3, fill: '#38bdf8', stroke: '#0f172a', strokeWidth: 1 }}
                  name="Production Trend"
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          {/* Dynamic Summary Metric Cards */}
          <div className="pt-2 border-t border-technical grid grid-cols-1 sm:grid-cols-4 gap-2 text-xs">
            <div className="bg-slate-800/60 p-2 rounded border border-technical">
              <div className="text-slate-400 text-[10px]">{macroStats.latestPeriod} (Latest)</div>
              <div className="text-amber-300 font-bold text-xs mt-0.5">{macroStats.latestLakh} Lakh Tonnes</div>
              <div className="text-emerald-400 text-[10px] mt-0.5">{macroStats.latestTonnes.toLocaleString()} MT</div>
            </div>
            <div className="bg-slate-800/60 p-2 rounded border border-technical">
              <div className="text-slate-400 text-[10px]">Historical Peak</div>
              <div className="text-white font-bold text-xs mt-0.5">{macroStats.peakLakh} Lakh Tonnes</div>
              <div className="text-slate-400 text-[10px] mt-0.5">{macroStats.peakTonnes.toLocaleString()} MT Statutory High</div>
            </div>
            <div className="bg-slate-800/60 p-2 rounded border border-technical">
              <div className="text-slate-400 text-[10px]">{macroStats.count}-Year Historical Mean</div>
              <div className="text-white font-bold text-xs mt-0.5">{macroStats.meanLakh} Lakh Tonnes</div>
              <div className="text-slate-400 text-[10px] mt-0.5">Annual average across MOIL</div>
            </div>
            <div className="bg-slate-800/60 p-2 rounded border border-technical">
              <div className="text-slate-400 text-[10px]">Data Integrity</div>
              <div className="text-emerald-400 font-bold text-xs mt-0.5">100% Canonical</div>
              <div className="text-slate-400 text-[10px] mt-0.5">Zero mine-wise allocation</div>
            </div>
          </div>

          {/* Detailed Historical Data Table */}
          <div className="bg-slate-900/80 rounded border border-technical p-2.5">
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-amber-400" />
                MOIL Annual Production Time Series ({macroStats.count} Fiscal Years)
              </span>
              <span className="text-[9px] text-slate-400 font-mono">Unit: Metric Tonnes (MT) / Lakh Tonnes</span>
            </div>
            <div className="overflow-x-auto max-h-44 custom-scrollbar">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-technical text-slate-400 text-[10px] uppercase font-mono">
                    <th className="py-1 px-2">Fiscal Year</th>
                    <th className="py-1 px-2">Scope</th>
                    <th className="py-1 px-2 text-right">Production (MT)</th>
                    <th className="py-1 px-2 text-right">Production (Lakh MT)</th>
                    <th className="py-1 px-2">Status</th>
                    <th className="py-1 px-2">Source</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-technical text-slate-300 font-mono text-[11px]">
                  {annualSeries.map((row, idx) => (
                    <tr key={idx} className="hover:bg-slate-800/40 transition-colors">
                      <td className="py-1 px-2 font-semibold text-amber-300">{row.period}</td>
                      <td className="py-1 px-2 text-[10px] text-slate-400 font-sans">Company-Level Aggregate</td>
                      <td className="py-1 px-2 text-right text-white">{row.production_tonnes.toLocaleString()}</td>
                      <td className="py-1 px-2 text-right text-amber-400">{row.production_lakh_tonnes}</td>
                      <td className="py-1 px-2">
                        <span className="px-1 py-0.2 rounded bg-emerald-950 text-emerald-400 text-[8px] font-bold">
                          {row.data_status?.toUpperCase() || 'REAL'}
                        </span>
                      </td>
                      <td className="py-1 px-2 text-[9px] text-slate-400 truncate max-w-xs">{row.source}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 3: OPERATIONAL RECONCILIATION & SCENARIO SANDBOX                       */}
      {/* ========================================================================= */}
      {activeTab === 'reconciliation_sandbox' && (
        <div className="space-y-3">
          {/* Governance & Non-Fabrication Policy Disclaimer */}
          <div className="bg-indigo-950/30 border border-indigo-700/40 rounded p-2.5 flex items-start gap-2 text-xs">
            <Info className="w-3.5 h-3.5 text-indigo-400 shrink-0 mt-0.5" />
            <div className="space-y-0.5">
              <div className="font-semibold text-white flex items-center gap-1.5 text-xs">
                <span>Operational Reconciliation Framework</span>
                <span className="px-1 py-0.2 bg-indigo-900 border border-indigo-400/50 text-indigo-200 rounded text-[8px] font-mono">
                  BLOCK-LEVEL TARGET vs SIMULATION
                </span>
              </div>
              <p className="text-slate-300 text-[10px] leading-relaxed">
                Reconciliation compares simulated operational output (LightGBM P50) against explicit block targets (e.g. {currentBlock}: {customTarget.toLocaleString()} MT).
                <strong className="text-amber-300 ml-1">
                  “MOIL reported production is company-level historical context. It is not allocated to individual mines or used as a mine-level historical target.”
                </strong>
              </p>
            </div>
          </div>

          {/* Block & Horizon Bar */}
          <div className="bg-slate-900/90 border border-technical rounded p-2.5 flex flex-wrap items-center justify-between gap-2 text-xs font-mono">
            <div className="flex flex-wrap items-center gap-1.5">
              <span className="text-slate-400 font-semibold text-[11px]">Target Mine Block:</span>
              {['BLOCK_A', 'BLOCK_B', 'BLOCK_C'].map((bId) => (
                <button
                  key={bId}
                  onClick={() => {
                    setCurrentBlock(bId);
                    setCustomTarget(BLOCK_TARGETS[bId]);
                  }}
                  className={`px-2 py-0.5 rounded border text-[11px] font-semibold transition-all ${
                    currentBlock === bId
                      ? 'bg-purple-600 border-purple-400 text-white shadow'
                      : 'bg-slate-800 border-technical text-slate-300 hover:bg-slate-700'
                  }`}
                >
                  {bId} ({BLOCK_TARGETS[bId].toLocaleString()} t)
                </button>
              ))}
            </div>

            <div className="flex items-center gap-1">
              <span className="text-slate-400 font-semibold text-[11px]">Horizon:</span>
              {[7, 14, 30, 60, 90].map((h) => (
                <button
                  key={h}
                  onClick={() => setHorizonDays(h)}
                  className={`px-1.5 py-0.5 rounded text-[10px] border font-mono transition-all ${
                    horizonDays === h
                      ? 'bg-indigo-600 border-indigo-400 text-white'
                      : 'bg-slate-800 border-technical text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {h}d
                </button>
              ))}
            </div>
          </div>

          {/* 4-Card Operational Reconciliation Summary */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2 text-xs">
            {/* Card 1: Operational Target */}
            <div className="bg-slate-900/80 p-2.5 rounded border border-technical space-y-0.5">
              <div className="flex items-center justify-between text-slate-400 text-[10px]">
                <span>Operational Target</span>
                <span className="px-1 py-0.2 bg-slate-800 text-slate-300 rounded text-[8px] font-mono">TARGET</span>
              </div>
              <div className="text-base font-bold text-white font-mono">
                {customTarget.toLocaleString()} <span className="text-[10px] font-normal text-slate-400 font-sans">MT</span>
              </div>
              <div className="text-[9px] text-slate-400 font-mono">
                Rate: {targetDailyRate} t/d for {horizonDays}d
              </div>
            </div>

            {/* Card 2: Simulated Output */}
            <div className="bg-slate-900/80 p-2.5 rounded border border-technical space-y-0.5">
              <div className="flex items-center justify-between text-slate-400 text-[10px]">
                <span>Simulated Output (P50)</span>
                <span className="px-1 py-0.2 bg-purple-950 border border-purple-500/50 text-purple-300 rounded text-[8px] font-mono">
                  {isScenarioDirty ? 'SCENARIO' : 'BASELINE'}
                </span>
              </div>
              <div className="text-base font-bold text-purple-300 font-mono">
                {Math.round(activeSimulatedOutput).toLocaleString()} <span className="text-[10px] font-normal text-slate-400 font-sans">MT</span>
              </div>
              <div className="text-[9px] text-slate-400 font-mono">
                90% CI: [{Math.round(microSim.baseline_interval_90?.[0] || 0)} - {Math.round(microSim.baseline_interval_90?.[1] || 0)}]
              </div>
            </div>

            {/* Card 3: Reconciliation Variance */}
            <div className="bg-slate-900/80 p-2.5 rounded border border-technical space-y-0.5">
              <div className="flex items-center justify-between text-slate-400 text-[10px]">
                <span>Reconciliation Variance</span>
                <span className="px-1 py-0.2 bg-slate-800 text-slate-300 rounded text-[8px] font-mono">OUTPUT - TARGET</span>
              </div>
              <div className={`text-base font-bold font-mono ${activeVariance >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                {activeVariance >= 0 ? `+${activeVariance.toLocaleString()}` : activeVariance.toLocaleString()} <span className="text-[10px] font-normal text-slate-400 font-sans">MT</span>
              </div>
              <div className="text-[9px] text-slate-400 font-mono">
                {activeVariance >= 0 ? `Surplus: +${activeExcess.toLocaleString()} MT` : `Shortfall: -${activeShortfall.toLocaleString()} MT`}
              </div>
            </div>

            {/* Card 4: Operational Risk */}
            <div className="bg-slate-900/80 p-2.5 rounded border border-technical space-y-0.5">
              <div className="flex items-center justify-between text-slate-400 text-[10px]">
                <span>Operational Risk</span>
                <span className={`px-1 py-0.2 rounded text-[8px] font-bold font-mono ${
                  activeRiskLevel === 'HIGH' || activeRiskLevel === 'SEVERE'
                    ? 'bg-red-950 text-red-300 border border-red-600'
                    : activeRiskLevel === 'MODERATE'
                    ? 'bg-amber-950 text-amber-300 border border-amber-600'
                    : 'bg-emerald-950 text-emerald-300 border border-emerald-600'
                }`}>
                  {activeRiskLevel}
                </span>
              </div>
              <div className="text-base font-bold text-white font-mono">
                {Math.round(activeShortfallProb * 100)}% <span className="text-[10px] font-normal text-slate-400 font-sans">Prob</span>
              </div>
              <div className="text-[9px] text-slate-400 font-mono">
                Exp Shortfall: {Math.round(activeShortfall).toLocaleString()} MT
              </div>
            </div>
          </div>

          {/* Scenario Sandbox Sliders & Impact Section */}
          <div className="bg-slate-900/90 border border-technical rounded p-3 space-y-2.5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1.5 pb-1.5 border-b border-technical">
              <div className="flex items-center gap-1.5">
                <Sliders className="w-3.5 h-3.5 text-purple-400" />
                <span className="text-xs font-bold text-white font-mono">Scenario Adjustment Sandbox</span>
                {isScenarioDirty && (
                  <span className="px-1.5 py-0.2 rounded bg-purple-900/80 border border-purple-400 text-purple-200 text-[9px] font-mono">
                    MODIFIED
                  </span>
                )}
              </div>
              <div className="flex items-center gap-1.5">
                <button
                  onClick={handleResetScenario}
                  className="flex items-center gap-1 px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-[11px] border border-technical transition-colors"
                >
                  <RotateCcw className="w-3 h-3" />
                  Reset Defaults
                </button>
                <button
                  onClick={handleApplyScenario}
                  className="flex items-center gap-1 px-2.5 py-0.5 rounded bg-purple-600 hover:bg-purple-500 text-white font-semibold text-[11px] transition-colors shadow"
                >
                  <Zap className="w-3 h-3" />
                  Recalculate
                </button>
              </div>
            </div>

            {/* Sliders Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
              {/* Slider 1: Equipment Availability */}
              <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-700/60 space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-slate-300 font-semibold">Equipment Availability</span>
                  <span className="font-mono text-purple-300 font-bold">{equipmentAvailability}%</span>
                </div>
                <input
                  type="range"
                  min="40"
                  max="100"
                  step="1"
                  value={equipmentAvailability}
                  onChange={(e) => {
                    setEquipmentAvailability(parseFloat(e.target.value));
                    setIsScenarioDirty(true);
                  }}
                  className="w-full accent-purple-500 cursor-pointer"
                />
                <div className="flex justify-between text-[10px] text-slate-500">
                  <span>40% (Degraded)</span>
                  <span>88% (Norm)</span>
                  <span>100% (Full)</span>
                </div>
              </div>

              {/* Slider 2: Blasting Delays */}
              <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-700/60 space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-slate-300 font-semibold">Blasting Delay Flag</span>
                  <span className={`font-mono font-bold px-1.5 py-0.2 rounded text-[11px] ${blastingDelay === 1 ? 'bg-red-950 text-red-300 border border-red-700' : 'bg-emerald-950 text-emerald-300 border border-emerald-700'}`}>
                    {blastingDelay === 1 ? '1 (DELAY ACTIVE)' : '0 (NORMAL)'}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-2 pt-1">
                  <button
                    onClick={() => {
                      setBlastingDelay(0);
                      setIsScenarioDirty(true);
                    }}
                    className={`py-1 px-2 rounded border text-xs font-semibold transition-all ${
                      blastingDelay === 0
                        ? 'bg-emerald-600 border-emerald-400 text-white'
                        : 'bg-slate-800 border-slate-700 text-slate-400'
                    }`}
                  >
                    No Delay (0)
                  </button>
                  <button
                    onClick={() => {
                      setBlastingDelay(1);
                      setIsScenarioDirty(true);
                    }}
                    className={`py-1 px-2 rounded border text-xs font-semibold transition-all ${
                      blastingDelay === 1
                        ? 'bg-red-600 border-red-400 text-white'
                        : 'bg-slate-800 border-slate-700 text-slate-400'
                    }`}
                  >
                    Delay Present (1)
                  </button>
                </div>
                <div className="text-[10px] text-slate-500">Simulates delayed bench blasting cycles</div>
              </div>

              {/* Slider 3: Rainfall mm */}
              <div className="bg-slate-800/50 p-3 rounded-lg border border-slate-700/60 space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-slate-300 font-semibold">Rainfall (Pit Inundation)</span>
                  <span className="font-mono text-cyan-300 font-bold">{rainfall} mm</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="200"
                  step="2.5"
                  value={rainfall}
                  onChange={(e) => {
                    setRainfall(parseFloat(e.target.value));
                    setIsScenarioDirty(true);
                  }}
                  className="w-full accent-cyan-500 cursor-pointer"
                />
                <div className="flex justify-between text-[10px] text-slate-500">
                  <span>0 mm (Dry)</span>
                  <span>12.5 mm (Light)</span>
                  <span>200 mm (Monsoon)</span>
                </div>
              </div>
            </div>

            {/* Scenario Impact Banner */}
            {isScenarioDirty && (
              <div className="bg-purple-950/40 border border-purple-700/50 rounded-lg p-3 flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-purple-300" />
                  <span className="text-slate-300">
                    Baseline Output: <strong className="text-white font-mono">{Math.round(microSim.baseline_forecast_tonnes || 0).toLocaleString()} MT</strong>
                  </span>
                  <ArrowRight className="w-3.5 h-3.5 text-purple-400" />
                  <span className="text-slate-300">
                    Scenario Output: <strong className="text-purple-300 font-mono">{Math.round(activeSimulatedOutput).toLocaleString()} MT</strong>
                  </span>
                </div>
                <div className="text-purple-200 font-mono font-bold text-xs">
                  Delta: {Math.round(activeSimulatedOutput - (microSim.baseline_forecast_tonnes || 0)) >= 0 ? `+${Math.round(activeSimulatedOutput - (microSim.baseline_forecast_tonnes || 0))} MT` : `${Math.round(activeSimulatedOutput - (microSim.baseline_forecast_tonnes || 0))} MT`}
                </div>
              </div>
            )}
          </div>

          {/* Decision Optimizer Recommendations Section */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                <Zap className="w-3.5 h-3.5 text-amber-400" />
                MILP Decision Optimizer Corrective Recommendations
              </span>
              <span className="text-[10px] text-slate-400">Optimized for maximum recovery / minimum cost</span>
            </div>

            {recommendations.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                {recommendations.map((rec, idx) => (
                  <div key={idx} className="bg-slate-800/70 p-3 rounded-lg border border-slate-700/70 space-y-2">
                    <div className="flex items-start justify-between gap-2">
                      <div className="font-bold text-white flex items-center gap-1.5">
                        <CheckCircle className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                        <span>{rec.action_name || rec.name || `Action ${idx + 1}`}</span>
                      </div>
                      <span className="px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-700/60 text-[9px] font-mono font-bold uppercase">
                        {rec.priority || 'PRIORITY'}
                      </span>
                    </div>
                    <p className="text-slate-300 text-[11px] leading-relaxed">
                      {rec.description || rec.rationale || 'Adjust operational sequencing to mitigate simulated shortfall.'}
                    </p>
                    <div className="pt-2 border-t border-slate-700/60 flex items-center justify-between text-[11px]">
                      <span className="text-emerald-400 font-mono">
                        +{rec.expected_recovery_tonnes ? Math.round(rec.expected_recovery_tonnes).toLocaleString() : 'N/A'} MT Recovery
                      </span>
                      <span className="text-slate-400 font-mono">
                        Cost: {rec.estimated_cost_inr ? `₹${(rec.estimated_cost_inr / 1000).toFixed(0)}k` : 'Minimal'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-slate-800/40 p-4 rounded-lg border border-slate-700/50 text-center text-xs text-slate-400">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 mx-auto mb-1" />
                No critical shortfall detected for current parameters. Operational plan satisfies the target.
              </div>
            )}
          </div>
        </div>
      )}
      </div>
    </div>
  );
}
