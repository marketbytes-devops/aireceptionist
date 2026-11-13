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

const DEFAULT_SREERUDRA_KB = `================================================================================
🏥 SREERUDRA AYURVEDA MULTI SPECIALITY HOSPITAL RESEARCH CENTRE
ശ്രീരുദ്ര ആയുർവേദ മൾട്ടി സ്പെഷ്യാലിറ്റി ഹോസ്പിറ്റൽ റിസർച്ച് സെന്റർ
MASTER HOSPITAL KNOWLEDGE BASE & CLINICAL DIRECTORY
================================================================================

1. EXECUTIVE SUMMARY & IDENTITY
- Official Legal Name: Sreerudra Ayurveda Multi Speciality Hospital Research Centre
- Short Name: Sreerudra Ayurveda
- Founded In: 2002 (over 20+ years of clinical service)
- Accreditation: NABH-Accredited (National Accreditation Board for Hospitals & Healthcare Providers)
- Heritage & Lineage: Rooted in the celebrated Kudalmana family tradition of Kerala, historically renowned for Ayurveda, Vedic scholarship, Sanskrit treatises, and traditional healing systems.
- Healing Philosophy: Seamless integration of classical Kerala Ayurveda, authentic Panchakarma, and Yoga therapy with modern medical diagnostic investigations. Treatments target the root cause of diseases by restoring the balance of the Tridoshas (Vata, Pitta, Kapha) and enhancing Ojas (vital energy).
- Patients Served: 5,000+ satisfied domestic and international patients (from USA, UK, UAE, Singapore, Europe, etc.).
- Official Website: https://www.sreerudraayurveda.com
- Official Email: info@sreerudraayurveda.com / email@sreerudraayurveda.com
- Central Helpline / Phone: +91 90379 03333

2. HOSPITAL BRANCHES & CONTACT DIRECTORY
📍 Branch 1: Alappuzha (Alleppey) — Main Hospital Campus & Research Centre
- Address: Sreerudra Ayurveda Multi-Speciality Hospital, Kaithavana, Alappuzha, Kerala – 688003, India.
- Landmark: Located behind Kaithavana Church (peaceful lakeside setting, 10 mins drive from Alappuzha town center & railway station).
- Landline Phone: +91 477 2266778 | Mobile / WhatsApp: +91 98479 48218
- Facilities: Full In-Patient (IPD) wards, peaceful recovery rooms, specialized Panchakarma therapy suites, in-house customized Ayurvedic diet kitchen, round-the-clock nursing.

📍 Branch 2: Thiruvananthapuram (Trivandrum) — Hospital Campus
- Address: Sreerudra Ayurveda Multi-Speciality Hospital, Kallampally, Sreekariyam, Thiruvananthapuram (Trivandrum), Kerala – 695017, India.
- Landmark: Kallampally, Sreekariyam (accessible via public transport, railway station, & Trivandrum International Airport).
- Landline Phone: +91 471 2590045 | Mobile / WhatsApp: +91 95677 48218
- Facilities: Full In-Patient (IPD) & Out-Patient (OPD) care, therapy suites, doctor consultation chambers.

📍 Clinical Consultation & Regional Hubs:
- Kochi (Ernakulam): Dedicated Ayurvedic consultation clinic catering to patients from Kakkanad, Edappally, Aluva, Vyttila, and Tripunithura.

3. MEDICAL LEADERSHIP & DOCTORS TEAM
1. Dr. K. S. Vishnu Nampoothiry
- Designation: Founder, Chairman, Patron & Medical Director
- Qualifications: BAMS, MD (Ayurveda), PGDYT, MSc Yoga
- Credentials: Kudalmana Ayurvedic lineage, 20+ years experience, Senior Medical Officer (Alappuzha), AMAI State President.
- Specializations: Ayurvedic Oncology (Cancer Supportive Care), Classical Panchakarma, Neurological Rehabilitation & Stroke Recovery, Severe Spine & Musculoskeletal disorders. Prior appointment mandatory!
- Consultation Fee: ₹750

2. Dr. Maya Lakshmi Vishnu Nampoothiry
- Designation: Managing Director
- Qualifications: M.Sc, MBA, B.Ed, Ph.D
- Role: Hospital administration, patient-centered care systems, treatment coordination.

3. Dr. Rabith K. Rajan
- Designation: Chief Physician
- Qualifications: BAMS, PGDYT
- Specializations: General Ayurvedic Medicine, Panchakarma therapy, Yoga therapy, In-Patient clinical management.
- Consultation Fee: ₹500

4. Dr. Amritha R. S.
- Designation: Senior Consultant – Proctology & Orthopaedics
- Qualifications: MS (Ayurveda)
- Specializations: Ayurvedic Proctology (Anorectal disorders), Orthopaedic care, Joint diseases, Arthritis, Spine disorders.
- Consultation Fee: ₹500

5. Dr. Reshma Paul
- Designation: Consultant – Siddha & Ayurvedic Medicine
- Qualifications: BAMS
- Specializations: Dermatology (Psoriasis, Eczema, Vitiligo), Systemic herbal medicine, Siddha integration.
- Consultation Fee: ₹450

6. Dr. Muhammed Hashim A. P.
- Designation: Consultant Proctologist (Ksharasoothra Specialist)
- Qualifications: BAMS, PGD Kshara Karma
- Specializations: Ksharasoothra and Kshara Karma treatments for Anal Fistula, Anal Fissure, Pilonidal Sinus, and Hemorrhoids/Piles.
- Consultation Fee: ₹500

7. Dr. Abdul Rasheed
- Designation: Senior Consultant – General Medicine
- Qualifications: Rtd. Joint Director, ISM (Indian Systems of Medicine)
- Specializations: Comprehensive internal medicine, Geriatric healthcare, Metabolic & lifestyle disorders.
- Consultation Fee: ₹500

4. CLINICAL SPECIALTIES & TREATMENTS
🧬 1. Ayurvedic Oncology (Cancer Supportive Care)
- Physician-led integrative care under Dr. K. S. Vishnu Nampoothiry.
- Improves quality of life, maintains Ojas/immunity, reduces chemo/radiation side effects, alleviates fatigue/pain.
- Cancers managed: Breast, prostate, thyroid, gastrointestinal, lung, and testicular cancers.

🦴 2. Spine, Joint & Orthopaedic Care
- Conditions: Low back pain, Cervical Spondylosis, Slip Disc, Spinal Stenosis, Sciatica, Osteoarthritis, Ankylosing Spondylitis, Rheumatoid Arthritis, Gout, Frozen Shoulder.
- Key Procedures: Kati Vasti, Greeva Vasti, Janu Vasti, Elakizhi, Podikizhi, Pizhichil, Lepanam.

🧠 3. Neurology, Stroke Rehab & Mental Health
- Conditions: Post-stroke paralysis rehab, Parkinson's Disease, Multiple Sclerosis (MS), Dementia, Trigeminal Neuralgia, Migraine, Vertigo, Insomnia, Stress, Anxiety & Depression.
- Procedures: Shirodhara, Shirovasti, Nasyam, Medhya Rasayanas, Yoga & Pranayama.

👶 4. Pediatrics & Neurodevelopmental Care (Autism)
- Holistic management for Autism Spectrum Disorder (ASD) and developmental delays using Medhya Ghritas, Nasya, Shirodhara, and Yoga therapy.

🩺 5. Proctology & Anorectal Clinic (Ksharasoothra)
- Classical non-surgical Ksharasoothra (medicated thread) therapy for Anal Fistula, Fissure, Pilonidal Sinus, and Piles with very low recurrence.

🌿 6. Dermatology & Cosmetology
- Psoriasis, Eczema, Vitiligo, Urticaria, Lipoma, Allergic Dermatitis, Hair fall treatments, anti-pigmentation skin care.

🩸 7. Metabolic & Lifestyle Disorders
- Weight loss / Obesity management (Udvartanam), Diabetes Mellitus, Hypertension, High Cholesterol, Thyroid disorders, Fatty Liver.

🌸 8. Women's Health (Gynecology & Obstetrics)
- PCOD/PCOS, Fibroids, Infertility, Post-Natal Care (Prasava Raksha - 28/45-day mother & newborn recovery).

🍃 9. Classical Panchakarma & Rejuvenation
- 5 Detox Therapies: Vamana, Virechana, Vasti/Basti, Nasya, Raktamokshana.
- Wellness packages: Abhyanga, Shirodhara, Pizhichil, Njavarakizhi, Kayakalpa anti-aging.

5. IN-PATIENT (IPD) FACILITIES & PATIENT CARE
- Accommodation: Clean, ventilated private and shared recovery rooms in peaceful lakeside (Alappuzha) and tranquil (Trivandrum) campuses.
- Customized Diet (Pathya Ahara): Wholesome vegetarian meals planned for each patient according to disease, digestive Agni, and Tridosha balance.
- International & Outstation Support: Airport transfers, pre-arrival tele-consultation, customized packages (7, 14, 21, or 28 days).

6. PATIENT BOOKING INFORMATION
Required fields collected for booking:
1. Patient Full Name
2. Phone / WhatsApp Number
3. Current City / Location
4. Health Complaint / Treatment Required
5. Preferred Branch: Alappuzha, Trivandrum, or Kochi Clinic
6. Mode: In-Person OPD Visit, In-Patient (IPD) Stay, or Video Tele-Consultation
7. Preferred Date & Time`;

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
      if (data.knowledge_base && data.knowledge_base.trim()) {
        setKbText(data.knowledge_base);
      } else {
        setKbText(DEFAULT_SREERUDRA_KB);
      }
    } catch (err: any) {
      console.error("Error loading knowledge base:", err);
      setKbText(DEFAULT_SREERUDRA_KB);
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
    setKbText(DEFAULT_SREERUDRA_KB);
    setStatusMessage({
      type: "success",
      text: "Master template loaded into editor. Click 'Save & Sync' to update the clinic."
    });
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-4 sm:p-6 rounded-2xl shadow-sm">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <BookOpen className="w-5 h-5" />
            </div>
            <h1 className="text-lg sm:text-xl font-bold text-white tracking-tight">
              Hospital Knowledge Base & AI Brain
            </h1>
            <span className="text-[10px] sm:text-xs px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-medium">
              Real-Time Sync
            </span>
          </div>
          <p className="text-xs sm:text-sm text-slate-400">
            Add your hospital details, doctor schedules, treatments, pricing, and rules. When patients call, the AI answers in Malayalam and English using this data.
          </p>
        </div>

        {/* Clinic Selector & Save Button */}
        <div className="flex flex-wrap items-center gap-2.5">
          <div className="flex items-center gap-2 bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 flex-1 sm:flex-none">
            <Building2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <select
              value={selectedClinic}
              onChange={handleClinicChange}
              className="bg-transparent text-xs sm:text-sm text-slate-200 outline-none cursor-pointer w-full"
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
            className="flex items-center justify-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-semibold text-xs sm:text-sm transition-all shadow-lg shadow-emerald-950/40 disabled:opacity-50 flex-1 sm:flex-none"
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
        <div className="flex flex-col sm:flex-row sm:items-center justify-between p-3.5 sm:px-6 sm:py-4 border-b border-slate-800 bg-slate-950/40 gap-3">
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

          <div className="flex flex-wrap items-center gap-2 sm:gap-3">
            {/* File Upload Button */}
            <label className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 cursor-pointer transition-all">
              <Upload className="w-3.5 h-3.5 text-emerald-400" />
              <span>Upload (.txt)</span>
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

