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
    <div className="space-y-3 max-w-4xl mx-auto font-sans">
      {/* 1. SCENARIO OUTPUT BANNER */}
      <div className="bg-[#FAF7F2] border border-[#DCD5CD] p-4 sm:p-5 rounded-xl shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="text-xs font-sans uppercase tracking-wider text-[#C87A5B] font-bold">
            What Happens If An Ore Shortfall Occurs? · Output Analysis ({horizonDays}d Horizon)
          </div>
          <div className="text-xl sm:text-2xl font-bold font-sans text-[#26211F] flex items-center gap-2">
            <span className="text-[#8A817D] font-normal">{Math.round(baseTonnes).toLocaleString()}</span>
            <span className="text-[#8A817D]">→</span>
            <span>{Math.round(simTonnes).toLocaleString()} t</span>
          </div>
          <div className="text-xs text-[#5A524F] font-sans">
            Stope Target: {targetTonnes.toLocaleString()} t
          </div>
        </div>

        <div className="flex items-center gap-6 sm:border-l sm:border-[#DCD5CD] sm:pl-5 font-sans">
          <div>
            <div className="text-[11px] uppercase tracking-wider text-[#8A817D]">
              Recovery Delta
            </div>
            <div className="text-xl sm:text-2xl font-bold text-emerald-700">
              +{Math.round(recoveryTonnes).toLocaleString()} t
            </div>
          </div>

          <div>
            <div className="text-[11px] uppercase tracking-wider text-[#8A817D]">
              Residual Deficit
            </div>
            <div className="text-xl sm:text-2xl font-bold text-[#C87A5B]">
              {newDeficit > 0 ? `-${Math.round(newDeficit).toLocaleString()} t` : '0 t'}
            </div>
          </div>
        </div>
      </div>

      {/* 2. SCENARIO INPUT LEVERS */}
      <div className="bg-white rounded-xl p-4 space-y-4 border border-[#DCD5CD] shadow-sm">
        <div className="flex items-center justify-between pb-2 border-b border-[#DCD5CD]">
          <h2 className="text-xs sm:text-sm font-bold text-[#26211F] font-sans uppercase tracking-wide">
            Operational Levers ({selectedBlock})
          </h2>
          <button
            onClick={handleReset}
            className="flex items-center gap-1 text-xs font-sans text-[#5A524F] hover:text-[#26211F] px-2.5 py-1 rounded-md bg-[#FAF7F2] hover:bg-[#EEE6DD] border border-[#DCD5CD] transition-colors cursor-pointer"
          >
            <RotateCcw className="w-3 h-3 text-[#5A524F]" />
            <span>Reset Defaults</span>
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {/* Lever 1: Fleet Availability */}
          <div className="bg-[#FAF7F2] p-3 rounded-lg border border-[#DCD5CD] space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-[#26211F] font-semibold font-sans">Equipment Availability</span>
              <span className="text-[#C87A5B] font-bold font-sans">{availability.toFixed(1)}%</span>
            </div>
            <input
              type="range"
              min="50"
              max="98"
              step="1"
              value={availability}
              onChange={(e) => setAvailability(parseFloat(e.target.value))}
              className="w-full accent-[#C87A5B] cursor-pointer"
            />
            <div className="flex justify-between text-[10px] font-sans text-[#8A817D]">
              <span>50% (Degraded)</span>
              <span>98% (Nominal)</span>
            </div>
          </div>

          {/* Lever 2: Blasting Delay */}
          <div className="bg-[#FAF7F2] p-3 rounded-lg border border-[#DCD5CD] space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-[#26211F] font-semibold font-sans">Blasting Stoppage</span>
              <span className={`font-sans text-xs font-bold ${blastingDelay ? 'text-rose-700' : 'text-emerald-700'}`}>
                {blastingDelay ? 'Active Delay' : 'Cleared'}
              </span>
            </div>
            <div className="flex items-center gap-2 pt-1">
              <button
                onClick={() => setBlastingDelay(1)}
                className={`flex-1 py-1 text-xs font-sans rounded-md border transition-colors cursor-pointer ${
                  blastingDelay === 1
                    ? 'bg-red-700 text-white border-red-800 font-bold shadow-sm'
                    : 'bg-white text-[#5A524F] border-[#DCD5CD]'
                }`}
              >
                Delay (1)
              </button>
              <button
                onClick={() => setBlastingDelay(0)}
                className={`flex-1 py-1 text-xs font-sans rounded-md border transition-colors cursor-pointer ${
                  blastingDelay === 0
                    ? 'bg-emerald-700 text-white border-emerald-800 font-bold shadow-sm'
                    : 'bg-white text-[#5A524F] border-[#DCD5CD]'
                }`}
              >
                Normal (0)
              </button>
            </div>
          </div>

          {/* Lever 3: Rainfall Inundation */}
          <div className="bg-[#FAF7F2] p-3 rounded-lg border border-[#DCD5CD] space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-[#26211F] font-semibold font-sans">Rainfall Inundation</span>
              <span className="text-[#C87A5B] font-bold font-sans">{rainfall.toFixed(1)} mm</span>
            </div>
            <input
              type="range"
              min="0"
              max="60"
              step="2"
              value={rainfall}
              onChange={(e) => setRainfall(parseFloat(e.target.value))}
              className="w-full accent-[#C87A5B] cursor-pointer"
            />
            <div className="flex justify-between text-[10px] font-sans text-[#8A817D]">
              <span>0 mm (Dry)</span>
              <span>60 mm (Wet Pit)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
