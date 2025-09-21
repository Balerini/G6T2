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

  // Logout user
  logout: () => {
    localStorage.removeItem('user')
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
