import React, { useState, useRef } from 'react';
import { Upload, CheckCircle } from 'lucide-react';
import { toast } from 'react-toastify';
import { apiClient } from '../api/client';

export function ValidateTestcases({ onValidationComplete }) {
  const [isLoading, setIsLoading] = useState(false);
  const [validationResult, setValidationResult] = useState(null);
  const fileInputRef = useRef(null);

  const handleValidateDeep = async () => {
    if (!validationResult) return;

    setIsLoading(true);
    try {
      console.log('Starting deep validation analysis...');
      // Extract the file from the previous upload - for now just show a message
      toast.info('Deep analysis feature coming soon');
    } catch (error) {
      console.error('Deep validation error:', error);
      toast.error('Deep analysis failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileSelect = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.xlsx') && !file.name.toLowerCase().endsWith('.xls')) {
      toast.error('Please upload an Excel file (.xlsx or .xls)');
      return;
    }

    setIsLoading(true);
    setValidationResult(null);

    try {
      console.log('Uploading file for validation:', file.name);
      const response = await apiClient.validateTestcases(file);
      console.log('Validation response:', response.data);
      
      // Format result for chat display
      const resultMessage = `**Test Case Validation Results**

File: ${response.data.filename}
Status: ${response.data.status}
${response.data.context_chunks_used !== undefined ? `Context chunks used: ${response.data.context_chunks_used}` : ''}
${response.data.message ? `\n${response.data.message}` : ''}

**Validation Analysis:**

${response.data.validation_result || 'No validation results available'}`;

      // Keep local copy (for potential deep analysis) and send to chat window
      setValidationResult(response.data);
      if (onValidationComplete) {
        onValidationComplete(resultMessage);
      }

      toast.success('✓ Test cases validated successfully');
    } catch (error) {
      console.error('Validation error:', error);
      const errorMsg = error.response?.data?.error || error.message || 'Failed to validate test cases';
      console.error('Error message:', errorMsg);
      toast.error(errorMsg);
    } finally {
      setIsLoading(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <div className="glassmorphism rounded-2xl p-6 mt-6">
      <div className="mb-4">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <CheckCircle className="w-5 h-5" />
          Validate Test Cases
        </h2>
        <p className="text-sm text-gray-400 mt-1">
          Upload an Excel file with test cases to validate them
        </p>
      </div>

      <div className="mt-4">
        <label className="flex items-center justify-center w-full p-4 border-2 border-dashed border-blue-400/30 rounded-lg cursor-pointer hover:bg-blue-500/10 transition-all">
          <div className="flex flex-col items-center justify-center">
            <Upload className="w-6 h-6 text-blue-400 mb-2" />
            <span className="text-sm font-medium text-gray-300">
              {isLoading ? 'Validating...' : 'Click to upload Excel file'}
            </span>
            <span className="text-xs text-gray-500 mt-1">(.xlsx or .xls)</span>
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept=".xlsx,.xls"
            onChange={handleFileSelect}
            disabled={isLoading}
            className="hidden"
          />
        </label>
      </div>

    </div>
  );
}
