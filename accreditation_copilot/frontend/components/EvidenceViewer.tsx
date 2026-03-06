"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { FileText, ChevronDown, ChevronUp } from "lucide-react";

interface EvidenceViewerProps {
  evidence: any[];
}

export default function EvidenceViewer({ evidence }: EvidenceViewerProps) {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  const getStrengthColor = (strength: string) => {
    switch (strength?.toLowerCase()) {
      case 'strong':
        return 'text-green-500 bg-green-500/10';
      case 'moderate':
        return 'text-yellow-500 bg-yellow-500/10';
      case 'weak':
        return 'text-red-500 bg-red-500/10';
      default:
        return 'text-gray-500 bg-gray-500/10';
    }
  };

  return (
    <div className="bg-card rounded-lg border border-border p-6">
      <h3 className="text-xl font-bold mb-4">Evidence</h3>
      
      <div className="space-y-3">
        {evidence && evidence.length > 0 ? (
          evidence.map((item, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-background rounded-lg border border-border overflow-hidden"
            >
              <div
                className="p-4 cursor-pointer hover:bg-accent/50 transition-colors"
                onClick={() => setExpandedIndex(expandedIndex === index ? null : index)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <FileText size={16} className="text-muted-foreground" />
                      <span className="text-sm font-medium">
                        {item.source || 'Unknown Source'}
                      </span>
                      {item.page && (
                        <span className="text-xs text-muted-foreground">
                          Page {item.page}
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground line-clamp-2">
                      {item.text || item.child_text || 'No text available'}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 ml-4">
                    {item.strength && (
                      <span className={`px-2 py-1 rounded text-xs ${getStrengthColor(item.strength)}`}>
                        {item.strength}
                      </span>
                    )}
                    {item.reranker_score && (
                      <span className="text-xs text-muted-foreground">
                        {(item.reranker_score * 100).toFixed(0)}%
                      </span>
                    )}
                    {expandedIndex === index ? (
                      <ChevronUp size={20} />
                    ) : (
                      <ChevronDown size={20} />
                    )}
                  </div>
                </div>
              </div>

              {expandedIndex === index && (
                <motion.div
                  initial={{ height: 0 }}
                  animate={{ height: 'auto' }}
                  exit={{ height: 0 }}
                  className="border-t border-border p-4 bg-accent/20"
                >
                  <p className="text-sm whitespace-pre-wrap">
                    {item.text || item.child_text || 'No text available'}
                  </p>
                  {item.metadata && (
                    <div className="mt-3 pt-3 border-t border-border">
                      <p className="text-xs text-muted-foreground">
                        Metadata: {JSON.stringify(item.metadata, null, 2)}
                      </p>
                    </div>
                  )}
                </motion.div>
              )}
            </motion.div>
          ))
        ) : (
          <p className="text-center text-muted-foreground py-8">
            No evidence found
          </p>
        )}
      </div>
    </div>
  );
}
