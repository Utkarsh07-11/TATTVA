import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { X, Sparkles, ChevronRight, ChevronLeft, Check, Crosshair } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const TOUR_STEPS = [
  {
    id: 'step-overview',
    path: '/',
    targetSelector: '#tour-brand-mark',
    title: 'TATTVA: Integrated Ore Intelligence Engine',
    description:
      'Engineered specifically for MOIL Limited (PS 26009). TATTVA fuses 786km orbital Sentinel-2 remote sensing, stope-face telemetry, and 24 years of statutory production data into a unified predictive decision system.',
    buttonText: 'Explore Map →',
  },
  {
    id: 'step-mine-selector',
    path: '/digital-mine',
    targetSelector: '#tour-mine-selector',
    title: 'Audited 10-Mine Statutory Selector',
    description:
      'Switch instantaneously between all 10 MOIL statutory leases in Madhya Pradesh and Maharashtra. Includes instant UTM 44N projection, Survey of India boundaries, and real-time bounding box flyovers.',
    buttonText: 'View 30m Grid →',
  },
  {
    id: 'step-exploration-grid',
    path: '/digital-mine',
    targetSelector: '#tour-toggle-exploration',
    title: '30m Multi-Spectral Sentinel-2 Grid',
    description:
      'Covers the 5.03 km × 4.96 km Balaghat mining lease AOI with 27,720 real multi-spectral cells. Combines Band 4/2 iron oxide and Band 8/11 clay hydrothermal alteration ratios with Copernicus DEM elevation models.',
    buttonText: 'Check ML Models →',
  },
  {
    id: 'step-anomaly-models',
    path: '/digital-mine',
    targetSelector: '#tour-exploration-subbar',
    title: '4-Dimension Anomaly Models & Heuristics',
    description:
      'Toggle between 4 ML dimensions: Unsupervised Isolation Forest, Mahalanobis Covariance Distance, Bharweli Shaft Anchor Similarity, and the unified Ensemble Priority Ranking.',
    buttonText: 'Adjust Cutoff →',
  },
  {
    id: 'step-cutoff-slider',
    path: '/digital-mine',
    targetSelector: '#tour-cutoff-slider',
    title: 'Dynamic Cutoff Threshold & Site Anchors',
    description:
      'Slide to filter candidate exploration targets in real-time (e.g. ≥ 0.80). Benchmarked against ground truth spatial anchors including the Bharweli shaft haulage portal and Mansar outcrop.',
    buttonText: 'Statutory Backtest →',
  },
  {
    id: 'step-backtest',
    path: '/production',
    targetSelector: '#tour-backtest-section',
    title: '10-Year Ministry Backtest Calibration',
    description:
      'Audited against 10 consecutive financial years (FY15–FY24) of statutory filings submitted to Parliament and the Ministry of Steel. Walk-forward held-out testing verifies a 9.90% MAPE accuracy.',
    buttonText: 'Daily Quantiles →',
  },
  {
    id: 'step-quantile-forecast',
    path: '/production',
    targetSelector: '#tour-daily-analytics',
    title: 'LightGBM Quantile Forecast (P10, P50, P90)',
    description:
      'Predicts shortfall risk probabilities and stochastic tonnage spreads (P10 conservative, P50 expected, P90 optimistic) to catch production bottlenecks 72 hours before quotas deviate.',
    buttonText: 'Try Operations →',
  },
  {
    id: 'step-operations-sim',
    path: '/operations',
    targetSelector: '#tour-operations-tools',
    title: 'Weather & Disruption Scenario Sandbox',
    description:
      'Model operational shocks in real-time: simulate heavy monsoon rainfalls (up to 75mm/hr), excavator mechanical downtime, and blasting clearance delays to measure run-rate degradation.',
    buttonText: 'Haul Optimizer →',
  },
  {
    id: 'step-milp-optimization',
    path: '/operations',
    targetSelector: '#tour-milp-forecast',
    title: 'Sub-200ms MILP Haul-Fleet Optimization',
    description:
      'The PuLP linear programming solver computes optimal haul-truck dispatch plans in under 200ms. Dynamically re-assigns dumpers to available shovels and crushers to recover lost tonnage.',
    buttonText: 'Weekly WSR →',
  },
  {
    id: 'step-log-wsr',
    path: '/digital-mine',
    targetSelector: '#tour-log-wsr',
    title: 'Weekly Production Summary (WSR) Logging',
    description:
      'Replaced daily friction with weekly reporting (Weeks 1 to 4). Site engineers enter extraction figures directly or upload CSV files to trigger instant ML quantile inference and dispatch recommendations.',
    buttonText: 'Role Governance →',
  },
  {
    id: 'step-governance',
    path: '/digital-mine',
    targetSelector: '#tour-user-badge',
    title: '3-Tier Semantic Role System & Expansion',
    description:
      'Site engineers (Tier 1: MPB...) are strictly scoped to their mine. HQ (Tier 2: MHN...) unlocks the 10-mine IBM compliance matrix. Apex Board owners (Tier 3: IN...) can commission brand-new mining leases dynamically.',
    buttonText: 'Finish Tour ✓',
  },
];

