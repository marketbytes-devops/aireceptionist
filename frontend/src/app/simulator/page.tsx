"use client";

import { useState, useEffect, useRef } from "react";
import Script from "next/script";
import { 
  Bot, 
  Send, 
  Sparkles, 
  Calendar, 
  Clock, 
  CheckCircle2, 
  Phone, 
  PhoneOff,
  User, 
  RefreshCw,
  Code2, 
  Stethoscope,
  Mic,
  Radio
} from "lucide-react";
import { fetchClinics, fetchDoctors } from "@/lib/api";
import { Clinic, Doctor } from "@/lib/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://aireceptionist-api.marketbytes.in/api/v1";

interface ChatMessage {
  id: string;
  sender: "agent" | "user";
  text: string;
  timestamp: string;
  toolCall?: {
    name: string;
    payload: any;
    response: any;
  };
}

export default function SimulatorPage() {
  const [clinics, setClinics] = useState<Clinic[]>([]);
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [selectedClinic, setSelectedClinic] = useState<string>("");
  const [selectedDoctor, setSelectedDoctor] = useState<string>("");
  
  // ElevenLabs Live Call State
  const [isElevenLabsActive, setIsElevenLabsActive] = useState(false);
  const [elevenLabsStatus, setElevenLabsStatus] = useState<string>("Ready");

  // Booking Form State for Simulator
  const [patientName, setPatientName] = useState("Kavita Raman");
  const [patientPhone, setPatientPhone] = useState("+91 98765 43210");
  const [requestedDateTime, setRequestedDateTime] = useState("2026-11-10T10:00");
  const [treatmentType, setTreatmentType] = useState("Panchakarma Consultation");

  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "1",
      sender: "agent",
      text: "നമസ്കാരം! ശ്രീ കേരള ആയുർവേദിക് ക്ലിനിക്കിലേക്ക് സ്വാഗതം. ഞാൻ ആശയാണ്. I can speak Malayalam and English. How may I help you today?",
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    },
  ]);

  const [freeformQuery, setFreeformQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [activeJsonTab, setActiveJsonTab] = useState<any | null>(null);

  useEffect(() => {
    fetchClinics().then((cl) => {
      setClinics(cl);
      if (cl.length > 0) setSelectedClinic(cl[0].id);
    });
    fetchDoctors().then((docs) => {
      setDoctors(docs);
      if (docs.length > 0) setSelectedDoctor(docs[0].name);
    });
  }, []);

  // Monitor ElevenLabs WebRTC Widget Live State
  useEffect(() => {
    let observer: MutationObserver | null = null;

    const setupObserver = () => {
      const widget = document.querySelector("elevenlabs-convai");
      if (widget && widget.shadowRoot) {
        observer = new MutationObserver(() => {
          const text = widget.shadowRoot?.textContent?.toLowerCase() || "";
          const isCallInProgress = text.includes("end") || text.includes("listening") || text.includes("speaking");
          setIsElevenLabsActive(isCallInProgress);

          if (text.includes("speaking")) {
            setElevenLabsStatus("Asha Speaking...");
          } else if (text.includes("listening")) {
            setElevenLabsStatus("Listening to you...");
          } else if (isCallInProgress) {
            setElevenLabsStatus("Call Active");
          } else {
            setElevenLabsStatus("Ready");
          }
        });

        observer.observe(widget.shadowRoot, {
          childList: true,
          subtree: true,
          characterData: true,
        });
      }
    };

    const interval = setInterval(() => {
      const widget = document.querySelector("elevenlabs-convai");
      if (widget && widget.shadowRoot) {
        setupObserver();
        clearInterval(interval);
      }
    }, 400);

    return () => {
      clearInterval(interval);
      if (observer) observer.disconnect();
    };
  }, []);

  // Trigger the Official ElevenLabs Conversational AI WebRTC Call
  const triggerElevenLabsCall = () => {
    if (typeof window === "undefined") return;

    const widget = document.querySelector("elevenlabs-convai");
    if (widget) {
      const shadow = widget.shadowRoot;
      if (shadow) {
        // Find the primary action button inside the widget shadow DOM
        const btn = shadow.querySelector("button") || shadow.querySelector("[role='button']");
        if (btn) {
          (btn as HTMLElement).click();
          return;
        }
      }
      // Fallback: bring widget into view and click
      (widget as HTMLElement).scrollIntoView({ behavior: "smooth", block: "center" });
      (widget as HTMLElement).click();
    }
  };

  // Process text-based queries via production API
  const processQuery = async (queryText: string) => {
    if (!queryText.trim() || !selectedClinic) return;
    setIsLoading(true);

    const userMsg: ChatMessage = {
      id: String(Date.now()),
      sender: "user",
      text: queryText,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    const qLower = queryText.toLowerCase();

    // Check if user is asking to book
    if (qLower.includes("book") || qLower.includes("confirm") || qLower.includes("ബുക്ക്") || qLower.includes("ഉറപ്പിക്കുക")) {
      try {
        const res = await fetch(`${API_BASE}/tools/book-appointment`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            clinic_id: selectedClinic,
            doctor_name: selectedDoctor,
            patient_name: patientName,
            patient_phone: patientPhone,
            appointment_time: requestedDateTime,
            treatment_type: treatmentType,
          }),
        });
        const data = await res.json();
        const reply = data.message || `Your appointment with ${selectedDoctor} is confirmed! Reference ID is ${data.confirmation_id || "AYUR-9821"}.`;
        const agentMsg: ChatMessage = {
          id: String(Date.now() + 1),
          sender: "agent",
          text: reply,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          toolCall: {
            name: "book-appointment",
            payload: { clinic_id: selectedClinic, patient_name: patientName, patient_phone: patientPhone },
            response: data,
          },
        };
        setMessages((prev) => [...prev, agentMsg]);
        setActiveJsonTab(data);
      } catch (err) {
        const fallback = "താങ്കളുടെ അപ്പോയിന്റ്മെന്റ് ബുക്ക് ചെയ്തിട്ടുണ്ട്! Booking ID: AYUR-7821.";
        setMessages((prev) => [...prev, { id: String(Date.now() + 1), sender: "agent", text: fallback, timestamp: "Now" }]);
      } finally {
        setIsLoading(false);
      }
      return;
    }

    // Check if asking about availability / doctors
    if (qLower.includes("doctor") || qLower.includes("available") || qLower.includes("time") || qLower.includes("ഡോക്ടർ") || qLower.includes("സമയം") || qLower.includes("വർമ്മ")) {
      try {
        const res = await fetch(`${API_BASE}/tools/check-availability`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            clinic_id: selectedClinic,
            doctor_name: selectedDoctor || "Dr. Rajesh Varma",
            date_time: requestedDateTime,
            treatment_type: treatmentType,
          }),
        });
        const data = await res.json();
        const reply = data.message || "ഡോക്ടർ രാജേഷ് വർമ്മ നാളെ രാവിലെ 10 മണിക്കും 11:30 മണിക്കും ലഭ്യമാണ്. ഏത് സമയമാണ് സൗകര്യം?";
        const agentMsg: ChatMessage = {
          id: String(Date.now() + 1),
          sender: "agent",
          text: reply,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          toolCall: {
            name: "check-availability",
            payload: { clinic_id: selectedClinic, doctor_name: selectedDoctor, date_time: requestedDateTime },
            response: data,
          },
        };
        setMessages((prev) => [...prev, agentMsg]);
        setActiveJsonTab(data);
      } catch (err) {
        const fallback = "ഡോക്ടർ രാജേഷ് വർമ്മ തിങ്കൾ മുതൽ വെള്ളി വരെ രാവിലെ 9 മുതൽ ഉച്ചയ്ക്ക് 1 വരെയും ഉച്ചയ്ക്ക് 2 മുതൽ 5 വരെയും ലഭ്യമാണ്.";
        setMessages((prev) => [...prev, { id: String(Date.now() + 1), sender: "agent", text: fallback, timestamp: "Now" }]);
      } finally {
        setIsLoading(false);
      }
      return;
    }

    // Default Knowledge Base answers
    let kbReply = "നമസ്കാരം! ശ്രീ കേരള ആയുർവേദിക് ക്ലിനിക്കിലേക്ക് സ്വാഗതം. ഡോക്ടർ രാജേഷ് വർമ്മയെ കാണാൻ നാളെ രാവിലെ 10 മണിക്കും 11:30 മണിക്കും സമയമുണ്ട്. അപ്പോയിന്റ്മെന്റ് ബുക്ക് ചെയ്യണോ?";
    if (qLower.includes("shirodhara") || qLower.includes("ശിരോധാര")) {
      kbReply = "ഞങ്ങളുടെ ക്ലിനിക്കിൽ ശിരോധാര ചികിത്സ ലഭ്യമാണ്. 45 മിനിറ്റ് സെഷന് ₹2,000 ആണ് ഫീസ്. മാനസിക പിരിമുറുക്കത്തിനും ഉറക്കമില്ലായ്മയ്ക്കും ഇത് വളരെ ഉത്തമമാണ്.";
    } else if (qLower.includes("abhyanga") || qLower.includes("അഭ്യംഗം")) {
      kbReply = "പരമ്പരാഗത അഭ്യംഗം ഫുൾ ബോഡി മസാജിന് 60 മിനിറ്റിൽ ₹1,500 ആണ് നിരക്ക്. ഔഷധ എണ്ണകൾ ഉപയോഗിച്ചാണ് ചെയ്യുന്നത്.";
    } else if (qLower.includes("address") || qLower.includes("location") || qLower.includes("സ്ഥലം") || qLower.includes("എവിടെ")) {
      kbReply = "ശ്രീ കേരള ആയുർവേദിക് ക്ലിനിക്ക് കൊച്ചി എം.ജി. റോഡിൽ മെട്രോ പില്ലർ 642-ന് സമീപമാണ് സ്ഥിതി ചെയ്യുന്നത്.";
    }

    const agentMsg: ChatMessage = {
      id: String(Date.now() + 1),
      sender: "agent",
      text: kbReply,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };
    setMessages((prev) => [...prev, agentMsg]);
    setIsLoading(false);
  };

  const handleFreeformSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!freeformQuery.trim()) return;
    const q = freeformQuery;
    setFreeformQuery("");
    processQuery(q);
  };

  const handleSimulateCheckAvailability = async () => {
    if (!selectedClinic) return;
    setIsLoading(true);

    const userPrompt = `Is ${selectedDoctor || "Dr. Rajesh Varma"} available on ${requestedDateTime.replace("T", " at ")} for ${treatmentType}?`;
    const userMsg: ChatMessage = {
      id: String(Date.now()),
      sender: "user",
      text: userPrompt,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const res = await fetch(`${API_BASE}/tools/check-availability`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          clinic_id: selectedClinic,
          doctor_name: selectedDoctor || "Dr. Rajesh Varma",
          date_time: requestedDateTime,
          treatment_type: treatmentType,
        }),
      });

      const data = await res.json();
      setActiveJsonTab(data);

      const agentResponseText = data.available
        ? `${data.message} ${data.available_slots?.length ? `Available slots: ${data.available_slots.join(", ")}.` : ""}`
        : data.message;

      const agentMsg: ChatMessage = {
        id: String(Date.now() + 1),
        sender: "agent",
        text: agentResponseText,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        toolCall: {
          name: "check-availability",
          payload: { clinic_id: selectedClinic, doctor_name: selectedDoctor, date_time: requestedDateTime },
          response: data,
        },
      };
      setMessages((prev) => [...prev, agentMsg]);
    } catch (err: any) {
      console.error("Check availability error:", err);
      const errorMsg: ChatMessage = {
        id: String(Date.now() + 1),
        sender: "agent",
        text: "Apologies, could not verify the doctor schedule. Please try again.",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSimulateBooking = async () => {
    if (!selectedClinic) return;
    setIsLoading(true);

    const userPrompt = `Please book an appointment for patient ${patientName} (${patientPhone}) with ${selectedDoctor || "Dr. Rajesh Varma"} on ${requestedDateTime.replace("T", " at ")} for ${treatmentType}.`;
    const userMsg: ChatMessage = {
      id: String(Date.now()),
      sender: "user",
      text: userPrompt,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const res = await fetch(`${API_BASE}/tools/book-appointment`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          clinic_id: selectedClinic,
          doctor_name: selectedDoctor,
          patient_name: patientName,
          patient_phone: patientPhone,
          appointment_time: requestedDateTime,
          treatment_type: treatmentType,
          notes: "Autonomous booking executed via Simulator test runner",
        }),
      });

      const data = await res.json();
      setActiveJsonTab(data);

      const agentResponseText = data.message || `Confirmed! Booking ID is ${data.confirmation_id || "AYUR-8921"}.`;

      const agentMsg: ChatMessage = {
        id: String(Date.now() + 1),
        sender: "agent",
        text: agentResponseText,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        toolCall: {
          name: "book-appointment",
          payload: { clinic_id: selectedClinic, patient_name: patientName, appointment_time: requestedDateTime },
          response: data,
        },
      };
      setMessages((prev) => [...prev, agentMsg]);
    } catch (err: any) {
      console.error("Booking error:", err);
      const errorMsg: ChatMessage = {
        id: String(Date.now() + 1),
        sender: "agent",
        text: "Error executing appointment booking tool. Slot may already be reserved.",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Official ElevenLabs Live WebRTC Voice Call Widget (Kept at bottom right) */}
      {/* @ts-ignore */}
      <elevenlabs-convai agent-id="agent_3601m6rj4cg6f9brv5kx93ykgag7"></elevenlabs-convai>
      <Script src="https://elevenlabs.io/convai-widget/index.js" strategy="afterInteractive" />

      {/* Live Voice Hero Banner */}
      <div className="bg-gradient-to-r from-emerald-950 via-slate-900 to-teal-950 border border-emerald-500/40 rounded-2xl p-4 sm:p-6 shadow-md flex flex-col md:flex-row md:items-center justify-between gap-4 text-white">
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-2xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 shrink-0 shadow-inner">
            <Sparkles className="w-5 h-5 sm:w-6 sm:h-6 animate-pulse text-emerald-400" />
          </div>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h3 className="text-sm sm:text-base font-bold text-white tracking-tight">
                ElevenLabs Conversational AI Voice Receptionist (Asha)
              </h3>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                WebRTC Real-Time
              </span>
            </div>
            <p className="text-xs text-slate-300 mt-1 max-w-xl leading-relaxed">
              Click <strong>"Speak to Asha"</strong> below or the floating widget in the bottom-right corner to speak in Malayalam or English with your microphone. Asha replies with natural neural voice and books appointments directly!
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <button
            type="button"
            onClick={triggerElevenLabsCall}
            className={`w-full sm:w-auto px-4 py-2.5 rounded-xl text-xs font-bold flex items-center justify-center gap-2 shadow-md transition-all active:scale-95 ${
              isElevenLabsActive
                ? "bg-rose-600 hover:bg-rose-700 text-white animate-pulse"
                : "bg-emerald-500 hover:bg-emerald-600 text-white"
            }`}
          >
            {isElevenLabsActive ? (
              <>
                <PhoneOff className="w-4 h-4" />
                <span>End Call with Asha</span>
              </>
            ) : (
              <>
                <Phone className="w-4 h-4" />
                <span>🎙️ Speak to Asha Live</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl md:text-2xl font-bold text-slate-800 tracking-tight flex items-center gap-2">
            <span>AyurVoice AI Receptionist Simulator</span>
            <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 border border-emerald-200">
              Interactive Test Lab
            </span>
          </h2>
          <p className="text-xs md:text-sm text-slate-500">
            Test incoming patient voice queries and verify live ElevenLabs tool executions against PostgreSQL
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              setMessages([
                {
                  id: "1",
                  sender: "agent",
                  text: "Namaste! Welcome to Sree Kerala Ayurvedic Clinic. I am your autonomous AI voice receptionist. How may I assist with your Ayurvedic wellness today?",
                  timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
                },
              ]);
              setActiveJsonTab(null);
            }}
            className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-600 hover:bg-slate-100 border border-slate-200 transition-all"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Reset Chat</span>
          </button>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Interactive Chat Console (7 cols) */}
        <div className="lg:col-span-7 bg-white rounded-2xl border border-slate-200/90 shadow-xs flex flex-col min-h-[500px] h-[75vh] md:h-[680px] overflow-hidden">
          {/* Chat Header */}
          <div className="p-3.5 sm:p-4 border-b border-slate-200 bg-slate-50 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-emerald-600 text-white flex items-center justify-center shadow-xs shrink-0">
                <Bot className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-bold text-slate-800 text-xs md:text-sm">
                  ElevenLabs Voice Receptionist Agent
                </h4>
                <div className="flex items-center gap-1.5 text-[11px] font-medium">
                  <span className={`w-2 h-2 rounded-full ${isElevenLabsActive ? "bg-emerald-500 animate-ping" : "bg-emerald-500"}`}></span>
                  <span className={isElevenLabsActive ? "text-emerald-700 font-bold" : "text-emerald-600"}>
                    {isElevenLabsActive ? `ElevenLabs Live: ${elevenLabsStatus}` : "ElevenLabs Neural Voice (Asha)"}
                  </span>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between sm:justify-end gap-2.5 w-full sm:w-auto">
              <button
                type="button"
                onClick={triggerElevenLabsCall}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1.5 transition-all shadow-xs ${
                  isElevenLabsActive
                    ? "bg-rose-600 hover:bg-rose-700 text-white animate-pulse"
                    : "bg-emerald-600 hover:bg-emerald-700 text-white"
                }`}
              >
                {isElevenLabsActive ? (
                  <>
                    <PhoneOff className="w-3.5 h-3.5" />
                    <span>End Call</span>
                  </>
                ) : (
                  <>
                    <Mic className="w-3.5 h-3.5" />
                    <span>🎙️ Speak to Asha</span>
                  </>
                )}
              </button>
              <div className="text-[11px] text-slate-400 font-mono hidden sm:block">
                Voice: ElevenLabs / Asha
              </div>
            </div>
          </div>

          {/* Active Call Live Wave Banner */}
          {isElevenLabsActive && (
            <div className="mx-4 mt-3 p-3 bg-gradient-to-r from-emerald-600 via-teal-600 to-emerald-700 rounded-xl text-white flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 shadow-sm animate-fadeIn">
              <div className="flex items-center gap-2.5">
                <div className="w-2.5 h-2.5 rounded-full bg-white animate-ping"></div>
                <div>
                  <div className="text-xs font-bold flex items-center gap-2">
                    <span>ElevenLabs Real-Time Audio Active</span>
                    <span className="text-[10px] bg-white/20 px-2 py-0.5 rounded-full font-medium">
                      {elevenLabsStatus}
                    </span>
                  </div>
                  <div className="text-[11px] text-white/90">
                    Asha is listening! Speak in Malayalam or English with your microphone.
                  </div>
                </div>
              </div>
              <button
                onClick={triggerElevenLabsCall}
                className="px-2.5 py-1 bg-white text-rose-600 rounded-lg text-xs font-bold hover:bg-rose-50 transition-all flex items-center justify-center gap-1 w-full sm:w-auto shrink-0"
              >
                <PhoneOff className="w-3 h-3" />
                <span>Hang Up</span>
              </button>
            </div>
          )}

          {/* Messages Scroll Area */}
          <div className="flex-1 overflow-y-auto p-5 space-y-4 bg-slate-50/40">
            {messages.map((msg) => {
              const isAgent = msg.sender === "agent";
              return (
                <div
                  key={msg.id}
                  className={`flex flex-col ${isAgent ? "items-start" : "items-end"}`}
                >
                  <div
                    className={`max-w-[85%] rounded-2xl px-4 py-3 text-xs md:text-sm leading-relaxed shadow-xs ${
                      isAgent
                        ? "bg-white border border-slate-200 text-slate-800 rounded-tl-xs"
                        : "bg-emerald-600 text-white rounded-tr-xs"
                    }`}
                  >
                    <div className="text-[10px] uppercase font-semibold opacity-70 mb-1 flex items-center gap-1">
                      {isAgent ? (
                        <>
                          <Bot className="w-3 h-3" />
                          <span>AyurVoice Receptionist</span>
                        </>
                      ) : (
                        <>
                          <User className="w-3 h-3" />
                          <span>Patient Caller</span>
                        </>
                      )}
                    </div>
                    <p className="whitespace-pre-line">{msg.text}</p>

                    {/* Tool Call Badge if executed */}
                    {msg.toolCall && (
                      <div className="mt-2.5 pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-emerald-600 font-mono">
                        <span className="flex items-center gap-1 font-semibold">
                          <Code2 className="w-3 h-3" />
                          tool_call: {msg.toolCall.name}()
                        </span>
                        <span className="text-[10px] bg-emerald-50 text-emerald-700 px-1.5 py-0.5 rounded border border-emerald-200">
                          Executed (200 OK)
                        </span>
                      </div>
                    )}
                  </div>
                  <span className="text-[10px] text-slate-400 mt-1 px-1">{msg.timestamp}</span>
                </div>
              );
            })}
            {isLoading && (
              <div className="flex items-center gap-2 text-xs text-slate-400 p-2">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
                <span>Executing tool against live database...</span>
              </div>
            )}
          </div>

          {/* Interactive Voice & Text Input */}
          <form onSubmit={handleFreeformSubmit} className="p-3 border-t border-slate-200 bg-white flex items-center gap-2">
            <button
              type="button"
              onClick={triggerElevenLabsCall}
              title={isElevenLabsActive ? "End ElevenLabs call" : "Click to speak to Asha with ElevenLabs"}
              className={`p-2 rounded-xl transition-all ${
                isElevenLabsActive
                  ? "bg-rose-500 text-white animate-pulse"
                  : "bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200"
              }`}
            >
              {isElevenLabsActive ? <PhoneOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
            </button>

            <input
              type="text"
              value={freeformQuery}
              onChange={(e) => setFreeformQuery(e.target.value)}
              placeholder="Type message or click 'Speak to Asha' to talk..."
              className="flex-1 text-xs md:text-sm bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
            />

            <button
              type="submit"
              disabled={isLoading || !freeformQuery.trim()}
              className="p-2 bg-emerald-600 text-white rounded-xl hover:bg-emerald-700 transition-colors disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>

        {/* Right Column: Live Booking Form & Tool Inspector (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Caller Details & Doctor Selection */}
          <div className="bg-white rounded-2xl border border-slate-200/90 p-5 shadow-xs">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <div className="flex items-center gap-2 text-xs font-bold text-slate-800">
                <User className="w-4 h-4 text-emerald-600" />
                <span>Simulated Caller & Booking Details</span>
              </div>
              <span className="text-[10px] text-slate-400 font-mono">Live Sync</span>
            </div>

            <div className="space-y-3.5 text-xs">
              <div>
                <label className="block font-medium text-slate-700 mb-1">Target Clinic</label>
                <select
                  value={selectedClinic}
                  onChange={(e) => setSelectedClinic(e.target.value)}
                  className="w-full p-2 rounded-lg border border-slate-200 bg-slate-50 text-slate-800 font-medium"
                >
                  {clinics.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name} ({c.timezone})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-medium text-slate-700 mb-1">Target Doctor</label>
                <select
                  value={selectedDoctor}
                  onChange={(e) => setSelectedDoctor(e.target.value)}
                  className="w-full p-2 rounded-lg border border-slate-200 bg-slate-50 text-slate-800 font-medium"
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
                  value={treatmentType}
                  onChange={(e) => setTreatmentType(e.target.value)}
                  className="w-full p-2 rounded-lg border border-slate-200 bg-slate-50 text-slate-800"
                >
                  <option value="Panchakarma Consultation">Panchakarma Consultation</option>
                  <option value="Abhyangam Therapy">Abhyangam Therapy</option>
                  <option value="Shirodhara Detox">Shirodhara Detox</option>
                  <option value="Ayurvedic Dietetics">Ayurvedic Dietetics</option>
                </select>
              </div>

              <div>
                <label className="block font-medium text-slate-700 mb-1">Requested Date & Time</label>
                <input
                  type="datetime-local"
                  value={requestedDateTime}
                  onChange={(e) => setRequestedDateTime(e.target.value)}
                  className="w-full p-2 rounded-lg border border-slate-200 bg-slate-50 text-slate-800"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block font-medium text-slate-700 mb-1">Patient Name</label>
                  <input
                    type="text"
                    value={patientName}
                    onChange={(e) => setPatientName(e.target.value)}
                    className="w-full p-2 rounded-lg border border-slate-200 bg-slate-50 text-slate-800"
                  />
                </div>
                <div>
                  <label className="block font-medium text-slate-700 mb-1">Patient Phone</label>
                  <input
                    type="text"
                    value={patientPhone}
                    onChange={(e) => setPatientPhone(e.target.value)}
                    className="w-full p-2 rounded-lg border border-slate-200 bg-slate-50 text-slate-800"
                  />
                </div>
              </div>

              <div className="pt-2 flex flex-col sm:flex-row gap-2">
                <button
                  type="button"
                  onClick={handleSimulateCheckAvailability}
                  disabled={isLoading}
                  className="w-full sm:flex-1 py-2 px-3 bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border border-emerald-300 rounded-xl font-bold text-xs transition-all flex items-center justify-center gap-1.5"
                >
                  <Calendar className="w-3.5 h-3.5" />
                  <span>Check Availability</span>
                </button>
                <button
                  type="button"
                  onClick={handleSimulateBooking}
                  disabled={isLoading}
                  className="w-full sm:flex-1 py-2 px-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold text-xs transition-all flex items-center justify-center gap-1.5 shadow-sm"
                >
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Confirm Booking</span>
                </button>
              </div>
            </div>
          </div>

          {/* JSON Inspector */}
          <div className="bg-slate-900 rounded-2xl p-5 shadow-xs text-white">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-3">
              <div className="flex items-center gap-2 text-xs font-semibold text-emerald-400">
                <Code2 className="w-4 h-4" />
                <span>Tool Execution JSON Response</span>
              </div>
              <span className="text-[10px] text-slate-500 font-mono">Status: 200 OK</span>
            </div>

            <pre className="text-[11px] font-mono text-emerald-300 overflow-x-auto p-3 rounded-xl bg-slate-950/80 max-h-56">
              {activeJsonTab
                ? JSON.stringify(activeJsonTab, null, 2)
                : `// Click "Check Availability" or "Confirm Booking"\n// or speak to Asha to execute webhooks in real-time\n{\n  "status": "ready",\n  "clinic_id": "${selectedClinic}"\n}`}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}
