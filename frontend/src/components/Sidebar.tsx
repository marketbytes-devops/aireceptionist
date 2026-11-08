"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutDashboard, 
  CalendarDays, 
  Stethoscope, 
  PhoneCall, 
  Bot, 
  Sparkles,
  Settings,
  ShieldCheck,
  BookOpen
} from "lucide-react";

const navigation = [
  { name: "Overview", href: "/", icon: LayoutDashboard },
  { name: "Appointments", href: "/appointments", icon: CalendarDays },
  { name: "Doctors & Timings", href: "/doctors", icon: Stethoscope },
  { name: "Hospital Knowledge Base", href: "/knowledge-base", icon: BookOpen },
  { name: "Call Logs & Audio", href: "/calls", icon: PhoneCall },
  { name: "AI Voice Simulator", href: "/simulator", icon: Bot, highlight: true },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-slate-900 text-slate-200 flex flex-col min-h-screen border-r border-slate-800">
      {/* Brand Logo */}
      <div className="p-6 border-b border-slate-800 flex items-center space-x-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center text-white shadow-lg shadow-emerald-900/30">
          <Sparkles className="w-5 h-5" />
        </div>
        <div>
          <div className="font-bold text-lg tracking-tight text-white flex items-center gap-1.5">
            AyurVoice
            <span className="text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-semibold border border-emerald-500/30">
              SaaS
            </span>
          </div>
          <p className="text-xs text-slate-400">AI Ayurvedic Receptionist</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-1.5">
        <div className="px-3 pb-2 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
          Clinic Portal
        </div>
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? "bg-emerald-600 text-white shadow-sm shadow-emerald-700/50"
                  : item.highlight
                  ? "text-emerald-400 hover:bg-slate-800/80 hover:text-emerald-300"
                  : "text-slate-300 hover:bg-slate-800/60 hover:text-white"
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? "text-white" : item.highlight ? "text-emerald-400" : "text-slate-400"}`} />
              <span>{item.name}</span>
              {item.highlight && (
                <span className="ml-auto text-[10px] font-semibold bg-emerald-500/20 text-emerald-300 px-1.5 py-0.5 rounded border border-emerald-500/30">
                  Test
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Multi-Tenant Status Card */}
      <div className="p-4 m-4 rounded-xl bg-slate-800/70 border border-slate-700/60 text-xs text-slate-300">
        <div className="flex items-center justify-between mb-2">
          <span className="font-semibold text-slate-200">Active Tenant</span>
          <span className="inline-flex items-center gap-1 text-[11px] text-emerald-400 font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            Online
          </span>
        </div>
        <div className="font-medium text-white truncate">Sree Kerala Ayurvedic</div>
        <div className="text-[11px] text-slate-400 truncate mt-0.5">+1 (800) 555-0199</div>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-slate-800 text-[11px] text-slate-400 flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span>Tenant Isolated</span>
        </div>
        <span>v1.0.0</span>
      </div>
    </aside>
  );
}

