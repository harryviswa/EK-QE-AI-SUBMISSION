import React, { useState, useRef } from 'react';
import { BarChart3, Upload, Folder, Loader, AlertCircle, CheckCircle, XCircle, Clock } from 'lucide-react';
import { toast } from 'react-toastify';
import { apiClient } from '../api/client';

export function AutomationLogAnalyzer() {
  const [activeTab, setActiveTab] = useState('upload'); // 'upload' or 'folder'
  const [isLoading, setIsLoading] = useState(false);
  const [folderPath, setFolderPath] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragActive(true);
  };

  const handleDragLeave = () => {
    setDragActive(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      uploadLogFiles(Array.from(files));
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files.length > 0) {
      uploadLogFiles(Array.from(e.target.files));
    }
  };

  const uploadLogFiles = async (files) => {
    // Validate file types
    const validTypes = ['xml', 'html', 'log', 'junit', 'txt'];
    const validFiles = files.filter(file => {
      const ext = file.name.split('.').pop().toLowerCase();
      return validTypes.includes(ext);
    });

    if (validFiles.length === 0) {
      toast.error('No valid log files. Supported: XML, HTML, LOG, JUNIT, TXT');
      return;
    }

    setIsLoading(true);
    try {
      console.log(`Uploading ${validFiles.length} log files...`);
      const response = await apiClient.uploadLogFiles(validFiles);
      setAnalysis(response.data);
      toast.success(`✓ Analyzed ${validFiles.length} log file(s)`);
    } catch (error) {
      console.error('Upload error:', error);
      const errorMsg = error.response?.data?.error || error.message || 'Analysis failed';
      toast.error(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  const analyzeFolder = async (e) => {
    e.preventDefault();
    if (!folderPath.trim()) {
      toast.error('Please enter a folder path');
      return;
    }

    setIsLoading(true);
    try {
      console.log('Analyzing folder:', folderPath);
      const response = await apiClient.analyzeLogFolder(folderPath, true);
      setAnalysis(response.data);
      toast.success('✓ Folder analysis completed');
    } catch (error) {
      console.error('Analysis error:', error);
      const errorMsg = error.response?.data?.error || error.message || 'Analysis failed';
      toast.error(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  const MetricsCard = ({ label, value, icon: Icon, color }) => (
    <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-lg p-4 border border-gray-700/50">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs text-gray-400 mb-1">{label}</p>
          <p className={`text-2xl font-bold ${color}`}>{value}</p>
        </div>
        <Icon className={`w-8 h-8 ${color} opacity-70`} />
      </div>
    </div>
  );

  const ErrorList = ({ errors }) => (
    <div className="space-y-2 max-h-64 overflow-y-auto">
      {errors.slice(0, 10).map((error, idx) => (
        <div key={idx} className="p-2 bg-red-500/10 border border-red-500/20 rounded text-xs text-red-300">
          <div className="font-semibold">{error.name || 'Test Case'}</div>
          <div className="text-red-400 mt-1">{error.type}: {error.message?.substring(0, 100) || 'Unknown error'}</div>
        </div>
      ))}
    </div>
  );

  return (
    <div className="glassmorphism rounded-2xl p-6 mt-6">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <BarChart3 className="w-5 h-5" />
          Automation Log Analyzer
        </h2>
        <p className="text-sm text-gray-400 mt-1">
          Analyze test automation logs and get AI-powered insights
        </p>
      </div>

      {/* Tab Selection */}
      <div className="flex gap-2 mb-6 border-b border-gray-700">
        <button
          onClick={() => setActiveTab('upload')}
          className={`px-4 py-2 font-medium transition-all ${
            activeTab === 'upload'
              ? 'border-b-2 border-blue-400 text-blue-400'
              : 'text-gray-400 hover:text-gray-300'
          }`}
        >
          <Upload className="w-4 h-4 inline mr-2" />
          Upload Files
        </button>
        <button
          onClick={() => setActiveTab('folder')}
          className={`px-4 py-2 font-medium transition-all ${
            activeTab === 'folder'
              ? 'border-b-2 border-blue-400 text-blue-400'
              : 'text-gray-400 hover:text-gray-300'
          }`}
        >
          <Folder className="w-4 h-4 inline mr-2" />
          Analyze Folder
        </button>
      </div>

      {/* Upload Tab */}
      {activeTab === 'upload' && (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`mb-6 p-8 rounded-lg border-2 border-dashed transition-all cursor-pointer ${
            dragActive
              ? 'border-blue-400 bg-blue-500/10'
              : 'border-gray-600 bg-gray-900/30 hover:border-gray-500'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            multiple
            onChange={handleFileInput}
            className="hidden"
            disabled={isLoading}
            accept=".xml,.html,.log,.junit,.txt"
          />
          <label onClick={() => fileInputRef.current?.click()} className="cursor-pointer block text-center">
            <Upload className={`w-10 h-10 mx-auto mb-2 ${dragActive ? 'text-blue-400' : 'text-gray-400'}`} />
            <p className="font-semibold mb-1">{isLoading ? 'Analyzing...' : 'Drag & Drop or Click'}</p>
            <p className="text-sm text-gray-400">
              Supported: XML, HTML, LOG, JUNIT, TXT (Max 50MB)
            </p>
          </label>
        </div>
      )}

      {/* Folder Tab */}
      {activeTab === 'folder' && (
        <form onSubmit={analyzeFolder} className="mb-6 space-y-3">
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-300">
              <Folder className="w-4 h-4 inline mr-2" />
              Folder Path
            </label>
            <input
              type="text"
              value={folderPath}
              onChange={(e) => setFolderPath(e.target.value)}
              placeholder="E.g., C:\TestResults or /home/user/logs"
              className="w-full glassmorphism px-3 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 bg-white/10"
              disabled={isLoading}
            />
            <p className="text-xs text-gray-500 mt-1">
              Enter the absolute path to a folder containing log files
            </p>
          </div>
          <button
            type="submit"
            disabled={isLoading || !folderPath.trim()}
            className="w-full px-3 py-2 bg-blue-500/30 hover:bg-blue-500/50 rounded-lg transition-all disabled:opacity-50 font-medium"
          >
            {isLoading ? 'Analyzing...' : 'Analyze Folder'}
          </button>
        </form>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <Loader className="w-8 h-8 text-blue-400 animate-spin mr-3" />
          <span className="text-gray-300">Analyzing logs and generating insights...</span>
        </div>
      )}

      {/* Analysis Results */}
      {analysis && !isLoading && (
        <div className="space-y-6">
          {/* Summary Metrics */}
          {analysis.summary && (
            <div>
              <h3 className="text-lg font-semibold mb-4 text-gray-300">Test Execution Summary</h3>
              <div className="grid grid-cols-2 lg:grid-cols-6 gap-3">
                <MetricsCard
                  label="Total Tests"
                  value={analysis.summary.total_tests}
                  icon={BarChart3}
                  color="text-blue-400"
                />
                <MetricsCard
                  label="Passed"
                  value={analysis.summary.passed}
                  icon={CheckCircle}
                  color="text-green-400"
                />
                <MetricsCard
                  label="Failed"
                  value={analysis.summary.failed}
                  icon={XCircle}
                  color="text-red-400"
                />
                <MetricsCard
                  label="Skipped"
                  value={analysis.summary.skipped}
                  icon={Clock}
                  color="text-yellow-400"
                />
                <MetricsCard
                  label="Pass Rate"
                  value={`${analysis.summary.pass_rate}%`}
                  icon={CheckCircle}
                  color="text-green-400"
                />
                <MetricsCard
                  label="Exec Time"
                  value={`${analysis.summary.execution_time}s`}
                  icon={Clock}
                  color="text-purple-400"
                />
              </div>
            </div>
          )}

          {/* Pass Rate Progress Bar */}
          {analysis.summary && (
            <div>
              <h3 className="text-lg font-semibold mb-3 text-gray-300">Pass Rate Breakdown</h3>
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between mb-1 text-sm">
                    <span className="text-gray-400">Success Rate</span>
                    <span className="text-green-400 font-semibold">{analysis.summary.success_rate}%</span>
                  </div>
                  <div className="w-full bg-gray-800 rounded-full h-2 overflow-hidden">
                    <div
                      className="bg-gradient-to-r from-green-500 to-green-400 h-full transition-all"
                      style={{ width: `${analysis.summary.success_rate}%` }}
                    ></div>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between mb-1 text-sm">
                    <span className="text-gray-400">Pass Rate</span>
                    <span className="text-blue-400 font-semibold">{analysis.summary.pass_rate}%</span>
                  </div>
                  <div className="w-full bg-gray-800 rounded-full h-2 overflow-hidden">
                    <div
                      className="bg-gradient-to-r from-blue-500 to-blue-400 h-full transition-all"
                      style={{ width: `${analysis.summary.pass_rate}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Common Errors */}
          {analysis.summary && Object.keys(analysis.summary.common_errors || {}).length > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-3 text-gray-300">Common Error Types</h3>
              <div className="space-y-2">
                {Object.entries(analysis.summary.common_errors).map(([errorType, count]) => (
                  <div key={errorType} className="flex items-center justify-between p-2 bg-red-500/10 rounded border border-red-500/20">
                    <span className="text-sm text-red-300">{errorType}</span>
                    <span className="px-2 py-1 bg-red-500/20 text-red-400 rounded text-xs font-semibold">{count}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Failed Tests */}
          {analysis.summary && analysis.summary.failed_tests_count > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-3 text-gray-300">
                Top Failed Tests ({analysis.summary.failed_tests_count} total)
              </h3>
              <ErrorList errors={analysis.summary.top_failed_tests || []} />
            </div>
          )}

          {/* AI Insights */}
          {analysis.insights && (
            <div className="p-4 bg-purple-500/10 border border-purple-500/30 rounded-lg">
              <h3 className="text-lg font-semibold mb-3 text-purple-300">AI-Generated Insights</h3>
              <div className="text-sm text-gray-300 whitespace-pre-wrap max-h-96 overflow-y-auto">
                {analysis.insights}
              </div>
            </div>
          )}

          {/* File Summary */}
          {analysis.file_count && (
            <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg text-xs text-blue-300">
              <p>📁 Analyzed <strong>{analysis.file_count}</strong> log file(s) from <strong>{analysis.uploaded_files?.length || 'multiple'}</strong> source(s)</p>
            </div>
          )}

          {/* Reset Button */}
          <button
            onClick={() => {
              setAnalysis(null);
              setFolderPath('');
              if (fileInputRef.current) fileInputRef.current.value = '';
            }}
            className="w-full mt-4 px-3 py-2 bg-blue-500/30 hover:bg-blue-500/50 rounded-lg transition-all text-sm font-medium"
          >
            Analyze New Logs
          </button>
        </div>
      )}

      {/* Empty State */}
      {!analysis && !isLoading && (
        <div className="py-8 text-center text-gray-400">
          <BarChart3 className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>Upload or select log files to analyze test results</p>
        </div>
      )}
    </div>
  );
}
