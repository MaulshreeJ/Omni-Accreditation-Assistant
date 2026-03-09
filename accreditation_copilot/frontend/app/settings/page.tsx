'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import { Bell, Lock, Globe, Palette, Database } from 'lucide-react';

export default function SettingsPage() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const auth = localStorage.getItem('isAuthenticated');
    if (auth === 'true') {
      setIsAuthenticated(true);
    } else {
      router.push('/login');
    }
  }, [router]);

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <Sidebar />
      
      <div className="flex-1 overflow-auto p-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold gradient-text mb-2">Settings</h1>
            <p className="text-muted-foreground">Manage your application preferences</p>
          </div>

          {/* Settings Sections */}
          <div className="space-y-6">
            {/* Notifications */}
            <div className="glass-card p-6 rounded-xl border border-border/50">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-cyan-500/10 flex items-center justify-center">
                  <Bell size={20} className="text-cyan-400" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-foreground">Notifications</h3>
                  <p className="text-sm text-muted-foreground">Manage your notification preferences</p>
                </div>
              </div>
              <div className="space-y-4">
                <label className="flex items-center justify-between cursor-pointer">
                  <span className="text-sm text-foreground">Email notifications</span>
                  <input type="checkbox" className="w-5 h-5 rounded border-slate-600 bg-slate-900/50 text-cyan-500" defaultChecked />
                </label>
                <label className="flex items-center justify-between cursor-pointer">
                  <span className="text-sm text-foreground">Audit completion alerts</span>
                  <input type="checkbox" className="w-5 h-5 rounded border-slate-600 bg-slate-900/50 text-cyan-500" defaultChecked />
                </label>
                <label className="flex items-center justify-between cursor-pointer">
                  <span className="text-sm text-foreground">Weekly summary reports</span>
                  <input type="checkbox" className="w-5 h-5 rounded border-slate-600 bg-slate-900/50 text-cyan-500" />
                </label>
              </div>
            </div>

            {/* Security */}
            <div className="glass-card p-6 rounded-xl border border-border/50">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center">
                  <Lock size={20} className="text-purple-400" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-foreground">Security</h3>
                  <p className="text-sm text-muted-foreground">Manage your security settings</p>
                </div>
              </div>
              <div className="space-y-4">
                <button className="w-full px-4 py-3 bg-slate-900/50 border border-slate-600 rounded-lg text-left text-sm text-foreground hover:bg-slate-900 transition">
                  Change password
                </button>
                <button className="w-full px-4 py-3 bg-slate-900/50 border border-slate-600 rounded-lg text-left text-sm text-foreground hover:bg-slate-900 transition">
                  Enable two-factor authentication
                </button>
                <button className="w-full px-4 py-3 bg-slate-900/50 border border-slate-600 rounded-lg text-left text-sm text-foreground hover:bg-slate-900 transition">
                  View active sessions
                </button>
              </div>
            </div>

            {/* Appearance */}
            <div className="glass-card p-6 rounded-xl border border-border/50">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-pink-500/10 flex items-center justify-center">
                  <Palette size={20} className="text-pink-400" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-foreground">Appearance</h3>
                  <p className="text-sm text-muted-foreground">Customize the look and feel</p>
                </div>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="text-sm text-foreground mb-2 block">Theme</label>
                  <select className="w-full px-4 py-3 bg-slate-900/50 border border-slate-600 rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-cyan-500">
                    <option>Stillness (Current)</option>
                    <option>Light</option>
                    <option>Dark</option>
                    <option>Auto</option>
                  </select>
                </div>
                <label className="flex items-center justify-between cursor-pointer">
                  <span className="text-sm text-foreground">Compact mode</span>
                  <input type="checkbox" className="w-5 h-5 rounded border-slate-600 bg-slate-900/50 text-cyan-500" />
                </label>
              </div>
            </div>

            {/* Language */}
            <div className="glass-card p-6 rounded-xl border border-border/50">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
                  <Globe size={20} className="text-green-400" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-foreground">Language & Region</h3>
                  <p className="text-sm text-muted-foreground">Set your language preferences</p>
                </div>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="text-sm text-foreground mb-2 block">Language</label>
                  <select className="w-full px-4 py-3 bg-slate-900/50 border border-slate-600 rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-cyan-500">
                    <option>English</option>
                    <option>Hindi</option>
                    <option>Tamil</option>
                    <option>Telugu</option>
                  </select>
                </div>
                <div>
                  <label className="text-sm text-foreground mb-2 block">Timezone</label>
                  <select className="w-full px-4 py-3 bg-slate-900/50 border border-slate-600 rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-cyan-500">
                    <option>IST (UTC+5:30)</option>
                    <option>UTC</option>
                    <option>EST</option>
                    <option>PST</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Data Management */}
            <div className="glass-card p-6 rounded-xl border border-border/50">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-yellow-500/10 flex items-center justify-center">
                  <Database size={20} className="text-yellow-400" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-foreground">Data Management</h3>
                  <p className="text-sm text-muted-foreground">Manage your data and storage</p>
                </div>
              </div>
              <div className="space-y-4">
                <button className="w-full px-4 py-3 bg-slate-900/50 border border-slate-600 rounded-lg text-left text-sm text-foreground hover:bg-slate-900 transition">
                  Export audit history
                </button>
                <button className="w-full px-4 py-3 bg-slate-900/50 border border-slate-600 rounded-lg text-left text-sm text-foreground hover:bg-slate-900 transition">
                  Clear cache
                </button>
                <button className="w-full px-4 py-3 bg-red-500/10 border border-red-500/50 rounded-lg text-left text-sm text-red-400 hover:bg-red-500/20 transition">
                  Delete all data
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
