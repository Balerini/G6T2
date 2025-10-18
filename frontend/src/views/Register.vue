<template>
  <div class="register-page">
    <div class="register-wrapper">
      <div class="brand">
        <h1 class="brand-title">Task Quest</h1>
        <p class="brand-subtitle">Join us and start managing your tasks efficiently</p>
      </div>

      <div class="card">
        <h2 class="card-title">Create your account</h2>
        <p class="card-subtitle">Please fill in your details to get started</p>

        <form @submit.prevent="register">
          <div class="form-row">
            <div class="form-group">
              <label for="name">Full Name</label>
              <input
                type="text"
                id="name"
                v-model="form.name"
                placeholder="John Doe"
                class="form-input"
                :class="{ 'error': errors.name }"
                @input="clearError('name')"
                @blur="validateField('name')"
              />
              <span class="error-message" :class="{ 'visible': errors.name }">{{ errors.name }}</span>
            </div>

            <div class="form-group">
              <label for="email">Email</label>
              <input
                type="email"
                id="email"
                v-model="form.email"
                placeholder="name@example.com"
                class="form-input"
                :class="{ 'error': errors.email }"
                @input="clearError('email')"
                @blur="validateField('email')"
              />
              <span class="error-message" :class="{ 'visible': errors.email }">{{ errors.email }}</span>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="password">Password</label>
              <input
                type="password"
                id="password"
                v-model="form.password"
                placeholder="••••••••"
                class="form-input"
                :class="{ 'error': errors.password }"
                @input="clearError('password')"
                @blur="validateField('password')"
              />
              <span class="error-message" :class="{ 'visible': errors.password }">{{ errors.password }}</span>
            </div>

            <div class="form-group">
              <label for="confirmPassword">Confirm Password</label>
              <input
                type="password"
                id="confirmPassword"
                v-model="form.confirmPassword"
                placeholder="••••••••"
                class="form-input"
                :class="{ 'error': errors.confirmPassword }"
                @input="clearError('confirmPassword')"
                @blur="validateField('confirmPassword')"
              />
              <span class="error-message" :class="{ 'visible': errors.confirmPassword }">{{ errors.confirmPassword }}</span>
            </div>
          </div>

          <div class="form-group">
            <label for="division">Department</label>
            <select
              id="division"
              v-model="form.division"
              class="form-select"
              :class="{ 'error': errors.division }"
              @change="clearError('division')"
            >
              <option value="">Select your department</option>
              <option value="Sales">Sales</option>
              <option value="Consultancy">Consultancy</option>
              <option value="System Solutioning">System Solutioning</option>
              <option value="Engineering Operation">Engineering Operation</option>
              <option value="HR and Admin">HR and Admin</option>
              <option value="Finance">Finance</option>
              <option value="IT">IT</option>
            </select>
            <span class="error-message" :class="{ 'visible': errors.division }">{{ errors.division }}</span>
          </div>

          <div class="error-message" :class="{ 'visible': error }">
            {{ error }}
          </div>
          
          <div class="success-message" :class="{ 'visible': successMessage }">
            {{ successMessage }}
          </div>

          <button type="submit" class="btn-primary" :disabled="loading">
            <span v-if="loading">Creating account...</span>
            <span v-else>Create Account</span>
          </button>

          <div class="divider">
            <span>or</span>
          </div>

          <div class="register">
            <span>Already have an account?</span>
            <router-link to="/login" class="link">Sign in</router-link>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { authAPI } from '@/services/api'
import authService from '@/services/auth'

