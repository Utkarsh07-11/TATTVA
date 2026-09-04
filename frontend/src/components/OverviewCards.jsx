import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Target, TrendingDown, AlertTriangle } from 'lucide-react';

export default function OverviewCards({ forecast, overview, selectedBlock }) {
  const navigate = useNavigate();
  if (!forecast) return null;

  const target = forecast.target_tonnes || 10000;
  const p50 = forecast.forecast_tonnes || 8650;
  const [p10, p90] = forecast.interval_90 || [7900, 9300];
  const shortfall = forecast.expected_shortfall_tonnes || 1350;
  const shortfallPct = forecast.shortfall_pct || 13.5;
  const prob = Math.round((forecast.shortfall_probability || 0.87) * 100);
  const riskLevel = forecast.risk_level || 'HIGH';

  const riskBadgeStyles = {
    CRITICAL: 'bg-red-950 text-red-400 border-red-800 animate-pulse',
    HIGH: 'bg-amber-950 text-amber-400 border-amber-800',
    MEDIUM: 'bg-yellow-950 text-yellow-400 border-yellow-800',
    LOW: 'bg-emerald-950 text-emerald-400 border-emerald-800',
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 stagger">
      {/* 1. Monthly Production Target */}
      <div className="panel p-4 relative overflow-hidden">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Planned Target
          </span>
          <span className="p-2 bg-indigo-950/80 rounded-lg text-indigo-400 border border-indigo-800/50">
            <Target className="w-4 h-4" />
          </span>
        </div>
        <div className="text-2xl font-black text-white">
          {target.toLocaleString()} <span className="text-sm font-normal text-slate-400">tonnes</span>
        </div>
        <div className="text-xs text-slate-400 mt-2 flex items-center gap-1.5">
          <span className="inline-block w-2 h-2 rounded-full bg-indigo-500"></span>
          Scheduled monthly quota for {selectedBlock}
        </div>
      </div>

      {/* 2. Model Production Forecast (P50 + Quantile Interval) */}
      <div className="panel p-4 relative overflow-hidden">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Quantile Forecast (P50)
          </span>
          <span className="p-2 bg-purple-950/80 rounded-lg text-purple-400 border border-purple-800/50">
            <TrendingDown className="w-4 h-4" />
          </span>
        </div>
        <div className="text-2xl font-black text-purple-400">
          {p50.toLocaleString()} <span className="text-sm font-normal text-slate-400">tonnes</span>
        </div>
        <div className="text-xs text-slate-400 mt-2">
          90% Interval: <span className="text-slate-300 font-mono font-medium">[{p10.toLocaleString()} - {p90.toLocaleString()} t]</span>
        </div>
      </div>

      {/* 3. Expected Shortfall Deficit */}
      <div className="panel p-4 relative overflow-hidden">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Expected Deficit
          </span>
          <span className="p-2 bg-red-950/80 rounded-lg text-red-400 border border-red-800/50">
            <AlertTriangle className="w-4 h-4" />
          </span>
        </div>
        <div className="text-2xl font-black text-red-400">
          {shortfall > 0 ? `-${shortfall.toLocaleString()}` : '0'}{' '}
          <span className="text-sm font-normal text-slate-400">tonnes</span>
        </div>
        <div className="text-xs text-red-400/90 mt-2 font-medium">
          {shortfall > 0 ? `Gap: ${shortfallPct}% below planned quota` : 'On target (0% deficit)'}
        </div>
      </div>

      {/* 4. Shortfall Probability & Categorical Risk Badge */}
      <div className="panel p-4 relative overflow-hidden">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Shortfall Risk Level
          </span>
          <span className={`px-2.5 py-1 rounded-full text-xs font-extrabold border ${riskBadgeStyles[riskLevel] || riskBadgeStyles.MEDIUM}`}>
            {riskLevel} RISK
          </span>
        </div>
        <div className="text-2xl font-black text-white">
          {prob}% <span className="text-sm font-normal text-slate-400">probability</span>
        </div>
        <div className="text-xs text-slate-400 mt-2 flex items-center justify-between">
          <span>P(Actual &lt; Target)</span>
          <span
            className="text-copper-300 font-medium cursor-pointer hover:underline"
            onClick={() => navigate('/explain')}
          >
            View root cause →
          </span>
        </div>
      </div>
    </div>
  );
}
