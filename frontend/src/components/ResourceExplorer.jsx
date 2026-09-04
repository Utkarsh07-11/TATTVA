import React, { useState, useEffect } from 'react';
import { Database, AlertTriangle, Layers, Award } from 'lucide-react';
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
    <div className="panel p-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3">
        <div className="flex items-center gap-2">
          <Database className="w-5 h-5 text-purple-400" />
          <h2 className="text-base font-bold text-white">
            Geological Resource Estimation & Grade Modeling
          </h2>
        </div>

        {/* Cutoff Grade Selector */}
        <div className="flex items-center gap-2 text-xs bg-slate-800 px-2.5 py-1 rounded-lg border border-slate-700">
          <span className="text-slate-300 font-medium">Cutoff Grade:</span>
          {[15, 20, 25, 30].map((grade) => (
            <button
              key={grade}
              onClick={() => setCutoffGrade(grade)}
              className={`px-2 py-0.5 rounded font-semibold transition-all ${
                cutoffGrade === grade
                  ? 'bg-purple-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {grade}% Mn
            </button>
          ))}
        </div>
      </div>

      <p className="text-xs text-slate-400 mb-4">
        Inverse Distance Weighting (IDW) and Ordinary Kriging geostatistical interpolation across 240 assay collars.
      </p>

      {/* Resource Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-4">
        <div className="bg-slate-800/80 p-3.5 rounded-lg border border-slate-700">
          <div className="text-xs text-slate-400">Total Inferred Tonnage</div>
          <div className="text-xl font-black text-purple-300 mt-1">
            {resource ? `${resource.total_inferred_tonnes.toLocaleString()} t` : 'Loading...'}
          </div>
          <div className="text-[11px] text-slate-400 mt-0.5">
            Specific gravity: 3.6 t/m³ (Gondite/Mansar)
          </div>
        </div>

        <div className="bg-slate-800/80 p-3.5 rounded-lg border border-slate-700">
          <div className="text-xs text-slate-400">Average Ore Grade</div>
          <div className="text-xl font-black text-pink-400 mt-1">
            {resource ? `${resource.average_grade_pct}% Mn` : 'Loading...'}
          </div>
          <div className="text-[11px] text-slate-400 mt-0.5">
            Thickness-weighted mean grade
          </div>
        </div>

        <div className="bg-slate-800/80 p-3.5 rounded-lg border border-slate-700">
          <div className="text-xs text-slate-400">Estimated In-Situ Volume</div>
          <div className="text-xl font-black text-indigo-400 mt-1">
            {resource ? `${resource.ore_volume_m3.toLocaleString()} m³` : 'Loading...'}
          </div>
          <div className="text-[11px] text-slate-400 mt-0.5">
            Active mineralized cells: {resource?.cell_count || 0}
          </div>
        </div>
      </div>

      {/* Strict Caveat Callout */}
      <div className="bg-slate-800/60 border border-slate-700 rounded-lg p-3 text-xs text-slate-400 flex items-start gap-2.5">
        <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-bold text-slate-300">Reserve vs. Resource Caveat: </span>
          {resource?.caveat || 'Illustrative geostatistical toy resource estimate, not a certified reserve. Requires dense infill drilling and engineering feasibility.'}
        </div>
      </div>
    </div>
  );
}
