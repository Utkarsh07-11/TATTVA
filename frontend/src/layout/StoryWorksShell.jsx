import React, { useState } from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { Menu, X, Sparkles, ShieldCheck, UploadCloud, PlusCircle } from 'lucide-react';
import { useDashboard } from '../context/DashboardContext';
import { useAuth } from '../context/AuthContext';
import InteractiveTourCallout from '../components/InteractiveTourCallout';
import TattvaLogo from '../components/TattvaLogo';
import LoginModal from '../components/LoginModal';
import WeeklyLogUploadModal from '../components/WeeklyLogUploadModal';
import CommissionMineModal from '../components/CommissionMineModal';

export default function StoryWorksShell() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [showDemoHUD, setShowDemoHUD] = useState(false);
  const { error, loading } = useDashboard();
  const {
    user,
    tier,
    isExecutive,
    isApex,
    setIsLoginModalOpen,
    setIsWeeklyModalOpen,
    setIsCommissionModalOpen,
  } = useAuth();

  // 5 standard editorial pages + conditionally visible Governance for Tier 2/3
  const navItems = [
    { to: '/', label: 'Overview' },
    { to: '/digital-mine', label: 'Mine map' },
    { to: '/production', label: 'Production' },
    { to: '/operations', label: 'Operations' },
    ...(isExecutive ? [{ to: '/governance', label: 'Data Governance' }] : []),
    { to: '/contact', label: 'Contact' },
  ];

  const getTierColor = (t) => {
    if (t === 3) return 'border-purple-300 bg-purple-50 text-purple-900';
    if (t === 2) return 'border-blue-300 bg-blue-50 text-blue-900';
    return 'border-[#DCD5CD] bg-[#EEE6DD] text-[#26211F]';
  };

  return (
    <div className="min-h-screen text-[#26211F] flex flex-col app-shell">
      <header className="sticky top-0 z-50 bg-[#F7F4EF] border-b border-[#DCD5CD]">
        <div className="max-w-[1440px] mx-auto px-5 sm:px-8">
          <div className="flex items-center justify-between h-[72px] gap-4">
            <NavLink
              to="/"
              id="tour-brand-mark"
              className="brand-mark shrink-0 flex items-center gap-2.5 group hover:opacity-90 transition-opacity"
              onClick={() => setMobileMenuOpen(false)}
            >
              <TattvaLogo className="w-8 h-8 shrink-0 transition-transform group-hover:scale-105 duration-200" />
              <div className="flex flex-col justify-center">
                <span className="font-editorial text-xl font-bold tracking-tight text-[#26211F] leading-none">
                  TATTVA
                </span>
                <span className="brand-subtitle font-sans text-[10px] tracking-[0.16em] font-semibold text-[#8A817D] uppercase mt-0.5 leading-none">
                  Ore Intelligence
                </span>
              </div>
            </NavLink>

            {/* Desktop Navigation */}
            <nav className="hidden lg:flex items-center gap-7">
              {navItems.map(({ to, label }) => (
                <NavLink
                  key={to}
                  to={to}
                  end={to === '/'}
                  className={({ isActive }) =>
                    `nav-link px-0 py-2 text-sm font-sans font-medium transition-all relative ${
                      isActive
                        ? 'text-[#C87A5B] font-semibold'
                        : 'text-[#5A524F] hover:text-[#26211F]'
                    }`
                  }
                >
                  {label}
                </NavLink>
              ))}
            </nav>

            {/* Header Right Actions */}
            <div className="flex items-center gap-2 shrink-0">
              {/* Log Weekly WSR Modal Trigger */}
              <button
                id="tour-log-wsr"
                type="button"
                onClick={() => setIsWeeklyModalOpen(true)}
                className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-sm border border-[#C87A5B]/40 bg-[#EDC7B7]/30 hover:bg-[#EDC7B7]/60 text-[#C87A5B] text-xs font-sans font-semibold transition-colors cursor-pointer shadow-xs"
                title="Log Weekly Operational Summary (WSR)"
              >
                <UploadCloud className="w-3.5 h-3.5 text-[#C87A5B]" />
                <span>Log WSR</span>
              </button>

              {/* Commission Mine Button for Tier 3 Apex */}
              {isApex && (
                <button
                  type="button"
                  onClick={() => setIsCommissionModalOpen(true)}
                  className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-sm border border-purple-300 bg-purple-50 hover:bg-purple-100 text-purple-900 text-xs font-sans font-semibold transition-colors cursor-pointer"
                  title="Commission Brand New Mining Lease"
                >
                  <PlusCircle className="w-3.5 h-3.5 text-purple-600" />
                  <span>Commission Mine</span>
                </button>
              )}

              {/* User Tier & Semantic ID Badge (Click to Switch User) */}
              <button
                id="tour-user-badge"
                type="button"
                onClick={() => setIsLoginModalOpen(true)}
                className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-sm border text-xs font-sans font-medium transition-colors cursor-pointer shadow-xs ${getTierColor(tier)}`}
                title="Switch MOIL User Role / Tier"
              >
                <ShieldCheck className="w-3.5 h-3.5 shrink-0" />
                <span className="font-mono font-bold">{user?.employee_id}</span>
                <span className="hidden xl:inline text-[11px] opacity-80 truncate max-w-[110px]">
                  · {user?.full_name?.split(' ')[0]}
                </span>
              </button>

              {/* Demo HUD Trigger */}
              <button
                type="button"
                onClick={() => setShowDemoHUD(!showDemoHUD)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-sm border text-xs font-sans font-semibold transition-colors cursor-pointer shadow-xs ${
                  showDemoHUD
                    ? 'bg-[#C87A5B] border-[#C87A5B] text-white shadow-sm'
                    : 'bg-white border-[#DCD5CD] text-[#5A524F] hover:bg-[#EEE6DD] hover:text-[#26211F]'
                }`}
                title="Toggle Live Presentation Stepper HUD"
              >
                <Sparkles className="w-3.5 h-3.5 text-[#C87A5B]" />
                <span>Demo Tour</span>
              </button>

              <button
                type="button"
                className="lg:hidden menu-button"
                aria-label="Toggle navigation"
                aria-expanded={mobileMenuOpen}
                onClick={() => setMobileMenuOpen((open) => !open)}
              >
                {mobileMenuOpen ? <X className="w-5 h-5 text-[#26211F]" /> : <Menu className="w-5 h-5 text-[#26211F]" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation */}
        <div className={`mobile-menu lg:hidden bg-[#F7F4EF] ${mobileMenuOpen ? 'mobile-menu-open' : ''}`}>
          {navItems.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `block px-5 py-3 text-base transition-colors ${
                  isActive
                    ? 'text-[#C87A5B] bg-[#EEE6DD]/60 font-semibold'
                    : 'text-[#5A524F] hover:text-[#26211F] hover:bg-[#EEE6DD]/30'
                }`
              }
              onClick={() => setMobileMenuOpen(false)}
            >
              {label}
            </NavLink>
          ))}
          <div className="p-4 border-t border-[#DCD5CD] space-y-2">
            <button
              type="button"
              onClick={() => {
                setIsWeeklyModalOpen(true);
                setMobileMenuOpen(false);
              }}
              className="w-full py-2 px-3 rounded-sm bg-[#EDC7B7]/40 border border-[#C87A5B]/40 text-[#C87A5B] text-xs font-bold flex items-center justify-center gap-2"
            >
              <UploadCloud className="w-4 h-4" />
              <span>Log Weekly WSR</span>
            </button>
            {isApex && (
              <button
                type="button"
                onClick={() => {
                  setIsCommissionModalOpen(true);
                  setMobileMenuOpen(false);
                }}
                className="w-full py-2 px-3 rounded-sm bg-purple-50 border border-purple-300 text-purple-900 text-xs font-bold flex items-center justify-center gap-2"
              >
                <PlusCircle className="w-4 h-4" />
                <span>Commission New Mine</span>
              </button>
            )}
            <button
              type="button"
              onClick={() => {
                setIsLoginModalOpen(true);
                setMobileMenuOpen(false);
              }}
              className="w-full py-2 px-3 rounded-sm bg-white border border-[#DCD5CD] text-[#26211F] text-xs font-semibold flex items-center justify-center gap-2 shadow-xs"
            >
              <ShieldCheck className="w-4 h-4 text-[#C87A5B]" />
              <span>Switch User ({user?.employee_id})</span>
            </button>
          </div>
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
            <div className="text-xs text-[#8A817D] flex items-center gap-2">
              <span className="inline-block w-2 h-2 rounded-full bg-[#C87A5B] animate-pulse" />
              Updating the latest mine data…
            </div>
          </div>
        )}
        <Outlet />
      </main>

      {/* Interactive Speech-Bubble Callout Tour (Slack/Userpilot Style) */}
      {showDemoHUD && <InteractiveTourCallout onClose={() => setShowDemoHUD(false)} />}

      {/* Global Role Authentication & Operational Modals */}
      <LoginModal />
      <WeeklyLogUploadModal />
      <CommissionMineModal />

      <footer className="site-footer">
        <div className="max-w-[1440px] mx-auto px-5 sm:px-8 flex flex-col sm:flex-row gap-3 justify-between items-center text-xs text-[#8A817D] font-sans">
          <span>© 2026 Tattva · MOIL Limited Manganese Intelligence Platform</span>
          <div className="flex items-center gap-3">
            <span className="font-mono text-[11px] text-[#8A817D]">
              Session: {user?.employee_id} ({user?.role})
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}
