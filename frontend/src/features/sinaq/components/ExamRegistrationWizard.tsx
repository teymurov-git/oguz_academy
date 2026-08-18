import { useMemo, useState } from 'react';
import { type Exam, type RegistrationData } from '../types';
import { EXAMS, generateTicketNumber, formatDate } from '../data/mockExams';
import {
  IconArrowLeft,
  IconArrowRight,
  IconBuilding,
  IconCalendar,
  IconCheck,
  IconClock,
  IconTag,
  IconUser,
} from './icons';

interface ExamRegistrationWizardProps {
  onSuccess: (registration: RegistrationData) => void;
  onCancel: () => void;
  preselectedExamId?: string | null;
}

type Step = 1 | 2 | 3;

const EMPTY_FORM = { fullName: '', email: '', phone: '' };

const inputCls =
  'w-full bg-slate-900/80 border border-white/10 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-gray-500 focus:outline-none focus:border-emerald-500/60 focus:ring-2 focus:ring-emerald-500/20 transition-all';

export function ExamRegistrationWizard({ onSuccess, onCancel, preselectedExamId }: ExamRegistrationWizardProps) {
  const [step, setStep] = useState<Step>(1);
  const [examId, setExamId] = useState<string | null>(preselectedExamId ?? null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const availableExams = useMemo(() => EXAMS.filter((e) => e.status === 'open'), []);
  const selectedExam = useMemo(() => EXAMS.find((e) => e.id === examId) ?? null, [examId]);

  const update = (key: keyof typeof EMPTY_FORM, value: string) => {
    setForm((f) => ({ ...f, [key]: value }));
    setErrors((e) => ({ ...e, [key]: '' }));
  };

  const validateStep2 = () => {
    const next: Record<string, string> = {};
    if (form.fullName.trim().length < 5) next.fullName = 'Ad və soyadınızı daxil edin.';
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) next.email = 'Düzgün e-poçt ünvanı daxil edin.';
    if (!/^\+?\d[\d\s-]{8,}$/.test(form.phone.trim())) next.phone = 'Düzgün telefon nömrəsi daxil edin.';
    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const confirm = () => {
    if (!selectedExam) return;
    const reg: RegistrationData = {
      id: `TICKET-${Math.random().toString(36).slice(2, 6).toUpperCase()}${Math.floor(Math.random() * 99)}`,
      ticketNumber: generateTicketNumber(),
      exam: selectedExam,
      fullName: form.fullName.trim(),
      email: form.email.trim(),
      phone: form.phone.trim(),
      registeredAt: new Date().toISOString(),
    };
    onSuccess(reg);
  };

  const seatsLeft = (e: Exam) => e.totalSeats - e.registeredCount;

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Progress */}
      <div className="flex items-center justify-center mb-10">
        {[
          { n: 1, label: 'İmtahanı seçin' },
          { n: 2, label: 'Məlumatlar' },
          { n: 3, label: 'Təsdiqləyin' },
        ].map((s, i) => (
          <div key={s.n} className="flex items-center">
            <div className="flex flex-col items-center gap-2">
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold border-2 transition-all ${
                  step > s.n
                    ? 'bg-emerald-500 border-emerald-500 text-white'
                    : step === s.n
                      ? 'bg-emerald-500/15 border-emerald-500 text-emerald-400'
                      : 'bg-slate-900 border-white/10 text-gray-500'
                }`}
              >
                {step > s.n ? <IconCheck className="w-5 h-5" /> : s.n}
              </div>
              <span
                className={`text-xs font-medium ${step >= s.n ? 'text-slate-200' : 'text-gray-500'}`}
              >
                {s.label}
              </span>
            </div>
            {i < 2 && (
              <div className={`w-16 sm:w-28 h-0.5 mx-2 mb-6 rounded ${step > s.n ? 'bg-emerald-500' : 'bg-white/10'}`} />
            )}
          </div>
        ))}
      </div>

      {/* Step 1: choose exam */}
      {step === 1 && (
        <section>
          <div className="text-center mb-8">
            <h2 className="text-2xl sm:text-3xl font-bold text-white">İmtahan seçin</h2>
            <p className="text-gray-500 text-sm mt-2">Qeydiyyatı açıq olan sınaq imtahanlarından birini seçin.</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {availableExams.map((exam) => {
              const selected = exam.id === examId;
              const left = seatsLeft(exam);
              return (
                <button
                  key={exam.id}
                  onClick={() => setExamId(exam.id)}
                  className={`relative text-left rounded-2xl p-5 border transition-all cursor-pointer ${
                    selected
                      ? 'bg-emerald-500/10 border-emerald-500/60 ring-2 ring-emerald-500/20'
                      : 'bg-slate-900/60 border-white/10 hover:border-emerald-500/40 hover:bg-slate-900'
                  }`}
                >
                  {selected && (
                    <span className="absolute top-4 right-4 w-6 h-6 rounded-full bg-emerald-500 flex items-center justify-center">
                      <IconCheck className="w-4 h-4 text-white" />
                    </span>
                  )}
                  <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-400 bg-emerald-500/10 border border-emerald-500/30 rounded-full px-3 py-1">
                    <IconTag className="w-3.5 h-3.5" />
                    {exam.subject}
                  </span>
                  <h3 className="text-white font-semibold text-base mt-3 leading-snug">{exam.title}</h3>
                  <div className="mt-4 space-y-1.5 text-sm text-gray-400">
                    <p className="flex items-center gap-2">
                      <IconCalendar className="w-4 h-4 text-gray-500 shrink-0" />
                      {formatDate(exam.date)}
                    </p>
                    <p className="flex items-center gap-2">
                      <IconClock className="w-4 h-4 text-gray-500 shrink-0" />
                      {exam.time} · {exam.durationMinutes} dəq
                    </p>
                    <p className="flex items-center gap-2">
                      <IconBuilding className="w-4 h-4 text-gray-500 shrink-0" />
                      {exam.center}
                    </p>
                  </div>
                  <div className="mt-4 flex items-center justify-between border-t border-white/5 pt-4">
                    <span className="text-sm font-bold text-white">{exam.price} AZN</span>
                    <span
                      className={`text-xs font-medium rounded-full px-2.5 py-1 ${
                        left <= 15
                          ? 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
                          : 'bg-white/5 text-gray-400 border border-white/10'
                      }`}
                    >
                      {left} yer qalıb
                    </span>
                  </div>
                </button>
              );
            })}
          </div>
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 mt-8">
            <button
              onClick={onCancel}
              className="inline-flex items-center gap-2 px-5 py-3 text-sm font-semibold text-gray-400 hover:text-white bg-white/5 hover:bg-white/10 rounded-xl transition-all cursor-pointer"
            >
              <IconArrowLeft className="w-4 h-4" />
              Geri
            </button>
            <button
              onClick={() => examId && setStep(2)}
              disabled={!examId}
              className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-emerald-500 to-teal-600 text-white text-sm font-semibold rounded-xl shadow-lg shadow-emerald-500/25 hover:shadow-emerald-500/40 transition-all disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
            >
              Davam et
              <IconArrowRight className="w-4 h-4" />
            </button>
          </div>
        </section>
      )}

      {/* Step 2: personal info */}
      {step === 2 && selectedExam && (
        <section className="max-w-2xl mx-auto">
          <div className="text-center mb-8">
            <h2 className="text-2xl sm:text-3xl font-bold text-white">Şəxsi məlumatlar</h2>
            <p className="text-gray-500 text-sm mt-2">Buraxılış vərəqəsi bu məlumatlarla hazırlanacaq.</p>
          </div>
          <div className="bg-slate-900/60 border border-white/10 rounded-2xl p-6 sm:p-8">
            <div className="flex items-center gap-3 mb-6 p-4 bg-white/5 border border-white/10 rounded-xl">
              <div className="w-10 h-10 rounded-lg bg-emerald-500/15 flex items-center justify-center shrink-0">
                <IconTag className="w-5 h-5 text-emerald-400" />
              </div>
              <div>
                <p className="text-white font-semibold text-sm">{selectedExam.title}</p>
                <p className="text-gray-500 text-xs">{formatDate(selectedExam.date)} · {selectedExam.time} · {selectedExam.center}</p>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1.5">Ad və soyad</label>
                <div className="relative">
                  <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-500">
                    <IconUser className="w-4 h-4" />
                  </span>
                  <input
                    type="text"
                    value={form.fullName}
                    onChange={(e) => update('fullName', e.target.value)}
                    placeholder="Məsələn: Ağasəf Zeynalov"
                    className={`${inputCls} ${form.fullName ? 'pl-11' : 'pl-11'}`}
                  />
                </div>
                {errors.fullName && <p className="text-red-400 text-xs mt-1">{errors.fullName}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1.5">E-poçt</label>
                <div className="relative">
                  <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-500">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                  </span>
                  <input
                    type="email"
                    value={form.email}
                    onChange={(e) => update('email', e.target.value)}
                    placeholder="ad@example.com"
                    className={`${inputCls} pl-11`}
                  />
                </div>
                {errors.email && <p className="text-red-400 text-xs mt-1">{errors.email}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1.5">Telefon</label>
                <div className="relative">
                  <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-500">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                    </svg>
                  </span>
                  <input
                    type="tel"
                    value={form.phone}
                    onChange={(e) => update('phone', e.target.value)}
                    placeholder="+994 XX XXX XX XX"
                    className={`${inputCls} pl-11`}
                  />
                </div>
                {errors.phone && <p className="text-red-400 text-xs mt-1">{errors.phone}</p>}
              </div>
            </div>
          </div>
          <div className="flex items-center justify-between gap-3 mt-6">
            <button
              onClick={() => setStep(1)}
              className="inline-flex items-center gap-2 px-5 py-3 text-sm font-semibold text-gray-400 hover:text-white bg-white/5 hover:bg-white/10 rounded-xl transition-all cursor-pointer"
            >
              <IconArrowLeft className="w-4 h-4" />
              Geri
            </button>
            <button
              onClick={() => validateStep2() && setStep(3)}
              className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-emerald-500 to-teal-600 text-white text-sm font-semibold rounded-xl shadow-lg shadow-emerald-500/25 hover:shadow-emerald-500/40 transition-all cursor-pointer"
            >
              Davam et
              <IconArrowRight className="w-4 h-4" />
            </button>
          </div>
        </section>
      )}

      {/* Step 3: confirm */}
      {step === 3 && selectedExam && (
        <section className="max-w-2xl mx-auto">
          <div className="text-center mb-8">
            <h2 className="text-2xl sm:text-3xl font-bold text-white">Qeydiyyatı təsdiqləyin</h2>
            <p className="text-gray-500 text-sm mt-2">Buraxılış vərəqəniz təsdiqdən dərhal sonra hazır olacaq.</p>
          </div>
          <div className="bg-slate-900/60 border border-white/10 rounded-2xl p-6 sm:p-8">
            <div className="divide-y divide-white/5">
              {[
                { label: 'İmtahan', value: selectedExam.title },
                { label: 'Tarix', value: formatDate(selectedExam.date) },
                { label: 'Saat', value: `${selectedExam.time} · ${selectedExam.durationMinutes} dəq` },
                { label: 'Mərkəz', value: `${selectedExam.center}, ${selectedExam.address}` },
                { label: 'Qiymət', value: `${selectedExam.price} AZN` },
                { label: 'Ad və soyad', value: form.fullName.trim() },
                { label: 'E-poçt', value: form.email.trim() },
                { label: 'Telefon', value: form.phone.trim() },
              ].map((r) => (
                <div key={r.label} className="flex items-start justify-between gap-4 py-3.5">
                  <span className="text-gray-500 text-sm">{r.label}</span>
                  <span className="text-slate-200 text-sm font-medium text-right">{r.value}</span>
                </div>
              ))}
            </div>
            <div className="mt-6 p-4 bg-amber-500/10 border border-amber-500/30 rounded-xl text-xs text-amber-300 leading-relaxed">
              Qeydiyyatı təsdiqləməklə imtahan qaydalarını oxuduğunuzu və qəbul etdiyinizi təsdiq edirsiniz. Ödəniş imtahan günü mərkəzdə həyata keçirilir.
            </div>
          </div>
          <div className="flex items-center justify-between gap-3 mt-6">
            <button
              onClick={() => setStep(2)}
              className="inline-flex items-center gap-2 px-5 py-3 text-sm font-semibold text-gray-400 hover:text-white bg-white/5 hover:bg-white/10 rounded-xl transition-all cursor-pointer"
            >
              <IconArrowLeft className="w-4 h-4" />
              Geri
            </button>
            <button
              onClick={confirm}
              className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-emerald-500 to-teal-600 text-white text-sm font-semibold rounded-xl shadow-lg shadow-emerald-500/25 hover:shadow-emerald-500/40 transition-all cursor-pointer"
            >
              <IconCheck className="w-4 h-4" />
              Təsdiqlə
            </button>
          </div>
        </section>
      )}
    </div>
  );
}
