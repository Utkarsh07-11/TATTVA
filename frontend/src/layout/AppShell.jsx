import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import {
  LayoutDashboard,
  Map,
  LineChart,
  Cpu,
  Zap,
  Sliders,
  Database,
  RefreshCw,
  ShieldAlert,
  Layers,
} from 'lucide-react';
import { useDashboard } from '../context/DashboardContext';

const links = [
  { to: '/', label: 'Overview', icon: LayoutDashboard },
  { to: '/mine-map', label: 'Digital Mine', icon: Map },
  { to: '/forecast', label: 'Forecast', icon: LineChart },
  { to: '/explain', label: 'Root Cause', icon: Cpu },
  { to: '/actions', label: 'Actions', icon: Zap },
  { to: '/simulate', label: 'Simulator', icon: Sliders },
  { to: '/resources', label: 'Resources', icon: Database },
];

export default function AppShell() {
  const {
    selectedBlock,
    setSelectedBlock,
    horizonDays,
    setHorizonDays,
    showWatermark,
    setShowWatermark,
    loading,
    loadDashboardData,
    error,
  } = useDashboard();

  return (
    <div className="min-h-screen text-slate-100 flex">
      <aside className="hidden lg:flex w-64 flex-col border-r border-white/10 bg-ink-900/90 backdrop-blur-md">
        <div className="px-5 py-6 border-b border-white/10">
          <div className="text-[11px] tracking-[0.22em] uppercase text-copper-400 font-semibold">SIH 2026 · PS 26009</div>
          <h1 className="mt-2 text-xl font-semibold tracking-tight">GeoProduction AI</h1>
          <p className="mt-1 text-xs text-slate-400 leading-relaxed">MOIL manganese reserve & shortfall decision support</p>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          {links.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `nav-link flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm ${
                  isActive
                    ? 'bg-copper-500/15 text-copper-300 border border-copper-500/30'
                    : 'text-slate-400 hover:bg-white/5 hover:text-white border border-transparent'
                }`
              }
            >
              <Icon className="w-4 h-4" />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="p-4 text-[11px] text-slate-500 border-t border-white/10">
          Predict → Explain → Simulate → Recommend → Visualize
        </div>
      </aside>

      <div className="flex-1 min-w-0 flex flex-col">
        <header className="sticky top-0 z-40 border-b border-white/10 bg-ink-950/80 backdrop-blur-md">
          <div className="px-4 lg:px-6 py-3 flex flex-col xl:flex-row xl:items-center justify-between gap-3">
            <div className="lg:hidden">
              <div className="text-[11px] tracking-[0.22em] uppercase text-copper-400 font-semibold">SIH 2026 · PS 26009</div>
              <div className="font-semibold">GeoProduction AI</div>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <div className="flex items-center bg-ink-800 rounded-xl p-1 border border-white/10">
                <span className="text-xs text-slate-400 px-2 flex items-center gap-1">
                  <Layers className="w-3.5 h-3.5" /> Block
                </span>
                <select
                  value={selectedBlock}
                  onChange={(e) => setSelectedBlock(e.target.value)}
                  className="bg-ink-900 text-white text-xs font-semibold py-1.5 px-2 rounded-lg border border-white/10 focus:outline-none"
                >
                  <option value="BLOCK_A">Block A — High-grade pit</option>
                  <option value="BLOCK_B">Block B — East extension</option>
                  <option value="BLOCK_C">Block C — South strip</option>
                </select>
              </div>
              <div className="flex items-center bg-ink-800 rounded-xl p-1 border border-white/10">
                <span className="text-xs text-slate-400 px-2">Horizon</span>
                {[7, 15, 30].map((days) => (
                  <button
                    key={days}
                    onClick={() => setHorizonDays(days)}
                    className={`soft-btn text-xs font-semibold px-2.5 py-1.5 rounded-lg ${
                      horizonDays === days ? 'bg-copper-500 text-ink-950' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    {days}d
                  </button>
                ))}
              </div>
              <button
                onClick={() => setShowWatermark(!showWatermark)}
                className={`soft-btn flex items-center gap-1.5 text-xs font-semibold px-3 py-2 rounded-xl border ${
                  showWatermark
                    ? 'bg-amber-950/70 border-amber-700/70 text-amber-300'
                    : 'bg-ink-800 border-white/10 text-slate-400'
                }`}
              >
                <ShieldAlert className="w-3.5 h-3.5" />
                Synthetic
              </button>
              <button
                onClick={loadDashboardData}
                disabled={loading}
                className="soft-btn p-2 rounded-xl bg-ink-800 border border-white/10 text-slate-300 disabled:opacity-50"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-copper-400' : ''}`} />
              </button>
            </div>
          </div>
          <nav className="lg:hidden flex overflow-x-auto gap-1 px-3 pb-3">
            {links.map(({ to, label }) => (
              <NavLink
                key={to}
                to={to}
                end={to === '/'}
                className={({ isActive }) =>
                  `whitespace-nowrap px-3 py-1.5 rounded-full text-xs border ${
                    isActive ? 'bg-copper-500/20 text-copper-300 border-copper-500/40' : 'text-slate-400 border-white/10'
                  }`
                }
              >
                {label}
              </NavLink>
            ))}
          </nav>
        </header>

        {showWatermark && (
          <div className="bg-amber-950/50 border-b border-amber-800/50 px-4 py-2 text-xs text-amber-200/90">
            <strong>[SYNTHETIC DEMO DATA]</strong> Parametric synthetic models and public geological context for SIH 2026 PS 26009. No proprietary MOIL data is shown.
          </div>
        )}

        <main className="flex-1 px-4 lg:px-6 py-5">
          {error && (
            <div className="mb-4 panel p-4 text-sm text-red-300 border-red-900/60">
              {error}. Start the FastAPI backend, then refresh.
            </div>
          )}
          {loading && !error && (
            <div className="mb-4 text-xs text-slate-400 animate-pulse">Refreshing live inference…</div>
          )}
          <Outlet />
        </main>
      </div>
    </div>
  );
}
