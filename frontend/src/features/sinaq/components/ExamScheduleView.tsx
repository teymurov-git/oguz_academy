import { useMemo } from 'react';
import { type Exam } from '../types';
import { EXAMS, formatDate } from '../data/mockExams';
import { IconBuilding, IconCheck, IconClock, IconLocation } from './icons';

interface ExamScheduleViewProps {
  onRegisterForExam: (examId: string) => void;
}

export function ExamScheduleView({ onRegisterForExam }: ExamScheduleViewProps) {
  const sorted = useMemo(
    () => [...EXAMS].sort((a, b) => a.date.localeCompare(b.date) || a.time.localeCompare(b.time)),
    []
  );

  const statusBadge = (e: Exam) => {
    if (e.status === 'full')
      return (
        <span className="inline-flex items-center gap-1 text-xs font-semibold text-gray-400 bg-white/5 border border-white/10 rounded-full px-3 py-1">
          Dolu
        </span>
      );
    if (e.status === 'closed')
      return (
        <span className="inline-flex items-center gap-1 text-xs font-semibold text-red-400 bg-red-500/10 border border-red-500/30 rounded-full px-3 py-1">
          Qeydiyyat bitib
        </span>
      );
    return (
      <span className="inline-flex items-center gap-1 text-xs font-semibold text-emerald-400 bg-emerald-500/10 border border-emerald-500/30 rounded-full px-3 py-1">
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
        Qeydiyyat açıqdır
      </span>
    );
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="text-center mb-10">
        <h2 className="text-2xl sm:text-3xl font-bold text-white">İmtahan Cədvəli</h2>
        <p className="text-gray-500 text-sm mt-2">2026-cı ilin payız dövrü üçün sınaq imtahanları.</p>
      </div>

      <div className="space-y-3">
        {sorted.map((exam) => {
          const left = exam.totalSeats - exam.registeredCount;
          const percent = Math.min(100, Math.round((exam.registeredCount / exam.totalSeats) * 100));
          const open = exam.status === 'open';
          return (
            <div
              key={exam.id}
              className="group flex flex-col lg:flex-row lg:items-center gap-4 lg:gap-6 bg-slate-900/60 border border-white/10 rounded-2xl p-5 hover:border-emerald-500/40 transition-all"
            >
              {/* Date block */}
              <div className="flex items-center gap-4 lg:gap-5 lg:w-40 shrink-0">
                <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-emerald-500/20 to-teal-600/20 border border-emerald-500/30 flex flex-col items-center justify-center shrink-0">
                  <span className="text-lg font-bold text-emerald-400 leading-none">{formatDate(exam.date).split(' ')[0]}</span>
                  <span className="text-[10px] text-gray-400 mt-0.5">{formatDate(exam.date).split(' ').slice(1).join(' ')}</span>
                </div>
                <div className="lg:hidden">
                  <p className="text-white font-semibold text-sm leading-snug">{exam.title}</p>
                  <p className="text-gray-500 text-xs mt-1 flex items-center gap-1.5">
                    <IconClock className="w-3.5 h-3.5" />
                    {exam.time} · {exam.durationMinutes} dəq
                  </p>
                </div>
              </div>

              {/* Info */}
              <div className="flex-1 min-w-0">
                <p className="text-white font-semibold text-sm leading-snug hidden lg:block">{exam.title}</p>
                <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5 mt-1.5 text-xs text-gray-500">
                  <span className="inline-flex items-center gap-1.5">
                    <IconClock className="w-3.5 h-3.5" />
                    {exam.time} · {exam.durationMinutes} dəq
                  </span>
                  <span className="inline-flex items-center gap-1.5">
                    <IconBuilding className="w-3.5 h-3.5" />
                    {exam.center}
                  </span>
                  <span className="inline-flex items-center gap-1.5">
                    <IconLocation className="w-3.5 h-3.5" />
                    {exam.address}
                  </span>
                  <span className="inline-flex items-center gap-1.5 text-white font-semibold">
                    {exam.price} AZN
                  </span>
                </div>
                {/* Capacity bar */}
                <div className="mt-3">
                  <div className="flex items-center justify-between text-[10px] text-gray-500 mb-1">
                    <span>Doldurulma: {percent}%</span>
                    <span>{open ? `${left} yer qalıb` : `${exam.registeredCount}/${exam.totalSeats}`}</span>
                  </div>
                  <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all ${open ? 'bg-gradient-to-r from-emerald-500 to-teal-500' : 'bg-gray-600'}`}
                      style={{ width: `${percent}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* Status + action */}
              <div className="flex items-center justify-between lg:flex-col lg:items-end lg:justify-center gap-3 shrink-0">
                {statusBadge(exam)}
                {open ? (
                  <button
                    onClick={() => onRegisterForExam(exam.id)}
                    className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-emerald-500 to-teal-600 text-white text-sm font-semibold rounded-xl shadow-lg shadow-emerald-500/20 hover:shadow-emerald-500/40 transition-all cursor-pointer"
                  >
                    <IconCheck className="w-4 h-4" />
                    Qeydiyyat
                  </button>
                ) : (
                  <span className="text-xs text-gray-600">Qeydiyyat bağlıdır</span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
