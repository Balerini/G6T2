<template>
  <div class="create-project-container">
    <!-- Header Section -->
    <div class="header-section">
      <div class="container">
        <div class="header-content">
          <div class="title-section">
            <h1 class="hero-title">Create New Project</h1>
            <div class="division-badge" v-if="currentUser">
              {{ currentUser.division_name }} Department
            </div>
          </div>
          <button class="back-btn" @click="goBack">← Back to Projects</button>
        </div>
      </div>
    </div>

    <!-- Success Toast -->
    <transition name="toast-slide">
      <div v-if="successMessage" class="toast toast-success">
        <div class="toast-icon">🎉</div>
        <div class="toast-content">
          <div class="toast-title">Success!</div>
          <div class="toast-message">{{ successMessage }}</div>
        </div>
        <button @click="clearSuccessMessage" class="toast-close">×</button>
      </div>
    </transition>

    <!-- Error Toast -->
    <transition name="toast-slide">
      <div v-if="errorMessage" class="toast toast-error">
        <div class="toast-icon">❌</div>
        <div class="toast-content">
          <div class="toast-title">Error</div>
          <div class="toast-message">{{ errorMessage }}</div>
        </div>
        <button @click="clearErrorMessage" class="toast-close">×</button>
      </div>
    </transition>

    <!-- Create Project Form -->
    <div class="form-section">
      <div class="container">
        <form @submit.prevent="createProject" class="project-form">
          <div class="form-grid">
            <!-- Project Name -->
            <div class="form-group full-width">
              <label for="projectName" class="form-label">
                Project Name <span class="required">*</span>
              </label>
              <input
                id="projectName"
                v-model="formData.proj_name"
                type="text"
                class="form-input"
                :class="{ error: errors.proj_name }"
                placeholder="Enter project name"
                required
                maxlength="100"
              />
              <span v-if="errors.proj_name" class="error-message">{{ errors.proj_name }}</span>
            </div>

            <!-- Project Description -->
            <div class="form-group full-width">
              <label for="projectDesc" class="form-label">Project Description</label>
              <textarea
                id="projectDesc"
                v-model="formData.proj_desc"
                class="form-textarea"
                placeholder="Enter project description (optional)"
                rows="4"
                maxlength="500"
              ></textarea>
              <div class="char-count">{{ (formData.proj_desc || '').length }}/500 characters</div>
            </div>

            <!-- Start Date -->
            <div class="form-group">
              <label for="startDate" class="form-label">
                Start Date <span class="required">*</span>
              </label>
              <input
                id="startDate"
                v-model="formData.start_date"
                type="date"
                class="form-input"
                :class="{ error: errors.start_date }"
                :min="todayDate"
                required
              />
              <span v-if="errors.start_date" class="error-message">{{ errors.start_date }}</span>
            </div>

            <!-- End Date -->
            <div class="form-group">
              <label for="endDate" class="form-label">
                End Date <span class="required">*</span>
              </label>
              <input
                id="endDate"
                v-model="formData.end_date"
                type="date"
                class="form-input"
                :class="{ error: errors.end_date }"
                :min="formData.start_date || todayDate"
                required
              />
              <span v-if="errors.end_date" class="error-message">{{ errors.end_date }}</span>
            </div>
          </div>

          <!-- Form Actions -->
          <div class="form-actions">
            <button type="button" class="cancel-btn" @click="goBack" :disabled="loading">
              Cancel
            </button>
            <button type="submit" class="submit-btn" :disabled="loading || !isFormValid">
              <span v-if="loading">Creating...</span>
              <span v-else>Create Project</span>
            </button>
          </div>
        </form>

        <!-- Form Info -->
        <div class="form-info">
          <h3>Project Information</h3>
          <ul>
            <li><strong>Status:</strong> Will be automatically calculated based on tasks added to the project</li>
            <li><strong>Collaborators:</strong> Will be shown based on users assigned to project tasks</li>
            <li><strong>Division:</strong> Project will be associated with {{ currentUser?.division_name || 'your' }} department</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
console.log('CreateProject.vue script loading...')

