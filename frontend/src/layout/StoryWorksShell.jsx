import React, { useState } from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { Menu, X, Sparkles } from 'lucide-react';
import { useDashboard } from '../context/DashboardContext';
import DemoPresenterHUD from '../components/DemoPresenterHUD';

const navItems = [
  { to: '/', label: 'Overview' },
  { to: '/digital-mine', label: 'Mine map' },
  { to: '/production', label: 'Production' },
  { to: '/operations', label: 'Operations' },
  { to: '/contact', label: 'Contact' },
];

export default function StoryWorksShell() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [showDemoHUD, setShowDemoHUD] = useState(false);
  const { error, loading } = useDashboard();

  return (
    <div className="min-h-screen text-slate-200 flex flex-col app-shell">
      <header className="sticky top-0 z-50 bg-black/95 backdrop-blur-md border-b border-white/10">
        <div className="max-w-[1440px] mx-auto px-5 sm:px-8">
          <div className="flex items-center justify-between h-[72px] gap-4">
            <NavLink to="/" className="brand-mark" onClick={() => setMobileMenuOpen(false)}>
              <span className="brand-dot" />
              <span className="font-editorial text-xl font-bold tracking-tight text-white">TATTVA</span>
              <span className="brand-subtitle font-sans text-xs tracking-wider text-slate-400">Ore Intelligence</span>
            </NavLink>

            {/* Desktop 5-Page Story Navigation */}
            <nav className="hidden md:flex items-center gap-8">
              {navItems.map(({ to, label }) => (
                <NavLink
                  key={to}
                  to={to}
                  end={to === '/'}
                  className={({ isActive }) =>
                    `nav-link px-0 py-2 text-sm font-sans font-medium transition-all relative ${
                      isActive
                        ? 'text-white font-semibold'
                        : 'text-slate-400 hover:text-white'
                    }`
                  }
                >
                  {label}
                </NavLink>
              ))}
            </nav>

            <div className="flex items-center gap-2 shrink-0">
              <button
                type="button"
                onClick={() => setShowDemoHUD(!showDemoHUD)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xs border text-xs font-sans font-semibold transition-colors cursor-pointer ${
                  showDemoHUD
                    ? 'bg-amber-950/80 border-amber-600 text-amber-300 shadow-sm shadow-amber-950/40'
                    : 'bg-[#0e121a] border-technical text-amber-300 hover:bg-amber-950/40 hover:text-amber-200'
                }`}
                title="Toggle Live Presentation Stepper HUD"
              >
                <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                <span>Demo Tour</span>
              </button>

              <button
                type="button"
                className="md:hidden menu-button"
                aria-label="Toggle navigation"
                aria-expanded={mobileMenuOpen}
                onClick={() => setMobileMenuOpen((open) => !open)}
              >
                {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </button>
            </div>
          </div>
        </div>

        <div className={`mobile-menu md:hidden ${mobileMenuOpen ? 'mobile-menu-open' : ''}`}>
          {navItems.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `block px-5 py-3.5 text-base transition-colors ${
                  isActive
                    ? 'text-white bg-white/[0.06]'
                    : 'text-slate-400 hover:text-white hover:bg-white/[0.03]'
                }`
              }
              onClick={() => setMobileMenuOpen(false)}
            >
              {label}
            </NavLink>
          ))}
        </div>
      </header>

      <main className="flex-1 w-full">
        {error && (
          <div className="max-w-[1440px] mx-auto px-5 sm:px-8 pt-4">
            <div className="data-notice">
              Live data is temporarily unavailable. The dashboard will reconnect automatically when the service is back online.
            </div>
          </div>
        )}
        {loading && !error && (
          <div className="max-w-[1440px] mx-auto px-5 sm:px-8 pt-3">
            <div className="text-xs text-slate-400 flex items-center gap-2">
              <span className="inline-block w-2 h-2 rounded-full bg-lime-300 animate-pulse" />
              Updating the latest mine data…
            </div>
          </div>
        )}
        <Outlet />
      </main>

      {/* Floating Live Presentation Stepper HUD */}
      {showDemoHUD && <DemoPresenterHUD onClose={() => setShowDemoHUD(false)} />}

      <footer className="site-footer">
        <div className="max-w-[1440px] mx-auto px-5 sm:px-8 flex flex-col sm:flex-row gap-3 justify-between items-center">
          <span>© 2026 Tattva · Ore mining operations</span>
        </div>
      </footer>
    </div>
  );
}
