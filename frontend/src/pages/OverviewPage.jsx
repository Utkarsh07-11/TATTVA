import React from 'react';
import { useNavigate } from 'react-router-dom';
import heroBg from '../assets/cinematic_mine_hero.jpg';
import { ArrowRight, Map, LineChart } from 'lucide-react';

export default function OverviewPage() {
  const navigate = useNavigate();

  return (
    <div className="page-enter space-y-4 sm:space-y-5 max-w-5xl mx-auto">
      {/* 1. COMPACT HERO SECTION (260-300px) */}
      <section className="relative w-full overflow-hidden rounded border border-technical bg-[#080b10] min-h-[250px] sm:min-h-[280px] flex flex-col justify-between p-5 sm:p-7">
        {/* Background Image with Cinematic High-Contrast Dark Gradient Overlay */}
        <div
          className="absolute inset-0 z-0 bg-cover bg-center opacity-35 mix-blend-luminosity filter contrast-125"
          style={{ backgroundImage: `url(${heroBg})` }}
        />
        <div className="absolute inset-0 z-0 bg-gradient-to-t from-[#07090d] via-[#07090d]/80 to-transparent" />
        <div className="absolute inset-0 z-0 bg-gradient-to-r from-[#07090d] via-[#07090d]/70 to-transparent" />

        {/* Hero Top Context */}
        <div className="relative z-10 flex items-center justify-between text-[11px] font-mono text-slate-400">
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            <span className="text-white font-bold">BALAGHAT</span>
            <span className="text-slate-600">·</span>
            <span>MADHYA PRADESH</span>
          </div>
          <div className="text-slate-400">
            21.8744°N, 80.2078°E
          </div>
        </div>

        {/* Hero Central Typography & Single Call to Action */}
        <div className="relative z-10 my-auto py-3 max-w-2xl space-y-2.5">
          <h1 className="text-2xl sm:text-3xl md:text-4xl font-black uppercase font-condensed tracking-tight text-white leading-[0.95]">
            MINE INTELLIGENCE <br />
            <span className="text-industrial-amber">FOR BETTER</span> MINE DECISIONS
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 font-sans leading-relaxed">
            Explore the mine, production and operations.
          </p>

          <div className="pt-2">
            <button
              onClick={() => navigate('/mine-map')}
              className="px-4 py-2 rounded bg-industrial-amber hover:bg-amber-400 text-black font-bold text-xs flex items-center gap-2 transition-colors cursor-pointer"
            >
              <span>OPEN DIGITAL MINE</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Hero Bottom Telemetry */}
        <div className="relative z-10 pt-2 border-t border-technical flex items-center justify-between text-[10px] font-mono text-slate-500">
          <span>CENTRAL INDIA MANGANESE BELT</span>
          <span>EPSG:32644 (UTM 44N)</span>
        </div>
      </section>

      {/* 2. DATA AVAILABILITY STRIP */}
      <section className="grid grid-cols-1 sm:grid-cols-3 gap-px bg-white/10 border border-technical rounded overflow-hidden">
        {/* Metric 1 */}
        <div className="bg-[#0b0e14] p-3 sm:p-4 flex items-center justify-between">
          <div>
            <div className="text-xl font-bold font-mono text-white">10 MINES</div>
            <div className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">Statutory Registry</div>
          </div>
          <div className="flex items-center gap-1.5 text-[10px] font-mono text-emerald-400">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            REAL
          </div>
        </div>

        {/* Metric 2 */}
        <div className="bg-[#0b0e14] p-3 sm:p-4 flex items-center justify-between">
          <div>
            <div className="text-xl font-bold font-mono text-white">27,720</div>
            <div className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">Raster Cells (30m)</div>
          </div>
          <div className="flex items-center gap-1.5 text-[10px] font-mono text-rose-400">
            <span className="w-1.5 h-1.5 rounded-full bg-rose-400"></span>
            EXPERIMENTAL
          </div>
        </div>

        {/* Metric 3 */}
        <div className="bg-[#0b0e14] p-3 sm:p-4 flex items-center justify-between">
          <div>
            <div className="text-xl font-bold font-mono text-white">FY16–FY26</div>
            <div className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">Company Production</div>
          </div>
          <div className="flex items-center gap-1.5 text-[10px] font-mono text-amber-400">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
            REPORTED
          </div>
        </div>
      </section>

      {/* 3. DIRECT WORKSPACE JUMP CARDS */}
      <section className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {/* Card 1: Digital Mine */}
        <div
          onClick={() => navigate('/mine-map')}
          className="bg-[#0a0d14] hover:bg-[#0e131d] border border-technical p-4 rounded transition-colors cursor-pointer flex items-center justify-between group"
        >
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
              <Map className="w-3.5 h-3.5 text-industrial-amber" />
              <span className="text-white font-bold uppercase font-condensed tracking-wider text-sm">DIGITAL MINE</span>
            </div>
            <p className="text-xs text-slate-400">
              Explore Balaghat satellite imagery, DEM topography, and exploration priority.
            </p>
          </div>
          <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-industrial-amber transition-colors shrink-0 ml-3" />
        </div>

        {/* Card 2: Production */}
        <div
          onClick={() => navigate('/forecast')}
          className="bg-[#0a0d14] hover:bg-[#0e131d] border border-technical p-4 rounded transition-colors cursor-pointer flex items-center justify-between group"
        >
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
              <LineChart className="w-3.5 h-3.5 text-purple-400" />
              <span className="text-white font-bold uppercase font-condensed tracking-wider text-sm">PRODUCTION</span>
            </div>
            <p className="text-xs text-slate-400">
              Operational outlook, pit block quotas, and reconciliation analysis.
            </p>
          </div>
          <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-industrial-amber transition-colors shrink-0 ml-3" />
        </div>
      </section>
    </div>
  );
}


