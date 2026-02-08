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
