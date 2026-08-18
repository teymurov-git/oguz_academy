import { EXAM_CENTERS } from '../data/mockExams';
import { IconBuilding, IconLocation, IconPhone } from './icons';

export function ExamCentersView() {
  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="text-center mb-10">
        <h2 className="text-2xl sm:text-3xl font-bold text-white">İmtahan Mərkəzləri</h2>
        <p className="text-gray-500 text-sm mt-2">Sınaq imtahanlarının keçirildiyi tədris mərkəzləri.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {EXAM_CENTERS.map((c) => (
          <div
            key={c.id}
            className="bg-slate-900/60 border border-white/10 rounded-2xl p-6 hover:border-emerald-500/40 hover:bg-slate-900 transition-all"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500/20 to-teal-600/20 border border-emerald-500/30 flex items-center justify-center">
                <IconBuilding className="w-6 h-6 text-emerald-400" />
              </div>
              <span className="text-xs font-semibold text-emerald-400 bg-emerald-500/10 border border-emerald-500/30 rounded-full px-3 py-1">
                {c.rooms} otaq · {c.capacity} yer
              </span>
            </div>
            <h3 className="text-white font-bold text-base mt-4">{c.name}</h3>
            <ul className="mt-3 space-y-2 text-sm text-gray-400">
              <li className="flex items-start gap-2.5">
                <IconLocation className="w-4 h-4 text-gray-500 shrink-0 mt-0.5" />
                {c.address}
              </li>
              <li className="flex items-center gap-2.5">
                <IconPhone className="w-4 h-4 text-gray-500 shrink-0" />
                {c.phone}
              </li>
            </ul>
            <div className="mt-4 pt-4 border-t border-white/5 flex items-center gap-2 text-xs text-gray-500">
              <span className="inline-flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                İmtahanlar burada keçirilir
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
