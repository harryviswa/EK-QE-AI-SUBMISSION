import React, { useState, useRef } from 'react';
import { BarChart3, Upload, Folder, Loader, AlertCircle, CheckCircle, XCircle, Clock, TrendingUp, Info } from 'lucide-react';
import { toast } from 'react-toastify';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { apiClient } from '../api/client';

export function AutomationLogAnalyzer() {
  const [activeTab, setActiveTab] = useState('upload'); // 'upload' or 'folder'
  const [isLoading, setIsLoading] = useState(false);
  const [folderPath, setFolderPath] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [processingStage, setProcessingStage] = useState('');
  const [progress, setProgress] = useState(0);
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
      const ext = file.name.split('.').pop
().toLowerCase();
      return validTypes.includes(ext);
    });

    if (validFiles.length === 0) {
      toast.error('No valid log files. Supported: XML, HTML, LOG, JUNIT, TXT');
      return;
    }

    setIsLoading(true);
    setProgress(0);
    
    const stages = [
      { stage: 'Uploading files...', progress: 5, delay: 100 },
      { stage: 'Parsing logs...', progress: 30, delay: 10000 },
      { stage: 'Analyzing metrics...', progress: 45, delay: 3000 },
      { stage: 'Generating AI insights...', progress: 60, delay: 50000 },
      { stage: 'Creating forecast...', progress: 75, delay: 7000 },
      { stage: 'Identifying test gaps...', progress: 90, delay: 20000 },
    ];
    
    try {
      console.log(`Uploading ${validFiles.length} log files...`);
      
      // Simulate progress while API call is in flight
      // Spread updates over ~2 minutes to match LLM processing time
      let currentStageIndex = 0;
      const progressInterval = setInterval(() => {
        if (currentStageIndex < stages.length) {
          const { stage, progress } = stages[currentStageIndex];
          setProcessingStage(stage);
          setProgress(progress);
          currentStageIndex++;
        }
      }, 15000); // Update every 15 seconds (6 stages = ~90 seconds)
      
      try {
        // Make API call
        const response = await apiClient.uploadLogFiles(validFiles);
        
        // Clear interval and complete progress
        clearInterval(progressInterval);
        
        setProcessingStage('Complete!');
        setProgress(100);
        
        console.log('[LOG ANALYZER] Upload response:', response.data);
        console.log('[LOG ANALYZER] LLM metrics:', response.data.llm_metrics);
        console.log('[LOG ANALYZER] Insights:', response.data.insights);
        console.log('[LOG ANALYZER] Forecast:', response.data.forecast);
        console.log('[LOG ANALYZER] Missing cases:', response.data.missing_test_cases);
        
        setAnalysis(response.data);
        toast.success(`✓ Analyzed ${validFiles.length} log file(s)`);
      } catch (apiError) {
        clearInterval(progressInterval);
        throw apiError;
      }
    } catch (error) {
      console.error('Upload error:', error);
      const errorMsg = error.response?.data?.error || error.message || 'Analysis failed';
      toast.error(errorMsg);
    } finally {
      // Show results immediately after completion
      setTimeout(() => setIsLoading(false), 500);
      // Reset progress indicators after showing results
      setTimeout(() => {
        setProcessingStage('');
        setProgress(0);
      }, 1500);
    }
  };

  const analyzeFolder = async (e) => {
    e.preventDefault();
    if (!folderPath.trim()) {
      toast.error('Please enter a folder path');
      return;
    }

    setIsLoading(true);
    setProgress(0);
    
    const stages = [
      { stage: 'Scanning folder...', progress: 15 },
      { stage: 'Parsing logs...', progress: 30 },
      { stage: 'Analyzing metrics...', progress: 45 },
      { stage: 'Generating AI insights...', progress: 60 },
      { stage: 'Creating forecast...', progress: 75 },
      { stage: 'Identifying test gaps...', progress: 90 },
    ];
    
    try {
      console.log('Analyzing folder:', folderPath);
      
      // Simulate progress while API call is in flight
      // Spread updates over ~2 minutes to match LLM processing time
      let currentStageIndex = 0;
      const progressInterval = setInterval(() => {
        if (currentStageIndex < stages.length) {
          const { stage, progress } = stages[currentStageIndex];
          setProcessingStage(stage);
          setProgress(progress);
          currentStageIndex++;
        }
      }, 15000); // Update every 15 seconds (6 stages = ~90 seconds)
      
      try {
        // Make API call
        const response = await apiClient.analyzeLogFolder(folderPath, true);
        
        // Clear interval and complete progress
        clearInterval(progressInterval);
        
        setProcessingStage('Complete!');
        setProgress(100);
        
        console.log('[LOG ANALYZER] Folder response:', response.data);
        console.log('[LOG ANALYZER] LLM metrics:', response.data.llm_metrics);
        console.log('[LOG ANALYZER] Insights:', response.data.insights);
        console.log('[LOG ANALYZER] Forecast:', response.data.forecast);
        console.log('[LOG ANALYZER] Missing cases:', response.data.missing_test_cases);
        
        setAnalysis(response.data);
        toast.success('✓ Folder analysis completed');
      } catch (apiError) {
        clearInterval(progressInterval);
        throw apiError;
      }
    } catch (error) {
      console.error('Analysis error:', error);
      const errorMsg = error.response?.data?.error || error.message || 'Analysis failed';
      toast.error(errorMsg);
    } finally {
      // Show results immediately after completion
      setTimeout(() => setIsLoading(false), 500);
      // Reset progress indicators after showing results
      setTimeout(() => {
        setProcessingStage('');
        setProgress(0);
      }, 1500);
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

  const ChartCard = ({ title, subtitle, children }) => (
    <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-4 border border-gray-700/50">
      <div className="mb-3">
        <h4 className="text-sm font-semibold text-gray-200">{title}</h4>
        {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
      </div>
      {children}
    </div>
  );

  const DonutChart = ({ data }) => {
    const size = 140;
    const stroke = 16;
    const radius = (size - stroke) / 2;
    const circumference = 2 * Math.PI * radius;
    const total = data.reduce((sum, item) => sum + item.value, 0) || 1;

    let offset = 0;

    return (
      <div className="flex items-center gap-4">
        <svg width={size} height={size} className="shrink-0">
          <g transform={`rotate(-90 ${size / 2} ${size / 2})`}>
            <circle
              cx={size / 2}
              cy={size / 2}
              r={radius}
              stroke="#1f2937"
              strokeWidth={stroke}
              fill="none"
            />
            {data.map((item, idx) => {
              const dash = (item.value / total) * circumference;
              const dashArray = `${dash} ${circumference - dash}`;
              const element = (
                <circle
                  key={item.label}
                  cx={size / 2}
                  cy={size / 2}
                  r={radius}
                  stroke={item.color}
                  strokeWidth={stroke}
                  fill="none"
                  strokeDasharray={dashArray}
                  strokeDashoffset={-offset}
                  strokeLinecap="round"
                />
              );
              offset += dash;
              return element;
            })}
          </g>
        </svg>
        <div className="space-y-2 text-xs">
          {data.map((item) => (
            <div key={item.label} className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }}></span>
                <span className="text-gray-300">{item.label}</span>
              </div>
              <span className="text-gray-400 font-semibold">{item.value}</span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const StackedBar = ({ data }) => {
    const total = data.reduce((sum, item) => sum + item.value, 0) || 1;
    return (
      <div>
        <div className="flex w-full h-3 rounded-full overflow-hidden bg-gray-800">
          {data.map((item) => (
            <div
              key={item.label}
              className="h-full"
              style={{ width: `${(item.value / total) * 100}%`, backgroundColor: item.color }}
            ></div>
          ))}
        </div>
        <div className="flex flex-wrap gap-3 mt-3 text-xs text-gray-400">
          {data.map((item) => (
            <div key={item.label} className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }}></span>
              <span>{item.label}</span>
              <span className="text-gray-500">{item.value}</span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const HorizontalBarChart = ({ data, maxBars = 6, color = '#60a5fa' }) => {
    const entries = Object.entries(data || {}).slice(0, maxBars);
    const maxValue = Math.max(...entries.map(([, value]) => value), 1);

    return (
      <div className="space-y-2">
        {entries.map(([label, value]) => (
          <div key={label} className="space-y-1">
            <div className="flex justify-between text-xs text-gray-400">
              <span className="truncate max-w-[65%]" title={label}>{label}</span>
              <span className="text-gray-300 font-semibold">{value}</span>
            </div>
            <div className="w-full bg-gray-800 rounded-full h-2">
              <div
                className="h-2 rounded-full"
                style={{ width: `${(value / maxValue) * 100}%`, backgroundColor: color }}
              ></div>
            </div>
          </div>
        ))}
      </div>
    );
  };

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
        <div className="py-12">
          <div className="flex items-center justify-center mb-6">
            <Loader className="w-8 h-8 text-blue-400 animate-spin mr-3" />
            <span className="text-gray-300 text-lg">{processingStage || 'Processing...'}</span>
          </div>
          
          <p className="text-center text-sm text-gray-400 mb-6 max-w-md mx-auto">
            <AlertCircle className="w-4 h-4 inline mr-1 opacity-70" />
            AI analysis with LLM insights may take 2-3 minutes. Please wait...
          </p>
          
          {/* Progress Pipeline */}
          <div className="max-w-2xl mx-auto">
            <div className="relative">
              {/* Progress Bar */}
              <div className="w-full bg-gray-800 rounded-full h-6 overflow-hidden mb-6">
                <div
                  className="bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 h-full transition-all duration-500 ease-out"
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
              
              {/* Pipeline Stages */}
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-xs">
                {[
                  { label: 'Upload', pct: 15 },
                  { label: 'Parse', pct: 30 },
                  { label: 'Analyze', pct: 45 },
                  { label: 'AI Insights', pct: 60 },
                  { label: 'Forecast', pct: 75 },
                  { label: 'Gap Analysis', pct: 90 },
                ].map((stage) => (
                  <div
                    key={stage.label}
                    className={`p-2 rounded-lg border transition-all ${
                      progress >= stage.pct
                        ? 'bg-blue-500/20 border-blue-400/50 text-blue-300'
                        : 'bg-gray-800/50 border-gray-700 text-gray-500'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{stage.label}</span>
                      {progress >= stage.pct && (
                        <CheckCircle className="w-4 h-4 text-blue-400" />
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Analysis Results */}
      {analysis && !isLoading && (
        <div className="space-y-6">
          {/* Summary Metrics */}
          {analysis.summary && (
            <div>
              <h3 className="text-lg font-semibold mb-4 text-gray-300">Test Execution Summary</h3>
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <MetricsCard
                  label="Total Tests"
                  value={analysis.summary.total_tests ?? 0}
                  icon={BarChart3}
                  color="text-blue-400"
                />
                <MetricsCard
                  label="Passed"
                  value={analysis.summary.passed ?? 0}
                  icon={CheckCircle}
                  color="text-green-400"
                />
                <MetricsCard
                  label="Failed"
                  value={analysis.summary.failed ?? 0}
                  icon={XCircle}
                  color="text-red-400"
                />
                <MetricsCard
                  label="Skipped"
                  value={analysis.summary.skipped ?? 0}
                  icon={Clock}
                  color="text-yellow-400"
                />
                <MetricsCard
                  label="Success Rate"
                  value={`${analysis.summary.success_rate ?? 0}%`}
                  icon={TrendingUp}
                  color="text-emerald-400"
                />
                <MetricsCard
                  label="Exec Time"
                  value={`${analysis.summary.execution_time ?? 0}s`}
                  icon={Clock}
                  color="text-purple-400"
                />
              </div>
            </div>
          )}

          {/* Visual Analytics */}
          {analysis.summary && (
            <div>
              <h3 className="text-lg font-semibold mb-4 text-gray-300">Visual Analytics</h3>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <ChartCard title="Test Outcome Distribution" subtitle="Pass / Fail / Skip breakdown">
                  <DonutChart
                    data={[
                      { label: 'Passed', value: analysis.summary.passed || 0, color: '#22c55e' },
                      { label: 'Failed', value: analysis.summary.failed || 0, color: '#ef4444' },
                      { label: 'Skipped', value: analysis.summary.skipped || 0, color: '#f59e0b' }
                    ]}
                  />
                </ChartCard>

                <ChartCard title="Execution Health" subtitle="Stacked outcome bar">
                  <StackedBar
                    data={[
                      { label: 'Passed', value: analysis.summary.passed || 0, color: '#22c55e' },
                      { label: 'Failed', value: analysis.summary.failed || 0, color: '#ef4444' },
                      { label: 'Skipped', value: analysis.summary.skipped || 0, color: '#f59e0b' }
                    ]}
                  />
                  <div className="mt-4 p-2 rounded-lg bg-gray-900/60 border border-gray-800">
                    <p className="text-gray-400">Success Rate</p>
                    <p className="text-green-400 font-semibold text-sm">{analysis.summary.success_rate ?? 0}%</p>
                  </div>
                </ChartCard>

                {analysis.summary.common_errors && Object.keys(analysis.summary.common_errors).length > 0 && (
                  <ChartCard title="Common Error Types" subtitle="Frequency by error category">
                    <HorizontalBarChart data={analysis.summary.common_errors} color="#f97316" />
                  </ChartCard>
                )}

                {analysis.summary.top_failed_tests && analysis.summary.top_failed_tests.length > 0 && (
                  <ChartCard title="Failure Hotspots" subtitle="Top failing tests">
                    <HorizontalBarChart
                      data={analysis.summary.top_failed_tests.reduce((acc, item) => {
                        const label = item.name || 'Test Case';
                        acc[label] = (acc[label] || 0) + 1;
                        return acc;
                      }, {})}
                      color="#38bdf8"
                    />
                  </ChartCard>
                )}
              </div>
            </div>
          )}

          {/* Success Rate Progress Bar */}
          {analysis.summary && (
            <div>
              <h3 className="text-lg font-semibold mb-4 text-gray-300">Success Rate</h3>
              <div className="relative group">
                <div className="flex justify-between mb-2 text-sm">
                  <span className="text-gray-400 flex items-center gap-1">
                    Success Rate
                    <Info className="w-3 h-3 opacity-50" />
                  </span>
                  <span className="text-green-400 font-semibold text-lg">{analysis.summary.success_rate ?? 0}%</span>
                </div>
                <div className="w-full bg-gray-800 rounded-full h-4 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-green-500 to-green-400 h-full transition-all"
                    style={{ width: `${analysis.summary.success_rate ?? 0}%` }}
                  ></div>
                </div>
                <div className="absolute top-full left-0 mt-2 hidden group-hover:block bg-gray-900 text-xs text-gray-300 px-3 py-2 rounded-lg shadow-lg w-64 z-10">
                  Passed + Skipped tests (excludes failed & errors)
                </div>
              </div>
            </div>
          )}
          {/* LLM-Derived Metrics */}
          {analysis.llm_metrics && (
            <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-lg">
              <h3 className="text-lg font-semibold mb-3 text-emerald-300">LLM-Derived Metrics</h3>
              {analysis.llm_metrics.status && analysis.llm_metrics.status !== 'ok' ? (
                <div className="text-sm text-gray-300">{analysis.llm_metrics.reason || analysis.llm_metrics.error || 'Metrics unavailable'}</div>
              ) : (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 text-sm text-gray-200">
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Overall Health</span>
                      <span className="font-semibold text-emerald-300">{analysis.llm_metrics.overall_health || 'Unknown'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Risk Level</span>
                      <span className="font-semibold text-orange-300">{analysis.llm_metrics.risk_level || 'Unknown'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Stability Score</span>
                      <span className="font-semibold text-blue-300">{analysis.llm_metrics.stability_score ?? 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Failure Trend</span>
                      <span className="font-semibold text-purple-300">{analysis.llm_metrics.failure_trend || 'Unknown'}</span>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div>
                      <p className="text-gray-400 mb-1">Primary Failure Modes</p>
                      <ul className="list-disc list-inside space-y-1 text-gray-300">
                        {(analysis.llm_metrics.primary_failure_modes || []).slice(0, 4).map((item, idx) => (
                          <li key={idx}>{item}</li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <p className="text-gray-400 mb-1">Priority Actions</p>
                      <ul className="list-disc list-inside space-y-1 text-gray-300">
                        {(analysis.llm_metrics.priority_actions || []).slice(0, 4).map((item, idx) => (
                          <li key={idx}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              )}
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
              <div className="text-sm text-gray-300 prose prose-invert prose-sm max-w-none max-h-96 overflow-y-auto">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{analysis.insights}</ReactMarkdown>
              </div>
            </div>
          )}

          {/* Forecaster */}
          {analysis.forecast && (
            <div className="p-4 bg-cyan-500/10 border border-cyan-500/30 rounded-lg">
              <h3 className="text-lg font-semibold mb-3 text-cyan-300 flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                Test Health Forecast
              </h3>
              <div className="text-sm text-gray-300 prose prose-invert prose-sm max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{analysis.forecast}</ReactMarkdown>
              </div>
            </div>
          )}

          {/* Missing Test Cases */}
          {analysis.missing_test_cases && (
            <div className="p-4 bg-amber-500/10 border border-amber-500/30 rounded-lg">
              <h3 className="text-lg font-semibold mb-3 text-amber-300 flex items-center gap-2">
                <AlertCircle className="w-5 h-5" />
                Test Coverage Gaps
              </h3>
              <p className="text-xs text-amber-200/70 mb-3">
                Based on knowledge base analysis - missing test scenarios identified
              </p>
              <div className="text-sm text-gray-300 prose prose-invert prose-sm max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{analysis.missing_test_cases}</ReactMarkdown>
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
