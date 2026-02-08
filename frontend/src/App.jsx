import React, { useState } from 'react';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { GlassBackground } from './components/GlassBackground';
import { SourceManager } from './components/SourceManager';
import { ValidateTestcases } from './components/ValidateTestcases';
import { SwaggerAutomation } from './components/SwaggerAutomation';
import { QueryChat } from './components/QueryChat';
import './styles/globals.css';

export default function App() {
  const queryChatRef = React.useRef(null);
  const [uploadedDocs, setUploadedDocs] = useState([]);

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
          {/* Header */}
          <div className="mb-8 text-center">
            <div className="inline-block glassmorphism px-8 py-4 rounded-2xl border border-white/20">
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-2">
                NexQA.ai
              </h1>
              <p className="text-gray-300">Quality Engineering Assistant - Redefine your QA process</p>
            </div>
          </div>

          {/* Main Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
            {/* Sidebar */}
            <div className="lg:col-span-1 space-y-6">
              <SourceManager onSourcesChange={() => {}} />
              <ValidateTestcases onValidationComplete={handleValidationComplete} />
              <SwaggerAutomation onScriptGenerated={handleScriptGenerated} />
            </div>

            {/* Main Chat Area */}
            <div className="lg:col-span-4 glassmorphism rounded-2xl p-6 flex flex-col" style={{ height: '82vh' }}>
              <QueryChat ref={queryChatRef} />
            </div>
          </div>

          {/* Footer */}
          <div className="mt-8 text-center text-gray-400 text-sm">
            <p>NexQA.ai • Powered by Ollama</p>
          </div>
        </div>
      </div>
    </>
  );
}
