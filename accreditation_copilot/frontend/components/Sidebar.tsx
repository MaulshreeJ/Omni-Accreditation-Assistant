"use client";

import { Home, FileText, BarChart3, History, Settings, Sparkles, User } from "lucide-react";
import ThemeSwitcher from "./ThemeSwitcher";

export default function Sidebar() {
  return (
    <div className="w-64 glass-card border-r border-border/50 flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-border/50">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-cyan-400" />
            <h1 className="text-xl font-bold gradient-text">Omni</h1>
          </div>
          <ThemeSwitcher />
        </div>
        <p className="text-sm text-muted-foreground">Accreditation Copilot</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          <li>
            <a
              href="#"
              className="flex items-center gap-3 px-4 py-3 rounded-xl gradient-bg text-white font-medium hover-glow"
            >
              <Home size={20} />
              <span>Dashboard</span>
            </a>
          </li>
          <li>
            <a
              href="#"
              className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-cyan-400/10 text-muted-foreground hover:text-cyan-400 transition-all hover-glow"
            >
              <FileText size={20} />
              <span>Run Audit</span>
            </a>
          </li>
          <li>
            <a
              href="#"
              className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-cyan-400/10 text-muted-foreground hover:text-cyan-400 transition-all hover-glow"
            >
              <BarChart3 size={20} />
              <span>Metrics</span>
            </a>
          </li>
          <li>
            <a
              href="#"
              className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-cyan-400/10 text-muted-foreground hover:text-cyan-400 transition-all hover-glow"
            >
              <History size={20} />
              <span>History</span>
            </a>
          </li>
          <li>
            <a
              href="#"
              className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-pink-400/10 text-muted-foreground hover:text-pink-400 transition-all hover-glow"
            >
              <User size={20} />
              <span>Profile</span>
            </a>
          </li>
        </ul>
      </nav>

      {/* Settings */}
      <div className="p-4 border-t border-border/50">
        <a
          href="#"
          className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-cyan-400/10 text-muted-foreground hover:text-cyan-400 transition-all hover-glow"
        >
          <Settings size={20} />
          <span>Settings</span>
        </a>
      </div>
    </div>
  );
}
