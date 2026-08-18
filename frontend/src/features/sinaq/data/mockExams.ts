import { type Exam, type RegistrationData, type ExamCenter, type ExamRule } from '../types';

export const EXAMS: Exam[] = [
  {
    id: 'EXAM-001',
    title: 'Riyaziyyat fənni üzrə sınaq imtahanı',
    subject: 'Riyaziyyat',
    date: '2026-09-14',
    time: '10:00',
    durationMinutes: 180,
    center: 'Binəqədi Tədris Mərkəzi',
    address: 'Binəqədi qəsəbəsi, S. Vurğun küç. 43',
    price: 15,
    totalSeats: 120,
    registeredCount: 87,
    status: 'open',
  },
  {
    id: 'EXAM-002',
    title: 'Azərbaycan dili üzrə sınaq imtahanı',
    subject: 'Azərbaycan dili',
    date: '2026-09-16',
    time: '10:00',
    durationMinutes: 150,
    center: 'Binəqədi Tədris Mərkəzi',
    address: 'Binəqədi qəsəbəsi, S. Vurğun küç. 43',
    price: 15,
    totalSeats: 120,
    registeredCount: 112,
    status: 'open',
  },
  {
    id: 'EXAM-003',
    title: 'Xarici dil (İngilis) üzrə sınaq imtahanı',
    subject: 'Xarici dil',
    date: '2026-09-20',
    time: '14:00',
    durationMinutes: 150,
    center: 'Nərimanov Tədris Mərkəzi',
    address: 'Nərimanov rayonu, Azadlıq prospekti 76',
    price: 15,
    totalSeats: 90,
    registeredCount: 90,
    status: 'full',
  },
  {
    id: 'EXAM-004',
    title: 'Fizika fənni üzrə sınaq imtahanı',
    subject: 'Fizika',
    date: '2026-09-27',
    time: '10:00',
    durationMinutes: 180,
    center: 'Nərimanov Tədris Mərkəzi',
    address: 'Nərimanov rayonu, Azadlıq prospekti 76',
    price: 15,
    totalSeats: 100,
    registeredCount: 41,
    status: 'open',
  },
  {
    id: 'EXAM-005',
    title: 'Kimya fənni üzrə sınaq imtahanı',
    subject: 'Kimya',
    date: '2026-10-04',
    time: '14:00',
    durationMinutes: 180,
    center: 'Nəsimi Tədris Mərkəzi',
    address: 'Nəsimi rayonu, C. Cabbarlı küç. 14',
    price: 15,
    totalSeats: 80,
    registeredCount: 23,
    status: 'open',
  },
  {
    id: 'EXAM-006',
    title: 'Riyaziyyat fənni üzrə sınaq imtahanı (II dəstə)',
    subject: 'Riyaziyyat',
    date: '2026-10-11',
    time: '10:00',
    durationMinutes: 180,
    center: 'Binəqədi Tədris Mərkəzi',
    address: 'Binəqədi qəsəbəsi, S. Vurğun küç. 43',
    price: 15,
    totalSeats: 120,
    registeredCount: 58,
    status: 'open',
  },
];

export const INITIAL_REGISTERED_TICKETS: RegistrationData[] = [
  {
    id: 'TICKET-4821',
    ticketNumber: 'SNQ-2026-04821',
    exam: EXAMS[0],
    fullName: 'Ağasəf Zeynalov',
    email: 'agashef@mail.com',
    phone: '+994501234567',
    registeredAt: '2026-08-18T10:24:00Z',
  },
  {
    id: 'TICKET-1193',
    ticketNumber: 'SNQ-2026-01193',
    exam: EXAMS[1],
    fullName: 'Nigar Babayeva',
    email: 'nigar.b@mail.com',
    phone: '+994507654321',
    registeredAt: '2026-08-15T16:40:00Z',
  },
];

export const EXAM_CENTERS: ExamCenter[] = [
  {
    id: 'CNTR-01',
    name: 'Binəqədi Tədris Mərkəzi',
    address: 'Binəqədi qəsəbəsi, S. Vurğun küç. 43, Bakı',
    phone: '+994 12 123 45 67',
    rooms: 6,
    capacity: 240,
  },
  {
    id: 'CNTR-02',
    name: 'Nərimanov Tədris Mərkəzi',
    address: 'Nərimanov rayonu, Azadlıq prospekti 76, Bakı',
    phone: '+994 12 765 43 21',
    rooms: 5,
    capacity: 200,
  },
  {
    id: 'CNTR-03',
    name: 'Nəsimi Tədris Mərkəzi',
    address: 'Nəsimi rayonu, C. Cabbarlı küç. 14, Bakı',
    phone: '+994 12 333 22 11',
    rooms: 4,
    capacity: 160,
  },
  {
    id: 'CNTR-04',
    name: 'Xətai Tədris Mərkəzi',
    address: 'Xətai rayonu, Xəqani küç. 5, Bakı',
    phone: '+994 12 456 78 90',
    rooms: 4,
    capacity: 160,
  },
];

export const EXAM_RULES: ExamRule[] = [
  {
    id: 1,
    title: 'Gəliş vaxtı',
    text: 'İmtahan başlamazdan ən azı 45 dəqiqə əvvəl binada olmalısınız. Gecikən iştirakçılar imtahana buraxılmır.',
  },
  {
    id: 2,
    title: 'Kimlik',
    text: 'Yanınızda buraxlış vərəqəsi (kağız və ya elektron) və şəxsiyyəti təsdiq edən sənəd olmalıdır.',
  },
  {
    id: 3,
    title: 'Qadağan olunanlar',
    text: 'Telefon, saat, kalkulyator və digər elektron cihazlar imtahan binasına gətirilmir.',
  },
  {
    id: 4,
    title: 'Dəftərxana ləvazimatları',
    text: 'Yalnız qara və ya tünd göy mürəkkəbli qələmdən istifadə edin. Qaralama üçün kağız verilir.',
  },
  {
    id: 5,
    title: 'Cavab vərəqəsi',
    text: 'Cavab vərəqəsi imtahan bitdikdə müəllimə təhvil verilməlidir. Nəticələr portalda iş nömrəsi ilə dərc olunur.',
  },
  {
    id: 6,
    title: 'Qeydiyyat təsdiqi',
    text: 'Qeydiyyatdan sonra buraxlış vərəqənizi yadda saxlayın və ya çap edin. Bilet nömrəsi nəticəyə baxmaq üçün tələb olunur.',
  },
];

export function generateTicketNumber(): string {
  const year = new Date().getFullYear();
  const num = String(Math.floor(10000 + Math.random() * 90000));
  return `SNQ-${year}-${num}`;
}

export function generateId(prefix: string): string {
  return `${prefix}-${Date.now().toString(36).toUpperCase()}${Math.floor(Math.random() * 999).toString(36).toUpperCase()}`;
}

export function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString('az-AZ', { day: '2-digit', month: 'long', year: 'numeric' });
}

export function formatDateTime(iso: string): string {
  const d = new Date(iso);
  return `${d.toLocaleDateString('az-AZ', { day: '2-digit', month: '2-digit', year: 'numeric' })} ${d.toLocaleTimeString('az-AZ', { hour: '2-digit', minute: '2-digit' })}`;
}
