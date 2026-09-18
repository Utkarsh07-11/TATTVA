import React, { useState } from 'react';
import { X, Shield, Lock, UserCheck, AlertCircle, CheckCircle2, ArrowRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import TattvaLogo from './TattvaLogo';

export default function LoginModal() {
  const { isLoginModalOpen, setIsLoginModalOpen, loginWithCredentials, user } = useAuth();

  const [employeeId, setEmployeeId] = useState('');
  const [pin, setPin] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState(null);

  if (!isLoginModalOpen) return null;

  const handleIdChange = (e) => {
    setEmployeeId(e.target.value.toUpperCase().replace(/\s+/g, ''));
    setError(null);
  };

  const getTierBadge = (id) => {
    const clean = id.trim().toUpperCase();
    if (/^IN[0-9]{3,8}$/.test(clean) || /^IN-[A-Z0-9]{3,8}$/.test(clean)) {
      return { text: 'Tier 3 · Apex Board / Ministry', color: 'bg-purple-100 text-purple-900 border-purple-300' };
    }
    if (clean.length === 10 && /^[A-Z]{3}[0-9]{7}$/.test(clean)) {
      return { text: 'Tier 2 · High Management / Directorate', color: 'bg-blue-100 text-blue-900 border-blue-300' };
    }
    if (clean.length === 9 && /^[A-Z]{3}[0-9]{6}$/.test(clean)) {
      return { text: 'Tier 1 · Mine Site Operations', color: 'bg-amber-100 text-amber-900 border-amber-300' };
    }
    return null;
  };

  const tierBadge = getTierBadge(employeeId);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    const res = await loginWithCredentials(employeeId, pin);
    setLoading(false);
    if (res.success) {
      setSuccessMsg(`Authenticated: ${res.user.full_name} (${res.user.role})`);
      setTimeout(() => {
        setSuccessMsg(null);
        setIsLoginModalOpen(false);
      }, 700);
    } else {
      setError(res.error);
    }
  };

  const handleFillPreset = (presetId, presetPin) => {
    setEmployeeId(presetId);
    setPin(presetPin);
    setError(null);
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm animate-fadeIn">
      {/* Crisp White / Warm Cream Enterprise Card */}
      <div className="relative w-full max-w-lg bg-[#faf9f5] border border-stone-300 shadow-2xl p-6 sm:p-8 rounded-lg text-stone-900">
        <button
          type="button"
          onClick={() => setIsLoginModalOpen(false)}
          className="absolute top-5 right-5 text-stone-400 hover:text-stone-800 transition-colors cursor-pointer p-1 rounded-full hover:bg-stone-200"
          aria-label="Close"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Corporate Header */}
        <div className="flex items-center gap-3.5 mb-5 border-b border-stone-200 pb-4">
          <div className="p-2 rounded-md bg-[#F7F4EF] border border-[#DCD5CD] text-[#26211F] shadow-xs shrink-0 flex items-center justify-center">
            <TattvaLogo className="w-8 h-8" />
          </div>
          <div>
            <h2 className="font-editorial text-2xl font-bold tracking-tight text-stone-900">
              MOIL Personnel Authentication
            </h2>
            <p className="font-sans text-xs text-stone-600">
              TATTVA Ore Intelligence · Regional Mine Jurisdiction
            </p>
          </div>
        </div>

        {/* 1-Click Evaluator Presets Bar */}
        <div className="mb-5 bg-white p-3.5 rounded-md border border-stone-200 shadow-xs">
          <div className="text-[11px] font-sans font-bold text-stone-500 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
            <UserCheck className="w-3.5 h-3.5 text-amber-600" />
            <span>1-Click Evaluator Presets</span>
          </div>
          <div className="grid grid-cols-1 gap-2 text-xs font-sans">
            <button
              type="button"
              onClick={() => handleFillPreset('MPB260001', '123456')}
              className="flex items-center justify-between p-2.5 rounded-md border border-stone-200 bg-stone-50/70 hover:bg-amber-50 hover:border-amber-400 text-left transition-all cursor-pointer group"
            >
              <div>
                <span className="font-bold text-stone-900 group-hover:text-amber-900">Tier 1 · Site Engineer</span>
                <span className="text-stone-500 ml-2">(Balaghat Mine)</span>
              </div>
              <span className="font-mono text-[11px] px-2 py-0.5 rounded bg-stone-200/80 text-stone-800 font-semibold border border-stone-300">
                MPB260001
              </span>
            </button>

            <button
              type="button"
              onClick={() => handleFillPreset('MHN2601001', '654321')}
              className="flex items-center justify-between p-2.5 rounded-md border border-stone-200 bg-stone-50/70 hover:bg-blue-50 hover:border-blue-400 text-left transition-all cursor-pointer group"
            >
              <div>
                <span className="font-bold text-stone-900 group-hover:text-blue-900">Tier 2 · HQ General Manager</span>
                <span className="text-stone-500 ml-2">(Nagpur HQ)</span>
              </div>
              <span className="font-mono text-[11px] px-2 py-0.5 rounded bg-stone-200/80 text-stone-800 font-semibold border border-stone-300">
                MHN2601001
              </span>
            </button>

            <button
              type="button"
              onClick={() => handleFillPreset('IN26009', '999999')}
              className="flex items-center justify-between p-2.5 rounded-md border border-stone-200 bg-stone-50/70 hover:bg-purple-50 hover:border-purple-400 text-left transition-all cursor-pointer group"
            >
              <div>
                <span className="font-bold text-stone-900 group-hover:text-purple-900">Tier 3 · Apex Board Owner</span>
                <span className="text-stone-500 ml-2">(National Grid)</span>
              </div>
              <span className="font-mono text-[11px] px-2 py-0.5 rounded bg-stone-200/80 text-stone-800 font-semibold border border-stone-300">
                IN26009
              </span>
            </button>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs font-sans font-semibold text-stone-800">
                Employee Identification Code
              </label>
              {tierBadge && (
                <span className={`text-[10px] font-sans font-semibold px-2 py-0.5 rounded border ${tierBadge.color}`}>
                  {tierBadge.text}
                </span>
              )}
            </div>
            <input
              type="text"
              required
              value={employeeId}
              onChange={handleIdChange}
              placeholder="e.g. MPB260001 or IN26009"
              className="w-full px-3.5 py-2.5 text-sm bg-white border border-stone-300 focus:border-amber-600 focus:ring-1 focus:ring-amber-500 focus:outline-none rounded-md font-mono text-stone-900 placeholder:text-stone-400 tracking-wider shadow-inner"
            />
            <p className="mt-1 text-[11px] text-stone-500 font-sans">
              Semantic syntax: [State 2 chars][Mine 1 char][Year 2 digits][Serial 4 digits].
            </p>
          </div>

          <div>
            <label className="block text-xs font-sans font-semibold text-stone-800 mb-1.5">
              6-Digit Security PIN
            </label>
            <div className="relative">
              <input
                type="password"
                required
                maxLength={8}
                value={pin}
                onChange={(e) => setPin(e.target.value)}
                placeholder="••••••"
                className="w-full px-3.5 py-2.5 text-sm bg-white border border-stone-300 focus:border-amber-600 focus:ring-1 focus:ring-amber-500 focus:outline-none rounded-md font-mono text-stone-900 tracking-widest shadow-inner"
              />
              <Lock className="w-4 h-4 text-stone-400 absolute right-3.5 top-3 pointer-events-none" />
            </div>
          </div>

          {error && (
            <div className="flex items-start gap-2 p-2.5 rounded-md bg-rose-50 border border-rose-200 text-rose-800 text-xs font-sans">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-600" />
              <span>{error}</span>
            </div>
          )}

          {successMsg && (
            <div className="flex items-center gap-2 p-2.5 rounded-md bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-sans">
              <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-600" />
              <span>{successMsg}</span>
            </div>
          )}

          <div className="pt-2 flex items-center justify-between gap-3">
            <span className="text-[11px] text-stone-600 font-sans">
              Active: <strong className="text-stone-900 font-mono">{user?.employee_id}</strong> ({user?.role})
            </span>
            <button
              type="submit"
              disabled={loading}
              className="flex items-center gap-1.5 px-6 py-2.5 rounded-md bg-[#C87A5B] hover:bg-[#B85D3B] text-white font-sans text-xs font-bold transition-all shadow-md cursor-pointer disabled:opacity-50"
            >
              <span>{loading ? 'Authenticating…' : 'Sign In & Verify'}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
