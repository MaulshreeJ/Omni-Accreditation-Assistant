"use client";

import { Home, FileText, BarChart3, History, Settings, Sparkles, User, LogOut, Trophy } from "lucide-react";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import ThemeSwitcher from "./ThemeSwitcher";

export default function Sidebar() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [showProfileMenu, setShowProfileMenu] = useState(false);

  useEffect(() => {
    // Load user from localStorage
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('user');
    localStorage.removeItem('isAuthenticated');
    router.push('/login');
  };

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

      {/* User Profile Section */}
      {user && (
        <div className="p-4 border-b border-border/50">
          <div className="relative">
            <button
              onClick={() => setShowProfileMenu(!showProfileMenu)}
              className="w-full flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-cyan-400/10 transition-all hover-glow"
            >
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-400 to-pink-400 flex items-center justify-center text-white font-bold">
                {user.name?.charAt(0).toUpperCase() || 'U'}
              </div>
              <div className="flex-1 text-left">
                <p className="text-sm font-semibold text-foreground">{user.name}</p>
                <p className="text-xs text-muted-foreground">{user.role}</p>
              </div>
            </button>

            {/* Profile Dropdown */}
            {showProfileMenu && (
              <div className="absolute top-full left-0 right-0 mt-2 p-2 glass-card border border-border/50 rounded-xl shadow-lg z-50">
                <div className="px-4 py-2 border-b border-border/50 mb-2">
                  <p className="text-xs text-muted-foreground">Institution</p>
                  <p className="text-sm font-medium text-foreground">{user.institution}</p>
                </div>
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-2 px-4 py-2 rounded-lg hover:bg-red-500/10 text-red-400 hover:text-red-300 transition-all"
                >
                  <LogOut size={16} />
                  <span className="text-sm">Logout</span>
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          <li>
            <button
              onClick={() => router.push('/')}
              className="w-full flex items-center gap-3 px-4 py-3 rounded-xl gradient-bg text-white font-medium hover-glow"
            >
              <Home size={20} />
              <span>Dashboard</span>
            </button>
          </li>
          <li>
            <button
              onClick={() => router.push('/')}
              className="w-full flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-cyan-400/10 text-muted-foreground hover:text-cyan-400 transition-all hover-glow"
            >
              <FileText size={20} />
              <span>Run Audit</span>
            </button>
          </li>
          <li>
            <button
              onClick={() => router.push('/metrics')}
              className="w-full flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-cyan-400/10 text-muted-foreground hover:text-cyan-400 transition-all hover-glow"
            >
              <BarChart3 size={20} />
              <span>Metrics</span>
            </button>
          </li>
          <li>
            <button
              onClick={() => router.push('/history')}
              className="w-full flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-cyan-400/10 text-muted-foreground hover:text-cyan-400 transition-all hover-glow"
            >
              <History size={20} />
              <span>History</span>
            </button>
          </li>
          <li>
            <button
              onClick={() => router.push('/top-universities')}
              className="w-full flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-yellow-400/10 text-muted-foreground hover:text-yellow-400 transition-all hover-glow"
            >
              <Trophy size={20} />
              <span>Top Universities</span>
            </button>
          </li>
          <li>
            <button
              onClick={() => router.push('/profile')}
              className="w-full flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-pink-400/10 text-muted-foreground hover:text-pink-400 transition-all hover-glow"
            >
              <User size={20} />
              <span>Profile</span>
            </button>
          </li>
        </ul>
      </nav>

      {/* Settings */}
      <div className="p-4 border-t border-border/50">
        <button
          onClick={() => router.push('/settings')}
          className="w-full flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-cyan-400/10 text-muted-foreground hover:text-cyan-400 transition-all hover-glow"
        >
          <Settings size={20} />
          <span>Settings</span>
        </button>
      </div>
    </div>
  );
}
