import React, { useState, useRef } from 'react';
import { Code, Copy, Download, AlertCircle } from 'lucide-react';
import { toast } from 'react-toastify';
import { apiClient } from '../api/client';

export function SwaggerAutomation({ onScriptGenerated }) {
  const [swaggerUrl, setSwaggerUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [generatedScript, setGeneratedScript] = useState(null);
  const scriptInputRef = useRef(null);

  const handleGenerateScript = async (e) => {
    e.preventDefault();
    if (!swaggerUrl.trim()) {
      toast.error('Please enter a Swagger/OpenAPI URL');
      return;
    }

    setIsLoading(true);
    try {
      console.log('Generating API automation script from:', swaggerUrl);
      const response = await apiClient.generateFromSwagger(swaggerUrl);
      console.log('Script generation response:', response.data);

      setGeneratedScript({
        filename: response.data.filename,
        script: response.data.script,
        message: response.data.message,
        status: response.data.status,
      });

      // Send to chat if callback provided
      if (onScriptGenerated) {
        const scriptPreview = `**API Automation Script Generated**

File: ${response.data.filename}
Status: ${response.data.status}

Generated from: ${swaggerUrl}

The Python automation script has been successfully generated. You can download it using the button below or copy its contents.

\`\`\`python
${response.data.script.substring(0, 500)}...
\`\`\`

The script includes:
- API client class with request handling
- Auto-generated endpoint methods from the OpenAPI spec
- Built-in authentication support
- Example usage
- Test suite with pytest`;

        onScriptGenerated(scriptPreview);
      }

      toast.success('✓ API automation script generated successfully');
    } catch (error) {
      console.error('Script generation error:', error);
      const errorMsg = error.response?.data?.error || error.message || 'Failed to generate script';
      console.error('Error message:', errorMsg);
      toast.error(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  const copyScriptToClipboard = () => {
    if (generatedScript?.script) {
      navigator.clipboard.writeText(generatedScript.script);
      toast.info('Script copied to clipboard');
    }
  };

  const downloadScript = () => {
    if (generatedScript?.script && generatedScript?.filename) {
      apiClient.downloadFile(generatedScript.filename, generatedScript.script, 'text/plain');
      toast.info(`Downloaded ${generatedScript.filename}`);
    }
  };

  return (
    <div className="glassmorphism rounded-2xl p-6 mt-6">
      <div className="mb-4">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <Code className="w-5 h-5" />
          API Automation Script Generator
        </h2>
        <p className="text-sm text-gray-400 mt-1">
          Generate Python API automation scripts from Swagger/OpenAPI URLs
        </p>
      </div>

      <form onSubmit={handleGenerateScript} className="space-y-3">
        <div>
          <input
            ref={scriptInputRef}
            type="url"
            value={swaggerUrl}
            onChange={(e) => setSwaggerUrl(e.target.value)}
            placeholder="E.g., https://api.example.com/swagger.json or /openapi.yaml"
            className="w-full glassmorphism px-3 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 bg-white/10"
            disabled={isLoading}
          />
          <p className="text-xs text-gray-500 mt-1">
            Enter the URL to a Swagger 2.0 or OpenAPI 3.0 specification
          </p>
        </div>
        <button
          type="submit"
          disabled={isLoading || !swaggerUrl.trim()}
          className="w-full px-3 py-2 bg-blue-500/30 hover:bg-blue-500/50 rounded-lg transition-all disabled:opacity-50 font-medium"
        >
          {isLoading ? 'Generating Script...' : 'Generate Automation Script'}
        </button>
      </form>

      {generatedScript && (
        <div className="mt-6 space-y-3">
          <div className="p-4 bg-green-500/10 border border-green-500/30 rounded-lg">
            <div className="text-sm text-green-300 font-semibold mb-2">
              ✓ {generatedScript.filename}
            </div>
            <div className="text-xs text-gray-300 mb-3">
              <div>Status: <span className="text-green-400">{generatedScript.status}</span></div>
              <div className="mt-1 text-gray-400">{generatedScript.message}</div>
            </div>

            <div className="flex gap-2 mt-4">
              <button
                onClick={downloadScript}
                className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-blue-500/30 hover:bg-blue-500/50 rounded-lg transition-all text-sm"
              >
                <Download className="w-4 h-4" />
                Download Script
              </button>
              <button
                onClick={copyScriptToClipboard}
                className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-green-500/30 hover:bg-green-500/50 rounded-lg transition-all text-sm"
              >
                <Copy className="w-4 h-4" />
                Copy to Clipboard
              </button>
            </div>

            <div className="mt-4 p-3 bg-black/20 rounded-lg border border-gray-700/50">
              <p className="text-xs text-gray-300 font-semibold mb-2">Script Preview:</p>
              <div className="text-xs text-gray-400 max-h-32 overflow-y-auto font-mono whitespace-pre-wrap">
                {generatedScript.script.substring(0, 300)}...
              </div>
            </div>

            <button
              onClick={() => {
                setGeneratedScript(null);
                setSwaggerUrl('');
                if (scriptInputRef.current) {
                  scriptInputRef.current.value = '';
                }
              }}
              className="w-full mt-3 px-3 py-1 bg-blue-500/30 hover:bg-blue-500/50 rounded text-xs transition-all"
            >
              Generate Another Script
            </button>
          </div>

          <div className="p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg flex gap-2">
            <AlertCircle className="w-4 h-4 text-blue-300 flex-shrink-0 mt-0.5" />
            <div className="text-xs text-blue-300">
              <p className="font-semibold">Installation:</p>
              <p className="mt-1">pip install requests pytest pytest-cov pyyaml</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
