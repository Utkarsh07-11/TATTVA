import React from 'react';
import { Layers, Cpu, Clock, CheckCircle2 } from 'lucide-react';
import StoryWorksHero from '../components/StoryWorksHero';
import BlockRevealImage from '../components/BlockRevealImage';
import { useDashboard } from '../context/DashboardContext';

// Authentic Indian Field Photography
import indianDozer from '../assets/indian_mines/dozer-crawler-push.jpg';
import indianShovelWorker from '../assets/indian_mines/shovel-dumper-worker.jpg';
import indianElectricShovel from '../assets/indian_mines/electric-rope-shovel.jpg';
import indianUndergroundStope from '../assets/indian_mines/underground-stope-cavern.jpg';
import indianAerialDrone from '../assets/indian_mines/aerial-drone-pit.jpg';

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

      {/* 2. FORMAL WARM LINEN SECTION: Geological Baseline & Predictive Telemetry */}
      <section className="bg-[#FAF7F2] text-[#26211F] border-y border-[#DCD5CD] py-16 sm:py-20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">
            {/* Left Column: Known Facts, Raw Data & Predictive Data */}
            <div className="lg:col-span-7 space-y-6">
              <div className="text-xs font-sans tracking-wider text-[#C87A5B] uppercase font-bold">
                OPERATIONAL BASELINE AND KNOWN DATA
              </div>

              <h2 className="font-sans text-3xl sm:text-4xl font-bold text-[#26211F] leading-[1.15]">
                Central India Ore Belt · Geological Baseline and Predictive Telemetry
              </h2>

              <p className="font-sans text-sm text-[#5A524F] leading-relaxed">
                Authoritative geological specifications, extraction telemetry, and predictive model parameters compiled from statutory records and real-time stope instrumentation.
              </p>

              {/* Data Group 1: Known Geological & In-Situ Facts (Raw Data) */}
              <div className="border border-[#DCD5CD] rounded-sm p-4 bg-white space-y-3 shadow-xs">
                <div className="flex items-center justify-between border-b border-[#DCD5CD] pb-2">
                  <span className="text-xs font-sans font-bold text-[#26211F] uppercase tracking-wider">
                    Known Geological Baseline (In-Situ)
                  </span>
                  <span className="text-[11px] font-sans text-[#8A817D] font-semibold">Audited Stratigraphy</span>
                </div>
                <div className="grid grid-cols-2 gap-3 text-xs font-sans">
                  <div>
                    <span className="text-[#8A817D] block text-[11px]">GEOLOGICAL STRATA</span>
                    <span className="font-semibold text-[#26211F]">Precambrian Sausar Belt</span>
                  </div>
                  <div>
                    <span className="text-[#8A817D] block text-[11px]">HOST LITHOLOGY</span>
                    <span className="font-semibold text-[#26211F]">Mansar Schist / Braunite Ore</span>
                  </div>
                  <div>
                    <span className="text-[#8A817D] block text-[11px]">ASSAY ORE GRADE</span>
                    <span className="font-semibold text-[#C87A5B]">42.8% Average Concentration</span>
                  </div>
                  <div>
                    <span className="text-[#8A817D] block text-[11px]">HAULAGE HORIZON</span>
                    <span className="font-semibold text-[#26211F]">300m Underground Level</span>
                  </div>
                </div>
              </div>

              {/* Data Group 2: Operational Observed Telemetry (Raw Shift Data) */}
              <div className="border border-[#DCD5CD] rounded-sm p-4 bg-white space-y-3 shadow-xs">
                <div className="flex items-center justify-between border-b border-[#DCD5CD] pb-2">
                  <span className="text-xs font-sans font-bold text-[#26211F] uppercase tracking-wider">
                    Operational Extraction Parameters (Raw Data)
                  </span>
                  <span className="text-[11px] font-sans text-emerald-700 font-semibold">Active Shift Telemetry</span>
                </div>
                <div className="grid grid-cols-2 gap-3 text-xs font-sans">
                  <div>
                    <span className="text-[#8A817D] block text-[11px]">ACTIVE WORKFORCE</span>
                    <span className="font-semibold text-[#26211F]">18 Shift Personnel Active</span>
                  </div>
                  <div>
                    <span className="text-[#8A817D] block text-[11px]">EXCAVATOR PAYLOAD</span>
                    <span className="font-semibold text-[#26211F]">42.0 Tonnes / Pass</span>
                  </div>
                  <div>
                    <span className="text-[#8A817D] block text-[11px]">HAUL CYCLE TIME</span>
                    <span className="font-semibold text-[#26211F]">18.4 Minutes / Round Trip</span>
                  </div>
                  <div>
                    <span className="text-[#8A817D] block text-[11px]">RUN-RATE CAPACITY</span>
                    <span className="font-semibold text-emerald-700">~41.2 Tonnes / Operating Hour</span>
                  </div>
                </div>
              </div>

              {/* Data Group 3: Predictive Shortfall Metrics (Predictable Data) */}
              <div className="border border-[#EDC7B7] rounded-sm p-4 bg-[#FAF7F2] space-y-3 shadow-xs">
                <div className="flex items-center justify-between border-b border-[#EDC7B7]/60 pb-2">
                  <span className="text-xs font-sans font-bold text-[#26211F] uppercase tracking-wider">
                    Predictive Shortfall Outlook (Forecast)
                  </span>
                  <span className="text-[11px] font-sans text-rose-700 font-semibold">Variance Projection</span>
                </div>
                <div className="grid grid-cols-2 gap-3 text-xs font-sans">
                  <div>
                    <span className="text-[#8A817D] block text-[11px]">STATUTORY QUOTA</span>
                    <span className="font-semibold text-[#26211F]">10,000 Tonnes / Month</span>
                  </div>
                  <div>
                    <span className="text-[#8A817D] block text-[11px]">PREDICTED YIELD (P50)</span>
                    <span className="font-semibold text-[#26211F]">8,650 Tonnes (±650 t)</span>
                  </div>
                  <div>
                    <span className="text-[#8A817D] block text-[11px]">FORECAST DEFICIT</span>
                    <span className="font-semibold text-rose-700">-1,350 Tonnes (13.5%)</span>
                  </div>
                  <div>
                    <span className="text-[#8A817D] block text-[11px]">PRIMARY SENSITIVITY</span>
                    <span className="font-semibold text-[#26211F]">Equipment Availability and Blasting</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Column: Clean Authentic Photography with Block Reveal */}
            <div className="lg:col-span-5 space-y-6">
              <BlockRevealImage
                src={indianDozer}
                alt="Crawler pushers and heavy dozers operating on an Indian opencast mining bench"
                aspectRatio="aspect-[4/3]"
                blockColor="bg-[#C87A5B]"
                delay={100}
              />

              <div className="p-4 bg-white border border-[#DCD5CD] rounded-sm space-y-2.5 shadow-xs">
                <div className="flex items-center justify-between border-b border-[#DCD5CD] pb-1.5">
                  <span className="text-xs font-sans font-bold text-[#C87A5B] uppercase">
                    STOPE CONTEXT #{selectedBlock}
                  </span>
                  <span className="text-xs font-sans text-emerald-700 font-semibold">18 Crew Active</span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs font-sans text-[#5A524F]">
                  <div>
                    <span className="text-[#8A817D] block text-[10px]">HOST ROCK:</span>
                    <span className="font-semibold text-[#26211F]">Mansar Schist Strata</span>
                  </div>
                  <div>
                    <span className="text-[#8A817D] block text-[10px]">AVERAGE GRADE:</span>
                    <span className="font-semibold text-[#C87A5B]">42.8% Braunite</span>
                  </div>
                </div>
              </div>

              <BlockRevealImage
                src={indianShovelWorker}
                alt="Indian mining shovel operator loading haulage dumper at the ore face"
                aspectRatio="aspect-[16/10]"
                blockColor="bg-[#BAB2B5]"
                delay={250}
              />
            </div>
          </div>
        </div>
      </section>

      {/* 2.5 CORE PURPOSE & OPERATIONAL DECISION-SUPPORT WORKFLOW */}
      <section className="bg-white text-[#26211F] border-b border-[#DCD5CD] py-16">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 space-y-10">
          <div className="max-w-3xl space-y-3">
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded bg-[#EDC7B7]/30 border border-[#EDC7B7] text-[#C87A5B] font-sans text-xs tracking-wider uppercase font-semibold">
              SYSTEM PURPOSE AND CORE OBJECTIVE
            </div>
            <h2 className="font-sans text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight text-[#26211F]">
              End-to-End Ore Shortfall Detection and Decision Support
            </h2>
            <p className="font-sans text-base sm:text-lg text-[#5A524F] leading-relaxed">
              The system detects ore shortfalls by analyzing historical data and incorporating real-time operational data. When a potential or current shortfall is detected, the system analyzes the situation and provides an appropriate solution or recommendation to address it.
            </p>
            <p className="font-sans text-xs sm:text-sm text-[#8A817D] leading-relaxed">
              More than an isolated forecasting model, TATTVA operates as a complete shortfall detection and decision-support workflow—bridging 10 years of audited statutory production baselines with live underground stope telemetry to protect monthly production targets.
            </p>
          </div>

          {/* Key Workflow: 2-Track Architectural Pipelines */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Track 1: Historical Data Pipeline */}
            <div className="p-6 rounded bg-[#FAF7F2] border border-[#DCD5CD] space-y-4 shadow-sm">
              <div className="flex items-center justify-between pb-3 border-b border-[#DCD5CD]">
                <span className="font-sans text-xs tracking-wider uppercase text-[#C87A5B] font-bold">
                  PIPELINE A · HISTORICAL INTELLIGENCE
                </span>
                <span className="text-xs font-sans text-[#8A817D]">10-Year Audited Baseline</span>
              </div>
              <div className="flex items-center gap-2 text-xs font-sans">
                <div className="flex-1 p-2.5 rounded bg-white border border-[#DCD5CD] text-center shadow-xs">
                  <span className="text-[#8A817D] block text-[10px]">INPUT</span>
                  <span className="font-semibold text-[#26211F] text-xs">Historical Data</span>
                </div>
                <span className="text-[#BAB2B5] font-bold text-xs">→</span>
                <div className="flex-1 p-2.5 rounded bg-white border border-[#DCD5CD] text-center shadow-xs">
                  <span className="text-[#8A817D] block text-[10px]">ANALYSIS</span>
                  <span className="font-semibold text-[#26211F] text-xs">Identify Patterns</span>
                </div>
                <span className="text-[#BAB2B5] font-bold text-xs">→</span>
                <div className="flex-1 p-2.5 rounded bg-white border border-[#DCD5CD] text-center shadow-xs">
                  <span className="text-[#8A817D] block text-[10px]">OUTPUT</span>
                  <span className="font-semibold text-[#26211F] text-xs">Predict Shortfall</span>
                </div>
              </div>
              <p className="text-xs text-[#5A524F] font-sans leading-relaxed">
                Extracts decadal production trends and seasonal capacity variations from official Ministry of Steel filings to eliminate optimistic forecasting bias.
              </p>
            </div>

            {/* Track 2: Real-Time Operational Pipeline */}
            <div className="p-6 rounded bg-[#FAF7F2] border border-[#DCD5CD] space-y-4 shadow-sm">
              <div className="flex items-center justify-between pb-3 border-b border-[#DCD5CD]">
                <span className="font-sans text-xs tracking-wider uppercase text-emerald-700 font-bold">
                  PIPELINE B · REAL-TIME DISPATCH
                </span>
                <span className="text-xs font-sans text-[#8A817D]">Live Stope Telemetry</span>
              </div>
              <div className="flex items-center gap-1.5 text-xs font-sans">
                <div className="flex-1 p-2 rounded bg-white border border-[#DCD5CD] text-center shadow-xs">
                  <span className="text-[#8A817D] block text-[10px]">TELEMETRY</span>
                  <span className="font-semibold text-[#26211F] text-xs">Real-Time Data</span>
                </div>
                <span className="text-[#BAB2B5] font-bold text-xs">→</span>
                <div className="flex-1 p-2 rounded bg-white border border-[#DCD5CD] text-center shadow-xs">
                  <span className="text-[#8A817D] block text-[10px]">DETECTION</span>
                  <span className="font-semibold text-[#26211F] text-xs">Detect Deficit</span>
                </div>
                <span className="text-[#BAB2B5] font-bold text-xs">→</span>
                <div className="flex-1 p-2 rounded bg-white border border-[#DCD5CD] text-center shadow-xs">
                  <span className="text-[#8A817D] block text-[10px]">DIAGNOSTICS</span>
                  <span className="font-semibold text-[#26211F] text-xs">Analyze Situation</span>
                </div>
                <span className="text-[#BAB2B5] font-bold text-xs">→</span>
                <div className="flex-1 p-2 rounded bg-white border border-[#DCD5CD] text-center shadow-xs">
                  <span className="text-[#8A817D] block text-[10px]">ACTION</span>
                  <span className="font-semibold text-[#26211F] text-xs">Provide Solution</span>
                </div>
              </div>
              <p className="text-xs text-[#5A524F] font-sans leading-relaxed">
                Streams excavator payload weights, fleet availability, and blasting stoppages to determine exact physical bottlenecks and issue corrective dispatch actions.
              </p>
            </div>
          </div>

          {/* Overall 4-Stage Decision Support Architecture */}
          <div className="p-6 rounded bg-[#F7F4EF] border border-[#DCD5CD] space-y-3">
            <div className="text-xs font-sans uppercase tracking-wider text-[#8A817D] font-bold">
              OVERALL 4-STAGE OPERATIONAL ARCHITECTURE
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-1">
              <div className="p-4 rounded bg-white border border-[#DCD5CD] space-y-1.5 shadow-xs">
                <div className="text-[#C87A5B] font-sans font-bold text-xs">01 · DATA FUSION</div>
                <div className="font-semibold text-[#26211F] text-sm">Historical and Real-Time</div>
                <p className="text-xs text-[#5A524F] font-sans">Learns from 10-year mining history while incorporating live underground stope sensors.</p>
              </div>
              <div className="p-4 rounded bg-white border border-[#DCD5CD] space-y-1.5 shadow-xs">
                <div className="text-[#C87A5B] font-sans font-bold text-xs">02 · SHORTFALL DETECTION</div>
                <div className="font-semibold text-[#26211F] text-sm">Quantified Risk Alerts</div>
                <p className="text-xs text-[#5A524F] font-sans">Detects potential or current ore deficits days before monthly quotas slip.</p>
              </div>
              <div className="p-4 rounded bg-white border border-[#DCD5CD] space-y-1.5 shadow-xs">
                <div className="text-[#C87A5B] font-sans font-bold text-xs">03 · SITUATION ANALYSIS</div>
                <div className="font-semibold text-[#26211F] text-sm">Factor Decomposition</div>
                <p className="text-xs text-[#5A524F] font-sans">Analyzes equipment availability, blasting delays, and weather impacts.</p>
              </div>
              <div className="p-4 rounded bg-white border border-[#DCD5CD] space-y-1.5 shadow-xs">
                <div className="text-[#C87A5B] font-sans font-bold text-xs">04 · DECISION SUPPORT</div>
                <div className="font-semibold text-[#26211F] text-sm">Targeted Solutions</div>
                <p className="text-xs text-[#5A524F] font-sans">Delivers solver-optimized haulage schedules and What-If simulation interventions.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 3. TECHNICAL OPERATIONAL STATION */}
      <section className="bg-[#FAF7F2] py-16 border-b border-[#DCD5CD]">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 space-y-8">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#DCD5CD] pb-4">
            <div>
              <div className="text-xs font-sans tracking-wider text-[#C87A5B] uppercase font-semibold mb-1">
                CURRENT EXTRACTION TELEMETRY
              </div>
              <h3 className="story-headline text-2xl sm:text-3xl text-[#26211F] font-bold">
                Stope Production Quota vs Predictive Run-Rate
              </h3>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-xs font-sans text-[#8A817D]">Select Mine Block:</span>
              {['BLOCK_A', 'BLOCK_B', 'BLOCK_C'].map((b) => (
                <button
                  key={b}
                  onClick={() => setSelectedBlock(b)}
                  className={`px-3 py-1 rounded text-xs font-sans transition-all duration-200 cursor-pointer ${
                    selectedBlock === b
                      ? 'bg-[#C87A5B] text-white font-bold border border-[#C87A5B] shadow-sm'
                      : 'bg-white text-[#5A524F] hover:text-[#26211F] hover:border-[#C87A5B] border border-[#DCD5CD]'
                  }`}
                >
                  {b.replace('_', ' ')}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Target */}
            <div className="story-card p-5 border-t-2 border-t-[#BAB2B5]">
              <div className="text-xs font-sans text-[#8A817D] uppercase tracking-wider">
                Monthly Quota
              </div>
              <div className="mt-2 text-2xl sm:text-3xl font-sans font-bold text-[#26211F] tracking-tight">
                {target.toLocaleString()} <span className="text-sm font-normal text-[#8A817D] font-sans">t</span>
              </div>
              <div className="mt-3 text-xs font-sans text-[#8A817D] border-t border-[#DCD5CD] pt-2 flex justify-between">
                <span>Allocated Stope</span>
                <span className="text-[#26211F] font-semibold">{selectedBlock}</span>
              </div>
            </div>

            {/* Forecast */}
            <div className="story-card p-5 border-t-2 border-t-[#C87A5B]">
              <div className="text-xs font-sans text-[#C87A5B] uppercase tracking-wider">
                Projected Run-Rate (P50)
              </div>
              <div className="mt-2 text-2xl sm:text-3xl font-sans font-bold text-[#26211F] tracking-tight">
                {p50.toLocaleString()} <span className="text-sm font-normal text-[#8A817D] font-sans">t</span>
              </div>
              <div className="mt-3 text-xs font-sans text-[#8A817D] border-t border-[#DCD5CD] pt-2 flex justify-between">
                <span>90% Envelope</span>
                <span className="text-[#26211F]">[{p10.toLocaleString()} - {p90.toLocaleString()}]</span>
              </div>
            </div>

            {/* Gap */}
            <div className="story-card p-5 border-t-2 border-t-[#C87A5B]">
              <div className="text-xs font-sans text-[#C87A5B] uppercase tracking-wider">
                Projected Shortfall
              </div>
              <div className="mt-2 text-2xl sm:text-3xl font-sans font-bold text-[#C87A5B] tracking-tight">
                {shortfall > 0 ? `-${shortfall.toLocaleString()}` : '0'}{' '}
                <span className="text-sm font-normal text-[#8A817D] font-sans">t</span>
              </div>
              <div className="mt-3 text-xs font-sans text-[#8A817D] border-t border-[#DCD5CD] pt-2 flex justify-between">
                <span>Quota Delta</span>
                <span className="text-[#C87A5B] font-bold">{shortfallPct}%</span>
              </div>
            </div>

            {/* Probability */}
            <div className="story-card p-5 border-t-2 border-t-rose-500">
              <div className="text-xs font-sans text-rose-700 uppercase tracking-wider">
                Shortfall Probability
              </div>
              <div className="mt-2 text-2xl sm:text-3xl font-sans font-bold text-rose-700 flex items-center gap-2 tracking-tight">
                <span>{prob}%</span>
                <span className="text-xs font-sans px-2 py-0.5 rounded bg-rose-50 border border-rose-300 text-rose-800 font-medium">
                  {riskLevel} RISK
                </span>
              </div>
              <div className="mt-3 text-xs font-sans text-[#8A817D] border-t border-[#DCD5CD] pt-2 flex justify-between">
                <span>Recommended Action</span>
                <span className="text-[#26211F] font-medium">Hauler Redeployment</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 4. FORMAL PHOTO SECTION: Geological Reconnaissance */}
      <section className="bg-white text-[#26211F] border-b border-[#DCD5CD] py-16 sm:py-20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 space-y-10">
          <div className="max-w-2xl">
            <div className="text-xs font-sans tracking-wider text-[#C87A5B] uppercase font-bold">
              GEOLOGICAL RECONNAISSANCE
            </div>
            <h3 className="font-sans text-3xl sm:text-4xl font-bold text-[#26211F] mt-1">
              Field Validation and Stratigraphic Logging
            </h3>
            <p className="font-sans text-sm text-[#5A524F] mt-2 leading-relaxed">
              Geological baseline verification across surface benches and drill-core specimens. Operational run-rates are calibrated directly against in-situ rock stability and assay grades.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <BlockRevealImage
              src={indianElectricShovel}
              alt="Electric rope shovel excavating ore in sunlit Central India open-pit bench"
              aspectRatio="aspect-[4/3]"
              blockColor="bg-[#C87A5B]"
              delay={100}
            />

            <BlockRevealImage
              src={indianUndergroundStope}
              alt="Illuminated subterranean stope cavern and rock strata profile"
              aspectRatio="aspect-[4/3]"
              blockColor="bg-[#BAB2B5]"
              delay={250}
            />

            <BlockRevealImage
              src={indianAerialDrone}
              alt="Aerial telemetry and excavator bench deployment across pit quarry"
              aspectRatio="aspect-[4/3]"
              blockColor="bg-[#EDC7B7]"
              delay={400}
            />
          </div>
        </div>
      </section>

      {/* 5. 24-HOUR EXTRACTION CYCLE TELEMETRY */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 pt-12">
        <div className="border-t border-[#DCD5CD] pt-10">
          <div className="text-xs font-sans tracking-wider text-[#C87A5B] uppercase font-semibold mb-1">
            SHIFT TELEMETRY LOG
          </div>
          <h3 className="story-headline text-2xl sm:text-3xl text-[#26211F] font-bold mb-8">
            Chronology of a 24-Hour Operational Cycle
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="story-card p-5 relative">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-sans font-bold text-[#26211F]">06:00 - 08:30</span>
                <Clock className="w-4 h-4 text-[#8A817D]" />
              </div>
              <div className="font-sans text-[#26211F] text-base font-bold mb-1">
                Phase 1 · Telemetric Face Scan
              </div>
              <p className="text-xs text-[#5A524F] leading-relaxed font-sans">
                Laser profiling of blasted wall surfaces coupled with spectrometer assay measurements to calibrate ore boundary models.
              </p>
            </div>

            <div className="story-card p-5 relative">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-sans font-bold text-[#26211F]">09:00 - 13:00</span>
                <CheckCircle2 className="w-4 h-4 text-[#8A817D]" />
              </div>
              <div className="font-sans text-[#26211F] text-base font-bold mb-1">
                Phase 2 · Semi-Auto Mucking
              </div>
              <p className="text-xs text-[#5A524F] leading-relaxed font-sans">
                Underground load-haul-dump loaders operate on guided paths, reducing personnel exposure to unsupported roofs.
              </p>
            </div>

            <div className="story-card p-5 relative">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-sans font-bold text-[#26211F]">14:00 - 18:00</span>
                <Cpu className="w-4 h-4 text-[#8A817D]" />
              </div>
              <div className="font-sans text-[#26211F] text-base font-bold mb-1">
                Phase 3 · Dispatch Rebalancing
              </div>
              <p className="text-xs text-[#5A524F] leading-relaxed font-sans">
                FastAPI LP optimizer calculates revised dumper routing when excavator hydraulic pressure drops below threshold.
              </p>
            </div>

            <div className="story-card p-5 relative">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-sans font-bold text-[#26211F]">19:00 - 23:00</span>
                <Layers className="w-4 h-4 text-[#8A817D]" />
              </div>
              <div className="font-sans text-[#26211F] text-base font-bold mb-1">
                Phase 4 · Reality Reconciliation
              </div>
              <p className="text-xs text-[#5A524F] leading-relaxed font-sans">
                Surface weighbridge tonnages cross-referenced with held-out walk-forward forecasts to update next-day baseline priors.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 6. OPERATIONAL INTELLIGENCE AND PREDICTIVE YIELD OUTLOOK */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 pt-12 pb-6">
        <div className="story-card p-6 sm:p-8 border-l-4 border-l-[#C87A5B] rounded-sm bg-white border border-[#DCD5CD]">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-[#DCD5CD] pb-3 mb-4 gap-2">
            <span className="text-xs font-sans font-bold text-[#C87A5B] uppercase tracking-wider">
              Operational Intelligence and Predictive Yield Outlook
            </span>
            <span className="text-[11px] font-sans text-[#8A817D] font-medium">
              Regional Ore Intelligence Brief
            </span>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            <div className="lg:col-span-7 space-y-2">
              <h4 className="text-base font-sans font-bold text-[#26211F] uppercase tracking-wide">
                Operational and Industry Intelligence
              </h4>
              <p className="text-xs sm:text-sm text-[#5A524F] font-sans leading-relaxed">
                National steel-grade raw material requirements indicate a 14% demand surge across Central India corridors, accelerating sensorized stope extraction. Audited ministry disclosures confirm intensified mechanical extraction schedules across high-grade braunite bands to maintain domestic supply resilience.
              </p>
            </div>

            <div className="lg:col-span-5 bg-[#FAF7F2] p-4 rounded border border-[#DCD5CD] space-y-2">
              <div className="text-[11px] font-sans font-bold text-emerald-700 uppercase tracking-wider">
                Predictive Telemetry Projection
              </div>
              <p className="text-xs text-[#5A524F] font-sans leading-relaxed">
                Automated variance telemetry projects a potential 1,350-tonne deficit under wet-season bench moisture; multi-stope haulage balancing is forecast to recover up to 1,050 tonnes (77.8% recovery efficiency) before end-of-month reconciliation.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
