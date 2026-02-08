import React, { useState } from 'react';
import { Menu, X, Settings, GitBranch } from 'lucide-react';

export function Sidebar({ children }) {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className="flex h-screen gap-4 p-4">
      {/* Sidebar */}
      <div
        className={`glassmorphism rounded-2xl p-6 transition-all duration-300 overflow-y-auto ${
          isOpen ? 'w-80' : 'w-0'
        }`}
        style={{ maxHeight: 'calc(100vh - 2rem)' }}
      >
        {isOpen && (
          <div className="space-y-6">
            {/* Header */}
            <div className="mb-8">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-10 h-10 bg-blue-500/30 rounded-lg flex items-center justify-center">
                  <GitBranch className="w-6 h-6 text-blue-400" />
                </div>
                <div>
                  <h1 className="font-bold text-lg">NexQA.ai</h1>
                  <p className="text-xs text-gray-400">RAG for QE</p>
                </div>
              </div>
            </div>

            {/* Content */}
            <div className="space-y-4">
              {children}
            </div>

            {/* Footer */}
            <div className="mt-auto pt-6 border-t border-white/10">
              <button className="w-full flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-white/10 transition-all">
                <Settings className="w-5 h-5" />
                <span>Settings</span>
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="glassmorphism p-3 rounded-lg h-fit hover:bg-white/20 transition-all"
      >
        {isOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
      </button>

      {/* Main Content */}
      <div className="flex-1 glassmorphism rounded-2xl p-6 flex flex-col overflow-hidden">
        {/* This will be filled by the main content */}
        <div className="flex-1 flex flex-col">
          {/* Content goes here */}
        </div>
      </div>
    </div>
  );
}
