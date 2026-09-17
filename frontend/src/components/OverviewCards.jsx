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
      <div className="bg-white border border-[#DCD5CD] p-3 sm:p-3.5 rounded-xl shadow-sm flex flex-col justify-between">
        <div>
          <div className="text-[10px] font-mono uppercase text-[#8A817D] tracking-wider mb-1">
            Planned Target
          </div>
          <div className="text-2xl font-bold font-mono text-[#26211F] tracking-tight">
            {target.toLocaleString()}{' '}
            <span className="text-xs font-normal text-[#8A817D]">t</span>
          </div>
        </div>
        <div className="text-[10px] text-[#5A524F] mt-2 pt-2 border-t border-[#DCD5CD] flex items-center justify-between font-mono">
          <span className="text-[#8A817D]">Scheduled</span>
          <span className="text-[#26211F] font-semibold">{selectedBlock}</span>
        </div>
      </div>

      {/* 2. Model Production Forecast */}
      <div className="bg-white border border-[#DCD5CD] p-3 sm:p-3.5 rounded-xl shadow-sm flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between text-[10px] font-mono uppercase text-[#8A817D] tracking-wider mb-1">
            <span>Forecast (P50)</span>
            <span className="text-[#8A817D] text-[9px]">Simulation</span>
          </div>
          <div className="text-2xl font-bold font-mono text-[#26211F] tracking-tight">
            {p50.toLocaleString()}{' '}
            <span className="text-xs font-normal text-[#8A817D]">t</span>
          </div>
        </div>
        <div className="text-[10px] text-[#5A524F] mt-2 pt-2 border-t border-[#DCD5CD] flex items-center justify-between font-mono">
          <span className="text-[#8A817D]">90% Range</span>
          <span className="text-[#5A524F]">[{p10.toLocaleString()} - {p90.toLocaleString()}]</span>
        </div>
      </div>

      {/* 3. Expected Shortfall Deficit */}
      <div className="bg-white border border-[#DCD5CD] p-3 sm:p-3.5 rounded-xl shadow-sm flex flex-col justify-between">
        <div>
          <div className="text-[10px] font-mono uppercase text-[#8A817D] tracking-wider mb-1">
            Expected Shortfall
          </div>
          <div className="text-2xl font-bold font-mono text-rose-700 tracking-tight">
            {shortfall > 0 ? `-${shortfall.toLocaleString()}` : '0'}{' '}
            <span className="text-xs font-normal text-[#8A817D]">t</span>
          </div>
        </div>
        <div className="text-[10px] text-[#5A524F] mt-2 pt-2 border-t border-[#DCD5CD] flex items-center justify-between font-mono">
          <span className="text-[#8A817D]">Variance</span>
          <span className="text-rose-700 font-semibold">{shortfall > 0 ? `${shortfallPct}%` : '0%'}</span>
        </div>
      </div>

      {/* 4. Shortfall Probability & Risk */}
      <div className="bg-white border border-[#DCD5CD] p-3 sm:p-3.5 rounded-xl shadow-sm flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between text-[10px] font-mono uppercase text-[#8A817D] tracking-wider mb-1">
            <span>Risk Level</span>
            <span className="flex items-center gap-1 font-mono text-[10px] text-[#26211F] font-semibold">
              <span className={`w-1.5 h-1.5 rounded-full ${riskDotColor}`}></span>
              {riskLevel}
            </span>
          </div>
          <div className="text-2xl font-bold font-mono text-[#26211F] tracking-tight">
            {prob}%{' '}
            <span className="text-xs font-normal text-[#8A817D]">risk</span>
          </div>
        </div>
        <div className="text-[10px] text-[#5A524F] mt-2 pt-2 border-t border-[#DCD5CD] flex items-center justify-between font-mono">
          <span className="text-[#8A817D]">Root Cause</span>
          <button
            onClick={() => navigate('/explain')}
            className="text-[#C87A5B] hover:underline font-semibold flex items-center gap-1 cursor-pointer"
          >
            <span>Inspect</span>
            <ArrowRight className="w-2.5 h-2.5" />
          </button>
        </div>
      </div>
    </div>
  );
}



