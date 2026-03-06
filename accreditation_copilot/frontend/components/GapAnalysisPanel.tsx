"use client";

import { motion } from "framer-motion";
import { AlertTriangle, Info, XCircle } from "lucide-react";

interface GapAnalysisPanelProps {
  gaps: any[];
}

export default function GapAnalysisPanel({ gaps }: GapAnalysisPanelProps) {
  const getSeverityIcon = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'high':
        return <XCircle className="text-red-500" size={20} />;
      case 'medium':
        return <AlertTriangle className="text-yellow-500" size={20} />;
      case 'low':
        return <Info className="text-blue-500" size={20} />;
      default:
        return <Info className="text-gray-500" size={20} />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'high':
        return 'border-red-500 bg-red-500/10';
      case 'medium':
        return 'border-yellow-500 bg-yellow-500/10';
      case 'low':
        return 'border-blue-500 bg-blue-500/10';
      default:
        return 'border-gray-500 bg-gray-500/10';
    }
  };

  return (
    <div className="bg-card rounded-lg border border-border p-6">
      <h3 className="text-xl font-bold mb-4">Gap Analysis</h3>
      
      <div className="space-y-3">
        {gaps && gaps.length > 0 ? (
          gaps.map((gap, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`rounded-lg border-l-4 p-4 ${getSeverityColor(gap.severity)}`}
            >
              <div className="flex items-start gap-3">
                {getSeverityIcon(gap.severity)}
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-semibold">{gap.type || 'Gap'}</span>
                    {gap.severity && (
                      <span className="text-xs px-2 py-0.5 rounded bg-background">
                        {gap.severity}
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground mb-2">
                    {gap.description || 'No description available'}
                  </p>
                  {gap.recommendation && (
                    <div className="mt-2 pt-2 border-t border-border/50">
                      <p className="text-xs font-medium mb-1">Recommendation:</p>
                      <p className="text-xs text-muted-foreground">
                        {gap.recommendation}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          ))
        ) : (
          <div className="text-center py-8">
            <p className="text-muted-foreground">No gaps detected</p>
            <p className="text-sm text-muted-foreground mt-1">
              All compliance dimensions are covered
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
