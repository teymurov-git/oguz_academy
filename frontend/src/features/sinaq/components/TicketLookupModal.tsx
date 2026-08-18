import { useState } from 'react';
import { type RegistrationData } from '../types';
import { formatDate } from '../data/mockExams';
import { IconClose, IconSearch, IconTicket } from './icons';

interface TicketLookupModalProps {
  open: boolean;
  onClose: () => void;
  registrations: RegistrationData[];
  onSelect: (ticket: RegistrationData) => void;
}

export function TicketLookupModal({ open, onClose, registrations, onSelect }: TicketLookupModalProps) {
  const [query, setQuery] = useState('');

  if (!open) return null;

  const q = query.trim().toLowerCase();
  const results = q
    ? registrations.filter(
        (r) =>
          r.ticketNumber.toLowerCase().includes(q) ||
          r.fullName.toLowerCase().includes(q) ||
          r.email.toLowerCase().includes(q) ||
          r.phone.replace(/\s/g, '').includes(q.replace(/\s/g, ''))
      )
    : [];

  const select = (t: RegistrationData) => {
    setQuery('');
    onSelect(t);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-slate-900 border border-white/10 rounded-2xl w-full max-w-md shadow-2xl shadow-black/50">
        <div className="flex items-center justify-between px-5 py-4 border-b border-white/5">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-emerald-500/15 flex items-center justify-center">
              <IconSearch className="w-4 h-4 text-emerald-400" />
            </div>
            <div>
              <h3 className="text-white font-semibold text-sm">Qeydiyyatı axtar</h3>
              <p className="text-gray-500 text-xs">Bilet nömrəsi, ad və ya telefonla</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-white/10 transition-colors cursor-pointer"
          >
            <IconClose className="w-5 h-5" />
          </button>
        </div>

        <div className="px-5 py-4">
          <input
            autoFocus
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="SNQ-2026-04821 və ya telefon..."
            className="w-full bg-slate-950/80 border border-white/10 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-gray-500 focus:outline-none focus:border-emerald-500/60 focus:ring-2 focus:ring-emerald-500/20 transition-all"
          />

          <div className="mt-4 max-h-80 overflow-y-auto space-y-2 pr-1">
            {q === '' && (
              <p className="text-center text-gray-500 text-sm py-6">
                Bilet nömrənizi və ya qeydiyyat məlumatlarınızı daxil edin.
              </p>
            )}
            {q !== '' && results.length === 0 && (
              <p className="text-center text-gray-500 text-sm py-6">Heç bir qeydiyyat tapılmadı.</p>
            )}
            {results.map((r) => (
              <button
                key={r.id}
                onClick={() => select(r)}
                className="w-full flex items-center gap-3 p-3 bg-slate-950/60 border border-white/5 rounded-xl hover:border-emerald-500/40 hover:bg-emerald-500/5 transition-all text-left cursor-pointer"
              >
                <div className="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center shrink-0">
                  <IconTicket className="w-5 h-5 text-emerald-400" />
                </div>
                <div className="min-w-0">
                  <p className="text-white font-semibold text-sm truncate">{r.fullName}</p>
                  <p className="text-gray-500 text-xs truncate">
                    <span className="font-mono text-emerald-400">{r.ticketNumber}</span> · {r.exam.subject} · {formatDate(r.exam.date)}
                  </p>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
