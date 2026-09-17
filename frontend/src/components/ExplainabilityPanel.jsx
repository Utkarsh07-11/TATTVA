import React, { useState } from 'react';
import { ChevronDown, AlertCircle } from 'lucide-react';

export default function ExplainabilityPanel({ explanation }) {
  const [showDetails, setShowDetails] = useState(false);
  if (!explanation) return null;

  const { contributors = [], narrative = '', note = '' } = explanation;
  const primaryDriver = contributors[0] || { label: 'Equipment Availability', raw_impact_tonnes: 580, contribution_pct: 45 };

  return (
    <div className="space-y-3 max-w-4xl mx-auto font-sans">
      {/* 1. DECISION-FIRST PRIMARY DRIVER BANNER */}
      <div className="bg-[#FAF7F2] border border-[#DCD5CD] p-4 sm:p-5 rounded-xl shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="text-xs font-sans uppercase tracking-wider text-[#8A817D]">
            Primary Production Driver
          </div>
          <div className="text-xl sm:text-2xl font-bold font-sans text-[#26211F]">
            {primaryDriver.label}
          </div>
          <div className="text-xs text-[#5A524F] font-sans">
            Contributes {primaryDriver.contribution_pct}% to forecasted shortfall.
          </div>
        </div>

        <div className="flex items-center gap-4 sm:border-l sm:border-[#DCD5CD] sm:pl-5">
          <div>
            <div className="text-xs font-sans uppercase tracking-wider text-[#8A817D]">
              Impact Deficit
            </div>
            <div className="text-xl sm:text-2xl font-bold font-sans text-rose-700">
              -{primaryDriver.raw_impact_tonnes} t
            </div>
          </div>
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="px-3 py-1.5 rounded-lg bg-white hover:bg-[#EEE6DD] border border-[#DCD5CD] text-[#5A524F] text-xs font-sans flex items-center gap-1.5 transition-colors cursor-pointer self-start sm:self-auto ml-auto"
          >
            <span>{showDetails ? 'Hide Details' : 'View Explanation'}</span>
            <ChevronDown className={`w-3.5 h-3.5 transition-transform ${showDetails ? 'rotate-180' : ''}`} />
          </button>
        </div>
      </div>

      {/* 2. DETAILED CONTRIBUTOR BREAKDOWN & NARRATIVE */}
      <div className="bg-white rounded-xl p-4 space-y-4 border border-[#DCD5CD] shadow-sm">
        <div className="flex items-center justify-between pb-2 border-b border-[#DCD5CD]">
          <h2 className="text-xs sm:text-sm font-bold text-[#26211F] font-sans uppercase tracking-wide">
            Operational Variance Factor Attribution
          </h2>
          <span className="text-xs font-sans text-[#8A817D]">
            Normalized Contributions (%)
          </span>
        </div>

        {/* Contributor Bars */}
        <div className="space-y-2.5">
          {contributors.map((c) => (
            <div key={c.factor} className="bg-[#FAF7F2] p-2.5 rounded-lg border border-[#DCD5CD]">
              <div className="flex items-center justify-between text-xs mb-1.5 font-sans">
                <span className="font-semibold text-[#26211F]">{c.label}</span>
                <div className="flex items-center gap-2">
                  <span className="text-[#8A817D] text-xs font-sans">
                    ~{c.raw_impact_tonnes} t deficit
                  </span>
                  <span className="font-sans font-bold text-[#C87A5B] w-10 text-right">
                    {c.contribution_pct}%
                  </span>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="w-full bg-[#EEE6DD] h-2 rounded-full overflow-hidden border border-[#DCD5CD]">
                <div
                  className="h-full bg-[#C87A5B] transition-all duration-300"
                  style={{ width: `${c.contribution_pct}%` }}
                />
              </div>
            </div>
          ))}
        </div>

        {/* Mining Narrative Translation */}
        {narrative && (
          <div className="bg-[#FAF7F2] border border-[#DCD5CD] rounded-lg p-3 text-xs text-[#5A524F] font-sans leading-relaxed">
            <div className="font-sans text-[#8A817D] mb-1 text-xs uppercase tracking-wider font-semibold">
              Operational Interpretation:
            </div>
            <p>{narrative}</p>
          </div>
        )}

        {/* Attribution vs Causation Disclaimer */}
        <div className="bg-[#FAF7F2] border border-[#DCD5CD] rounded-lg p-2.5 text-xs text-[#5A524F] flex items-start gap-2 font-sans">
          <AlertCircle className="w-4 h-4 text-[#C87A5B] shrink-0 mt-0.5" />
          <div>
            <span className="font-bold text-[#26211F]">Engineering Governance Note: </span>
            {note || 'Empirical variance attribution, not verified physical causation. Cross-check against shift logs before executive signoff.'}
          </div>
        </div>
      </div>
    </div>
  );
}
