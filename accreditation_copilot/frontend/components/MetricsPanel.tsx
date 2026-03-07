"use client";

import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { motion } from "framer-motion";

export default function MetricsPanel() {
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/metrics/');
      const data = await response.json();
      setMetrics(data);
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-card rounded-lg border border-border p-6">
        <h3 className="text-xl font-bold mb-4">Retrieval Metrics</h3>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="bg-card rounded-lg border border-border p-6">
        <h3 className="text-xl font-bold mb-4">Retrieval Metrics</h3>
        <p className="text-center text-muted-foreground py-8">
          Failed to load metrics
        </p>
      </div>
    );
  }

  const chartData = [
    { name: 'Precision', value: metrics.precision * 100 },
    { name: 'Recall', value: metrics.recall * 100 },
    { name: 'F1 Score', value: metrics.f1 * 100 },
    { name: 'MRR', value: metrics.mrr * 100 },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-card rounded-lg border border-border p-6"
    >
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-bold">Retrieval Metrics</h3>
          <p className="text-sm text-muted-foreground">
            Evaluated on {metrics.num_queries} queries (Top-{metrics.top_k})
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Chart */}
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="name" stroke="#888" />
              <YAxis stroke="#888" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1a1a1a',
                  border: '1px solid #333',
                  borderRadius: '8px',
                }}
              />
              <Bar dataKey="value" fill="#3b82f6" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Metrics Cards */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-background rounded-lg p-4">
            <p className="text-sm text-muted-foreground mb-1">Precision@{metrics.top_k}</p>
            <p className="text-2xl font-bold">{(metrics.precision * 100).toFixed(1)}%</p>
          </div>
          <div className="bg-background rounded-lg p-4">
            <p className="text-sm text-muted-foreground mb-1">Recall@{metrics.top_k}</p>
            <p className="text-2xl font-bold">{(metrics.recall * 100).toFixed(1)}%</p>
          </div>
          <div className="bg-background rounded-lg p-4">
            <p className="text-sm text-muted-foreground mb-1">F1 Score@{metrics.top_k}</p>
            <p className="text-2xl font-bold">{(metrics.f1 * 100).toFixed(1)}%</p>
          </div>
          <div className="bg-background rounded-lg p-4">
            <p className="text-sm text-muted-foreground mb-1">MRR</p>
            <p className="text-2xl font-bold">{(metrics.mrr * 100).toFixed(1)}%</p>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
