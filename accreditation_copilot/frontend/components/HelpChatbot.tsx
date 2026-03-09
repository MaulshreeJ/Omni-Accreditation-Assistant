'use client';

import { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, Sparkles } from 'lucide-react';

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

export default function HelpChatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "Hi! I'm Omni Assistant 👋 I'm here to help you navigate the accreditation system. Ask me anything about how to use the platform, improve your scores, or understand your audit results!",
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const getBotResponse = async (userMessage: string): Promise<string> => {
    try {
      // Call AI backend with shorter timeout for faster responses
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
      
      const response = await fetch('http://localhost:8000/api/chatbot/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          history: messages.slice(-5).map(m => ({  // Reduced to last 5 for speed
            role: m.sender === 'user' ? 'user' : 'assistant',
            content: m.text
          }))
        }),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      return data.response;
    } catch (error: any) {
      console.error('Chatbot error:', error);
      
      // Provide helpful fallback responses based on the question
      const lowerMessage = userMessage.toLowerCase();
      
      if (lowerMessage.includes('start') || lowerMessage.includes('begin')) {
        return "To get started:\n1. Upload your SSR PDF (max 20MB)\n2. Click 'Ingest Files' to process\n3. Select framework (NAAC/NBA) and criterion\n4. Click 'Run Audit' to see results\n\nNote: I'm currently offline, but these steps should help you get started!";
      } else if (lowerMessage.includes('upload')) {
        return "To upload documents:\n1. Click the upload area on the Dashboard\n2. Select your SSR PDF file (max 20MB)\n3. Wait for upload to complete\n4. Click 'Ingest Files' to process the document\n\nNote: I'm currently offline, but this should help!";
      } else if (lowerMessage.includes('improve') || lowerMessage.includes('score')) {
        return "To improve your score:\n→ Include detailed data tables with numbers and dates\n→ Document all funding sources and amounts\n→ Provide complete evidence for each criterion\n→ Include supporting documents and reports\n→ Ensure all dimensions are covered\n\nNote: I'm currently offline, but these tips should help!";
      } else if (lowerMessage.includes('result') || lowerMessage.includes('mean')) {
        return "Results explained:\n→ Confidence Score (0-100%): How well your evidence matches requirements\n→ Grade (A+ to D): Overall quality rating\n→ Coverage: Percentage of required dimensions found\n→ Recommendations: Specific suggestions to improve\n\nNote: I'm currently offline, but this should clarify the results!";
      } else {
        return "I'm currently offline (API server may not be running). However, you can:\n\n→ Explore the Dashboard to upload and audit documents\n→ Check the History page for past audits\n→ View Metrics for performance analytics\n→ Visit Top Universities to learn from the best\n\nTo reconnect me, ensure the API server is running on port 8000.";
      }
    }
  };

  const handleSend = async () => {
    if (!inputText.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: messages.length + 1,
      text: inputText,
      sender: 'user',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setInputText('');

    // Show typing indicator
    const typingMessage: Message = {
      id: messages.length + 2,
      text: '...',
      sender: 'bot',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, typingMessage]);

    // Get bot response
    const botResponseText = await getBotResponse(inputText);
    
    // Replace typing indicator with actual response
    setMessages(prev => {
      const filtered = prev.filter(m => m.text !== '...');
      return [...filtered, {
        id: prev.length + 1,
        text: botResponseText,
        sender: 'bot',
        timestamp: new Date()
      }];
    });
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const quickQuestions = [
    "How do I get started?",
    "How to upload documents?",
    "How to improve my score?",
    "What do the results mean?"
  ];

  return (
    <>
      {/* Chat Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 w-16 h-16 bg-gradient-to-br from-cyan-500 to-purple-600 rounded-full shadow-2xl flex items-center justify-center hover:scale-110 transition-transform z-50 animate-pulse"
        >
          <MessageCircle size={28} className="text-white" />
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 w-96 h-[600px] glass-card border border-border/50 rounded-2xl shadow-2xl flex flex-col z-50 animate-in slide-in-from-bottom-4">
          {/* Header */}
          <div className="p-4 border-b border-border/50 flex items-center justify-between bg-gradient-to-r from-cyan-500/10 to-purple-500/10">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-400 to-purple-600 flex items-center justify-center">
                <Sparkles size={20} className="text-white" />
              </div>
              <div>
                <h3 className="font-bold text-foreground">Omni Assistant</h3>
                <p className="text-xs text-muted-foreground">Always here to help</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="w-8 h-8 rounded-lg hover:bg-slate-700/50 flex items-center justify-center transition"
            >
              <X size={20} className="text-muted-foreground" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                    message.sender === 'user'
                      ? 'bg-gradient-to-r from-cyan-500 to-purple-600 text-white'
                      : 'bg-slate-800/50 text-foreground border border-border/50'
                  }`}
                >
                  <p className="text-sm whitespace-pre-line">{message.text}</p>
                  <p className={`text-xs mt-1 ${message.sender === 'user' ? 'text-white/70' : 'text-muted-foreground'}`}>
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Questions */}
          {messages.length <= 2 && (
            <div className="px-4 pb-2">
              <p className="text-xs text-muted-foreground mb-2">Quick questions:</p>
              <div className="flex flex-wrap gap-2">
                {quickQuestions.map((question, index) => (
                  <button
                    key={index}
                    onClick={() => {
                      setInputText(question);
                      setTimeout(() => handleSend(), 100);
                    }}
                    className="text-xs px-3 py-1.5 bg-cyan-500/10 text-cyan-400 rounded-full hover:bg-cyan-500/20 transition"
                  >
                    {question}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Input */}
          <div className="p-4 border-t border-border/50">
            <div className="flex gap-2">
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me anything..."
                className="flex-1 px-4 py-2 bg-slate-900/50 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 text-sm"
              />
              <button
                onClick={handleSend}
                disabled={!inputText.trim()}
                className="w-10 h-10 bg-gradient-to-r from-cyan-500 to-purple-600 rounded-lg flex items-center justify-center hover:from-cyan-600 hover:to-purple-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Send size={18} className="text-white" />
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
