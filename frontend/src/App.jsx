import React, { useState, useRef, useEffect } from 'react';
import { Send, Scale, FileText, AlertCircle, Paperclip, X } from 'lucide-react';

export default function App() {
  const messageIdRef = useRef(1);
  const [messages, setMessages] = useState([
    {
      id: messageIdRef.current++,
      text: "Hello! I'm Fiona the Form Filler. I'm here to help you understand your workplace rights under British Columbia law. I'll ask you some questions about your situation to provide accurate guidance. What brings you here today?",
      sender: 'bot',
      timestamp: new Date(),
      isReport: false,
      confirmed: false
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [latestMessage, setLatestMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [attachedFiles, setAttachedFiles] = useState([]);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const fileInputRef = useRef(null);
  

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    setAttachedFiles(prev => [...prev, ...files]);
  };

  const removeFile = (indexToRemove) => {
    setAttachedFiles(prev => prev.filter((_, index) => index !== indexToRemove));
  };

  const handleSend = async () => {
    if (inputValue.trim() === '' && attachedFiles.length === 0) return;

    // Upload files if any are attached
    if (attachedFiles.length > 0) {
      try {
        const formData = new FormData();
        attachedFiles.forEach(file => {
          formData.append('file', file);
        });

        const uploadResponse = await fetch('http://localhost:8000/upload', {
          method: 'POST',
          body: formData
        });

        if (!uploadResponse.ok) throw new Error('File upload failed');
      } catch (error) {
        console.error('Error uploading files:', error);
        const errorMessage = {
          id: messageIdRef.current++,
          text: "I'm sorry, I couldn't upload your files. Please try again.",
          sender: 'bot',
          timestamp: new Date(),
          isReport: false,
          confirmed: false
        };
        setMessages(prev => [...prev, errorMessage]);
        return;
      }
    }

    // Create message text with file information
    let messageText = inputValue;
    if (attachedFiles.length > 0) {
      const fileList = attachedFiles.map(f => f.name).join(', ');
      messageText = messageText ? `${messageText}\n\nUser added ${fileList}` : `User added ${fileList}`;
    }

    const newMessage = {
      id: messageIdRef.current++,
      text: messageText,
      sender: 'user',
      timestamp: new Date(),
      files: attachedFiles.length > 0 ? attachedFiles.map(f => f.name) : null
    };

    setMessages(prev => [...prev, newMessage]);
    const userInput = messageText;
    setInputValue('');
    setAttachedFiles([]);

    setIsTyping(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userInput })
      });

      if (!response.ok) throw new Error('Network response was not ok');

      const data = await response.json();
      console.log(data)
      let pdfUrls
      if (data.pdfs) {
        pdfUrls = data.pdfs.map(pdf => {
            const blob = new Blob(
            [Uint8Array.from(atob(pdf.pdf_base64), c => c.charCodeAt(0))],
            { type: "application/pdf" }
            );
            return { url: URL.createObjectURL(blob), filename: pdf.filename };
        });
      }

      const botResponse = {
        id: messageIdRef.current++,
        text: data.reply,
        sender: 'bot',
        timestamp: new Date(),
        isReport: data.is_report || false,
        confirmed: false,
        pdfUrls,
      };
      setLatestMessage(data.reply);
      console.log(latestMessage)

      setMessages(prev => [...prev, botResponse]);

    } catch (error) {
      console.error('Error:', error);
      const errorMessage = {
        id: messageIdRef.current++,
        text: "I'm sorry, I'm having trouble connecting. Please try again later.",
        sender: 'bot',
        timestamp: new Date(),
        isReport: false,
        confirmed: false
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleConfirmReport = async (messageId, confirmed) => {
    try {
      // Mark the original message as confirmed
      setMessages(prev => prev.map(msg => 
        msg.id === messageId ? { ...msg, confirmed: true } : msg
      ));

      const response = await fetch('http://localhost:8000/confirm-report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ confirmed: confirmed })
      });

      const data = await response.json();

      const botResponse = {
        id: messageIdRef.current++,
        text: data.reply,
        sender: 'bot',
        timestamp: new Date(),
        isReport: false,
        confirmed: false
      };

      setMessages(prev => [...prev, botResponse]);

      if (confirmed) {
        try {
            setLoading(true)
            const response = await fetch('http://localhost:8000/after-report', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ message: latestMessage })
            });
      
            if (!response.ok) throw new Error('Network response was not ok');
      
            const data = await response.json();
            console.log(data)
      
            const botResponse = {
              id: messageIdRef.current++,
              text: data.reply,
              sender: 'bot',
              timestamp: new Date(),
              isReport: false,
              confirmed: false
            };
      
            setMessages(prev => [...prev, botResponse]);
      
          } catch (error) {
            console.error('Error:', error);
            const errorMessage = {
              id: messageIdRef.current++,
              text: "I'm sorry, I'm having trouble connecting. Please try again later.",
              sender: 'bot',
              timestamp: new Date(),
              isReport: false,
              confirmed: false
            };
            setMessages(prev => [...prev, errorMessage]);
          } finally {
            setIsTyping(false);
            setLoading(false);
          }
      }

    } catch (err) {
      console.error('Error confirming report:', err);
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

  return (
    <div className="relative flex flex-col h-screen bg-white overflow-hidden">
      {/* Background gradients */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-gradient-to-br from-purple-200/30 via-blue-200/30 to-transparent rounded-full blur-3xl animate-float"></div>
        <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-gradient-to-tl from-blue-300/30 via-purple-200/30 to-transparent rounded-full blur-3xl animate-float-delayed"></div>
        <div className="absolute top-1/4 left-1/3 w-96 h-96 bg-gradient-to-br from-indigo-200/20 to-transparent rounded-full blur-3xl animate-pulse-slow"></div>
      </div>

      <div className="relative z-10 flex flex-col h-full">
        {/* Header */}
        <div className="backdrop-blur-xl bg-white/80 shadow-sm border-b border-purple-100/50">
          <div className="max-w-4xl mx-auto px-6 py-5 flex items-center gap-3">
            <div className="bg-gradient-to-br from-purple-500 via-purple-600 to-blue-600 p-2.5 rounded-2xl shadow-lg shadow-purple-500/30">
              <Scale className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-purple-700 to-blue-700 bg-clip-text text-transparent">
                Fiona the Form Filler
              </h1>
              <p className="text-sm text-slate-500">Powered by Employment Standards Act</p>
            </div>
          </div>
        </div>

        {/* Privacy notice */}
        <div className="backdrop-blur-xl bg-amber-50/80 border-b border-amber-200/50">
          <div className="max-w-4xl mx-auto px-6 py-3 flex items-start gap-2 text-sm">
            <AlertCircle className="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" />
            <p className="text-amber-800">
              <strong>Privacy Notice:</strong> This is general information only and not legal advice. 
              Your conversation is confidential and not stored permanently.
            </p>
          </div>
        </div>

        {/* Chat messages */}
        <div className="flex-1 overflow-y-auto">
          <div className="max-w-4xl mx-auto px-6 py-8">
            <div className="space-y-6">
              {messages.map((message) => (
                <div key={message.id} className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}>
                  <div className={`max-w-2xl ${message.sender === 'user'
                    ? 'bg-gradient-to-br from-purple-500 via-purple-600 to-blue-600 text-white shadow-xl shadow-purple-500/30'
                    : 'backdrop-blur-xl bg-white/90 text-slate-800 shadow-lg border border-purple-100/50'
                  } rounded-3xl px-6 py-4`}>

                    {message.sender === 'bot' && (
                      <div className="flex items-center gap-2 mb-2 pb-2 border-b border-purple-100">
                        <FileText className="w-4 h-4 text-purple-600" />
                        <span className="text-xs font-semibold text-purple-600">Legal Assistant</span>
                      </div>
                    )}

                    <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.text}</p>
                    {message.pdfUrls?.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-4">
                        {message.pdfUrls.map((pdf, i) => (
                        <div
                            key={i}
                            className="w-72 flex flex-col items-center bg-white/20 rounded-xl p-3 border border-gray-200 shadow-sm"
                        >
                            <iframe
                            src={pdf.url}
                            width="100%"
                            height="300px"
                            title={`PDF-${i}`}
                            className="rounded-lg border border-gray-300"
                            ></iframe>
                            <a
                            href={pdf.url}
                            download={pdf.filename}
                            className="text-purple-600 text-sm underline mt-2"
                            >
                            Download {pdf.filename}
                            </a>
                        </div>
                        ))}
                    </div>
                    )}



                    {message.files && message.files.length > 0 && (
                      <div className="mt-3 space-y-1">
                        {message.files.map((fileName, idx) => (
                          <div key={idx} className="flex items-center gap-2 text-xs bg-white/20 rounded-lg px-2 py-1">
                            <Paperclip className="w-3 h-3" />
                            <span>{fileName}</span>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Report confirmation buttons */}
                    {message.isReport && !message.confirmed && (
                      <div className="mt-3 flex gap-2">
                        <button
                          onClick={() => handleConfirmReport(message.id, true)}
                          className="px-4 py-2 bg-green-500 text-white rounded-xl hover:bg-green-600 transition"
                        >
                          Confirm
                        </button>
                        <button
                          onClick={() => handleConfirmReport(message.id, false)}
                          className="px-4 py-2 bg-red-500 text-white rounded-xl hover:bg-red-600 transition"
                        >
                          Request Revision
                        </button>
                      </div>
                    )}

                    <div className={`text-xs mt-2 ${message.sender === 'user' ? 'text-purple-100' : 'text-slate-400'}`}>
                      {formatTime(message.timestamp)}
                    </div>
                  </div>
                </div>
              ))}

              {isTyping && (
                <div className="flex justify-start animate-fade-in">
                  <div className="backdrop-blur-xl bg-white/90 rounded-3xl px-6 py-4 shadow-lg border border-purple-100/50">
                    <div className="flex items-center gap-2 mb-2 pb-2 border-b border-purple-100">
                      <FileText className="w-4 h-4 text-purple-600" />
                      <span className="text-xs font-semibold text-purple-600">Legal Assistant</span>
                    </div>
                    <div className="flex gap-1.5">
                      <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                      <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                      <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          </div>
        </div>

        {/* Input section */}
        <div className="backdrop-blur-xl bg-white/80 border-t border-purple-100/50 shadow-xl">
          <div className="max-w-4xl mx-auto px-6 py-5">
            {attachedFiles.length > 0 && (
              <div className="mb-3 flex flex-wrap gap-2">
                {attachedFiles.map((file, index) => (
                  <div key={index} className="flex items-center gap-2 bg-gradient-to-br from-purple-50 to-blue-50 border border-purple-200 rounded-xl px-3 py-2 text-sm">
                    <Paperclip className="w-4 h-4 text-purple-600" />
                    <span className="text-slate-700 max-w-xs truncate">{file.name}</span>
                    <button onClick={() => removeFile(index)} className="ml-1 text-slate-400 hover:text-slate-600 transition-colors">
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}

            <div className="flex gap-3 items-end">
              <input ref={fileInputRef} type="file" multiple onChange={handleFileSelect} className="hidden" accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png" />
              <button onClick={() => fileInputRef.current && fileInputRef.current.click()} className="p-3.5 rounded-2xl backdrop-blur-xl bg-gradient-to-br from-purple-50 to-blue-50 border border-purple-200 text-purple-600 hover:from-purple-100 hover:to-blue-100 transition-all duration-200 flex-shrink-0 shadow-sm hover:shadow-md" title="Attach files">
                <Paperclip className="w-5 h-5" />
              </button>

              <div className="flex-1 relative">
                <textarea
                  ref={inputRef}
                  value={inputValue}
                  onKeyPress={handleKeyPress}
                  onChange={(e) => setInputValue(e.target.value)}
                  autoCapitalize='sentences'
                  placeholder="Describe your workplace situation..."
                  className="w-full px-5 py-3.5 backdrop-blur-xl bg-white/70 border-2 border-purple-200 rounded-2xl focus:outline-none focus:border-purple-400 focus:bg-white/90 transition-all resize-none text-slate-800 placeholder-slate-400 shadow-sm"
                  rows="1"
                  style={{ minHeight: '52px', maxHeight: '120px' }}
                  onInput={(e) => {
                    e.target.style.height = 'auto';
                    e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
                  }}
                />
              </div>

              <button
                onClick={handleSend}
                disabled={inputValue.trim() === '' && attachedFiles.length === 0}
                className={`p-3.5 rounded-2xl transition-all duration-200 flex-shrink-0 ${
                  inputValue.trim() === '' && attachedFiles.length === 0
                    ? 'bg-slate-200 text-slate-400 cursor-not-allowed'
                    : 'bg-gradient-to-br from-purple-500 via-purple-600 to-blue-600 text-white shadow-lg shadow-purple-500/30 hover:shadow-xl hover:shadow-purple-500/40 hover:scale-105 active:scale-95'
                }`}
              >
                <Send className="w-5 h-5" />
              </button>
            </div>

            <p className="text-xs text-slate-500 mt-3 text-center">
              Press Enter to send • Shift + Enter for new line • Attach documents for context
            </p>
          </div>
        </div>
      </div>

      {/* Styles (animations, scrollbar) */}
      <style>{`
        @keyframes fade-in { from {opacity:0;transform:translateY(10px);} to {opacity:1;transform:translateY(0);} }
        .animate-fade-in { animation: fade-in 0.3s ease-out; }

        @keyframes bounce { 0%,100%{transform:translateY(0);} 50%{transform:translateY(-5px);} }
        .animate-bounce { animation: bounce 0.6s ease-in-out infinite; }

        @keyframes float {0%,100%{transform:translate(0,0) rotate(0deg);}33%{transform:translate(30px,-30px) rotate(120deg);}66%{transform:translate(-20px,20px) rotate(240deg);} }
        .animate-float { animation: float 20s ease-in-out infinite; }
        .animate-float-delayed { animation: float 25s ease-in-out infinite; animation-delay: -5s; }

        @keyframes pulse-slow {0%,100%{opacity:0.3;transform:scale(1);}50%{opacity:0.5;transform:scale(1.05);} }
        .animate-pulse-slow { animation: pulse-slow 8s ease-in-out infinite; }

        .overflow-y-auto::-webkit-scrollbar { width: 8px; }
        .overflow-y-auto::-webkit-scrollbar-track { background: rgba(243,244,246,0.5); }
        .overflow-y-auto::-webkit-scrollbar-thumb { background: rgba(168,85,247,0.3); border-radius:4px; }
        .overflow-y-auto::-webkit-scrollbar-thumb:hover { background: rgba(168,85,247,0.5); }
      `}</style>
    </div>
  );
}