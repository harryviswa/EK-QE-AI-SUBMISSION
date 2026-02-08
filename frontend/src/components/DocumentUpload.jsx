import React, { useCallback } from 'react';
import { Upload, X } from 'lucide-react';
import { toast } from 'react-toastify';
import { apiClient } from '../api/client';

export function DocumentUpload({ onUploadSuccess }) {
  const [isDragging, setIsDragging] = React.useState(false);
  const [isLoading, setIsLoading] = React.useState(false);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files.length > 0) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = async (file) => {
    // Validate file type
    const validTypes = ['application/pdf', 'text/plain', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
    
    if (!validTypes.includes(file.type) && !file.name.match(/\.(pdf|txt|xlsx|xls)$/i)) {
      toast.error('Invalid file type. Allowed: PDF, TXT, XLSX, XLS');
      return;
    }

    if (file.size > 50 * 1024 * 1024) {
      toast.error('File too large. Maximum size: 50MB');
      return;
    }

    setIsLoading(true);
    try {
      const response = await apiClient.uploadDocument(file);
      toast.success(`✓ ${response.data.filename} uploaded successfully`);
      onUploadSuccess(response.data);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Upload failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`glassmorphism rounded-2xl p-8 text-center cursor-pointer transition-all duration-300 ${
        isDragging ? 'ring-2 ring-blue-400 scale-105' : ''
      }`}
    >
      <input
        type="file"
        id="file-input"
        onChange={handleFileInput}
        className="hidden"
        disabled={isLoading}
      />
      <label htmlFor="file-input" className="cursor-pointer">
        <Upload className={`w-12 h-12 mx-auto mb-3 transition-transform ${isLoading ? 'animate-pulse' : ''}`} />
        <p className="text-lg font-semibold mb-1">
          {isLoading ? 'Uploading...' : 'Drag & Drop or Click to Upload'}
        </p>
        <p className="text-sm text-gray-300">PDF, TXT, XLSX, XLS (Max 50MB)</p>
      </label>
    </div>
  );
}
