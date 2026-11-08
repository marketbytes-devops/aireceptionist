"use client";

import { X, Bot, User, PhoneCall, Sparkles } from "lucide-react";

interface TranscriptModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  transcript?: string;
  callerPhone?: string;
  patientName?: string;
  date?: string;
  sentiment?: string;
}

export default function TranscriptModal({
  isOpen,
  onClose,
  title,
  transcript,
  callerPhone,
  patientName,
  date,
  sentiment,
}: TranscriptModalProps) {
  if (!isOpen) return null;

  // Parse lines into speaker turns
  const lines = transcript ? transcript.split("\n").filter((l) => l.trim().length > 0) : [];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4 animate-in fade-in duration-200">
      <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[85vh] flex flex-col shadow-2xl border border-slate-200 overflow-hidden">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50/70">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center">
              <PhoneCall className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-semibold text-slate-800 text-sm md:text-base">{title}</h3>
              <p className="text-xs text-slate-500">
                {patientName ? `Patient: ${patientName} • ` : ""}
                {callerPhone ? `Phone: ${callerPhone}` : ""}
                {date ? ` • ${new Date(date).toLocaleString()}` : ""}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-200/60 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Sentiment Banner */}
        {sentiment && (
          <div className="px-6 py-2.5 bg-emerald-50/60 border-b border-emerald-100 flex items-center gap-2 text-xs text-emerald-800 font-medium">
            <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
            <span>AI Sentiment: <strong className="capitalize">{sentiment}</strong></span>
          </div>
        )}

        {/* Transcript Dialogue Scroll Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-slate-50/30">
          {lines.length === 0 ? (
            <div className="text-center py-12 text-slate-400 text-sm">
              No audio transcript recorded for this interaction.
            </div>
          ) : (
            lines.map((line, idx) => {
              const isAgent =
                line.toLowerCase().startsWith("agent:") ||
                line.toLowerCase().startsWith("ai:") ||
                line.toLowerCase().startsWith("receptionist:");
              const cleanText = line.replace(/^(agent|ai|receptionist|patient|user|caller):\s*/i, "");

              return (
                <div
                  key={idx}
                  className={`flex gap-3 ${isAgent ? "items-start" : "items-start flex-row-reverse"}`}
                >
                  <div
                    className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold shrink-0 shadow-xs ${
                      isAgent
                        ? "bg-emerald-600 text-white"
                        : "bg-slate-700 text-white"
                    }`}
                  >
                    {isAgent ? <Bot className="w-4 h-4" /> : <User className="w-4 h-4" />}
                  </div>

                  <div
                    className={`max-w-[78%] rounded-2xl px-4 py-2.5 text-xs md:text-sm leading-relaxed shadow-xs ${
                      isAgent
                        ? "bg-white border border-slate-200 text-slate-800 rounded-tl-xs"
                        : "bg-emerald-600 text-white rounded-tr-xs"
                    }`}
                  >
                    <div className="text-[10px] uppercase tracking-wider font-semibold opacity-70 mb-0.5">
                      {isAgent ? "AyurVoice Receptionist" : "Patient / Caller"}
                    </div>
                    {cleanText}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3.5 border-t border-slate-200 bg-white flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-medium rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 transition-colors"
          >
            Close Viewer
          </button>
        </div>
      </div>
    </div>
  );
}

