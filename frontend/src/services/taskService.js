// frontend/src/services/taskService.js
import axios from 'axios';
import notificationService from './notificationService';
import taskEventService from './taskEventService';

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
      // Trigger notification refresh after task creation
      notificationService.triggerRefresh();
      taskEventService.triggerTaskCreated(response.data);
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
      const userString = sessionStorage.getItem('user') || '{}';
      let userData = {};
      try {
        userData = JSON.parse(userString);
      } catch (parseError) {
        userData = {};
      }

      const response = await api.put(
        `/api/tasks/${id}`,
        taskData,
        {
          headers: {
            'X-User-Id': userData.id || userData.user_ID || userData.uid || '',
            'X-User-Role': userData.role_num || userData.rank || 4,
            'X-User-Name': userData.name || userData.email || ''
          }
        }
      );
      // Trigger notification refresh after task update
      notificationService.triggerRefresh();
      taskEventService.triggerTasksRefresh(response.data);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to update task');
    }
  },

  async deleteTask(taskId) {
      try {
          const userString = sessionStorage.getItem('user');
          const userData = JSON.parse(userString);
          
          const response = await api.put(`/api/tasks/${taskId}/delete`, {
              userId: userData.id  // Send user ID for backend validation
          });
          return response.data;
      } catch (error) {
          console.error('Delete task error:', error);
          throw new Error(error.response?.data?.error || 'Failed to delete task');
      }
  },
  
  async getDeletedTasks(userId) {
      try {
          const response = await api.get(`/api/tasks/deleted?userId=${userId}`);
          return response.data;
      } catch (error) {
          console.error('Get deleted tasks error:', error);
          throw new Error(error.response?.data?.error || 'Failed to get deleted tasks');
      }
  },

  async getDeletedSubtasks(userId) {
    try {
        const response = await api.get(`/api/subtasks/deleted-new?userId=${userId}`);
        return response.data;
    } catch (error) {
        console.error('Get deleted subtasks error:', error);
        throw new Error(error.response?.data?.error || 'Failed to get deleted subtasks');
    }
},

async restoreSubtask(subtaskId) {
    try {
        const response = await api.put(`/api/subtasks/${subtaskId}/restore-new`);
        return response.data;
    } catch (error) {
        console.error('Restore subtask error:', error);
        throw new Error(error.response?.data?.error || 'Failed to restore subtask');
    }
},

async permanentlyDeleteSubtask(subtaskId) {
    try {
        const response = await api.delete(`/api/subtasks/${subtaskId}/permanent-new`);
        return response.data;
    } catch (error) {
        console.error('Permanent delete subtask error:', error);
        throw new Error(error.response?.data?.error || 'Failed to permanently delete subtask');
    }
},

  async restoreTask(taskId) {
      try {
          const response = await api.put(`/api/tasks/${taskId}/restore`);
          return response.data;
      } catch (error) {
          console.error('Restore task error:', error);
          throw new Error(error.response?.data?.error || 'Failed to restore task');
      }
  },

  async permanentlyDeleteTask(taskId) {
      try {
          const response = await api.delete(`/api/tasks/${taskId}/permanent`);
          return response.data;
      } catch (error) {
          console.error('Permanent delete task error:', error);
          throw new Error(error.response?.data?.error || 'Failed to permanently delete task');
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

  async getProjects(userId, divisionName) {
    try {
      if (userId && divisionName) {
        // Use filtered API to get only projects where user is a collaborator
        const response = await api.get(`/api/projects/filtered/${encodeURIComponent(divisionName)}?user_id=${encodeURIComponent(userId)}`);
        return response.data;
      } else {
        // Fallback to all projects if no user info
        const response = await api.get('/api/projects');
        return response.data;
      }
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch projects');
    }
  },

  async createSubtask(subtaskData) {
    if (!subtaskData || typeof subtaskData !== 'object') {
        throw new Error('Invalid subtask data');
    }
    if (!subtaskData.name || !subtaskData.parent_task_id) {
        throw new Error('Subtask name and parent task ID are required');
    }
    
    try {
      const response = await api.post('/api/subtasks', subtaskData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to create subtask');
    }
  },

  async getSubtasksByTask(taskId) {
    try {
        const response = await api.get(`/api/tasks/${taskId}/subtasks`);
        return response.data;
    } catch (error) {
        console.error('Get subtasks by task error:', error);
        throw new Error(error.response?.data?.error || 'Failed to fetch subtasks');
    }
},

  async updateSubtask(subtaskId, subtaskData) {
    try {
      // Get current user info from session storage
      const currentUser = JSON.parse(sessionStorage.getItem('user') || '{}');

      // Include user authentication headers 
      const response = await api.put(`/api/subtasks/${subtaskId}`, subtaskData, {
        headers: {
          'X-User-Id': currentUser.id,
          'X-User-Role': currentUser.role_num || currentUser.rank || 4
        }
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to update subtask');
    }
  },

  async deleteSubtask(subtaskId) {
    try {
      const userString = sessionStorage.getItem('user');
      const userData = JSON.parse(userString);
      const userId = userData.id;
      
      const response = await api.put(`/api/subtasks/${subtaskId}/delete`, {
        userId: userId
      });
      return response.data;
    } catch (error) {
      console.error('Delete subtask error:', error);
      throw new Error(error.response?.data?.error || 'Failed to delete subtask');
    }
  },
  
  async getTeamSubtasks(managerId) {
    try {
      const response = await api.get(`/api/subtasks/team/${managerId}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to fetch team subtasks');
    }
  },
};

  