export default {
  name: 'Register',
  data() {
    return {
      form: {
        name: '',
        email: '',
        password: '',
        confirmPassword: '',
        division: ''
      },
      errors: {},
      loading: false,
      error: '',
      successMessage: ''
    }
  },
  methods: {
    clearError(field) {
      if (this.errors[field]) {
        this.errors = { ...this.errors, [field]: '' }
      }
      if (this.error) {
        this.error = ''
      }
      if (this.successMessage) {
        this.successMessage = ''
      }
    },


    validateField(field) {
      this.errors = { ...this.errors, [field]: '' }

      switch (field) {
        case 'name':
          if (!this.form.name.trim()) {
            this.errors.name = 'Name is required'
          } else if (this.form.name.trim().length < 2) {
            this.errors.name = 'Name must be at least 2 characters'
          }
          break

        case 'email':
          if (!this.form.email) {
            this.errors.email = 'Email is required'
          } else if (!this.isValidEmail(this.form.email)) {
            this.errors.email = 'Please enter a valid email address'
          }
          break

        case 'password':
          if (!this.form.password) {
            this.errors.password = 'Password is required'
          } else {
            const passwordErrors = this.validatePassword(this.form.password)
            if (passwordErrors) {
              this.errors.password = passwordErrors
            }
          }
          break

        case 'confirmPassword':
          if (!this.form.confirmPassword) {
            this.errors.confirmPassword = 'Please confirm your password'
          } else if (this.form.password !== this.form.confirmPassword) {
            this.errors.confirmPassword = 'Passwords do not match'
          }
          break


        case 'division':
          if (!this.form.division) {
            this.errors.division = 'Department is required'
          }
          break
      }
    },

    isValidEmail(email) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return emailRegex.test(email)
    },

    validatePassword(password) {
      if (password.length < 8) {
        return 'Password must be at least 8 characters long'
      }
      
      if (password.length > 128) {
        return 'Password must be less than 128 characters'
      }
      
      // Check for at least one uppercase letter
      if (!/[A-Z]/.test(password)) {
        return 'Password must contain at least one uppercase letter'
      }
      
      // Check for at least one lowercase letter
      if (!/[a-z]/.test(password)) {
        return 'Password must contain at least one lowercase letter'
      }
      
      // Check for at least one digit
      if (!/\d/.test(password)) {
        return 'Password must contain at least one number'
      }
      
      // Check for at least one special character
      if (!/[!@#$%^&*()_+\-=[\]{}|;:,.<>?]/.test(password)) {
        return 'Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)'
      }
      
      return null
    },

    validateForm() {
      const fields = ['name', 'email', 'password', 'confirmPassword', 'division']
      let isValid = true

      fields.forEach(field => {
        this.validateField(field)
        if (this.errors[field]) {
          isValid = false
        }
      })

      return isValid
    },

    async register() {
      if (!this.validateForm()) {
        return
      }

      this.loading = true
      this.error = ''

      try {
        const response = await authAPI.register({
          name: this.form.name.trim(),
          email: this.form.email.toLowerCase().trim(),
          password: this.form.password,
          division_name: this.form.division.trim()
        })

        if (response.ok) {
          // Registration successful - redirect to login for security
          console.log('Registration successful:', response)
          
          // Show success message and redirect to login
          this.successMessage = 'Registration successful! Please log in with your credentials.'
          
          // Clear form
          this.form = {
            name: '',
            email: '',
            password: '',
            confirmPassword: '',
            division: ''
          }
          
          // Redirect to login after a short delay
          setTimeout(() => {
            this.$router.push('/login')
          }, 2000)
        } else {
          this.error = response.error || 'Registration failed'
        }
      } catch (error) {
        this.error = error.error || 'An error occurred during registration'
        console.error('Registration error:', error)
      } finally {
        this.loading = false
      }
    }
  },

  mounted() {
    // Check if user came from login page with registered=true
    if (this.$route.query.registered === 'true') {
      this.$router.replace('/login')
    }
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #eef2ff 0%, #fdf2f8 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
}

.register-wrapper {
  width: 100%;
  max-width: 1200px;
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 3rem;
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
  padding: 2.5rem;
  box-shadow: 0 10px 25px rgba(17, 24, 39, 0.08);
  border: 1px solid #f3f4f6;
  min-width: 480px;
}

.card-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 0.25rem;
}

.card-subtitle {
  color: #6b7280;
  margin-bottom: 1.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
  margin-bottom: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

label {
  font-size: 0.875rem;
  color: #374151;
  margin-bottom: 0.375rem;
  font-weight: 500;
}

.form-control {
  appearance: none;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 0.875rem 1.125rem;
  outline: none;
  background: #fff;
  color: #111827;
  transition: border-color 0.2s, box-shadow 0.2s;
  font-size: 0.875rem;
  min-height: 48px;
}

/* Exact styling matching CreateTaskForm */
.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 12px 16px;
  font-size: 16px;
  color: #000000;
  background-color: #ffffff;
  border: 1px solid #d1d1d1;
  border-radius: 6px;
  transition: all 0.2s ease;
  box-sizing: border-box;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #000000;
  box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.1);
}

/* Error styling for form inputs */
.form-input.error,
.form-select.error,
.form-textarea.error {
  border-color: #dc3545;
  box-shadow: 0 0 0 2px rgba(220, 53, 69, 0.1);
}

.form-input::placeholder,
.form-textarea::placeholder {
  color: #888888;
}

/* Error Message */
.error-message {
  color: #dc3545;
  font-size: 12px;
  margin-top: 4px;
  display: block;
  min-height: 16px;
  opacity: 0;
  transition: opacity 0.2s ease;
  margin-bottom: 0;
}

.error-message.visible {
  opacity: 1;
}

/* Special styling for general error messages */
.error-message:not(span) {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  margin-top: 1rem;
  margin-bottom: 1rem;
  min-height: auto;
}

/* Success message styling */
.success-message {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #166534;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  margin-top: 1rem;
  margin-bottom: 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.success-message.visible {
  opacity: 1;
}


.form-control:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.15);
}

.form-control.error {
  border-color: #ef4444;
}

.form-control.error:focus {
  border-color: #ef4444;
  box-shadow: 0 0 0 4px rgba(239, 68, 68, 0.15);
}

.field-error {
  color: #ef4444;
  font-size: 0.75rem;
  margin-top: 0.25rem;
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
  margin-top: 0.5rem;
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
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

@media (max-width: 1024px) {
  .register-wrapper {
    grid-template-columns: 1fr;
    max-width: 600px;
    gap: 2rem;
  }
  .brand {
    text-align: center;
  }
  .card {
    min-width: auto;
    padding: 2rem;
  }
}

@media (max-width: 600px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .card {
    padding: 1.5rem;
  }
}
</style>
