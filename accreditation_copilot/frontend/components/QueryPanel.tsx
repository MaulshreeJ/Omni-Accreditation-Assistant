"use client";

import { useState, useRef } from "react";
import { Mic, Upload, Send, X, Loader2 } from "lucide-react";

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
  const [isUploading, setIsUploading] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Voice input using Web Speech API
  const startVoiceInput = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert('Voice input not supported in this browser. Please use Chrome or Edge.');
      return;
    }

    const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setQuery(transcript);
      setIsListening(false);
    };

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      setIsListening(false);
      if (event.error !== 'no-speech') {
        alert(`Voice input error: ${event.error}`);
      }
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    try {
      recognition.start();
    } catch (error) {
      console.error('Failed to start recognition:', error);
      setIsListening(false);
    }
  };

  // File upload handler
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      const validFiles = files.filter(file => {
        const ext = file.name.toLowerCase();
        return ext.endsWith('.pdf') || ext.endsWith('.png') || ext.endsWith('.jpg') || ext.endsWith('.jpeg');
      });
      
      if (validFiles.length !== files.length) {
        alert('Some files were skipped. Only PDF, PNG, and JPG files are allowed.');
      }
      
      setUploadedFiles(prev => [...prev, ...validFiles]);
    }
  };

  // Upload files to backend
  const uploadFilesToBackend = async () => {
    if (uploadedFiles.length === 0) return;

    setIsUploading(true);
    try {
      const formData = new FormData();
      uploadedFiles.forEach(file => {
        formData.append('files', file);
      });

      const response = await fetch('http://localhost:8000/api/upload/', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const result = await response.json();
      console.log('Upload successful:', result);
      alert(`Successfully uploaded ${uploadedFiles.length} file(s). Click "Ingest Files" to process them.`);
    } catch (error) {
      console.error('Upload failed:', error);
      alert('File upload failed. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  // Trigger ingestion
  const handleIngestFiles = async () => {
    setIsUploading(true);
    try {
      const response = await fetch('http://localhost:8000/api/upload/ingest', {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Ingestion failed');
      }

      const result = await response.json();
      console.log('Ingestion successful:', result);
      alert('Files ingested successfully! You can now run audits.');
    } catch (error) {
      console.error('Ingestion failed:', error);
      alert('File ingestion failed. Please check the backend logs.');
    } finally {
      setIsUploading(false);
    }
  };

  // Run audit
  const handleRunAudit = async () => {
    if (!criterion.trim()) {
      alert('Please enter a criterion (e.g., 3.2.1 for NAAC or C5 for NBA)');
      return;
    }

    // Upload files first if any
    if (uploadedFiles.length > 0) {
      await uploadFilesToBackend();
    }

    setIsRunning(true);
    onAuditStart();

    try {
      const response = await fetch('http://localhost:8000/api/audit/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          framework,
          criterion: criterion.trim(),
          query: query.trim() || null,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Audit failed');
      }

      const result = await response.json();
      onAuditComplete(result);
    } catch (error: any) {
      console.error('Audit failed:', error);
      alert(error.message || 'Audit failed. Please check if the backend is running and try again.');
      onAuditComplete(null);
    } finally {
      setIsRunning(false);
    }
  };

  // Remove uploaded file
  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-4">
      {/* Framework and Criterion Selection */}
      <div className="flex gap-4">
        <div className="flex-1">
          <label className="block text-sm font-medium mb-2 text-cyan-400">Framework</label>
          <select
            value={framework}
            onChange={(e) => setFramework(e.target.value)}
            className="w-full px-4 py-3 glass-card rounded-xl focus:outline-none focus:ring-2 focus:ring-primary transition-all hover-glow"
            disabled={isRunning}
          >
            <option value="NAAC">NAAC</option>
            <option value="NBA">NBA</option>
          </select>
        </div>
        <div className="flex-1">
          <label className="block text-sm font-medium mb-2 text-cyan-400">Criterion</label>
          <input
            type="text"
            value={criterion}
            onChange={(e) => setCriterion(e.target.value)}
            placeholder="e.g., 3.2.1 or C5"
            className="w-full px-4 py-3 glass-card rounded-xl focus:outline-none focus:ring-2 focus:ring-primary transition-all hover-glow"
            disabled={isRunning}
          />
        </div>
      </div>

      {/* Query Input */}
      <div>
        <label className="block text-sm font-medium mb-2 text-cyan-400">Query (Optional)</label>
        <div className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your query or use voice input..."
            className="flex-1 px-4 py-3 glass-card rounded-xl focus:outline-none focus:ring-2 focus:ring-primary transition-all hover-glow"
            disabled={isRunning}
          />
          
          {/* Voice Input Button */}
          <button
            onClick={startVoiceInput}
            disabled={isRunning || isListening}
            className={`px-4 py-3 rounded-xl transition-all hover-glow ${
              isListening
                ? 'bg-red-500/20 text-red-400 glow-pink animate-pulse'
                : 'glass-card text-cyan-400 hover:glow-cyan'
            }`}
            title="Voice Input"
          >
            <Mic size={20} className={isListening ? 'animate-pulse' : ''} />
          </button>
          
          {/* Upload Button */}
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isRunning}
            className="px-4 py-3 glass-card text-pink-400 rounded-xl hover:glow-pink transition-all hover-glow"
            title="Upload Files"
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
          
          {/* Run Audit Button */}
          <button
            onClick={handleRunAudit}
            disabled={isRunning || !criterion.trim()}
            className="px-6 py-3 gradient-bg text-white rounded-xl hover:opacity-90 transition-all flex items-center gap-2 font-medium disabled:opacity-50 disabled:cursor-not-allowed hover-glow"
          >
            {isRunning ? (
              <>
                <Loader2 size={20} className="animate-spin" />
                Running...
              </>
            ) : (
              <>
                <Send size={20} />
                Run Audit
              </>
            )}
          </button>
        </div>
      </div>

      {/* Uploaded Files Preview */}
      {uploadedFiles.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-cyan-400">
              Uploaded Files ({uploadedFiles.length})
            </label>
            <div className="flex items-center gap-2">
              {isUploading && (
                <span className="text-sm text-muted-foreground flex items-center gap-2">
                  <Loader2 size={16} className="animate-spin" />
                  Processing...
                </span>
              )}
              <button
                onClick={handleIngestFiles}
                disabled={isUploading}
                className="px-3 py-1 text-sm gradient-bg text-white rounded-lg hover:opacity-90 transition-all disabled:opacity-50"
              >
                Ingest Files
              </button>
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            {uploadedFiles.map((file, index) => (
              <div
                key={index}
                className="px-3 py-2 glass-card rounded-full text-sm flex items-center gap-2 hover-glow"
              >
                <span className="text-cyan-400">{file.name}</span>
                <span className="text-muted-foreground text-xs">
                  ({(file.size / 1024).toFixed(1)} KB)
                </span>
                <button
                  onClick={() => removeFile(index)}
                  className="hover:text-red-400 transition-colors"
                  disabled={isUploading}
                >
                  <X size={16} />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Voice Listening Indicator */}
      {isListening && (
        <div className="flex items-center gap-2 text-sm text-cyan-400 animate-pulse">
          <div className="w-2 h-2 bg-cyan-400 rounded-full animate-ping"></div>
          Listening... Speak now
        </div>
      )}
    </div>
  );
}
