import { useEffect, useState } from 'react';
import { type ExamTab } from '../types';
import { IconDoc, IconBuilding, IconCalendar, IconPlus, IconSearch, IconClose } from './icons';

interface HeaderProps {
  activeTab: ExamTab;
  setActiveTab: (tab: ExamTab) => void;
  onOpenLookup: () => void;
  onNewRegistration: () => void;
}

const TABS: { id: ExamTab; label: string; icon: (cls: string) => React.ReactNode }[] = [
  { id: 'register', label: 'Qeydiyyat', icon: (cls) => <IconPlus className={cls} /> },
  { id: 'schedule', label: 'Cədvəl', icon: (cls) => <IconCalendar className={cls} /> },
  { id: 'centers', label: 'Mərkəzlər', icon: (cls) => <IconBuilding className={cls} /> },
  { id: 'rules', label: 'Qaydalar', icon: (cls) => <IconDoc className={cls} /> },
];

export function Header({ activeTab, setActiveTab, onOpenLookup, onNewRegistration }: HeaderProps) {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24);
    onScroll();
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const goTo = (tab: ExamTab) => {
    setActiveTab(tab);
    setMobileOpen(false);
  };

  return (
    <header
      className={`sticky top-0 z-40 bg-slate-950/80 backdrop-blur-xl border-b border-white/5 transition-shadow ${
        scrolled ? 'shadow-2xl shadow-black/30' : ''
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-18">
          {/* Logo */}
          <button
            onClick={() => goTo('register')}
            className="flex items-center gap-3 cursor-pointer group"
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-500/25 group-hover:shadow-emerald-500/40 transition-shadow">
              <span className="text-white font-bold text-lg">S</span>
            </div>
            <div className="text-left hidden sm:block">
              <span className="text-white font-bold text-lg leading-none block">
                Oğuz <span className="text-emerald-400">Sınaq</span>
              </span>
              <span className="text-gray-500 text-xs tracking-widest uppercase">Portalı</span>
            </div>
          </button>

          {/* Desktop Tabs */}
          <nav className="hidden md:flex items-center gap-1">
            {TABS.map((tab) => {
              const active = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => goTo(tab.id)}
                  className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-xl transition-all cursor-pointer ${
                    active
                      ? 'text-white bg-emerald-500/10 border border-emerald-500/30'
                      : 'text-gray-400 hover:text-white hover:bg-white/5 border border-transparent'
                  }`}
                >
                  {tab.icon('w-4 h-4')}
                  {tab.label}
                </button>
              );
            })}
          </nav>

          {/* Actions */}
          <div className="flex items-center gap-2.5">
            <button
              onClick={onOpenLookup}
              className="hidden sm:inline-flex items-center gap-2 px-4 py-2.5 text-sm font-semibold text-gray-300 hover:text-white bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl transition-all cursor-pointer"
            >
              <IconSearch className="w-4 h-4" />
              Qeydiyyatı axtar
            </button>
            <button
              onClick={onNewRegistration}
              className="inline-flex items-center gap-2 px-4 sm:px-5 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-600 text-white text-sm font-semibold rounded-xl shadow-lg shadow-emerald-500/25 hover:shadow-emerald-500/40 hover:-translate-y-0.5 transition-all cursor-pointer"
            >
              <IconPlus className="w-4 h-4" />
              <span className="hidden sm:inline">Yeni qeydiyyat</span>
              <span className="sm:hidden">Qeydiyyat</span>
            </button>
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="md:hidden p-2 text-gray-400 hover:text-white rounded-lg hover:bg-white/10 transition-colors cursor-pointer"
            >
              {mobileOpen ? (
                <IconClose className="w-6 h-6" />
              ) : (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {mobileOpen && (
        <div className="md:hidden bg-slate-900/95 backdrop-blur-xl border-t border-white/5">
          <div className="px-4 py-4 space-y-1">
            {TABS.map((tab) => {
              const active = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => goTo(tab.id)}
                  className={`flex items-center gap-3 w-full text-left px-4 py-3 text-sm font-medium rounded-xl transition-all cursor-pointer ${
                    active
                      ? 'text-white bg-emerald-500/10 border border-emerald-500/30'
                      : 'text-gray-400 hover:text-white hover:bg-white/5'
                  }`}
                >
                  {tab.icon('w-4 h-4')}
                  {tab.label}
                </button>
              );
            })}
            <button
              onClick={() => {
                setMobileOpen(false);
                onOpenLookup();
              }}
              className="flex items-center gap-3 w-full text-left px-4 py-3 text-sm font-medium text-gray-400 hover:text-white rounded-xl hover:bg-white/5 transition-all cursor-pointer"
            >
              <IconSearch className="w-4 h-4" />
              Qeydiyyatı axtar
            </button>
          </div>
        </div>
      )}
    </header>
  );
}
