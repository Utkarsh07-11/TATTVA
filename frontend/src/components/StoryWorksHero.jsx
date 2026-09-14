import React from 'react';
import bbcTruck from '../assets/bbc/truck.jpg';
import BlockRevealImage from './BlockRevealImage';

export default function StoryWorksHero() {
  return (
    <section className="relative pt-6 pb-12 max-w-7xl mx-auto px-4 sm:px-6">
      {/* 1. Operational Top Attribution Bar */}
      <div className="mb-6 border-b border-white/20 pb-4 text-slide-down">
        <span className="text-xs font-sans tracking-widest uppercase text-white font-semibold">
          CENTRAL INDIA ORE BELT
        </span>
      </div>

      {/* 2. Text Fade-In & Slide-Down Animations */}
      <div className="max-w-4xl mb-8">
        <h1 className="font-editorial text-4xl sm:text-6xl lg:text-7xl font-bold text-white tracking-tight leading-[1.06] text-slide-down-d2">
          The Mining Tech With People At The Centre
        </h1>

        <p className="mt-5 font-sans text-lg sm:text-xl text-white max-w-3xl leading-relaxed text-slide-down-d3 drop-shadow-sm">
          Precision mining is not about replacing human expertise—it is about empowering the shift supervisor with instantaneous geospatial sensing, operational shortfall diagnostics, and audited daily dispatch reconciliation.
        </p>
      </div>

      {/* 3. The Hero Visual with Real Mining Photography & Sliding Reveal */}
      <div className="relative rounded-sm overflow-hidden border border-technical bg-[#080b10] shadow-2xl">
        <BlockRevealImage
          src={bbcTruck}
          alt="Autonomous Haulage System at the Mining Face"
          aspectRatio="aspect-[16/9] sm:aspect-[21/9]"
          blockColor="bg-[#d4a574]"
          delay={150}
        />
      </div>

      {/* 4. Operational Telemetry Cards */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="story-card p-4 border-l-2 border-l-amber-500">
          <div className="text-[10px] font-sans uppercase tracking-wider text-slate-400">
            PROVENANCE
          </div>
          <div className="mt-1 text-xl font-semibold font-sans text-white">10 Mines</div>
          <div className="text-xs text-slate-400 mt-1 font-sans">
            Central India statutory registry
          </div>
        </div>

        <div className="story-card p-4 border-l-2 border-l-emerald-500">
          <div className="text-[10px] font-sans uppercase tracking-wider text-slate-400">
            ORE CONCENTRATION
          </div>
          <div className="mt-1 text-xl font-semibold font-sans text-white">38.4% Share</div>
          <div className="text-xs text-slate-400 mt-1 font-sans">
            Regional ore output
          </div>
        </div>

        <div className="story-card p-4 border-l-2 border-l-amber-500">
          <div className="text-[10px] font-sans uppercase tracking-wider text-slate-400">
            BACKTEST ACCURACY
          </div>
          <div className="mt-1 text-xl font-semibold font-sans text-white">9.90% MAPE</div>
          <div className="text-xs text-slate-400 mt-1 font-sans">
            Audited 10-year walk-forward holdout
          </div>
        </div>

        <div className="story-card p-4 border-l-2 border-l-slate-600">
          <div className="text-[10px] font-sans uppercase tracking-wider text-slate-400">
            GEOSPATIAL GRID
          </div>
          <div className="mt-1 text-xl font-semibold font-sans text-white">30m Spacing</div>
          <div className="text-xs text-slate-400 mt-1 font-sans">
            Copernicus DEM and Sentinel-2 spectral rasters
          </div>
        </div>
      </div>
    </section>
  );
}
