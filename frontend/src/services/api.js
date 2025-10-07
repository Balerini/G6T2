import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000', 
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// API methods
export const authAPI = {
  // Login user
  login: async (email, password) => {
    try {
      const response = await api.post('/login', {
        email,
        password
      })
      console.log('API response:', response);
      return response.data
    } catch (error) {
      console.error('API error:', error);
      throw error.response?.data || { error: 'Login failed' }
    }
  },

  // Register user
  register: async (userData) => {
    try {
      const response = await api.post('/register', userData)
      console.log('API response:', response);
      return response.data
    } catch (error) {
      console.error('API error:', error);
      throw error.response?.data || { error: 'Registration failed' }
    }
  },

  // Logout user
  logout: () => {
    localStorage.removeItem('user')
    sessionStorage.removeItem('user')
    sessionStorage.removeItem('isLoggedIn')
  },

  // Get current user from localStorage
  getCurrentUser: () => {
    const user = localStorage.getItem('user')
    return user ? JSON.parse(user) : null
  },

  // Check if user is logged in
  isLoggedIn: () => {
    return !!localStorage.getItem('user')
  }
}

// Project API with department filtering
export const projectAPI = {
  // Get all projects (unfiltered - for admin use)
  getAllProjects: async () => {
    try {
      const response = await api.get('/api/projects')
      return response.data
    } catch (error) {
      throw error.response?.data || { error: 'Failed to fetch projects' }
    }
  },

  // Get projects filtered by division
  getFilteredProjectsByDivision: async (divisionName, userId) => {
    try {
      const response = await api.get(`/api/projects/filtered/${encodeURIComponent(divisionName)}?user_id=${encodeURIComponent(userId)}`)
      console.log('Filtered projects response:', response.data);
      return response.data
    } catch (error) {
      console.error('Error fetching filtered projects:', error);
      throw error.response?.data || { error: 'Failed to fetch filtered projects' }
    }
  },

  // Get single project
  getProject: async (projectId) => {
    try {
      const response = await api.get(`/api/projects/${projectId}`)
      return response.data
    } catch (error) {
      throw error.response?.data || { error: 'Failed to fetch project' }
    }
  },

  // Get project with tasks
  getProjectWithTasks: async (projectId) => {
    try {
      const response = await api.get(`/api/projects/${projectId}/tasks`)
      return response.data
    } catch (error) {
      throw error.response?.data || { error: 'Failed to fetch project with tasks' }
    }
  },

  // Get specific task from project
  getProjectTask: async (projectId, taskId) => {
    try {
      const response = await api.get(`/api/projects/${projectId}/tasks/${taskId}`)
      return response.data
    } catch (error) {
      throw error.response?.data || { error: 'Failed to fetch project task' }
    }
  },

  createProject: async (projectData) => {
    try {
      const response = await api.post('/api/projects', projectData)
      console.log('Project created successfully:', response.data)
      return response.data
    } catch (error) {
      console.error('Error creating project:', error)
      throw error.response?.data || { error: 'Failed to create project' }
    }
  },

  // Update existing project
  updateProject: async (projectId, projectData) => {
    try {
      const response = await api.put(`/api/projects/${projectId}`, projectData)
      console.log('Project updated successfully:', response.data)
      return response.data
    } catch (error) {
      console.error('Error updating project:', error)
      throw error.response?.data || { error: 'Failed to update project' }
    }
  },

  // Delete project
  deleteProject: async (projectId) => {
    try {
      const response = await api.delete(`/api/projects/${projectId}`)
      console.log('Project deleted successfully:', response.data)
      return response.data
    } catch (error) {
      console.error('Error deleting project:', error)
      throw error.response?.data || { error: 'Failed to delete project' }
    }
  }
}

// User API with department filtering
export const userAPI = {
  // Get all users (unfiltered - for admin use)
  getAllUsers: async () => {
    try {
      const response = await api.get('/api/users')
      return response.data
    } catch (error) {
      throw error.response?.data || { error: 'Failed to fetch users' }
    }
  },

  // Get users filtered by division
  getFilteredUsersByDivision: async (divisionName) => {
    try {
      const response = await api.get(`/api/users/filtered/${encodeURIComponent(divisionName)}`)
      console.log('Filtered users response:', response.data);
      return response.data
    } catch (error) {
      console.error('Error fetching filtered users:', error);
      throw error.response?.data || { error: 'Failed to fetch filtered users' }
    }
  }
}

// Health check
export const healthAPI = {
  check: async () => {
    try {
      const response = await api.get('/health')
      return response.data
    } catch (error) {
      throw error.response?.data || { error: 'Health check failed' }
    }
  }
}

export default api