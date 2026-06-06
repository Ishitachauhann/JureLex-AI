// App.jsx
import React, { useState, useRef, useEffect } from 'react';
import { 
  Scale, FileText, Search, MessageCircle, Send, Bot, User, Home, 
  ChevronRight, Loader2, Copy, Check, BookOpen, Gavel, Users, 
  Award, TrendingUp, Mic, MicOff, Volume2, VolumeX, UploadCloud, 
  Globe, Languages, FileCheck, HelpCircle, ArrowRightLeft, Sparkles
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';

// Main App Component
const App = () => {
  const [currentView, setCurrentView] = useState('home');
  const [chatHistory, setChatHistory] = useState([]);
  const [activeModel, setActiveModel] = useState('Llama');
  const [activeLanguage, setActiveLanguage] = useState('English');

  const addMessageToHistory = (message, response, type) => {
    setChatHistory(prev => [...prev, { message, response, type, timestamp: new Date() }]);
  };

  const clearHistory = () => {
    setChatHistory([]);
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case 'ipc':
        return (
          <IPCFinder 
            onAddMessage={addMessageToHistory} 
            activeModel={activeModel} 
            activeLanguage={activeLanguage} 
          />
        );
      case 'precedence':
        return (
          <PrecedenceFinder 
            onAddMessage={addMessageToHistory} 
            activeModel={activeModel} 
            activeLanguage={activeLanguage} 
          />
        );
      case 'document':
        return (
          <DocumentCreator 
            onAddMessage={addMessageToHistory} 
            activeModel={activeModel} 
            activeLanguage={activeLanguage} 
          />
        );
      case 'upload':
        return <KnowledgeBaseUploader />;
      case 'history':
        return <ChatHistory history={chatHistory} onClear={clearHistory} />;
      default:
        return <HomePage onNavigate={setCurrentView} />;
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Header 
        currentView={currentView} 
        onNavigate={setCurrentView} 
        activeModel={activeModel}
        setActiveModel={setActiveModel}
        activeLanguage={activeLanguage}
        setActiveLanguage={setActiveLanguage}
      />
      <main className="flex-1 container mx-auto px-4 py-8 max-w-6xl">
        {renderCurrentView()}
      </main>
      <footer className="py-6 border-t border-slate-800 text-center text-xs text-slate-500 bg-slate-950">
        &copy; {new Date().getFullYear()} JureLex AI - Legal Intelligence Suite. All rights reserved.
      </footer>
    </div>
  );
};

// Header Component
const Header = ({ currentView, onNavigate, activeModel, setActiveModel, activeLanguage, setActiveLanguage }) => {
  const navItems = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'ipc', label: 'IPC / BNS', icon: Scale },
    { id: 'precedence', label: 'Precedence', icon: Search },
    { id: 'document', label: 'Drafting', icon: FileText },
    { id: 'upload', label: 'Ingest', icon: UploadCloud },
    { id: 'history', label: 'History', icon: MessageCircle },
  ];

  return (
    <header className="bg-slate-900/95 backdrop-blur-md sticky top-0 z-50 border-b border-slate-850 shadow-lg px-4">
      <div className="container mx-auto max-w-6xl flex flex-col md:flex-row items-center justify-between py-3 md:h-20 gap-4">
        
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => onNavigate('home')}>
          <div className="bg-gradient-to-tr from-blue-600 to-indigo-500 p-2 rounded-xl shadow-md shadow-blue-500/20">
            <Scale className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-extrabold bg-gradient-to-r from-blue-400 to-indigo-300 bg-clip-text text-transparent leading-none">JureLex AI</h1>
            <span className="text-[10px] text-slate-400 tracking-wider uppercase">Legal Assistant</span>
          </div>
        </div>

        {/* Navigation buttons */}
        <nav className="flex flex-wrap justify-center gap-1">
          {navItems.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => onNavigate(id)}
              className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-xs font-semibold tracking-wide transition-all ${currentView === id
                  ? 'bg-blue-600/90 text-white shadow-md shadow-blue-600/10'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{label}</span>
            </button>
          ))}
        </nav>

        {/* Global LLM and Language Settings Panel */}
        <div className="flex items-center space-x-3 bg-slate-950/50 p-1.5 rounded-xl border border-slate-800/80">
          {/* Model selection */}
          <div className="flex items-center space-x-1 bg-slate-900 p-1 rounded-lg">
            <Sparkles className="w-3.5 h-3.5 text-indigo-400 ml-1" />
            <select
              value={activeModel}
              onChange={(e) => setActiveModel(e.target.value)}
              className="bg-transparent text-slate-200 text-xs font-medium focus:outline-none cursor-pointer pr-1"
            >
              <option value="Llama">Llama 3.2</option>
              <option value="Phi">Phi 2.7B</option>
              <option value="Mistral">Mistral 7B</option>
              <option value="Gemini">Gemini 1.5</option>
              <option value="All Models">All Models</option>
            </select>
          </div>

          {/* Language Selection */}
          <div className="flex items-center space-x-1 bg-slate-900 p-1 rounded-lg">
            <Globe className="w-3.5 h-3.5 text-blue-400 ml-1" />
            <select
              value={activeLanguage}
              onChange={(e) => setActiveLanguage(e.target.value)}
              className="bg-transparent text-slate-200 text-xs font-medium focus:outline-none cursor-pointer pr-1"
            >
              <option value="English">English</option>
              <option value="Hindi">हिंदी (Hindi)</option>
              <option value="Tamil">தமிழ் (Tamil)</option>
              <option value="Telugu">తెలుగు (Telugu)</option>
              <option value="Bengali">বাংলা (Bengali)</option>
              <option value="Marathi">मराठी (Marathi)</option>
            </select>
          </div>
        </div>

      </div>
    </header>
  );
};

