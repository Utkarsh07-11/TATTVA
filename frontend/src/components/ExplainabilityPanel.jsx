import React from 'react';
import { HelpCircle, AlertCircle, Cpu, CheckCircle } from 'lucide-react';

export default function ExplainabilityPanel({ explanation }) {
  if (!explanation) return null;

  const { contributors = [], narrative = '', note = '' } = explanation;

  // Colors for operational categories
  const getBarColor = (factor) => {
    switch (factor) {
      case 'equipment_downtime':
        return 'from-red-500 to-rose-600';
      case 'blasting_delay':
        return 'from-amber-500 to-orange-600';
      case 'rainfall_forecast':
        return 'from-blue-500 to-cyan-600';
      case 'equipment_availability':
        return 'from-purple-500 to-indigo-600';
      default:
        return 'from-slate-500 to-slate-600';
    }
  };

  return (
    <div className="panel p-5">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Cpu className="w-5 h-5 text-purple-400" />
          <h2 className="text-base font-bold text-white">
            Root-Cause Attribution (SHAP TreeExplainer)
          </h2>
        </div>
        <span className="text-xs text-slate-400">
          Normalized Feature Contributions (%)
        </span>
      </div>

      <p className="text-xs text-slate-400 mb-4">
        Decomposition of forecasted production shortfall into operational model drivers.
      </p>

      {/* Contributor Bars */}
      <div className="space-y-3 mb-5">
        {contributors.map((c) => (
          <div key={c.factor}>
            <div className="flex items-center justify-between text-xs mb-1">
              <span className="font-semibold text-slate-200">{c.label}</span>
              <div className="flex items-center gap-2">
                <span className="text-slate-400 font-mono">
                  ~{c.raw_impact_tonnes} t deficit
                </span>
                <span className="font-bold text-white w-10 text-right">
                  {c.contribution_pct}%
                </span>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
              <div
                className={`h-full bg-gradient-to-r ${getBarColor(c.factor)} rounded-full transition-all duration-500`}
                style={{ width: `${c.contribution_pct}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Mining Narrative Translation */}
      <div className="bg-slate-800/80 border border-slate-700/80 rounded-lg p-3.5 mb-3 text-xs leading-relaxed text-slate-300">
        <div className="font-bold text-indigo-400 mb-1 flex items-center gap-1.5">
          <span>Operational Interpretation:</span>
        </div>
        <p>{narrative}</p>
      </div>

      {/* Attribution vs Causation Disclaimer */}
      <div className="bg-amber-950/40 border border-amber-800/50 rounded-lg p-3 text-[11px] text-amber-300/90 flex items-start gap-2">
        <AlertCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-bold">Engineering Governance Note: </span>
          {note || 'Model-attributed contributions (SHAP), not verified physical causation. Cross-check against shift logs before executive signoff.'}
        </div>
      </div>
    </div>
  );
}
