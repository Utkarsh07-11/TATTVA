import React, { useState } from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { RefreshCw, Sparkles } from 'lucide-react';
import { useDashboard } from '../context/DashboardContext';
import DemoPresenterHUD from '../components/DemoPresenterHUD';

const navItems = [
  { to: '/', label: 'Overview' },
  { to: '/mine-map', label: 'Digital Mine' },
  { to: '/forecast', label: 'Production' },
  { to: '/explain', label: 'Root Cause' },
  { to: '/actions', label: 'Actions' },
  { to: '/simulate', label: 'Simulator' },
  { to: '/resources', label: 'Resources' },
];

export default function AppShell() {
  const {
    selectedBlock,
    setSelectedBlock,
    horizonDays,
    setHorizonDays,
    loading,
    loadDashboardData,
    error,
  } = useDashboard();

  const [showDemoHUD, setShowDemoHUD] = useState(false);

  return (
    <div className="min-h-screen text-slate-200 flex flex-col bg-[#07090d]">
      {/* 1. QUIET WORKSTATION TOP NAVIGATION */}
      <header className="sticky top-0 z-50 bg-[#07090d]/95 backdrop-blur-md border-b border-technical">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="flex items-center justify-between h-12 gap-3">
            {/* Brand Logo & Current Mine Context */}
            <div className="flex items-center gap-3 shrink-0">
              <NavLink to="/" className="flex items-center gap-1.5 group">
                <span className="text-xl font-black font-condensed tracking-wider text-white group-hover:text-industrial-amber transition-colors">
                  TATTVA
                </span>
              </NavLink>
              <div className="hidden sm:block h-3.5 w-px bg-white/10" />
              <div className="hidden sm:flex items-center gap-1.5 text-[10px] font-mono text-slate-400">
                <span className="text-white font-bold">BALAGHAT</span>
                <span className="text-slate-600">·</span>
                <span className="text-slate-400">MP</span>
              </div>
            </div>

            {/* Quiet Horizontal Navigation Links */}
            <nav className="hidden lg:flex items-center space-x-1">
              {navItems.map(({ to, label }) => (
                <NavLink
                  key={to}
                  to={to}
                  end={to === '/'}
                  className={({ isActive }) =>
                    `px-3 py-1 text-xs font-sans font-medium transition-colors relative ${
                      isActive
                        ? 'text-industrial-amber font-semibold'
                        : 'text-slate-400 hover:text-white'
                    }`
                  }
                >
                  {({ isActive }) => (
                    <>
                      <span>{label}</span>
                      {isActive && (
                        <span className="absolute bottom-[-14px] left-2 right-2 h-[2px] bg-industrial-amber" />
                      )}
                    </>
                  )}
                </NavLink>
              ))}
            </nav>

            {/* Quick Status Bar */}
            <div className="flex items-center gap-2 font-mono text-[10px] shrink-0">
              <button
                onClick={() => setShowDemoHUD(!showDemoHUD)}
                className={`flex items-center gap-1 px-2.5 py-1 rounded border text-[11px] font-sans font-semibold transition-colors cursor-pointer ${
                  showDemoHUD
                    ? 'bg-amber-950/80 border-industrial-amber text-industrial-amber shadow-sm shadow-amber-950/40'
                    : 'bg-[#0b0e14] border-amber-900/60 text-amber-300 hover:bg-amber-950/40 hover:text-amber-200'
                }`}
                title="Toggle Live Presentation Stepper HUD"
              >
                <Sparkles className="w-3.5 h-3.5 text-industrial-amber" />
                <span>Demo Tour</span>
              </button>

              <div className="hidden sm:flex items-center gap-1 px-2 py-0.5 rounded bg-[#0b0e14] border border-technical">
                <span className="text-slate-500">BLOCK:</span>
                <select
                  value={selectedBlock}
                  onChange={(e) => setSelectedBlock(e.target.value)}
                  className="bg-transparent text-slate-200 font-bold focus:outline-none cursor-pointer"
                >
                  <option value="BLOCK_A" className="bg-[#0b0e14] text-slate-200">Block A</option>
                  <option value="BLOCK_B" className="bg-[#0b0e14] text-slate-200">Block B</option>
                  <option value="BLOCK_C" className="bg-[#0b0e14] text-slate-200">Block C</option>
                </select>
              </div>

              <div className="hidden xl:flex items-center gap-0.5 bg-[#0b0e14] rounded border border-technical p-0.5">
                {[7, 15, 30].map((days) => (
                  <button
                    key={days}
                    onClick={() => setHorizonDays(days)}
                    className={`px-1.5 py-0.5 rounded text-[9px] font-bold transition-colors ${
                      horizonDays === days
                        ? 'bg-industrial-amber text-black'
                        : 'text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {days}D
                  </button>
                ))}
              </div>

              <span className="hidden md:inline-flex items-center gap-1 text-[10px] text-slate-400">
                <span className="w-1.5 h-1.5 rounded-full bg-purple-400"></span>
                SIMULATION
              </span>

              <button
                onClick={loadDashboardData}
                disabled={loading}
                className="flex items-center gap-1 px-2 py-0.5 rounded bg-[#0b0e14] hover:bg-[#141b26] border border-technical text-slate-300 hover:text-white transition-colors cursor-pointer disabled:opacity-50"
                title="Synchronize live inference"
              >
                <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin text-industrial-amber' : 'text-slate-400'}`} />
                <span className="text-[10px] font-medium hidden xs:inline">Sync</span>
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation Scrollbar */}
        <div className="lg:hidden flex overflow-x-auto gap-1.5 px-3 py-1.5 border-t border-technical bg-[#0a0d14]">
          {navItems.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `whitespace-nowrap px-2.5 py-0.5 rounded text-xs transition-colors ${
                  isActive
                    ? 'bg-industrial-amber text-black font-semibold'
                    : 'text-slate-400 hover:text-white'
                }`
              }
            >
              {label}
            </NavLink>
          ))}
        </div>
      </header>

      {/* 2. MAIN WORKSPACE CONTAINER */}
      <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 py-4">
        {error && (
          <div className="mb-4 p-3 text-xs font-mono text-rose-300 border border-rose-800/80 bg-rose-950/30 rounded">
            [SYSTEM ERROR] {error}. Ensure FastAPI backend service is operational on port 8000.
          </div>
        )}
        {loading && !error && (
          <div className="mb-3 text-xs font-mono text-industrial-amber flex items-center gap-2">
            <span className="inline-block w-1.5 h-1.5 rounded-full bg-industrial-amber animate-pulse"></span>
            Synchronizing mine telemetry & inference pipeline...
          </div>
        )}
        <Outlet />
      </main>

      {/* Floating Demo Presenter HUD */}
      {showDemoHUD && <DemoPresenterHUD onClose={() => setShowDemoHUD(false)} />}

      {/* 3. QUIET INDUSTRIAL FOOTER */}
      <footer className="border-t border-technical bg-[#05070a] py-2.5 text-slate-500 text-[11px] font-mono">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="font-bold text-white">TATTVA</span>
            <span className="text-slate-700">|</span>
            <span>Central India Manganese Belt Spatial Decision Support</span>
          </div>
          <div className="flex items-center gap-3 text-slate-500">
            <span>EPSG:32644 (UTM 44N)</span>
            <span>·</span>
            <span>10 MOIL Mines</span>
            <span>·</span>
            <span className="text-emerald-400">● Online</span>
          </div>
        </div>
      </footer>
    </div>
  );
}


