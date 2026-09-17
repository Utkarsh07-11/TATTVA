import React from 'react';
import { ArrowRight } from 'lucide-react';

export default function RecommendationsPanel({ recommendations, onApplyAction }) {
  if (!recommendations) return null;

  const {
    options = [],
    solver_status = 'Optimal'
  } = recommendations;

  const topRecommended = options.find((o) => o.lp_recommended) || options[0];

  return (
    <div className="space-y-3 max-w-4xl mx-auto font-sans">
      {/* 1. DECISION-FIRST DOMINANT RECOMMENDED ACTION */}
      {topRecommended && (
        <div className="bg-[#FAF7F2] border border-[#DCD5CD] p-4 sm:p-5 rounded-xl shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="text-xs font-sans uppercase tracking-wider text-[#8A817D]">
              Recommended Action · Optimized Dispatch
            </div>
            <div className="text-xl sm:text-2xl font-bold font-sans text-[#26211F]">
              {topRecommended.title}
            </div>
            <p className="text-xs text-[#5A524F] max-w-xl font-sans">
              {topRecommended.details}
            </p>
          </div>

          <div className="flex items-center gap-4 sm:border-l sm:border-[#DCD5CD] sm:pl-5 shrink-0">
            <div>
              <div className="text-[11px] font-sans uppercase tracking-wider text-[#8A817D]">
                Expected Recovery
              </div>
              <div className="text-xl sm:text-2xl font-bold font-sans text-emerald-700">
                +{topRecommended.expected_recovery_tonnes.toLocaleString()} t
              </div>
            </div>
            <button
              onClick={() => onApplyAction(topRecommended)}
              className="px-4 py-2 rounded-lg bg-[#C87A5B] hover:bg-[#B85D3B] text-white font-bold text-xs flex items-center gap-1.5 transition-colors cursor-pointer self-start sm:self-auto shadow-sm"
            >
              <span>Apply Scenario</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}

      {/* 2. RANKED ALTERNATIVE ACTIONS */}
      <div className="bg-white rounded-xl p-4 space-y-3 border border-[#DCD5CD] shadow-sm">
        <div className="flex items-center justify-between pb-2 border-b border-[#DCD5CD]">
          <h2 className="text-xs sm:text-sm font-bold text-[#26211F] font-sans uppercase tracking-wide">
            Ranked Intervention Options
          </h2>
          <span className="text-xs font-sans text-[#8A817D]">
            Optimization Engine: <strong className="text-[#26211F]">{solver_status}</strong>
          </span>
        </div>

        <div className="space-y-2">
          {options.map((opt) => (
            <div
              key={opt.action_id}
              className={`border rounded-lg p-3 transition-colors ${
                opt.lp_recommended
                  ? 'border-[#C87A5B] bg-[#FAF7F2]'
                  : 'border-[#DCD5CD] bg-white'
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-start gap-2.5">
                  <span className="text-xs font-sans font-bold text-[#8A817D] mt-0.5">
                    0{opt.rank}
                  </span>
                  <div>
                    <h3 className="text-xs font-bold text-[#26211F] flex items-center gap-2">
                      {opt.title}
                      {opt.lp_recommended && (
                        <span className="text-[#8C3A1E] bg-[#EDC7B7]/40 border border-[#C87A5B] px-1.5 py-0.2 rounded text-[10px] font-sans font-bold">
                          ● SELECTED
                        </span>
                      )}
                    </h3>
                    <p className="text-xs text-[#5A524F] mt-0.5 font-sans">
                      {opt.details}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3 shrink-0 self-end sm:self-auto font-sans text-xs">
                  <div className="text-right">
                    <span className="text-emerald-700 font-bold font-mono">+{opt.expected_recovery_tonnes.toLocaleString()} t</span>
                  </div>
                  <button
                    onClick={() => onApplyAction(opt)}
                    className="px-2.5 py-1 rounded-md bg-[#FAF7F2] hover:bg-[#EEE6DD] text-[#5A524F] hover:text-[#26211F] text-xs border border-[#DCD5CD] transition-colors cursor-pointer"
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
