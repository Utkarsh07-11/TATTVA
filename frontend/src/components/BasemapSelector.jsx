import React, { useState, useRef, useEffect } from 'react';
import { Layers, Globe, Map as MapIcon, Mountain, Moon, Check, ChevronDown } from 'lucide-react';
import { BASEMAP_OPTIONS } from '../config/basemaps';

const ICON_MAP = {
  Moon: Moon,
  Globe: Globe,
  Layers: Layers,
  Map: MapIcon,
  Mountain: Mountain,
};

export default function BasemapSelector({
  currentBasemap,
  onSelectBasemap,
  variant = 'dropdown',
  className = '',
}) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef(null);

  const activeOption = BASEMAP_OPTIONS.find((b) => b.id === currentBasemap) || BASEMAP_OPTIONS[0];
  const ActiveIcon = ICON_MAP[activeOption.icon] || Layers;

  // Handle click outside to close dropdown
  useEffect(() => {
    function handleClickOutside(event) {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  if (variant === 'pills') {
    return (
      <div className={`flex items-center gap-1 p-0.5 bg-[#0b0e14]/90 rounded border border-technical ${className}`}>
        {BASEMAP_OPTIONS.map((option) => {
          const Icon = ICON_MAP[option.icon] || Layers;
          const isSelected = option.id === currentBasemap;
          return (
            <button
              key={option.id}
              onClick={() => onSelectBasemap(option.id)}
              className={`flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono transition-colors ${
                isSelected
                  ? 'bg-industrial-amber text-black font-bold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-[#141b26]'
              }`}
              title={option.description}
            >
              <Icon className="w-3 h-3" />
              <span>{option.shortName}</span>
            </button>
          );
        })}
      </div>
    );
  }

  return (
    <div ref={containerRef} className={`relative inline-block ${className}`}>
      {/* Selector Trigger Button */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-1.5 px-2.5 py-1 rounded border border-technical bg-[#0b0e14] hover:bg-[#141b26] text-slate-200 text-xs font-mono transition-colors cursor-pointer"
        title="Change Basemap"
      >
        <ActiveIcon className="w-3.5 h-3.5 text-industrial-amber" />
        <span className="text-slate-400 text-[11px]">Basemap:</span>
        <span className="font-semibold text-white text-[11px]">{activeOption.shortName || activeOption.name}</span>
        <ChevronDown className={`w-3 h-3 text-slate-400 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute right-0 mt-1 w-60 bg-[#080b10] border border-technical rounded shadow-2xl p-1 z-[1001] animate-in fade-in duration-100">
          <div className="px-2 py-1 text-[10px] font-mono text-slate-500 uppercase tracking-wider border-b border-technical flex items-center justify-between">
            <span>Basemap Imagery</span>
            <span>5 Styles</span>
          </div>

          <div className="mt-1 space-y-0.5">
            {BASEMAP_OPTIONS.map((option) => {
              const Icon = ICON_MAP[option.icon] || Layers;
              const isSelected = option.id === currentBasemap;

              return (
                <button
                  key={option.id}
                  type="button"
                  onClick={() => {
                    onSelectBasemap(option.id);
                    setIsOpen(false);
                  }}
                  className={`w-full text-left px-2 py-1.5 rounded transition-colors flex items-center gap-2 ${
                    isSelected
                      ? 'bg-[#141b26] text-industrial-amber font-semibold'
                      : 'hover:bg-[#101520] text-slate-300 hover:text-white'
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 ${isSelected ? 'text-industrial-amber' : 'text-slate-400'}`} />
                  <span className="text-xs truncate flex-1">{option.name}</span>
                  {isSelected && <Check className="w-3 h-3 text-industrial-amber ml-1 shrink-0" />}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

