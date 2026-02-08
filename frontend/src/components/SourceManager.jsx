import React, { useState } from 'react';
import { FileUp } from 'lucide-react';
import { DocumentUpload } from './DocumentUpload';
import { toast } from 'react-toastify';
import { apiClient } from '../api/client';

export function SourceManager({ onSourcesChange }) {
  const [sources, setSources] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [urlInput, setUrlInput] = useState('');

  const loadSources = async () => {
    try {
      const response = await apiClient.listDocuments();
      setSources(response.data.documents || []);
      onSourcesChange(response.data.documents);
    } catch (error) {
      toast.error('Failed to load sources');
    }
  };

  React.useEffect(() => {
    loadSources();
  }, []);

  const handleAddUrl = async (e) => {
    e.preventDefault();
    if (!urlInput.trim()) return;

    setIsLoading(true);
    try {
      const response = await apiClient.addUrl(urlInput);
      toast.success(`✓ URL added: ${response.data.url}`);
      setUrlInput('');
      await loadSources(); // Refresh the sources list
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to add URL');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="glassmorphism rounded-2xl p-6">
      <div className="mb-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <FileUp className="w-5 h-5" />
            Knowledge Sources
          </h2>
        </div>

        {/* Combined upload area: document upload + optional URL input */}
        <div className="mt-4">
          <DocumentUpload onUploadSuccess={() => loadSources()} />

          {/* Always show the URL input (remove collapsible + button) */}
          <form onSubmit={handleAddUrl} className="mt-4 space-y-2">
            <input
              type="url"
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
              placeholder="Enter URL (e.g., https://docs.example.com)"
              className="w-full glassmorphism px-3 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 bg-white/10"
              disabled={isLoading}
            />
            <div className="flex gap-2">
              <button
                type="submit"
                disabled={isLoading || !urlInput.trim()}
                className="flex-1 px-3 py-2 bg-blue-500/30 hover:bg-blue-500/50 rounded-lg transition-all disabled:opacity-50"
              >
                {isLoading ? 'Adding...' : 'Add URL'}
              </button>
              <button
                type="button"
                onClick={() => {
                  // Clear the input but do not collapse the form
                  setUrlInput('');
                }}
                className="px-3 py-2 bg-red-500/20 hover:bg-red-500/30 rounded-lg transition-all"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>

      <div className="space-y-2">
        {sources.length === 0 ? (
          <p className="text-gray-400 text-sm">No documents uploaded yet</p>
        ) : (
          sources.map((source, idx) => (
            <div
              key={idx}
              className="p-3 bg-white/5 rounded-lg border border-white/10 flex items-start justify-between group hover:bg-white/10 transition-all"
            >
              <div>
                <p className="text-sm font-medium truncate">{source}</p>
                <p className="text-xs text-gray-400">Document source</p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
