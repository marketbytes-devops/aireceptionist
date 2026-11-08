"use client";

import { useEffect, useState } from "react";
import { 
  CalendarDays, 
  Search, 
  Filter, 
  Clock, 
  Phone, 
  FileText, 
  CheckCircle, 
  XCircle, 
  UserPlus,
  Sparkles,
  Plus,
  X,
  Stethoscope,
  Check
} from "lucide-react";
import { fetchAppointments, fetchDoctors } from "@/lib/api";
import { Appointment, Doctor } from "@/lib/types";
import TranscriptModal from "@/components/TranscriptModal";

export default function AppointmentsPage() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [isBookingModalOpen, setIsBookingModalOpen] = useState(false);

  // New Appointment Form State
  const [newPatientName, setNewPatientName] = useState("");
  const [newPatientPhone, setNewPatientPhone] = useState("");
  const [newDoctorName, setNewDoctorName] = useState("");
  const [newDateTime, setNewDateTime] = useState("");
  const [newTreatment, setNewTreatment] = useState("Panchakarma Consultation");
  const [newNotes, setNewNotes] = useState("");

  const [selectedTranscript, setSelectedTranscript] = useState<{
    title: string;
    transcript?: string;
    patientName?: string;
    callerPhone?: string;
    date?: string;
    sentiment?: string;
  } | null>(null);

  useEffect(() => {
    fetchAppointments().then(setAppointments);
    fetchDoctors().then((docs) => {
      setDoctors(docs);
      if (docs.length > 0) setNewDoctorName(docs[0].name);
    });
  }, []);

  const filteredAppointments = appointments.filter((app) => {
    const matchesStatus = filterStatus === "all" || app.status === filterStatus;
    const matchesSearch =
      app.patient_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      app.patient_phone.includes(searchQuery) ||
      (app.doctor_name && app.doctor_name.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesStatus && matchesSearch;
  });

  const handleStatusChange = (id: string, newStatus: Appointment["status"]) => {
    setAppointments((prev) =>
      prev.map((app) => (app.id === id ? { ...app, status: newStatus } : app))
    );
  };

  const handleCreateAppointment = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newPatientName || !newPatientPhone || !newDateTime) return;

    const newApp: Appointment = {
      id: `manual-${Date.now()}`,
      clinic_id: "c1",
      doctor_id: doctors.find((d) => d.name === newDoctorName)?.id || "d1",
      patient_name: newPatientName,
      patient_phone: newPatientPhone,
      appointment_time: new Date(newDateTime).toISOString(),
      status: "booked",
      treatment_type: newTreatment,
      doctor_name: newDoctorName || "Dr. Rajesh Varma",
      clinic_name: "Sree Kerala Ayurvedic Clinic",
      notes: newNotes || "Walk-in patient booked manually by clinic desk.",
      created_at: new Date().toISOString()
    };

    setAppointments((prev) => [newApp, ...prev]);
    setIsBookingModalOpen(false);
    setNewPatientName("");
    setNewPatientPhone("");
    setNewDateTime("");
    setNewNotes("");
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl md:text-2xl font-bold text-slate-800 tracking-tight">
            Patient Appointments
          </h2>
          <p className="text-xs md:text-sm text-slate-500">
            Real-time Ayurvedic consultation bookings routed by ElevenLabs AI Receptionist & Clinic Desk
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsBookingModalOpen(true)}
            className="inline-flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-4 py-2 rounded-xl text-xs transition-colors shadow-xs"
          >
            <Plus className="w-4 h-4" />
            <span>Book Walk-In Patient</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white rounded-xl p-4 border border-slate-200/90 shadow-xs flex flex-col md:flex-row gap-4 items-center justify-between">
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by patient name, phone, or doctor..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-slate-50"
          />
        </div>

        <div className="flex items-center gap-2 w-full md:w-auto overflow-x-auto pb-1 md:pb-0">
          <span className="text-xs text-slate-400 font-medium flex items-center gap-1">
            <Filter className="w-3.5 h-3.5" /> Filter:
          </span>
          {["all", "booked", "completed", "cancelled"].map((status) => (
            <button
              key={status}
              onClick={() => setFilterStatus(status)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition-all ${
                filterStatus === status
                  ? "bg-emerald-600 text-white shadow-xs"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              {status}
            </button>
          ))}
        </div>
      </div>

      {/* Appointments Table */}
      <div className="bg-white rounded-2xl border border-slate-200/90 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs min-w-[760px]">
            <thead>
              <tr className="bg-slate-50/80 text-slate-500 uppercase tracking-wider border-b border-slate-200 font-medium">
                <th className="py-3.5 px-6">Patient</th>
                <th className="py-3.5 px-6">Doctor & Treatment</th>
                <th className="py-3.5 px-6">Date & Time</th>
                <th className="py-3.5 px-6">Status</th>
                <th className="py-3.5 px-6">Notes / Complaint</th>
                <th className="py-3.5 px-6 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredAppointments.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center py-12 text-slate-400 text-sm">
                    No appointments match your filter criteria.
                  </td>
                </tr>
              ) : (
                filteredAppointments.map((app) => (
                  <tr key={app.id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="py-4 px-6 font-medium text-slate-800">
                      <div className="text-sm font-semibold text-slate-900">{app.patient_name}</div>
                      <div className="text-[11px] text-slate-500 flex items-center gap-1 mt-0.5">
                        <Phone className="w-3 h-3 text-slate-400" />
                        <span>{app.patient_phone}</span>
                      </div>
                    </td>

                    <td className="py-4 px-6">
                      <div className="font-semibold text-slate-800">{app.doctor_name || "Specialist Vaidya"}</div>
                      <div className="text-[11px] font-medium text-emerald-600 mt-0.5">
                        {app.treatment_type || "General Ayurvedic Consultation"}
                      </div>
                    </td>

                    <td className="py-4 px-6 text-slate-700">
                      <div className="flex items-center gap-1.5 font-medium">
                        <Clock className="w-3.5 h-3.5 text-slate-400" />
                        <span>
                          {new Date(app.appointment_time).toLocaleString([], {
                            weekday: "short",
                            month: "short",
                            day: "numeric",
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </span>
                      </div>
                    </td>

                    <td className="py-4 px-6">
                      <span
                        className={`inline-flex items-center px-2.5 py-1 rounded-full text-[11px] font-semibold capitalize ${
                          app.status === "booked"
                            ? "bg-emerald-100 text-emerald-800 border border-emerald-200"
                            : app.status === "completed"
                            ? "bg-blue-100 text-blue-800 border border-blue-200"
                            : "bg-rose-100 text-rose-800 border border-rose-200"
                        }`}
                      >
                        {app.status}
                      </span>
                    </td>

                    <td className="py-4 px-6 text-slate-600 max-w-xs truncate">
                      {app.notes || "Booked autonomously by AI receptionist."}
                    </td>

                    <td className="py-4 px-6 text-right space-x-2 whitespace-nowrap">
                      {app.call_transcript ? (
                        <button
                          onClick={() =>
                            setSelectedTranscript({
                              title: `AI Call Transcript - ${app.patient_name}`,
                              transcript: app.call_transcript,
                              patientName: app.patient_name,
                              callerPhone: app.patient_phone,
                              date: app.appointment_time,
                              sentiment: "positive",
                            })
                          }
                          className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-700 font-medium text-xs transition-colors border border-emerald-200"
                        >
                          <FileText className="w-3.5 h-3.5" />
                          <span>AI Transcript</span>
                        </button>
                      ) : (
                        <span className="text-[11px] text-slate-400 italic mr-2">Walk-in</span>
                      )}

                      {app.status === "booked" && (
                        <>
                          <button
                            onClick={() => handleStatusChange(app.id, "completed")}
                            title="Mark as Completed"
                            className="p-1.5 rounded-lg text-emerald-600 hover:bg-emerald-50 hover:text-emerald-700 transition-colors"
                          >
                            <CheckCircle className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleStatusChange(app.id, "cancelled")}
                            title="Cancel Appointment"
                            className="p-1.5 rounded-lg text-rose-500 hover:bg-rose-50 hover:text-rose-700 transition-colors"
                          >
                            <XCircle className="w-4 h-4" />
                          </button>
                        </>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Manual Booking Modal */}
      {isBookingModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4 animate-in fade-in">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <h3 className="font-bold text-slate-800 text-base flex items-center gap-2">
                <UserPlus className="w-4 h-4 text-emerald-600" />
                <span>Book Walk-In Patient</span>
              </h3>
              <button
                onClick={() => setIsBookingModalOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateAppointment} className="space-y-4 text-xs">
              <div>
                <label className="block font-medium text-slate-700 mb-1">Patient Full Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Ramesh Varma"
                  value={newPatientName}
                  onChange={(e) => setNewPatientName(e.target.value)}
                  className="w-full p-2.5 rounded-lg border border-slate-200 bg-slate-50 text-slate-800"
                />
              </div>

              <div>
                <label className="block font-medium text-slate-700 mb-1">Phone Number</label>
                <input
                  type="text"
                  required
                  placeholder="+91 98765 43210"
                  value={newPatientPhone}
                  onChange={(e) => setNewPatientPhone(e.target.value)}
                  className="w-full p-2.5 rounded-lg border border-slate-200 bg-slate-50 text-slate-800"
                />
              </div>

              <div>
                <label className="block font-medium text-slate-700 mb-1">Select Doctor</label>
                <select
                  value={newDoctorName}
                  onChange={(e) => setNewDoctorName(e.target.value)}
                  className="w-full p-2.5 rounded-lg border border-slate-200 bg-slate-50 text-slate-800 font-medium"
                >
                  {doctors.map((d) => (
                    <option key={d.id} value={d.name}>
                      {d.name} ({d.specialization})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-medium text-slate-700 mb-1">Treatment Type</label>
                <select
                  value={newTreatment}
                  onChange={(e) => setNewTreatment(e.target.value)}
                  className="w-full p-2.5 rounded-lg border border-slate-200 bg-slate-50 text-slate-800 font-medium"
                >
                  <option value="Panchakarma Consultation">Panchakarma Consultation</option>
                  <option value="Nadi Pariksha & Pulse Diagnosis">Nadi Pariksha & Pulse Diagnosis</option>
                  <option value="Dosha Assessment & Diet Plan">Dosha Assessment & Diet Plan</option>
                  <option value="General Ayurvedic Consultation">General Ayurvedic Consultation</option>
                  <option value="Ayurvedic Skin Wellness Therapy">Ayurvedic Skin Wellness Therapy</option>
                </select>
              </div>

              <div>
                <label className="block font-medium text-slate-700 mb-1">Appointment Date & Time</label>
                <input
                  type="datetime-local"
                  required
                  value={newDateTime}
                  onChange={(e) => setNewDateTime(e.target.value)}
                  className="w-full p-2.5 rounded-lg border border-slate-200 bg-slate-50 text-slate-800 font-medium"
                />
              </div>

              <div>
                <label className="block font-medium text-slate-700 mb-1">Notes / Health Complaints</label>
                <textarea
                  rows={2}
                  placeholder="Primary health complaints or history..."
                  value={newNotes}
                  onChange={(e) => setNewNotes(e.target.value)}
                  className="w-full p-2.5 rounded-lg border border-slate-200 bg-slate-50 text-slate-800"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setIsBookingModalOpen(false)}
                  className="px-4 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold flex items-center gap-1.5 shadow-xs"
                >
                  <Check className="w-4 h-4" />
                  <span>Confirm Booking</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

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
