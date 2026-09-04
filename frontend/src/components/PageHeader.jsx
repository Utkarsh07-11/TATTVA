import React from 'react';

export default function PageHeader({ kicker, title, subtitle }) {
  return (
    <div className="mb-5">
      <div className="text-[11px] uppercase tracking-[0.2em] text-copper-400 font-semibold">{kicker}</div>
      <h2 className="mt-1 text-2xl font-semibold tracking-tight">{title}</h2>
      {subtitle && <p className="mt-1 text-sm text-slate-400 max-w-3xl">{subtitle}</p>}
    </div>
  );
}
