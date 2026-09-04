import React from 'react';
import { useNavigate } from 'react-router-dom';
import PageHeader from '../components/PageHeader';
import OverviewCards from '../components/OverviewCards';
import { useDashboard } from '../context/DashboardContext';
import { CloudRain, Wrench, ShieldCheck } from 'lucide-react';

export default function OverviewPage() {
  const { forecast, overview, selectedBlock } = useDashboard();
  const navigate = useNavigate();

  return (
    <div className="page-enter space-y-5">
      <PageHeader
        kicker="Operations center"
        title="Mine production shortfall desk"
        subtitle="Closed-loop support: forecast the gap, explain the drivers, simulate levers, then rank feasible interventions."
      />
      <OverviewCards forecast={forecast} overview={overview} selectedBlock={selectedBlock} />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 stagger">
        <div className="panel p-5">
          <div className="flex items-center gap-2 text-copper-300 text-sm font-semibold">
            <CloudRain className="w-4 h-4" /> Weather advisory
          </div>
          <p className="mt-3 text-sm text-slate-300">{overview?.current_weather?.condition || 'Loading weather…'}</p>
          <p className="mt-2 text-xs text-slate-400">{overview?.current_weather?.blast_risk_advisory}</p>
        </div>
        <div className="panel p-5">
          <div className="flex items-center gap-2 text-teal-300 text-sm font-semibold">
            <Wrench className="w-4 h-4" /> Fleet snapshot
          </div>
          <p className="mt-3 text-2xl font-semibold">{overview?.active_equipment_count ?? '—'} <span className="text-sm text-slate-400">active</span></p>
          <p className="mt-1 text-xs text-slate-400">{overview?.equipment_under_repair_count ?? 0} units under repair</p>
        </div>
        <div className="panel p-5">
          <div className="flex items-center gap-2 text-emerald-300 text-sm font-semibold">
            <ShieldCheck className="w-4 h-4" /> Model status
          </div>
          <p className="mt-3 text-sm text-slate-300">{overview?.model_status?.status || 'Connecting…'}</p>
          <p className="mt-1 text-xs text-slate-400">LightGBM · SHAP · PuLP · XGBoost spatial CV</p>
        </div>
      </div>

      <div className="panel p-5">
        <div className="text-sm font-semibold mb-3">Active blocks</div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {(overview?.blocks || []).map((block) => (
            <button
              key={block.block_id}
              onClick={() => navigate('/forecast')}
              className="soft-btn text-left rounded-xl border border-white/10 bg-ink-900/60 p-4 hover:border-copper-500/40"
            >
              <div className="text-xs text-slate-400">{block.block_id}</div>
              <div className="font-semibold mt-1">{block.name}</div>
              <div className="mt-2 text-xs text-slate-400">Forecast {block.forecast_tonnes?.toLocaleString()} t · {block.risk_level} risk</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
