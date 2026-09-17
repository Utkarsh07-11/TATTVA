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
  theme = 'light',
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
      <div className={`flex items-center gap-1 p-1 bg-white/95 rounded-lg border border-[#DCD5CD] shadow-sm ${className}`}>
        {BASEMAP_OPTIONS.map((option) => {
          const Icon = ICON_MAP[option.icon] || Layers;
          const isSelected = option.id === currentBasemap;
          return (
            <button
              key={option.id}
              onClick={() => onSelectBasemap(option.id)}
              className={`flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono transition-colors cursor-pointer ${
                isSelected
                  ? 'bg-[#C87A5B] text-white font-bold'
                  : 'text-[#5A524F] hover:text-[#26211F] hover:bg-[#FAF7F2]'
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
        className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-xs font-mono transition-colors cursor-pointer ${
          theme === 'dark'
            ? 'border-technical bg-[#0b0e14] hover:bg-[#141b26] text-slate-200'
            : 'border-[#DCD5CD] bg-white hover:bg-[#FAF7F2] text-[#26211F] shadow-sm'
        }`}
        title="Change Basemap"
      >
        <ActiveIcon className={`w-3.5 h-3.5 ${theme === 'dark' ? 'text-industrial-amber' : 'text-[#C87A5B]'}`} />
        <span className={`${theme === 'dark' ? 'text-slate-400' : 'text-[#8A817D]'} text-[11px]`}>Basemap:</span>
        <span className={`font-semibold text-[11px] ${theme === 'dark' ? 'text-white' : 'text-[#26211F]'}`}>{activeOption.shortName || activeOption.name}</span>
        <ChevronDown className={`w-3 h-3 transition-transform duration-200 ${theme === 'dark' ? 'text-slate-400' : 'text-[#8A817D]'} ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className={`absolute right-0 mt-1 w-60 rounded-xl shadow-xl p-1.5 z-[1001] animate-in fade-in duration-100 ${
          theme === 'dark'
            ? 'bg-[#080b10] border border-technical text-white'
            : 'bg-white border border-[#DCD5CD] text-[#26211F]'
        }`}>
          <div className={`px-2 py-1 text-[10px] font-mono uppercase tracking-wider border-b flex items-center justify-between ${
            theme === 'dark' ? 'text-slate-500 border-technical' : 'text-[#8A817D] border-[#DCD5CD]'
          }`}>
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
                  className={`w-full text-left px-2 py-1.5 rounded-lg transition-colors flex items-center gap-2 cursor-pointer ${
                    isSelected
                      ? theme === 'dark'
                        ? 'bg-[#141b26] text-industrial-amber font-semibold'
                        : 'bg-[#EDC7B7]/40 text-[#8C3A1E] font-semibold border border-[#C87A5B]/30'
                      : theme === 'dark'
                      ? 'hover:bg-[#101520] text-slate-300 hover:text-white'
                      : 'hover:bg-[#FAF7F2] text-[#5A524F] hover:text-[#26211F]'
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 ${isSelected ? (theme === 'dark' ? 'text-industrial-amber' : 'text-[#C87A5B]') : (theme === 'dark' ? 'text-slate-400' : 'text-[#8A817D]')}`} />
                  <span className="text-xs truncate flex-1">{option.name}</span>
                  {isSelected && <Check className={`w-3 h-3 ml-1 shrink-0 ${theme === 'dark' ? 'text-industrial-amber' : 'text-[#C87A5B]'}`} />}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

