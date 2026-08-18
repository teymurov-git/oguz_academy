import { useState } from 'react';
import { EXAM_RULES } from '../data/mockExams';
import { IconDoc, IconClose } from './icons';

export function ExamRulesView() {
  const [openRule, setOpenRule] = useState<number | null>(1);

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="text-center mb-10">
        <h2 className="text-2xl sm:text-3xl font-bold text-white">İmtahan Qaydaları</h2>
        <p className="text-gray-500 text-sm mt-2">Rahat keçiş üçün qaydaları diqqətlə oxuyun.</p>
      </div>

      <div className="space-y-3">
        {EXAM_RULES.map((rule) => {
          const open = openRule === rule.id;
          return (
            <div
              key={rule.id}
              className={`bg-slate-900/60 border rounded-2xl overflow-hidden transition-all ${
                open ? 'border-emerald-500/40' : 'border-white/10 hover:border-white/20'
              }`}
            >
              <button
                onClick={() => setOpenRule(open ? null : rule.id)}
                className="w-full flex items-center gap-4 p-5 text-left cursor-pointer"
              >
                <div
                  className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 transition-all ${
                    open ? 'bg-emerald-500 text-white' : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                  }`}
                >
                  <IconDoc className="w-5 h-5" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-white font-semibold text-sm">
                    <span className="text-emerald-400 mr-2">{String(rule.id).padStart(2, '0')}</span>
                    {rule.title}
                  </p>
                </div>
                <span
                  className={`text-gray-500 transition-transform ${open ? 'rotate-45 text-emerald-400' : ''}`}
                >
                  <IconClose className="w-5 h-5" />
                </span>
              </button>
              {open && (
                <div className="px-5 pb-5 pt-0 border-t border-white/5">
                  <p className="text-gray-400 text-sm leading-relaxed mt-4">{rule.text}</p>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
