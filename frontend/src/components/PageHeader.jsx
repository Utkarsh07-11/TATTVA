import React from 'react';

export default function PageHeader({ kicker, title, subtitle, rightElement }) {
  return (
    <div className="mb-4 pb-2.5 border-b border-technical flex flex-col sm:flex-row sm:items-end justify-between gap-2.5">
      <div>
        {kicker && (
          <div className="text-[10px] uppercase tracking-widest text-industrial-amber font-mono font-semibold mb-0.5">
            {kicker}
          </div>
        )}
        <h1 className="text-xl sm:text-2xl font-extrabold uppercase font-condensed text-white tracking-wide leading-tight">
          {title}
        </h1>
        {subtitle && (
          <p className="text-xs text-slate-400 mt-0.5 max-w-3xl font-sans leading-normal">
            {subtitle}
          </p>
        )}
      </div>
      {rightElement && (
        <div className="self-start sm:self-auto shrink-0 font-mono">
          {rightElement}
        </div>
      )}
    </div>
  );
}

