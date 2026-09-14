import React from 'react';
import { Layers, Cpu, Clock, CheckCircle2 } from 'lucide-react';
import StoryWorksHero from '../components/StoryWorksHero';
import BlockRevealImage from '../components/BlockRevealImage';
import { useDashboard } from '../context/DashboardContext';

// Authentic Field Photography
import bbcDigger from '../assets/bbc/digger.jpg';
import bbcPatroller from '../assets/bbc/patroller-1.jpg';
import bbcDust from '../assets/bbc/dust.jpg';
import bbcMasonry from '../assets/bbc/masonry.jpg';
import bbcStory2 from '../assets/bbc/story-2.jpg';

export default function StoryOverviewPage() {
  const { forecast, selectedBlock, setSelectedBlock } = useDashboard();

  const target = forecast?.target_tonnes || 10000;
  const p50 = forecast?.forecast_tonnes || 8650;
  const [p10, p90] = forecast?.interval_90 || [7900, 9300];
  const shortfall = forecast?.expected_shortfall_tonnes || 1350;
  const shortfallPct = forecast?.shortfall_pct || 13.5;
  const prob = Math.round((forecast?.shortfall_probability || 0.87) * 100);
  const riskLevel = forecast?.risk_level || 'HIGH';

  return (
    <div className="space-y-0 pb-20">
      {/* 1. Cinematic Hero Header */}
      <StoryWorksHero />

      {/* 2. FORMAL WHITE SECTION: Geological Baseline & Predictive Telemetry */}
      <section className="bg-white text-slate-900 border-y border-slate-200 py-16 sm:py-20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">
            {/* Left Column: Known Facts, Raw Data & Predictive Data */}
            <div className="lg:col-span-7 space-y-6">
              <div className="text-xs font-sans tracking-wider text-amber-700 uppercase font-bold">
                OPERATIONAL BASELINE AND KNOWN DATA
              </div>

              <h2 className="font-sans text-3xl sm:text-4xl font-bold text-slate-950 leading-[1.15]">
                Central India Ore Belt · Geological Baseline and Predictive Telemetry
              </h2>

              <p className="font-sans text-sm text-slate-600 leading-relaxed">
                Authoritative geological specifications, extraction telemetry, and predictive model parameters compiled from statutory records and real-time stope instrumentation.
              </p>

              {/* Data Group 1: Known Geological & In-Situ Facts (Raw Data) */}
              <div className="border border-slate-200 rounded-xs p-4 bg-slate-50 space-y-3">
                <div className="flex items-center justify-between border-b border-slate-200 pb-2">
                  <span className="text-xs font-sans font-bold text-slate-900 uppercase tracking-wider">
                    Known Geological Baseline (In-Situ)
                  </span>
                  <span className="text-[11px] font-sans text-slate-500 font-semibold">Audited Stratigraphy</span>
                </div>
                <div className="grid grid-cols-2 gap-3 text-xs font-sans">
                  <div>
                    <span className="text-slate-500 block text-[11px]">GEOLOGICAL STRATA</span>
                    <span className="font-semibold text-slate-900">Precambrian Sausar Belt</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[11px]">HOST LITHOLOGY</span>
                    <span className="font-semibold text-slate-900">Mansar Schist / Braunite Ore</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[11px]">ASSAY ORE GRADE</span>
                    <span className="font-semibold text-amber-700">42.8% Average Concentration</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[11px]">HAULAGE HORIZON</span>
                    <span className="font-semibold text-slate-900">300m Underground Level</span>
                  </div>
                </div>
              </div>

              {/* Data Group 2: Operational Observed Telemetry (Raw Shift Data) */}
              <div className="border border-slate-200 rounded-xs p-4 bg-slate-50 space-y-3">
                <div className="flex items-center justify-between border-b border-slate-200 pb-2">
                  <span className="text-xs font-sans font-bold text-slate-900 uppercase tracking-wider">
                    Operational Extraction Parameters (Raw Data)
                  </span>
                  <span className="text-[11px] font-sans text-emerald-700 font-semibold">Active Shift Telemetry</span>
                </div>
                <div className="grid grid-cols-2 gap-3 text-xs font-sans">
                  <div>
                    <span className="text-slate-500 block text-[11px]">ACTIVE WORKFORCE</span>
                    <span className="font-semibold text-slate-900">18 Shift Personnel Active</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[11px]">EXCAVATOR PAYLOAD</span>
                    <span className="font-semibold text-slate-900">42.0 Tonnes / Pass</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[11px]">HAUL CYCLE TIME</span>
                    <span className="font-semibold text-slate-900">18.4 Minutes / Round Trip</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[11px]">RUN-RATE CAPACITY</span>
                    <span className="font-semibold text-emerald-700">~41.2 Tonnes / Operating Hour</span>
                  </div>
                </div>
              </div>

              {/* Data Group 3: Predictive Shortfall Metrics (Predictable Data) */}
              <div className="border border-slate-200 rounded-xs p-4 bg-amber-50/50 border-amber-200 space-y-3">
                <div className="flex items-center justify-between border-b border-amber-200/60 pb-2">
                  <span className="text-xs font-sans font-bold text-slate-900 uppercase tracking-wider">
                    Predictive Shortfall Outlook (Forecast)
                  </span>
                  <span className="text-[11px] font-sans text-rose-700 font-semibold">Variance Projection</span>
                </div>
                <div className="grid grid-cols-2 gap-3 text-xs font-sans">
                  <div>
                    <span className="text-slate-500 block text-[11px]">STATUTORY QUOTA</span>
                    <span className="font-semibold text-slate-900">10,000 Tonnes / Month</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[11px]">PREDICTED YIELD (P50)</span>
                    <span className="font-semibold text-slate-900">8,650 Tonnes (±650 t)</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[11px]">FORECAST DEFICIT</span>
                    <span className="font-semibold text-rose-700">-1,350 Tonnes (13.5%)</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[11px]">PRIMARY SENSITIVITY</span>
                    <span className="font-semibold text-slate-900">Equipment Availability and Blasting</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Column: Clean Authentic Photography with Block Reveal */}
            <div className="lg:col-span-5 space-y-6">
              <BlockRevealImage
                src={bbcDigger}
                alt="Hydraulic excavator loading ore"
                aspectRatio="aspect-[4/3]"
                blockColor="bg-[#d4a574]"
                delay={100}
              />

              <div className="p-4 bg-slate-50 border border-slate-200 rounded-xs space-y-2.5">
                <div className="flex items-center justify-between border-b border-slate-200 pb-1.5">
                  <span className="text-xs font-sans font-bold text-amber-800 uppercase">
                    STOPE CONTEXT #{selectedBlock}
                  </span>
                  <span className="text-xs font-sans text-emerald-700 font-semibold">18 Crew Active</span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs font-sans text-slate-600">
                  <div>
                    <span className="text-slate-400 block text-[10px]">HOST ROCK:</span>
                    <span className="font-semibold text-slate-900">Mansar Schist Strata</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px]">AVERAGE GRADE:</span>
                    <span className="font-semibold text-amber-700">42.8% Braunite</span>
                  </div>
                </div>
              </div>

              <BlockRevealImage
                src={bbcPatroller}
                alt="Safety vehicle surveying site"
                aspectRatio="aspect-[16/10]"
                blockColor="bg-[#1e293b]"
                delay={250}
              />
            </div>
          </div>
        </div>
      </section>

      {/* 2.5 CORE PURPOSE & OPERATIONAL DECISION-SUPPORT WORKFLOW */}
      <section className="bg-[#0c1018] text-white border-b border-technical py-16">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 space-y-10">
          <div className="max-w-3xl space-y-3">
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded bg-amber-500/10 border border-amber-500/30 text-amber-300 font-sans text-xs tracking-wider uppercase font-semibold">
              SYSTEM PURPOSE AND CORE OBJECTIVE
            </div>
            <h2 className="font-sans text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight text-white">
              End-to-End Ore Shortfall Detection and Decision Support
            </h2>
            <p className="font-sans text-base sm:text-lg text-slate-200 leading-relaxed">
              The system detects ore shortfalls by analyzing historical data and incorporating real-time operational data. When a potential or current shortfall is detected, the system analyzes the situation and provides an appropriate solution or recommendation to address it.
            </p>
            <p className="font-sans text-xs sm:text-sm text-slate-300 leading-relaxed">
              More than an isolated forecasting model, TATTVA operates as a complete shortfall detection and decision-support workflow—bridging 10 years of audited statutory production baselines with live underground stope telemetry to protect monthly production targets.
            </p>
          </div>

          {/* Key Workflow: 2-Track Architectural Pipelines */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Track 1: Historical Data Pipeline */}
            <div className="p-6 rounded bg-[#07090e] border border-white/10 space-y-4 shadow-xl">
              <div className="flex items-center justify-between pb-3 border-b border-white/10">
                <span className="font-sans text-xs tracking-wider uppercase text-amber-400 font-bold">
                  PIPELINE A · HISTORICAL INTELLIGENCE
                </span>
                <span className="text-xs font-sans text-slate-400">10-Year Audited Baseline</span>
              </div>
              <div className="flex items-center gap-2 text-xs font-sans">
                <div className="flex-1 p-2.5 rounded bg-[#10141e] border border-white/10 text-center">
                  <span className="text-slate-400 block text-[10px]">INPUT</span>
                  <span className="font-semibold text-white text-xs">Historical Data</span>
                </div>
                <span className="text-slate-500 font-bold text-xs">→</span>
                <div className="flex-1 p-2.5 rounded bg-[#10141e] border border-white/10 text-center">
                  <span className="text-slate-400 block text-[10px]">ANALYSIS</span>
                  <span className="font-semibold text-white text-xs">Identify Patterns</span>
                </div>
                <span className="text-slate-500 font-bold text-xs">→</span>
                <div className="flex-1 p-2.5 rounded bg-[#10141e] border border-white/10 text-center">
                  <span className="text-slate-400 block text-[10px]">OUTPUT</span>
                  <span className="font-semibold text-white text-xs">Predict Shortfall</span>
                </div>
              </div>
              <p className="text-xs text-slate-300 font-sans leading-relaxed">
                Extracts decadal production trends and seasonal capacity variations from official Ministry of Steel filings to eliminate optimistic forecasting bias.
              </p>
            </div>

            {/* Track 2: Real-Time Operational Pipeline */}
            <div className="p-6 rounded bg-[#07090e] border border-white/10 space-y-4 shadow-xl">
              <div className="flex items-center justify-between pb-3 border-b border-white/10">
                <span className="font-sans text-xs tracking-wider uppercase text-emerald-400 font-bold">
                  PIPELINE B · REAL-TIME DISPATCH
                </span>
                <span className="text-xs font-sans text-slate-400">Live Stope Telemetry</span>
              </div>
              <div className="flex items-center gap-1.5 text-xs font-sans">
                <div className="flex-1 p-2 rounded bg-[#10141e] border border-white/10 text-center">
                  <span className="text-slate-400 block text-[10px]">TELEMETRY</span>
                  <span className="font-semibold text-white text-xs">Real-Time Data</span>
                </div>
                <span className="text-slate-500 font-bold text-xs">→</span>
                <div className="flex-1 p-2 rounded bg-[#10141e] border border-white/10 text-center">
                  <span className="text-slate-400 block text-[10px]">DETECTION</span>
                  <span className="font-semibold text-white text-xs">Detect Deficit</span>
                </div>
                <span className="text-slate-500 font-bold text-xs">→</span>
                <div className="flex-1 p-2 rounded bg-[#10141e] border border-white/10 text-center">
                  <span className="text-slate-400 block text-[10px]">DIAGNOSTICS</span>
                  <span className="font-semibold text-white text-xs">Analyze Situation</span>
                </div>
                <span className="text-slate-500 font-bold text-xs">→</span>
                <div className="flex-1 p-2 rounded bg-[#10141e] border border-white/10 text-center">
                  <span className="text-slate-400 block text-[10px]">ACTION</span>
                  <span className="font-semibold text-white text-xs">Provide Solution</span>
                </div>
              </div>
              <p className="text-xs text-slate-300 font-sans leading-relaxed">
                Streams excavator payload weights, fleet availability, and blasting stoppages to determine exact physical bottlenecks and issue corrective dispatch actions.
              </p>
            </div>
          </div>

          {/* Overall 4-Stage Decision Support Architecture */}
          <div className="p-6 rounded bg-[#080c14] border border-technical space-y-3">
            <div className="text-xs font-sans uppercase tracking-wider text-slate-400 font-bold">
              OVERALL 4-STAGE OPERATIONAL ARCHITECTURE
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-1">
              <div className="p-4 rounded bg-[#0f1422] border border-white/5 space-y-1.5">
                <div className="text-amber-400 font-sans font-bold text-xs">01 · DATA FUSION</div>
                <div className="font-semibold text-white text-sm">Historical and Real-Time</div>
                <p className="text-xs text-slate-300 font-sans">Learns from 10-year mining history while incorporating live underground stope sensors.</p>
              </div>
              <div className="p-4 rounded bg-[#0f1422] border border-white/5 space-y-1.5">
                <div className="text-amber-400 font-sans font-bold text-xs">02 · SHORTFALL DETECTION</div>
                <div className="font-semibold text-white text-sm">Quantified Risk Alerts</div>
                <p className="text-xs text-slate-300 font-sans">Detects potential or current ore deficits days before monthly quotas slip.</p>
              </div>
              <div className="p-4 rounded bg-[#0f1422] border border-white/5 space-y-1.5">
                <div className="text-amber-400 font-sans font-bold text-xs">03 · SITUATION ANALYSIS</div>
                <div className="font-semibold text-white text-sm">Factor Decomposition</div>
                <p className="text-xs text-slate-300 font-sans">Analyzes equipment availability, blasting delays, and weather impacts.</p>
              </div>
              <div className="p-4 rounded bg-[#0f1422] border border-white/5 space-y-1.5">
                <div className="text-amber-400 font-sans font-bold text-xs">04 · DECISION SUPPORT</div>
                <div className="font-semibold text-white text-sm">Targeted Solutions</div>
                <p className="text-xs text-slate-300 font-sans">Delivers solver-optimized haulage schedules and What-If simulation interventions.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 3. TECHNICAL OPERATIONAL STATION */}
      <section className="bg-[#07090d] py-16 border-b border-technical">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 space-y-8">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-technical pb-4">
            <div>
              <div className="text-xs font-sans tracking-wider text-amber-500 uppercase font-semibold mb-1">
                CURRENT EXTRACTION TELEMETRY
              </div>
              <h3 className="story-headline text-2xl sm:text-3xl text-white font-bold">
                Stope Production Quota vs Predictive Run-Rate
              </h3>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-xs font-sans text-slate-400">Select Mine Block:</span>
              {['BLOCK_A', 'BLOCK_B', 'BLOCK_C'].map((b) => (
                <button
                  key={b}
                  onClick={() => setSelectedBlock(b)}
                  className={`px-3 py-1 rounded text-xs font-sans transition-all duration-200 cursor-pointer ${
                    selectedBlock === b
                      ? 'bg-amber-500 text-slate-950 font-bold border border-amber-400 shadow-md shadow-amber-500/25'
                      : 'bg-[#0e1219] text-slate-300 hover:text-amber-300 hover:border-amber-500/80 hover:bg-amber-500/10 border border-white/10'
                  }`}
                >
                  {b.replace('_', ' ')}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Target */}
            <div className="story-card p-5 border-t-2 border-t-slate-500">
              <div className="text-xs font-sans text-slate-400 uppercase tracking-wider">
                Monthly Quota
              </div>
              <div className="mt-2 text-2xl sm:text-3xl font-sans font-bold text-white tracking-tight">
                {target.toLocaleString()} <span className="text-sm font-normal text-slate-400 font-sans">t</span>
              </div>
              <div className="mt-3 text-xs font-sans text-slate-400 border-t border-white/5 pt-2 flex justify-between">
                <span>Allocated Stope</span>
                <span className="text-slate-200 font-semibold">{selectedBlock}</span>
              </div>
            </div>

            {/* Forecast */}
            <div className="story-card p-5 border-t-2 border-t-amber-500">
              <div className="text-xs font-sans text-amber-400 uppercase tracking-wider">
                Projected Run-Rate (P50)
              </div>
              <div className="mt-2 text-2xl sm:text-3xl font-sans font-bold text-white tracking-tight">
                {p50.toLocaleString()} <span className="text-sm font-normal text-slate-400 font-sans">t</span>
              </div>
              <div className="mt-3 text-xs font-sans text-slate-400 border-t border-white/5 pt-2 flex justify-between">
                <span>90% Envelope</span>
                <span className="text-slate-200">[{p10.toLocaleString()} - {p90.toLocaleString()}]</span>
              </div>
            </div>

            {/* Gap */}
            <div className="story-card p-5 border-t-2 border-t-amber-500">
              <div className="text-xs font-sans text-amber-400 uppercase tracking-wider">
                Projected Shortfall
              </div>
              <div className="mt-2 text-2xl sm:text-3xl font-sans font-bold text-amber-400 tracking-tight">
                {shortfall > 0 ? `-${shortfall.toLocaleString()}` : '0'}{' '}
                <span className="text-sm font-normal text-slate-400 font-sans">t</span>
              </div>
              <div className="mt-3 text-xs font-sans text-slate-400 border-t border-white/5 pt-2 flex justify-between">
                <span>Quota Delta</span>
                <span className="text-amber-400 font-bold">{shortfallPct}%</span>
              </div>
            </div>

            {/* Probability */}
            <div className="story-card p-5 border-t-2 border-t-rose-500">
              <div className="text-xs font-sans text-rose-400 uppercase tracking-wider">
                Shortfall Probability
              </div>
              <div className="mt-2 text-2xl sm:text-3xl font-sans font-bold text-rose-400 flex items-center gap-2 tracking-tight">
                <span>{prob}%</span>
                <span className="text-xs font-sans px-2 py-0.5 rounded bg-rose-950/60 border border-rose-800 text-rose-200 font-medium">
                  {riskLevel} RISK
                </span>
              </div>
              <div className="mt-3 text-xs font-sans text-slate-400 border-t border-white/5 pt-2 flex justify-between">
                <span>Recommended Action</span>
                <span className="text-slate-200 font-medium">Hauler Redeployment</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 4. FORMAL PHOTO SECTION: Geological Reconnaissance */}
      <section className="bg-[#f8fafc] text-slate-900 border-b border-slate-200 py-16 sm:py-20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 space-y-10">
          <div className="max-w-2xl">
            <div className="text-xs font-sans tracking-wider text-amber-700 uppercase font-bold">
              GEOLOGICAL RECONNAISSANCE
            </div>
            <h3 className="font-sans text-3xl sm:text-4xl font-bold text-slate-950 mt-1">
              Field Validation and Stratigraphic Logging
            </h3>
            <p className="font-sans text-sm text-slate-600 mt-2 leading-relaxed">
              Geological baseline verification across surface benches and drill-core specimens. Operational run-rates are calibrated directly against in-situ rock stability and assay grades.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <BlockRevealImage
              src={bbcDust}
              alt="Airborne dust over mining benches"
              aspectRatio="aspect-[4/3]"
              blockColor="bg-[#c4894a]"
              delay={100}
            />

            <BlockRevealImage
              src={bbcMasonry}
              alt="High-wall manganese rock strata"
              aspectRatio="aspect-[4/3]"
              blockColor="bg-[#334155]"
              delay={250}
            />

            <BlockRevealImage
              src={bbcStory2}
              alt="Field geologist examining drill core"
              aspectRatio="aspect-[4/3]"
              blockColor="bg-[#d4a574]"
              delay={400}
            />
          </div>
        </div>
      </section>

      {/* 5. 24-HOUR EXTRACTION CYCLE TELEMETRY */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 pt-12">
        <div className="border-t border-technical pt-10">
          <div className="text-xs font-sans tracking-wider text-amber-500 uppercase font-semibold mb-1">
            SHIFT TELEMETRY LOG
          </div>
          <h3 className="story-headline text-2xl sm:text-3xl text-white font-bold mb-8">
            Chronology of a 24-Hour Operational Cycle
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="story-card p-5 relative">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-sans font-bold text-slate-200">06:00 - 08:30</span>
                <Clock className="w-4 h-4 text-slate-400" />
              </div>
              <div className="font-sans text-white text-base font-bold mb-1">
                Phase 1 · Telemetric Face Scan
              </div>
              <p className="text-xs text-slate-400 leading-relaxed font-sans">
                Laser profiling of blasted wall surfaces coupled with spectrometer assay measurements to calibrate ore boundary models.
              </p>
            </div>

            <div className="story-card p-5 relative">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-sans font-bold text-slate-200">09:00 - 13:00</span>
                <CheckCircle2 className="w-4 h-4 text-slate-400" />
              </div>
              <div className="font-sans text-white text-base font-bold mb-1">
                Phase 2 · Semi-Auto Mucking
              </div>
              <p className="text-xs text-slate-400 leading-relaxed font-sans">
                Underground load-haul-dump loaders operate on guided paths, reducing personnel exposure to unsupported roofs.
              </p>
            </div>

            <div className="story-card p-5 relative">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-sans font-bold text-slate-200">14:00 - 18:00</span>
                <Cpu className="w-4 h-4 text-slate-400" />
              </div>
              <div className="font-sans text-white text-base font-bold mb-1">
                Phase 3 · Dispatch Rebalancing
              </div>
              <p className="text-xs text-slate-400 leading-relaxed font-sans">
                FastAPI LP optimizer calculates revised dumper routing when excavator hydraulic pressure drops below threshold.
              </p>
            </div>

            <div className="story-card p-5 relative">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-sans font-bold text-slate-200">19:00 - 23:00</span>
                <Layers className="w-4 h-4 text-slate-400" />
              </div>
              <div className="font-sans text-white text-base font-bold mb-1">
                Phase 4 · Reality Reconciliation
              </div>
              <p className="text-xs text-slate-400 leading-relaxed font-sans">
                Surface weighbridge tonnages cross-referenced with held-out walk-forward forecasts to update next-day baseline priors.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 6. OPERATIONAL INTELLIGENCE AND PREDICTIVE YIELD OUTLOOK */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 pt-12 pb-6">
        <div className="story-card p-6 sm:p-8 border-l-4 border-l-amber-500 rounded-sm bg-[#0a0e17]">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-technical pb-3 mb-4 gap-2">
            <span className="text-xs font-sans font-bold text-amber-400 uppercase tracking-wider">
              Operational Intelligence and Predictive Yield Outlook
            </span>
            <span className="text-[11px] font-sans text-slate-400 font-medium">
              Regional Ore Intelligence Brief
            </span>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            <div className="lg:col-span-7 space-y-2">
              <h4 className="text-base font-sans font-bold text-white uppercase tracking-wide">
                Operational and Industry Intelligence
              </h4>
              <p className="text-xs sm:text-sm text-slate-300 font-sans leading-relaxed">
                National steel-grade raw material requirements indicate a 14% demand surge across Central India corridors, accelerating sensorized stope extraction. Audited ministry disclosures confirm intensified mechanical extraction schedules across high-grade braunite bands to maintain domestic supply resilience.
              </p>
            </div>

            <div className="lg:col-span-5 bg-[#05070b] p-4 rounded border border-white/10 space-y-2">
              <div className="text-[11px] font-sans font-bold text-emerald-400 uppercase tracking-wider">
                Predictive Telemetry Projection
              </div>
              <p className="text-xs text-slate-300 font-sans leading-relaxed">
                Automated variance telemetry projects a potential 1,350-tonne deficit under wet-season bench moisture; multi-stope haulage balancing is forecast to recover up to 1,050 tonnes (77.8% recovery efficiency) before end-of-month reconciliation.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
