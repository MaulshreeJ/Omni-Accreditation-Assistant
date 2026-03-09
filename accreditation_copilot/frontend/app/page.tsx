"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "@/components/Sidebar";
import QueryPanel from "@/components/QueryPanel";
import AuditDashboard from "@/components/AuditDashboard";
import EvidenceViewer from "@/components/EvidenceViewer";
import GapAnalysisPanel from "@/components/GapAnalysisPanel";
import MetricsPanel from "@/components/MetricsPanel";
import ComparisonComponent from "@/components/ComparisonComponent";
import RecommendationEngine from "@/components/RecommendationEngine";
import GapAnalysisVisualizer from "@/components/GapAnalysisVisualizer";
import { Sparkles } from "lucide-react";

export default function Home() {
  const router = useRouter();
  const [auditResult, setAuditResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [checkingAuth, setCheckingAuth] = useState(true);

  useEffect(() => {
    // Check authentication
    const auth = localStorage.getItem('isAuthenticated');
    if (auth === 'true') {
      setIsAuthenticated(true);
    } else {
      router.push('/login');
    }
    setCheckingAuth(false);
  }, [router]);

  const handleAuditComplete = (result: any) => {
    setAuditResult(result);
    setLoading(false);
  };

  // Show loading while checking auth
  if (checkingAuth) {
    return (
      <div className="flex items-center justify-center h-screen bg-background">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-cyan-400/30 border-t-cyan-400 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-lg font-medium gradient-text">Loading...</p>
        </div>
      </div>
    );
  }

  // Don't render if not authenticated
  if (!isAuthenticated) {
    return null;
  }

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
            <div className="space-y-6 animate-in fade-in duration-500">
              {/* Audit Dashboard */}
              <AuditDashboard result={auditResult} />

              {/* NAAC vs Institutional Comparison */}
              {auditResult.dimensions && auditResult.dimensions.length > 0 && (
                <ComparisonComponent 
                  dimensions={auditResult.dimensions}
                  coverageRatio={auditResult.coverage_ratio || 0}
                />
              )}

              {/* Gap Analysis Visualizer */}
              {auditResult.gaps && auditResult.gaps.length > 0 && (
                <GapAnalysisVisualizer 
                  gaps={auditResult.gaps}
                  coverageRatio={auditResult.coverage_ratio || 0}
                  totalDimensions={auditResult.dimensions?.length || 0}
                  coveredDimensions={auditResult.dimensions_covered || []}
                  missingDimensions={auditResult.dimensions_missing || []}
                />
              )}

              {/* Recommendations */}
              <RecommendationEngine 
                confidenceScore={auditResult.confidence_score || 0}
                coverageRatio={auditResult.coverage_ratio || 0}
                missingDimensions={auditResult.dimensions_missing || []}
                criterionId={auditResult.criterion || ""}
                showTopOnly={false}
              />

              {/* Evidence Viewer */}
              <EvidenceViewer 
                evidence={auditResult.evidence}
                dimensions={auditResult.dimensions_covered || []}
              />

              {/* Legacy Gap Analysis Panel (for backward compatibility) */}
              <GapAnalysisPanel 
                gaps={auditResult.gaps} 
                recommendations={auditResult.recommendations}
                result={auditResult}
              />

              {/* Metrics Panel */}
              <MetricsPanel />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
