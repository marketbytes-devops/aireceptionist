"use client";

import { useEffect, useState } from "react";
import { 
  Stethoscope, 
  Clock, 
  Calendar, 
  Plus, 
  Edit3, 
  Check, 
  IndianRupee, 
  ShieldCheck, 
  UserCheck,
  UserPlus,
  X
} from "lucide-react";
import { fetchDoctors } from "@/lib/api";
import { Doctor, DoctorSchedule } from "@/lib/types";

const DAYS_OF_WEEK = [
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
  "Sunday"
];

export default function DoctorsPage() {
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [selectedDoctorId, setSelectedDoctorId] = useState<string>("");
  const [editingSchedule, setEditingSchedule] = useState<{
    doctorId: string;
    dayOfWeek: number;
    startTime: string;
    endTime: string;
    slotDuration: number;
  } | null>(null);

  // New Doctor Modal State
  const [isNewDoctorModalOpen, setIsNewDoctorModalOpen] = useState(false);
  const [newDoctorName, setNewDoctorName] = useState("");
  const [newSpecialization, setNewSpecialization] = useState("Panchakarma & Pulse Diagnosis Specialist");
  const [newFee, setNewFee] = useState(500);
  const [newBio, setNewBio] = useState("");

  useEffect(() => {
    fetchDoctors().then((docs) => {
      setDoctors(docs);
      if (docs.length > 0) {
        setSelectedDoctorId(docs[0].id);
      }
    });
  }, []);

  const selectedDoctor = doctors.find((d) => d.id === selectedDoctorId) || doctors[0];

  const handleSaveSchedule = (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingSchedule || !selectedDoctor) return;

    setDoctors((prev) =>
      prev.map((doc) => {
        if (doc.id !== selectedDoctor.id) return doc;
        const currentSchedules = doc.schedules || [];
        const existingIdx = currentSchedules.findIndex(
          (s) => s.day_of_week === editingSchedule.dayOfWeek
        );

        let updatedSchedules: DoctorSchedule[];
        if (existingIdx >= 0) {
          updatedSchedules = [...currentSchedules];
          updatedSchedules[existingIdx] = {
            ...updatedSchedules[existingIdx],
            start_time: editingSchedule.startTime,
            end_time: editingSchedule.endTime,
            slot_duration_minutes: editingSchedule.slotDuration,
            is_active: true,
          };
        } else {
          updatedSchedules = [
            ...currentSchedules,
            {
              id: `sched-${Date.now()}`,
              doctor_id: selectedDoctor.id,
              day_of_week: editingSchedule.dayOfWeek,
              start_time: editingSchedule.startTime,
              end_time: editingSchedule.endTime,
              slot_duration_minutes: editingSchedule.slotDuration,
              is_active: true,
            },
          ];
        }

        return { ...doc, schedules: updatedSchedules };
      })
    );

    setEditingSchedule(null);
  };

  const handleCreateDoctor = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newDoctorName) return;

    const newDoc: Doctor = {
      id: `doc-${Date.now()}`,
      clinic_id: "c1",
      name: newDoctorName.startsWith("Dr.") ? newDoctorName : `Dr. ${newDoctorName}`,
      specialization: newSpecialization,
      consultation_fee: Number(newFee) || 500,
      bio: newBio || "Qualified Ayurvedic Practitioner.",
      is_active: true,
      schedules: [
        { id: `s-${Date.now()}-0`, doctor_id: `doc-${Date.now()}`, day_of_week: 0, start_time: "09:00:00", end_time: "17:00:00", slot_duration_minutes: 30, is_active: true },
        { id: `s-${Date.now()}-1`, doctor_id: `doc-${Date.now()}`, day_of_week: 1, start_time: "09:00:00", end_time: "17:00:00", slot_duration_minutes: 30, is_active: true },
        { id: `s-${Date.now()}-2`, doctor_id: `doc-${Date.now()}`, day_of_week: 2, start_time: "09:00:00", end_time: "17:00:00", slot_duration_minutes: 30, is_active: true },
        { id: `s-${Date.now()}-3`, doctor_id: `doc-${Date.now()}`, day_of_week: 3, start_time: "09:00:00", end_time: "17:00:00", slot_duration_minutes: 30, is_active: true },
        { id: `s-${Date.now()}-4`, doctor_id: `doc-${Date.now()}`, day_of_week: 4, start_time: "09:00:00", end_time: "17:00:00", slot_duration_minutes: 30, is_active: true },
      ]
    };

    setDoctors((prev) => [...prev, newDoc]);
    setSelectedDoctorId(newDoc.id);
    setIsNewDoctorModalOpen(false);
    setNewDoctorName("");
    setNewBio("");
  };

  return (
    <div className="space-y-6">
      {/* Page Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl md:text-2xl font-bold text-slate-800 tracking-tight">
            Doctor Timings & Schedule Manager
          </h2>
          <p className="text-xs md:text-sm text-slate-500">
            Configure working hours and slot durations used by the AI voice receptionist for real-time bookings
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsNewDoctorModalOpen(true)}
            className="inline-flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-4 py-2 rounded-xl text-xs transition-colors shadow-xs"
          >
            <UserPlus className="w-4 h-4" />
            <span>Onboard New Doctor</span>
          </button>
        </div>
      </div>

      {/* Main Grid: Doctor Selector & Timetable */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Doctor Profiles Cards */}
        <div className="space-y-4">
          <h3 className="font-semibold text-slate-700 text-sm">Specialist Ayurvedic Doctors</h3>
          {doctors.map((doc) => {
            const isSelected = doc.id === selectedDoctorId;
            return (
              <div
                key={doc.id}
                onClick={() => setSelectedDoctorId(doc.id)}
                className={`p-4 rounded-2xl border transition-all cursor-pointer ${
                  isSelected
                    ? "bg-white border-emerald-500 shadow-md ring-2 ring-emerald-500/10"
                    : "bg-white/70 border-slate-200 hover:bg-white hover:border-slate-300"
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold text-sm">
                      <Stethoscope className="w-5 h-5 text-emerald-700" />
                    </div>
                    <div>
                      <h4 className="font-bold text-slate-800 text-sm">{doc.name}</h4>
                      <p className="text-xs text-emerald-600 font-medium">{doc.specialization}</p>
                    </div>
                  </div>
                  <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-slate-700 bg-slate-100 px-2 py-0.5 rounded-full">
                    <IndianRupee className="w-3 h-3 text-slate-500" />
                    {doc.consultation_fee}
                  </span>
                </div>

                <p className="text-[11px] text-slate-500 mt-3 line-clamp-2 leading-relaxed">
                  {doc.bio || "Registered Ayurvedic Practitioner."}
                </p>

                <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-400">
                  <span className="flex items-center gap-1">
                    <UserCheck className="w-3.5 h-3.5 text-emerald-500" />
                    Active on AI Receptionist
                  </span>
                  <span className="font-medium text-emerald-700">
                    {doc.schedules?.length || 0} Days / Wk
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Right 2 Columns: Weekly Schedule Matrix for Selected Doctor */}
        <div className="lg:col-span-2 space-y-6">
          {selectedDoctor && (
            <div className="bg-white rounded-2xl border border-slate-200/90 p-6 shadow-xs">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-100 gap-2">
                <div>
                  <h3 className="font-bold text-slate-800 text-base">
                    Weekly Timetable: {selectedDoctor.name}
                  </h3>
                  <p className="text-xs text-slate-500">
                    Consultation fee: ₹{selectedDoctor.consultation_fee} • {selectedDoctor.specialization}
                  </p>
                </div>
                <div className="inline-flex items-center gap-1.5 text-xs text-slate-500 bg-slate-100 px-3 py-1 rounded-lg">
                  <ShieldCheck className="w-4 h-4 text-emerald-600" />
                  <span>Slots Auto-synced with ElevenLabs</span>
                </div>
              </div>

              {/* Schedule list by Day of Week */}
              <div className="mt-5 space-y-2.5">
                {DAYS_OF_WEEK.map((dayName, dayIndex) => {
                  const schedule = selectedDoctor.schedules?.find(
                    (s) => s.day_of_week === dayIndex && s.is_active
                  );

                  return (
                    <div
                      key={dayName}
                      className="flex items-center justify-between p-3.5 rounded-xl border border-slate-100 bg-slate-50/70 hover:bg-slate-50 transition-colors"
                    >
                      <div className="w-32 font-semibold text-xs text-slate-800 flex items-center gap-2">
                        <Calendar className="w-3.5 h-3.5 text-slate-400" />
                        <span>{dayName}</span>
                      </div>

                      {schedule ? (
                        <div className="flex-1 flex flex-wrap items-center justify-between gap-3 text-xs">
                          <div className="flex items-center gap-2">
                            <span className="px-2.5 py-1 rounded-md bg-white border border-slate-200 text-slate-800 font-semibold shadow-2xs">
                              {schedule.start_time.slice(0, 5)} - {schedule.end_time.slice(0, 5)}
                            </span>
                            <span className="text-[11px] text-slate-400 font-medium">
                              ({schedule.slot_duration_minutes} min slots)
                            </span>
                          </div>

                          <div className="flex items-center gap-2">
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 uppercase">
                              Available
                            </span>
                            <button
                              onClick={() =>
                                setEditingSchedule({
                                  doctorId: selectedDoctor.id,
                                  dayOfWeek: dayIndex,
                                  startTime: schedule.start_time.slice(0, 5),
                                  endTime: schedule.end_time.slice(0, 5),
                                  slotDuration: schedule.slot_duration_minutes,
                                })
                              }
                              className="p-1 rounded text-slate-400 hover:text-slate-600 hover:bg-slate-200/60"
                            >
                              <Edit3 className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        </div>
                      ) : (
                        <div className="flex-1 flex items-center justify-between text-xs">
                          <span className="text-slate-400 italic text-[11px]">No slots scheduled (Off Duty)</span>
                          <button
                            onClick={() =>
                              setEditingSchedule({
                                doctorId: selectedDoctor.id,
                                dayOfWeek: dayIndex,
                                startTime: "09:00",
                                endTime: "17:00",
                                slotDuration: 30,
                              })
                            }
                            className="text-xs font-semibold text-emerald-600 hover:text-emerald-700 flex items-center gap-1"
                          >
                            <Plus className="w-3 h-3" /> Add Hours
                          </button>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Edit / Add Schedule Form Modal */}
          {editingSchedule && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4 animate-in fade-in">
              <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200">
                <h3 className="font-bold text-slate-800 text-base mb-1">
                  Configure Schedule: {DAYS_OF_WEEK[editingSchedule.dayOfWeek]}
                </h3>
                <p className="text-xs text-slate-500 mb-4">
                  Set the daily consultation hours and slot interval for {selectedDoctor?.name}.
                </p>

                <form onSubmit={handleSaveSchedule} className="space-y-4 text-xs">
                  <div>
                    <label className="block font-medium text-slate-700 mb-1">Day of Week</label>
                    <select
                      value={editingSchedule.dayOfWeek}
                      onChange={(e) =>
                        setEditingSchedule({
                          ...editingSchedule,
                          dayOfWeek: parseInt(e.target.value),
                        })
                      }
                      className="w-full p-2.5 rounded-lg border border-slate-200 bg-slate-50 text-slate-800 font-medium"
                    >
                      {DAYS_OF_WEEK.map((day, idx) => (
                        <option key={day} value={idx}>
                          {day}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block font-medium text-slate-700 mb-1">Start Time</label>
                      <input
                        type="time"
                        value={editingSchedule.startTime}
                        onChange={(e) =>
                          setEditingSchedule({ ...editingSchedule, startTime: e.target.value })
                        }
                        className="w-full p-2.5 rounded-lg border border-slate-200 bg-slate-50 text-slate-800"
                        required
                      />
                    </div>
                    <div>
                      <label className="block font-medium text-slate-700 mb-1">End Time</label>
                      <input
                        type="time"
                        value={editingSchedule.endTime}
                        onChange={(e) =>
                          setEditingSchedule({ ...editingSchedule, endTime: e.target.value })
                        }
                        className="w-full p-2.5 rounded-lg border border-slate-200 bg-slate-50 text-slate-800"
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block font-medium text-slate-700 mb-1">
                      Slot Duration (Minutes)
                    </label>
                    <select
                      value={editingSchedule.slotDuration}
                      onChange={(e) =>
                        setEditingSchedule({
                          ...editingSchedule,
                          slotDuration: parseInt(e.target.value),
                        })
                      }
                      className="w-full p-2.5 rounded-lg border border-slate-200 bg-slate-50 text-slate-800 font-medium"
                    >
                      <option value={15}>15 Minutes</option>
                      <option value={30}>30 Minutes (Recommended)</option>
                      <option value={45}>45 Minutes (Panchakarma Consultation)</option>
                      <option value={60}>60 Minutes (Comprehensive Assessment)</option>
                    </select>
                  </div>

                  <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-100">
                    <button
                      type="button"
                      onClick={() => setEditingSchedule(null)}
                      className="px-4 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold transition-colors flex items-center gap-1.5 shadow-xs"
                    >
                      <Check className="w-4 h-4" />
                      <span>Save Timings</span>
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}

          {/* Onboard Doctor Modal */}
          {isNewDoctorModalOpen && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4 animate-in fade-in">
              <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200">
                <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
                  <h3 className="font-bold text-slate-800 text-base flex items-center gap-2">
                    <UserPlus className="w-4 h-4 text-emerald-600" />
                    <span>Onboard New Ayurvedic Doctor</span>
                  </h3>
                  <button
                    onClick={() => setIsNewDoctorModalOpen(false)}
                    className="p-1 rounded-lg text-slate-400 hover:text-slate-600"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                <form onSubmit={handleCreateDoctor} className="space-y-4 text-xs">
                  <div>
                    <label className="block font-medium text-slate-700 mb-1">Doctor Name</label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. Dr. Ramesh Namboodiri"
                      value={newDoctorName}
                      onChange={(e) => setNewDoctorName(e.target.value)}
                      className="w-full p-2.5 rounded-lg border border-slate-200 bg-slate-50 text-slate-800"
                    />
                  </div>

                  <div>
                    <label className="block font-medium text-slate-700 mb-1">Specialization</label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. Shirodhara & Stress Management"
                      value={newSpecialization}
                      onChange={(e) => setNewSpecialization(e.target.value)}
                      className="w-full p-2.5 rounded-lg border border-slate-200 bg-slate-50 text-slate-800"
                    />
                  </div>

                  <div>
                    <label className="block font-medium text-slate-700 mb-1">Consultation Fee (₹ INR)</label>
                    <input
                      type="number"
                      required
                      min={100}
                      max={10000}
                      step={50}
                      value={newFee}
                      onChange={(e) => setNewFee(Number(e.target.value))}
                      className="w-full p-2.5 rounded-lg border border-slate-200 bg-slate-50 text-slate-800"
                    />
                  </div>

                  <div>
                    <label className="block font-medium text-slate-700 mb-1">Professional Biography</label>
                    <textarea
                      rows={2}
                      placeholder="BAMS degree, clinical focus, years of experience..."
                      value={newBio}
                      onChange={(e) => setNewBio(e.target.value)}
                      className="w-full p-2.5 rounded-lg border border-slate-200 bg-slate-50 text-slate-800"
                    />
                  </div>

                  <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-100">
                    <button
                      type="button"
                      onClick={() => setIsNewDoctorModalOpen(false)}
                      className="px-4 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold flex items-center gap-1.5 shadow-xs"
                    >
                      <Check className="w-4 h-4" />
                      <span>Onboard Doctor</span>
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
