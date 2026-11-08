"use client";

import { Bell, Phone, Radio, User } from "lucide-react";

export default function Header() {
  return (
    <header className="h-16 bg-white border-b border-slate-200 px-8 flex items-center justify-between sticky top-0 z-30 shadow-xs">
      <div className="flex items-center gap-4">
        <div>
          <h1 className="text-base font-semibold text-slate-800">Sree Kerala Ayurvedic Clinic</h1>
          <p className="text-xs text-slate-500">Kochi, Kerala • Asia/Kolkata (IST)</p>
        </div>
        <div className="hidden sm:flex items-center gap-2 bg-emerald-50 text-emerald-700 text-xs px-3 py-1 rounded-full border border-emerald-200/80 font-medium">
          <Radio className="w-3.5 h-3.5 text-emerald-600 animate-pulse" />
          <span>ElevenLabs AI Receptionist Active</span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-100 text-slate-700 text-xs font-medium">
          <Phone className="w-3.5 h-3.5 text-emerald-600" />
          <span>+1 (800) 555-0199</span>
        </div>

        <button className="relative p-2 text-slate-400 hover:text-slate-600 transition-colors">
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-emerald-500"></span>
        </button>

        <div className="flex items-center gap-2 pl-2 border-l border-slate-200">
          <div className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center font-semibold text-xs border border-emerald-200">
            RV
          </div>
          <div className="hidden md:block text-left text-xs">
            <div className="font-semibold text-slate-800">Dr. Rajesh Varma</div>
            <div className="text-slate-400 text-[10px]">Clinic Administrator</div>
          </div>
        </div>
      </div>
    </header>
  );
}

