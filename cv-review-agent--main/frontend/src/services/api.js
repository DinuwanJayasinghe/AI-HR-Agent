import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000, // 2 minutes for long operations
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const errorMessage = error.response?.data?.detail || error.message || 'An error occurred';
    console.error('API Error:', errorMessage);
    return Promise.reject(error);
  }
);

// API Services
export const apiService = {
  // Health check
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  // Review CVs from Gmail or Google Drive
  reviewCVs: async (data) => {
    const response = await api.post('/api/review-cvs', {
      job_description: data.jobDescription || '',
      use_drive: data.useDrive || false,
      folder_id: data.folderId || '',
    });
    return response.data;
  },

  // Download CVs by date range
  downloadCVsByDate: async (data) => {
    const response = await api.post('/api/download-cvs-by-date', {
      days_back: data.daysBack || 7,
      job_position: data.jobPosition || '',
      job_description: data.jobDescription || '',
      analyze: data.analyze !== false,
    });
    return response.data;
  },

  // Get all CVs from cv_collection folder
  getCVs: async () => {
    const response = await api.get('/api/cvs');
    return response.data;
  },

  // Get CV analysis results
  getCVAnalysis: async () => {
    const response = await api.get('/api/cv-analysis');
    return response.data;
  },

  // Get dashboard statistics
  getDashboardStats: async () => {
    const response = await api.get('/api/dashboard-stats');
    return response.data;
  },

  // Chat with AI agent
  chat: async (data) => {
    const response = await api.post('/api/chat', {
      message: data.message,
      conversation_history: data.conversationHistory || [],
      session_id: data.sessionId || null,
    });
    return response.data;
  },

  // Chat with streaming
  chatStream: async (data, onMessage, onError) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: data.message,
          conversation_history: data.conversationHistory || [],
          session_id: data.sessionId || null,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const jsonData = JSON.parse(line.slice(6));
              onMessage(jsonData);
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        }
      }
    } catch (error) {
      onError(error);
    }
  },
};

export default api;
