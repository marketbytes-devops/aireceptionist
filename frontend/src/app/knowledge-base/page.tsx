"use client";

import { useState, useEffect } from "react";
import { 
  BookOpen, 
  Sparkles, 
  Save, 
  Upload, 
  RefreshCw, 
  CheckCircle2, 
  AlertCircle, 
  Bot, 
  Phone, 
  Mic, 
  Volume2, 
  Building2, 
  Stethoscope, 
  FileText,
  Clock,
  MapPin,
  IndianRupee,
  HelpCircle
} from "lucide-react";
import { fetchClinics, fetchKnowledgeBase, updateKnowledgeBase } from "@/lib/api";
import { Clinic } from "@/lib/types";

export default function KnowledgeBasePage() {
  const [clinics, setClinics] = useState<Clinic[]>([]);
  const [selectedClinic, setSelectedClinic] = useState<string>("");
  const [kbText, setKbText] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [statusMessage, setStatusMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);
  const [activeTab, setActiveTab] = useState<"editor" | "preview">("editor");

  // Load clinic & knowledge base
  useEffect(() => {
    fetchClinics().then((cl) => {
      setClinics(cl);
      if (cl.length > 0) {
        setSelectedClinic(cl[0].id);
        loadKnowledgeBase(cl[0].id);
      } else {
        setIsLoading(false);
      }
    });
  }, []);

  const loadKnowledgeBase = async (clinicId: string) => {
    setIsLoading(true);
    setStatusMessage(null);
    try {
      const data = await fetchKnowledgeBase(clinicId);
      setKbText(data.knowledge_base || "");
    } catch (err: any) {
      console.error("Error loading knowledge base:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClinicChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newId = e.target.value;
    setSelectedClinic(newId);
    loadKnowledgeBase(newId);
  };

  const handleSaveAndSync = async () => {
    if (!selectedClinic) return;
    setIsSaving(true);
    setStatusMessage(null);
    try {
      const res = await updateKnowledgeBase(selectedClinic, kbText, true);
      setStatusMessage({
        type: "success",
        text: res.message || "Knowledge Base successfully saved and synced to AI Receptionist!"
      });
    } catch (err: any) {
      setStatusMessage({
        type: "error",
        text: "Failed to sync knowledge base. Please check backend connection."
      });
    } finally {
      setIsSaving(false);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result as string;
      if (content) {
        setKbText((prev) => prev ? `${prev}\n\n--- UPLOADED FILE: ${file.name} ---\n${content}` : content);
        setStatusMessage({
          type: "success",
          text: `File "${file.name}" loaded into the editor. Click "Save & Sync" to push to AI.`
        });
      }
    };
    reader.readAsText(file);
  };

  const loadTemplate = () => {
    const template = `================================================================================
SREE KERALA AYURVEDIC CLINIC - OFFICIAL KNOWLEDGE BASE & CLINIC GUIDE
ശ്രീ കേരള ആയുർവേദിക് ക്ലിനിക്ക് - ഔദ്യോഗിക വിവരങ്ങൾ
================================================================================

1. GENERAL CLINIC INFORMATION (ക്ലിനിക്ക് വിവരങ്ങൾ)
- Clinic Name: Sree Kerala Ayurvedic Clinic (ശ്രീ കേരള ആയുർവേദിക് ക്ലിനിക്ക്)
- Location: MG Road, Near Metro Pillar 642, Kochi, Kerala - 682016
- Contact Phone: +1 (757) 914-3149
- Working Hours:
  * Monday to Saturday: 9:00 AM to 7:00 PM
  * Sunday: 9:00 AM to 1:00 PM
- Payment Methods: UPI (Google Pay, PhonePe), Credit/Debit Cards, Cash.

2. DOCTORS & SPECIALISTS (ഡോക്ടർമാരും സമയക്രമവും)
Dr. Rajesh Varma (ഡോക്ടർ രാജേഷ് വർമ്മ):
- Role: Chief Ayurvedic Physician & Senior Vaidya
- Specialization: Classical Panchakarma, Nadi Pariksha (Pulse Diagnosis / നാഡി പരീക്ഷ), Arthritis, Cervical Spondylosis, and Joint Pain.
- Consultation Fee: ₹500
- Visiting Days: Monday to Friday
- Timings: 9:00 AM – 1:00 PM and 2:00 PM – 5:00 PM

Dr. Ananya Nair (ഡോക്ടർ അനന്യ നായർ):
- Role: Ayurvedic Wellness Consultant
- Specialization: Skin Care (Psoriasis, Eczema), Hair Fall, Dietetics, and Stress Management.
- Consultation Fee: ₹450
- Visiting Days: Monday, Wednesday, Friday, Saturday
- Timings: 10:00 AM – 4:00 PM

3. POPULAR AYURVEDIC TREATMENTS (ചികിത്സകൾ)
- Abhyanga (അഭ്യംഗം): Full body medicated herbal oil massage | Duration: 60 mins | Fee: ₹1,500
- Shirodhara (ശിരോധാര): Warm herbal oil therapy on forehead for stress & insomnia | Duration: 45 mins | Fee: ₹2,000
- Elakizhi / Podikizhi (ഇലക്കിഴി / പൊടിക്കിഴി): Herbal pouch therapy for back pain and spondylosis | Duration: 50 mins | Fee: ₹1,800
- Panchakarma Full Detox (പഞ്ചകർമ്മം): 7-Day Package (₹14,000) / 14-Day Package (₹26,000)

4. APPOINTMENT POLICIES (നിബന്ധനകൾ)
- Prior booking is required.
- Please arrive 10 minutes before the appointment time.
- Cancellation: Free if cancelled at least 2 hours in advance.`;

    setKbText(template);
  };

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-sm">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <BookOpen className="w-5 h-5" />
            </div>
            <h1 className="text-xl font-bold text-white tracking-tight">
              Hospital Knowledge Base & AI Brain
            </h1>
            <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-medium">
              Real-Time Sync
            </span>
          </div>
          <p className="text-sm text-slate-400">
            Add your hospital details, doctor schedules, treatments, pricing, and rules. When patients call, the AI answers in Malayalam and English using this data.
          </p>
        </div>

        {/* Clinic Selector & Save Button */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-slate-800 border border-slate-700 rounded-xl px-3 py-1.5">
            <Building2 className="w-4 h-4 text-emerald-400" />
            <select
              value={selectedClinic}
              onChange={handleClinicChange}
              className="bg-transparent text-sm text-slate-200 outline-none cursor-pointer"
            >
              {clinics.map((c) => (
                <option key={c.id} value={c.id} className="bg-slate-900 text-slate-200">
                  {c.name}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={handleSaveAndSync}
            disabled={isSaving || isLoading}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-medium text-sm transition-all shadow-lg shadow-emerald-950/40 disabled:opacity-50"
          >
            {isSaving ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Save className="w-4 h-4" />
            )}
            <span>{isSaving ? "Syncing..." : "Save & Sync to AI"}</span>
          </button>
        </div>
      </div>

      {/* Status Alert Banner */}
      {statusMessage && (
        <div
          className={`p-4 rounded-xl border flex items-center gap-3 text-sm transition-all ${
            statusMessage.type === "success"
              ? "bg-emerald-950/40 border-emerald-500/40 text-emerald-300"
              : "bg-rose-950/40 border-rose-500/40 text-rose-300"
          }`}
        >
          {statusMessage.type === "success" ? (
            <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
          ) : (
            <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />
          )}
          <span>{statusMessage.text}</span>
        </div>
      )}

      {/* Quick In-Browser Voice Test Banner */}
      <div className="bg-gradient-to-r from-emerald-950/40 via-slate-900 to-teal-950/40 border border-emerald-500/30 rounded-2xl p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shrink-0">
            <Mic className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">
              Test by Speaking Directly in Browser
            </h3>
            <p className="text-xs text-slate-400">
              Speak into your microphone in Malayalam or English to test how Asha answers your newly updated facts.
            </p>
          </div>
        </div>
        <a
          href="/simulator"
          className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold border border-slate-700 transition-all shrink-0"
        >
          <Bot className="w-4 h-4 text-emerald-400" />
          <span>Open AI Voice Simulator</span>
        </a>
      </div>

      {/* Main Knowledge Base Editor Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-sm overflow-hidden">
        {/* Editor Toolbar */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/40">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setActiveTab("editor")}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeTab === "editor"
                  ? "bg-slate-800 text-white border border-slate-700"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              Knowledge Editor
            </button>
            <button
              onClick={() => setActiveTab("preview")}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeTab === "preview"
                  ? "bg-slate-800 text-white border border-slate-700"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              Formatted Preview
            </button>
          </div>

          <div className="flex items-center gap-3">
            {/* File Upload Button */}
            <label className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 cursor-pointer transition-all">
              <Upload className="w-3.5 h-3.5 text-emerald-400" />
              <span>Upload Document (.txt)</span>
              <input
                type="file"
                accept=".txt,.md,.json"
                onChange={handleFileUpload}
                className="hidden"
              />
            </label>

            {/* Load Default Template */}
            <button
              onClick={loadTemplate}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 transition-all"
            >
              <Sparkles className="w-3.5 h-3.5 text-teal-400" />
              <span>Load Template</span>
            </button>
          </div>
        </div>

        {/* Editor / Preview Body */}
        {isLoading ? (
          <div className="p-16 flex flex-col items-center justify-center space-y-3 text-slate-500">
            <RefreshCw className="w-8 h-8 animate-spin text-emerald-500" />
            <p className="text-sm">Loading clinic knowledge base...</p>
          </div>
        ) : activeTab === "editor" ? (
          <div className="p-6">
            <textarea
              value={kbText}
              onChange={(e) => setKbText(e.target.value)}
              placeholder="Paste or write your hospital details, doctor qualifications, visiting hours, treatment prices, and clinic policies here..."
              rows={22}
              className="w-full bg-slate-950 text-slate-200 text-sm font-mono p-4 rounded-xl border border-slate-800 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 outline-none leading-relaxed resize-y"
            />
            <div className="mt-3 flex items-center justify-between text-xs text-slate-400 px-1">
              <span>{kbText.length} characters • Bilingual Malayalam & English supported</span>
              <span>All updates sync to inbound phone calls & in-browser simulator</span>
            </div>
          </div>
        ) : (
          <div className="p-8 prose prose-invert max-w-none text-slate-300 font-sans text-sm leading-relaxed whitespace-pre-wrap">
            {kbText || "No knowledge base content available. Switch to Editor to add details."}
          </div>
        )}
      </div>

      {/* Guide Card: How Asha Uses This Data */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-2">
          <div className="flex items-center gap-2 text-emerald-400 text-sm font-semibold">
            <Building2 className="w-4 h-4" />
            <span>Clinic & Timings</span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            When callers ask "Where are you located?" or "What are your Sunday hours?", Asha answers directly in Malayalam or English with your exact address and timings.
          </p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-2">
          <div className="flex items-center gap-2 text-teal-400 text-sm font-semibold">
            <Stethoscope className="w-4 h-4" />
            <span>Doctors & Treatments</span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Specialists, fees, and packages (e.g. Shirodhara, Abhyanga) are answered accurately without making up imaginary prices or services.
          </p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-2">
          <div className="flex items-center gap-2 text-amber-400 text-sm font-semibold">
            <Phone className="w-4 h-4" />
            <span>Inbound Calling</span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Calls to your Twilio number <strong className="text-slate-200">+1 (757) 914-3149</strong> instantly inherit these changes the second you click "Save & Sync".
          </p>
        </div>
      </div>
    </div>
  );
}

