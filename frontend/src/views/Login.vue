<template>
  <div class="login-page">
    <div class="login-wrapper">
      <div class="brand">
        <h1 class="brand-title">Task Quest</h1>
        <p class="brand-subtitle">Sign in to manage your tasks efficiently</p>
      </div>

      <div class="card">
        <h2 class="card-title">Welcome back</h2>
        <p class="card-subtitle">Please sign in to continue</p>

        <div class="form-group">
          <label for="email">Email</label>
          <input
            type="email"
            id="email"
            v-model="email"
            placeholder="name@example.com"
            class="form-control"
          />
        </div>

        <div class="form-group">
          <div class="password-header">
            <label for="password">Password</label>
            <router-link to="/reset-password" class="forgot-link">Forgot password?</router-link>
          </div>
          <input
            type="password"
            id="password"
            v-model="password"
            placeholder="••••••••"
            class="form-control"
          />
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <button @click="login" class="btn-primary" :disabled="loading">
          <span v-if="loading">Signing in...</span>
          <span v-else>Sign In</span>
        </button>

        <div class="divider">
          <span>or</span>
        </div>

        <div class="register">
          <span>New here?</span>
          <router-link to="/register" class="link">Create an account</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { authAPI } from '@/services/api'
import authService from '@/services/auth'
import notificationService from '@/services/notificationService'

export default {
  name: 'Login',
  data() {
    return {
      email: '',
      password: '',
      loading: false,
      error: ''
    }
  },
  methods: {
    async testConnection() {
      try {
        console.log('Testing backend connection...');
        const response = await fetch('/api/health');
        const data = await response.json();
        console.log('Backend health check:', data);
        return data;
      } catch (error) {
        console.error('Backend connection failed:', error);
        return null;
      }
    },
    
    async login() {
      if (!this.email || !this.password) {
        this.error = 'Please enter email and password';
        return;
      }

      this.loading = true;
      this.error = '';

      const healthCheck = await this.testConnection();
      if (!healthCheck) {
        console.error('Backend server is not running or not accessible');
        this.error = 'Login failed. Please try again.';
        this.loading = false;
        return;
      }

      try {
        console.log('Attempting login with:', { email: this.email, password: '***' });
        const response = await authAPI.login(this.email, this.password);
        console.log('Login response:', response);
        
        if (response.ok) {
          console.log('Login successful, redirecting to home...');
          // Store user data in auth service
          authService.login(response.user);
          
          // Check for upcoming deadlines in the background
          notificationService.checkUpcomingDeadlines();
          
          this.$router.push('/');
        } else {
          this.error = response.error || 'Login failed';
          console.log('Login failed:', response);
        }
      } catch (error) {
        this.error = error.error || 'An error occurred during login';
        console.error('Login error:', error);
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #eef2ff 0%, #fdf2f8 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
}

.login-wrapper {
  width: 100%;
  max-width: 960px;
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 2rem;
  align-items: center;
}

.brand {
  padding: 1rem 0;
}

.brand-title {
  font-size: 2.25rem;
  line-height: 1.2;
  font-weight: 800;
  color: #111827;
  margin-bottom: 0.5rem;
}

.brand-subtitle {
  color: #6b7280;
}

.card {
  background: #ffffff;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 10px 25px rgba(17, 24, 39, 0.08);
  border: 1px solid #f3f4f6;
}

.card-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
}

.card-subtitle {
  color: #6b7280;
  margin-top: 0.25rem;
  margin-bottom: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 1rem;
}

label {
  font-size: 0.875rem;
  color: #374151;
  margin-bottom: 0.375rem;
}

.form-control {
  appearance: none;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 0.75rem 1rem;
  outline: none;
  background: #fff;
  color: #111827;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-control:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.15);
}

.btn-primary {
  width: 100%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-radius: 10px;
  background: #111827;
  color: #fff;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: transform 0.05s ease-in, background-color 0.2s;
}

.btn-primary:hover {
  background: #1f2937;
}

.btn-primary:active {
  transform: translateY(1px);
}

.btn-primary:disabled {
  background: #9ca3af;
  cursor: not-allowed;
  transform: none;
}

.btn-primary:disabled:hover {
  background: #9ca3af;
}

.error-message {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.divider {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 1.25rem 0;
  color: #9ca3af;
  font-size: 0.875rem;
}

.divider::before,
.divider::after {
  content: '';
  height: 1px;
  background: #e5e7eb;
  flex: 1;
}

.register {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: #6b7280;
}

.link {
  color: #4f46e5;
  font-weight: 600;
}

@media (max-width: 900px) {
  .login-wrapper {
    grid-template-columns: 1fr;
  }
  .brand {
    text-align: center;
  }
}

.password-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.375rem;
}

.forgot-link {
  font-size: 0.875rem;
  color: #4f46e5;
  text-decoration: none;
  font-weight: 500;
}

.forgot-link:hover {
  text-decoration: underline;
}
</style>
