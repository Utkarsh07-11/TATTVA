import React from 'react';
import { CheckCircle2, Zap, ArrowRight, ShieldCheck, DollarSign, Activity } from 'lucide-react';

export default function RecommendationsPanel({ recommendations, onApplyAction }) {
  if (!recommendations) return null;

  const {
    options = [],
    top_2_projected_recovery = 1050,
    expected_shortfall = 1350,
    residual_shortfall = 300,
    solver_status = 'Optimal'
  } = recommendations;

  const getCostBadge = (cost) => {
    switch (cost) {
      case 'Low':
        return 'bg-emerald-950 text-emerald-400 border-emerald-800';
      case 'Medium':
        return 'bg-amber-950 text-amber-400 border-amber-800';
      default:
        return 'bg-red-950 text-red-400 border-red-800';
    }
  };

  const getFeasibilityBadge = (feasibility) => {
    switch (feasibility) {
      case 'High':
        return 'bg-indigo-950 text-indigo-400 border-indigo-800';
      case 'Medium':
        return 'bg-purple-950 text-purple-400 border-purple-800';
      default:
        return 'bg-slate-800 text-slate-400 border-slate-700';
    }
  };

  return (
    <div className="panel p-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
        <div className="flex items-center gap-2">
          <Zap className="w-5 h-5 text-amber-400" />
          <h2 className="text-base font-bold text-white">
            Decision Optimization & Action Plan
          </h2>
        </div>
        <span className="text-xs bg-slate-800 text-slate-300 font-mono px-2 py-0.5 rounded border border-slate-700">
          PuLP Solver: {solver_status}
        </span>
      </div>

      <p className="text-xs text-slate-400 mb-4">
        Constrained scenario simulation ranked by expected recovery, cost, operational risk, and feasibility.
      </p>

      {/* Top Projected Recovery Banner */}
      <div className="bg-gradient-to-r from-purple-950/80 via-indigo-950/80 to-slate-900 border border-indigo-800/60 rounded-xl p-4 mb-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="text-xs font-semibold text-indigo-300 uppercase tracking-wider">
              Projected Shortfall Recovery (Top 2 Interventions)
            </div>
            <div className="text-2xl font-black text-white mt-0.5">
              +{top_2_projected_recovery.toLocaleString()}{' '}
              <span className="text-sm font-normal text-slate-400">tonnes recovered</span>
            </div>
          </div>
          <div className="text-right sm:border-l sm:border-slate-800 sm:pl-4">
            <div className="text-xs text-slate-400">Residual Deficit</div>
            <div className="text-lg font-bold text-amber-400">
              {residual_shortfall > 0 ? `-${residual_shortfall.toLocaleString()} t` : '0 t'}
            </div>
            <div className="text-[11px] text-emerald-400 font-medium">
              {expected_shortfall > 0
                ? `${Math.round((top_2_projected_recovery / expected_shortfall) * 100)}% of gap resolved`
                : '100% resolved'}
            </div>
          </div>
        </div>
      </div>

      {/* Ranked Action Cards */}
      <div className="space-y-3">
        {options.map((opt) => (
          <div
            key={opt.action_id}
            className={`bg-slate-800/70 border rounded-xl p-4 transition-all hover:bg-slate-800/90 ${
              opt.lp_recommended ? 'border-indigo-600/70 shadow-sm shadow-indigo-900/20' : 'border-slate-700'
            }`}
          >
            <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2 mb-2">
              <div className="flex items-start gap-2.5">
                <span className="flex items-center justify-center w-6 h-6 rounded-full bg-indigo-600 text-white text-xs font-black shrink-0 mt-0.5">
                  #{opt.rank}
                </span>
                <div>
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    {opt.title}
                    {opt.lp_recommended && (
                      <span className="bg-emerald-950 text-emerald-400 text-[10px] font-bold px-1.5 py-0.5 rounded border border-emerald-800">
                        MILP Selected
                      </span>
                    )}
                  </h3>
                  <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                    {opt.details}
                  </p>
                </div>
              </div>

              {/* Recovery Metric Badge */}
              <div className="sm:text-right shrink-0">
                <div className="text-emerald-400 font-black text-lg">
                  +{opt.expected_recovery_tonnes.toLocaleString()} t
                </div>
                <div className="text-[10px] text-slate-400 uppercase font-semibold">
                  Expected Gain
                </div>
              </div>
            </div>

            {/* Tags and Action trigger */}
            <div className="flex flex-wrap items-center justify-between gap-2 pt-3 border-t border-slate-700/60 text-xs">
              <div className="flex items-center gap-2">
                <span className={`px-2 py-0.5 rounded text-[11px] font-semibold border ${getCostBadge(opt.cost)}`}>
                  Cost: {opt.cost}
                </span>
                <span className={`px-2 py-0.5 rounded text-[11px] font-semibold border ${getFeasibilityBadge(opt.feasibility)}`}>
                  Feasibility: {opt.feasibility}
                </span>
                <span className="text-slate-400 text-[11px]">
                  Score: <strong className="text-slate-200">{opt.net_utility_score}</strong>
                </span>
              </div>

              <button
                onClick={() => onApplyAction(opt)}
                className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-indigo-600/80 hover:bg-indigo-600 text-white font-semibold text-xs transition-all cursor-pointer"
              >
                <span>Simulate in Sandbox</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
