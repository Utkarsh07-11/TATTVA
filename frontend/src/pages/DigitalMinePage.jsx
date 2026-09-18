import React from 'react';
import { Globe, Satellite, Compass, MapPin } from 'lucide-react';
import DigitalMineMap from '../components/DigitalMineMap';
import BlockRevealImage from '../components/BlockRevealImage';
import { useDashboard } from '../context/DashboardContext';

// Authentic Indian Field Photography
import indianExcavatorBench from '../assets/indian_mines/excavator-terrace-bench.jpg';

export default function DigitalMinePage() {
  const { prospectivityGeoJson, drillholesGeoJson, blocksGeoJson, equipmentList, selectedBlock } = useDashboard();

  return (
    <div className="space-y-12 pb-20 max-w-7xl mx-auto px-4 sm:px-6 pt-6">
      {/* 1. Header with Slide-Down Animation */}
      <div className="border-b border-[#DCD5CD] pb-6">
        <div className="text-xs font-sans tracking-wider text-[#C87A5B] uppercase font-semibold mb-2 flex items-center gap-2 text-slide-down">
          <Satellite className="w-3.5 h-3.5 text-[#C87A5B]" />
          <span>ORBITAL AND TERRESTRIAL CARTOGRAPHY</span>
        </div>

        <h1 className="font-editorial text-3xl sm:text-5xl text-[#26211F] font-bold tracking-tight text-slide-down-d1">
          Spatial Intelligence Across the Sausar Belt
        </h1>

        <p className="mt-4 font-sans text-base sm:text-lg text-[#5A524F] max-w-3xl leading-relaxed text-slide-down-d2">
          From 786 kilometers in orbit, European Space Agency Sentinel-2 multispectral sensors capture reflectance bands that penetrate the forest canopy. Fused with Copernicus 30-meter elevation models and ground-truth Survey of India boundaries, satellite analytics reveal spectral signatures of ore-bearing formations long before physical core drilling commences.
        </p>

        <div className="mt-6 flex flex-wrap items-center gap-4 text-xs font-sans text-[#5A524F] text-slide-down-d3">
          <div className="flex items-center gap-1.5 bg-white px-3 py-1.5 rounded-sm border border-[#DCD5CD] shadow-xs">
            <Globe className="w-3.5 h-3.5 text-[#C87A5B]" />
            <span>Survey of India National Boundary Verified</span>
          </div>
          <div className="flex items-center gap-1.5 bg-white px-3 py-1.5 rounded-sm border border-[#DCD5CD] shadow-xs">
            <Compass className="w-3.5 h-3.5 text-[#8A817D]" />
            <span>UTM Zone 44N (EPSG:32644) Projected</span>
          </div>
          <div className="flex items-center gap-1.5 bg-white px-3 py-1.5 rounded-sm border border-[#DCD5CD] shadow-xs">
            <MapPin className="w-3.5 h-3.5 text-emerald-700" />
            <span>10 Statutory Mining Leases</span>
          </div>
        </div>
      </div>

      {/* 2. Formal Warm Linen Section: Ground Truthing the Spaceborne Spectrum */}
      <section className="bg-[#FAF7F2] text-[#26211F] border border-[#DCD5CD] p-6 sm:p-10 rounded-sm shadow-xs">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          <div className="lg:col-span-7 space-y-4">
            <span className="text-xs font-sans uppercase tracking-wider text-[#C87A5B] font-bold">
              GROUND TRUTH RECONNAISSANCE
            </span>
            <h3 className="font-sans text-2xl sm:text-3xl font-bold text-[#26211F]">
              Calibrating Spaceborne Reflectance with Pit Benches
            </h3>
            <p className="font-sans text-sm text-[#5A524F] leading-relaxed">
              Orbital sensors alone cannot substitute for geological ground reality. In the Sausar Group, thick lateritic overburden can mask mineralization signatures. By pairing Sentinel-2 Band 8A (Narrow NIR) and Band 11 (SWIR) ratios with physical pit benches, false anomaly positives from dense vegetation are filtered out.
            </p>
            <div className="grid grid-cols-2 gap-4 pt-2 font-sans text-xs text-[#5A524F]">
              <div className="border-l-2 border-[#C87A5B] pl-3">
                <div className="font-bold text-[#26211F]">Band 4 / Band 2</div>
                <div className="text-[11px] text-[#8A817D]">Iron Oxide and Ferruginous Index</div>
              </div>
              <div className="border-l-2 border-stone-400 pl-3">
                <div className="font-bold text-[#26211F]">Band 8 / Band 11</div>
                <div className="text-[11px] text-[#8A817D]">Clay and Hydrothermal Alteration</div>
              </div>
            </div>
          </div>

          <div className="lg:col-span-5">
            <BlockRevealImage
              src={indianExcavatorBench}
              alt="Terraced opencast mine benches and heavy extraction equipment in Central India"
              aspectRatio="aspect-[16/10]"
              blockColor="bg-[#C87A5B]"
            />
          </div>
        </div>
      </section>

      {/* 3. Interactive Digital Mine Cartographic Station */}
      <div className="rounded-lg border-2 border-[#DCD5CD] bg-[#FAF7F2] shadow-xl p-1 overflow-hidden relative z-0 isolate">
        <DigitalMineMap
          prospectivityGeoJson={prospectivityGeoJson}
          drillholesGeoJson={drillholesGeoJson}
          blocksGeoJson={blocksGeoJson}
          equipmentList={equipmentList}
          selectedBlock={selectedBlock}
        />
      </div>

      {/* 4. GEOSPATIAL INTELLIGENCE AND ANOMALY EXPLORATION BRIEFING */}
      <section className="story-card p-6 sm:p-8 border-l-4 border-l-[#C87A5B] rounded-sm bg-white border border-[#DCD5CD]">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-[#DCD5CD] pb-3 mb-4 gap-2">
          <span className="text-xs font-sans font-bold text-[#C87A5B] uppercase tracking-wider">
            Geospatial Intelligence and Anomaly Exploration Briefing
          </span>
          <span className="text-[11px] font-sans text-[#8A817D] font-medium">
            Orbital Remote Sensing Dispatch
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          <div className="lg:col-span-7 space-y-2">
            <h4 className="text-base font-sans font-bold text-[#26211F] uppercase tracking-wide">
              Operational and Industry Intelligence
            </h4>
            <p className="text-xs sm:text-sm text-[#5A524F] font-sans leading-relaxed">
              Remote sensing integration pairs ESA Sentinel-2 SWIR band ratios with 30m Copernicus elevation rasters across the Sausar Group. Systematic spectral ratio calibration isolates lateritic cover from exposed manganiferous lenses, eliminating false positives from dense forest canopy.
            </p>
          </div>

          <div className="lg:col-span-5 bg-[#FAF7F2] p-4 rounded border border-[#DCD5CD] space-y-2">
            <div className="text-[11px] font-sans font-bold text-emerald-700 uppercase tracking-wider">
              Predictive Telemetry Projection
            </div>
            <p className="text-xs text-[#5A524F] font-sans leading-relaxed">
              Combined isolation forest anomaly ranking and spatial distance modeling predict a 28% higher probability of concealed mineralized reef extension northeast of current portals without initial surface clearing.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
