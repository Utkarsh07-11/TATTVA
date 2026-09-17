import React, { useState, useEffect } from 'react';
import { AlertCircle } from 'lucide-react';
import { api } from '../services/api';

export default function ResourceExplorer() {
  const [cutoffGrade, setCutoffGrade] = useState(20.0);
  const [resource, setResource] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function loadResource() {
      setLoading(true);
      try {
        const res = await api.getResourceEstimate(cutoffGrade);
        setResource(res);
      } catch (e) {
        console.error('Resource estimate error:', e);
      } finally {
        setLoading(false);
      }
    }
    loadResource();
  }, [cutoffGrade]);

  return (
    <div className="bg-white rounded-xl p-4 space-y-4 max-w-4xl mx-auto border border-[#DCD5CD] shadow-sm">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2.5 border-b border-[#DCD5CD]">
        <h2 className="text-xs sm:text-sm font-bold text-[#26211F] font-mono uppercase tracking-wide">
          Geostatistical Resource Modeling
        </h2>

        {/* Cutoff Grade Selector */}
        <div className="flex items-center gap-1.5 text-xs font-mono bg-[#FAF7F2] px-2 py-1 rounded-md border border-[#DCD5CD]">
          <span className="text-[#8A817D]">Cutoff:</span>
          {[15, 20, 25, 30].map((grade) => (
            <button
              key={grade}
              onClick={() => setCutoffGrade(grade)}
              className={`px-2 py-0.5 rounded transition-colors cursor-pointer ${
                cutoffGrade === grade
                  ? 'bg-[#C87A5B] text-white font-bold'
                  : 'text-[#5A524F] hover:text-[#26211F]'
              }`}
            >
              {grade}%
            </button>
          ))}
        </div>
      </div>

      {/* Resource Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
        <div className="bg-[#FAF7F2] p-3 rounded-lg border border-[#DCD5CD]">
          <div className="text-[10px] font-mono text-[#8A817D] uppercase">Inferred Tonnage</div>
          <div className="text-xl font-bold font-mono text-[#26211F] mt-1">
            {resource ? `${resource.total_inferred_tonnes.toLocaleString()} t` : '...'}
          </div>
          <div className="text-[10px] font-mono text-[#8A817D] mt-1">
            Specific gravity: 3.6 t/m³
          </div>
        </div>

        <div className="bg-[#FAF7F2] p-3 rounded-lg border border-[#DCD5CD]">
          <div className="text-[10px] font-mono text-[#8A817D] uppercase">Average Grade</div>
          <div className="text-xl font-bold font-mono text-[#26211F] mt-1">
            {resource ? `${resource.average_grade_pct}% Mn` : '...'}
          </div>
          <div className="text-[10px] font-mono text-[#8A817D] mt-1">
            Thickness-weighted
          </div>
        </div>

        <div className="bg-[#FAF7F2] p-3 rounded-lg border border-[#DCD5CD]">
          <div className="text-[10px] font-mono text-[#8A817D] uppercase">In-Situ Volume</div>
          <div className="text-xl font-bold font-mono text-[#26211F] mt-1">
            {resource ? `${resource.ore_volume_m3.toLocaleString()} m³` : '...'}
          </div>
          <div className="text-[10px] font-mono text-[#8A817D] mt-1">
            Sampled cells: {resource?.cell_count || 0}
          </div>
        </div>
      </div>

      {/* Strict Caveat Callout */}
      <div className="bg-[#FAF7F2] border border-[#DCD5CD] rounded-lg p-2.5 text-[11px] text-[#5A524F] flex items-start gap-2 font-sans">
        <AlertCircle className="w-4 h-4 text-[#C87A5B] shrink-0 mt-0.5" />
        <div>
          <span className="font-bold text-[#26211F]">Reserve vs. Resource Caveat: </span>
          {resource?.caveat || 'Illustrative geostatistical toy resource estimate, not a certified reserve. Requires dense infill drilling and engineering feasibility.'}
        </div>
      </div>
    </div>
  );
}

