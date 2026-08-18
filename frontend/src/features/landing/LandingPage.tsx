import { useState, useEffect, useRef, useCallback } from 'react';

/* ──────────────────────────────────────────────
   HOOKS
   ────────────────────────────────────────────── */

function useCountUp(end: number, duration = 2000) {
  const [count, setCount] = useState(0);
  const [started, setStarted] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      ([e]) => { if (e.isIntersecting) { setStarted(true); obs.disconnect(); } },
      { threshold: 0.3 }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  useEffect(() => {
    if (!started) return;
    let start = 0;
    const step = (ts: number) => {
      if (!start) start = ts;
      const p = Math.min((ts - start) / duration, 1);
      setCount(Math.floor(p * end));
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, [started, end, duration]);

  return { count, ref };
}

function useScrollReveal() {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      ([e]) => { if (e.isIntersecting) { setVisible(true); obs.disconnect(); } },
      { threshold: 0.15 }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  return { ref, visible };
}

/* ──────────────────────────────────────────────
   HERO
   ────────────────────────────────────────────── */

function HeroSection() {
  const [idx, setIdx] = useState(0);
  const words = ['KODLA!', 'ÖYRƏN!', 'İNKİŞAF ET!'];

  useEffect(() => {
    const t = setInterval(() => setIdx((i) => (i + 1) % words.length), 2500);
    return () => clearInterval(t);
  }, []);

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Video BG */}
      <video
        autoPlay muted loop playsInline
        className="absolute inset-0 w-full h-full object-cover"
        poster="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='1920' height='1080'%3E%3Crect fill='%230a0a1a' width='1920' height='1080'/%3E%3C/svg%3E"
      >
        <source src="https://cdn.coverr.co/videos/coverr-a-man-working-on-a-laptop-5989/1080p.mp4" type="video/mp4" />
      </video>
      {/* Overlays */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a1a]/80 via-[#0a0a1a]/60 to-[#0a0a1a]" />
      <div className="absolute inset-0" style={{ background: 'radial-gradient(ellipse at 30% 50%, rgba(99,102,241,0.08) 0%, transparent 60%)' }} />

      {/* Floating particles */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className="absolute rounded-full bg-indigo-500/10"
            style={{
              width: `${Math.random() * 4 + 2}px`,
              height: `${Math.random() * 4 + 2}px`,
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animation: `float ${3 + Math.random() * 4}s ease-in-out infinite`,
              animationDelay: `${Math.random() * 3}s`,
            }}
          />
        ))}
      </div>

      <div className="relative z-10 text-center px-4 max-w-5xl mx-auto">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 backdrop-blur-sm mb-8 animate-fade-in">
          <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          <span className="text-sm text-gray-300 font-medium">2026 Qəbul artıq açıqdır</span>
        </div>

        {/* Animated Heading */}
        <h1 className="text-5xl sm:text-7xl lg:text-8xl font-black text-white mb-6 leading-tight">
          <span className="block">Oğuz Tədris</span>
          <span className="block mt-2">
            Mərkəzi{' '}
            <span className="bg-gradient-to-r from-indigo-400 via-violet-400 to-purple-400 bg-clip-text text-transparent">
              {words[idx]}
            </span>
          </span>
        </h1>

        <p className="text-lg sm:text-xl text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed">
          Gələcəyinizi bizimlə qurun. Proqramlaşdırma, robototexnika və rəqəmsal savadlılıq üzrə peşəkar təhsil.
        </p>

        {/* CTAs */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <a
            href="#about"
            className="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-indigo-500 to-violet-600 text-white font-bold rounded-2xl hover:shadow-2xl hover:shadow-indigo-500/25 transition-all hover:-translate-y-1 text-base"
          >
            Dərslərə Qoşul
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </a>
          <a
            href="#about"
            className="inline-flex items-center gap-2 px-8 py-4 bg-white/5 border border-white/10 text-white font-semibold rounded-2xl hover:bg-white/10 transition-all backdrop-blur-sm text-base"
          >
            Kəşf et
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </a>
        </div>

        {/* Scroll indicator */}
        <div className="mt-16 animate-bounce">
          <svg className="w-6 h-6 text-gray-500 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </div>
      </div>
    </section>
  );
}

/* ──────────────────────────────────────────────
   ABOUT
   ────────────────────────────────────────────── */

