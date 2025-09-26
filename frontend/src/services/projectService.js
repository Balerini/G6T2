import axios from 'axios';
import { projectAPI, userAPI } from './api.js';

const API_BASE_URL = process.env.VUE_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/* global process */

export const projectService = {
  getAllProjectsWithTasks: (divisionName, userId) => projectAPI.getFilteredProjectsByDivision(divisionName, userId),
  getAllUsers: (divisionName) => userAPI.getFilteredUsersByDivision(divisionName),

  // ============== Get all projects ==============
  async getAllProjects() {
    try {
      const response = await api.get('/api/projects');
      // console.log('Projects response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error in getAllProjects:', error);
      throw new Error(error.response?.data?.error || 'Failed to fetch projects');
    }
  },

  // ============== Get single project (with tasks included) ==============
  async getProject(projectId) {
    try {
      const response = await api.get(`/api/projects/${projectId}`);
      console.log('Project response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error in getProject:', error);
      throw new Error(error.response?.data?.error || 'Failed to fetch project');
    }
  },

  // // ============== Get all projects  ==============
  // async getAllProjectsWithTasks() {
  //   try {
  //     const response = await api.get('/api/projects');
  //     console.log('Projects with tasks response:', response.data);
  //     return response.data;
  //   } catch (error) {
  //     console.error('Error in getAllProjectsWithTasks:', error);
  //     throw new Error(error.response?.data?.error || 'Failed to fetch projects with tasks');
  //   }
  // },

  // ============== Get project with tasks (basically projects page) ==============
  async getProjectWithTasks(projectId) {
    try {
      const response = await api.get(`/api/projects/${projectId}/tasks`);
      console.log('Project with tasks response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error in getProjectWithTasks:', error);
      throw new Error(error.response?.data?.error || 'Failed to fetch project with tasks');
    }
  },

  // ============== Get specific task from project via id ==============
  async getProjectTask(projectId, taskId) {
    try {
      console.log('Fetching task:', taskId, 'from project:', projectId);
      const response = await api.get(`/api/projects/${projectId}/tasks/${taskId}`);
      console.log('Project task response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error in getProjectTask:', error);
      throw new Error(error.response?.data?.error || 'Failed to fetch project task');
    }
  },

  // ============== Get all users for projects collaborators, created by, assigned to ==============
  // async getAllUsers() {
  //   try { 
  //     const response = await api.get('/api/users');
  //     // console.log('Users response:', response.data);
  //     return response.data;
  //   } catch (error) {
  //     console.error('Error in getAllUsers:', error);
  //     throw new Error(error.response?.data?.error || 'Failed to fetch users');
  //   }
  // },

  async getAllUsersUnfiltered() {
    try {
      const response = await api.get('/api/users');
      return response.data;
    } catch (error) {
      console.error('Error in getAllUsersUnfiltered:', error);
      throw new Error(error.response?.data?.error || 'Failed to fetch users');
    }
  }
};