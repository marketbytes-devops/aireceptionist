"use client";

import { useEffect, useState } from "react";
import { 
  PhoneCall, 
  Play, 
  Pause, 
  FileText, 
  Clock, 
  Calendar, 
  Volume2, 
  Sparkles,
  Search,
  Filter
} from "lucide-react";
import { fetchCallLogs } from "@/lib/api";
import { CallLog } from "@/lib/types";
import TranscriptModal from "@/components/TranscriptModal";

export default function CallLogsPage() {
  const [callLogs, setCallLogs] = useState<CallLog[]>([]);
  const [playingCallId, setPlayingCallId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedTranscript, setSelectedTranscript] = useState<{
    title: string;
    transcript?: string;
    callerPhone?: string;
    date?: string;
    sentiment?: string;
  } | null>(null);

  useEffect(() => {
    fetchCallLogs().then(setCallLogs);
  }, []);

  const filteredLogs = callLogs.filter(
    (c) =>
      c.caller_phone.includes(searchQuery) ||
      (c.summary && c.summary.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (c.transcript && c.transcript.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const toggleAudio = (callId: string) => {
    if (playingCallId === callId) {
      setPlayingCallId(null);
    } else {
      setPlayingCallId(callId);
      // Simulate auto-stop after 8 seconds
      setTimeout(() => {
        setPlayingCallId((curr) => (curr === callId ? null : curr));
      }, 8000);
    }
  };

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl md:text-2xl font-bold text-slate-800 tracking-tight">
            AI Receptionist Call Logs & Transcripts
          </h2>
          <p className="text-xs md:text-sm text-slate-500">
            Recorded phone interactions handled by ElevenLabs Conversational AI and Twilio
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-200/80 flex items-center gap-1.5">
            <Volume2 className="w-3.5 h-3.5 text-emerald-600" />
            <span>Post-Call Audio & NLP Extraction Active</span>
          </span>
        </div>
      </div>

      {/* Search Bar */}
      <div className="bg-white rounded-xl p-4 border border-slate-200/90 shadow-xs flex items-center justify-between gap-4">
        <div className="relative w-full max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search transcripts by caller phone, keyword, or doctor..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-slate-50"
          />
        </div>

        <div className="text-xs text-slate-400 font-medium">
          Showing {filteredLogs.length} interactions
        </div>
      </div>

      {/* Call Logs List */}
      <div className="space-y-4">
        {filteredLogs.length === 0 ? (
          <div className="bg-white rounded-2xl p-12 text-center border border-slate-200 text-slate-400 text-sm">
            No call logs found matching your query.
          </div>
        ) : (
          filteredLogs.map((call) => {
            const isPlaying = playingCallId === call.id;

            return (
              <div
                key={call.id}
                className="bg-white rounded-2xl p-5 border border-slate-200/90 shadow-xs hover:border-emerald-300 transition-all space-y-4"
              >
                {/* Header Row */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-slate-100 text-slate-700 flex items-center justify-center font-bold">
                      <PhoneCall className="w-5 h-5 text-emerald-600" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="font-bold text-slate-800 text-sm md:text-base">
                          {call.caller_phone}
                        </h4>
                        {call.call_sid && (
                          <span className="text-[10px] font-mono text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded">
                            {call.call_sid.slice(0, 10)}...
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-3 text-xs text-slate-400 mt-0.5">
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {new Date(call.created_at).toLocaleString([], {
                            month: "short",
                            day: "numeric",
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </span>
                        <span>•</span>
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {call.duration_seconds || 45} seconds
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 self-start sm:self-auto">
                    {call.sentiment && (
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-semibold capitalize bg-emerald-50 text-emerald-700 border border-emerald-200">
                        <Sparkles className="w-3 h-3 text-emerald-500" />
                        <span>{call.sentiment}</span>
                      </span>
                    )}

                    <span className="px-2.5 py-1 rounded-full text-[11px] font-semibold bg-slate-100 text-slate-700 capitalize">
                      {call.outcome?.replace("_", " ") || "Inquiry Handled"}
                    </span>
                  </div>
                </div>

                {/* AI Summary Banner */}
                {call.summary && (
                  <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100 text-xs text-slate-700 leading-relaxed">
                    <strong className="text-slate-900 font-semibold">AI Call Summary: </strong>
                    {call.summary}
                  </div>
                )}

                {/* Audio Player & Transcript Controls */}
                <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-3 border-t border-slate-100">
                  {/* Simulated Audio Waveform / Controls */}
                  <div className="flex items-center gap-3 w-full sm:w-auto">
                    <button
                      onClick={() => toggleAudio(call.id)}
                      className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                        isPlaying
                          ? "bg-emerald-600 text-white shadow-xs"
                          : "bg-slate-100 hover:bg-slate-200 text-slate-700"
                      }`}
                    >
                      {isPlaying ? (
                        <>
                          <Pause className="w-3.5 h-3.5" />
                          <span>Pause Audio</span>
                        </>
                      ) : (
                        <>
                          <Play className="w-3.5 h-3.5 fill-current" />
                          <span>Play Audio Recording</span>
                        </>
                      )}
                    </button>

                    {/* Simulated Waveform Animation */}
                    <div className="flex items-center gap-0.5 h-4">
                      {[12, 24, 16, 28, 10, 20, 32, 14, 22, 18, 26, 8, 30].map((h, i) => (
                        <span
                          key={i}
                          style={{ height: isPlaying ? `${(h * 0.7) % 20 + 6}px` : "6px" }}
                          className={`w-1 rounded-full transition-all duration-150 ${
                            isPlaying ? "bg-emerald-500 animate-pulse" : "bg-slate-300"
                          }`}
                        />
                      ))}
                    </div>
                  </div>

                  {/* View Transcript Button */}
                  <button
                    onClick={() =>
                      setSelectedTranscript({
                        title: `Full Conversation Transcript - ${call.caller_phone}`,
                        transcript: call.transcript,
                        callerPhone: call.caller_phone,
                        date: call.created_at,
                        sentiment: call.sentiment || "positive",
                      })
                    }
                    className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-800 text-xs font-semibold transition-colors border border-emerald-200/80 w-full sm:w-auto justify-center"
                  >
                    <FileText className="w-3.5 h-3.5 text-emerald-600" />
                    <span>View Dialogue Transcript</span>
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Transcript Modal */}
      {selectedTranscript && (
        <TranscriptModal
          isOpen={true}
          onClose={() => setSelectedTranscript(null)}
          title={selectedTranscript.title}
          transcript={selectedTranscript.transcript}
          callerPhone={selectedTranscript.callerPhone}
          date={selectedTranscript.date}
          sentiment={selectedTranscript.sentiment}
        />
      )}
    </div>
  );
}

