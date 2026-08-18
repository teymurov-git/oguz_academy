import { useMemo, useState } from 'react';
import { type RegistrationData } from '../types';
import { formatDate } from '../data/mockExams';
import {
  IconBuilding,
  IconCalendar,
  IconCheck,
  IconClock,
  IconCopy,
  IconLocation,
  IconPrint,
  IconTag,
  IconUser,
} from './icons';

interface TicketPassViewProps {
  ticket: RegistrationData;
  onNewRegistration: () => void;
  onDone?: () => void;
}

function QrCode({ seed }: { seed: string }) {
  const cells = useMemo(() => {
    let h = 0;
    for (let i = 0; i < seed.length; i++) h = (h * 31 + seed.charCodeAt(i)) >>> 0;
    const rnd = (i: number) => ((h * (i + 7) + i * 13) % 100) < 42;
    const grid: boolean[][] = [];
    const size = 21;
    for (let r = 0; r < size; r++) {
      const row: boolean[] = [];
      for (let c = 0; c < size; c++) {
        const corner =
          (r < 7 && c < 7) || (r < 7 && c > size - 8) || (r > size - 8 && c < 7);
        row.push(corner ? !((r + c) % 2 === 0 && r > 0 && r < 6 && c > 0 && c < 6) : rnd(r * size + c));
      }
      grid.push(row);
    }
    return grid;
  }, [seed]);

  return (
    <svg viewBox="0 0 21 21" className="w-full h-full">
      {cells.flatMap((row, r) =>
        row.map((on, c) => (on ? <rect key={`${r}-${c}`} x={c} y={r} width={1} height={1} fill="#10b981" /> : null))
      )}
    </svg>
  );
}

