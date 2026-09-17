import React, { useState } from 'react';
import { Sliders, Search, Cpu, CheckCircle } from 'lucide-react';
import ExplainabilityPanel from '../components/ExplainabilityPanel';
import WhatIfSandbox from '../components/WhatIfSandbox';
import RecommendationsPanel from '../components/RecommendationsPanel';
import BlockRevealImage from '../components/BlockRevealImage';
import { useDashboard } from '../context/DashboardContext';

// Authentic Indian Field Photography
import indianShovelWorker from '../assets/indian_mines/shovel-dumper-worker.jpg';

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
      <div className="border-b border-[#DCD5CD] pb-6">
        <div className="text-xs font-sans tracking-wider text-[#C87A5B] uppercase font-semibold mb-2 flex items-center gap-2 text-slide-down">
          <Cpu className="w-3.5 h-3.5 text-[#C87A5B]" />
          <span>OPERATIONAL DIAGNOSTICS AND SIMULATION</span>
        </div>

        <h1 className="font-editorial text-3xl sm:text-5xl text-[#26211F] font-bold tracking-tight text-slide-down-d1">
          Root-Cause Diagnostics and Operational Scheduling
        </h1>

        <p className="mt-4 font-sans text-base sm:text-lg text-[#5A524F] max-w-3xl leading-relaxed text-slide-down-d2">
          Underground mining operations cannot rely on uninterpretable algorithms. When telemetry indicates a risk of shortfall at the stope, shift supervisors require three essential capabilities: factor sensitivity diagnostics to isolate bottlenecks, a real-time scenario simulator to model equipment and weather shifts, and linear optimization to dispatch corrective hauling resources.
        </p>
      </div>

      {/* 2. Formal Card Section: Safety Envelope & Operational Reality */}
      <section className="bg-white text-[#26211F] border border-[#DCD5CD] p-6 sm:p-10 rounded-xl shadow-sm">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          <div className="lg:col-span-7 space-y-4">
            <span className="text-xs font-sans uppercase tracking-wider text-[#C87A5B] font-bold">
              AUTONOMOUS SAFETY ENVELOPE
            </span>
            <h3 className="font-sans text-2xl sm:text-3xl font-bold text-[#26211F]">
              Preserving Safety at the Automation Interface
            </h3>
            <p className="font-sans text-sm text-[#5A524F] leading-relaxed">
              When heavy haulers and robotic mucking shovels navigate underground drifts, machine perception must interact seamlessly with human supervisors. Optical LIDAR, infrared proximity sweeps, and dynamic geofencing establish safety corridors around active loaders, allowing human inspections to proceed without halting production lines.
            </p>
            <div className="grid grid-cols-2 gap-4 pt-2 font-sans text-xs text-[#5A524F]">
              <div className="border-l-2 border-[#C87A5B] pl-3">
                <div className="font-bold text-[#26211F]">&lt; 200 ms Latency</div>
                <div className="text-[11px] text-[#8A817D]">Autonomous Emergency Stop Cycle</div>
              </div>
              <div className="border-l-2 border-emerald-700 pl-3">
                <div className="font-bold text-[#26211F]">Zero Stope Incidents</div>
                <div className="text-[11px] text-[#8A817D]">Continuous Underground Level Record</div>
              </div>
            </div>
          </div>

          <div className="lg:col-span-5">
            <BlockRevealImage
              src={indianShovelWorker}
              alt="Mining face supervisor and shovel equipment interface in an Indian open-cast pit"
              aspectRatio="aspect-[16/10]"
              blockColor="bg-[#C87A5B]"
            />
          </div>
        </div>
      </section>

      {/* 3. Workstation Mode Selector */}
      <div className="space-y-4">
        <div id="tour-operations-tools" className="flex flex-wrap items-center gap-2.5">
          <span className="text-xs font-sans text-[#8A817D] mr-1 uppercase tracking-wider font-semibold">
            Operational Tool:
          </span>
          <button
            type="button"
            onClick={() => setActiveTab('simulate')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-sans font-semibold transition-all duration-200 cursor-pointer ${
              activeTab === 'simulate'
                ? 'bg-[#C87A5B] text-white font-bold border border-[#B85D3B] shadow-sm'
                : 'bg-white text-[#5A524F] hover:text-[#26211F] hover:bg-[#EEE6DD]/50 border border-[#DCD5CD]'
            }`}
          >
            <Sliders className={`w-3.5 h-3.5 ${activeTab === 'simulate' ? 'text-white' : 'text-[#C87A5B]'}`} />
            <span>Operational Scenario Simulator</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('explain')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-sans font-semibold transition-all duration-200 cursor-pointer ${
              activeTab === 'explain'
                ? 'bg-[#C87A5B] text-white font-bold border border-[#B85D3B] shadow-sm'
                : 'bg-white text-[#5A524F] hover:text-[#26211F] hover:bg-[#EEE6DD]/50 border border-[#DCD5CD]'
            }`}
          >
            <Search className={`w-3.5 h-3.5 ${activeTab === 'explain' ? 'text-white' : 'text-[#C87A5B]'}`} />
            <span>Factor Sensitivity Diagnostics</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('actions')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-sans font-semibold transition-all duration-200 cursor-pointer ${
              activeTab === 'actions'
                ? 'bg-[#C87A5B] text-white font-bold border border-[#B85D3B] shadow-sm'
                : 'bg-white text-[#5A524F] hover:text-[#26211F] hover:bg-[#EEE6DD]/50 border border-[#DCD5CD]'
            }`}
          >
            <CheckCircle className={`w-3.5 h-3.5 ${activeTab === 'actions' ? 'text-white' : 'text-[#C87A5B]'}`} />
            <span>Optimized Dispatch Schedule</span>
          </button>
        </div>

        {/* Active Tab Content Container */}
        <div id="tour-operations-workbench" className="bg-white rounded-xl p-4 sm:p-6 border border-[#DCD5CD] shadow-sm">
        {activeTab === 'simulate' && (
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-[#DCD5CD] gap-2">
              <div>
                <h3 className="font-sans text-xl text-[#26211F] font-bold">
                  What Happens If An Ore Shortfall Occurs? · Operational Scenario Simulator
                </h3>
                <p className="text-xs font-sans text-[#5A524F] mt-0.5">
                  Simulate potential ore shortfall outcomes under fluctuating operational conditions (equipment breakdowns, blasting stoppages, wet pit rainfall), analyze the severity of the deficit, and evaluate solver-recommended recovery actions.
                </p>
              </div>
              <span className="text-xs font-sans text-[#8C3A1E] bg-[#EDC7B7]/40 px-2.5 py-1 rounded border border-[#C87A5B]/40 font-semibold self-start sm:self-auto shrink-0">
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
            <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-[#DCD5CD] gap-2">
              <div>
                <h3 className="font-sans text-xl text-[#26211F] font-bold">
                  SHAP Operational Root Cause Attribution
                </h3>
                <p className="text-xs font-sans text-[#5A524F] mt-0.5">
                  Feature contributions attributing predicted shortfall against historical rolling baseline.
                </p>
              </div>
              <span className="text-xs font-sans text-[#8C3A1E] bg-[#EDC7B7]/40 px-2.5 py-1 rounded border border-[#C87A5B]/40 font-semibold self-start sm:self-auto shrink-0">
                SHAPLEY MARGINAL CONTRIBUTION
              </span>
            </div>

            <ExplainabilityPanel explanation={explanation} />
          </div>
        )}

        {activeTab === 'actions' && (
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-[#DCD5CD] gap-2">
              <div>
                <h3 className="font-sans text-xl text-[#26211F] font-bold">
                  Linear Programming Constrained Dispatch Recommendations
                </h3>
                <p className="text-xs font-sans text-[#5A524F] mt-0.5">
                  Feasible interventions solved via PuLP Coin-CBC optimizer maximizing tonnage recovered under equipment limits.
                </p>
              </div>
              <span className="text-xs font-sans text-emerald-800 bg-emerald-100 px-2.5 py-1 rounded border border-emerald-300 font-semibold self-start sm:self-auto shrink-0">
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
      </div>

      {/* 4. OPERATIONAL SIMULATION AND LINEAR DISPATCH FORECAST */}
      <section id="tour-milp-forecast" className="bg-white p-6 sm:p-8 border-l-4 border-l-[#C87A5B] rounded-xl border border-[#DCD5CD] shadow-sm scroll-mt-24">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-[#DCD5CD] pb-3 mb-4 gap-2">
          <span className="text-xs font-sans font-bold text-[#C87A5B] uppercase tracking-wider">
            Operational Simulation and Linear Dispatch Forecast
          </span>
          <span className="text-[11px] font-sans text-[#8A817D] font-medium">
            Dynamic Scheduling Dispatch
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          <div className="lg:col-span-7 space-y-2">
            <h4 className="text-base font-sans font-bold text-[#26211F] uppercase tracking-wide">
              Operational and Industry Intelligence
            </h4>
            <p className="text-xs sm:text-sm text-[#5A524F] font-sans leading-relaxed">
              Mixed-integer linear programming algorithms are deployed across central dispatch to balance equipment availability during sudden rainfall and blasting pauses. High-frequency solver iterations continuously evaluate re-routing haulers to mitigate stope congestion.
            </p>
          </div>

          <div className="lg:col-span-5 bg-[#FAF7F2] p-4 rounded-lg border border-[#DCD5CD] space-y-2">
            <div className="text-[11px] font-sans font-bold text-emerald-700 uppercase tracking-wider">
              Predictive Telemetry Projection
            </div>
            <p className="text-xs text-[#5A524F] font-sans leading-relaxed">
              Simulating equipment availability at 90% and clearing blasting delays predicts a recovery of +1,050 tonnes, lowering residual shortfall to 300 tonnes (80.7% recovery efficiency).
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
