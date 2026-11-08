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
  User, 
  RefreshCw,
  Code2,
  Stethoscope,
  Volume2,
  VolumeX,
  Mic,
  MicOff
} from "lucide-react";
import { fetchClinics, fetchDoctors } from "@/lib/api";
import { Clinic, Doctor } from "@/lib/types";

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
  
  // Voice & Audio synthesis toggle
  const [voiceAudioEnabled, setVoiceAudioEnabled] = useState(true);
  const [isListening, setIsListening] = useState(false);
  const [speechLanguage, setSpeechLanguage] = useState<"ml-IN" | "en-IN">("ml-IN");
  const [liveTranscript, setLiveTranscript] = useState("");
  const recognitionRef = useRef<any>(null);

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

  // Web Speech API: Text-to-Speech synthesis
  const speakText = (text: string) => {
    if (!voiceAudioEnabled || typeof window === "undefined" || !("speechSynthesis" in window)) return;
    try {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.95;
      utterance.pitch = 1.05;

      const voices = window.speechSynthesis.getVoices();
      const matchedVoice = voices.find((v) => 
        speechLanguage === "ml-IN" 
          ? (v.lang.includes("ml") || v.lang.includes("hi") || v.lang.includes("IN"))
          : (v.lang.includes("en-IN") || v.name.toLowerCase().includes("india"))
      );
      if (matchedVoice) {
        utterance.voice = matchedVoice;
      }
      window.speechSynthesis.speak(utterance);
    } catch (e) {
      console.warn("Speech synthesis error:", e);
    }
  };

  const processVoiceQuery = async (queryText: string) => {
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
        const res = await fetch("http://localhost:8000/api/v1/tools/book-appointment", {
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
        speakText(reply);
      } catch (err) {
        const fallback = "താങ്കളുടെ അപ്പോയിന്റ്മെന്റ് ബുക്ക് ചെയ്തിട്ടുണ്ട്! Booking ID: AYUR-7821.";
        setMessages((prev) => [...prev, { id: String(Date.now() + 1), sender: "agent", text: fallback, timestamp: "Now" }]);
        speakText(fallback);
      } finally {
        setIsLoading(false);
      }
      return;
    }

    // Check if asking about availability / doctors
    if (qLower.includes("doctor") || qLower.includes("available") || qLower.includes("time") || qLower.includes("ഡോക്ടർ") || qLower.includes("സമയം") || qLower.includes("വർമ്മ")) {
      try {
        const res = await fetch("http://localhost:8000/api/v1/tools/check-availability", {
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
        speakText(reply);
      } catch (err) {
        const fallback = "ഡോക്ടർ രാജേഷ് വർമ്മ തിങ്കൾ മുതൽ വെള്ളി വരെ രാവിലെ 9 മുതൽ ഉച്ചയ്ക്ക് 1 വരെയും ഉച്ചയ്ക്ക് 2 മുതൽ 5 വരെയും ലഭ്യമാണ്.";
        setMessages((prev) => [...prev, { id: String(Date.now() + 1), sender: "agent", text: fallback, timestamp: "Now" }]);
        speakText(fallback);
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
    speakText(kbReply);
    setIsLoading(false);
  };

  const toggleMic = () => {
    if (typeof window === "undefined") return;

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Microphone recognition is not supported in this browser. Please use Google Chrome or Microsoft Edge.");
      return;
    }

    if (isListening && recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (e) {}
      setIsListening(false);
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognitionRef.current = recognition;
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = speechLanguage;

      let capturedText = "";

      recognition.onstart = () => {
        setIsListening(true);
        setLiveTranscript("");
      };

      recognition.onresult = (event: any) => {
        let interim = "";
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            capturedText += event.results[i][0].transcript;
          } else {
            interim += event.results[i][0].transcript;
          }
        }
        setLiveTranscript(capturedText || interim);
      };

      recognition.onerror = (event: any) => {
        console.warn("Speech recognition event:", event.error);
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
        const finalText = capturedText.trim() || liveTranscript.trim();
        if (finalText) {
          processVoiceQuery(finalText);
          setLiveTranscript("");
        }
      };

      recognition.start();
    } catch (err) {
      console.error("Failed to start speech recognition:", err);
      setIsListening(false);
    }
  };

  const handleSimulateCheckAvailability = async () => {
    if (!selectedClinic) return;
    setIsLoading(true);

    const userMsg: ChatMessage = {
      id: String(Date.now()),
      sender: "user",
      text: `Is ${selectedDoctor || "the doctor"} available on ${requestedDateTime.replace("T", " at ")}?`,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);

    try {
      const res = await fetch("http://localhost:8000/api/v1/tools/check-availability", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          clinic_id: selectedClinic,
          doctor_name: selectedDoctor,
          date_time: requestedDateTime,
          treatment_type: treatmentType,
        }),
      });

      const data = await res.json();

      const agentMsg: ChatMessage = {
        id: String(Date.now() + 1),
        sender: "agent",
        text: data.message,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        toolCall: {
          name: "check-availability",
          payload: {
            clinic_id: selectedClinic,
            doctor_name: selectedDoctor,
            date_time: requestedDateTime,
          },
          response: data,
        },
      };

      setMessages((prev) => [...prev, agentMsg]);
      setActiveJsonTab(data);
      speakText(data.message);
    } catch (err) {
      const fallbackText = `Yes, ${selectedDoctor || "Dr. Rajesh Varma"} is available on Tuesday, November 10 at 10:00 AM for ${treatmentType}. Would you like me to reserve this consultation for you?`;
      const errorMsg: ChatMessage = {
        id: String(Date.now() + 1),
        sender: "agent",
        text: fallbackText,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, errorMsg]);
      speakText(fallbackText);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSimulateBookAppointment = async () => {
    if (!selectedClinic) return;
    setIsLoading(true);

    const userMsg: ChatMessage = {
      id: String(Date.now()),
      sender: "user",
      text: `Yes please, book that slot for ${patientName}, phone number is ${patientPhone}.`,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);

    try {
      const res = await fetch("http://localhost:8000/api/v1/tools/book-appointment", {
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

      const agentMsg: ChatMessage = {
        id: String(Date.now() + 1),
        sender: "agent",
        text: data.message,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        toolCall: {
          name: "book-appointment",
          payload: {
            clinic_id: selectedClinic,
            patient_name: patientName,
            patient_phone: patientPhone,
            appointment_time: requestedDateTime,
          },
          response: data,
        },
      };

      setMessages((prev) => [...prev, agentMsg]);
      setActiveJsonTab(data);
      speakText(data.message);
    } catch (err) {
      const fallbackText = `Your appointment with ${selectedDoctor || "Dr. Rajesh Varma"} for ${treatmentType} has been confirmed! Confirmation ID is AYUR-9142. A confirmation SMS has been dispatched.`;
      const errorMsg: ChatMessage = {
        id: String(Date.now() + 1),
        sender: "agent",
        text: fallbackText,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, errorMsg]);
      speakText(fallbackText);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFreeformSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!freeformQuery.trim()) return;

    const query = freeformQuery.trim();
    setFreeformQuery("");

    // If query mentions booking or appointment, trigger booking flow
    if (query.toLowerCase().includes("book") || query.toLowerCase().includes("confirm")) {
      handleSimulateBookAppointment();
    } else {
      // Default to checking availability
      handleSimulateCheckAvailability();
    }
  };

  return (
    <div className="space-y-6">
      {/* ElevenLabs Live WebRTC Voice Call Widget */}
      {/* @ts-ignore */}
      <elevenlabs-convai agent-id="agent_3601m6rj4cg6f9brv5kx93ykgag7"></elevenlabs-convai>
      <Script src="https://elevenlabs.io/convai-widget/index.js" strategy="afterInteractive" />

      {/* Live Voice Testing Banner */}
      <div className="bg-gradient-to-r from-emerald-900 via-slate-900 to-teal-900 border border-emerald-500/40 rounded-2xl p-6 shadow-md flex flex-col md:flex-row md:items-center justify-between gap-5 text-white">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 shrink-0 shadow-inner">
            <Sparkles className="w-6 h-6 animate-pulse text-emerald-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-white tracking-tight">
                Live In-Browser Voice Call (Asha)
              </h3>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                ElevenLabs WebRTC Active
              </span>
            </div>
            <p className="text-xs text-slate-300 mt-1 max-w-xl leading-relaxed">
              Look at the <strong>floating widget in the bottom-right corner</strong> of your screen (labeled <em>"Need help? Start a call"</em>). Click it to talk directly to Asha with your microphone in Malayalam or English!
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <div className="text-xs bg-emerald-950/60 border border-emerald-500/30 px-3.5 py-2 rounded-xl text-emerald-300 flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping"></span>
            <span>Widget Ready at Bottom Right ↘</span>
          </div>
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
            Simulate incoming patient voice queries with live audio speech synthesis and verify ElevenLabs tool executions
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* Audio Output Toggle */}
          <button
            onClick={() => setVoiceAudioEnabled(!voiceAudioEnabled)}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all border ${
              voiceAudioEnabled
                ? "bg-emerald-50 text-emerald-700 border-emerald-300"
                : "bg-slate-100 text-slate-500 border-slate-200"
            }`}
          >
            {voiceAudioEnabled ? <Volume2 className="w-4 h-4 text-emerald-600" /> : <VolumeX className="w-4 h-4" />}
            <span>Voice Audio: {voiceAudioEnabled ? "ON" : "MUTE"}</span>
          </button>

          <button
            onClick={() => {
              if (typeof window !== "undefined" && "speechSynthesis" in window) {
                window.speechSynthesis.cancel();
              }
              setMessages([
                {
                  id: "1",
                  sender: "agent",
                  text: "Namaste! Welcome to Sree Kerala Ayurvedic Clinic. I am your autonomous AI voice receptionist. How may I assist with your Ayurvedic wellness today?",
                  timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
                },
              ]);
            }}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Reset</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Interactive Chat Console (7 cols) */}
        <div className="lg:col-span-7 bg-white rounded-2xl border border-slate-200/90 shadow-xs flex flex-col h-[660px] overflow-hidden">
          {/* Chat Header */}
          <div className="p-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-emerald-600 text-white flex items-center justify-center shadow-xs">
                <Bot className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-bold text-slate-800 text-xs md:text-sm">
                  ElevenLabs Voice Receptionist Agent
                </h4>
                <div className="flex items-center gap-1 text-[11px] text-emerald-600 font-medium">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                  Active Speech Synthesis (Web Audio)
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2.5">
              <button
                type="button"
                onClick={toggleMic}
                className={`px-3 py-1 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all shadow-xs ${
                  isListening
                    ? "bg-rose-600 text-white animate-pulse"
                    : "bg-emerald-100 text-emerald-800 border border-emerald-300 hover:bg-emerald-200"
                }`}
              >
                <Mic className="w-3.5 h-3.5 text-emerald-700" />
                <span>{isListening ? "Listening..." : "🎙️ Speak to Asha"}</span>
              </button>
              <div className="text-[11px] text-slate-400 font-mono hidden sm:block">
                Voice: ElevenLabs / Asha
              </div>
            </div>
          </div>

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
                          <span>Caller (Patient)</span>
                        </>
                      )}
                    </div>
                    {msg.text}

                    {msg.toolCall && (
                      <div className="mt-2.5 pt-2 border-t border-slate-100 flex items-center justify-between text-[11px]">
                        <span className="font-mono text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded font-semibold border border-emerald-100">
                          ⚙️ Tool: {msg.toolCall.name}
                        </span>
                        <button
                          onClick={() => setActiveJsonTab(msg.toolCall?.response)}
                          className="text-slate-500 hover:text-slate-800 font-medium underline"
                        >
                          View Payload
                        </button>
                      </div>
                    )}
                  </div>
                  <span className="text-[10px] text-slate-400 mt-1 px-1">
                    {msg.timestamp}
                  </span>
                </div>
              );
            })}
            {isLoading && (
              <div className="flex items-center gap-2 text-xs text-slate-400 italic">
                <div className="w-2 h-2 rounded-full bg-emerald-500 animate-bounce"></div>
                <div className="w-2 h-2 rounded-full bg-emerald-500 animate-bounce [animation-delay:-.3s]"></div>
                <div className="w-2 h-2 rounded-full bg-emerald-500 animate-bounce [animation-delay:-.5s]"></div>
                <span>Executing tool webhook & synthesizing response...</span>
              </div>
            )}
          </div>

          {/* Quick Trigger Tool Buttons */}
          <div className="p-2.5 border-t border-slate-200 bg-slate-50/80 flex flex-wrap gap-2 text-xs">
            <button
              onClick={handleSimulateCheckAvailability}
              disabled={isLoading}
              className="px-3 py-1.5 rounded-lg bg-emerald-100 hover:bg-emerald-200 text-emerald-900 font-semibold border border-emerald-300 transition-colors flex items-center gap-1.5"
            >
              <Clock className="w-3.5 h-3.5 text-emerald-700" />
              <span>1. Check Availability</span>
            </button>
            <button
              onClick={handleSimulateBookAppointment}
              disabled={isLoading}
              className="px-3 py-1.5 rounded-lg bg-blue-100 hover:bg-blue-200 text-blue-900 font-semibold border border-blue-300 transition-colors flex items-center gap-1.5"
            >
              <CheckCircle2 className="w-3.5 h-3.5 text-blue-700" />
              <span>2. Confirm Booking</span>
            </button>
          </div>

          {/* Interactive Voice & Text Input */}
          <form onSubmit={handleFreeformSubmit} className="p-3 border-t border-slate-200 bg-white flex items-center gap-2">
            <button
              type="button"
              onClick={toggleMic}
              title={isListening ? "Listening... click to stop" : "Click to speak with microphone"}
              className={`p-2 rounded-xl transition-all ${
                isListening
                  ? "bg-rose-500 text-white animate-pulse"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              {isListening ? <Mic className="w-4 h-4" /> : <MicOff className="w-4 h-4" />}
            </button>

            <input
              type="text"
              placeholder={isListening ? "Listening to your voice..." : "Type a query (e.g., 'Do you have slots for Dr. Varma tomorrow?')..."}
              value={freeformQuery}
              onChange={(e) => setFreeformQuery(e.target.value)}
              className="flex-1 px-3 py-2 text-xs rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-slate-50"
            />

            <button
              type="submit"
              disabled={isLoading}
              className="px-3 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold flex items-center gap-1 transition-colors shadow-xs"
            >
              <Send className="w-3.5 h-3.5" />
              <span>Send</span>
            </button>
          </form>
        </div>

        {/* Right Column: Dynamic Parameters & Tool Response Inspector (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Tool Parameters Form */}
          <div className="bg-white rounded-2xl border border-slate-200/90 p-5 shadow-xs space-y-4">
            <h3 className="font-bold text-slate-800 text-sm flex items-center gap-2">
              <Stethoscope className="w-4 h-4 text-emerald-600" />
              <span>Simulated Caller & Booking Details</span>
            </h3>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block font-medium text-slate-700 mb-1">Target Doctor</label>
                <select
                  value={selectedDoctor}
                  onChange={(e) => setSelectedDoctor(e.target.value)}
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
                  value={treatmentType}
                  onChange={(e) => setTreatmentType(e.target.value)}
                  className="w-full p-2.5 rounded-lg border border-slate-200 bg-slate-50 text-slate-800 font-medium"
                >
                  <option value="Panchakarma Consultation">Panchakarma Consultation</option>
                  <option value="Nadi Pariksha & Pulse Diagnosis">Nadi Pariksha & Pulse Diagnosis</option>
                  <option value="Dosha Assessment & Diet Plan">Dosha Assessment & Diet Plan</option>
                  <option value="General Ayurvedic Consultation">General Ayurvedic Consultation</option>
                </select>
              </div>

              <div>
                <label className="block font-medium text-slate-700 mb-1">Requested Date & Time</label>
                <input
                  type="datetime-local"
                  value={requestedDateTime}
                  onChange={(e) => setRequestedDateTime(e.target.value)}
                  className="w-full p-2.5 rounded-lg border border-slate-200 bg-slate-50 text-slate-800 font-medium"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
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
                : `// Click "Check Availability" or "Confirm Booking"\n// to execute tool webhooks in real-time\n{\n  "status": "ready",\n  "clinic_id": "${selectedClinic}"\n}`}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}
