import { DashboardStats, Appointment, Doctor, CallLog, Clinic } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export async function fetchClinics(): Promise<Clinic[]> {
  try {
    const res = await fetch(`${API_BASE}/clinics`);
    if (!res.ok) throw new Error("Failed to fetch clinics");
    return await res.json();
  } catch (err) {
    return [
      {
        id: "c1111111-2222-3333-4444-555555555555",
        name: "Sree Kerala Ayurvedic Clinic",
        slug: "sree-kerala-ayurveda",
        phone_number: "+18005550199",
        address: "108 Dhanwantari Road, Fort Kochi, Kerala",
        timezone: "Asia/Kolkata"
      }
    ];
  }
}

export async function fetchDashboardStats(clinicId?: string): Promise<DashboardStats> {
  try {
    const url = clinicId ? `${API_BASE}/analytics/dashboard?clinic_id=${clinicId}` : `${API_BASE}/analytics/dashboard`;
    const res = await fetch(url);
    if (!res.ok) throw new Error("Failed to fetch dashboard stats");
    return await res.json();
  } catch (err) {
    // Graceful fallback for initial preview
    return {
      total_calls_today: 18,
      appointments_booked_today: 12,
      active_doctors: 2,
      total_patients: 46,
      recent_appointments: [
        {
          id: "app-1",
          clinic_id: "c1",
          doctor_id: "d1",
          patient_name: "Kavita Raman",
          patient_phone: "+91 98765 43210",
          appointment_time: new Date(Date.now() + 3600000 * 2).toISOString(),
          status: "booked",
          treatment_type: "Panchakarma Consultation",
          doctor_name: "Dr. Rajesh Varma",
          clinic_name: "Sree Kerala Ayurvedic Clinic",
          notes: "Patient complaining of stiff shoulders and fatigue.",
          created_at: new Date().toISOString()
        },
        {
          id: "app-2",
          clinic_id: "c1",
          doctor_id: "d2",
          patient_name: "Rahul Nambiar",
          patient_phone: "+91 98451 12345",
          appointment_time: new Date(Date.now() + 3600000 * 5).toISOString(),
          status: "completed",
          treatment_type: "Nadi Pariksha & Pulse Diagnosis",
          doctor_name: "Dr. Ananya Nair",
          clinic_name: "Sree Kerala Ayurvedic Clinic",
          notes: "Routine quarterly wellness assessment.",
          created_at: new Date(Date.now() - 86400000).toISOString()
        }
      ],
      recent_call_logs: [
        {
          id: "call-1",
          clinic_id: "c1",
          caller_phone: "+91 98765 43210",
          duration_seconds: 142,
          sentiment: "positive",
          outcome: "appointment_booked",
          summary: "Caller booked Panchakarma consultation with Dr. Rajesh Varma for 11:30 AM.",
          created_at: new Date(Date.now() - 1800000).toISOString()
        },
        {
          id: "call-2",
          clinic_id: "c1",
          caller_phone: "+91 98123 99999",
          duration_seconds: 88,
          sentiment: "neutral",
          outcome: "inquiry_answered",
          summary: "Caller inquired about clinic operating hours and Panchakarma package pricing.",
          created_at: new Date(Date.now() - 7200000).toISOString()
        }
      ]
    };
  }
}

export async function fetchAppointments(clinicId?: string): Promise<Appointment[]> {
  try {
    const url = clinicId ? `${API_BASE}/appointments?clinic_id=${clinicId}` : `${API_BASE}/appointments`;
    const res = await fetch(url);
    if (!res.ok) throw new Error("Failed to fetch appointments");
    return await res.json();
  } catch (err) {
    return [
      {
        id: "app-1",
        clinic_id: "c1",
        doctor_id: "d1",
        patient_name: "Kavita Raman",
        patient_phone: "+91 98765 43210",
        patient_email: "kavita@example.com",
        appointment_time: new Date(Date.now() + 3600000 * 4).toISOString(),
        status: "booked",
        treatment_type: "Panchakarma Consultation",
        doctor_name: "Dr. Rajesh Varma",
        clinic_name: "Sree Kerala Ayurvedic Clinic",
        notes: "Booking created autonomously by ElevenLabs Voice Receptionist.",
        call_transcript: "Agent: Namaste! Welcome to Sree Kerala Ayurvedic Clinic.\nPatient: Hi, I'd like to book an appointment with Dr. Varma tomorrow.\nAgent: Dr. Varma is available at 11:30 AM tomorrow. Shall I confirm that for you?\nPatient: Yes please, my name is Kavita Raman.\nAgent: Confirmed! Your confirmation ID is AYUR-4821.",
        created_at: new Date().toISOString()
      },
      {
        id: "app-2",
        clinic_id: "c1",
        doctor_id: "d2",
        patient_name: "Arjun Menon",
        patient_phone: "+91 97456 78901",
        patient_email: "arjun@example.com",
        appointment_time: new Date(Date.now() + 3600000 * 24).toISOString(),
        status: "booked",
        treatment_type: "Dosha Assessment & Diet Plan",
        doctor_name: "Dr. Ananya Nair",
        clinic_name: "Sree Kerala Ayurvedic Clinic",
        notes: "Dietary consultation for Pitta imbalance.",
        call_transcript: "Agent: Namaste and welcome to Sree Kerala Ayurvedic Clinic.\nPatient: Hello, do you have doctors for diet consultation?\nAgent: Yes! Dr. Ananya Nair specializes in Ayurvedic Dietetics and Wellness.\nPatient: Great, please book me for tomorrow afternoon.",
        created_at: new Date().toISOString()
      }
    ];
  }
}

