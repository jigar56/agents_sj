import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const launchAPI = {
  // Get all launches
  getLaunches: async () => {
    const response = await api.get('/api/launches/');
    return response.data;
  },

  // Get a specific launch
  getLaunch: async (id) => {
    const response = await api.get(`/api/launches/${id}`);
    return response.data;
  },

  // Create a new launch
  createLaunch: async (launchData) => {
    const response = await api.post('/api/launches/', launchData);
    return response.data;
  },

  // Start workflow for a launch
  startWorkflow: async (id) => {
    const response = await api.post(`/api/orchestrator/start/${id}`);
    return response.data;
  },

  // Get workflow status
  getWorkflowStatus: async (id) => {
    const response = await api.get(`/api/orchestrator/status/${id}`);
    return response.data;
  },

  // Update launch status
  updateLaunchStatus: async (id, status, summary = null) => {
    const response = await api.put(`/api/launches/${id}/status`, {
      status,
      summary,
    });
    return response.data;
  },

  // Delete a launch
  deleteLaunch: async (id) => {
    const response = await api.delete(`/api/launches/${id}`);
    return response.data;
  },
};

export default api;