import { authAPI, projectAPI } from '../services/api.js'

export default {
  name: 'CreateProject',
  data() {
    return {
      currentUser: null,
      loading: false,
      successMessage: '',
      errorMessage: '',
      formData: {
        proj_name: '',
        proj_desc: '',
        start_date: '',
        end_date: '',
        proj_status: 'Not Started',
        owner: '',
        division_name: ''
      },
      errors: {}
    }
  },
  computed: {
    todayDate() {
      return new Date().toISOString().split('T')[0]
    },
    isFormValid() {
      return (
        this.formData.proj_name.trim() &&
        this.formData.start_date &&
        this.formData.end_date &&
        !Object.keys(this.errors).length
      )
    }
  },
  watch: {
    'formData.proj_name'() {
      this.validateProjectName()
    },
    'formData.start_date'() {
      this.validateStartDate()
      // Revalidate end date when start date changes
      if (this.formData.end_date) {
        this.validateEndDate()
      }
    },
    'formData.end_date'() {
      this.validateEndDate()
    }
  },
  async created() {
    // Check authentication using your authAPI
    if (!authAPI.isLoggedIn()) {
      this.$router.push('/login')
      return
    }

    this.currentUser = authAPI.getCurrentUser()
    if (!this.currentUser) {
      this.errorMessage = 'Unable to get user information'
      return
    }

    // Set default form values
    this.formData.owner = this.currentUser.id || this.currentUser.user_ID
    this.formData.division_name = this.currentUser.division_name
  },
  methods: {
    validateProjectName() {
      if (!this.formData.proj_name.trim()) {
        this.$set(this.errors, 'proj_name', 'Project name is required')
      } else if (this.formData.proj_name.trim().length < 3) {
        this.$set(this.errors, 'proj_name', 'Project name must be at least 3 characters')
      } else {
        this.$delete(this.errors, 'proj_name')
      }
    },
    validateStartDate() {
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      const startDate = new Date(this.formData.start_date)
      
      if (!this.formData.start_date) {
        this.$set(this.errors, 'start_date', 'Start date is required')
      } else if (startDate < today) {
        this.$set(this.errors, 'start_date', 'Start date cannot be before today')
      } else {
        this.$delete(this.errors, 'start_date')
      }
    },
    validateEndDate() {
      const startDate = new Date(this.formData.start_date)
      const endDate = new Date(this.formData.end_date)
      
      if (!this.formData.end_date) {
        this.$set(this.errors, 'end_date', 'End date is required')
      } else if (!this.formData.start_date) {
        this.$set(this.errors, 'end_date', 'Please select start date first')
      } else if (endDate < startDate) {
        this.$set(this.errors, 'end_date', 'End date cannot be before start date')
      } else {
        this.$delete(this.errors, 'end_date')
      }
    },
    async createProject() {
      // Final validation
      this.validateProjectName()
      this.validateStartDate()
      this.validateEndDate()

      if (!this.isFormValid) {
        this.errorMessage = 'Please fix the form errors before submitting'
        return
      }

      this.loading = true
      this.errorMessage = ''

      try {
        // Prepare project data
        const projectData = {
          proj_name: this.formData.proj_name.trim(),
          proj_desc: this.formData.proj_desc.trim() || '',
          start_date: this.formData.start_date,
          end_date: this.formData.end_date,
          proj_status: 'Not Started',
          owner: this.currentUser.id || this.currentUser.user_ID,
          division_name: this.currentUser.division_name
        }

        console.log('Creating project with data:', projectData)
        
        // Create project via API
        const createdProject = await projectAPI.createProject(projectData)
        
        console.log('Project created successfully:', createdProject)
        
        // Show success message
        this.successMessage = `Project "${projectData.proj_name}" created successfully!`
        
        // Redirect to projects page after delay
        setTimeout(() => {
          this.$router.push('/projects?refresh=true')
        }, 2000)

      } catch (error) {
        console.error('Error creating project:', error)
        
        // Handle specific error messages from backend
        if (error.message) {
          this.errorMessage = error.message
        } else if (error.error) {
          this.errorMessage = error.error
        } else {
          this.errorMessage = 'Failed to create project. Please try again.'
        }
      } finally {
        this.loading = false
      }
    },
    goBack() {
      this.$router.push('/projects')
    },
    clearSuccessMessage() {
      this.successMessage = ''
    },
    clearErrorMessage() {
      this.errorMessage = ''
    }
  }
}
</script>

