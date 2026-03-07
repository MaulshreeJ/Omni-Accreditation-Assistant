"use client";

import { motion } from "framer-motion";
import { Lightbulb, TrendingUp, Target, CheckCircle2, ArrowRight } from "lucide-react";

interface GapAnalysisPanelProps {
  gaps: any[];
  recommendations?: string[];
  result?: any;
}

export default function GapAnalysisPanel({ gaps, recommendations, result }: GapAnalysisPanelProps) {
  // Debug: Log the result to see what we're receiving
  console.log('[GapAnalysisPanel] Received result:', result);
  
  // Generate actionable recommendations based on the audit result
  const generateActionableRecommendations = () => {
    const recs = [];
    
    // Check what's covered and what's missing
    const dimensionsCovered = result?.dimensions_covered || [];
    const dimensionsMissing = result?.dimensions_missing || [];
    const confidenceScore = result?.confidence_score || 0;
    const coverageRatio = result?.coverage_ratio || 0;
    
    console.log('[GapAnalysisPanel] Dimensions covered:', dimensionsCovered);
    console.log('[GapAnalysisPanel] Dimensions missing:', dimensionsMissing);
    console.log('[GapAnalysisPanel] Confidence:', confidenceScore);
    console.log('[GapAnalysisPanel] Coverage:', coverageRatio);
    
    // Recommendation 1: Based on confidence score
    if (confidenceScore < 0.3) {
      recs.push({
        title: "Strengthen Evidence Documentation",
        description: "Your current evidence is weak. To move from B+ to A+, you need comprehensive documentation with specific numbers, dates, and proof.",
        actions: [
          "Collect detailed data for all research projects with funding amounts",
          "Document all externally funded projects with agency names and dates",
          "Maintain year-wise records for the last 5 years",
          "Include supporting documents like sanction letters and completion reports"
        ],
        priority: "High",
        impact: "Can improve score by 20-30%"
      });
    }
    
    // Recommendation 2: Based on missing dimensions
    if (dimensionsMissing.length > 0) {
      const missingDims = dimensionsMissing.map(d => {
        if (d === 'funding_amount') return 'total research funding amounts';
        if (d === 'project_count') return 'number of funded projects';
        if (d === 'funding_agencies') return 'funding agency details';
        if (d === 'time_period') return 'year-wise breakdown';
        return d;
      }).join(', ');
      
      recs.push({
        title: `Add Missing Information: ${missingDims}`,
        description: `You're missing critical data that NAAC requires for A+ grade. Add these specific details to your documentation.`,
        actions: [
          `Provide complete ${missingDims} in your institutional reports`,
          "Ensure all data is verifiable with supporting documents",
          "Update your Self-Study Report (SSR) with this information"
        ],
        priority: "Critical",
        impact: "Required for A+ grade"
      });
    }
    
    // Recommendation 3: Based on coverage
    if (coverageRatio === 1.0 && confidenceScore < 0.5) {
      recs.push({
        title: "Improve Evidence Quality",
        description: "You have all required dimensions covered, but the evidence quality is insufficient. Focus on providing detailed, quantitative data.",
        actions: [
          "Replace vague statements with specific numbers and metrics",
          "Add tables showing year-wise data for the last 5 years",
          "Include proof documents: sanction letters, completion certificates, publications",
          "Provide institutional data, not just framework guidelines"
        ],
        priority: "High",
        impact: "Can improve score by 15-25%"
      });
    }
    
    // Recommendation 4: Specific to research funding (3.2.1)
    if (result?.criterion === '3.2.1') {
      recs.push({
        title: "Enhance Research Funding Documentation",
        description: "For NAAC Criterion 3.2.1 (Extramural Research Funding), A+ grade requires substantial evidence of external funding.",
        actions: [
          "Document total research funding received (minimum ₹50 Lakhs for A+)",
          "List all externally funded projects with PI names, departments, and amounts",
          "Show funding from multiple agencies (DST, SERB, DBT, ICSSR, Industry)",
          "Provide year-wise breakdown showing consistent funding growth",
          "Include copies of sanction letters and utilization certificates"
        ],
        priority: "Critical",
        impact: "Essential for A+ in this criterion"
      });
    }
    
    // Recommendation 5: General improvement
    recs.push({
      title: "Overall Strategy to Reach A+ Grade",
      description: "Moving from B+ to A+ requires systematic improvement across all criteria.",
      actions: [
        "Conduct internal audit of all NAAC criteria to identify weak areas",
        "Set up a dedicated NAAC cell to maintain continuous documentation",
        "Organize faculty training on research proposal writing and funding acquisition",
        "Establish industry partnerships for collaborative research projects",
        "Create a digital repository of all evidence documents for easy access"
      ],
      priority: "Medium",
      impact: "Long-term improvement strategy"
    });
    
    return recs;
  };
  
  const actionableRecommendations = generateActionableRecommendations();
  
  // If no recommendations were generated, show a default message
  if (actionableRecommendations.length === 0) {
    return (
      <div className="bg-card rounded-lg border border-border p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 rounded-lg bg-primary/10">
            <TrendingUp className="text-primary" size={24} />
          </div>
          <div>
            <h3 className="text-xl font-bold">Roadmap to A+ Grade</h3>
            <p className="text-sm text-muted-foreground">
              Actionable steps to improve from B+ to A+
            </p>
          </div>
        </div>
        <div className="text-center py-8">
          <p className="text-muted-foreground">
            No specific recommendations available. Please ensure audit data is complete.
          </p>
        </div>
      </div>
    );
  }
  
  const getPriorityColor = (priority: string) => {
    switch (priority?.toLowerCase()) {
      case 'critical':
        return 'border-red-500 bg-red-500/10 text-red-600';
      case 'high':
        return 'border-orange-500 bg-orange-500/10 text-orange-600';
      case 'medium':
        return 'border-yellow-500 bg-yellow-500/10 text-yellow-600';
      default:
        return 'border-blue-500 bg-blue-500/10 text-blue-600';
    }
  };

  return (
    <div className="bg-card rounded-lg border border-border p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 rounded-lg bg-primary/10">
          <TrendingUp className="text-primary" size={24} />
        </div>
        <div>
          <h3 className="text-xl font-bold">Roadmap to A+ Grade</h3>
          <p className="text-sm text-muted-foreground">
            Actionable steps to improve from B+ to A+
          </p>
        </div>
      </div>
      
      <div className="space-y-6">
        {actionableRecommendations.map((rec, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.15 }}
            className="rounded-xl border border-border bg-background/50 p-6 hover:shadow-lg transition-all"
          >
            {/* Header */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-start gap-3 flex-1">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-sm font-bold text-primary">
                  {index + 1}
                </div>
                <div className="flex-1">
                  <h4 className="font-semibold text-lg mb-1">{rec.title}</h4>
                  <p className="text-sm text-muted-foreground">{rec.description}</p>
                </div>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getPriorityColor(rec.priority)}`}>
                {rec.priority}
              </span>
            </div>
            
            {/* Action Items */}
            <div className="space-y-2 mb-4">
              <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground mb-2">
                <Target size={16} />
                <span>Action Items:</span>
              </div>
              {rec.actions.map((action, actionIndex) => (
                <div key={actionIndex} className="flex items-start gap-3 pl-6">
                  <CheckCircle2 size={16} className="text-green-500 flex-shrink-0 mt-0.5" />
                  <p className="text-sm flex-1">{action}</p>
                </div>
              ))}
            </div>
            
            {/* Impact */}
            <div className="flex items-center gap-2 pt-4 border-t border-border/50">
              <Lightbulb size={16} className="text-yellow-500" />
              <span className="text-sm font-medium">Expected Impact:</span>
              <span className="text-sm text-primary">{rec.impact}</span>
            </div>
          </motion.div>
        ))}
        
        {/* Summary Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: actionableRecommendations.length * 0.15 }}
          className="rounded-xl border-2 border-primary/30 bg-primary/5 p-6"
        >
          <div className="flex items-start gap-4">
            <div className="p-3 rounded-lg bg-primary/20">
              <ArrowRight className="text-primary" size={24} />
            </div>
            <div className="flex-1">
              <h4 className="font-bold text-lg mb-2">Next Steps</h4>
              <p className="text-sm text-muted-foreground mb-4">
                Start with the Critical and High priority items first. Focus on collecting comprehensive evidence with specific numbers, dates, and supporting documents. Regular monitoring and documentation will help you achieve A+ grade in the next assessment cycle.
              </p>
              <div className="flex items-center gap-2 text-sm font-medium text-primary">
                <span>Timeline: 6-12 months for significant improvement</span>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
