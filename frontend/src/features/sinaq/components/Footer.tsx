import { type ExamTab } from '../types';
import { IconCalendar, IconBuilding, IconDoc, IconPlus, IconSearch, IconLocation, IconPhone, IconTicket } from './icons';

interface FooterProps {
  setActiveTab: (tab: ExamTab) => void;
  onOpenLookup: () => void;
}

export function Footer({ setActiveTab, onOpenLookup }: FooterProps) {
  const links: { tab: ExamTab; label: string }[] = [
    { tab: 'register', label: 'Qeydiyyat' },
    { tab: 'schedule', label: 'İmtahan cədvəli' },
    { tab: 'centers', label: 'Mərkəzlər' },
    { tab: 'rules', label: 'İmtahan qaydaları' },
  ];

  return (
    <footer className="relative bg-[#060614] border-t border-white/5">
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-emerald-500/40 to-transparent" />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12">
          {/* Brand */}
          <div className="md:col-span-1">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center">
                <span className="text-white font-bold text-lg">S</span>
              </div>
              <span className="text-white font-bold text-lg">
                Oğuz <span className="text-emerald-400">Sınaq</span>
              </span>
            </div>
            <p className="text-gray-500 text-sm leading-relaxed">
              Abituriyentlər üçün real imtahan formatına uyğun sınaq imtahanları. Qeydiyyatdan keçin, biletinizi alın və nəticənizi izləyin.
            </p>
            <div className="flex gap-3 mt-5">
              {['instagram', 'youtube', 'telegram'].map((s) => (
                <a
                  key={s}
                  href="#"
                  className="w-9 h-9 rounded-lg bg-white/5 flex items-center justify-center text-gray-500 hover:text-emerald-400 hover:bg-white/10 transition-all"
                >
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                    <circle cx="12" cy="12" r="4" />
                  </svg>
                </a>
              ))}
            </div>
          </div>

          {/* Quick links */}
          <div>
            <h4 className="text-white font-semibold text-sm mb-4">Bölmələr</h4>
            <ul className="space-y-2.5">
              {links.map((l) => (
                <li key={l.tab}>
                  <button
                    onClick={() => setActiveTab(l.tab)}
                    className="flex items-center gap-2 text-gray-500 text-sm hover:text-emerald-400 transition-colors cursor-pointer"
                  >
                    {l.tab === 'register' ? (
                      <IconPlus className="w-4 h-4" />
                    ) : l.tab === 'schedule' ? (
                      <IconCalendar className="w-4 h-4" />
                    ) : l.tab === 'centers' ? (
                      <IconBuilding className="w-4 h-4" />
                    ) : (
                      <IconDoc className="w-4 h-4" />
                    )}
                    {l.label}
                  </button>
                </li>
              ))}
              <li>
                <button
                  onClick={onOpenLookup}
                  className="flex items-center gap-2 text-gray-500 text-sm hover:text-emerald-400 transition-colors cursor-pointer"
                >
                  <IconTicket className="w-4 h-4" />
                  Bilet yoxla
                </button>
              </li>
            </ul>
          </div>

          {/* Info */}
          <div>
            <h4 className="text-white font-semibold text-sm mb-4">Məlumat</h4>
            <ul className="space-y-2.5">
              <li className="text-gray-500 text-sm">Qeydiyyat imtahandan 1 gün öncə bağlanır.</li>
              <li className="text-gray-500 text-sm">Buraxılış vərəqəsi qeydiyyatdan sonra elektron şəkildə təqdim olunur.</li>
              <li className="text-gray-500 text-sm">Nəticələr imtahandan 5 gün sonra portalda dərc olunur.</li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="text-white font-semibold text-sm mb-4">Əlaqə</h4>
            <ul className="space-y-3">
              <li className="flex items-center gap-2.5 text-gray-500 text-sm">
                <IconPhone className="w-4 h-4 text-emerald-400 shrink-0" />
                +994 12 123 45 67
              </li>
              <li className="flex items-center gap-2.5 text-gray-500 text-sm">
                <IconLocation className="w-4 h-4 text-emerald-400 shrink-0" />
                Bakı, Binəqədi qəsəbəsi, S. Vurğun 43
              </li>
              <li className="flex items-center gap-2.5 text-gray-500 text-sm">
                <svg className="w-4 h-4 text-emerald-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                sinaq@oguztm.az
              </li>
            </ul>
            <button
              onClick={onOpenLookup}
              className="mt-5 inline-flex items-center gap-2 px-4 py-2.5 bg-white/5 hover:bg-white/10 border border-white/10 text-gray-300 hover:text-white text-sm font-semibold rounded-xl transition-all cursor-pointer"
            >
              <IconSearch className="w-4 h-4" />
              Qeydiyyatı axtar
            </button>
          </div>
        </div>

        <div className="mt-12 pt-8 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-gray-600 text-xs">
            &copy; 2026 Oğuz Tədris Mərkəzi · Sınaq Portalı. Bütün hüquqlar qorunur.
          </p>
          <p className="text-gray-700 text-xs">
            Powered by <span className="text-emerald-500 font-semibold">AI Technology</span>
          </p>
        </div>
      </div>
    </footer>
  );
}
