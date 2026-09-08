import React from 'react';
import { ArrowRight } from 'lucide-react';

export default function RecommendationsPanel({ recommendations, onApplyAction }) {
  if (!recommendations) return null;

  const {
    options = [],
    top_2_projected_recovery = 1050,
    expected_shortfall = 1350,
    residual_shortfall = 300,
    solver_status = 'Optimal'
  } = recommendations;

  const topRecommended = options.find((o) => o.lp_recommended) || options[0];

  return (
    <div className="space-y-3 max-w-4xl mx-auto">
      {/* 1. DECISION-FIRST DOMINANT RECOMMENDED ACTION */}
      {topRecommended && (
        <div className="bg-[#080b10] border border-technical p-4 sm:p-5 rounded flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="text-[10px] font-mono uppercase tracking-wider text-slate-400">
              Recommended Action · MILP Optimal
            </div>
            <div className="text-xl sm:text-2xl font-bold font-mono text-white">
              {topRecommended.title}
            </div>
            <p className="text-xs text-slate-400 max-w-xl">
              {topRecommended.details}
            </p>
          </div>

          <div className="flex items-center gap-4 sm:border-l sm:border-technical sm:pl-5 shrink-0">
            <div>
              <div className="text-[10px] font-mono uppercase tracking-wider text-slate-400">
                Expected Recovery
              </div>
              <div className="text-xl sm:text-2xl font-bold font-mono text-emerald-400">
                +{topRecommended.expected_recovery_tonnes.toLocaleString()} t
              </div>
            </div>
            <button
              onClick={() => onApplyAction(topRecommended)}
              className="px-4 py-2 rounded bg-industrial-amber hover:bg-amber-400 text-black font-bold text-xs flex items-center gap-1.5 transition-colors cursor-pointer self-start sm:self-auto"
            >
              <span>Apply Scenario</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}

      {/* 2. RANKED ALTERNATIVE ACTIONS */}
      <div className="panel p-4 space-y-3">
        <div className="flex items-center justify-between pb-2 border-b border-technical">
          <h2 className="text-xs sm:text-sm font-bold text-white font-mono uppercase tracking-wide">
            Ranked Intervention Options
          </h2>
          <span className="text-[10px] font-mono text-slate-500">
            PuLP Solver: <strong className="text-slate-300">{solver_status}</strong>
          </span>
        </div>

        <div className="space-y-2">
          {options.map((opt) => (
            <div
              key={opt.action_id}
              className={`bg-[#080b10] border rounded p-3 transition-colors ${
                opt.lp_recommended ? 'border-amber-900/60' : 'border-technical'
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-start gap-2.5">
                  <span className="text-xs font-mono font-bold text-slate-500 mt-0.5">
                    0{opt.rank}
                  </span>
                  <div>
                    <h3 className="text-xs font-bold text-white flex items-center gap-2">
                      {opt.title}
                      {opt.lp_recommended && (
                        <span className="text-industrial-amber text-[9px] font-mono font-bold">
                          ● SELECTED
                        </span>
                      )}
                    </h3>
                    <p className="text-xs text-slate-400 mt-0.5">
                      {opt.details}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3 shrink-0 self-end sm:self-auto font-mono text-xs">
                  <div className="text-right">
                    <span className="text-emerald-400 font-bold">+{opt.expected_recovery_tonnes.toLocaleString()} t</span>
                  </div>
                  <button
                    onClick={() => onApplyAction(opt)}
                    className="px-2.5 py-1 rounded bg-[#101622] hover:bg-[#182233] text-slate-200 text-xs border border-technical transition-colors cursor-pointer"
                  >
                    Simulate
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}


