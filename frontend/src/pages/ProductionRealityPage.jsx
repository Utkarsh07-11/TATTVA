import React, { useEffect, useState } from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';
import { TrendingUp, CheckCircle2 } from 'lucide-react';
import BlockRevealImage from '../components/BlockRevealImage';
import ProductionAnalytics from '../components/ProductionAnalytics';
import { api } from '../services/api';
import { useDashboard } from '../context/DashboardContext';

// Authentic Field Photography
import bbcDark1 from '../assets/bbc/dark-1.jpg';
import canonicalBacktest from '../data/canonical_backtest.json';

function fmt(n) {
  return Number(n || 0).toLocaleString();
}

export default function ProductionRealityPage() {
  const { forecast, selectedBlock } = useDashboard();
  const [backtest, setBacktest] = useState(canonicalBacktest);

  useEffect(() => {
    api.getHistoricalBacktest()
      .then(setBacktest)
      .catch((err) => console.warn('Historical backtest notice:', err.message));
  }, []);

  const chartData = (backtest?.history || []).map((row) => {
    const fold = (backtest.folds || []).find((f) => f.fiscal_year === row.fiscal_year);
    return {
      year: row.fiscal_year,
      actual: row.production_mt,
      naive: fold?.naive_last_year_mt,
      ridge: fold?.ridge_trend_mt,
    };
  });

  return (
    <div className="space-y-14 pb-20 max-w-7xl mx-auto px-4 sm:px-6 pt-6">
      {/* 1. Header with Slide-Down Animation */}
      <div className="border-b border-technical pb-6">
        <div className="text-xs font-sans tracking-wider text-amber-500 uppercase font-semibold mb-2 flex items-center gap-2 text-slide-down">
          <TrendingUp className="w-3.5 h-3.5 text-amber-500" />
          <span>STATUTORY GROUND TRUTH AND BACKTESTING</span>
        </div>

        <h1 className="font-editorial text-3xl sm:text-5xl text-white font-bold tracking-tight text-slide-down-d1">
          Audited Production Benchmarks and Historical Verification
        </h1>

        <p className="mt-4 font-sans text-base sm:text-lg text-slate-300 max-w-3xl leading-relaxed text-slide-down-d2">
          Operational extraction planning demands verifiable historical benchmarks. Before guiding daily stope schedules, our yield models are audited against ten consecutive financial years of statutory filings submitted to the Ministry of Steel and Parliament.
        </p>
      </div>

      {/* 2. Formal White Section: The Domain Bridge Hierarchy */}
      <section className="bg-white text-slate-900 border border-slate-200 p-6 sm:p-10 rounded-xs">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          <div className="lg:col-span-7 space-y-4">
            <span className="text-xs font-sans uppercase tracking-wider text-amber-700 font-bold">
              AUDIT PROVENANCE AND HISTORICAL ALIGNMENT
            </span>
            <h3 className="font-sans text-2xl sm:text-3xl font-bold text-slate-950">
              The Operational Bridge: From Statutory Filings to Pit Faces
            </h3>
            <p className="font-sans text-sm text-slate-700 leading-relaxed">
              No single pit operates in isolation. By grounding our baselines in ten years of statutory Ministry of Steel filings (Lok Sabha Unstarred Q.1774 and MOIL Annual Report 2023-24), our planning tools capture true macroeconomic cycles—such as national market fluctuations and high-grade shaft expansions—before estimating daily block variances.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2 font-sans text-xs">
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-xs">
                <span className="text-slate-500 block text-[11px]">CORPORATE ANNUAL</span>
                <span className="font-bold text-slate-950 text-sm">1.75M Tonnes</span>
                <span className="text-slate-500 block text-[10px]">Total Production</span>
              </div>
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-xs">
                <span className="text-slate-500 block text-[11px]">REGIONAL SHARE</span>
                <span className="font-bold text-amber-800 text-sm">~670,000 Tonnes</span>
                <span className="text-slate-500 block text-[10px]">38.4% Output</span>
              </div>
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-xs">
                <span className="text-slate-500 block text-[11px]">PIT TARGET</span>
                <span className="font-bold text-emerald-700 text-sm">10,000 t / mo</span>
                <span className="text-slate-500 block text-[10px]">Active Shift Stope</span>
              </div>
            </div>
          </div>

          <div className="lg:col-span-5">
            <BlockRevealImage
              src={bbcDark1}
              alt="Underground mining haulage cross-cut"
              aspectRatio="aspect-[4/3]"
              blockColor="bg-[#d4a574]"
            />
          </div>
        </div>
      </section>

      {/* 3. Walk-Forward Cross Validation Metric Scorecards */}
      {backtest && (
        <section className="space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <span className="text-xs font-sans text-amber-500 uppercase tracking-wider font-semibold">
                STATUTORY PRODUCTION BACKTEST
              </span>
              <h3 className="font-sans text-2xl text-white font-bold">
                10-Year Historical Model Calibration
              </h3>
            </div>
            <span className="text-xs font-sans text-slate-400">
              Calibration Window: FY15 → FY24 (Held-out 1-step ahead walk-forward evaluation)
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(backtest.methods).map(([name, metrics]) => {
              const isWinner = backtest.winner === name;
              return (
                <div
                  key={name}
                  className={`story-card p-5 relative ${
                    isWinner ? 'border-amber-500/60 bg-[#0f141f]' : ''
                  }`}
                >
                  {isWinner && (
                    <div className="absolute top-3 right-3 flex items-center gap-1 text-[10px] font-sans font-bold text-amber-400 bg-amber-500/15 px-2 py-0.5 rounded-xs border border-amber-500/40">
                      <CheckCircle2 className="w-3 h-3" />
                      <span>BEST ACCURACY</span>
                    </div>
                  )}
                  <div className="text-xs font-sans uppercase tracking-wider text-slate-400">
                    {name.replaceAll('_', ' ')}
                  </div>
                  <div className="mt-2 text-2xl sm:text-3xl font-sans font-bold text-white tracking-tight">
                    {metrics.mape_pct}%{' '}
                    <span className="text-xs font-normal text-slate-400 font-sans">MAPE</span>
                  </div>
                  <div className="mt-2 text-xs font-sans text-slate-400 space-y-1">
                    <div>MAE: {fmt(metrics.mae_mt)} tonnes</div>
                    <div>Directional Accuracy: {metrics.directional_accuracy_pct}%</div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Actual vs Held-Out Prediction Chart */}
          <div className="story-card p-6 border border-technical">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
              <div>
                <h4 className="font-sans text-lg text-white font-bold">
                  Audited Production vs Held-Out Model Projections
                </h4>
                <p className="text-xs font-sans text-slate-400">
                  Statutory ore tonnages published by the Ministry of Steel compared against out-of-sample model projections.
                </p>
              </div>
              <div className="text-xs font-sans text-slate-400 flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-400" /> Audited Actual
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" /> Trend Projection
                <span className="w-2.5 h-2.5 rounded-full bg-slate-500" /> Prior Year Baseline
              </div>
            </div>

            <div className="h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={chartData} margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#222f44" opacity={0.4} />
                  <XAxis dataKey="year" stroke="#64748b" fontSize={11} />
                  <YAxis
                    stroke="#64748b"
                    fontSize={11}
                    tickFormatter={(v) => `${(v / 100000).toFixed(1)}L t`}
                  />
                  <Tooltip
                    contentStyle={{
                      background: '#0b0e14',
                      border: '1px solid rgba(255,255,255,0.1)',
                      borderRadius: 4,
                      fontFamily: 'Inter, sans-serif',
                      fontSize: 12,
                    }}
                    formatter={(value) => [`${fmt(value)} metric tonnes`, '']}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="actual"
                    name="Published Actual"
                    stroke="#f59e0b"
                    strokeWidth={2.5}
                    dot={{ r: 4, fill: '#f59e0b' }}
                  />
                  <Line
                    type="monotone"
                    dataKey="naive"
                    name="Prior Year Baseline"
                    stroke="#64748b"
                    strokeDasharray="4 4"
                    strokeWidth={1.8}
                    connectNulls
                  />
                  <Line
                    type="monotone"
                    dataKey="ridge"
                    name="Calibrated Trend Projection"
                    stroke="#10b981"
                    strokeWidth={2.2}
                    connectNulls
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Holdout Fold Audit Table */}
          <div className="story-card p-6 overflow-x-auto">
            <h4 className="font-sans text-lg text-white font-bold mb-3">
              Annual Statutory Backtest Audit Log
            </h4>
            <table className="w-full text-xs font-sans text-left">
              <thead className="text-slate-400 border-b border-white/10 uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="py-2.5 pr-4">Fiscal Year</th>
                  <th className="py-2.5 pr-4">Audited Actual</th>
                  <th className="py-2.5 pr-4">Prior Year Baseline</th>
                  <th className="py-2.5 pr-4">3-Yr Rolling MA</th>
                  <th className="py-2.5 pr-4">Calibrated Trend</th>
                  <th className="py-2.5">Annual Variance</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {backtest.folds.map((fold) => (
                  <tr key={fold.fiscal_year} className="hover:bg-white/5 transition-colors">
                    <td className="py-2.5 pr-4 font-bold text-white">{fold.fiscal_year}</td>
                    <td className="py-2.5 pr-4 text-amber-400 font-semibold">{fmt(fold.actual_mt)} t</td>
                    <td className="py-2.5 pr-4 text-slate-400">{fmt(fold.naive_last_year_mt)} t</td>
                    <td className="py-2.5 pr-4 text-slate-400">{fmt(fold.moving_average_3y_mt)} t</td>
                    <td className="py-2.5 pr-4 text-emerald-400 font-semibold">{fmt(fold.ridge_trend_mt)} t</td>
                    <td
                      className={`py-2.5 font-bold ${
                        fold.ridge_error_mt > 0 ? 'text-amber-400' : 'text-emerald-400'
                      }`}
                    >
                      {fold.ridge_error_mt > 0 ? '+' : ''}
                      {fmt(fold.ridge_error_mt)} t
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* 4. Operational Pit-Face Quantile Forecast */}
      <section className="border-t border-technical pt-10 space-y-6">
        <div>
          <div className="text-xs font-sans tracking-wider text-amber-500 uppercase font-semibold mb-1">
            DAILY EXTRACTION TELEMETRY
          </div>
          <h3 className="story-headline text-2xl text-white font-bold mt-1">
            Stope Extraction Run-Rate and Daily Production Analytics
          </h3>
          <p className="text-xs text-slate-400 font-sans mt-1 max-w-2xl">
            Daily underground ore haulage tracking and predictive run-rate analysis for {selectedBlock}, calibrated against historical stope cycles, muckpile fragmentation, and seasonal wet-haulage constraints.
          </p>
        </div>

        <div className="story-card p-4">
          <ProductionAnalytics forecast={forecast} selectedBlock={selectedBlock} />
        </div>
      </section>

      {/* 5. STATUTORY PRODUCTION RECONCILIATION AND DECADAL MODEL AUDIT */}
      <section className="story-card p-6 sm:p-8 border-l-4 border-l-amber-500 rounded-sm bg-[#0a0e17]">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-technical pb-3 mb-4 gap-2">
          <span className="text-xs font-sans font-bold text-amber-400 uppercase tracking-wider">
            Statutory Production Reconciliation and Decadal Model Audit
          </span>
          <span className="text-[11px] font-sans text-slate-400 font-medium">
            Ministry of Steel Benchmarking
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          <div className="lg:col-span-7 space-y-2">
            <h4 className="text-base font-sans font-bold text-white uppercase tracking-wide">
              Operational and Industry Intelligence
            </h4>
            <p className="text-xs sm:text-sm text-slate-300 font-sans leading-relaxed">
              Audited production filings benchmark regional output at 1.75 million tonnes annually, contributing 38.4% of domestic high-grade ore. Ministry oversight verifies that systematic haulage reporting and digital weighbridge audits eliminate optimistic dispatch assumptions across active shafts.
            </p>
          </div>

          <div className="lg:col-span-5 bg-[#05070b] p-4 rounded border border-white/10 space-y-2">
            <div className="text-[11px] font-sans font-bold text-emerald-400 uppercase tracking-wider">
              Predictive Telemetry Projection
            </div>
            <p className="text-xs text-slate-300 font-sans leading-relaxed">
              10-year walk-forward backtest holdouts maintain a 9.90% MAPE accuracy, predicting stable baseline yields of 8,650 tonnes against the 10,000-tonne quota and alerting dispatch 72 hours before monthly quotas deviate.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
