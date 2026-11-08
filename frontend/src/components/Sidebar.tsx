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
  ShieldCheck,
  BookOpen,
  X
} from "lucide-react";

const navigation = [
  { name: "Overview", href: "/", icon: LayoutDashboard },
  { name: "Appointments", href: "/appointments", icon: CalendarDays },
  { name: "Doctors & Timings", href: "/doctors", icon: Stethoscope },
  { name: "Hospital Knowledge Base", href: "/knowledge-base", icon: BookOpen },
  { name: "Call Logs & Audio", href: "/calls", icon: PhoneCall },
  { name: "AI Voice Simulator", href: "/simulator", icon: Bot, highlight: true },
];

interface SidebarProps {
  onClose?: () => void;
  isMobile?: boolean;
}

export default function Sidebar({ onClose, isMobile = false }: SidebarProps) {
  const pathname = usePathname();

  const handleLinkClick = () => {
    if (onClose) onClose();
  };

  return (
    <aside className="w-64 md:w-64 bg-slate-900 text-slate-200 flex flex-col h-full md:min-h-screen border-r border-slate-800 shrink-0 md:sticky md:top-0 md:h-screen overflow-y-auto">
      {/* Brand Logo & Close Button for Mobile */}
      <div className="p-5 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center text-white shadow-lg shadow-emerald-900/30">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <div className="font-bold text-base tracking-tight text-white flex items-center gap-1.5">
              AyurVoice
              <span className="text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-semibold border border-emerald-500/30">
                SaaS
              </span>
            </div>
            <p className="text-[11px] text-slate-400">AI Ayurvedic Receptionist</p>
          </div>
        </div>

        {isMobile && (
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            aria-label="Close menu"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-5 space-y-1">
        <div className="px-3 pb-2 text-[10px] font-semibold uppercase tracking-wider text-slate-400">
          Clinic Portal
        </div>
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.name}
              href={item.href}
              onClick={handleLinkClick}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs sm:text-sm font-medium transition-all ${
                isActive
                  ? "bg-emerald-600 text-white shadow-sm shadow-emerald-700/50"
                  : item.highlight
                  ? "text-emerald-400 hover:bg-slate-800/80 hover:text-emerald-300"
                  : "text-slate-300 hover:bg-slate-800/60 hover:text-white"
              }`}
            >
              <Icon className={`w-4 h-4 shrink-0 ${isActive ? "text-white" : item.highlight ? "text-emerald-400" : "text-slate-400"}`} />
              <span className="truncate">{item.name}</span>
              {item.highlight && (
                <span className="ml-auto text-[10px] font-semibold bg-emerald-500/20 text-emerald-300 px-1.5 py-0.5 rounded border border-emerald-500/30 shrink-0">
                  Test
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Multi-Tenant Status Card */}
      <div className="p-3.5 m-3 rounded-xl bg-slate-800/70 border border-slate-700/60 text-xs text-slate-300">
        <div className="flex items-center justify-between mb-1.5">
          <span className="font-semibold text-[11px] text-slate-300">Active Tenant</span>
          <span className="inline-flex items-center gap-1 text-[10px] text-emerald-400 font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            Online
          </span>
        </div>
        <div className="font-semibold text-white truncate text-xs">Sree Kerala Ayurvedic</div>
        <div className="text-[11px] text-slate-400 truncate mt-0.5">+1 (757) 914-3149</div>
      </div>

      {/* Footer */}
      <div className="p-3.5 border-t border-slate-800 text-[11px] text-slate-400 flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span>Tenant Isolated</span>
        </div>
        <span>v1.0.0</span>
      </div>
    </aside>
  );
}
