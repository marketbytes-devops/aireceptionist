export interface Clinic {
  id: string;
  name: string;
  slug: string;
  phone_number: string;
  address?: string;
  timezone: string;
}

export interface DoctorSchedule {
  id: string;
  doctor_id: string;
  day_of_week: number;
  start_time: string;
  end_time: string;
  slot_duration_minutes: number;
  is_active: boolean;
}

export interface Doctor {
  id: string;
  clinic_id: string;
  name: string;
  specialization: string;
  consultation_fee: number;
  bio?: string;
  is_active: boolean;
  schedules?: DoctorSchedule[];
}

export interface Appointment {
  id: string;
  clinic_id: string;
  doctor_id: string;
  patient_name: string;
  patient_phone: string;
  patient_email?: string;
  appointment_time: string;
  status: "booked" | "completed" | "cancelled" | "no_show";
  treatment_type?: string;
  notes?: string;
  call_transcript?: string;
  doctor_name?: string;
  clinic_name?: string;
  created_at: string;
}

export interface CallLog {
  id: string;
  clinic_id: string;
  call_sid?: string;
  caller_phone: string;
  duration_seconds?: number;
  recording_url?: string;
  transcript?: string;
  summary?: string;
  sentiment?: string;
  outcome?: string;
  created_at: string;
}

export interface DashboardStats {
  total_calls_today: number;
  appointments_booked_today: number;
  active_doctors: number;
  total_patients: number;
  recent_appointments: Appointment[];
  recent_call_logs: CallLog[];
}

