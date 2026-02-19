"use client";

import { Menu } from "lucide-react";

interface HeaderProps {
  onToggleSidebar: () => void;
}

export function Header({ onToggleSidebar }: HeaderProps) {
  return (
    <header className="bg-primary text-white">
      <div className="max-w-5xl mx-auto px-4 py-6 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">
            Evaluador de Examenes Orales
          </h1>
          <p className="text-sm opacity-70 mt-0.5">
            Sistema de evaluacion automatizada multi-paso
          </p>
        </div>
        <button
          onClick={onToggleSidebar}
          className="p-2 rounded-md hover:bg-white/10 transition-colors"
          aria-label="Toggle settings"
        >
          <Menu className="w-5 h-5" />
        </button>
      </div>
    </header>
  );
}
