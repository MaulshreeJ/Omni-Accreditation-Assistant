'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import { Clock, FileText, TrendingUp, TrendingDown, Calendar } from 'lucide-react';

export default function HistoryPage() {
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

  // Mock history data
  const auditHistory = [
    {
      id: 1,
      criterion: '3.2.1',
      framework: 'NAAC',
      date: '2024-01-15',
      confidence: 74,
      grade: 'A+',
      status: 'Compliant',
      trend: 'up'
    },
    {
      id: 2,
      criterion: '3.2.1',
      framework: 'NAAC',
      date: '2024-01-14',
      confidence: 59,
      grade: 'B+',
      status: 'Compliant',
      trend: 'up'
    },
    {
      id: 3,
      criterion: '3.2.1',
      framework: 'NAAC',
      date: '2024-01-13',
      confidence: 28,
      grade: 'C',
      status: 'Weak',
      trend: 'down'
    }
  ];

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <Sidebar />
      
      <div className="flex-1 overflow-auto p-8">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold gradient-text mb-2">Audit History</h1>
            <p className="text-muted-foreground">View your past audit results and track progress</p>
          </div>

          {/* Stats Overview */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="glass-card p-6 rounded-xl border border-border/50">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-muted-foreground">Total Audits</p>
                <FileText size={20} className="text-cyan-400" />
              </div>
              <p className="text-3xl font-bold text-foreground">12</p>
            </div>
            <div className="glass-card p-6 rounded-xl border border-border/50">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-muted-foreground">Avg Score</p>
                <TrendingUp size={20} className="text-green-400" />
              </div>
              <p className="text-3xl font-bold text-green-400">68%</p>
            </div>
            <div className="glass-card p-6 rounded-xl border border-border/50">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-muted-foreground">This Month</p>
                <Calendar size={20} className="text-purple-400" />
              </div>
              <p className="text-3xl font-bold text-purple-400">8</p>
            </div>
            <div className="glass-card p-6 rounded-xl border border-border/50">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-muted-foreground">Improvement</p>
                <TrendingUp size={20} className="text-cyan-400" />
              </div>
              <p className="text-3xl font-bold text-cyan-400">+15%</p>
            </div>
          </div>

          {/* History Table */}
          <div className="glass-card rounded-2xl border border-border/50 overflow-hidden">
            <div className="p-6 border-b border-border/50">
              <h2 className="text-xl font-bold text-foreground">Recent Audits</h2>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-900/50">
                  <tr>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">Date</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">Framework</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">Criterion</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">Confidence</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">Grade</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">Status</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-slate-300">Trend</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/50">
                  {auditHistory.map((audit) => (
                    <tr key={audit.id} className="hover:bg-slate-900/30 transition cursor-pointer">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2 text-sm text-foreground">
                          <Clock size={16} className="text-muted-foreground" />
                          {new Date(audit.date).toLocaleDateString()}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="px-3 py-1 bg-cyan-500/10 text-cyan-400 rounded-full text-sm font-medium">
                          {audit.framework}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm font-medium text-foreground">{audit.criterion}</td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <div className="w-24 h-2 bg-slate-700 rounded-full overflow-hidden">
                            <div 
                              className="h-full bg-gradient-to-r from-cyan-400 to-purple-600"
                              style={{ width: `${audit.confidence}%` }}
                            ></div>
                          </div>
                          <span className="text-sm font-semibold text-foreground">{audit.confidence}%</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`text-2xl font-bold ${
                          audit.grade.startsWith('A') ? 'text-green-400' :
                          audit.grade.startsWith('B') ? 'text-yellow-400' :
                          'text-red-400'
                        }`}>
                          {audit.grade}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                          audit.status === 'Compliant' ? 'bg-green-500/10 text-green-400' :
                          audit.status === 'Weak' ? 'bg-red-500/10 text-red-400' :
                          'bg-yellow-500/10 text-yellow-400'
                        }`}>
                          {audit.status}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        {audit.trend === 'up' ? (
                          <TrendingUp size={20} className="text-green-400" />
                        ) : (
                          <TrendingDown size={20} className="text-red-400" />
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