export async function fetchDoctors(clinicId?: string): Promise<Doctor[]> {
  try {
    const url = clinicId ? `${API_BASE}/doctors?clinic_id=${clinicId}` : `${API_BASE}/doctors`;
    const res = await fetch(url);
    if (!res.ok) throw new Error("Failed to fetch doctors");
    return await res.json();
  } catch (err) {
    return [
      {
        id: "d1",
        clinic_id: "c1",
        name: "Dr. Rajesh Varma",
        specialization: "Panchakarma & Pulse Diagnosis Specialist",
        consultation_fee: 600,
        bio: "BAMS, MD (Ayurveda) with 18+ years experience in authentic Kerala Panchakarma therapies.",
        is_active: true,
        schedules: [
          { id: "s1", doctor_id: "d1", day_of_week: 0, start_time: "09:00:00", end_time: "17:00:00", slot_duration_minutes: 30, is_active: true },
          { id: "s2", doctor_id: "d1", day_of_week: 1, start_time: "09:00:00", end_time: "17:00:00", slot_duration_minutes: 30, is_active: true },
          { id: "s3", doctor_id: "d1", day_of_week: 2, start_time: "09:00:00", end_time: "17:00:00", slot_duration_minutes: 30, is_active: true },
          { id: "s4", doctor_id: "d1", day_of_week: 3, start_time: "09:00:00", end_time: "17:00:00", slot_duration_minutes: 30, is_active: true },
          { id: "s5", doctor_id: "d1", day_of_week: 4, start_time: "09:00:00", end_time: "17:00:00", slot_duration_minutes: 30, is_active: true },
          { id: "s6", doctor_id: "d1", day_of_week: 5, start_time: "09:00:00", end_time: "14:00:00", slot_duration_minutes: 30, is_active: true },
        ]
      },
      {
        id: "d2",
        clinic_id: "c1",
        name: "Dr. Ananya Nair",
        specialization: "Ayurvedic Dietetics & Skin Wellness",
        consultation_fee: 500,
        bio: "Expert in herbal pharmacology and holistic lifestyle coaching.",
        is_active: true,
        schedules: [
          { id: "s7", doctor_id: "d2", day_of_week: 0, start_time: "10:00:00", end_time: "18:00:00", slot_duration_minutes: 30, is_active: true },
          { id: "s8", doctor_id: "d2", day_of_week: 1, start_time: "10:00:00", end_time: "18:00:00", slot_duration_minutes: 30, is_active: true },
          { id: "s9", doctor_id: "d2", day_of_week: 2, start_time: "10:00:00", end_time: "18:00:00", slot_duration_minutes: 30, is_active: true },
          { id: "s10", doctor_id: "d2", day_of_week: 3, start_time: "10:00:00", end_time: "18:00:00", slot_duration_minutes: 30, is_active: true },
          { id: "s11", doctor_id: "d2", day_of_week: 4, start_time: "10:00:00", end_time: "18:00:00", slot_duration_minutes: 30, is_active: true },
        ]
      }
    ];
  }
}

export async function fetchCallLogs(clinicId?: string): Promise<CallLog[]> {
  try {
    const url = clinicId ? `${API_BASE}/analytics/call-logs?clinic_id=${clinicId}` : `${API_BASE}/analytics/call-logs`;
    const res = await fetch(url);
    if (!res.ok) throw new Error("Failed to fetch call logs");
    return await res.json();
  } catch (err) {
    return [
      {
        id: "call-1",
        clinic_id: "c1",
        call_sid: "CA382947192834",
        caller_phone: "+91 98765 43210",
        duration_seconds: 142,
        sentiment: "positive",
        outcome: "appointment_booked",
        summary: "Caller booked Panchakarma consultation with Dr. Rajesh Varma.",
        transcript: "Agent: Namaste! Welcome to Sree Kerala Ayurvedic Clinic. How can I assist you?\nCaller: Hello, I'd like to book an appointment with Dr. Varma tomorrow.\nAgent: Dr. Varma is available at 11:30 AM tomorrow. Shall I book that for you?\nCaller: Yes, please. My name is Kavita Raman.\nAgent: Done! Your booking reference is AYUR-4821.",
        created_at: new Date(Date.now() - 1800000).toISOString()
      },
      {
        id: "call-2",
        clinic_id: "c1",
        call_sid: "CA102938475612",
        caller_phone: "+91 98123 99999",
        duration_seconds: 88,
        sentiment: "neutral",
        outcome: "inquiry_answered",
        summary: "Inquiry regarding treatment packages and clinic timings.",
        transcript: "Agent: Namaste! Welcome to Sree Kerala Ayurvedic Clinic.\nCaller: Hi, what are your working hours and consultation charges?\nAgent: We are open Monday through Saturday from 9 AM to 6 PM. Consultation with our specialists is 500 to 600 rupees.\nCaller: Great, thank you so much!",
        created_at: new Date(Date.now() - 7200000).toISOString()
      }
    ];
  }
}

export async function fetchKnowledgeBase(clinicId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/clinics/${clinicId}/knowledge-base`);
  if (!res.ok) throw new Error("Failed to fetch knowledge base");
  return await res.json();
}

export async function updateKnowledgeBase(
  clinicId: string,
  knowledgeBaseText: string,
  syncToElevenlabs: boolean = true
): Promise<any> {
  const res = await fetch(`${API_BASE}/clinics/${clinicId}/knowledge-base`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      knowledge_base: knowledgeBaseText,
      sync_to_elevenlabs: syncToElevenlabs,
    }),
  });
  if (!res.ok) throw new Error("Failed to update knowledge base");
  return await res.json();
}