function AboutSection() {
  const { ref, visible } = useScrollReveal();

  return (
    <section id="about" className="relative py-24 lg:py-32">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div ref={ref} className={`grid lg:grid-cols-2 gap-16 items-center transition-all duration-700 ${visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
          {/* Left */}
          <div>
            <span className="inline-block text-indigo-400 text-sm font-semibold tracking-wider uppercase mb-4">Haqqımızda</span>
            <h2 className="text-4xl lg:text-5xl font-black text-white mb-6 leading-tight">
              Biz kimik?
            </h2>
            <p className="text-gray-400 text-lg leading-relaxed mb-6">
              Oğuz Tədris Mərkəzi — Azərbaycanda informatika, proqramlaşdırma və robototexnika sahəsində fəaliyyət göstərən aparıcı tədris müəssisəsidir.
            </p>
            <p className="text-gray-500 leading-relaxed mb-8">
              Müasir tədris metodları, təcrübəli müəllimlər və peşəkar proqramla tələbələrimizi gələcəyin texnologiya peşələrinə hazırlayırıq. Hər bir tələbəyə fərdi yanaşma ilə onların potensialını tam açmağa çalışırıq.
            </p>
            <div className="flex flex-wrap gap-4">
              <a href="#contact" className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-indigo-500 to-violet-600 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-indigo-500/25 transition-all hover:-translate-y-0.5">
                Əlaqə saxla
              </a>
              <a href="#teachers" className="inline-flex items-center gap-2 px-6 py-3 bg-white/5 border border-white/10 text-white font-semibold rounded-xl hover:bg-white/10 transition-all">
                Fəaliyyətlərimiz
              </a>
            </div>
          </div>

          {/* Right — Visual */}
          <div className="relative">
            <div className="relative rounded-3xl overflow-hidden bg-gradient-to-br from-indigo-500/20 to-violet-500/20 border border-white/5 p-8">
              <div className="grid grid-cols-2 gap-4">
                {[
                  { icon: '💻', label: 'Proqramlaşdırma', color: 'from-blue-500/20 to-cyan-500/20' },
                  { icon: '🤖', label: 'Robototexnika', color: 'from-purple-500/20 to-pink-500/20' },
                  { icon: '📐', label: 'Veb Dizayn', color: 'from-amber-500/20 to-orange-500/20' },
                  { icon: '📊', label: 'Rəqəmsal Savadlılıq', color: 'from-green-500/20 to-emerald-500/20' },
                ].map((item) => (
                  <div key={item.label} className={`p-5 rounded-2xl bg-gradient-to-br ${item.color} border border-white/5 text-center hover:scale-105 transition-transform`}>
                    <span className="text-3xl block mb-2">{item.icon}</span>
                    <span className="text-sm text-gray-300 font-medium">{item.label}</span>
                  </div>
                ))}
              </div>
              {/* Decorative */}
              <div className="absolute -top-4 -right-4 w-24 h-24 bg-indigo-500/10 rounded-full blur-2xl" />
              <div className="absolute -bottom-4 -left-4 w-32 h-32 bg-violet-500/10 rounded-full blur-2xl" />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ──────────────────────────────────────────────
   STATS
   ────────────────────────────────────────────── */

function StatsSection() {
  const s1 = useCountUp(25, 2000);
  const s2 = useCountUp(115, 2000);
  const s3 = useCountUp(253, 2000);
  const s4 = useCountUp(15, 2000);

  const stats = [
    { ref: s1.ref, val: s1.count, suffix: '+', label: '100% Nəticə', sub: 'Tam mükəmməl bal alan tələbələr', color: 'from-indigo-500 to-violet-600' },
    { ref: s2.ref, val: s2.count, suffix: '+', label: '90%+ Nəticə', sub: 'Yüksək bal qazanan tələbələr', color: 'from-emerald-500 to-teal-500' },
    { ref: s3.ref, val: s3.count, suffix: '+', label: '80%+ Nəticə', sub: 'Güclü nəticə göstərən tələbələr', color: 'from-amber-500 to-orange-500' },
    { ref: s4.ref, val: s4.count, suffix: '+', label: 'İl Təcrübə', sub: 'Təhsil sahəsində təcrübə', color: 'from-blue-500 to-cyan-500' },
  ];

  return (
    <section id="achievements" className="relative py-24 lg:py-32">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <span className="inline-block text-indigo-400 text-sm font-semibold tracking-wider uppercase mb-4">Statistika</span>
          <h2 className="text-4xl lg:text-5xl font-black text-white">
            Uğurlu <span className="bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">Nəticələrimiz</span>
          </h2>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((s, i) => (
            <div
              key={i}
              ref={s.ref}
              className="relative p-6 rounded-2xl bg-white/[0.03] border border-white/5 text-center group hover:border-indigo-500/30 transition-all"
            >
              <div className={`w-12 h-12 mx-auto mb-4 rounded-xl bg-gradient-to-br ${s.color} flex items-center justify-center shadow-lg`}>
                <span className="text-white text-lg font-bold">{s.val}</span>
              </div>
              <div className="text-3xl lg:text-4xl font-black text-white mb-1">
                {s.val}{s.suffix}
              </div>
              <div className="text-sm font-semibold text-indigo-400 mb-1">{s.label}</div>
              <div className="text-xs text-gray-500">{s.sub}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ──────────────────────────────────────────────
   TEACHERS
   ────────────────────────────────────────────── */

const teachers = [
  { name: 'Əli Məmmədov', subject: 'Proqramlaşdırma', exp: '8 il', initials: 'ƏM', gradient: 'from-blue-500 to-indigo-600' },
  { name: 'Leyla Hüseynova', subject: 'Veb Dizayn', exp: '6 il', initials: 'LH', gradient: 'from-purple-500 to-pink-600' },
  { name: 'Kərim Əliyev', subject: 'Robototexnika', exp: '10 il', initials: 'KƏ', gradient: 'from-amber-500 to-orange-600' },
  { name: 'Nigarə Babayeva', subject: 'Rəqəmsal Savadlılıq', exp: '5 il', initials: 'NB', gradient: 'from-emerald-500 to-teal-600' },
];

function TeachersSection() {
  const { ref, visible } = useScrollReveal();
  const [active, setActive] = useState(0);

  return (
    <section id="teachers" className="relative py-24 lg:py-32">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div ref={ref} className={`text-center mb-16 transition-all duration-700 ${visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
          <span className="inline-block text-indigo-400 text-sm font-semibold tracking-wider uppercase mb-4">Komanda</span>
          <h2 className="text-4xl lg:text-5xl font-black text-white mb-4">
            Müəllimlərimiz
          </h2>
          <p className="text-gray-500 text-lg max-w-2xl mx-auto">Təcrübəli və peşəkar müəllim heyəti</p>
        </div>

        {/* Carousel */}
        <div className="relative max-w-4xl mx-auto">
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {teachers.map((t, i) => (
              <div
                key={i}
                className={`group relative p-6 rounded-2xl bg-white/[0.03] border transition-all duration-300 cursor-pointer text-center ${
                  active === i ? 'border-indigo-500/40 bg-indigo-500/5' : 'border-white/5 hover:border-white/10'
                }`}
                onMouseEnter={() => setActive(i)}
              >
                <div className={`w-20 h-20 mx-auto mb-4 rounded-2xl bg-gradient-to-br ${t.gradient} flex items-center justify-center text-white text-xl font-bold shadow-lg group-hover:scale-105 transition-transform`}>
                  {t.initials}
                </div>
                <h4 className="text-white font-bold mb-1">{t.name}</h4>
                <p className="text-indigo-400 text-sm font-medium mb-1">{t.subject}</p>
                <p className="text-gray-500 text-xs">Təcrübə: {t.exp}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

/* ──────────────────────────────────────────────
   AI CHATBOT
   ────────────────────────────────────────────── */

function AISection() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<{ role: string; text: string }[]>([
    { role: 'ai', text: 'Salam! Mən Oğuz TM-nin AI köməkçisiyəm. Sizə necə kömək edə bilərəm? 🤖' },
  ]);
  const [input, setInput] = useState('');
  const [typing, setTyping] = useState(false);
  const boxRef = useRef<HTMLDivElement>(null);

  const aiResponses: Record<string, string> = {
    'salam': 'Salam! Xoş gəlmisiniz! Oğuz Tədris Mərkəzi haqqında suallarınızı verə bilərsiniz.',
    'kurs': 'Bizim əsas kurslarımız: Proqramlaşdırma (Python, JavaScript), Veb Dizayn, Robototexnika və Rəqəmsal Savadlılıq. Hansı maraqlandırır?',
    'qiymət': 'Kurs qiymətləri barədə ətraflı məlumat üçün bizimlə əlaqə saxlayın: +994 XX XXX XX XX',
    'qeydiyyat': 'Qeydiyyatdan keçmək üçün "Kabinet" bölməsinə daxil ola və ya birbaşa bizimlə əlaqə saxlaya bilərsiniz.',
    'saat': 'Dərslərimiz həftədə 3 dəfə, axşam saat 18:00-20:00 arası keçirilir.',
    'ünvan': 'Bizim ünvanımız: Bakı şəhəri. Ətraflı məlumat üçün əlaqə bölməsinə baxın.',
  };

  const getAIResponse = useCallback((msg: string) => {
    const lower = msg.toLowerCase();
    for (const [key, val] of Object.entries(aiResponses)) {
      if (lower.includes(key)) return val;
    }
    return 'Bu sualı dəqiq başa düşmədim. Zəhmət olmasa daha ətraflı yazın və ya birbaşa bizimlə əlaqə saxlayın: +994 XX XXX XX XX';
  }, []);

  const send = () => {
    if (!input.trim()) return;
    const userMsg = input.trim();
    setMessages((m) => [...m, { role: 'user', text: userMsg }]);
    setInput('');
    setTyping(true);
    setTimeout(() => {
      setMessages((m) => [...m, { role: 'ai', text: getAIResponse(userMsg) }]);
      setTyping(false);
    }, 800);
  };

  useEffect(() => {
    if (boxRef.current) boxRef.current.scrollTop = boxRef.current.scrollHeight;
  }, [messages]);

  return (
    <>
      {/* FAB */}
      <button
        onClick={() => setOpen(!open)}
        className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-600 text-white shadow-2xl shadow-indigo-500/30 flex items-center justify-center hover:shadow-indigo-500/50 hover:scale-105 transition-all"
      >
        {open ? (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
        ) : (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" /></svg>
        )}
      </button>

      {/* Chat Window */}
      {open && (
        <div className="fixed bottom-24 right-6 z-50 w-[380px] max-w-[calc(100vw-3rem)] bg-[#0d0d24] border border-white/10 rounded-2xl shadow-2xl shadow-black/40 overflow-hidden flex flex-col" style={{ height: '480px' }}>
          {/* Header */}
          <div className="px-5 py-4 bg-gradient-to-r from-indigo-500 to-violet-600 flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" /></svg>
            </div>
            <div>
              <h4 className="text-white font-bold text-sm">AI Köməkçi</h4>
              <p className="text-white/60 text-xs">Həmişə onlayn</p>
            </div>
          </div>

          {/* Messages */}
          <div ref={boxRef} className="flex-1 overflow-y-auto p-4 space-y-3">
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] px-4 py-2.5 rounded-2xl text-sm leading-relaxed ${
                  m.role === 'user'
                    ? 'bg-indigo-500 text-white rounded-br-md'
                    : 'bg-white/5 text-gray-300 border border-white/5 rounded-bl-md'
                }`}>
                  {m.text}
                </div>
              </div>
            ))}
            {typing && (
              <div className="flex justify-start">
                <div className="bg-white/5 border border-white/5 rounded-2xl rounded-bl-md px-4 py-3 flex gap-1">
                  <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            )}
          </div>

          {/* Quick Replies */}
          <div className="px-4 pb-2 flex gap-2 flex-wrap">
            {['Kurs', 'Qiymət', 'Saat', 'Qeydiyyat'].map((q) => (
              <button
                key={q}
                onClick={() => { setInput(q); setTimeout(send, 50); }}
                className="px-3 py-1 text-xs font-medium text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 rounded-full hover:bg-indigo-500/20 transition-colors"
              >
                {q}
              </button>
            ))}
          </div>

          {/* Input */}
          <div className="px-4 pb-4">
            <div className="flex gap-2">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && send()}
                placeholder="Sualınızı yazın..."
                className="flex-1 px-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500/50 transition-colors"
              />
              <button
                onClick={send}
                className="px-4 py-2.5 bg-indigo-500 rounded-xl text-white hover:bg-indigo-600 transition-colors"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" /></svg>
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

/* ──────────────────────────────────────────────
   CONTACT
   ────────────────────────────────────────────── */

function ContactSection() {
  const { ref, visible } = useScrollReveal();
  const [formState, setFormState] = useState({ name: '', email: '', phone: '', message: '' });
  const [sent, setSent] = useState(false);
  const [error, setError] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(false);
    try {
      const res = await fetch('/api/v1/contact/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          first_name: formState.name,
          last_name: '',
          email: formState.email,
          phone: formState.phone,
          message: formState.message,
        }),
      });
      if (!res.ok) throw new Error('send failed');
      setSent(true);
      setTimeout(() => setSent(false), 3000);
      setFormState({ name: '', email: '', phone: '', message: '' });
    } catch {
      setError(true);
      setTimeout(() => setError(false), 3000);
    }
  };

  return (
    <section id="contact" className="relative py-24 lg:py-32">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div ref={ref} className={`transition-all duration-700 ${visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
          <div className="text-center mb-16">
            <span className="inline-block text-indigo-400 text-sm font-semibold tracking-wider uppercase mb-4">Əlaqə</span>
            <h2 className="text-4xl lg:text-5xl font-black text-white mb-4">
              Bizimlə <span className="bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">Əlaqə</span> Saxlayın
            </h2>
          </div>

          <div className="grid lg:grid-cols-2 gap-12">
            {/* Form */}
            <form onSubmit={handleSubmit} className="p-8 rounded-2xl bg-white/[0.03] border border-white/5">
              <div className="space-y-5">
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">Adınız</label>
                  <input
                    type="text"
                    value={formState.name}
                    onChange={(e) => setFormState({ ...formState, name: e.target.value })}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white text-sm placeholder-gray-500 focus:outline-none focus:border-indigo-500/50 transition-colors"
                    placeholder="Adınızı daxil edin"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">Email</label>
                  <input
                    type="email"
                    value={formState.email}
                    onChange={(e) => setFormState({ ...formState, email: e.target.value })}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white text-sm placeholder-gray-500 focus:outline-none focus:border-indigo-500/50 transition-colors"
                    placeholder="Email ünvanınız"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">Telefon</label>
                  <input
                    type="tel"
                    value={formState.phone}
                    onChange={(e) => setFormState({ ...formState, phone: e.target.value })}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white text-sm placeholder-gray-500 focus:outline-none focus:border-indigo-500/50 transition-colors"
                    placeholder="+994 XX XXX XX XX"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">Mesaj</label>
                  <textarea
                    value={formState.message}
                    onChange={(e) => setFormState({ ...formState, message: e.target.value })}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white text-sm placeholder-gray-500 focus:outline-none focus:border-indigo-500/50 transition-colors resize-none"
                    rows={4}
                    placeholder="Mesajınızı yazın..."
                  />
                </div>
                <button
                  type="submit"
                  className="w-full py-3.5 bg-gradient-to-r from-indigo-500 to-violet-600 text-white font-bold rounded-xl hover:shadow-lg hover:shadow-indigo-500/25 transition-all hover:-translate-y-0.5"
                >
                  {sent ? '✓ Göndərildi!' : 'Göndər'}
                </button>
                {error && (
                  <p className="text-center text-sm text-red-400">Mesaj göndərilə bilmədi, bir daha yoxlayın.</p>
                )}
              </div>
            </form>

            {/* Info */}
            <div className="space-y-6">
              {[
                { icon: '📞', title: 'Telefon', value: '+994 XX XXX XX XX', color: 'from-blue-500/20 to-cyan-500/20' },
                { icon: '📍', title: 'Ünvan', value: 'Bakı, Azərbaycan', color: 'from-purple-500/20 to-pink-500/20' },
                { icon: '✉️', title: 'Email', value: 'info@oguztm.az', color: 'from-amber-500/20 to-orange-500/20' },
                { icon: '🕐', title: 'İş saatı', value: 'B.e — Cümə: 09:00 — 18:00', color: 'from-green-500/20 to-emerald-500/20' },
              ].map((item) => (
                <div key={item.title} className="flex items-center gap-4 p-5 rounded-2xl bg-white/[0.03] border border-white/5 hover:border-white/10 transition-all">
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${item.color} flex items-center justify-center text-xl shrink-0`}>
                    {item.icon}
                  </div>
                  <div>
                    <h4 className="text-white font-semibold text-sm">{item.title}</h4>
                    <p className="text-gray-500 text-sm">{item.value}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ──────────────────────────────────────────────
   MAIN LANDING PAGE
   ────────────────────────────────────────────── */

export default function LandingPage() {
  return (
    <>
      <HeroSection />
      <AboutSection />
      <StatsSection />
      <TeachersSection />
      <ContactSection />
      <AISection />
    </>
  );
}
