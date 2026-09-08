import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';

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

  const riskDotColor = {
    CRITICAL: 'bg-rose-400',
    HIGH: 'bg-amber-400',
    MEDIUM: 'bg-yellow-400',
    LOW: 'bg-emerald-400',
  }[riskLevel] || 'bg-amber-400';

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
      {/* 1. Monthly Production Target */}
      <div className="bg-[#0a0d14] border border-technical p-3 sm:p-3.5 rounded flex flex-col justify-between">
        <div>
          <div className="text-[10px] font-mono uppercase text-slate-400 tracking-wider mb-1">
            Planned Target
          </div>
          <div className="text-2xl font-bold font-mono text-white tracking-tight">
            {target.toLocaleString()}{' '}
            <span className="text-xs font-normal text-slate-400">t</span>
          </div>
        </div>
        <div className="text-[10px] text-slate-400 mt-2 pt-2 border-t border-technical flex items-center justify-between font-mono">
          <span className="text-slate-500">Scheduled</span>
          <span className="text-slate-200">{selectedBlock}</span>
        </div>
      </div>

      {/* 2. Model Production Forecast */}
      <div className="bg-[#0a0d14] border border-technical p-3 sm:p-3.5 rounded flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between text-[10px] font-mono uppercase text-slate-400 tracking-wider mb-1">
            <span>Forecast (P50)</span>
            <span className="text-slate-500 text-[9px]">Simulation</span>
          </div>
          <div className="text-2xl font-bold font-mono text-white tracking-tight">
            {p50.toLocaleString()}{' '}
            <span className="text-xs font-normal text-slate-400">t</span>
          </div>
        </div>
        <div className="text-[10px] text-slate-400 mt-2 pt-2 border-t border-technical flex items-center justify-between font-mono">
          <span className="text-slate-500">90% Range</span>
          <span className="text-slate-300">[{p10.toLocaleString()} - {p90.toLocaleString()}]</span>
        </div>
      </div>

      {/* 3. Expected Shortfall Deficit */}
      <div className="bg-[#0a0d14] border border-technical p-3 sm:p-3.5 rounded flex flex-col justify-between">
        <div>
          <div className="text-[10px] font-mono uppercase text-slate-400 tracking-wider mb-1">
            Expected Shortfall
          </div>
          <div className="text-2xl font-bold font-mono text-rose-400 tracking-tight">
            {shortfall > 0 ? `-${shortfall.toLocaleString()}` : '0'}{' '}
            <span className="text-xs font-normal text-slate-400">t</span>
          </div>
        </div>
        <div className="text-[10px] text-slate-400 mt-2 pt-2 border-t border-technical flex items-center justify-between font-mono">
          <span className="text-slate-500">Variance</span>
          <span className="text-rose-300 font-semibold">{shortfall > 0 ? `${shortfallPct}%` : '0%'}</span>
        </div>
      </div>

      {/* 4. Shortfall Probability & Risk */}
      <div className="bg-[#0a0d14] border border-technical p-3 sm:p-3.5 rounded flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between text-[10px] font-mono uppercase text-slate-400 tracking-wider mb-1">
            <span>Risk Level</span>
            <span className="flex items-center gap-1 font-mono text-[10px] text-slate-300 font-semibold">
              <span className={`w-1.5 h-1.5 rounded-full ${riskDotColor}`}></span>
              {riskLevel}
            </span>
          </div>
          <div className="text-2xl font-bold font-mono text-white tracking-tight">
            {prob}%{' '}
            <span className="text-xs font-normal text-slate-400">risk</span>
          </div>
        </div>
        <div className="text-[10px] text-slate-400 mt-2 pt-2 border-t border-technical flex items-center justify-between font-mono">
          <span className="text-slate-500">Root Cause</span>
          <button
            onClick={() => navigate('/explain')}
            className="text-industrial-amber hover:underline font-semibold flex items-center gap-1 cursor-pointer"
          >
            <span>Inspect</span>
            <ArrowRight className="w-2.5 h-2.5" />
          </button>
        </div>
      </div>
    </div>
  );
}



