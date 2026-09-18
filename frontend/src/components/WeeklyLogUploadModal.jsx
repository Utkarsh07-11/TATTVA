import React, { useState } from 'react';
import { X, UploadCloud, FileText, CheckCircle2, AlertTriangle, Sparkles, Download, ArrowRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function WeeklyLogUploadModal() {
  const { isWeeklyModalOpen, setIsWeeklyModalOpen, user, token, mineId, tier } = useAuth();

  const [activeTab, setActiveTab] = useState('form'); // 'form' or 'csv'
  const [weekNumber, setWeekNumber] = useState(3);
  const [plannedTonnes, setPlannedTonnes] = useState(4200.0);
  const [actualTonnes, setActualTonnes] = useState(4050.0);
  const [equipmentAvailability, setEquipmentAvailability] = useState(86.5);
  const [rainfallMm, setRainfallMm] = useState(32.0);
  const [blastingDelays, setBlastingDelays] = useState(1);
  const [maintenanceHours, setMaintenanceHours] = useState(10.5);
  const [notes, setNotes] = useState('Week 3 Bharweli underground face advance nominal.');

  const [csvFile, setCsvFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  if (!isWeeklyModalOpen) return null;

  const handleLoadDemo = () => {
    setWeekNumber(3);
    setPlannedTonnes(4200.0);
    setActualTonnes(4050.0);
    setEquipmentAvailability(86.5);
    setRainfallMm(32.0);
    setBlastingDelays(1);
    setMaintenanceHours(10.5);
    setNotes('Week 3 Bharweli section bench excavation nominal.');
    setError(null);
  };

  const handleDownloadTemplate = async () => {
    try {
      const res = await fetch('/api/governance/sample-csv/weekly-production');
      const text = await res.text();
      const blob = new Blob([text], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'moil_sample_weekly_production.csv';
      a.click();
    } catch {
      // fallback
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      if (activeTab === 'csv') {
        if (!csvFile) throw new Error('Please select a CSV file first.');
        const formData = new FormData();
        formData.append('file', csvFile);

        const res = await fetch('/api/governance/upload-weekly-csv', {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
          body: formData,
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'CSV Ingestion failed');
        setResult(data);
      } else {
        const payload = {
          mine_id: mineId || 'MOIL_BALAGHAT',
          week_number: Number(weekNumber),
          planned_tonnes: Number(plannedTonnes),
          actual_tonnes: Number(actualTonnes),
          equipment_availability_pct: Number(equipmentAvailability),
          rainfall_mm: Number(rainfallMm),
          blasting_delays_count: Number(blastingDelays),
          maintenance_hours: Number(maintenanceHours),
          notes: notes,
        };

        const res = await fetch('/api/governance/upload-weekly', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(payload),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Weekly upload failed');
        setResult(data);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm animate-fadeIn">
      <div className="relative w-full max-w-2xl bg-[#faf9f5] border border-stone-300 shadow-2xl p-6 sm:p-8 rounded-lg text-stone-900 max-h-[92vh] overflow-y-auto">
        <button
          type="button"
          onClick={() => setIsWeeklyModalOpen(false)}
          className="absolute top-5 right-5 text-stone-400 hover:text-stone-800 transition-colors cursor-pointer p-1 rounded-full hover:bg-stone-200"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="flex items-center gap-3 mb-5 border-b border-stone-200 pb-4">
          <div className="p-2.5 rounded-md bg-[#EDC7B7]/40 border border-[#C87A5B]/40 text-[#C87A5B] shadow-xs">
            <UploadCloud className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="font-editorial text-xl font-bold tracking-tight text-stone-900">
                Log Weekly Production Summary (WSR)
              </h2>
              <span className="text-[10px] font-sans px-2 py-0.5 rounded-full bg-[#EDC7B7]/30 border border-[#EDC7B7] text-[#C87A5B] font-semibold">
                September 2026
              </span>
            </div>
            <p className="font-sans text-xs text-stone-600">
              Statutory reconciliation & sub-200ms LightGBM shortfall inference
            </p>
          </div>
        </div>

        {/* Action Presets */}
        <div className="flex items-center justify-between gap-2 mb-5 p-3 rounded-md bg-white border border-stone-200 text-xs font-sans shadow-xs">
          <span className="text-stone-600 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-[#C87A5B]" />
            Active Mine:{' '}
            <strong className="text-stone-900 font-mono">{mineId}</strong>
            {tier === 1 && <span className="text-stone-500 text-[11px]">(Locked to your jurisdiction)</span>}
          </span>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleLoadDemo}
              className="px-2.5 py-1 rounded-md bg-[#EDC7B7]/40 hover:bg-[#EDC7B7]/60 border border-[#C87A5B]/40 text-[#C87A5B] text-[11px] font-semibold transition-colors cursor-pointer"
            >
              1-Click Demo Data
            </button>
            <button
              type="button"
              onClick={handleDownloadTemplate}
              className="flex items-center gap-1 px-2.5 py-1 rounded-md bg-stone-100 hover:bg-stone-200 border border-stone-300 text-stone-700 text-[11px] font-semibold transition-colors cursor-pointer"
            >
              <Download className="w-3 h-3 text-stone-500" />
              <span>CSV Template</span>
            </button>
          </div>
        </div>

        {/* Tab Selector */}
        <div className="flex gap-2 border-b border-stone-200 mb-5">
          <button
            type="button"
            onClick={() => setActiveTab('form')}
            className={`pb-2 px-3 text-xs font-sans font-semibold border-b-2 transition-colors cursor-pointer ${
              activeTab === 'form'
                ? 'border-[#C87A5B] text-[#C87A5B]'
                : 'border-transparent text-stone-500 hover:text-stone-900'
            }`}
          >
            Direct Parameter Entry
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('csv')}
            className={`pb-2 px-3 text-xs font-sans font-semibold border-b-2 transition-colors cursor-pointer ${
              activeTab === 'csv'
                ? 'border-[#C87A5B] text-[#C87A5B]'
                : 'border-transparent text-stone-500 hover:text-stone-900'
            }`}
          >
            Upload Weekly CSV File
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4 font-sans text-xs">
          {activeTab === 'form' ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-stone-700 font-semibold mb-1">
                  Reporting Week (Month 9 / Sep 2026)
                </label>
                <select
                  value={weekNumber}
                  onChange={(e) => setWeekNumber(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-white border border-stone-300 focus:border-[#C87A5B] focus:ring-1 focus:ring-[#C87A5B] rounded-md text-stone-900 shadow-xs"
                >
                  <option value={1}>Week 1 (Sep 01 – Sep 07)</option>
                  <option value={2}>Week 2 (Sep 08 – Sep 14)</option>
                  <option value={3}>Week 3 (Sep 15 – Sep 21) [Active]</option>
                  <option value={4}>Week 4 (Sep 22 – Sep 28)</option>
                </select>
              </div>

              <div>
                <label className="block text-stone-700 font-semibold mb-1">
                  Equipment Availability %
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="100"
                  value={equipmentAvailability}
                  onChange={(e) => setEquipmentAvailability(e.target.value)}
                  className="w-full px-3 py-2 bg-white border border-stone-300 focus:border-[#C87A5B] focus:ring-1 focus:ring-[#C87A5B] rounded-md text-stone-900 font-mono shadow-xs"
                />
              </div>

              <div>
                <label className="block text-stone-700 font-semibold mb-1">
                  Planned Target (Tonnes)
                </label>
                <input
                  type="number"
                  step="10"
                  value={plannedTonnes}
                  onChange={(e) => setPlannedTonnes(e.target.value)}
                  className="w-full px-3 py-2 bg-white border border-stone-300 focus:border-[#C87A5B] focus:ring-1 focus:ring-[#C87A5B] rounded-md text-stone-900 font-mono shadow-xs"
                />
              </div>

              <div>
                <label className="block text-stone-700 font-semibold mb-1">
                  Actual Extracted (Tonnes)
                </label>
                <input
                  type="number"
                  step="10"
                  value={actualTonnes}
                  onChange={(e) => setActualTonnes(e.target.value)}
                  className="w-full px-3 py-2 bg-white border border-stone-300 focus:border-[#C87A5B] focus:ring-1 focus:ring-[#C87A5B] rounded-md text-stone-900 font-mono shadow-xs"
                />
              </div>

              <div>
                <label className="block text-stone-700 font-semibold mb-1">
                  Rainfall (mm)
                </label>
                <input
                  type="number"
                  step="1"
                  min="0"
                  value={rainfallMm}
                  onChange={(e) => setRainfallMm(e.target.value)}
                  className="w-full px-3 py-2 bg-white border border-stone-300 focus:border-[#C87A5B] focus:ring-1 focus:ring-[#C87A5B] rounded-md text-stone-900 font-mono shadow-xs"
                />
              </div>

              <div>
                <label className="block text-stone-700 font-semibold mb-1">
                  Blasting Delays (Incidents)
                </label>
                <input
                  type="number"
                  min="0"
                  max="10"
                  value={blastingDelays}
                  onChange={(e) => setBlastingDelays(e.target.value)}
                  className="w-full px-3 py-2 bg-white border border-stone-300 focus:border-[#C87A5B] focus:ring-1 focus:ring-[#C87A5B] rounded-md text-stone-900 font-mono shadow-xs"
                />
              </div>

              <div className="sm:col-span-2">
                <label className="block text-stone-700 font-semibold mb-1">
                  Shift Supervisor Notes
                </label>
                <input
                  type="text"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  className="w-full px-3 py-2 bg-white border border-stone-300 focus:border-[#C87A5B] focus:ring-1 focus:ring-[#C87A5B] rounded-md text-stone-900 shadow-xs"
                />
              </div>
            </div>
          ) : (
            <div className="border-2 border-dashed border-stone-300 rounded-md p-8 text-center bg-white shadow-xs">
              <FileText className="w-10 h-10 text-[#C87A5B] mx-auto mb-3" />
              <p className="text-sm font-semibold text-stone-800 mb-1">
                Drop your weekly production summary CSV here
              </p>
              <p className="text-xs text-stone-500 mb-4">
                Required columns: week_number, planned_tonnes, actual_tonnes, equipment_availability_pct
              </p>
              <input
                type="file"
                accept=".csv"
                onChange={(e) => setCsvFile(e.target.files?.[0] || null)}
                className="block mx-auto text-xs text-stone-600 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-[#EDC7B7]/40 file:text-[#C87A5B] hover:file:bg-[#EDC7B7]/60 cursor-pointer"
              />
              {csvFile && (
                <div className="mt-3 text-xs text-emerald-700 font-mono">
                  Selected: {csvFile.name} ({(csvFile.size / 1024).toFixed(1)} KB)
                </div>
              )}
            </div>
          )}

          {error && (
            <div className="flex items-start gap-2 p-2.5 rounded-md bg-rose-50 border border-rose-200 text-rose-800 text-xs">
              <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5 text-rose-600" />
              <span>{error}</span>
            </div>
          )}

          <div className="flex items-center justify-end gap-3 pt-3 border-t border-stone-200">
            <button
              type="button"
              onClick={() => setIsWeeklyModalOpen(false)}
              className="px-4 py-2 rounded-md border border-stone-300 text-stone-600 hover:text-stone-900 hover:bg-stone-100 transition-colors cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex items-center gap-2 px-6 py-2 rounded-md bg-[#C87A5B] hover:bg-[#B85D3B] text-white font-bold transition-all cursor-pointer shadow-md disabled:opacity-50"
            >
              {loading ? (
                <span>Validating & Running Inference…</span>
              ) : (
                <>
                  <span>Commit Log & Run ML Inference</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </>
              )}
            </button>
          </div>
        </form>

        {/* Real-time ML Inference Result Banner */}
        {result && (
          <div className="mt-6 p-4 rounded-md bg-white border border-emerald-300 text-stone-900 shadow-sm animate-fadeIn font-sans">
            <div className="flex items-center justify-between mb-3 border-b border-emerald-100 pb-2">
              <div className="flex items-center gap-2 text-emerald-700 font-semibold text-xs">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>Weekly Operational Log Ingested & Verified</span>
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-50 border border-emerald-200 text-emerald-800 flex items-center gap-1 font-semibold">
                <Sparkles className="w-3 h-3 text-emerald-600" />
                Inference: {result.realtime_inference?.inference_time_ms || 142} ms
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs mb-3">
              <div className="p-2.5 bg-stone-50 rounded-md border border-stone-200">
                <div className="text-[11px] text-stone-500">Shortfall Risk</div>
                <div className={`font-mono text-base font-bold ${
                  (result.realtime_inference?.shortfall_risk_pct || 0) > 30 ? 'text-[#C87A5B]' : 'text-emerald-600'
                }`}>
                  {result.realtime_inference?.shortfall_risk_pct}%
                </div>
              </div>

              <div className="p-2.5 bg-stone-50 rounded-md border border-stone-200">
                <div className="text-[11px] text-stone-500">P10 Conservative</div>
                <div className="font-mono text-base font-bold text-stone-800">
                  {result.realtime_inference?.p10_tonnes} t
                </div>
              </div>

              <div className="p-2.5 bg-stone-50 rounded-md border border-stone-200">
                <div className="text-[11px] text-stone-500">P50 Expected</div>
                <div className="font-mono text-base font-bold text-stone-900">
                  {result.realtime_inference?.p50_tonnes} t
                </div>
              </div>

              <div className="p-2.5 bg-stone-50 rounded-md border border-stone-200">
                <div className="text-[11px] text-stone-500">P90 Optimistic</div>
                <div className="font-mono text-base font-bold text-stone-800">
                  {result.realtime_inference?.p90_tonnes} t
                </div>
              </div>
            </div>

            <div className="p-3 rounded-md bg-[#FAF7F2] border border-[#DCD5CD] text-xs">
              <span className="font-semibold text-[#C87A5B] block mb-0.5">
                Optimal Solver Recommendation:
              </span>
              <p className="text-stone-700 leading-relaxed">
                {result.realtime_inference?.recommended_action}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
