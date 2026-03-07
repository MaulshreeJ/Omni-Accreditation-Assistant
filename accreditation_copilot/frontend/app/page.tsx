"use client";

import { useState } from "react";
import Sidebar from "@/components/Sidebar";
import QueryPanel from "@/components/QueryPanel";
import AuditDashboard from "@/components/AuditDashboard";
import EvidenceViewer from "@/components/EvidenceViewer";
import GapAnalysisPanel from "@/components/GapAnalysisPanel";
import MetricsPanel from "@/components/MetricsPanel";
import { Sparkles } from "lucide-react";

export default function Home() {
  const [auditResult, setAuditResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleAuditComplete = (result: any) => {
    setAuditResult(result);
    setLoading(false);
  };

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Query Panel */}
        <div className="p-6 border-b border-border/50">
          <QueryPanel 
            onAuditStart={() => setLoading(true)}
            onAuditComplete={handleAuditComplete}
          />
        </div>

        {/* Dashboard Content */}
        <div className="flex-1 overflow-auto p-6">
          {loading && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="relative">
                  <div className="w-16 h-16 border-4 border-cyan-400/30 border-t-cyan-400 rounded-full animate-spin mx-auto mb-4"></div>
                  <div className="absolute inset-0 w-16 h-16 border-4 border-pink-400/30 border-t-pink-400 rounded-full animate-spin mx-auto mb-4" style={{ animationDirection: 'reverse', animationDuration: '1.5s' }}></div>
                </div>
                <p className="text-lg font-medium gradient-text">Analyzing institutional evidence...</p>
                <p className="text-sm text-muted-foreground mt-2">This may take a few moments</p>
              </div>
            </div>
          )}

          {!loading && !auditResult && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center max-w-2xl">
                <div className="mb-6 flex justify-center">
                  <div className="relative">
                    <Sparkles className="w-20 h-20 text-cyan-400 animate-pulse" />
                    <div className="absolute inset-0 w-20 h-20 text-pink-400 animate-pulse" style={{ animationDelay: '0.5s' }}>
                      <Sparkles className="w-20 h-20" />
                    </div>
                  </div>
                </div>
                <h2 className="text-4xl font-bold mb-4 gradient-text">
                  Welcome to Omni Accreditation Copilot
                </h2>
                <p className="text-lg text-muted-foreground mb-6">
                  AI-powered accreditation intelligence for NAAC and NBA frameworks
                </p>
                <div className="glass-card p-6 rounded-2xl">
                  <p className="text-sm text-cyan-400 mb-2">Get Started</p>
                  <p className="text-muted-foreground">
                    Select a framework and criterion above, then click "Run Audit" to analyze your institutional compliance
                  </p>
                </div>
              </div>
            </div>
          )}

          {!loading && auditResult && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-in fade-in duration-500">
              {/* Audit Dashboard */}
              <div className="lg:col-span-2">
                <AuditDashboard result={auditResult} />
              </div>

              {/* Evidence Viewer */}
              <div>
                <EvidenceViewer evidence={auditResult.evidence} />
              </div>

              {/* Gap Analysis */}
              <div>
                <GapAnalysisPanel 
                  gaps={auditResult.gaps} 
                  recommendations={auditResult.recommendations}
                  result={auditResult}
                />
              </div>

              {/* Metrics Panel */}
              <div className="lg:col-span-2">
                <MetricsPanel />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
