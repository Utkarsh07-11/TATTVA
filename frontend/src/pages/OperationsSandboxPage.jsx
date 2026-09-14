import React, { useState } from 'react';
import { Sliders, Search, Cpu, CheckCircle } from 'lucide-react';
import ExplainabilityPanel from '../components/ExplainabilityPanel';
import WhatIfSandbox from '../components/WhatIfSandbox';
import RecommendationsPanel from '../components/RecommendationsPanel';
import BlockRevealImage from '../components/BlockRevealImage';
import { useDashboard } from '../context/DashboardContext';

// Authentic Field Photography
import bbcPatroller from '../assets/bbc/patroller-1.jpg';

export default function OperationsSandboxPage() {
  const {
    explanation,
    recommendations,
    selectedBlock,
    horizonDays,
    forecast,
    activePreset,
    setActivePreset,
  } = useDashboard();

  const [activeTab, setActiveTab] = useState('simulate'); // 'simulate' | 'explain' | 'actions'

  return (
    <div className="space-y-12 pb-20 max-w-7xl mx-auto px-4 sm:px-6 pt-6">
      {/* 1. Header with Slide-Down Animation */}
      <div className="border-b border-technical pb-6">
        <div className="text-xs font-sans tracking-wider text-amber-500 uppercase font-semibold mb-2 flex items-center gap-2 text-slide-down">
          <Cpu className="w-3.5 h-3.5 text-amber-500" />
          <span>OPERATIONAL DIAGNOSTICS AND SIMULATION</span>
        </div>

        <h1 className="font-editorial text-3xl sm:text-5xl text-white font-bold tracking-tight text-slide-down-d1">
          Root-Cause Diagnostics and Operational Scheduling
        </h1>

        <p className="mt-4 font-sans text-base sm:text-lg text-slate-300 max-w-3xl leading-relaxed text-slide-down-d2">
          Underground mining operations cannot rely on uninterpretable algorithms. When telemetry indicates a risk of shortfall at the stope, shift supervisors require three essential capabilities: factor sensitivity diagnostics to isolate bottlenecks, a real-time scenario simulator to model equipment and weather shifts, and linear optimization to dispatch corrective hauling resources.
        </p>

        {/* Workstation Mode Selector */}
        <div className="mt-6 flex flex-wrap items-center gap-2 border-t border-technical pt-4 text-slide-down-d3">
          <span className="text-xs font-sans text-slate-400 mr-2 uppercase tracking-wider font-semibold">
            Operational Tool:
          </span>
          <button
            onClick={() => setActiveTab('simulate')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded text-xs font-sans font-medium transition-all cursor-pointer ${
              activeTab === 'simulate'
                ? 'bg-story-accent text-black font-bold shadow'
                : 'bg-[#0e1219] text-slate-400 hover:text-white border border-technical'
            }`}
          >
            <Sliders className="w-3.5 h-3.5" />
            <span>Operational Scenario Simulator</span>
          </button>

          <button
            onClick={() => setActiveTab('explain')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded text-xs font-sans font-medium transition-all cursor-pointer ${
              activeTab === 'explain'
                ? 'bg-story-accent text-black font-bold shadow'
                : 'bg-[#0e1219] text-slate-400 hover:text-white border border-technical'
            }`}
          >
            <Search className="w-3.5 h-3.5" />
            <span>Factor Sensitivity Diagnostics</span>
          </button>

          <button
            onClick={() => setActiveTab('actions')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded text-xs font-sans font-medium transition-all cursor-pointer ${
              activeTab === 'actions'
                ? 'bg-story-accent text-black font-bold shadow'
                : 'bg-[#0e1219] text-slate-400 hover:text-white border border-technical'
            }`}
          >
            <CheckCircle className="w-3.5 h-3.5" />
            <span>Optimized Dispatch Schedule</span>
          </button>
        </div>
      </div>

      {/* 2. Formal White Section: Safety Envelope & Operational Reality */}
      <section className="bg-white text-slate-900 border border-slate-200 p-6 sm:p-10 rounded-xs">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          <div className="lg:col-span-7 space-y-4">
            <span className="text-xs font-sans uppercase tracking-wider text-amber-700 font-bold">
              AUTONOMOUS SAFETY ENVELOPE
            </span>
            <h3 className="font-sans text-2xl sm:text-3xl font-bold text-slate-950">
              Preserving Safety at the Automation Interface
            </h3>
            <p className="font-sans text-sm text-slate-700 leading-relaxed">
              When heavy haulers and robotic mucking shovels navigate underground drifts, machine perception must interact seamlessly with human supervisors. Optical LIDAR, infrared proximity sweeps, and dynamic geofencing establish safety corridors around active loaders, allowing human inspections to proceed without halting production lines.
            </p>
            <div className="grid grid-cols-2 gap-4 pt-2 font-sans text-xs text-slate-600">
              <div className="border-l-2 border-amber-600 pl-3">
                <div className="font-bold text-slate-950">&lt; 200 ms Latency</div>
                <div className="text-[11px] text-slate-500">Autonomous Emergency Stop Cycle</div>
              </div>
              <div className="border-l-2 border-emerald-600 pl-3">
                <div className="font-bold text-slate-950">Zero Stope Incidents</div>
                <div className="text-[11px] text-slate-500">Continuous Underground Level Record</div>
              </div>
            </div>
          </div>

          <div className="lg:col-span-5">
            <BlockRevealImage
              src={bbcPatroller}
              alt="Autonomous site patroller and supervisor"
              aspectRatio="aspect-[16/10]"
              blockColor="bg-[#d4a574]"
            />
          </div>
        </div>
      </section>

      {/* 3. Active Tab Content Container */}
      <div className="story-card p-4 sm:p-6 bg-[#0a0d14] border border-technical">
        {activeTab === 'simulate' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-white/5">
              <div>
                <h3 className="font-sans text-xl text-white font-bold">
                  What Happens If An Ore Shortfall Occurs? · Operational Scenario Simulator
                </h3>
                <p className="text-xs font-sans text-slate-300">
                  Simulate potential ore shortfall outcomes under fluctuating operational conditions (equipment breakdowns, blasting stoppages, wet pit rainfall), analyze the severity of the deficit, and evaluate solver-recommended recovery actions.
                </p>
              </div>
              <span className="text-xs font-sans text-amber-400 bg-amber-500/10 px-2 py-0.5 border border-amber-500/20 font-semibold">
                SHORTFALL DECISION SIMULATOR
              </span>
            </div>

            <WhatIfSandbox
              selectedBlock={selectedBlock}
              horizonDays={horizonDays}
              baselineForecast={forecast}
              activePreset={activePreset}
              onClearPreset={() => setActivePreset(null)}
            />
          </div>
        )}

        {activeTab === 'explain' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-white/5">
              <div>
                <h3 className="font-sans text-xl text-white font-bold">
                  SHAP Operational Root Cause Attribution
                </h3>
                <p className="text-xs font-sans text-slate-400">
                  Feature contributions attributing predicted shortfall against historical rolling baseline.
                </p>
              </div>
              <span className="text-xs font-sans text-amber-400 bg-amber-950/40 px-2 py-0.5 border border-amber-700/50 font-semibold">
                SHAPLEY MARGINAL CONTRIBUTION
              </span>
            </div>

            <ExplainabilityPanel explanation={explanation} />
          </div>
        )}

        {activeTab === 'actions' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-white/5">
              <div>
                <h3 className="font-sans text-xl text-white font-bold">
                  Linear Programming Constrained Dispatch Recommendations
                </h3>
                <p className="text-xs font-sans text-slate-400">
                  Feasible interventions solved via PuLP Coin-CBC optimizer maximizing tonnage recovered under equipment limits.
                </p>
              </div>
              <span className="text-xs font-sans text-emerald-400 bg-emerald-950/40 px-2 py-0.5 border border-emerald-700/50 font-semibold">
                CBC MILP SOLVER
              </span>
            </div>

            <RecommendationsPanel
              recommendations={recommendations}
              onApplyAction={(opt) => {
                setActivePreset(opt);
                setActiveTab('simulate');
              }}
            />
          </div>
        )}
      </div>

      {/* 4. OPERATIONAL SIMULATION AND LINEAR DISPATCH FORECAST */}
      <section className="story-card p-6 sm:p-8 border-l-4 border-l-amber-500 rounded-sm bg-[#0a0e17]">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-technical pb-3 mb-4 gap-2">
          <span className="text-xs font-sans font-bold text-amber-400 uppercase tracking-wider">
            Operational Simulation and Linear Dispatch Forecast
          </span>
          <span className="text-[11px] font-sans text-slate-400 font-medium">
            Dynamic Scheduling Dispatch
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          <div className="lg:col-span-7 space-y-2">
            <h4 className="text-base font-sans font-bold text-white uppercase tracking-wide">
              Operational and Industry Intelligence
            </h4>
            <p className="text-xs sm:text-sm text-slate-300 font-sans leading-relaxed">
              Mixed-integer linear programming algorithms are deployed across central dispatch to balance equipment availability during sudden rainfall and blasting pauses. High-frequency solver iterations continuously evaluate re-routing haulers to mitigate stope congestion.
            </p>
          </div>

          <div className="lg:col-span-5 bg-[#05070b] p-4 rounded border border-white/10 space-y-2">
            <div className="text-[11px] font-sans font-bold text-emerald-400 uppercase tracking-wider">
              Predictive Telemetry Projection
            </div>
            <p className="text-xs text-slate-300 font-sans leading-relaxed">
              Simulating equipment availability at 90% and clearing blasting delays predicts a recovery of +1,050 tonnes, lowering residual shortfall to 300 tonnes (80.7% recovery efficiency).
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
