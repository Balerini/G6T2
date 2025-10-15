<template>
  <div class="forgot-password-page">
    <div class="forgot-password-wrapper">
      <div class="brand">
        <h1 class="brand-title">Task Quest</h1>
        <p class="brand-subtitle">Reset your password</p>
      </div>

      <div class="card">
        <h2 class="card-title">Forgot Password?</h2>
        <p class="card-subtitle">Enter your email address and we'll send you a password reset link</p>

        <div v-if="!emailSent">
          <div class="form-group">
            <label for="email">Email</label>
            <input
              type="email"
              id="email"
              v-model="email"
              placeholder="name@example.com"
              class="form-control"
              @keyup.enter="sendResetLink"
            />
          </div>

          <div v-if="error" class="error-message">
            {{ error }}
          </div>

          <button @click="sendResetLink" class="btn-primary" :disabled="loading">
            <span v-if="loading">Sending...</span>
            <span v-else>Send Reset Link</span>
          </button>
        </div>

        <div v-else class="success-message">
          <svg class="success-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <h3>Check your email</h3>
          <p>We've sent a password reset link to <strong>{{ email }}</strong></p>
          <p class="small-text">The link will expire in 1 hour.</p>
        </div>

        <div class="divider">
          <span>or</span>
        </div>

        <div class="back-to-login">
          <router-link to="/login" class="link">← Back to Sign In</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { authAPI } from '@/services/api'

export default {
  name: 'ForgotPassword',
  data() {
    return {
      email: '',
      loading: false,
      error: '',
      emailSent: false
    }
  },
  methods: {
    async sendResetLink() {
      if (!this.email) {
        this.error = 'Please enter your email address';
        return;
      }

      // Basic email validation
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(this.email)) {
        this.error = 'Please enter a valid email address';
        return;
      }

      this.loading = true;
      this.error = '';

      try {
        const response = await authAPI.forgotPassword(this.email);
        
        if (response.ok) {
          this.emailSent = true;
        } else {
          this.error = response.error || 'Failed to send reset link. Please try again.';
        }
      } catch (error) {
        this.error = error.error || 'An error occurred. Please try again.';
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>

<style scoped>
.forgot-password-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #eef2ff 0%, #fdf2f8 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
}

.forgot-password-wrapper {
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

.error-message {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.success-message {
  text-align: center;
  padding: 1.5rem 0;
}

.success-icon {
  width: 64px;
  height: 64px;
  color: #10b981;
  margin: 0 auto 1rem;
}

.success-message h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 0.5rem;
}

.success-message p {
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.small-text {
  font-size: 0.875rem;
  color: #9ca3af;
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

.back-to-login {
  display: flex;
  justify-content: center;
}

.link {
  color: #4f46e5;
  font-weight: 600;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

@media (max-width: 900px) {
  .forgot-password-wrapper {
    grid-template-columns: 1fr;
  }
  .brand {
    text-align: center;
  }
}
</style>