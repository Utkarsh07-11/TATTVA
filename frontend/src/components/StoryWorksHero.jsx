import React from 'react';
import indianHeroTruck from '../assets/indian_mines/hero-haul-road.jpg';
import BlockRevealImage from './BlockRevealImage';

export default function StoryWorksHero() {
  return (
    <section className="relative pt-6 pb-12 max-w-7xl mx-auto px-4 sm:px-6">
      {/* 1. Operational Top Attribution Bar */}
      <div className="mb-6 border-b border-[#DCD5CD] pb-4 text-slide-down">
        <span className="text-xs font-sans tracking-widest uppercase text-[#C87A5B] font-semibold">
          CENTRAL INDIA ORE BELT
        </span>
      </div>

      {/* 2. Text Fade-In & Slide-Down Animations */}
      <div className="max-w-4xl mb-8">
        <h1 className="font-editorial text-4xl sm:text-6xl lg:text-7xl font-bold text-[#26211F] tracking-tight leading-[1.06] text-slide-down-d2">
          The Mining Tech With People At The Centre
        </h1>

        <p className="mt-5 font-sans text-lg sm:text-xl text-[#5A524F] max-w-3xl leading-relaxed text-slide-down-d3">
          Precision mining is not about replacing human expertise—it is about empowering the shift supervisor with instantaneous geospatial sensing, operational shortfall diagnostics, and audited daily dispatch reconciliation.
        </p>
      </div>

      {/* 3. The Hero Visual with Real Mining Photography & Sliding Reveal */}
      <div className="relative rounded-sm overflow-hidden border border-[#DCD5CD] bg-[#EEE6DD] shadow-lg">
        <BlockRevealImage
          src={indianHeroTruck}
          alt="Heavy Haulage and Extraction Operations at the Central India Mine Face"
          aspectRatio="aspect-[16/9] sm:aspect-[21/9]"
          blockColor="bg-[#C87A5B]"
          delay={150}
        />
      </div>

      {/* 4. Operational Telemetry Cards */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="story-card p-4 border-l-2 border-l-[#C87A5B]">
          <div className="text-[10px] font-sans uppercase tracking-wider text-[#8A817D]">
            PROVENANCE
          </div>
          <div className="mt-1 text-xl font-semibold font-sans text-[#26211F]">10 Mines</div>
          <div className="text-xs text-[#5A524F] mt-1 font-sans">
            Central India statutory registry
          </div>
        </div>

        <div className="story-card p-4 border-l-2 border-l-emerald-600">
          <div className="text-[10px] font-sans uppercase tracking-wider text-[#8A817D]">
            ORE CONCENTRATION
          </div>
          <div className="mt-1 text-xl font-semibold font-sans text-[#26211F]">38.4% Share</div>
          <div className="text-xs text-[#5A524F] mt-1 font-sans">
            Regional ore output
          </div>
        </div>

        <div className="story-card p-4 border-l-2 border-l-[#C87A5B]">
          <div className="text-[10px] font-sans uppercase tracking-wider text-[#8A817D]">
            BACKTEST ACCURACY
          </div>
          <div className="mt-1 text-xl font-semibold font-sans text-[#26211F]">9.90% MAPE</div>
          <div className="text-xs text-[#5A524F] mt-1 font-sans">
            Audited 10-year walk-forward holdout
          </div>
        </div>

        <div className="story-card p-4 border-l-2 border-l-stone-400">
          <div className="text-[10px] font-sans uppercase tracking-wider text-[#8A817D]">
            GEOSPATIAL GRID
          </div>
          <div className="mt-1 text-xl font-semibold font-sans text-[#26211F]">30m Spacing</div>
          <div className="text-xs text-[#5A524F] mt-1 font-sans">
            Copernicus DEM and Sentinel-2 spectral rasters
          </div>
        </div>
      </div>
    </section>
  );
}
