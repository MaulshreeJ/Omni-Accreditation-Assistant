"use client";

import { Home, FileText, BarChart3, History, Settings } from "lucide-react";

export default function Sidebar() {
  return (
    <div className="w-64 bg-card border-r border-border flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-border">
        <h1 className="text-xl font-bold">Omni Accreditation</h1>
        <p className="text-sm text-muted-foreground">Copilot</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          <li>
            <a
              href="#"
              className="flex items-center gap-3 px-4 py-2 rounded-lg bg-primary text-primary-foreground"
            >
              <Home size={20} />
              <span>Dashboard</span>
            </a>
          </li>
          <li>
            <a
              href="#"
              className="flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-accent text-muted-foreground hover:text-foreground transition-colors"
            >
              <FileText size={20} />
              <span>Audits</span>
            </a>
          </li>
          <li>
            <a
              href="#"
              className="flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-accent text-muted-foreground hover:text-foreground transition-colors"
            >
              <BarChart3 size={20} />
              <span>Metrics</span>
            </a>
          </li>
          <li>
            <a
              href="#"
              className="flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-accent text-muted-foreground hover:text-foreground transition-colors"
            >
              <History size={20} />
              <span>History</span>
            </a>
          </li>
        </ul>
      </nav>

      {/* Settings */}
      <div className="p-4 border-t border-border">
        <a
          href="#"
          className="flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-accent text-muted-foreground hover:text-foreground transition-colors"
        >
          <Settings size={20} />
          <span>Settings</span>
        </a>
      </div>
    </div>
  );
}