// Home Component
const HomePage = ({ onNavigate }) => {
  const features = [
    {
      id: 'ipc',
      title: 'IPC / BNS Legal Bridge',
      description: 'Scan penal sections instantly and translate between the legacy IPC provisions and the new Bharatiya Nyaya Sanhita (BNS).',
      icon: Scale,
      color: 'from-blue-600 to-cyan-500',
      stats: 'Full Statutory Mapping'
    },
    {
      id: 'precedence',
      title: 'Precedent Discovery',
      description: 'Locate judicial precedents, court summaries, and citations using semantic search over court records.',
      icon: Search,
      color: 'from-emerald-600 to-teal-500',
      stats: 'Vector Context Search'
    },
    {
      id: 'document',
      title: 'Automated Drafting',
      description: 'Generate contracts, agreements, and notices guided by templates with structured prompt guidance.',
      icon: FileText,
      color: 'from-purple-600 to-pink-500',
      stats: 'Interactive Templates'
    },
  ];

  const stats = [
    { icon: BookOpen, label: 'Statutes & Codes', value: 'IPC & BNS' },
    { icon: Gavel, label: 'Indian Precedents', value: 'Supreme/High Courts' },
    { icon: Users, label: 'Legal Professionals', value: '1,500+' },
    { icon: Sparkles, label: 'LLMs supported', value: '4 Engines' },
  ];

  return (
    <div className="space-y-12">
      
      {/* Hero Section */}
      <div className="text-center py-8 max-w-4xl mx-auto space-y-6">
        <div className="inline-flex items-center space-x-2 bg-blue-500/10 border border-blue-500/20 px-3 py-1 rounded-full text-blue-400 text-xs font-semibold uppercase tracking-wider animate-pulse">
          <Sparkles className="w-3.5 h-3.5" />
          <span>V2.0 Indian Legal Assistant</span>
        </div>
        <h1 className="text-4xl md:text-6xl font-black tracking-tight text-white leading-tight">
          Next-Generation <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-300 to-emerald-400">Legal Intelligence</span>
        </h1>
        <p className="text-lg md:text-xl text-slate-400 leading-relaxed font-light">
          Your smart companion for decoding law, mapping penal sections, searching case precedence, and generating formal agreements instantly.
        </p>
        <div className="flex justify-center gap-4 pt-4">
          <button
            onClick={() => onNavigate('ipc')}
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-8 py-3.5 rounded-xl transition-all shadow-lg shadow-blue-600/15 transform hover:-translate-y-0.5"
          >
            Start Legal Research
          </button>
          <button 
            onClick={() => onNavigate('upload')}
            className="border border-slate-700 hover:border-slate-600 text-slate-300 font-semibold px-8 py-3.5 rounded-xl transition-all hover:bg-slate-900"
          >
            Upload Documents
          </button>
        </div>
      </div>

      {/* Stats Section */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map(({ icon: Icon, label, value }, index) => (
          <div key={index} className="bg-slate-900/50 backdrop-blur-sm border border-slate-850 rounded-2xl p-6 text-center shadow-md">
            <div className="bg-slate-800/80 w-10 h-10 rounded-xl flex items-center justify-center mx-auto mb-4 border border-slate-750">
              <Icon className="w-5 h-5 text-blue-400" />
            </div>
            <div className="text-xl font-bold text-white mb-1">{value}</div>
            <div className="text-slate-400 text-xs font-medium uppercase tracking-wide">{label}</div>
          </div>
        ))}
      </div>

      {/* Features Grid */}
      <div className="grid md:grid-cols-3 gap-6">
        {features.map(({ id, title, description, icon: Icon, color, stats }) => (
          <div
            key={id}
            onClick={() => onNavigate(id)}
            className="group relative bg-slate-900/60 hover:bg-slate-900 border border-slate-850 hover:border-slate-700 rounded-2xl p-6 transition-all duration-300 cursor-pointer shadow-lg hover:shadow-2xl flex flex-col justify-between"
          >
            <div>
              <div className={`w-12 h-12 bg-gradient-to-br ${color} rounded-xl flex items-center justify-center mb-5 shadow-lg shadow-blue-500/5 group-hover:scale-105 transition-transform`}>
                <Icon className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-lg font-bold text-white mb-2 tracking-wide group-hover:text-blue-400 transition-colors">{title}</h3>
              <p className="text-slate-400 text-sm leading-relaxed mb-6 font-light">{description}</p>
            </div>
            <div className="border-t border-slate-850 pt-4 flex items-center justify-between text-xs font-semibold">
              <span className="text-indigo-400 uppercase tracking-wide">{stats}</span>
              <div className="flex items-center text-blue-400 group-hover:translate-x-1 transition-transform">
                <span>Access</span>
                <ChevronRight className="w-3.5 h-3.5 ml-1" />
              </div>
            </div>
          </div>
        ))}
      </div>

    </div>
  );
};

