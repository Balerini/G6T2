import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const ownTasksService = {
  async getTasks(userId = null) {
    try {
      const url = userId ? `/api/tasks?userId=${userId}` : `/api/tasks`;
      const response = await api.get(url);
      // console.log("enter mytaskservice", url);
      return response.data;
    } catch (error) {
      console.error("Error in getTasks:", error);
      throw new Error(error.response?.data?.error || "Failed to fetch tasks");
    }
  }

  // async getProjectTasks(proj_ID) {
  //   try {
  //     console.log('Fetching tasks for project ID:', proj_ID);
  //     const response = await api.get(`/api/projects/${proj_ID}/tasks`);
  //     // console.log('Project tasks response:', response.data);
  //     return response.data;
  //   } catch (error) {
  //     console.error('Error in getProjectTasks:', error);
  //     throw new Error(error.response?.data?.error || 'Failed to fetch project tasks');
  //   }
  // },

  // async getAllUsers() {
  //   try {
  //     // console.log('Fetching all users...');
  //     const response = await api.get('/api/users');
  //     // console.log('Users response:', response.data);
  //     return response.data;
  //   } catch (error) {
  //     console.error('Error in getAllUsers:', error);
  //     throw new Error(error.response?.data?.error || 'Failed to fetch users');
  //   }
  // }
};