export default function InteractiveTourCallout({ onClose }) {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [targetRect, setTargetRect] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();
  const { isExecutive } = useAuth();
  const calloutRef = useRef(null);

  // Animation frame and one-time auto-scroll tracking refs
  const rafId = useRef(null);
  const scrolledStepRef = useRef(-1);

  const step = TOUR_STEPS[currentStepIndex];

  // Check if current target belongs to the sticky navbar
  const isNavbarElement = Boolean(
    step.targetSelector && (
      step.targetSelector === '#tour-brand-mark' ||
      step.targetSelector === '#tour-log-wsr' ||
      step.targetSelector === '#tour-user-badge'
    )
  );

  // Route synchronization when step specifies a different page
  useEffect(() => {
    if (step.path && location.pathname !== step.path) {
      if (step.id === 'step-governance' && !isExecutive) {
        // Site operators remain on current view and point to header role badge
      } else {
        navigate(step.path);
      }
    }
  }, [currentStepIndex, step.path, location.pathname, isExecutive, navigate, step.id]);

  // Intelligent scroll calculation taking 72px sticky navbar into account
  const scrollToTarget = useCallback((el) => {
    if (!el) return;
    if (el.closest('header')) {
      // Navbar elements are already sticky at top: do not scroll
      return;
    }

    const rect = el.getBoundingClientRect();
    const NAVBAR_HEIGHT = 76;
    const PADDING = 20;
    const availableHeight = window.innerHeight - NAVBAR_HEIGHT - PADDING * 2;

    let targetScrollY;
    if (rect.height >= availableHeight * 0.7) {
      // If element is tall, align its top cleanly 20px below navbar
      targetScrollY = window.scrollY + rect.top - NAVBAR_HEIGHT - PADDING;
    } else {
      // Otherwise center it in the remaining viewable space below navbar
      const idealTop = NAVBAR_HEIGHT + PADDING + (availableHeight - rect.height) / 2;
      targetScrollY = window.scrollY + rect.top - idealTop;
    }

    try {
      window.scrollTo({
        top: Math.max(0, targetScrollY),
        behavior: 'smooth',
      });
    } catch {
      // Fallback
    }
  }, []);

  // Update target element bounding rectangle - NEVER calls scrollIntoView
  const measureTargetRect = useCallback((performScroll = false) => {
    if (!step.targetSelector) {
      setTargetRect(null);
      return;
    }
    const el = document.querySelector(step.targetSelector);
    if (el) {
      if (performScroll && scrolledStepRef.current !== currentStepIndex) {
        scrolledStepRef.current = currentStepIndex;
        scrollToTarget(el);
      }
      const rect = el.getBoundingClientRect();
      setTargetRect({
        top: rect.top,
        left: rect.left,
        width: rect.width,
        height: rect.height,
        bottom: rect.bottom,
        right: rect.right,
      });
    } else {
      setTargetRect(null);
    }
  }, [step.targetSelector, currentStepIndex, scrollToTarget]);

  // Initial step transition positioning & passive scroll/resize measurement
  useEffect(() => {
    // Reset scrolled flag for new step
    scrolledStepRef.current = -1;

    // Small delay to allow page route navigation and DOM rendering to settle
    const initTimer = setTimeout(() => {
      measureTargetRect(true);
      setTimeout(() => measureTargetRect(false), 350);
    }, 250);

    // Passive scroll and resize listener: strictly measures position via requestAnimationFrame
    // NEVER calls scrollIntoView, ensuring 100% natural, jitter-free user scrolling!
    const handleScrollOrResize = () => {
      if (rafId.current) return;
      rafId.current = requestAnimationFrame(() => {
        rafId.current = null;
        measureTargetRect(false);
      });
    };

    window.addEventListener('scroll', handleScrollOrResize, { passive: true });
    window.addEventListener('resize', handleScrollOrResize, { passive: true });

    return () => {
      clearTimeout(initTimer);
      if (rafId.current) cancelAnimationFrame(rafId.current);
      window.removeEventListener('scroll', handleScrollOrResize);
      window.removeEventListener('resize', handleScrollOrResize);
    };
  }, [currentStepIndex, step.targetSelector, location.pathname, measureTargetRect]);

  const handleNext = () => {
    if (currentStepIndex < TOUR_STEPS.length - 1) {
      setCurrentStepIndex((prev) => prev + 1);
    } else {
      onClose();
    }
  };

  const handlePrev = () => {
    if (currentStepIndex > 0) {
      setCurrentStepIndex((prev) => prev - 1);
    }
  };

  const handleManualFocus = () => {
    if (step.targetSelector) {
      const el = document.querySelector(step.targetSelector);
      if (el) {
        scrollToTarget(el);
        setTimeout(() => measureTargetRect(false), 300);
      }
    }
  };

  // Determine if target is currently inside the visible viewport below the sticky navbar
  const NAVBAR_HEIGHT = 76;
  const isTargetInView =
    targetRect &&
    (isNavbarElement
      ? true
      : targetRect.bottom > NAVBAR_HEIGHT + 10 &&
        targetRect.top < window.innerHeight - 60 &&
        targetRect.right > 10 &&
        targetRect.left < window.innerWidth - 10);

  // Calculate coordinates and orientation for speech bubble
  const getCalloutPlacement = () => {
    const cardWidth = Math.min(340, window.innerWidth - 32);
    const cardHeight = 230;

    // Fallback or when element is scrolled off-screen: cleanly docked bottom-right
    if (!targetRect || !isTargetInView) {
      return {
        style: {
          position: 'fixed',
          bottom: '24px',
          right: '24px',
          width: `${cardWidth}px`,
        },
        isPlacedAbove: false,
        showArrow: false,
      };
    }

    let isPlacedAbove = false;
    let top = targetRect.bottom + 14;
    let left = targetRect.left + targetRect.width / 2 - cardWidth / 2;

    // Constrain horizontally within viewport bounds
    left = Math.max(16, Math.min(window.innerWidth - cardWidth - 16, left));

    // Constrain vertically: place above if overflowing bottom
    if (top + cardHeight > window.innerHeight - 16) {
      if (targetRect.top - cardHeight - 14 >= (isNavbarElement ? 16 : NAVBAR_HEIGHT + 10)) {
        top = targetRect.top - cardHeight - 14;
        isPlacedAbove = true;
      } else {
        top = Math.max(NAVBAR_HEIGHT + 10, window.innerHeight - cardHeight - 20);
        isPlacedAbove = targetRect.top > top;
      }
    } else {
      top = Math.max(isNavbarElement ? 16 : NAVBAR_HEIGHT + 10, top);
    }

    return {
      style: {
        position: 'fixed',
        top: `${top}px`,
        left: `${left}px`,
        width: `${cardWidth}px`,
      },
      isPlacedAbove,
      showArrow: true,
    };
  };

  const { style: calloutStyle, isPlacedAbove, showArrow } = getCalloutPlacement();

  // Compute safe beacon box strictly below the navbar for page elements
  const getBeaconStyle = () => {
    if (!isTargetInView || !targetRect) return null;

    if (isNavbarElement) {
      return {
        style: {
          top: `${targetRect.top - 4}px`,
          left: `${targetRect.left - 4}px`,
          width: `${targetRect.width + 8}px`,
          height: `${targetRect.height + 8}px`,
        },
        zIndex: 'z-[55]',
      };
    }

    // Page elements: clamp top strictly below the sticky navbar
    const beaconTop = Math.max(NAVBAR_HEIGHT, targetRect.top - 4);
    const beaconBottom = Math.min(window.innerHeight, targetRect.bottom + 4);
    const beaconHeight = beaconBottom - beaconTop;

    if (beaconHeight <= 8) return null;

    return {
      style: {
        top: `${beaconTop}px`,
        left: `${targetRect.left - 4}px`,
        width: `${targetRect.width + 8}px`,
        height: `${beaconHeight}px`,
      },
      zIndex: 'z-[35]', // Below the z-50 sticky navbar
    };
  };

  const beaconConfig = getBeaconStyle();

  return (
    <>
      {/* Target Focus Beacon Ring Overlay - Strictly below navbar, never bleeding over */}
      {beaconConfig && (
        <div
          className={`fixed pointer-events-none ${beaconConfig.zIndex} rounded-xs ring-4 ring-[#C87A5B] ring-offset-4 ring-offset-[#F7F4EF]/80 animate-pulse transition-[box-shadow] duration-200`}
          style={beaconConfig.style}
        />
      )}

      {/* Interactive Speech Bubble Callout (z-[99999] so never hidden behind map) */}
      <div
        ref={calloutRef}
        style={calloutStyle}
        className="z-[99999] bg-white text-stone-900 rounded-xl shadow-2xl p-4 sm:p-5 border border-stone-200 animate-fadeIn pointer-events-auto transition-[top,left] duration-75"
      >
        {/* Directional Speech Bubble Pointer (Arrow) */}
        {showArrow && (
          isPlacedAbove ? (
            <div className="absolute -bottom-2 left-8 w-4 h-4 bg-white border-b border-r border-stone-200 transform rotate-45 pointer-events-none" />
          ) : (
            <div className="absolute -top-2 left-8 w-4 h-4 bg-white border-t border-l border-stone-200 transform rotate-45 pointer-events-none" />
          )
        )}

        {/* Close button */}
        <button
          type="button"
          onClick={onClose}
          className="absolute top-3 right-3 text-stone-400 hover:text-stone-800 transition-colors p-1 rounded-full hover:bg-stone-100 cursor-pointer"
          aria-label="Dismiss tour"
        >
          <X className="w-3.5 h-3.5" />
        </button>

        {/* Header with Step Counter */}
        <div className="text-center pt-0.5 mb-2.5">
          <div className="flex items-center justify-center gap-1.5 mb-1.5">
            <Sparkles className="w-3.5 h-3.5 text-[#C87A5B] fill-[#EDC7B7]" />
            <span className="text-[10px] font-sans font-bold tracking-wider uppercase text-[#C87A5B] bg-[#EDC7B7]/30 px-2 py-0.5 rounded-full border border-[#EDC7B7]">
              Interactive Tour · Step {currentStepIndex + 1} of {TOUR_STEPS.length}
            </span>
            <Sparkles className="w-3.5 h-3.5 text-[#C87A5B] fill-[#EDC7B7]" />
          </div>

          <h3 className="font-editorial text-base sm:text-lg font-bold tracking-tight text-stone-900 leading-snug">
            {step.title}
          </h3>
        </div>

        {/* Explanation Text */}
        <p className="font-sans text-xs text-stone-600 leading-relaxed text-center mb-3">
          {step.description}
        </p>

        {/* Off-screen Re-center Helper Bar */}
        {!isTargetInView && step.targetSelector && (
          <div className="mb-3 flex items-center justify-center">
            <button
              type="button"
              onClick={handleManualFocus}
              className="flex items-center gap-1.5 text-[11px] font-sans font-medium text-[#C87A5B] bg-[#EDC7B7]/20 hover:bg-[#EDC7B7]/40 px-2.5 py-1 rounded-full border border-[#EDC7B7] transition-colors cursor-pointer"
            >
              <Crosshair className="w-3 h-3 text-[#C87A5B]" />
              <span>Target out of view · Click to center</span>
            </button>
          </div>
        )}

        {/* Footer Navigation Buttons */}
        <div className="flex items-center justify-between gap-2 pt-2.5 border-t border-stone-100 font-sans">
          <div className="flex items-center gap-1">
            {currentStepIndex > 0 ? (
              <button
                type="button"
                onClick={handlePrev}
                className="flex items-center gap-1 text-xs font-semibold text-stone-600 hover:text-stone-900 px-2 py-1 rounded hover:bg-stone-100 transition-colors cursor-pointer"
              >
                <ChevronLeft className="w-3 h-3" />
                <span>Back</span>
              </button>
            ) : (
              <button
                type="button"
                onClick={onClose}
                className="text-xs text-stone-400 hover:text-stone-700 px-2 py-1 transition-colors cursor-pointer"
              >
                Skip
              </button>
            )}
          </div>

          {/* Action / Next Button */}
          <button
            type="button"
            onClick={handleNext}
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-[#C87A5B] hover:bg-[#B85D3B] text-white text-xs font-bold transition-all shadow-md hover:shadow-lg cursor-pointer transform hover:-translate-y-0.5"
          >
            <span>{step.buttonText}</span>
            {currentStepIndex === TOUR_STEPS.length - 1 ? (
              <Check className="w-3.5 h-3.5" />
            ) : (
              <ChevronRight className="w-3.5 h-3.5" />
            )}
          </button>
        </div>
      </div>
    </>
  );
}