// Enhanced Chat Interface Component
const ChatInterface = ({ title, onSubmit, loading, activeLanguage, children }) => {
  const [input, setInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [children]);

  const handleSubmit = () => {
    if (input.trim() && !loading) {
      onSubmit(input.trim());
      setInput('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  // Browser speech transcription
  const toggleSpeechRecognition = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Speech recognition is not supported in this browser. Please use Chrome or Safari.");
      return;
    }

    if (isListening) {
      window.speechRecognitionInstance?.stop();
      setIsListening(false);
      return;
    }

    const recognition = new SpeechRecognition();
    // Match recognition language code
    let langCode = 'en-IN';
    if (activeLanguage === 'Hindi') langCode = 'hi-IN';
    else if (activeLanguage === 'Tamil') langCode = 'ta-IN';
    else if (activeLanguage === 'Telugu') langCode = 'te-IN';
    else if (activeLanguage === 'Bengali') langCode = 'bn-IN';
    else if (activeLanguage === 'Marathi') langCode = 'mr-IN';

    recognition.lang = langCode;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onerror = (e) => {
      console.error("Speech Recognition Error:", e.error);
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInput(prev => (prev ? prev + ' ' : '') + transcript);
    };

    window.speechRecognitionInstance = recognition;
    recognition.start();
  };

  return (
    <div className="bg-slate-900 border border-slate-850 rounded-2xl h-[700px] flex flex-col overflow-hidden shadow-2xl">
      
      {/* Header bar */}
      <div className="border-b border-slate-800 bg-slate-900/60 p-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="bg-blue-600/10 p-2 rounded-lg border border-blue-500/10">
            <Bot className="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white tracking-wide">{title}</h2>
            <span className="text-[10px] text-emerald-400 font-medium flex items-center">
              <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full inline-block mr-1.5 animate-pulse"></span>
              Secure Sandbox Environment
            </span>
          </div>
        </div>
      </div>

      {/* Conversation Thread */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-950/20">
        {children}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Console */}
      <div className="border-t border-slate-800 p-4 bg-slate-900/80 backdrop-blur-sm">
        <div className="flex items-center space-x-2 bg-slate-950 border border-slate-850 rounded-xl px-4 py-2 focus-within:ring-2 focus-within:ring-blue-600 focus-within:border-transparent transition-all">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder={`Ask in ${activeLanguage}...`}
            className="flex-1 bg-transparent text-slate-100 placeholder-slate-500 text-sm focus:outline-none resize-none h-8 max-h-24 leading-relaxed scrollbar-thin"
            disabled={loading}
            rows={1}
          />

          <div className="flex items-center space-x-1">
            {/* Dictate Microphone */}
            <button
              onClick={toggleSpeechRecognition}
              disabled={loading}
              className={`p-2 rounded-lg transition-all ${
                isListening 
                  ? 'bg-red-600 text-white animate-bounce' 
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
              }`}
              title="Dictate Query"
            >
              {isListening ? (
                <MicOff className="w-4 h-4" />
              ) : (
                <Mic className="w-4 h-4" />
              )}
            </button>

            {/* Send */}
            <button
              onClick={handleSubmit}
              disabled={loading || !input.trim()}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-850 text-white rounded-lg p-2 flex items-center justify-center transition-all disabled:text-slate-600"
            >
              {loading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Message components - User on right
const UserMessage = ({ message }) => (
  <div className="flex items-start space-x-3 justify-end">
    <div className="bg-blue-600/90 border border-blue-500/20 text-white rounded-2xl rounded-tr-none py-3 px-4 max-w-lg shadow-md">
      <p className="text-sm leading-relaxed whitespace-pre-wrap">{message}</p>
    </div>
    <div className="bg-blue-600 w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 shadow-md shadow-blue-600/10">
      <User className="w-4 h-4 text-white" />
    </div>
  </div>
);

// Bot Message with proper Markdown + TTS + BNS convert alert
const BotMessage = ({ message, citations, documents, bnsTransitions, activeLanguage }) => {
  const [copied, setCopied] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(message);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text');
    }
  };

  const toggleSpeak = () => {
    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      return;
    }

    // Clean markdown characters and extra spacing for cleaner speech narration
    const speakText = message
      .replace(/[\*\#\`\_]/g, '')
      .replace(/\[([^\]]+)\]\(([^\)]+)\)/g, '$1')
      .replace(/\s+/g, ' ')
      .trim();

    const utterance = new SpeechSynthesisUtterance(speakText);
    
    // Choose high-quality female voice matching activeLanguage
    const voices = window.speechSynthesis.getVoices();
    let langPrefix = 'en';
    if (activeLanguage === 'Hindi') langPrefix = 'hi';
    else if (activeLanguage === 'Tamil') langPrefix = 'ta';
    else if (activeLanguage === 'Telugu') langPrefix = 'te';
    else if (activeLanguage === 'Bengali') langPrefix = 'bn';
    else if (activeLanguage === 'Marathi') langPrefix = 'mr';

    // Filter voices by selected language prefix
    let langVoices = voices.filter(v => v.lang.toLowerCase().startsWith(langPrefix));
    if (langVoices.length === 0 && langPrefix !== 'en') {
      // Fallback to English voices if no voices found for the active language
      langVoices = voices.filter(v => v.lang.toLowerCase().startsWith('en'));
    }

    // Explicitly exclude known male voices or male keywords to avoid deep/robotic male voices
    const maleNames = ['alex', 'fred', 'daniel', 'oliver', 'rishi', 'george', 'mark', 'david', 'ravi', 'thomas', 'felipe', 'luca', 'ralf', 'vincent', 'male', 'guy', 'man', 'boy', 'yoda', 'xander'];
    const nonMaleVoices = langVoices.filter(v => 
      !maleNames.some(name => v.name.toLowerCase().includes(name))
    );

    // List of known high-quality female voice names/keywords to prioritize
    const femalePriorities = [
      'female', 'samantha', 'zira', 'victoria', 'hazel', 'susan', 'tessa', 'karen', 'moira', 
      'fiona', 'veena', 'kathy', 'sangeeta', 'lekha', 'vani', 'gita', 'sabina', 'heera', 'kanya', 
      'google us english', 'google uk english female', 'google हिन्दी', 'google தமிழ்', 'google తెలుగు', 'google বাঙালি', 'google मराठी'
    ];

    // Search for a matching prioritized female voice in our non-male list
    let femaleVoice = nonMaleVoices.find(v =>
      femalePriorities.some(fav => v.name.toLowerCase().includes(fav))
    );

    // If none match our priorities, take the first non-male voice in that language
    if (!femaleVoice && nonMaleVoices.length > 0) {
      femaleVoice = nonMaleVoices[0];
    }

    // If still no voice, look at all available non-male voices regardless of language
    if (!femaleVoice) {
      const allNonMaleVoices = voices.filter(v => 
        !maleNames.some(name => v.name.toLowerCase().includes(name))
      );
      femaleVoice = allNonMaleVoices.find(v =>
        femalePriorities.some(fav => v.name.toLowerCase().includes(fav))
      ) || allNonMaleVoices[0];
    }

    // Absolute fallback: search all voices for any female name or take any voice
    if (!femaleVoice) {
      femaleVoice = voices.find(v =>
        femalePriorities.some(fav => v.name.toLowerCase().includes(fav))
      ) || voices[0];
    }

    if (femaleVoice) {
      utterance.voice = femaleVoice;
      console.log('Selected TTS Voice:', femaleVoice.name, femaleVoice.lang);
    }

    // Make the narration feel professional and pleasant
    utterance.rate = 0.95;  // Slightly slower for better clarity
    utterance.pitch = 1.05; // Slightly higher pitch for natural female tone

    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = (e) => {
      console.error('Speech synthesis error:', e);
      setIsSpeaking(false);
    };

    setIsSpeaking(true);
    window.speechSynthesis.speak(utterance);
  };

  // Cleanup speech when component unmounts
  useEffect(() => {
    return () => {
      window.speechSynthesis.cancel();
    };
  }, []);

  return (
    <div className="flex items-start space-x-3 justify-start">
      <div className="bg-slate-800/80 w-8 h-8 border border-slate-700 rounded-full flex items-center justify-center flex-shrink-0 shadow-md">
        <Bot className="w-4 h-4 text-blue-400" />
      </div>
      <div className="flex-1 max-w-3xl space-y-3">
        <div className="bg-slate-900 border border-slate-850 rounded-2xl rounded-tl-none p-5 shadow-lg relative group">
          
          {/* Action buttons (copy, speak) */}
          <div className="absolute top-4 right-4 flex items-center space-x-1.5 opacity-60 hover:opacity-100 transition-opacity">
            <button
              onClick={toggleSpeak}
              className="p-1 hover:bg-slate-800 rounded text-slate-400 hover:text-slate-200 transition-colors"
              title={isSpeaking ? "Mute" : "Read Aloud"}
            >
              {isSpeaking ? (
                <VolumeX className="w-3.5 h-3.5 text-red-400" />
              ) : (
                <Volume2 className="w-3.5 h-3.5" />
              )}
            </button>
            <button
              onClick={copyToClipboard}
              className="p-1 hover:bg-slate-800 rounded text-slate-400 hover:text-slate-200 transition-colors"
              title="Copy"
            >
              {copied ? (
                <Check className="w-3.5 h-3.5 text-emerald-400" />
              ) : (
                <Copy className="w-3.5 h-3.5" />
              )}
            </button>
          </div>

          {/* BNS transition highlight */}
          {bnsTransitions && bnsTransitions.length > 0 && (
            <div className="mb-4 bg-gradient-to-r from-blue-900/40 to-indigo-900/40 border border-blue-500/30 rounded-xl p-4 shadow-inner">
              <h4 className="text-xs font-bold text-blue-300 flex items-center mb-2 uppercase tracking-wider">
                <ArrowRightLeft className="w-4 h-4 mr-2 text-indigo-400" /> Statutory Reform Mappings (IPC ⇄ BNS)
              </h4>
              {bnsTransitions.map((tr, idx) => (
                <div key={idx} className="text-xs text-slate-300 space-y-1 mt-2 border-t border-slate-800/80 pt-2 first:mt-0 first:border-0 first:pt-0">
                  <div className="flex items-center space-x-2 text-sm">
                    <span className="font-semibold text-slate-100">{tr.type === 'IPC_TO_BNS' ? 'IPC Sec ' + tr.source : 'BNS Sec ' + tr.source}</span>
                    <ChevronRight className="w-3.5 h-3.5 text-blue-400" />
                    <span className="font-semibold text-emerald-400">{tr.type === 'IPC_TO_BNS' ? 'BNS Sec ' + tr.target : 'IPC Sec ' + tr.target}</span>
                  </div>
                  <div className="font-semibold text-slate-200 mt-1">{tr.title}</div>
                  <div className="text-slate-400 font-light leading-relaxed">{tr.desc}</div>
                </div>
              ))}
            </div>
          )}

          {/* Premium Markdown content */}
          <div className="prose prose-invert prose-sm max-w-none text-slate-200 font-normal leading-relaxed">
            <ReactMarkdown>{message}</ReactMarkdown>
          </div>

        </div>

        {/* Citations panel */}
        {citations && citations.length > 0 && (
          <div className="p-3 bg-slate-900/50 rounded-xl border border-slate-850">
            <h4 className="text-xs font-bold text-blue-400 mb-2 flex items-center tracking-wider uppercase">
              <BookOpen className="w-3.5 h-3.5 mr-1.5" /> Extracted Legal Codes
            </h4>
            <div className="flex flex-wrap gap-1.5">
              {citations.map((citation, index) => (
                <a
                  key={index}
                  href={`https://indiankanoon.org/search/?formInput=${encodeURIComponent(citation)}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white px-2.5 py-1 rounded-full text-[10px] font-semibold tracking-wide border border-slate-700 transition-colors cursor-pointer inline-block"
                  title="Search case/act on Indian Kanoon"
                >
                  {citation}
                </a>
              ))}
            </div>
          </div>
        )}

        {/* References documents panel */}
        {documents && documents.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-xs font-bold text-slate-400 flex items-center tracking-wider uppercase">
              <FileCheck className="w-3.5 h-3.5 mr-1.5" /> Search Citations ({documents.length})
            </h4>
            <div className="grid gap-2">
              {documents.map((doc, index) => (
                <div key={index} className="bg-slate-900/40 hover:bg-slate-900/60 border border-slate-850 rounded-xl p-3.5 transition-colors">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-bold text-slate-300">{doc.filename || 'Statutory Code'}</span>
                    <div className="flex items-center space-x-2">
                      <span className="text-[10px] text-slate-500 font-medium">
                        Similarity: {doc.score ? (doc.score * 100).toFixed(0) : 'N/A'}%
                      </span>
                      <div className="w-16 bg-slate-800 rounded-full h-1">
                        <div
                          className="bg-blue-500 h-1 rounded-full"
                          style={{ width: `${doc.score ? doc.score * 100 : 0}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed font-light line-clamp-2 italic">"{doc.text}"</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// IPC Finder Component
const IPCFinder = ({ onAddMessage, activeModel, activeLanguage }) => {
  const [messages, setMessages] = useState([
    { type: 'bot', content: 'Hello! I am ready. Ask me any queries about Indian criminal laws. I will automatically match the legal codes to the legacy IPC as well as the new **Bharatiya Nyaya Sanhita (BNS)**.' }
  ]);
  const [loading, setLoading] = useState(false);

  const extractCitations = (text) => {
    const patterns = [
      /Section\s+\d+/gi,
      /IPC\s+\d+/gi,
      /BNS\s+\d+/gi,
      /Chapter\s+[IVX]+/gi,
    ];
    const citations = [];
    patterns.forEach(pattern => {
      const matches = text.match(pattern);
      if (matches) {
        citations.push(...matches.map(match => match.trim()));
      }
    });
    return [...new Set(citations)];
  };

  const handleSubmit = async (query) => {
    setMessages(prev => [...prev, { type: 'user', content: query }]);
    setLoading(true);

    try {
      const response = await fetch('http://localhost:5050/query/ipc', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query,
          model: activeModel,
          language: activeLanguage
        }),
      });

      const data = await response.json();

      if (data.answers) {
        // Handle single or multi model formats
        const replies = Object.entries(data.answers).map(([model, text]) => ({
          type: 'bot',
          content: activeModel === 'All Models' ? `### [${model} Response]\n\n${text}` : text,
          citations: extractCitations(text),
          documents: data.retrieved_docs || [],
          bnsTransitions: data.bns_transitions || []
        }));

        setMessages(prev => [...prev, ...replies]);

        const firstModel = Object.keys(data.answers)[0];
        onAddMessage(query, data.answers[firstModel], 'IPC');
      } else {
        setMessages(prev => [
          ...prev,
          {
            type: 'bot',
            content: 'I apologize, but I couldn\'t retrieve specific legal provisions. Please reformulate your question.'
          }
        ]);
      }
    } catch (error) {
      setMessages(prev => [...prev, {
        type: 'bot',
        content: 'Failed to establish connection with the Flask backend. Ensure server is active at `localhost:5050`.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ChatInterface title="IPC / BNS Finder" onSubmit={handleSubmit} loading={loading} activeLanguage={activeLanguage}>
      {messages.map((message, index) => (
        <div key={index}>
          {message.type === 'user' ? (
            <UserMessage message={message.content} />
          ) : (
            <BotMessage
              message={message.content}
              citations={message.citations}
              documents={message.documents}
              bnsTransitions={message.bnsTransitions}
              activeLanguage={activeLanguage}
            />
          )}
        </div>
      ))}
      {loading && (
        <div className="flex items-center space-x-2 text-slate-500 text-xs">
          <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
          <span>Searching criminal code indexes...</span>
        </div>
      )}
    </ChatInterface>
  );
};

// Precedence Finder Component
const PrecedenceFinder = ({ onAddMessage, activeModel, activeLanguage }) => {
  const [messages, setMessages] = useState([
    { type: 'bot', content: 'Describe the facts of your case. I will retrieve case citations, rulings, and summaries of legal precedents matching your description.' }
  ]);
  const [loading, setLoading] = useState(false);

  const extractCitations = (text) => {
    const patterns = [
      /AIR\s+\d{4}\s+[A-Z]{2,4}\s+\d+/gi,
      /\(\d{4}\)\s+\d+\s+SCC\s+\d+/gi,
      /\d{4}\s+SCC\s+\([^)]+\)\s+\d+/gi,
      /\d{4}\s+\(\d+\)\s+SCC\s+\d+/gi,
    ];
    const citations = [];
    patterns.forEach(pattern => {
      const matches = text.match(pattern);
      if (matches) {
        citations.push(...matches.map(match => match.trim()));
      }
    });
    return [...new Set(citations)];
  };

  const handleSubmit = async (query) => {
    setMessages(prev => [...prev, { type: 'user', content: query }]);
    setLoading(true);

    try {
      const res = await fetch('http://localhost:5050/query/legal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query,
          model: activeModel,
          language: activeLanguage
        })
      });
      const data = await res.json();

      if (data.answers) {
        const botMessages = Object.entries(data.answers).map(([model, text]) => ({
          type: 'bot',
          content: activeModel === 'All Models' ? `### [${model} Response]\n\n${text}` : text,
          citations: extractCitations(text),
          documents: data.retrieved_docs || []
        }));

        setMessages(prev => [...prev, ...botMessages]);

        const firstModel = Object.keys(data.answers)[0];
        onAddMessage(query, data.answers[firstModel], 'Precedence');
      } else {
        setMessages(prev => [...prev, {
          type: 'bot',
          content: 'No response retrieved. Make sure database clusters are active.'
        }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, {
        type: 'bot',
        content: 'Error connecting to the backend. Please check connection logs.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ChatInterface title="Judicial Precedence Finder" onSubmit={handleSubmit} loading={loading} activeLanguage={activeLanguage}>
      {messages.map((message, index) => (
        <div key={index}>
          {message.type === 'user' ? (
            <UserMessage message={message.content} />
          ) : (
            <BotMessage
              message={message.content}
              citations={message.citations}
              documents={message.documents}
              activeLanguage={activeLanguage}
            />
          )}
        </div>
      ))}
      {loading && (
        <div className="flex items-center space-x-2 text-slate-500 text-xs">
          <Loader2 className="w-4 h-4 animate-spin text-emerald-500" />
          <span>Searching precedent archives...</span>
        </div>
      )}
    </ChatInterface>
  );
};

// Document Creator Component
const DocumentCreator = ({ onAddMessage, activeModel, activeLanguage }) => {
  const [messages, setMessages] = useState([
    { type: 'bot', content: 'What document would you like to draft? (e.g., *Rental Agreement, Partnership Agreement, Non-Disclosure Agreement*).\n\nSpecify names of parties, duration, covenants, or rent value if known.' }
  ]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (query) => {
    setMessages(prev => [...prev, { type: 'user', content: query }]);
    setLoading(true);

    try {
      const response = await fetch('http://localhost:5050/generate_contract', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          question: query,
          model: activeModel,
          language: activeLanguage
        }),
      });

      const data = await response.json();

      if (data.contract) {
        // Handle answers dictionary
        const replies = Object.entries(data.answers || { [activeModel]: data.contract }).map(([model, text]) => ({
          type: 'bot',
          content: activeModel === 'All Models' ? `### [Draft by ${model}]\n\n${text}` : text,
          documents: data.retrieved_docs || []
        }));

        setMessages(prev => [...prev, ...replies]);
        onAddMessage(query, data.contract, 'Document');
      } else {
        setMessages(prev => [...prev, {
          type: 'bot',
          content: 'Failed to draft agreement. Add more explicit specifications.'
        }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, {
        type: 'bot',
        content: 'Error connecting to contract synthesizer.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ChatInterface title="Legal Drafting Suite" onSubmit={handleSubmit} loading={loading} activeLanguage={activeLanguage}>
      {messages.map((message, index) => (
        <div key={index}>
          {message.type === 'user' ? (
            <UserMessage message={message.content} />
          ) : (
            <BotMessage 
              message={message.content} 
              documents={message.documents} 
              activeLanguage={activeLanguage} 
            />
          )}
        </div>
      ))}
      {loading && (
        <div className="flex items-center space-x-2 text-slate-500 text-xs">
          <Loader2 className="w-4 h-4 animate-spin text-purple-500" />
          <span>Drafting agreement template...</span>
        </div>
      )}
    </ChatInterface>
  );
};

// Real-Time Knowledge Base Ingest Component (Dynamic Uploads)
const KnowledgeBaseUploader = () => {
  const [file, setFile] = useState(null);
  const [dbType, setDbType] = useState('precedence');
  const [loading, setLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState('');
  const [isError, setIsError] = useState(false);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const triggerSelectFile = () => {
    fileInputRef.current.click();
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setStatusMsg('Uploading file, performing text extraction & OCR parsing...');
    setIsError(false);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', dbType);

    try {
      const response = await fetch('http://localhost:5050/api/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        setStatusMsg(data.message || 'File indexed successfully!');
        setFile(null);
      } else {
        setIsError(true);
        setStatusMsg(data.error || 'Failed to process document.');
      }
    } catch (error) {
      setIsError(true);
      setStatusMsg('Network connection failure. Verify Flask server is active.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto bg-slate-900 border border-slate-850 rounded-2xl p-6 shadow-2xl space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white flex items-center tracking-wide">
          <UploadCloud className="w-5 h-5 mr-2.5 text-blue-400" />
          Ingest Knowledge Base Documents
        </h2>
        <p className="text-slate-400 text-xs mt-1.5 font-light leading-relaxed">
          Upload PDF files, scanned image files, or TXT records. The files will be parsed (with OCR fallsbacks if required), chunked, and embedded into the vector store in real-time.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4 bg-slate-950/40 p-3 rounded-xl border border-slate-850">
        <div>
          <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">Target Collection</label>
          <select
            value={dbType}
            onChange={(e) => setDbType(e.target.value)}
            className="w-full bg-slate-900 text-slate-200 border border-slate-800 rounded-lg p-2 text-xs focus:outline-none focus:ring-1 focus:ring-blue-600"
          >
            <option value="precedence">Precedence Collection (Judgments)</option>
            <option value="document">Drafting Collection (Templates)</option>
            <option value="ipc">Criminal Code Collection (IPC/BNS)</option>
          </select>
        </div>
        <div className="flex flex-col justify-end">
          <span className="text-[10px] text-slate-500 font-light leading-snug">
            Vectors will be encoded with SentenceTransformer (all-MiniLM-L6-v2) and indexed dynamically in Milvus.
          </span>
        </div>
      </div>

      {/* Drag & Drop tray */}
      <div
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={triggerSelectFile}
        className="border-2 border-dashed border-slate-800 hover:border-blue-600/50 bg-slate-950/20 hover:bg-slate-950/40 rounded-2xl py-10 text-center cursor-pointer transition-all flex flex-col items-center justify-center space-y-3 p-6 group"
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept=".pdf,.png,.jpg,.jpeg,.webp,.txt"
          className="hidden"
        />
        <div className="bg-slate-900 group-hover:bg-blue-600/10 p-3.5 rounded-2xl border border-slate-800 transition-colors">
          <UploadCloud className="w-6 h-6 text-slate-400 group-hover:text-blue-400 transition-colors" />
        </div>
        <div className="space-y-1">
          <p className="text-sm font-semibold text-slate-200">
            {file ? file.name : 'Drag & drop file here, or click to browse'}
          </p>
          <p className="text-slate-500 text-[10px] uppercase tracking-wide">
            PDF, PNG, JPG, WEBP, TXT (Max 15MB)
          </p>
        </div>
      </div>

      {file && (
        <div className="flex items-center justify-between bg-slate-950/80 border border-slate-850 p-3.5 rounded-xl text-xs">
          <div className="flex items-center space-x-2.5">
            <div className="bg-emerald-500/10 p-2 rounded-lg border border-emerald-500/15">
              <FileCheck className="w-4 h-4 text-emerald-400" />
            </div>
            <div>
              <p className="font-semibold text-slate-200">{file.name}</p>
              <p className="text-slate-500 text-[10px]">{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
            </div>
          </div>
          <button
            onClick={handleUpload}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-4 py-2 rounded-lg transition-colors flex items-center space-x-1.5"
          >
            {loading && <Loader2 className="w-3 h-3 animate-spin" />}
            <span>Process & Index</span>
          </button>
        </div>
      )}

      {statusMsg && (
        <div className={`p-4 rounded-xl border text-xs font-medium ${
          isError 
            ? 'bg-red-950/30 border-red-500/20 text-red-400' 
            : 'bg-blue-950/20 border-blue-500/20 text-blue-400'
        }`}>
          <p className="leading-relaxed">{statusMsg}</p>
        </div>
      )}
    </div>
  );
};

// Chat History Component
const ChatHistory = ({ history, onClear }) => {
  const getTypeColor = (type) => {
    switch (type) {
      case 'IPC': return 'bg-blue-600/20 border-blue-500/30 text-blue-400';
      case 'Precedence': return 'bg-emerald-600/20 border-emerald-500/30 text-emerald-400';
      case 'Document': return 'bg-purple-600/20 border-purple-500/30 text-purple-400';
      default: return 'bg-slate-800 text-slate-300 border-slate-700';
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-850 rounded-2xl p-6 shadow-2xl">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-bold text-white tracking-wide">Archived Conversations</h2>
          <p className="text-slate-400 text-xs font-light">History of user requests and model outputs in the active session.</p>
        </div>
        {history.length > 0 && (
          <button
            onClick={onClear}
            className="bg-red-650 hover:bg-red-700 text-white font-semibold text-xs px-4 py-2.5 rounded-xl transition-all"
          >
            Clear History
          </button>
        )}
      </div>

      {history.length === 0 ? (
        <div className="text-center text-slate-500 py-16 bg-slate-950/10 rounded-2xl border border-slate-850 border-dashed">
          <MessageCircle className="w-10 h-10 mx-auto mb-3 text-slate-600 opacity-60" />
          <p className="text-sm font-medium">No chat records yet.</p>
          <p className="text-xs text-slate-650 mt-1">Start a conversation in other panels to see items appear here.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {history.map((item, index) => (
            <div key={index} className="bg-slate-950/30 border border-slate-850 rounded-2xl p-5 space-y-3">
              <div className="flex items-center justify-between pb-3 border-b border-slate-900">
                <span className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider border ${getTypeColor(item.type)}`}>
                  {item.type} Finder
                </span>
                <span className="text-slate-500 text-xs">
                  {item.timestamp.toLocaleTimeString()}
                </span>
              </div>
              <div className="space-y-1">
                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">User Query</span>
                <p className="text-slate-200 text-sm">{item.message}</p>
              </div>
              <div className="space-y-1">
                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Generated Response</span>
                <div className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap font-light">
                  {item.response}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default App;