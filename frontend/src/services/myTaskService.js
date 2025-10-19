import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const ownTasksService = {
  async getTasks(userId = null, options = {}) {
    try {
      const params = {};

      if (userId) {
        params.userId = userId;
      }

      const statusesInput = options.statuses ?? options.status;
      if (statusesInput) {
        let statusParam;
        if (Array.isArray(statusesInput)) {
          statusParam = statusesInput.map(status => status?.toString().trim()).filter(Boolean).join(',');
        } else {
          statusParam = statusesInput.toString().trim();
        }

        if (statusParam) {
          params.status = statusParam;
        }
      }

      const response = await api.get('/api/tasks', { params });
      console.log("enter mytaskservice", params);
      return response.data;
    } catch (error) {
      console.error("Error in getTasks:", error);
      throw new Error(error.response?.data?.error || "Failed to fetch tasks");
    }
  }
};
