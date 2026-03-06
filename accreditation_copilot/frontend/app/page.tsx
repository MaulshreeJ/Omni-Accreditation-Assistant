"use client";

import { useState } from "react";
import Sidebar from "@/components/Sidebar";
import QueryPanel from "@/components/QueryPanel";
import AuditDashboard from "@/components/AuditDashboard";
import EvidenceViewer from "@/components/EvidenceViewer";
import GapAnalysisPanel from "@/components/GapAnalysisPanel";
import MetricsPanel from "@/components/MetricsPanel";

export default function Home() {
  const [auditResult, setAuditResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleAuditComplete = (result: any) => {
    setAuditResult(result);
    setLoading(false);
  };

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Query Panel */}
        <div className="p-6 border-b border-border">
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
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
                <p className="text-muted-foreground">Running audit...</p>
              </div>
            </div>
          )}

          {!loading && !auditResult && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <h2 className="text-2xl font-bold mb-2">Welcome to Omni Accreditation Copilot</h2>
                <p className="text-muted-foreground">
                  Enter a query above to start an audit
                </p>
              </div>
            </div>
          )}

          {!loading && auditResult && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
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
                <GapAnalysisPanel gaps={auditResult.gaps} />
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