export function TicketPassView({ ticket, onNewRegistration, onDone }: TicketPassViewProps) {
  const [copied, setCopied] = useState(false);

  const copyNumber = async () => {
    try {
      await navigator.clipboard.writeText(ticket.ticketNumber);
      setCopied(true);
      setTimeout(() => setCopied(false), 1800);
    } catch {
      /* clipboard unavailable */
    }
  };

  const print = () => window.print();

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="text-center mb-8">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-emerald-500/15 border border-emerald-500/40 rounded-full text-emerald-400 text-sm font-semibold">
          <IconCheck className="w-4 h-4" />
          Qeydiyyatınız təsdiqləndi
        </div>
        <h2 className="text-2xl sm:text-3xl font-bold text-white mt-4">Buraxılış Vərəqəsi</h2>
        <p className="text-gray-500 text-sm mt-2">İmtahan günü bu vərəqə və şəxsiyyəti təsdiq edən sənədlə gəlin.</p>
      </div>

      <div className="bg-slate-900 border border-white/10 rounded-3xl overflow-hidden shadow-2xl shadow-black/40">
        {/* Top strip */}
        <div className="bg-gradient-to-r from-emerald-600 to-teal-600 px-6 sm:px-8 py-4 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-white/20 flex items-center justify-center">
              <span className="text-white font-bold">S</span>
            </div>
            <div>
              <p className="text-white font-bold text-sm leading-none">Oğuz Sınaq Portalı</p>
              <p className="text-emerald-100 text-xs mt-1">Sınaq İmtahanı · Buraxılış Vərəqəsi</p>
            </div>
          </div>
          <span className="inline-flex items-center gap-1.5 text-xs font-bold text-emerald-950 bg-emerald-300/90 rounded-full px-3 py-1.5">
            <IconCheck className="w-3.5 h-3.5" />
            Təsdiqləndi
          </span>
        </div>

        {/* Ticket number */}
        <div className="px-6 sm:px-8 pt-7 pb-2 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Bilet nömrəsi</p>
            <div className="flex items-center gap-3">
              <span className="font-mono text-2xl sm:text-3xl font-bold text-white tracking-wider">{ticket.ticketNumber}</span>
              <button
                onClick={copyNumber}
                className="inline-flex items-center gap-1.5 text-xs font-semibold text-gray-400 hover:text-emerald-400 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg px-2.5 py-1.5 transition-all cursor-pointer"
              >
                {copied ? <IconCheck className="w-3.5 h-3.5 text-emerald-400" /> : <IconCopy className="w-3.5 h-3.5" />}
                {copied ? 'Kopyalandı' : 'Kopyala'}
              </button>
            </div>
          </div>
          {/* QR */}
          <div className="w-24 h-24 rounded-xl bg-white p-2 border border-white/10 shrink-0">
            <QrCode seed={ticket.ticketNumber} />
          </div>
        </div>

        {/* Perforation */}
        <div className="relative mx-6 sm:mx-8 my-4">
          <div className="border-t-2 border-dashed border-white/10" />
          <div className="absolute -left-6 top-1/2 -translate-y-1/2 w-4 h-4 rounded-full bg-slate-950" />
          <div className="absolute -right-6 top-1/2 -translate-y-1/2 w-4 h-4 rounded-full bg-slate-950" />
        </div>

        {/* Details */}
        <div className="px-6 sm:px-8 pb-8">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-5">
            <div>
              <div className="flex items-center gap-2 text-gray-500 text-xs mb-1">
                <IconTag className="w-3.5 h-3.5" />
                İmtahan
              </div>
              <p className="text-slate-200 text-sm font-medium leading-snug">{ticket.exam.title}</p>
            </div>
            <div>
              <div className="flex items-center gap-2 text-gray-500 text-xs mb-1">
                <IconUser className="w-3.5 h-3.5" />
                İştirakçı
              </div>
              <p className="text-slate-200 text-sm font-medium">{ticket.fullName}</p>
            </div>
            <div>
              <div className="flex items-center gap-2 text-gray-500 text-xs mb-1">
                <IconCalendar className="w-3.5 h-3.5" />
                Tarix
              </div>
              <p className="text-slate-200 text-sm font-medium">{formatDate(ticket.exam.date)}</p>
            </div>
            <div>
              <div className="flex items-center gap-2 text-gray-500 text-xs mb-1">
                <IconClock className="w-3.5 h-3.5" />
                Saat
              </div>
              <p className="text-slate-200 text-sm font-medium">
                {ticket.exam.time} · müddət: {ticket.exam.durationMinutes} dəq
              </p>
            </div>
            <div>
              <div className="flex items-center gap-2 text-gray-500 text-xs mb-1">
                <IconBuilding className="w-3.5 h-3.5" />
                Mərkəz
              </div>
              <p className="text-slate-200 text-sm font-medium">{ticket.exam.center}</p>
            </div>
            <div>
              <div className="flex items-center gap-2 text-gray-500 text-xs mb-1">
                <IconLocation className="w-3.5 h-3.5" />
                Ünvan
              </div>
              <p className="text-slate-200 text-sm font-medium">{ticket.exam.address}</p>
            </div>
          </div>

          {/* Contact strip */}
          <div className="mt-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 p-4 bg-white/5 border border-white/10 rounded-xl text-xs text-gray-400">
            <span>E-poçt: <span className="text-slate-300">{ticket.email}</span></span>
            <span>Telefon: <span className="text-slate-300">{ticket.phone}</span></span>
          </div>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row items-center justify-center gap-3 mt-8">
        <button
          onClick={print}
          className="inline-flex items-center gap-2 px-6 py-3 bg-white/5 hover:bg-white/10 border border-white/10 text-gray-300 hover:text-white text-sm font-semibold rounded-xl transition-all cursor-pointer"
        >
          <IconPrint className="w-4 h-4" />
          Çap et
        </button>
        <button
          onClick={onNewRegistration}
          className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-emerald-500 to-teal-600 text-white text-sm font-semibold rounded-xl shadow-lg shadow-emerald-500/25 hover:shadow-emerald-500/40 transition-all cursor-pointer"
        >
          Yeni qeydiyyat
        </button>
        {onDone && (
          <button
            onClick={onDone}
            className="inline-flex items-center gap-2 px-6 py-3 text-sm font-semibold text-gray-400 hover:text-white transition-all cursor-pointer"
          >
            Tamam
          </button>
        )}
      </div>
    </div>
  );
}
