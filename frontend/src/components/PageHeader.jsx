import React from 'react';

export default function PageHeader({ kicker, title, subtitle, rightElement }) {
  return (
    <div className="mb-4 pb-2.5 border-b border-[#DCD5CD] flex flex-col sm:flex-row sm:items-end justify-between gap-2.5">
      <div>
        {kicker && (
          <div className="text-[10px] uppercase tracking-widest text-[#C87A5B] font-sans font-semibold mb-0.5">
            {kicker}
          </div>
        )}
        <h1 className="text-xl sm:text-2xl font-bold font-editorial text-[#26211F] tracking-wide leading-tight">
          {title}
        </h1>
        {subtitle && (
          <p className="text-xs text-[#5A524F] mt-0.5 max-w-3xl font-sans leading-normal">
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