<style scoped>
/* Toast Styles (reused from projects-view-page) */
.toast {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 10000;
  display: flex;
  align-items: center;
  min-width: 280px;
  max-width: 400px;
  padding: 12px 16px;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(10px);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  animation: toastBounce 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.toast-success {
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
  color: white;
  border-left: 4px solid #2E7D32;
}

.toast-error {
  background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
  color: white;
  border-left: 4px solid #c62828;
}

.toast-icon {
  font-size: 20px;
  margin-right: 10px;
  flex-shrink: 0;
}

.toast-content {
  flex: 1;
  min-width: 0;
}

.toast-title {
  font-weight: 600;
  font-size: 13px;
  margin-bottom: 2px;
  opacity: 0.9;
}

.toast-message {
  font-size: 12px;
  line-height: 1.3;
  opacity: 0.95;
}

.toast-close {
  background: none;
  border: none;
  color: white;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  padding: 0;
  margin-left: 10px;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s ease;
  flex-shrink: 0;
}

.toast-close:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.toast-slide-enter-active {
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.toast-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.toast-slide-enter-from {
  transform: translateX(100%) scale(0.8);
  opacity: 0;
}

.toast-slide-leave-to {
  transform: translateX(100%) scale(0.8);
  opacity: 0;
}

@keyframes toastBounce {
  0% {
    transform: translateX(100%) scale(0.8);
    opacity: 0;
  }
  50% {
    transform: translateX(-10px) scale(1.05);
  }
  100% {
    transform: translateX(0) scale(1);
    opacity: 1;
  }
}

/* Main Styles */
.create-project-container {
  min-height: 100vh;
  background: #f8fafc;
}

.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.header-section {
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  padding: 1.5rem 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.title-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.hero-title {
  font-size: 2.25rem;
  line-height: 1.2;
  font-weight: 800;
  color: #111827;
  margin: 0;
}

.division-badge {
  background: #e0f2fe;
  color: #0277bd;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 500;
  align-self: flex-start;
}

.back-btn {
  background: #6b7280;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 0.75rem 1.5rem;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.back-btn:hover {
  background: #4b5563;
}

.form-section {
  padding: 2rem 0;
}

.project-form {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 2rem;
  margin-bottom: 2rem;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.5rem;
}

.required {
  color: #ef4444;
}

.form-input,
.form-textarea {
  border: 2px solid #e5e7eb;
  border-radius: 6px;
  padding: 0.75rem;
  font-size: 0.875rem;
  transition: border-color 0.2s ease;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
}

.form-input.error,
.form-textarea.error {
  border-color: #ef4444;
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

.char-count {
  font-size: 0.75rem;
  color: #6b7280;
  text-align: right;
  margin-top: 0.25rem;
}

.error-message {
  color: #ef4444;
  font-size: 0.75rem;
  margin-top: 0.25rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.cancel-btn,
.submit-btn {
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.cancel-btn {
  background: #f3f4f6;
  color: #374151;
}

.cancel-btn:hover:not(:disabled) {
  background: #e5e7eb;
}

.submit-btn {
  background: #3b82f6;
  color: #fff;
}

.submit-btn:hover:not(:disabled) {
  background: #2563eb;
}

.submit-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.form-info {
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 8px;
  padding: 1.5rem;
}

.form-info h3 {
  color: #0c4a6e;
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
}

.form-info ul {
  margin: 0;
  padding-left: 1.25rem;
  color: #0369a1;
}

.form-info li {
  margin-bottom: 0.5rem;
}

/* Responsive */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }

  .hero-title {
    font-size: 1.875rem;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .form-actions {
    flex-direction: column-reverse;
  }

  .toast {
    right: 10px;
    left: 10px;
    min-width: auto;
    max-width: none;
  }
}
</style>
