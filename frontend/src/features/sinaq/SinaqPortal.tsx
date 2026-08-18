import { useEffect, useState } from 'react';
import { type ExamTab, type RegistrationData } from './types';
import { INITIAL_REGISTERED_TICKETS, EXAMS, EXAM_CENTERS } from './data/mockExams';
import { Header } from './components/Header';
import { Footer } from './components/Footer';
import { ExamRegistrationWizard } from './components/ExamRegistrationWizard';
import { TicketPassView } from './components/TicketPassView';
import { TicketLookupModal } from './components/TicketLookupModal';
import { ExamScheduleView } from './components/ExamScheduleView';
import { ExamCentersView } from './components/ExamCentersView';
import { ExamRulesView } from './components/ExamRulesView';
import { IconBuilding, IconCalendar, IconUser } from './components/icons';

const STORAGE_KEY = 'sinaq_registrations';

function loadRegistrations(): RegistrationData[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed)) return parsed;
    }
  } catch {
    /* corrupted storage — fall back to initial */
  }
  return INITIAL_REGISTERED_TICKETS;
}

function Hero() {
  const stats = [
    { icon: <IconCalendar className="w-5 h-5" />, value: `${EXAMS.length}`, label: 'İmtahan' },
    { icon: <IconUser className="w-5 h-5" />, value: `${EXAMS.reduce((s, e) => s + e.registeredCount, 0)}+`, label: 'İştirakçı' },
    { icon: <IconBuilding className="w-5 h-5" />, value: `${EXAM_CENTERS.length}`, label: 'Mərkəz' },
  ];

  return (
    <div className="relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-emerald-500/[0.07] via-transparent to-transparent" />
      <div className="absolute -top-40 -right-40 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl" />
      <div className="absolute -top-40 -left-40 w-96 h-96 bg-teal-500/10 rounded-full blur-3xl" />

      <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pt-14 pb-16 text-center">
        <span className="inline-flex items-center gap-2 px-4 py-1.5 bg-emerald-500/10 border border-emerald-500/30 rounded-full text-emerald-400 text-xs font-semibold uppercase tracking-widest">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          2026 · Payız dövrü
        </span>
        <h1 className="mt-6 text-3xl sm:text-5xl font-bold text-white leading-tight">
          Sınaq imtahanlarına
          <span className="block bg-gradient-to-r from-emerald-400 to-teal-300 bg-clip-text text-transparent">
            onlayn qeydiyyat
          </span>
        </h1>
        <p className="mt-4 text-gray-400 text-sm sm:text-base max-w-2xl mx-auto">
          Dövlət imtahan mərkəzinin qaydalarına uyğun keçirilən sınaq imtahanlarına bir neçə addımda
          qeydiyyatdan keçin və buraxılış vərəqənizi dərhal əldə edin.
        </p>

        <div className="mt-10 grid grid-cols-3 gap-3 sm:gap-4 max-w-lg mx-auto">
          {stats.map((s, i) => (
            <div
              key={i}
              className="bg-slate-900/70 backdrop-blur border border-white/10 rounded-2xl px-4 py-5 hover:border-emerald-500/40 transition-all"
            >
              <div className="w-10 h-10 mx-auto rounded-xl bg-emerald-500/15 flex items-center justify-center text-emerald-400">
                {s.icon}
              </div>
              <p className="mt-3 text-2xl font-bold text-white">{s.value}</p>
              <p className="text-gray-500 text-xs">{s.label}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export function SinaqPortal() {
  const [activeTab, setActiveTab] = useState<ExamTab>('register');
  const [registrations, setRegistrations] = useState<RegistrationData[]>(loadRegistrations);
  const [currentTicket, setCurrentTicket] = useState<RegistrationData | null>(null);
  const [lookupOpen, setLookupOpen] = useState(false);
  const [preselectedExamId, setPreselectedExamId] = useState<string | null>(null);
  const [wizardNonce, setWizardNonce] = useState(0);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(registrations));
    } catch {
      /* storage full or unavailable */
    }
  }, [registrations]);

  const handleNewRegistration = () => {
    setPreselectedExamId(null);
    setWizardNonce((n) => n + 1);
    setActiveTab('register');
    setCurrentTicket(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleRegisterForExam = (examId: string) => {
    setPreselectedExamId(examId);
    setWizardNonce((n) => n + 1);
    setActiveTab('register');
    setCurrentTicket(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSuccess = (reg: RegistrationData) => {
    setRegistrations((r) => [reg, ...r]);
    setCurrentTicket(reg);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSelectTicket = (t: RegistrationData) => {
    setCurrentTicket(t);
    setLookupOpen(false);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const setTab = (tab: ExamTab) => {
    setActiveTab(tab);
    setCurrentTicket(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 selection:bg-emerald-500 selection:text-white">
      <Header
        activeTab={activeTab}
        setActiveTab={setTab}
        onOpenLookup={() => setLookupOpen(true)}
        onNewRegistration={handleNewRegistration}
      />

      <main>
        {currentTicket ? (
          <TicketPassView
            ticket={currentTicket}
            onNewRegistration={handleNewRegistration}
            onDone={() => setCurrentTicket(null)}
          />
        ) : activeTab === 'register' ? (
          <>
            <Hero />
            <ExamRegistrationWizard
              key={wizardNonce}
              onSuccess={handleSuccess}
              onCancel={handleNewRegistration}
              preselectedExamId={preselectedExamId}
            />
          </>
        ) : activeTab === 'schedule' ? (
          <ExamScheduleView onRegisterForExam={handleRegisterForExam} />
        ) : activeTab === 'centers' ? (
          <ExamCentersView />
        ) : (
          <ExamRulesView />
        )}
      </main>

      <Footer setActiveTab={setTab} onOpenLookup={() => setLookupOpen(true)} />

      <TicketLookupModal
        open={lookupOpen}
        onClose={() => setLookupOpen(false)}
        registrations={registrations}
        onSelect={handleSelectTicket}
      />
    </div>
  );
}
