import React, { useState, useEffect } from 'react';
import { Sliders, Play, RotateCcw, TrendingUp, Sparkles } from 'lucide-react';
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
    <div className="panel p-5">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Sliders className="w-5 h-5 text-indigo-400" />
          <h2 className="text-base font-bold text-white">
            What-If Scenario Simulation Sandbox
          </h2>
        </div>
        <button
          onClick={handleReset}
          className="flex items-center gap-1 text-xs text-slate-400 hover:text-white px-2 py-1 rounded bg-slate-800 border border-slate-700 transition-all cursor-pointer"
        >
          <RotateCcw className="w-3 h-3" /> Reset Defaults
        </button>
      </div>

      <p className="text-xs text-slate-400 mb-4">
        Dynamically perturb operational levers and re-score the trained LightGBM model in real time.
      </p>

      {/* Interactive Controls Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-5">
        {/* 1. Fleet Availability Slider */}
        <div className="bg-slate-800/80 p-3.5 rounded-lg border border-slate-700">
          <div className="flex items-center justify-between text-xs mb-2">
            <span className="text-slate-300 font-semibold">Equipment Availability</span>
            <span className="text-indigo-400 font-bold font-mono">{availability.toFixed(1)}%</span>
          </div>
          <input
            type="range"
            min="50"
            max="98"
            step="1"
            value={availability}
            onChange={(e) => setAvailability(parseFloat(e.target.value))}
            className="w-full accent-indigo-500 cursor-pointer"
          />
          <div className="flex justify-between text-[10px] text-slate-400 mt-1">
            <span>50% (High Breakdowns)</span>
            <span>98% (Optimal)</span>
          </div>
        </div>

        {/* 2. Blasting Delay Toggle */}
        <div className="bg-slate-800/80 p-3.5 rounded-lg border border-slate-700">
          <div className="flex items-center justify-between text-xs mb-2">
            <span className="text-slate-300 font-semibold">Blasting Operations Delay</span>
            <span className={blastingDelay ? 'text-amber-400 font-bold' : 'text-emerald-400 font-bold'}>
              {blastingDelay ? 'DELAY ACTIVE' : 'CLEARED / ON SCHEDULE'}
            </span>
          </div>
          <div className="flex items-center gap-2 mt-2">
            <button
              onClick={() => setBlastingDelay(1)}
              className={`flex-1 py-1 text-xs font-semibold rounded transition-all ${
                blastingDelay === 1
                  ? 'bg-amber-950 text-amber-300 border border-amber-700'
                  : 'bg-slate-900 text-slate-400 border border-slate-700'
              }`}
            >
              Delay Active (1)
            </button>
            <button
              onClick={() => setBlastingDelay(0)}
              className={`flex-1 py-1 text-xs font-semibold rounded transition-all ${
                blastingDelay === 0
                  ? 'bg-emerald-950 text-emerald-300 border border-emerald-700'
                  : 'bg-slate-900 text-slate-400 border border-slate-700'
              }`}
            >
              Cleared (0)
            </button>
          </div>
          <div className="text-[10px] text-slate-400 mt-2">
            Rescheduling blast avoids fragmentation delays.
          </div>
        </div>

        {/* 3. Rainfall Forecast Slider */}
        <div className="bg-slate-800/80 p-3.5 rounded-lg border border-slate-700">
          <div className="flex items-center justify-between text-xs mb-2">
            <span className="text-slate-300 font-semibold">Rainfall Forecast</span>
            <span className="text-blue-400 font-bold font-mono">{rainfall.toFixed(1)} mm</span>
          </div>
          <input
            type="range"
            min="0"
            max="60"
            step="2"
            value={rainfall}
            onChange={(e) => setRainfall(parseFloat(e.target.value))}
            className="w-full accent-blue-500 cursor-pointer"
          />
          <div className="flex justify-between text-[10px] text-slate-400 mt-1">
            <span>0 mm (Dry Pit)</span>
            <span>60 mm (Heavy Wet)</span>
          </div>
        </div>
      </div>

      {/* Live Simulation Response Banner */}
      <div className="bg-slate-800/95 border border-indigo-700/60 rounded-xl p-4 shadow-lg">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-indigo-950 border border-indigo-800 text-indigo-400">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xs text-slate-400">Simulated 30-Day Production</div>
              <div className="text-2xl font-black text-white">
                {Math.round(simTonnes).toLocaleString()}{' '}
                <span className="text-sm font-normal text-slate-400">tonnes</span>
              </div>
              <div className="text-xs text-slate-400 mt-0.5">
                Baseline Forecast: <span className="font-mono text-slate-300">{Math.round(baseTonnes).toLocaleString()} t</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-6 sm:border-l sm:border-slate-700 sm:pl-6">
            <div>
              <div className="text-xs text-slate-400">Projected Tonnage Gain</div>
              <div className="text-xl font-black text-emerald-400">
                +{Math.round(recoveryTonnes).toLocaleString()} t
              </div>
              <div className="text-[11px] text-emerald-400/90 font-medium">
                Expected Recovery
              </div>
            </div>

            <div>
              <div className="text-xs text-slate-400">Remaining Deficit</div>
              <div className="text-xl font-black text-amber-400">
                {newDeficit > 0 ? `-${Math.round(newDeficit).toLocaleString()} t` : '0 t'}
              </div>
              <div className="text-[11px] text-slate-400">
                Target: {targetTonnes.toLocaleString()} t
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
