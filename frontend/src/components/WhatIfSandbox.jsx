import React, { useState, useEffect } from 'react';
import { RotateCcw } from 'lucide-react';
import { api } from '../services/api';

export default function WhatIfSandbox({ selectedBlock, horizonDays = 30, baselineForecast, activePreset, onClearPreset }) {
  const [availability, setAvailability] = useState(72.0);
  const [blastingDelay, setBlastingDelay] = useState(1);
  const [rainfall, setRainfall] = useState(15.0);

  const [simResult, setSimResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // Apply preset from recommendations card if user clicks "Simulate in Sandbox"
  useEffect(() => {
    if (activePreset) {
      if (activePreset.action === 'redeploy_excavator') {
        setAvailability(90.0);
      } else if (activePreset.action === 'reschedule_blasting') {
        setBlastingDelay(0);
      } else if (activePreset.action === 'preventive_maintenance') {
        setAvailability(82.0);
      }
    }
  }, [activePreset]);

  // Run simulation on parameter changes
  const runSimulation = async () => {
    setLoading(true);
    try {
      const res = await api.simulateScenario(selectedBlock, {
        horizon_days: horizonDays,
        equipment_availability_pct: availability,
        blasting_delay_flag: blastingDelay,
        rainfall_mm: rainfall,
      });
      setSimResult(res);
    } catch (e) {
      console.error('Simulation error:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      runSimulation();
    }, 250);
    return () => clearTimeout(timer);
  }, [availability, blastingDelay, rainfall, selectedBlock, horizonDays]);

  const handleReset = () => {
    setAvailability(72.0);
    setBlastingDelay(1);
    setRainfall(15.0);
    if (onClearPreset) onClearPreset();
  };

  const baseTonnes = baselineForecast?.forecast_tonnes || 8650;
  const targetTonnes = baselineForecast?.target_tonnes || 10000;
  const simTonnes = simResult?.simulated_tonnes || baseTonnes;
  const recoveryTonnes = simResult?.expected_recovery_tonnes || Math.max(0, simTonnes - baseTonnes);
  const newDeficit = Math.max(0, targetTonnes - simTonnes);

  return (
    <div className="space-y-3 max-w-4xl mx-auto">
      {/* 1. SCENARIO OUTPUT BANNER */}
      <div className="bg-[#080b10] border border-technical p-4 sm:p-5 rounded flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="text-[10px] font-mono uppercase tracking-wider text-slate-400">
            Scenario Output ({horizonDays}d Horizon)
          </div>
          <div className="text-xl sm:text-2xl font-bold font-mono text-white flex items-center gap-2">
            <span className="text-slate-400 font-normal">{Math.round(baseTonnes).toLocaleString()}</span>
            <span className="text-slate-600">→</span>
            <span>{Math.round(simTonnes).toLocaleString()} t</span>
          </div>
          <div className="text-xs text-slate-400 font-mono">
            Target: {targetTonnes.toLocaleString()} t
          </div>
        </div>

        <div className="flex items-center gap-6 sm:border-l sm:border-technical sm:pl-5 font-mono">
          <div>
            <div className="text-[10px] uppercase tracking-wider text-slate-400">
              Recovery Delta
            </div>
            <div className="text-xl sm:text-2xl font-bold text-emerald-400">
              +{Math.round(recoveryTonnes).toLocaleString()} t
            </div>
          </div>

          <div>
            <div className="text-[10px] uppercase tracking-wider text-slate-400">
              Residual Deficit
            </div>
            <div className="text-xl sm:text-2xl font-bold text-amber-400">
              {newDeficit > 0 ? `-${Math.round(newDeficit).toLocaleString()} t` : '0 t'}
            </div>
          </div>
        </div>
      </div>

      {/* 2. SCENARIO INPUT LEVERS */}
      <div className="panel p-4 space-y-4">
        <div className="flex items-center justify-between pb-2 border-b border-technical">
          <h2 className="text-xs sm:text-sm font-bold text-white font-mono uppercase tracking-wide">
            Operational Levers ({selectedBlock})
          </h2>
          <button
            onClick={handleReset}
            className="flex items-center gap-1 text-[11px] font-mono text-slate-400 hover:text-white px-2 py-0.5 rounded bg-[#101622] border border-technical transition-colors cursor-pointer"
          >
            <RotateCcw className="w-3 h-3 text-slate-400" />
            <span>Reset Defaults</span>
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {/* Lever 1: Fleet Availability */}
          <div className="bg-[#080b10] p-3 rounded border border-technical space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-300 font-mono">Equipment Availability</span>
              <span className="text-white font-bold font-mono">{availability.toFixed(1)}%</span>
            </div>
            <input
              type="range"
              min="50"
              max="98"
              step="1"
              value={availability}
              onChange={(e) => setAvailability(parseFloat(e.target.value))}
              className="w-full accent-amber-400 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] font-mono text-slate-500">
              <span>50% (Degraded)</span>
              <span>98% (Nominal)</span>
            </div>
          </div>

          {/* Lever 2: Blasting Delay */}
          <div className="bg-[#080b10] p-3 rounded border border-technical space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-300 font-mono">Blasting Stoppage</span>
              <span className={`font-mono text-[11px] font-bold ${blastingDelay ? 'text-rose-400' : 'text-emerald-400'}`}>
                {blastingDelay ? 'Active Delay' : 'Cleared'}
              </span>
            </div>
            <div className="flex items-center gap-2 pt-1">
              <button
                onClick={() => setBlastingDelay(1)}
                className={`flex-1 py-1 text-xs font-mono rounded border transition-colors ${
                  blastingDelay === 1
                    ? 'bg-[#221010] text-rose-300 border-rose-800 font-bold'
                    : 'bg-[#0b0e14] text-slate-400 border-technical'
                }`}
              >
                Delay (1)
              </button>
              <button
                onClick={() => setBlastingDelay(0)}
                className={`flex-1 py-1 text-xs font-mono rounded border transition-colors ${
                  blastingDelay === 0
                    ? 'bg-[#102216] text-emerald-300 border-emerald-800 font-bold'
                    : 'bg-[#0b0e14] text-slate-400 border-technical'
                }`}
              >
                Normal (0)
              </button>
            </div>
          </div>

          {/* Lever 3: Rainfall Inundation */}
          <div className="bg-[#080b10] p-3 rounded border border-technical space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-300 font-mono">Rainfall Inundation</span>
              <span className="text-white font-bold font-mono">{rainfall.toFixed(1)} mm</span>
            </div>
            <input
              type="range"
              min="0"
              max="60"
              step="2"
              value={rainfall}
              onChange={(e) => setRainfall(parseFloat(e.target.value))}
              className="w-full accent-amber-400 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] font-mono text-slate-500">
              <span>0 mm (Dry)</span>
              <span>60 mm (Wet Pit)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}


