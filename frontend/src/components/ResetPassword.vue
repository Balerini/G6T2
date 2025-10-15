<template>
  <div class="reset-password-page">
    <div class="reset-password-wrapper">
      <div class="brand">
        <h1 class="brand-title">Task Quest</h1>
        <p class="brand-subtitle">Create your new password</p>
      </div>

      <div class="card">
        <h2 class="card-title">Reset Password</h2>
        <p class="card-subtitle">Enter your new password below</p>

        <div v-if="!resetSuccess">
          <div class="form-group">
            <label for="password">New Password</label>
            <input
              type="password"
              id="password"
              v-model="password"
              placeholder="••••••••"
              class="form-control"
              @input="validatePassword"
            />
          </div>

          <div class="form-group">
            <label for="confirmPassword">Confirm New Password</label>
            <input
              type="password"
              id="confirmPassword"
              v-model="confirmPassword"
              placeholder="••••••••"
              class="form-control"
              @input="validateConfirmPassword"
            />
          </div>

          <!-- Password Requirements -->
          <div class="password-requirements">
            <p class="requirements-title">Password must contain:</p>
            <ul class="requirements-list">
              <li :class="{ valid: validations.length }">
                <span class="icon">{{ validations.length ? '✓' : '○' }}</span>
                8-12 characters
              </li>
              <li :class="{ valid: validations.hasUpperCase }">
                <span class="icon">{{ validations.hasUpperCase ? '✓' : '○' }}</span>
                At least one uppercase letter
              </li>
              <li :class="{ valid: validations.hasLowerCase }">
                <span class="icon">{{ validations.hasLowerCase ? '✓' : '○' }}</span>
                At least one lowercase letter
              </li>
              <li :class="{ valid: validations.hasNumber }">
                <span class="icon">{{ validations.hasNumber ? '✓' : '○' }}</span>
                At least one number
              </li>
              <li :class="{ valid: validations.hasSpecialChar }">
                <span class="icon">{{ validations.hasSpecialChar ? '✓' : '○' }}</span>
                At least one special character
              </li>
              <li v-if="confirmPassword" :class="{ valid: validations.passwordsMatch }">
                <span class="icon">{{ validations.passwordsMatch ? '✓' : '○' }}</span>
                Passwords match
              </li>
            </ul>
          </div>

          <div v-if="error" class="error-message">
            {{ error }}
          </div>

          <button 
            @click="resetPassword" 
            class="btn-primary" 
            :disabled="loading || !isPasswordValid"
          >
            <span v-if="loading">Resetting...</span>
            <span v-else>Reset Password</span>
          </button>
        </div>

        <div v-else class="success-message">
          <svg class="success-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <h3>Password Reset Successful!</h3>
          <p>Your password has been successfully reset.</p>
          <button @click="goToLogin" class="btn-primary">Go to Sign In</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { authAPI } from '@/services/api'

export default {
  name: 'ResetPassword',
  data() {
    return {
      password: '',
      confirmPassword: '',
      loading: false,
      error: '',
      resetSuccess: false,
      token: '',
      validations: {
        length: false,
        hasUpperCase: false,
        hasLowerCase: false,
        hasNumber: false,
        hasSpecialChar: false,
        passwordsMatch: false
      }
    }
  },
  computed: {
    isPasswordValid() {
      return (
        this.validations.length &&
        this.validations.hasUpperCase &&
        this.validations.hasLowerCase &&
        this.validations.hasNumber &&
        this.validations.hasSpecialChar &&
        this.validations.passwordsMatch
      );
    }
  },
  created() {
    // Get token from URL query parameters
    this.token = this.$route.query.token;
    
    if (!this.token) {
      this.error = 'Invalid or missing reset token. Please request a new password reset link.';
    }
  },
  methods: {
    validatePassword() {
      const password = this.password;
      
      // Length check (8-12 characters)
      this.validations.length = password.length >= 8 && password.length <= 12;
      
      // Uppercase letter check
      this.validations.hasUpperCase = /[A-Z]/.test(password);
      
      // Lowercase letter check
      this.validations.hasLowerCase = /[a-z]/.test(password);
      
      // Number check
      this.validations.hasNumber = /\d/.test(password);
      
      // Special character check
      this.validations.hasSpecialChar = /[^a-zA-Z0-9]/.test(password);
      
      // Check if passwords match
      this.validateConfirmPassword();
    },
    
    validateConfirmPassword() {
      this.validations.passwordsMatch = 
        this.password === this.confirmPassword && 
        this.confirmPassword.length > 0;
    },
    
    async resetPassword() {
      if (!this.token) {
        this.error = 'Invalid reset token. Please request a new password reset link.';
        return;
      }

      if (!this.isPasswordValid) {
        this.error = 'Please ensure your password meets all requirements';
        return;
      }

      this.loading = true;
      this.error = '';

      try {
        const response = await authAPI.resetPassword(this.token, this.password);
        
        if (response.ok) {
          this.resetSuccess = true;
        } else {
          this.error = response.error || 'Failed to reset password. The link may have expired.';
        }
      } catch (error) {
        this.error = error.error || 'An error occurred. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    
    goToLogin() {
      this.$router.push('/login');
    }
  }
}
</script>

<style scoped>
.reset-password-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #eef2ff 0%, #fdf2f8 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
}

.reset-password-wrapper {
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

.password-requirements {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.requirements-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.5rem;
}

.requirements-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.requirements-list li {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #6b7280;
  padding: 0.25rem 0;
  transition: color 0.2s;
}

.requirements-list li.valid {
  color: #10b981;
  font-weight: 500;
}

.requirements-list .icon {
  font-weight: 600;
  font-size: 1rem;
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
  margin-bottom: 1.5rem;
}

@media (max-width: 900px) {
  .reset-password-wrapper {
    grid-template-columns: 1fr;
  }
  .brand {
    text-align: center;
  }
}
</style>