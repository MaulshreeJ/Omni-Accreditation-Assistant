"use client";

import { motion } from "framer-motion";
import { CheckCircle2, AlertCircle, XCircle, Clock } from "lucide-react";

interface AuditDashboardProps {
  result: any;
}

export default function AuditDashboard({ result }: AuditDashboardProps) {
  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'compliant':
        return <CheckCircle2 className="text-green-500" size={24} />;
      case 'partially_compliant':
        return <AlertCircle className="text-yellow-500" size={24} />;
      case 'non_compliant':
        return <XCircle className="text-red-500" size={24} />;
      default:
        return <Clock className="text-gray-500" size={24} />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'compliant':
        return 'text-green-500';
      case 'partially_compliant':
        return 'text-yellow-500';
      case 'non_compliant':
        return 'text-red-500';
      default:
        return 'text-gray-500';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-card rounded-lg border border-border p-6"
    >
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold">Audit Results</h2>
          <p className="text-muted-foreground">
            {result.framework} Criterion {result.criterion}
          </p>
        </div>
        {result.cached && (
          <span className="px-3 py-1 bg-primary/20 text-primary rounded-full text-sm">
            Cached
          </span>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Compliance Status */}
        <div className="bg-background rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            {getStatusIcon(result.compliance_status)}
            <span className="text-sm text-muted-foreground">Status</span>
          </div>
          <p className={`text-lg font-semibold ${getStatusColor(result.compliance_status)}`}>
            {result.compliance_status.replace('_', ' ')}
          </p>
        </div>

        {/* Confidence Score */}
        <div className="bg-background rounded-lg p-4">
          <p className="text-sm text-muted-foreground mb-2">Confidence</p>
          <div className="flex items-end gap-2">
            <p className="text-2xl font-bold">{(result.confidence_score * 100).toFixed(0)}%</p>
          </div>
          <div className="w-full bg-secondary rounded-full h-2 mt-2">
            <div
              className="bg-primary h-2 rounded-full transition-all"
              style={{ width: `${result.confidence_score * 100}%` }}
            />
          </div>
        </div>

        {/* Coverage Ratio */}
        <div className="bg-background rounded-lg p-4">
          <p className="text-sm text-muted-foreground mb-2">Coverage</p>
          <div className="flex items-end gap-2">
            <p className="text-2xl font-bold">{(result.coverage_ratio * 100).toFixed(0)}%</p>
          </div>
          <div className="w-full bg-secondary rounded-full h-2 mt-2">
            <div
              className="bg-green-500 h-2 rounded-full transition-all"
              style={{ width: `${result.coverage_ratio * 100}%` }}
            />
          </div>
        </div>

        {/* Evidence Count */}
        <div className="bg-background rounded-lg p-4">
          <p className="text-sm text-muted-foreground mb-2">Evidence</p>
          <p className="text-2xl font-bold">{result.evidence_count}</p>
          <p className="text-sm text-muted-foreground mt-1">chunks found</p>
        </div>
      </div>
    </motion.div>
  );
}
