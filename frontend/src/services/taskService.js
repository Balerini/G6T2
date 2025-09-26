// frontend/src/services/taskService.js
import axios from 'axios';

const API_BASE_URL = process.env.VUE_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add this comment at the top to tell ESLint that process is a global
/* global process */

export const taskService = {
  async createTask(taskData) {
    try {
      const response = await api.post('/api/tasks', taskData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to create task');
    }
  },

  async getTasks() {
    try {
      const response = await api.get('/api/tasks');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch tasks');
    }
  },

  async getTask(id) {
    try {
      const response = await api.get(`/api/tasks/${id}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch task');
    }
  },

  async getTaskById(id) {
    try {
      const response = await api.get(`/api/tasks/${id}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch task');
    }
  },

  async getProjectById(id) {
    try {
      const response = await api.get(`/api/projects/${id}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch project');
    }
  },

  async updateTask(id, taskData) {
    try {
      // id can be Firestore doc id or business task_ID; backend resolves both
      const response = await api.put(`/api/tasks/${id}`, taskData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to update task');
    }
  },

  async deleteTask(id) {
    try {
      const response = await api.delete(`/api/tasks/${id}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to delete task');
    }
  },

  async getTasksByProject(projId) {
    try {
      const response = await api.get(`/api/projects/${projId}/tasks`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch project tasks');
    }
  },
  
  async getUsers() {
    try {
      const response = await api.get('/api/users');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch users');
    }
  },

  async getProjects() {
    try {
      const response = await api.get('/api/projects');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch projects');
    }
  },
};
