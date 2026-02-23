import React, { useState } from 'react';
import { BookOpen, Bot, BarChart3, Code2 } from 'lucide-react';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { GlassBackground } from './components/GlassBackground';
import { SourceManager } from './components/SourceManager';
import { ValidateTestcases } from './components/ValidateTestcases';
import { SwaggerAutomation } from './components/SwaggerAutomation';
import { AutomationLogAnalyzer } from './components/AutomationLogAnalyzer';
import { QueryChat } from './components/QueryChat';
import './styles/globals.css';

export default function App() {
  const queryChatRef = React.useRef(null);
  const [activeTab, setActiveTab] = useState('assistant');

  const tabs = [
    {
      id: 'knowledge',
      label: 'Knowledge Base',
      description: 'Upload docs, add URLs, manage sources & validate test cases',
      icon: BookOpen,
    },
    {
      id: 'assistant',
      label: 'AI Assistant',
      description: 'Chat with the QE assistant for answers and guidance',
      icon: Bot,
    },
    {
      id: 'log-analyzer',
      label: 'AI Log Analyzer',
      description: 'Analyze automation results and visualize metrics',
      icon: BarChart3,
    },
    {
      id: 'api-autogen',
      label: 'AI API AutoGen',
      description: 'Generate API automation scripts from OpenAPI/Swagger',
      icon: Code2,
    },
  ];

  const handleValidationComplete = (validationResult) => {
    if (queryChatRef.current) {
      queryChatRef.current.addMessage(validationResult, 'validation');
    }
  };

  const handleScriptGenerated = (scriptResult) => {
    if (queryChatRef.current) {
      queryChatRef.current.addMessage(scriptResult, 'automation');
    }
  };

  return (
    <>
      <GlassBackground />
      <ToastContainer
        position="bottom-right"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="dark"
        style={{ opacity: 0.9 }}
      />

      <div className="min-h-screen py-8 px-4">
        <div className="max-w-full mx-auto">
          {/* Title + Tabs */}
          <div className="glassmorphism rounded-2xl p-6 border border-white/10 mb-6">
            <div className="text-center">
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-2">
                NexQA.ai
              </h1>
              <p className="text-gray-300">Quality Engineering Assistant - Redefine your QA process</p>
            </div>

            <div className="mt-6">
              <div className="mx-auto w-full xl:w-[60%]">
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3">
                  {tabs.map((tab) => {
                    const Icon = tab.icon;
                    const isActive = activeTab === tab.id;
                    return (
                      <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`text-left p-4 rounded-xl border transition-all ${
                          isActive
                            ? 'border-blue-400/60 bg-blue-500/10 shadow-lg shadow-blue-500/10'
                            : 'border-white/10 hover:border-white/20 hover:bg-white/5'
                        }`}
                      >
                        <div className="flex items-center gap-3 mb-2">
                          <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${isActive ? 'bg-blue-500/20' : 'bg-white/5'}`}>
                            <Icon className={`w-5 h-5 ${isActive ? 'text-blue-300' : 'text-gray-300'}`} />
                          </div>
                          <div className="font-semibold text-gray-100">{tab.label}</div>
                        </div>
                        <p className="text-xs text-gray-400 leading-relaxed">{tab.description}</p>
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>

          {/* Tab Content */}
          <div className="glassmorphism rounded-2xl p-6 border border-white/10">
            {/* Knowledge Base */}
            <div className={activeTab === 'knowledge' ? 'block' : 'hidden'}>
              <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                <SourceManager onSourcesChange={() => {}} />
                <ValidateTestcases onValidationComplete={handleValidationComplete} />
              </div>
            </div>

            {/* AI Assistant */}
            <div className={activeTab === 'assistant' ? 'block' : 'hidden'}>
              <div className="h-[72vh]">
                <QueryChat ref={queryChatRef} />
              </div>
            </div>

            {/* AI Log Analyzer */}
            <div className={activeTab === 'log-analyzer' ? 'block' : 'hidden'}>
              <AutomationLogAnalyzer />
            </div>

            {/* AI API AutoGen */}
            <div className={activeTab === 'api-autogen' ? 'block' : 'hidden'}>
              <SwaggerAutomation onScriptGenerated={handleScriptGenerated} />
            </div>
          </div>

          {/* Footer */}
          <div className="mt-8 glassmorphism rounded-2xl p-4 border border-white/10 text-center text-gray-400 text-sm">
            <p>Harry | NexGen.AI Your Quality Engineering Assistant</p>
          </div>
        </div>
      </div>
    </>
  );
}
