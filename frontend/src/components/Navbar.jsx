import React from 'react';
import { Pickaxe, ShieldAlert, Cpu, Layers, RefreshCw } from 'lucide-react';

export default function Navbar({
  selectedBlock,
  onSelectBlock,
  horizonDays,
  onSelectHorizon,
  showWatermark,
  onToggleWatermark,
  onRefresh,
  loading
}) {
  return (
    <header className="bg-slate-900 border-b border-slate-800 sticky top-0 z-50 px-4 lg:px-8 py-3">
      <div className="flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Brand & Project Title */}
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-tr from-purple-600 to-indigo-500 p-2.5 rounded-xl shadow-lg shadow-indigo-500/20 text-white">
            <Pickaxe className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold text-white tracking-wide">
                MOIL GeoProduction AI
              </h1>
              <span className="bg-purple-950 text-purple-300 text-xs font-semibold px-2 py-0.5 rounded border border-purple-800">
                SIH 2026 PS 26009
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Manganese Reserve Identification & Production-Shortfall Decision Support
            </p>
          </div>
        </div>

        {/* Global Controls */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Mine Block Selector */}
          <div className="flex items-center bg-slate-800/80 rounded-lg p-1 border border-slate-700">
            <span className="text-xs font-medium text-slate-400 px-2 flex items-center gap-1">
              <Layers className="w-3.5 h-3.5" /> Block:
            </span>
            <select
              value={selectedBlock}
              onChange={(e) => onSelectBlock(e.target.value)}
              className="bg-slate-900 text-white text-xs font-semibold py-1 px-2.5 rounded border border-slate-700 focus:outline-none focus:border-indigo-500 cursor-pointer"
            >
              <option value="BLOCK_A">Block A (High-Grade Pit)</option>
              <option value="BLOCK_B">Block B (East Extension)</option>
              <option value="BLOCK_C">Block C (South Strip)</option>
            </select>
          </div>

          {/* Planning Horizon Selector */}
          <div className="flex items-center bg-slate-800/80 rounded-lg p-1 border border-slate-700">
            <span className="text-xs font-medium text-slate-400 px-2">Horizon:</span>
            {[7, 15, 30].map((days) => (
              <button
                key={days}
                onClick={() => onSelectHorizon(days)}
                className={`text-xs font-semibold px-2.5 py-1 rounded transition-all ${
                  horizonDays === days
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {days}d
              </button>
            ))}
          </div>

          {/* Synthetic Watermark Toggle */}
          <button
            onClick={onToggleWatermark}
            className={`flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1.5 rounded-lg border transition-all ${
              showWatermark
                ? 'bg-amber-950/70 border-amber-600 text-amber-300'
                : 'bg-slate-800 border-slate-700 text-slate-400'
            }`}
            title="Toggle Synthetic Demo Data Watermark Banner"
          >
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>SYNTHETIC DEMO DATA</span>
          </button>

          {/* Live Refresh Button */}
          <button
            onClick={onRefresh}
            disabled={loading}
            className="p-2 rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white transition-all disabled:opacity-50"
            title="Refresh Live Inference Pipeline"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-indigo-400' : ''}`} />
          </button>
        </div>
      </div>
    </header>
  );
}
