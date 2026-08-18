export type ExamTab = 'register' | 'schedule' | 'centers' | 'rules';

export type ExamStatus = 'open' | 'closed' | 'full';

export interface Exam {
  id: string;
  title: string;
  subject: string;
  date: string;
  time: string;
  durationMinutes: number;
  center: string;
  address: string;
  price: number;
  totalSeats: number;
  registeredCount: number;
  status: ExamStatus;
}

export interface RegistrationData {
  id: string;
  ticketNumber: string;
  exam: Exam;
  fullName: string;
  email: string;
  phone: string;
  registeredAt: string;
}

export interface ExamCenter {
  id: string;
  name: string;
  address: string;
  phone: string;
  rooms: number;
  capacity: number;
}

export interface ExamRule {
  id: number;
  title: string;
  text: string;
}
