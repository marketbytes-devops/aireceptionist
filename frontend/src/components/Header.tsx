"use client";

import { Bell, Phone, Radio, Menu } from "lucide-react";

interface HeaderProps {
  onOpenMobileMenu?: () => void;
}

export default function Header({ onOpenMobileMenu }: HeaderProps) {
  return (
    <header className="h-16 bg-white border-b border-slate-200 px-4 sm:px-6 md:px-8 flex items-center justify-between sticky top-0 z-30 shadow-xs">
      {/* Left: Mobile Hamburger & Clinic Title */}
      <div className="flex items-center gap-3 min-w-0">
        {onOpenMobileMenu && (
          <button
            type="button"
            onClick={onOpenMobileMenu}
            className="p-2 -ml-1 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors md:hidden shrink-0"
            aria-label="Open navigation menu"
          >
            <Menu className="w-5 h-5" />
          </button>
        )}

        <div className="min-w-0">
          <h1 className="text-xs sm:text-sm md:text-base font-bold text-slate-800 truncate">
            Sreerudra Ayurveda Multi Speciality Hospital
          </h1>
          <p className="text-[10px] sm:text-xs text-slate-500 truncate">
            Alappuzha & Trivandrum, Kerala • Asia/Kolkata (IST)
          </p>
        </div>

        <div className="hidden lg:flex items-center gap-2 bg-emerald-50 text-emerald-700 text-xs px-3 py-1 rounded-full border border-emerald-200/80 font-medium shrink-0">
          <Radio className="w-3.5 h-3.5 text-emerald-600 animate-pulse" />
          <span>Asha AI Receptionist Active</span>
        </div>
      </div>

      {/* Right: Phone, Notification, Profile */}
      <div className="flex items-center gap-2 sm:gap-4 shrink-0">
        <div className="hidden sm:flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-slate-100 text-slate-700 text-xs font-medium">
          <Phone className="w-3.5 h-3.5 text-emerald-600" />
          <span>+91 90379 03333</span>
        </div>

        <button 
          type="button" 
          className="relative p-1.5 sm:p-2 text-slate-400 hover:text-slate-600 transition-colors"
          aria-label="Notifications"
        >
          <Bell className="w-4 h-4" />
          <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-emerald-500"></span>
        </button>

        <div className="flex items-center gap-2 pl-2 border-l border-slate-200">
          <div className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold text-xs border border-emerald-200 shrink-0">
            VN
          </div>
          <div className="hidden md:block text-left text-xs">
            <div className="font-semibold text-slate-800 leading-tight">Dr. K. S. Vishnu Nampoothiry</div>
            <div className="text-slate-400 text-[10px]">Medical Director</div>
          </div>
        </div>
      </div>
    </header>
  );
}
