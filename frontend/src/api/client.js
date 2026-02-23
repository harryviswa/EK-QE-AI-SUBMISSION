import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Note: user session headers were removed per UI requirements

export const apiClient = {
  // Health & Info
  getHealth: () => api.get('/health'),
  getInfo: () => api.get('/info'),

  // Documents
  uploadDocument: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  addUrl: (url) => api.post('/documents/add-url', { url }),
  listDocuments: () => api.get('/documents/list'),
  validateTestcases: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/validate/testcases', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 300000, // 5 minute timeout for validation
    });
  },
  validateTestcasesDeep: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/validate/testcases', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 300000, // 5 minute timeout for deep validation
    });
  },

  // API Automation
  generateFromSwagger: (swaggerUrl) =>
    api.post('/automation/generate-from-swagger', { swagger_url: swaggerUrl }, {
      timeout: 60000, // 60 second timeout for script generation
    }),

  // Query & RAG
  search: (query, topK = 5) =>
    api.post('/query/search', { query, top_k: topK }),
  ragQuery: (query, type = 'qa', topK = 5, useReranking = true) =>
    api.post('/query/rag', {
      query,
      type,
      top_k: topK,
      use_reranking: useReranking,
    }),
  ragQueryStream: async (query, type = null, topK = 5, useReranking = true, handlers = {}) => {
    const { onMeta, onToken, onDone, onError, signal } = handlers;
    const response = await fetch(`${API_BASE_URL}/query/rag/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query,
        type,
        top_k: topK,
        use_reranking: useReranking,
      }),
      signal,
    });

    if (!response.ok || !response.body) {
      const errorText = await response.text().catch(() => '');
      throw new Error(errorText || `Streaming request failed (${response.status})`);
    }

    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('text/event-stream')) {
      const errorText = await response.text().catch(() => '');
      throw new Error(errorText || 'Expected SSE stream but received non-stream response');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    const handleEvent = (eventName, data) => {
      let payload = data;
      try {
        payload = JSON.parse(data);
      } catch {
        payload = data;
      }

      if (eventName === 'meta' && onMeta) onMeta(payload);
      if (eventName === 'token' && onToken) onToken(payload?.token ?? payload);
      if (eventName === 'done' && onDone) onDone(payload);
      if (eventName === 'error' && onError) onError(payload);
    };

    const parseBuffer = () => {
      const parts = buffer.split('\n\n');
      buffer = parts.pop() || '';

      parts.forEach((part) => {
        const lines = part.split('\n');
        let eventName = 'message';
        const dataLines = [];

        lines.forEach((line) => {
          if (line.startsWith('event:')) {
            eventName = line.slice(6).trim();
          } else if (line.startsWith('data:')) {
            dataLines.push(line.slice(5).trimStart());
          }
        });

        if (dataLines.length > 0) {
          handleEvent(eventName, dataLines.join('\n'));
        }
      });
    };

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      buffer = buffer.replace(/\r\n/g, '\n');
      parseBuffer();
    }

    if (buffer.trim()) {
      buffer = buffer.replace(/\r\n/g, '\n');
      parseBuffer();
    }
  },

  // Automation Logs
  analyzeLogFolder: (folderPath, generateInsights = true) =>
    api.post('/logs/analyze-folder', { 
      folder_path: folderPath,
      generate_insights: generateInsights
    }, {
      timeout: 120000, // 2 minute timeout for analysis
    }),
  uploadLogFiles: (files) => {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    return api.post('/logs/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 120000, // 2 minute timeout for upload and analysis
    });
  },
  getLogsSummary: () =>
    api.get('/logs/summary'),

  // Export
  exportPdf: (content, title = 'NexQA Report') =>
    api.post(
      '/export/pdf',
      { content, title },
      { responseType: 'blob' }
    ),
  exportExcel: (data) =>
    api.post('/export/excel', { data }, { responseType: 'blob' }),
  downloadFile: (filename, content, type = 'text/plain') => {
    const element = document.createElement('a');
    element.setAttribute('href', `data:${type};charset=utf-8,${encodeURIComponent(content)}`);
    element.setAttribute('download', filename);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  },
};

export default api;
