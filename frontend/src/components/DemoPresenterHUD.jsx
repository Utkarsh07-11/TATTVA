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
      <div className="fixed bottom-3 right-4 z-[2000] bg-white/95 backdrop-blur-md border border-[#DCD5CD] p-3 rounded-lg text-xs text-[#5A524F] font-mono shadow-2xl">
        Loading Presenter HUD...
      </div>
    );
  }

  if (!currentStep) return null;

  return (
    <div className="fixed bottom-3 left-4 right-4 sm:left-auto sm:right-6 z-[2000] max-w-2xl w-full bg-white/95 backdrop-blur-md border border-[#DCD5CD] rounded-xl shadow-2xl text-xs font-mono pointer-events-auto animate-in slide-in-from-bottom-3 duration-200">
      {/* 1. COMPACT HUD HEADER */}
      <div className="flex items-center justify-between px-3.5 py-2.5 bg-[#FAF7F2] border-b border-[#DCD5CD] rounded-t-xl">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#C87A5B] animate-pulse"></span>
          <span className="font-bold uppercase tracking-wider text-[#26211F] text-[11px] font-sans">
            PRESENTER HUD
          </span>
          <span className="text-[10px] px-2 py-0.5 rounded bg-[#EDC7B7]/50 border border-[#C87A5B] text-[#8C3A1E] font-bold">
            Step {currentStep.step_id} of {steps.length}
          </span>
          {preflightStatus?.status === 'PASS' ? (
            <span className="hidden md:inline-flex items-center gap-1 text-[10px] text-emerald-700 font-sans font-medium">
              <CheckCircle2 className="w-3 h-3 text-emerald-700" />
              Preflight PASS ({preflightStatus?.performance?.observed_ms}ms)
            </span>
          ) : (
            <span className="hidden md:inline-flex items-center gap-1 text-[10px] text-[#C87A5B] font-sans">
              <AlertTriangle className="w-3 h-3 text-[#C87A5B]" />
              Preflight Check
            </span>
          )}
        </div>

        {/* Timer & Controls */}
        <div className="flex items-center gap-2">
          <div
            className={`flex items-center gap-1 px-2.5 py-1 rounded-md border text-[11px] cursor-pointer ${
              timerSeconds > DEMO_PRESENTATION_DEFAULTS.totalPresentationSeconds
                ? 'bg-rose-100 border-rose-300 text-rose-800'
                : 'bg-white border-[#DCD5CD] text-[#C87A5B]'
            }`}
            onClick={() => setIsTimerRunning(!isTimerRunning)}
            title="Click to pause/play presentation timer"
          >
            <Clock className="w-3 h-3" />
            <span className="font-bold">{formatTime(timerSeconds)}</span>
            <span className="text-[9px] text-[#8A817D]">/ 05:00</span>
          </div>

          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1 text-[#5A524F] hover:text-[#26211F] rounded hover:bg-[#EEE6DD] cursor-pointer"
            title={isExpanded ? 'Collapse HUD' : 'Expand HUD'}
          >
            {isExpanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronUp className="w-3.5 h-3.5" />}
          </button>
          <button
            onClick={onClose}
            className="p-1 text-[#5A524F] hover:text-rose-600 rounded hover:bg-[#EEE6DD] cursor-pointer"
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
          <div className="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-[#DCD5CD]">
            <div>
              <div className="text-[10px] uppercase tracking-wider text-[#8A817D]">
                Target Mine: <strong className="text-[#26211F]">{currentStep.mine_id}</strong> · Target View:{' '}
                <strong className="text-[#C87A5B]">{currentStep.target_screen}</strong>
              </div>
              <h4 className="text-sm font-bold text-[#26211F] font-sans mt-0.5">{currentStep.title}</h4>
            </div>

            <div className="flex items-center gap-2">
              <span
                className={`text-[10px] px-2 py-0.5 rounded font-bold border ${
                  currentStep.tier === 'LEVEL_A'
                    ? 'bg-emerald-100 text-emerald-800 border-emerald-300'
                    : currentStep.tier === 'LEVEL_B'
                    ? 'bg-blue-100 text-blue-800 border-blue-300'
                    : currentStep.tier === 'LEVEL_C'
                    ? 'bg-[#EDC7B7]/50 text-[#8C3A1E] border-[#C87A5B]'
                    : 'bg-[#EEE6DD] text-[#5A524F] border-[#DCD5CD]'
                }`}
              >
                {currentStep.tier}
              </span>
              <button
                onClick={() => handleExecuteStep(currentStep)}
                className="px-3 py-1 rounded-md bg-[#C87A5B] text-white font-bold text-[11px] font-sans hover:bg-[#B85D3B] transition-colors flex items-center gap-1 cursor-pointer shadow-sm"
              >
                <Play className="w-3 h-3 fill-white" />
                Execute Step
              </button>
            </div>
          </div>

          {/* Speaker Teleprompter Card */}
          <div className="p-2.5 rounded-lg bg-[#FAF7F2] border border-[#DCD5CD] space-y-1.5">
            <div className="flex items-center justify-between text-[10px] text-[#8A817D] uppercase tracking-wide font-sans font-semibold">
              <span className="flex items-center gap-1 text-[#C87A5B]">
                <Sparkles className="w-3 h-3 text-[#C87A5B]" />
                Speaker Talking Points (Target: ~{currentStep.timing_target_sec}s)
              </span>
            </div>
            <p className="text-[11px] text-[#26211F] leading-relaxed font-sans font-normal italic">
              "{currentStep.speaker_notes}"
            </p>
          </div>

          {/* Juror Defense & Governance Accordion */}
          <div>
            <button
              onClick={() => setShowJurorDefense(!showJurorDefense)}
              className="flex items-center justify-between w-full p-2.5 rounded-lg bg-[#FAF7F2] border border-[#DCD5CD] text-[10px] text-[#5A524F] hover:text-[#26211F] font-sans transition-colors cursor-pointer"
            >
              <span className="flex items-center gap-1.5 font-semibold text-[#C87A5B]">
                <HelpCircle className="w-3 h-3 text-[#C87A5B]" />
                Juror Defense and Scientific Backing
              </span>
              <span>{showJurorDefense ? '▲ Hide' : '▼ View Q&A Defense'}</span>
            </button>

            {showJurorDefense && (
              <div className="mt-1.5 p-2.5 rounded-lg bg-[#EEE6DD]/50 border border-[#DCD5CD] text-[11px] text-[#5A524F] space-y-1.5 font-sans leading-relaxed">
                <div>
                  <strong className="text-[#C87A5B] font-mono text-[10px] uppercase block">
                    Technical Defense / Objection Answer:
                  </strong>
                  {currentStep.juror_defense_notes}
                </div>
                <div className="pt-1 border-t border-[#DCD5CD] text-[10px] text-[#8A817D]">
                  <strong className="text-[#26211F]">Governance Disclosure: </strong>
                  {currentStep.governance_disclosure}
                </div>
              </div>
            )}
          </div>

          {/* Bottom Controls Bar */}
          <div className="flex items-center justify-between pt-1 border-t border-[#DCD5CD] font-sans">
            <button
              onClick={handleResetDemo}
              className="px-2.5 py-1 rounded-md bg-[#FAF7F2] hover:bg-[#EEE6DD] border border-[#DCD5CD] text-[#5A524F] hover:text-[#26211F] text-[10px] flex items-center gap-1 cursor-pointer transition-colors"
              title="Reset presentation to Step 1 and initial state"
            >
              <RotateCcw className="w-3 h-3" />
              Reset Demo
            </button>

            <div className="flex items-center gap-1.5">
              <button
                onClick={handlePrevStep}
                disabled={currentStepIndex === 0}
                className={`px-2.5 py-1 rounded-md border text-[11px] flex items-center gap-1 transition-colors ${
                  currentStepIndex === 0
                    ? 'opacity-30 cursor-not-allowed bg-[#FAF7F2] border-[#DCD5CD] text-[#8A817D]'
                    : 'bg-white border-[#DCD5CD] text-[#5A524F] hover:text-[#26211F] hover:bg-[#EEE6DD] cursor-pointer'
                }`}
              >
                <ChevronLeft className="w-3.5 h-3.5" />
                Prev
              </button>

              <button
                onClick={handleNextStep}
                disabled={currentStepIndex === steps.length - 1}
                className={`px-3 py-1 rounded-md border font-semibold text-[11px] flex items-center gap-1 transition-colors ${
                  currentStepIndex === steps.length - 1
                    ? 'opacity-30 cursor-not-allowed bg-[#FAF7F2] border-[#DCD5CD] text-[#8A817D]'
                    : 'bg-[#C87A5B] border-[#B85D3B] text-white hover:bg-[#B85D3B] cursor-pointer shadow-sm'
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
