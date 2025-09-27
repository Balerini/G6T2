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
      console.log("enter mytaskservice", url);
      return response.data;
    } catch (error) {
      console.error("Error in getTasks:", error);
      throw new Error(error.response?.data?.error || "Failed to fetch tasks");
    }
  }
};