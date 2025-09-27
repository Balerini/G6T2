<template>
  <div class="modal-overlay" @click="$emit('close')">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2 class="modal-title">Create New Project</h2>
        <!-- Removed circle/border from close button -->
        <button class="close-button" @click="$emit('close')">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M13 1L1 13M1 1L13 13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
      
      <div class="modal-body">
        <form class="project-form" @submit.prevent="handleSubmit" novalidate>
          
          <!-- Project Name -->
          <div class="form-group">
            <label class="form-label" for="projectName">Project Name *</label>
            <input
              id="projectName"
              v-model="formData.proj_name"
              type="text"
              class="form-input"
              :class="{ 'error': validationErrors.proj_name }"
              placeholder="Enter project name"
              @input="validateField('proj_name', $event.target.value)"
              @blur="validateField('proj_name', formData.proj_name)"
            />
            <span v-if="validationErrors.proj_name" class="error-message">
              {{ validationErrors.proj_name }}
            </span>
          </div>

          <!-- Project Description -->
          <div class="form-group">
            <label class="form-label" for="projectDesc">Project Description</label>
            <textarea
              id="projectDesc"
              v-model="formData.proj_desc"
              class="form-textarea"
              :class="{ 'error': validationErrors.proj_desc }"
              placeholder="Enter project description (max 500 characters)"
              rows="4"
              @input="validateField('proj_desc', $event.target.value)"
              @blur="validateField('proj_desc', formData.proj_desc)"
            ></textarea>
            <div class="char-count">
              {{ formData.proj_desc.length }}/500 characters
            </div>
            <span v-if="validationErrors.proj_desc" class="error-message">
              {{ validationErrors.proj_desc }}
            </span>
          </div>

          <!-- Start Date -->
          <div class="form-group">
            <label class="form-label" for="startDate">Start Date *</label>
            <input
              id="startDate"
              v-model="formData.start_date"
              type="date"
              class="form-input"
              :class="{ 'error': validationErrors.start_date }"
              :min="getCurrentDate()"
              @change="validateDates(); validateField('start_date', formData.start_date)"
              @blur="validateField('start_date', formData.start_date)"
            />
            <span v-if="validationErrors.start_date" class="error-message">
              {{ validationErrors.start_date }}
            </span>
          </div>

          <!-- End Date -->
          <div class="form-group">
            <label class="form-label" for="endDate">End Date *</label>
            <input
              id="endDate"
              v-model="formData.end_date"
              type="date"
              class="form-input"
              :class="{ 'error': validationErrors.end_date }"
              :min="formData.start_date || getCurrentDate()"
              @change="validateDates(); validateField('end_date', formData.end_date)"
              @blur="validateField('end_date', formData.end_date)"
            />
            <span v-if="validationErrors.end_date || dateValidationError" class="error-message">
              {{ validationErrors.end_date || dateValidationError }}
            </span>
          </div>

          <!-- Created By (Auto-populated, read-only) -->
          <div class="form-group">
            <label class="form-label" for="createdBy">Created By</label>
            <input
              id="createdBy"
              v-model="displayCreatedBy"
              type="text"
              class="form-input readonly-input"
              readonly
              placeholder="Loading user information..."
            />
          </div>

          <!-- Form Actions -->
          <div class="form-actions">
            <button type="button" class="btn btn-cancel" @click="$emit('close')" :disabled="loading">
              Cancel
            </button>
            <!-- Removed :disabled condition so button is always clickable -->
            <button type="submit" class="btn btn-primary" :disabled="loading">
              {{ loading ? 'Creating...' : 'Create Project' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import AuthService from '../services/auth.js'
import { projectAPI } from '../services/api.js'

export default {
  name: 'CreateProjectForm',
  emits: ['close', 'project-created'],
  data() {
    return {
      loading: false,
      dateValidationError: '',
      currentUser: null,
      formData: {
        proj_name: '',
        proj_desc: '',
        start_date: '',
        end_date: '',
        created_by: ''
      },
      validationErrors: {
        proj_name: '',
        proj_desc: '',
        start_date: '',
        end_date: ''
      },
      touchedFields: {
        proj_name: false,
        proj_desc: false,
        start_date: false,
        end_date: false
      }
    }
  },
  computed: {
    displayCreatedBy() {
      if (this.currentUser) {
        return this.currentUser.name || this.currentUser.email || `User ${this.currentUser.id || this.currentUser.user_ID}`
      }
      return 'Loading user information...'
    },
    isFormValid() {
      const hasValidationErrors = Object.values(this.validationErrors).some(error => error !== '')
      const hasDateError = this.dateValidationError !== ''
      return !hasValidationErrors && !hasDateError && this.formData.proj_name.trim() && this.formData.start_date && this.formData.end_date
    }
  },
  async created() {
    console.log('CreateProjectForm created, getting current user...')
    
    // Use AuthService instead of authAPI
    this.currentUser = AuthService.getCurrentUser()
    console.log('Current user from AuthService:', this.currentUser)
    
    if (this.currentUser) {
      this.formData.created_by = this.currentUser.id || this.currentUser.user_ID || 'Unknown ID'
      console.log('Set created_by to:', this.formData.created_by)
    } else {
      console.warn('No current user found!')
      
      // Additional debugging
      console.log('Checking localStorage for user:', localStorage.getItem('user'))
      console.log('Auth status:', AuthService.checkAuthStatus())
    }
  },
  methods: {
    getCurrentDate() {
      const today = new Date()
      return today.toISOString().split('T')[0]
    },

    validateProjectName(value) {
      if (!value || !value.trim()) {
        return 'Project name is required'
      }
      if (value.length < 3) {
        return 'Project name must be at least 3 characters'
      }
      if (value.length > 100) {
        return 'Project name must be less than 100 characters'
      }
      return ''
    },

    validateProjectDescription(value) {
      if (value && value.length > 500) {
        return 'Project description must be less than 500 characters'
      }
      return ''
    },

    validateStartDate(value) {
      if (!value) {
        return 'Start date is required'
      }
      const startDate = new Date(value)
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      
      if (startDate < today) {
        return 'Start date cannot be in the past'
      }
      return ''
    },

    validateEndDate(value, startDate) {
      if (!value) {
        return 'End date is required'
      }
      if (!startDate) {
        return ''
      }
      const start = new Date(startDate)
      const end = new Date(value)
      
      if (end <= start) {
        return 'End date must be after start date'
      }
      return ''
    },

    validateDates() {
      this.dateValidationError = ''
      
      if (this.formData.start_date && this.formData.end_date) {
        const startDate = new Date(this.formData.start_date)
        const endDate = new Date(this.formData.end_date)
        
        if (endDate <= startDate) {
          this.dateValidationError = 'End date must be after start date'
          return false
        }
      }
      return true
    },

    validateField(fieldName, value, markAsTouched = true) {
      if (markAsTouched) {
        this.touchedFields[fieldName] = true
      }
      
      switch (fieldName) {
        case 'proj_name':
          this.validationErrors.proj_name = this.touchedFields.proj_name ? this.validateProjectName(value) : ''
          break
        case 'proj_desc':
          this.validationErrors.proj_desc = this.touchedFields.proj_desc ? this.validateProjectDescription(value) : ''
          break
        case 'start_date':
          this.validationErrors.start_date = this.touchedFields.start_date ? this.validateStartDate(value) : ''
          // Re-validate end date when start date changes
          if (this.formData.end_date && this.touchedFields.end_date) {
            this.validationErrors.end_date = this.validateEndDate(this.formData.end_date, value)
          }
          break
        case 'end_date':
          this.validationErrors.end_date = this.touchedFields.end_date ? this.validateEndDate(value, this.formData.start_date) : ''
          break
      }
    },

    async handleSubmit() {
      if (this.loading) return

      console.log('Form submitted, validating all fields...')

      // Mark all fields as touched to show validation errors
      Object.keys(this.touchedFields).forEach(key => {
        this.touchedFields[key] = true
      })

      // Validate all fields
      this.validateField('proj_name', this.formData.proj_name, true)
      this.validateField('proj_desc', this.formData.proj_desc, true)
      this.validateField('start_date', this.formData.start_date, true)
      this.validateField('end_date', this.formData.end_date, true)
      this.validateDates()

      // Show errors and stop submission if form is invalid
      if (!this.isFormValid) {
        console.log('Form validation failed, showing errors')
        return
      }

      this.loading = true

      try {
        if (!this.currentUser) {
          this.currentUser = AuthService.getCurrentUser()
        }
        
        if (!this.currentUser) {
          throw new Error('User not authenticated')
        }
        
        const creatorId = this.currentUser.id || this.currentUser.user_ID
        
        const projectData = {
          proj_name: this.formData.proj_name.trim(),
          proj_desc: this.formData.proj_desc.trim(),
          start_date: this.formData.start_date,
          end_date: this.formData.end_date,
          created_by: creatorId,
          division_name: this.currentUser.division_name,
          collaborators: [creatorId] // 👈 ADD CREATOR AS COLLABORATOR
        }
        
        console.log('Creating project with creator as collaborator:', projectData)
        
        const result = await projectAPI.createProject(projectData)
        
        console.log('Project created successfully:', result)
        
        this.$emit('project-created', result)
        
      } catch (error) {
        console.error('Error creating project:', error)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
/* Modal Overlay */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

/* Modal Header */
.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.modal-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  flex-grow: 1;
}

/* Close Button - Removed circle/border styling */
.close-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s ease;
  padding: 0;
  flex-shrink: 0;
}

.close-button:hover {
  color: #374151;
}

.close-button:active {
  transform: scale(0.95);
}

.close-button svg {
  width: 14px;
  height: 14px;
}

/* Modal Body */
.modal-body {
  padding: 1.5rem;
}

/* Form Styles - Matching CreateTaskForm exactly */
.project-form {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  font-weight: 600;
  color: #000000;
  margin-bottom: 4px;
}

.form-input,
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

.form-textarea {
  resize: vertical;
  min-height: 100px;
  font-family: inherit;
}

.readonly-input {
  background-color: #f8f9fa;
  color: #6c757d;
  cursor: not-allowed;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #000000;
  box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.1);
}

.form-input::placeholder,
.form-textarea::placeholder {
  color: #888888;
}

/* Error States - Matching CreateTaskForm */
.error-message {
  color: #dc3545;
  font-size: 12px;
  margin-top: 4px;
  display: block;
}

.form-input.error,
.form-textarea.error {
  border-color: #dc3545;
  box-shadow: 0 0 0 2px rgba(220, 53, 69, 0.1);
}

/* Character Count */
.char-count {
  font-size: 12px;
  color: #666666;
  text-align: right;
  margin-top: 4px;
}

/* Form Actions - Matching CreateTaskForm exactly */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #e5e5e5;
}

.btn {
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 600;
  border-radius: 6px;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.2s ease;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-cancel {
  background-color: #ffffff;
  color: #666666;
  border-color: #d1d1d1;
}

.btn-cancel:hover:not(:disabled) {
  background-color: #f5f5f5;
  color: #333333;
}

.btn-primary {
  background-color: #000000;
  color: #ffffff;
}

.btn-primary:hover:not(:disabled) {
  background-color: #333333;
}

/* Responsive Design */
@media (max-width: 768px) {
  .form-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}
</style>
