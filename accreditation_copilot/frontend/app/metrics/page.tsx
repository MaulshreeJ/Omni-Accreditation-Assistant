'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import { BarChart3, TrendingUp, Award, Target } from 'lucide-react';

export default function MetricsPage() {
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
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold gradient-text mb-2">Performance Metrics</h1>
            <p className="text-muted-foreground">Track your institution's accreditation performance</p>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="glass-card p-6 rounded-xl border border-border/50">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-lg bg-cyan-500/10 flex items-center justify-center">
                  <BarChart3 size={24} className="text-cyan-400" />
                </div>
                <span className="text-xs text-green-400 font-semibold">+12%</span>
              </div>
              <p className="text-sm text-muted-foreground mb-1">Overall Score</p>
              <p className="text-3xl font-bold gradient-text">68%</p>
            </div>

            <div className="glass-card p-6 rounded-xl border border-border/50">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-lg bg-purple-500/10 flex items-center justify-center">
                  <Award size={24} className="text-purple-400" />
                </div>
                <span className="text-xs text-green-400 font-semibold">+8%</span>
              </div>
              <p className="text-sm text-muted-foreground mb-1">Compliance Rate</p>
              <p className="text-3xl font-bold text-purple-400">85%</p>
            </div>

            <div className="glass-card p-6 rounded-xl border border-border/50">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-lg bg-pink-500/10 flex items-center justify-center">
                  <Target size={24} className="text-pink-400" />
                </div>
                <span className="text-xs text-yellow-400 font-semibold">-3%</span>
              </div>
              <p className="text-sm text-muted-foreground mb-1">Coverage</p>
              <p className="text-3xl font-bold text-pink-400">92%</p>
            </div>

            <div className="glass-card p-6 rounded-xl border border-border/50">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-lg bg-green-500/10 flex items-center justify-center">
                  <TrendingUp size={24} className="text-green-400" />
                </div>
                <span className="text-xs text-green-400 font-semibold">+15%</span>
              </div>
              <p className="text-sm text-muted-foreground mb-1">Improvement</p>
              <p className="text-3xl font-bold text-green-400">+15%</p>
            </div>
          </div>

          {/* Framework Breakdown */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <div className="glass-card p-6 rounded-xl border border-border/50">
              <h3 className="text-lg font-bold text-foreground mb-4">NAAC Performance</h3>
              <div className="space-y-4">
                {[
                  { criterion: '3.2.1', score: 74, grade: 'A+' },
                  { criterion: '3.2.2', score: 65, grade: 'B+' },
                  { criterion: '3.2.3', score: 58, grade: 'B' },
                  { criterion: '3.2.4', score: 72, grade: 'A' }
                ].map((item) => (
                  <div key={item.criterion} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-medium text-foreground">{item.criterion}</span>
                      <span className={`text-lg font-bold ${
                        item.grade.startsWith('A') ? 'text-green-400' : 'text-yellow-400'
                      }`}>
                        {item.grade}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-32 h-2 bg-slate-700 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-gradient-to-r from-cyan-400 to-purple-600"
                          style={{ width: `${item.score}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-semibold text-foreground w-12">{item.score}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="glass-card p-6 rounded-xl border border-border/50">
              <h3 className="text-lg font-bold text-foreground mb-4">NBA Performance</h3>
              <div className="space-y-4">
                {[
                  { criterion: 'C1', score: 68, grade: 'B+' },
                  { criterion: 'C2', score: 71, grade: 'A' },
                  { criterion: 'C3', score: 62, grade: 'B' },
                  { criterion: 'C4', score: 75, grade: 'A+' }
                ].map((item) => (
                  <div key={item.criterion} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-medium text-foreground">{item.criterion}</span>
                      <span className={`text-lg font-bold ${
                        item.grade.startsWith('A') ? 'text-green-400' : 'text-yellow-400'
                      }`}>
                        {item.grade}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-32 h-2 bg-slate-700 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-gradient-to-r from-cyan-400 to-purple-600"
                          style={{ width: `${item.score}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-semibold text-foreground w-12">{item.score}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Progress Chart Placeholder */}
          <div className="glass-card p-6 rounded-xl border border-border/50">
            <h3 className="text-lg font-bold text-foreground mb-4">Progress Over Time</h3>
            <div className="h-64 flex items-center justify-center text-muted-foreground">
              <p>Chart visualization coming soon...</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
