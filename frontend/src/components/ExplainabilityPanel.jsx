import React, { useState } from 'react';
import { ChevronDown, AlertCircle } from 'lucide-react';

export default function ExplainabilityPanel({ explanation }) {
  const [showDetails, setShowDetails] = useState(false);
  if (!explanation) return null;

  const { contributors = [], narrative = '', note = '' } = explanation;
  const primaryDriver = contributors[0] || { label: 'Equipment Availability', raw_impact_tonnes: 580, contribution_pct: 45 };

  return (
    <div className="space-y-3 max-w-4xl mx-auto">
      {/* 1. DECISION-FIRST PRIMARY DRIVER BANNER */}
      <div className="bg-[#080b10] border border-technical p-4 sm:p-5 rounded flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="text-[10px] font-mono uppercase tracking-wider text-slate-400">
            Primary Production Driver
          </div>
          <div className="text-xl sm:text-2xl font-bold font-mono text-white">
            {primaryDriver.label}
          </div>
          <div className="text-xs text-slate-400">
            Contributes {primaryDriver.contribution_pct}% to forecasted shortfall.
          </div>
        </div>

        <div className="flex items-center gap-4 sm:border-l sm:border-technical sm:pl-5">
          <div>
            <div className="text-[10px] font-mono uppercase tracking-wider text-slate-400">
              Impact Deficit
            </div>
            <div className="text-xl sm:text-2xl font-bold font-mono text-rose-400">
              -{primaryDriver.raw_impact_tonnes} t
            </div>
          </div>
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="px-3 py-1.5 rounded bg-[#101622] hover:bg-[#182233] border border-technical text-slate-200 text-xs font-mono flex items-center gap-1.5 transition-colors cursor-pointer self-start sm:self-auto ml-auto"
          >
            <span>{showDetails ? 'Hide Details' : 'View Explanation'}</span>
            <ChevronDown className={`w-3.5 h-3.5 transition-transform ${showDetails ? 'rotate-180' : ''}`} />
          </button>
        </div>
      </div>

      {/* 2. DETAILED CONTRIBUTOR BREAKDOWN & NARRATIVE */}
      <div className="panel p-4 space-y-4">
        <div className="flex items-center justify-between pb-2 border-b border-technical">
          <h2 className="text-xs sm:text-sm font-bold text-white font-mono uppercase tracking-wide">
            Root Cause Attribution (SHAP TreeExplainer)
          </h2>
          <span className="text-[10px] font-mono text-slate-500">
            Normalized Contributions (%)
          </span>
        </div>

        {/* Contributor Bars */}
        <div className="space-y-2.5">
          {contributors.map((c) => (
            <div key={c.factor} className="bg-[#080b10] p-2.5 rounded border border-technical">
              <div className="flex items-center justify-between text-xs mb-1.5">
                <span className="font-semibold text-slate-200">{c.label}</span>
                <div className="flex items-center gap-2">
                  <span className="text-slate-400 font-mono text-[11px]">
                    ~{c.raw_impact_tonnes} t deficit
                  </span>
                  <span className="font-mono font-bold text-white w-10 text-right">
                    {c.contribution_pct}%
                  </span>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="w-full bg-[#05070a] h-1.5 rounded overflow-hidden border border-technical">
                <div
                  className="h-full bg-industrial-amber transition-all duration-300"
                  style={{ width: `${c.contribution_pct}%` }}
                />
              </div>
            </div>
          ))}
        </div>

        {/* Mining Narrative Translation */}
        {narrative && (
          <div className="bg-[#080b10] border border-technical rounded p-3 text-xs text-slate-300 font-sans leading-relaxed">
            <div className="font-mono text-slate-400 mb-1 text-[10px] uppercase tracking-wider">
              Operational Interpretation:
            </div>
            <p>{narrative}</p>
          </div>
        )}

        {/* Attribution vs Causation Disclaimer */}
        <div className="bg-[#0e0c08] border border-amber-900/40 rounded p-2.5 text-[11px] text-amber-300/90 flex items-start gap-2">
          <AlertCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
          <div>
            <span className="font-bold">Engineering Governance Note: </span>
            {note || 'Model-attributed contributions (SHAP), not verified physical causation. Cross-check against shift logs before executive signoff.'}
          </div>
        </div>
      </div>
    </div>
  );
}


