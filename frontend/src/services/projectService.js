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

export const projectService = {
  async getAllProjects() {
    try {
      console.log('Fetching all projects...');
      const response = await api.get('/api/projects');
      console.log('Projects response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error in getAllProjects:', error);
      throw new Error(error.response?.data?.error || 'Failed to fetch projects');
    }
  },

  async getProject(id) {
    try {
      console.log('Fetching project with ID:', id);
      const response = await api.get(`/api/projects/${id}`);
      console.log('Project response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error in getProject:', error);
      throw new Error(error.response?.data?.error || 'Failed to fetch project');
    }
  },

  async getProjectTasks(proj_ID) {
    try {
      console.log('Fetching tasks for project ID:', proj_ID);
      const response = await api.get(`/api/projects/${proj_ID}/tasks`);
      console.log('Project tasks response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error in getProjectTasks:', error);
      throw new Error(error.response?.data?.error || 'Failed to fetch project tasks');
    }
  },

  async getAllUsers() {
    try {
      console.log('Fetching all users...');
      const response = await api.get('/api/users');
      console.log('Users response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error in getAllUsers:', error);
      throw new Error(error.response?.data?.error || 'Failed to fetch users');
    }
  }
};