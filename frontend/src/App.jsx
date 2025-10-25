import React, { useState, useRef, useEffect } from 'react';
import { Send, Scale, FileText, AlertCircle, Download } from 'lucide-react';

export default function LegalAssistantChat() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm your B.C. Employment Rights Assistant. I'm here to help you understand your workplace rights under British Columbia law. I'll ask you some questions about your situation to provide accurate guidance. What brings you here today?",
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState(null);
  const [showReport, setShowReport] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Configure your backend URL here
  const API_BASE_URL = 'http://127.0.0.1:8000';

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const sendMessageToBackend = async (message) => {
    console.log('anijaks')
    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message })
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      return data.reply;
    } catch (err) {
      console.error('Error calling backend:', err);
      throw err;
    }
  };

  const handleSend = async () => {
    if (inputValue.trim() === '') return;
  
    const newMessage = {
      id: messages.length + 1,
      text: inputValue,
      sender: 'user',
      timestamp: new Date()
    };
  
    setMessages([...messages, newMessage]);
    const userInput = inputValue;
    setInputValue('');
    
    // Show typing indicator
    setIsTyping(true);
    
    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userInput })
      });
      
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      
      const data = await response.json();
      
      const botResponse = {
        id: messages.length + 2,
        text: data.reply,
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botResponse]);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage = {
        id: messages.length + 2,
        text: "I'm sorry, I'm having trouble connecting. Please try again later.",
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  const handleDownloadReport = () => {
    // Collect all messages for the report
    const conversationText = messages
      .map(msg => `[${msg.sender === 'user' ? 'YOU' : 'ASSISTANT'}] ${msg.text}`)
      .join('\n\n');
    
    const reportContent = `B.C. WORKERS RIGHTS ASSISTANT - SITUATION REPORT
Generated: ${new Date().toLocaleString()}

===============================================
CONVERSATION SUMMARY
===============================================

${conversationText}

===============================================
NEXT STEPS
===============================================

This report summarizes your conversation with the B.C. Workers Rights Assistant. 
Please share this with a legal clinic or employment advocate for further assistance.

DISCLAIMER: This is general information only and not legal advice. 
For specific legal advice, please consult with a qualified legal professional.
`;

    const blob = new Blob([reportContent], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `BC-Workers-Rights-Report-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
      {/* Header */}
      <div className="bg-white shadow-md border-b border-slate-200">
        <div className="max-w-5xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-br from-blue-600 to-blue-700 p-2.5 rounded-xl shadow-lg">
                <Scale className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-800">B.C. Workers Rights Assistant</h1>
                <p className="text-sm text-slate-500">Powered by Employment Standards Act</p>
              </div>
            </div>
            {showReport && (
              <button
                onClick={handleDownloadReport}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-br from-green-600 to-green-700 text-white rounded-lg hover:shadow-lg transition-all duration-200 hover:scale-105"
              >
                <Download className="w-4 h-4" />
                <span className="text-sm font-medium">Download Report</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Disclaimer Banner */}
      <div className="bg-amber-50 border-b border-amber-200">
        <div className="max-w-5xl mx-auto px-6 py-3">
          <div className="flex items-start gap-2 text-sm">
            <AlertCircle className="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" />
            <p className="text-amber-800">
              <strong>Privacy Notice:</strong> This is general information only and not legal advice. 
              Your conversation is confidential and not stored permanently.
            </p>
          </div>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="bg-red-50 border-b border-red-200">
          <div className="max-w-5xl mx-auto px-6 py-3">
            <div className="flex items-start gap-2 text-sm">
              <AlertCircle className="w-4 h-4 text-red-600 mt-0.5 flex-shrink-0" />
              <p className="text-red-800">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-5xl mx-auto px-6 py-6">
          <div className="space-y-6">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}
              >
                <div
                  className={`max-w-2xl ${
                    message.sender === 'user'
                      ? 'bg-gradient-to-br from-blue-600 to-blue-700 text-white shadow-lg'
                      : message.isError
                      ? 'bg-red-50 text-red-800 shadow-md border border-red-200'
                      : message.isReport
                      ? 'bg-gradient-to-br from-green-50 to-emerald-50 text-slate-800 shadow-md border-2 border-green-300'
                      : 'bg-white text-slate-800 shadow-md border border-slate-200'
                  } rounded-2xl px-5 py-3.5`}
                >
                  {message.sender === 'bot' && (
                    <div className={`flex items-center gap-2 mb-2 pb-2 border-b ${
                      message.isReport ? 'border-green-200' : 'border-slate-100'
                    }`}>
                      <FileText className={`w-4 h-4 ${message.isReport ? 'text-green-600' : 'text-blue-600'}`} />
                      <span className={`text-xs font-semibold ${
                        message.isReport ? 'text-green-600' : 'text-blue-600'
                      }`}>
                        {message.isReport ? 'Report Generated' : 'Legal Assistant'}
                      </span>
                    </div>
                  )}
                  <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.text}</p>
                  <div className={`text-xs mt-2 ${
                    message.sender === 'user' ? 'text-blue-100' : 'text-slate-400'
                  }`}>
                    {formatTime(message.timestamp)}
                  </div>
                </div>
              </div>
            ))}

            {isTyping && (
              <div className="flex justify-start animate-fade-in">
                <div className="bg-white text-slate-800 rounded-2xl px-5 py-4 shadow-md border border-slate-200">
                  <div className="flex items-center gap-2 mb-2 pb-2 border-b border-slate-100">
                    <FileText className="w-4 h-4 text-blue-600" />
                    <span className="text-xs font-semibold text-blue-600">Legal Assistant</span>
                  </div>
                  <div className="flex gap-1.5">
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>
      </div>

      {/* Input Area */}
      <div className="bg-white border-t border-slate-200 shadow-lg">
        <div className="max-w-5xl mx-auto px-6 py-4">
          <div className="flex gap-3 items-end">
            <div className="flex-1 relative">
              <textarea
                ref={inputRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Describe your workplace situation..."
                disabled={isTyping}
                className="w-full px-4 py-3 pr-12 border-2 border-slate-200 rounded-xl focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all resize-none text-slate-800 placeholder-slate-400 disabled:bg-slate-50 disabled:cursor-not-allowed"
                rows="1"
                style={{ minHeight: '48px', maxHeight: '120px' }}
                onInput={(e) => {
                  e.target.style.height = 'auto';
                  e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
                }}
              />
            </div>
            <button
              onClick={handleSend}
              disabled={inputValue.trim() === '' || isTyping}
              className={`p-3.5 rounded-xl transition-all duration-200 flex-shrink-0 ${
                inputValue.trim() === '' || isTyping
                  ? 'bg-slate-200 text-slate-400 cursor-not-allowed'
                  : 'bg-gradient-to-br from-blue-600 to-blue-700 text-white shadow-lg hover:shadow-xl hover:scale-105 active:scale-95'
              }`}
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
          <p className="text-xs text-slate-500 mt-3 text-center">
            Press Enter to send • Shift + Enter for new line
          </p>
        </div>
      </div>

      <style>{`
        @keyframes fade-in {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        .animate-fade-in {
          animation: fade-in 0.3s ease-out;
        }

        @keyframes bounce {
          0%, 100% {
            transform: translateY(0);
          }
          50% {
            transform: translateY(-5px);
          }
        }

        .animate-bounce {
          animation: bounce 0.6s ease-in-out infinite;
        }

        /* Custom scrollbar */
        .overflow-y-auto::-webkit-scrollbar {
          width: 8px;
        }

        .overflow-y-auto::-webkit-scrollbar-track {
          background: #f1f5f9;
        }

        .overflow-y-auto::-webkit-scrollbar-thumb {
          background: #cbd5e1;
          border-radius: 4px;
        }

        .overflow-y-auto::-webkit-scrollbar-thumb:hover {
          background: #94a3b8;
        }
      `}</style>
    </div>
  );
}