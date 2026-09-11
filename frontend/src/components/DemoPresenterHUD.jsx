import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Play,
  RotateCcw,
  ChevronRight,
  ChevronLeft,
  ShieldCheck,
  Clock,
  HelpCircle,
  Sparkles,
  Layers,
  ChevronDown,
  ChevronUp,
  X,
  CheckCircle2,
  AlertTriangle,
} from 'lucide-react';
import { api } from '../services/api';
import { SCREEN_ROUTE_MAP, DEMO_PRESENTATION_DEFAULTS } from '../config/demoConfig';

export default function DemoPresenterHUD({ onClose }) {
  const navigate = useNavigate();
  const location = useLocation();

  const [demoConfig, setDemoConfig] = useState(null);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [isExpanded, setIsExpanded] = useState(true);
  const [showJurorDefense, setShowJurorDefense] = useState(false);
  const [preflightStatus, setPreflightStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  // Presentation Timer (5-minute countdown / elapsed)
  const [timerSeconds, setTimerSeconds] = useState(0);
  const [isTimerRunning, setIsTimerRunning] = useState(false);
  const timerRef = useRef(null);

  // 1. Fetch Authoritative Demo Config & Preflight on Mount
  useEffect(() => {
    let isMounted = true;
    Promise.all([api.getDemoConfig(), api.getDemoPreflight()])
      .then(([cfg, pf]) => {
        if (isMounted) {
          setDemoConfig(cfg);
          setPreflightStatus(pf);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.warn('Could not fetch demo configuration:', err);
        setLoading(false);
      });

    return () => {
      isMounted = false;
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  // Timer Tick
  useEffect(() => {
    if (isTimerRunning) {
      timerRef.current = setInterval(() => {
        setTimerSeconds((prev) => prev + 1);
      }, 1000);
    } else if (timerRef.current) {
      clearInterval(timerRef.current);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isTimerRunning]);

  const steps = demoConfig?.demonstration_path || [];
  const currentStep = steps[currentStepIndex] || null;

  // Format MM:SS
  const formatTime = (secs) => {
    const mins = Math.floor(secs / 60);
    const rem = secs % 60;
    return `${String(mins).padStart(2, '0')}:${String(rem).padStart(2, '0')}`;
  };

  // 2. Execute Step Action via Standard Public Application Pathways
  const handleExecuteStep = (stepToExec = currentStep) => {
    if (!stepToExec) return;

    if (!isTimerRunning && timerSeconds === 0) {
      setIsTimerRunning(true);
    }

    const targetMine = stepToExec.mine_id || 'MOIL_BALAGHAT';
    const targetScreen = stepToExec.target_screen || 'overview';
    const routePath = SCREEN_ROUTE_MAP[targetScreen] || '/';

    // Synchronize mine ID in URL query param safely (public standard pathway)
    const url = new URL(window.location.href);
    url.pathname = routePath;
    url.searchParams.set('mine', targetMine);
    window.history.replaceState({}, '', url.toString());

    // Navigate to target route
    navigate(`${routePath}?mine=${targetMine}`);
  };

  // 3. Navigation Controls
  const handleNextStep = () => {
    if (currentStepIndex < steps.length - 1) {
      const nextIdx = currentStepIndex + 1;
      setCurrentStepIndex(nextIdx);
      handleExecuteStep(steps[nextIdx]);
    }
  };

  const handlePrevStep = () => {
    if (currentStepIndex > 0) {
      const prevIdx = currentStepIndex - 1;
      setCurrentStepIndex(prevIdx);
      handleExecuteStep(steps[prevIdx]);
    }
  };

  // 4. Deterministic Replay Reset
  const handleResetDemo = () => {
    setCurrentStepIndex(0);
    setTimerSeconds(0);
    setIsTimerRunning(false);
    setShowJurorDefense(false);

    // Reset URL to initial Balaghat state on Overview
    const initialMine = DEMO_PRESENTATION_DEFAULTS.initialDemoMine;
    const url = new URL(window.location.href);
    url.pathname = '/';
    url.searchParams.set('mine', initialMine);
    window.history.replaceState({}, '', url.toString());

    navigate(`/?mine=${initialMine}`);
  };

  if (loading) {
    return (
      <div className="fixed bottom-3 right-4 z-[2000] bg-[#07090d]/95 backdrop-blur-md border border-technical p-3 rounded text-xs text-slate-400 font-mono shadow-2xl">
        Loading Presenter HUD...
      </div>
    );
  }

  if (!currentStep) return null;

  return (
    <div className="fixed bottom-3 left-4 right-4 sm:left-auto sm:right-6 z-[2000] max-w-2xl w-full bg-[#07090d]/95 backdrop-blur-md border border-amber-900/60 rounded shadow-2xl text-xs font-mono pointer-events-auto animate-in slide-in-from-bottom-3 duration-200">
      {/* 1. COMPACT HUD HEADER */}
      <div className="flex items-center justify-between px-3.5 py-2 bg-slate-950/90 border-b border-technical">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-industrial-amber animate-pulse"></span>
          <span className="font-bold uppercase tracking-wider text-white text-[11px] font-sans">
            PRESENTER HUD
          </span>
          <span className="text-[10px] px-1.5 py-0.2 rounded bg-amber-950/70 border border-amber-800 text-amber-300 font-bold">
            Step {currentStep.step_id} of {steps.length}
          </span>
          {preflightStatus?.status === 'PASS' ? (
            <span className="hidden md:inline-flex items-center gap-1 text-[10px] text-emerald-400 font-sans">
              <CheckCircle2 className="w-3 h-3 text-emerald-400" />
              Preflight PASS ({preflightStatus?.performance?.observed_ms}ms)
            </span>
          ) : (
            <span className="hidden md:inline-flex items-center gap-1 text-[10px] text-amber-400 font-sans">
              <AlertTriangle className="w-3 h-3 text-amber-400" />
              Preflight Check
            </span>
          )}
        </div>

        {/* Timer & Controls */}
        <div className="flex items-center gap-2">
          <div
            className={`flex items-center gap-1 px-2 py-0.5 rounded border text-[11px] cursor-pointer ${
              timerSeconds > DEMO_PRESENTATION_DEFAULTS.totalPresentationSeconds
                ? 'bg-rose-950/80 border-rose-700 text-rose-300'
                : 'bg-[#0b0f17] border-technical text-industrial-amber'
            }`}
            onClick={() => setIsTimerRunning(!isTimerRunning)}
            title="Click to pause/play presentation timer"
          >
            <Clock className="w-3 h-3" />
            <span className="font-bold">{formatTime(timerSeconds)}</span>
            <span className="text-[9px] text-slate-500">/ 05:00</span>
          </div>

          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1 text-slate-400 hover:text-white rounded hover:bg-slate-800 cursor-pointer"
            title={isExpanded ? 'Collapse HUD' : 'Expand HUD'}
          >
            {isExpanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronUp className="w-3.5 h-3.5" />}
          </button>
          <button
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-rose-400 rounded hover:bg-slate-800 cursor-pointer"
            title="Exit Demo Mode"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* 2. EXPANDED PRESENTER TELEPROMPTER & CONTROLLER */}
      {isExpanded && (
        <div className="p-3.5 space-y-3">
          {/* Step Metadata Bar */}
          <div className="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-technical">
            <div>
              <div className="text-[10px] uppercase tracking-wider text-slate-500">
                Target Mine: <strong className="text-white">{currentStep.mine_id}</strong> · Target View:{' '}
                <strong className="text-industrial-amber">{currentStep.target_screen}</strong>
              </div>
              <h4 className="text-sm font-bold text-white font-sans mt-0.5">{currentStep.title}</h4>
            </div>

            <div className="flex items-center gap-2">
              <span
                className={`text-[10px] px-2 py-0.5 rounded font-bold border ${
                  currentStep.tier === 'LEVEL_A'
                    ? 'bg-emerald-950 text-emerald-300 border-emerald-700'
                    : currentStep.tier === 'LEVEL_B'
                    ? 'bg-cyan-950 text-cyan-300 border-cyan-700'
                    : currentStep.tier === 'LEVEL_C'
                    ? 'bg-amber-950 text-amber-300 border-amber-700'
                    : 'bg-slate-900 text-slate-300 border-slate-700'
                }`}
              >
                {currentStep.tier}
              </span>
              <button
                onClick={() => handleExecuteStep(currentStep)}
                className="px-2.5 py-1 rounded bg-industrial-amber text-black font-bold text-[11px] font-sans hover:bg-amber-400 transition-colors flex items-center gap-1 cursor-pointer"
              >
                <Play className="w-3 h-3 fill-black" />
                Execute Step
              </button>
            </div>
          </div>

          {/* Speaker Teleprompter Card */}
          <div className="p-2.5 rounded bg-[#0b0f17] border border-technical space-y-1.5">
            <div className="flex items-center justify-between text-[10px] text-slate-400 uppercase tracking-wide font-sans font-semibold">
              <span className="flex items-center gap-1 text-amber-300">
                <Sparkles className="w-3 h-3 text-industrial-amber" />
                Speaker Talking Points (Target: ~{currentStep.timing_target_sec}s)
              </span>
            </div>
            <p className="text-[11px] text-slate-200 leading-relaxed font-sans font-normal italic">
              "{currentStep.speaker_notes}"
            </p>
          </div>

          {/* Juror Defense & Governance Accordion */}
          <div>
            <button
              onClick={() => setShowJurorDefense(!showJurorDefense)}
              className="flex items-center justify-between w-full p-2 rounded bg-slate-950 border border-technical text-[10px] text-slate-300 hover:text-white font-sans transition-colors cursor-pointer"
            >
              <span className="flex items-center gap-1.5 font-semibold text-cyan-300">
                <HelpCircle className="w-3 h-3 text-cyan-400" />
                Juror Defense & Scientific Backing
              </span>
              <span>{showJurorDefense ? '▲ Hide' : '▼ View Q&A Defense'}</span>
            </button>

            {showJurorDefense && (
              <div className="mt-1.5 p-2.5 rounded bg-cyan-950/20 border border-cyan-800/40 text-[11px] text-slate-300 space-y-1.5 font-sans leading-relaxed">
                <div>
                  <strong className="text-cyan-300 font-mono text-[10px] uppercase block">
                    Technical Defense / Objection Answer:
                  </strong>
                  {currentStep.juror_defense_notes}
                </div>
                <div className="pt-1 border-t border-cyan-900/40 text-[10px] text-slate-400">
                  <strong className="text-slate-300">Governance Disclosure: </strong>
                  {currentStep.governance_disclosure}
                </div>
              </div>
            )}
          </div>

          {/* Bottom Controls Bar */}
          <div className="flex items-center justify-between pt-1 border-t border-technical font-sans">
            <button
              onClick={handleResetDemo}
              className="px-2 py-1 rounded bg-slate-900 hover:bg-slate-800 border border-technical text-slate-400 hover:text-white text-[10px] flex items-center gap-1 cursor-pointer transition-colors"
              title="Reset presentation to Step 1 & initial state"
            >
              <RotateCcw className="w-3 h-3" />
              Reset Demo
            </button>

            <div className="flex items-center gap-1.5">
              <button
                onClick={handlePrevStep}
                disabled={currentStepIndex === 0}
                className={`px-2.5 py-1 rounded border text-[11px] flex items-center gap-1 transition-colors ${
                  currentStepIndex === 0
                    ? 'opacity-30 cursor-not-allowed bg-slate-950 border-technical text-slate-600'
                    : 'bg-[#0b0f17] border-technical text-slate-300 hover:text-white hover:bg-slate-800 cursor-pointer'
                }`}
              >
                <ChevronLeft className="w-3.5 h-3.5" />
                Prev
              </button>

              <button
                onClick={handleNextStep}
                disabled={currentStepIndex === steps.length - 1}
                className={`px-3 py-1 rounded border font-semibold text-[11px] flex items-center gap-1 transition-colors ${
                  currentStepIndex === steps.length - 1
                    ? 'opacity-30 cursor-not-allowed bg-slate-950 border-technical text-slate-600'
                    : 'bg-industrial-amber/20 border-industrial-amber text-industrial-amber hover:bg-industrial-amber hover:text-black cursor-pointer'
                }`}
              >
                Next
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
