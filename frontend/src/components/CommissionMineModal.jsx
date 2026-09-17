import React, { useState } from 'react';
import { X, PlusCircle, MapPin, CheckCircle2, AlertCircle, Compass, Building2, Sparkles } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function CommissionMineModal() {
  const { isCommissionModalOpen, setIsCommissionModalOpen, token, isApex } = useAuth();

  const [mineName, setMineName] = useState('Barbil Manganese Horizon');
  const [state, setState] = useState('Odisha');
  const [district, setDistrict] = useState('Keonjhar');
  const [latitude, setLatitude] = useState('22.1150');
  const [longitude, setLongitude] = useState('85.3850');
  const [leaseAreaHa, setLeaseAreaHa] = useState('145.0');
  const [miningMethod, setMiningMethod] = useState('Opencast');
  const [annualTargetTonnes, setAnnualTargetTonnes] = useState('60000');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  if (!isCommissionModalOpen) return null;

  const getSemanticPrefix = () => {
    const st = (state || 'IN').trim().toUpperCase().slice(0, 2);
    const dist = (district || 'M').trim().toUpperCase().slice(0, 1);
    return `${st}${dist}`;
  };

  const semanticPrefix = getSemanticPrefix();

  const handleFillPreset = (preset) => {
    if (preset === 'ODISHA') {
      setMineName('Barbil Manganese Horizon');
      setState('Odisha');
      setDistrict('Keonjhar');
      setLatitude('22.1150');
      setLongitude('85.3850');
      setLeaseAreaHa('160.0');
      setMiningMethod('Opencast');
      setAnnualTargetTonnes('65000');
    } else if (preset === 'KARNATAKA') {
      setMineName('Sandur South Ridge Block');
      setState('Karnataka');
      setDistrict('Bellary');
      setLatitude('15.0833');
      setLongitude('76.5500');
      setLeaseAreaHa('125.0');
      setMiningMethod('Opencast');
      setAnnualTargetTonnes('50000');
    }
    setError(null);
    setResult(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const payload = {
        mine_name: mineName.trim(),
        state: state.trim(),
        district: district.trim(),
        latitude: parseFloat(latitude),
        longitude: parseFloat(longitude),
        lease_area_ha: parseFloat(leaseAreaHa),
        mining_method: miningMethod,
        annual_target_tonnes: parseFloat(annualTargetTonnes),
      };

      const res = await fetch('/api/governance/commission-mine', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to commission mine');
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm animate-fadeIn">
      <div className="relative w-full max-w-xl bg-[#faf9f5] border border-stone-300 shadow-2xl p-6 sm:p-8 rounded-lg text-stone-900 max-h-[92vh] overflow-y-auto">
        <button
          type="button"
          onClick={() => setIsCommissionModalOpen(false)}
          className="absolute top-5 right-5 text-stone-400 hover:text-stone-800 transition-colors cursor-pointer p-1 rounded-full hover:bg-stone-200"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="flex items-center gap-3 mb-5 border-b border-stone-200 pb-4">
          <div className="p-2.5 rounded-md bg-purple-100 border border-purple-300 text-purple-800 shadow-xs">
            <PlusCircle className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="font-editorial text-xl font-bold tracking-tight text-stone-900">
                Commission New Mining Lease
              </h2>
              <span className="text-[10px] font-sans px-2 py-0.5 rounded-full bg-purple-100 border border-purple-300 text-purple-900 font-semibold">
                Tier 3 · Apex Authority
              </span>
            </div>
            <p className="font-sans text-xs text-stone-600">
              Zero-code dynamic onboarding to MOIL National Mineral Grid
            </p>
          </div>
        </div>

        {/* Preset Quick Fill */}
        <div className="flex items-center justify-between p-3 rounded-md bg-white border border-stone-200 text-xs font-sans mb-5 shadow-xs">
          <span className="text-stone-600 font-medium">Expansion Presets:</span>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => handleFillPreset('ODISHA')}
              className="px-2.5 py-1 rounded-md bg-purple-50 hover:bg-purple-100 border border-purple-200 text-purple-800 text-[11px] font-semibold transition-colors cursor-pointer"
            >
              Barbil (Odisha)
            </button>
            <button
              type="button"
              onClick={() => handleFillPreset('KARNATAKA')}
              className="px-2.5 py-1 rounded-md bg-purple-50 hover:bg-purple-100 border border-purple-200 text-purple-800 text-[11px] font-semibold transition-colors cursor-pointer"
            >
              Sandur (Karnataka)
            </button>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4 font-sans text-xs">
          <div>
            <label className="block text-stone-700 font-semibold mb-1">Mine Lease Name</label>
            <input
              type="text"
              required
              value={mineName}
              onChange={(e) => setMineName(e.target.value)}
              className="w-full px-3 py-2 bg-white border border-stone-300 focus:border-purple-600 focus:ring-1 focus:ring-purple-500 rounded-md text-stone-900 shadow-xs"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-stone-700 font-semibold mb-1">State</label>
              <input
                type="text"
                required
                value={state}
                onChange={(e) => setState(e.target.value)}
                className="w-full px-3 py-2 bg-white border border-stone-300 focus:border-purple-600 focus:ring-1 focus:ring-purple-500 rounded-md text-stone-900 shadow-xs"
              />
            </div>

            <div>
              <label className="block text-stone-700 font-semibold mb-1">District</label>
              <input
                type="text"
                required
                value={district}
                onChange={(e) => setDistrict(e.target.value)}
                className="w-full px-3 py-2 bg-white border border-stone-300 focus:border-purple-600 focus:ring-1 focus:ring-purple-500 rounded-md text-stone-900 shadow-xs"
              />
            </div>

            <div>
              <label className="block text-stone-700 font-semibold mb-1">Latitude (°N)</label>
              <input
                type="number"
                step="0.0001"
                required
                value={latitude}
                onChange={(e) => setLatitude(e.target.value)}
                className="w-full px-3 py-2 bg-white border border-stone-300 focus:border-purple-600 focus:ring-1 focus:ring-purple-500 rounded-md text-stone-900 font-mono shadow-xs"
              />
            </div>

            <div>
              <label className="block text-stone-700 font-semibold mb-1">Longitude (°E)</label>
              <input
                type="number"
                step="0.0001"
                required
                value={longitude}
                onChange={(e) => setLongitude(e.target.value)}
                className="w-full px-3 py-2 bg-white border border-stone-300 focus:border-purple-600 focus:ring-1 focus:ring-purple-500 rounded-md text-stone-900 font-mono shadow-xs"
              />
            </div>

            <div>
              <label className="block text-stone-700 font-semibold mb-1">Lease Area (Hectares)</label>
              <input
                type="number"
                step="0.1"
                required
                value={leaseAreaHa}
                onChange={(e) => setLeaseAreaHa(e.target.value)}
                className="w-full px-3 py-2 bg-white border border-stone-300 focus:border-purple-600 focus:ring-1 focus:ring-purple-500 rounded-md text-stone-900 font-mono shadow-xs"
              />
            </div>

            <div>
              <label className="block text-stone-700 font-semibold mb-1">Annual Target (Tonnes)</label>
              <input
                type="number"
                step="1000"
                required
                value={annualTargetTonnes}
                onChange={(e) => setAnnualTargetTonnes(e.target.value)}
                className="w-full px-3 py-2 bg-white border border-stone-300 focus:border-purple-600 focus:ring-1 focus:ring-purple-500 rounded-md text-stone-900 font-mono shadow-xs"
              />
            </div>
          </div>

          {/* Semantic Prefix Preview Badge */}
          <div className="p-3.5 rounded-md bg-purple-50 border border-purple-200 flex items-center justify-between">
            <div>
              <span className="text-stone-600 block text-[11px]">Auto-Generated Semantic Prefix:</span>
              <span className="font-mono text-base font-bold text-purple-900">{semanticPrefix}</span>
            </div>
            <div className="text-right">
              <span className="text-stone-600 block text-[11px]">Future Operator ID Format:</span>
              <span className="font-mono text-xs font-semibold text-stone-900">
                {semanticPrefix}260001
              </span>
            </div>
          </div>

          {error && (
            <div className="flex items-start gap-2 p-2.5 rounded-md bg-rose-50 border border-rose-200 text-rose-800 text-xs">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-600" />
              <span>{error}</span>
            </div>
          )}

          <div className="flex items-center justify-end gap-3 pt-3 border-t border-stone-200">
            <button
              type="button"
              onClick={() => setIsCommissionModalOpen(false)}
              className="px-4 py-2 rounded-md border border-stone-300 text-stone-600 hover:text-stone-900 hover:bg-stone-100 transition-colors cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 rounded-md bg-purple-700 hover:bg-purple-800 text-white font-bold transition-all cursor-pointer disabled:opacity-50 shadow-md"
            >
              {loading ? 'Commissioning Lease…' : 'Authorize & Commission Mine'}
            </button>
          </div>
        </form>

        {/* Confirmation */}
        {result && (
          <div className="mt-5 p-4 rounded-md bg-white border border-purple-200 text-stone-900 shadow-sm animate-fadeIn font-sans text-xs">
            <div className="flex items-center gap-2 text-purple-800 font-semibold mb-2">
              <CheckCircle2 className="w-4 h-4 text-purple-700" />
              <span>{result.message}</span>
            </div>
            <div className="space-y-1 text-stone-700 font-mono text-[11px]">
              <div>Mine ID: <strong className="text-stone-900">{result.commissioned_mine?.mine_id}</strong></div>
              <div>Semantic Prefix: <strong className="text-purple-800">{result.commissioned_mine?.semantic_prefix}</strong></div>
              <div>Example Site Operator: <strong className="text-stone-900">{result.commissioned_mine?.example_operator_id}</strong></div>
            </div>
            <p className="mt-2 text-stone-500 text-[11px]">
              The new lease is activated and immediately accessible in the Weekly Compliance Matrix.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
