import { useState, useEffect, useCallback } from 'react';
import { Link, useLocation } from 'react-router-dom';

const navLinks = [
  { label: 'Haqqımızda', href: '#about' },
  { label: 'Nailiyyətlər', href: '#achievements' },
  { label: 'Fənlər', href: '#courses' },
  { label: 'Müəllimlər', href: '#teachers' },
  { label: 'Əlaqə', href: '#contact' },
];

export default function PublicLayout({ children }: { children: React.ReactNode }) {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  useEffect(() => { setMobileOpen(false); }, [location]);

  const scrollTo = useCallback((href: string) => {
    const el = document.querySelector(href);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  }, []);

  useEffect(() => {
    if (location.hash) {
      const timer = setTimeout(() => scrollTo(location.hash), 100);
      return () => clearTimeout(timer);
    }
  }, [location, scrollTo]);

  const handleNav = (href: string) => {
    window.history.pushState(null, '', href);
    scrollTo(href);
  };

  return (
    <div className="min-h-screen bg-[#0a0a1a]">
      {/* Navbar */}
      <nav
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          scrolled
            ? 'bg-[#0a0a1a]/90 backdrop-blur-xl border-b border-white/5 shadow-2xl shadow-black/20'
            : 'bg-transparent'
        }`}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-18">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-3 group">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/25 group-hover:shadow-indigo-500/40 transition-shadow">
                <span className="text-white font-bold text-lg">O</span>
              </div>
              <span className="text-white font-bold text-lg hidden sm:block">
                Oğuz <span className="text-indigo-400">TM</span>
              </span>
            </Link>

            {/* Desktop Nav */}
            <div className="hidden md:flex items-center gap-1">
              {navLinks.map((link) => (
                <button
                  key={link.href}
                  onClick={() => handleNav(link.href)}
                  className="px-4 py-2 text-sm font-medium text-gray-400 hover:text-white rounded-lg hover:bg-white/5 transition-all cursor-pointer"
                >
                  {link.label}
                </button>
              ))}
              <Link
                to="/sinaq"
                className="px-4 py-2 text-sm font-medium text-emerald-400 hover:text-white rounded-lg hover:bg-emerald-500/10 transition-all"
              >
                Sınaq
              </Link>
            </div>

            {/* CTA */}
            <div className="flex items-center gap-3">
              <Link
                to="/login"
                className="hidden sm:inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-indigo-500 to-violet-600 text-white text-sm font-semibold rounded-xl hover:shadow-lg hover:shadow-indigo-500/25 transition-all hover:-translate-y-0.5"
              >
                Kabinet
              </Link>
              <button
                onClick={() => setMobileOpen(!mobileOpen)}
                className="md:hidden p-2 text-gray-400 hover:text-white rounded-lg hover:bg-white/10 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  {mobileOpen ? (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  ) : (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  )}
                </svg>
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileOpen && (
          <div className="md:hidden bg-[#0d0d24]/95 backdrop-blur-xl border-t border-white/5">
            <div className="px-4 py-4 space-y-1">
              {navLinks.map((link) => (
                <button
                  key={link.href}
                  onClick={() => handleNav(link.href)}
                  className="block w-full text-left px-4 py-3 text-sm font-medium text-gray-400 hover:text-white rounded-lg hover:bg-white/5 transition-all"
                >
                  {link.label}
                </button>
              ))}
              <Link
                to="/sinaq"
                className="block w-full text-left px-4 py-3 text-sm font-medium text-emerald-400 rounded-lg hover:bg-emerald-500/10 transition-all"
              >
                Sınaq
              </Link>
              <Link
                to="/login"
                className="block w-full text-center px-4 py-3 bg-gradient-to-r from-indigo-500 to-violet-600 text-white text-sm font-semibold rounded-xl mt-3"
              >
                Kabinetə Giriş
              </Link>
            </div>
          </div>
        )}
      </nav>

      {/* Content */}
      <main>{children}</main>

      {/* Footer */}
      <footer className="relative bg-[#060614] border-t border-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-12">
            {/* Brand */}
            <div className="md:col-span-1">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center">
                  <span className="text-white font-bold text-lg">O</span>
                </div>
                <span className="text-white font-bold text-lg">
                  Oğuz <span className="text-indigo-400">TM</span>
                </span>
              </div>
              <p className="text-gray-500 text-sm leading-relaxed">
                Azərbaycanda təhsil sahəsində aparıcı tədris mərkəzi. Gələcəyinizi bizimlə qurun.
              </p>
              <div className="flex gap-3 mt-5">
                {['instagram', 'youtube', 'linkedin'].map((s) => (
                  <a
                    key={s}
                    href="#"
                    className="w-9 h-9 rounded-lg bg-white/5 flex items-center justify-center text-gray-500 hover:text-white hover:bg-white/10 transition-all"
                  >
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                      <circle cx="12" cy="12" r="4" />
                    </svg>
                  </a>
                ))}
              </div>
            </div>

            {/* Links */}
            <div>
              <h4 className="text-white font-semibold text-sm mb-4">Sürətli Keçidlər</h4>
              <ul className="space-y-2.5">
                <li>
                  <button onClick={() => handleNav('#about')} className="text-gray-500 text-sm hover:text-indigo-400 transition-colors">Haqqımızda</button>
                </li>
                <li>
                  <button onClick={() => handleNav('#courses')} className="text-gray-500 text-sm hover:text-indigo-400 transition-colors">Fənlər</button>
                </li>
                <li>
                  <button onClick={() => handleNav('#teachers')} className="text-gray-500 text-sm hover:text-indigo-400 transition-colors">Müəllimlər</button>
                </li>
                <li>
                  <button onClick={() => handleNav('#achievements')} className="text-gray-500 text-sm hover:text-indigo-400 transition-colors">Nailiyyətlər</button>
                </li>
                <li>
                  <button onClick={() => handleNav('#contact')} className="text-gray-500 text-sm hover:text-indigo-400 transition-colors">Əlaqə</button>
                </li>
                <li>
                  <Link to="/sinaq" className="text-gray-500 text-sm hover:text-emerald-400 transition-colors">Sınaq imtahanları</Link>
                </li>
              </ul>
            </div>

            {/* Programs */}
            <div>
              <h4 className="text-white font-semibold text-sm mb-4">İxtisaslar</h4>
              <ul className="space-y-2.5">
                {['Proqramlaşdırma', 'Veb Dizayn', 'Robototexnika', 'Rəqəmsal Savadlılıq'].map((l) => (
                  <li key={l}>
                    <span className="text-gray-500 text-sm">{l}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Contact */}
            <div>
              <h4 className="text-white font-semibold text-sm mb-4">Əlaqə</h4>
              <ul className="space-y-3">
                <li className="flex items-center gap-2.5 text-gray-500 text-sm">
                  <svg className="w-4 h-4 text-indigo-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                  +994 XX XXX XX XX
                </li>
                <li className="flex items-center gap-2.5 text-gray-500 text-sm">
                  <svg className="w-4 h-4 text-indigo-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  Bakı, Azərbaycan
                </li>
                <li className="flex items-center gap-2.5 text-gray-500 text-sm">
                  <svg className="w-4 h-4 text-indigo-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  info@oguztm.az
                </li>
              </ul>
            </div>
          </div>

          <div className="mt-12 pt-8 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-gray-600 text-xs">
              &copy; 2026 Oğuz Tədris Mərkəzi. Bütün hüquqlar qorunur.
            </p>
            <p className="text-gray-700 text-xs">
              Powered by <span className="text-indigo-500 font-semibold">AI Technology</span>
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
