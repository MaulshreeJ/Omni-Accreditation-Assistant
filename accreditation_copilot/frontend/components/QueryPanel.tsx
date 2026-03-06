"use client";

import { useState, useRef } from "react";
import { Mic, Upload, Send } from "lucide-react";

interface QueryPanelProps {
  onAuditStart: () => void;
  onAuditComplete: (result: any) => void;
}

export default function QueryPanel({ onAuditStart, onAuditComplete }: QueryPanelProps) {
  const [query, setQuery] = useState("");
  const [framework, setFramework] = useState("NAAC");
  const [criterion, setCriterion] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Voice input using Web Speech API
  const startVoiceInput = () => {
    if (!('webkitSpeechRecognition' in window)) {
      alert('Voice input not supported in this browser');
      return;
    }

    const recognition = new (window as any).webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setQuery(transcript);
      setIsListening(false);
    };

    recognition.onerror = () => {
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.start();
  };

  // File upload handler
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      setUploadedFiles(prev => [...prev, ...files]);
    }
  };

  // Run audit
  const handleRunAudit = async () => {
    if (!criterion) {
      alert('Please enter a criterion');
      return;
    }

    onAuditStart();

    try {
      const response = await fetch('http://localhost:8000/api/audit/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          framework,
          criterion,
          query: query || null,
        }),
      });

      const result = await response.json();
      onAuditComplete(result);
    } catch (error) {
      console.error('Audit failed:', error);
      alert('Audit failed. Please try again.');
    }
  };

  return (
    <div className="space-y-4">
      {/* Framework and Criterion Selection */}
      <div className="flex gap-4">
        <div className="flex-1">
          <label className="block text-sm font-medium mb-2">Framework</label>
          <select
            value={framework}
            onChange={(e) => setFramework(e.target.value)}
            className="w-full px-4 py-2 bg-card border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="NAAC">NAAC</option>
            <option value="NBA">NBA</option>
          </select>
        </div>
        <div className="flex-1">
          <label className="block text-sm font-medium mb-2">Criterion</label>
          <input
            type="text"
            value={criterion}
            onChange={(e) => setCriterion(e.target.value)}
            placeholder="e.g., 3.2.1"
            className="w-full px-4 py-2 bg-card border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
      </div>

      {/* Query Input */}
      <div>
        <label className="block text-sm font-medium mb-2">Query (Optional)</label>
        <div className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your query or use voice input..."
            className="flex-1 px-4 py-2 bg-card border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
          />
          <button
            onClick={startVoiceInput}
            className={`px-4 py-2 rounded-lg transition-colors ${
              isListening
                ? 'bg-destructive text-destructive-foreground'
                : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
            }`}
          >
            <Mic size={20} />
          </button>
          <button
            onClick={() => fileInputRef.current?.click()}
            className="px-4 py-2 bg-secondary text-secondary-foreground rounded-lg hover:bg-secondary/80 transition-colors"
          >
            <Upload size={20} />
          </button>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.png,.jpg,.jpeg"
            onChange={handleFileUpload}
            className="hidden"
          />
          <button
            onClick={handleRunAudit}
            className="px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors flex items-center gap-2"
          >
            <Send size={20} />
            Run Audit
          </button>
        </div>
      </div>

      {/* Uploaded Files Preview */}
      {uploadedFiles.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {uploadedFiles.map((file, index) => (
            <div
              key={index}
              className="px-3 py-1 bg-secondary text-secondary-foreground rounded-full text-sm flex items-center gap-2"
            >
              <span>{file.name}</span>
              <button
                onClick={() => setUploadedFiles(prev => prev.filter((_, i) => i !== index))}
                className="hover:text-destructive"
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Voice Transcript Indicator */}
      {isListening && (
        <div className="text-sm text-muted-foreground animate-pulse">
          Listening...
        </div>
      )}
    </div>
  );
}
