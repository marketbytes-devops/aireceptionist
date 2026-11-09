"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { 
  PhoneCall, 
  CalendarCheck, 
  Users, 
  Stethoscope, 
  Bot, 
  ArrowUpRight, 
  Clock, 
  Sparkles,
  ChevronRight,
  FileText
} from "lucide-react";
import StatCard from "@/components/StatCard";
import TranscriptModal from "@/components/TranscriptModal";
import { fetchDashboardStats } from "@/lib/api";
import { DashboardStats, Appointment, CallLog } from "@/lib/types";

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [selectedTranscript, setSelectedTranscript] = useState<{
    title: string;
    transcript?: string;
    patientName?: string;
    callerPhone?: string;
    date?: string;
    sentiment?: string;
  } | null>(null);

  useEffect(() => {
    fetchDashboardStats().then(setStats);
  }, []);

  if (!stats) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-xs text-slate-500 font-medium">Loading clinic analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Top Banner / Welcome */}
      <div className="bg-gradient-to-r from-emerald-900 via-teal-900 to-slate-900 rounded-2xl p-5 sm:p-6 md:p-8 text-white shadow-xl relative overflow-hidden">
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 text-xs font-semibold mb-3 border border-emerald-500/30">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Ayurvedic Conversational Receptionist Active</span>
          </div>
          <h2 className="text-xl sm:text-2xl md:text-3xl font-bold tracking-tight">
            Namaste, Sreerudra Ayurveda Multi Speciality Hospital
          </h2>
          <p className="mt-2 text-xs sm:text-sm text-slate-300 leading-relaxed">
            Your ElevenLabs AI voice receptionist (Asha) is handling patient calls for Alappuzha & Trivandrum hospital campuses, checking doctor schedules, and scheduling consultations.
          </p>

          <div className="mt-5 flex flex-wrap gap-3">
            <Link
              href="/simulator"
              className="inline-flex items-center gap-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold px-4 py-2 rounded-lg text-xs transition-all shadow-md"
            >
              <Bot className="w-4 h-4" />
              <span>Launch AI Voice Simulator</span>
            </Link>
            <Link
              href="/appointments"
              className="inline-flex items-center gap-2 bg-white/10 hover:bg-white/20 text-white font-medium px-4 py-2 rounded-lg text-xs transition-all backdrop-blur-xs"
            >
              <span>View All Bookings</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          title="Calls Received Today"
          value={stats.total_calls_today}
          change="+18%"
          isPositive={true}
          icon={PhoneCall}
          color="emerald"
          subtext="Processed autonomously by AI"
        />
        <StatCard
          title="Appointments Booked"
          value={stats.appointments_booked_today}
          change="+25%"
          isPositive={true}
          icon={CalendarCheck}
          color="blue"
          subtext="Confirmed & synced to calendar"
        />
        <StatCard
          title="Active Doctors On Duty"
          value={stats.active_doctors}
          icon={Stethoscope}
          color="amber"
          subtext="Available for Panchakarma & Pulse diagnosis"
        />
        <StatCard
          title="Total Registered Patients"
          value={stats.total_patients}
          change="+6 today"
          isPositive={true}
          icon={Users}
          color="indigo"
          subtext="Multi-tenant patient registry"
        />
      </div>

      {/* Two Column Section: Recent Bookings & Recent Calls */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left 2 Cols: Recent Bookings Table */}
        <div className="lg:col-span-2 bg-white rounded-2xl p-6 border border-slate-200/90 shadow-xs">
          <div className="flex items-center justify-between pb-4 border-b border-slate-100">
            <div>
              <h3 className="font-semibold text-slate-800 text-base">Recent AI Receptionist Bookings</h3>
              <p className="text-xs text-slate-500">Appointments scheduled directly from patient phone calls</p>
            </div>
            <Link
              href="/appointments"
              className="text-xs text-emerald-600 hover:text-emerald-700 font-semibold flex items-center gap-1"
            >
              View all <ChevronRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="overflow-x-auto mt-4 -mx-2 sm:mx-0">
            <table className="w-full text-left text-xs min-w-[640px]">
              <thead>
                <tr className="text-slate-400 uppercase tracking-wider border-b border-slate-100">
                  <th className="pb-3 font-medium">Patient</th>
                  <th className="pb-3 font-medium">Doctor & Treatment</th>
                  <th className="pb-3 font-medium">Scheduled Time</th>
                  <th className="pb-3 font-medium">Status</th>
                  <th className="pb-3 font-medium text-right">Call Transcript</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {stats.recent_appointments.map((app) => (
                  <tr key={app.id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="py-3.5 font-medium text-slate-800">
                      <div>{app.patient_name}</div>
                      <div className="text-[11px] text-slate-400 font-normal">{app.patient_phone}</div>
                    </td>
                    <td className="py-3.5">
                      <div className="text-slate-700 font-medium">{app.doctor_name || "Specialist Vaidya"}</div>
                      <div className="text-[11px] text-emerald-600 font-medium">{app.treatment_type}</div>
                    </td>
                    <td className="py-3.5 text-slate-600">
                      <div className="flex items-center gap-1.5">
                        <Clock className="w-3.5 h-3.5 text-slate-400" />
                        <span>{new Date(app.appointment_time).toLocaleString([], { dateStyle: "short", timeStyle: "short" })}</span>
                      </div>
                    </td>
                    <td className="py-3.5">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold capitalize ${
                        app.status === "booked"
                          ? "bg-emerald-100 text-emerald-800"
                          : app.status === "completed"
                          ? "bg-blue-100 text-blue-800"
                          : "bg-rose-100 text-rose-800"
                      }`}>
                        {app.status}
                      </span>
                    </td>
                    <td className="py-3.5 text-right">
                      <button
                        onClick={() =>
                          setSelectedTranscript({
                            title: `Call Dialogue - ${app.patient_name}`,
                            transcript: app.call_transcript || "Agent: Namaste! How may I assist you with Ayurvedic care?\nPatient: I need an appointment for pulse diagnosis.\nAgent: Confirmed for tomorrow 11:30 AM.",
                            patientName: app.patient_name,
                            callerPhone: app.patient_phone,
                            date: app.appointment_time,
                            sentiment: "positive",
                          })
                        }
                        className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium text-[11px] transition-colors"
                      >
                        <FileText className="w-3 h-3 text-slate-500" />
                        <span>Transcript</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right 1 Col: Live AI Receptionist Activity & Recent Calls */}
        <div className="space-y-6">
          {/* Quick Telephony Status */}
          <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-xs">
            <h3 className="font-semibold text-slate-800 text-sm mb-3">Telephony & AI Status</h3>
            <div className="space-y-3 text-xs">
              <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-50 border border-slate-100">
                <span className="text-slate-600 font-medium">Twilio Inbound DID</span>
                <span className="font-semibold text-slate-800">+1 (800) 555-0199</span>
              </div>
              <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-50 border border-slate-100">
                <span className="text-slate-600 font-medium">ElevenLabs Agent</span>
                <span className="inline-flex items-center gap-1 font-semibold text-emerald-600">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                  Connected
                </span>
              </div>
              <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-50 border border-slate-100">
                <span className="text-slate-600 font-medium">Tool Webhooks</span>
                <span className="font-semibold text-slate-700">2 Active (Check & Book)</span>
              </div>
            </div>
          </div>

          {/* Recent Call Logs Feed */}
          <div className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-xs">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-slate-800 text-sm">Recent Call Logs</h3>
              <Link href="/calls" className="text-xs text-emerald-600 hover:text-emerald-700 font-medium">
                All Logs
              </Link>
            </div>

            <div className="space-y-3">
              {stats.recent_call_logs.map((call) => (
                <div
                  key={call.id}
                  onClick={() =>
                    setSelectedTranscript({
                      title: `Call Log - ${call.caller_phone}`,
                      transcript: call.transcript || "Agent: Namaste! Welcome to Sree Kerala Ayurvedic Clinic.\nCaller: Hello, I called to inquire about Panchakarma treatments.",
                      callerPhone: call.caller_phone,
                      date: call.created_at,
                      sentiment: call.sentiment || "positive",
                    })
                  }
                  className="p-3 rounded-xl bg-slate-50 hover:bg-emerald-50/50 border border-slate-100 hover:border-emerald-200 cursor-pointer transition-all"
                >
                  <div className="flex items-center justify-between text-xs font-semibold text-slate-800">
                    <span>{call.caller_phone}</span>
                    <span className="text-[10px] text-slate-400 font-normal">
                      {call.duration_seconds ? `${call.duration_seconds}s` : "45s"}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 mt-1 line-clamp-2 leading-relaxed">
                    {call.summary || "Patient consulted AI receptionist regarding appointment availability."}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Transcript Modal */}
      {selectedTranscript && (
        <TranscriptModal
          isOpen={true}
          onClose={() => setSelectedTranscript(null)}
          title={selectedTranscript.title}
          transcript={selectedTranscript.transcript}
          patientName={selectedTranscript.patientName}
          callerPhone={selectedTranscript.callerPhone}
          date={selectedTranscript.date}
          sentiment={selectedTranscript.sentiment}
        />
      )}
    </div>
  );
}

