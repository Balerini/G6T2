<template>
  <div class="modal-overlay" @click="$emit('close')">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2 class="modal-title">Create New Project</h2>
        <button class="close-button" @click="$emit('close')">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M13 1L1 13M1 1L13 13" stroke="currentColor" stroke-width="2" stroke-linecap="round"
              stroke-linejoin="round" />
          </svg>
        </button>
      </div>

      <div class="modal-body">
        <form class="project-form" @submit.prevent="handleSubmit" novalidate>

          <!-- Project Name -->
          <div class="form-group">
            <label class="form-label" for="projectName">Project Name *</label>
            <input id="projectName" v-model="formData.proj_name" type="text" class="form-input"
              :class="{ 'error': validationErrors.proj_name }" placeholder="Enter project name"
              @input="validateField('proj_name', $event.target.value)"
              @blur="validateField('proj_name', formData.proj_name)" />
            <span v-if="validationErrors.proj_name" class="error-message">
              {{ validationErrors.proj_name }}
            </span>
          </div>

          <!-- Project Description -->
          <div class="form-group">
            <label class="form-label" for="projectDesc">Project Description</label>
            <textarea id="projectDesc" v-model="formData.proj_desc" class="form-textarea"
              :class="{ 'error': validationErrors.proj_desc }"
              placeholder="Enter project description (max 500 characters)" rows="4"
              @input="validateField('proj_desc', $event.target.value)"
              @blur="validateField('proj_desc', formData.proj_desc)"></textarea>
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
            <input id="startDate" v-model="formData.start_date" type="date" class="form-input"
              :class="{ 'error': validationErrors.start_date }" :min="getCurrentDate()"
              @change="validateDates(); validateField('start_date', formData.start_date)"
              @blur="validateField('start_date', formData.start_date)" />
            <span v-if="validationErrors.start_date" class="error-message">
              {{ validationErrors.start_date }}
            </span>
          </div>

          <!-- End Date -->
          <div class="form-group">
            <label class="form-label" for="endDate">End Date *</label>
            <input id="endDate" v-model="formData.end_date" type="date" class="form-input"
              :class="{ 'error': validationErrors.end_date }" :min="formData.start_date || getCurrentDate()"
              @change="validateDates(); validateField('end_date', formData.end_date)"
              @blur="validateField('end_date', formData.end_date)" />
            <span v-if="validationErrors.end_date || dateValidationError" class="error-message">
              {{ validationErrors.end_date || dateValidationError }}
            </span>
          </div>

          <!-- Created By (Auto-populated, read-only) -->
          <div class="form-group">
            <label class="form-label" for="createdBy">Created By</label>
            <input id="createdBy" v-model="displayCreatedBy" type="text" class="form-input readonly-input" readonly
              placeholder="Auto-populated from current user" />
          </div>

          <!-- Collaborators - MATCHING CREATETASKFORM EXACTLY -->
          <div class="form-group">
            <label class="form-label" for="collaborators">
              Collaborators (1-10 required) *
            </label>

            <!-- Combined search input with dropdown -->
            <div class="search-dropdown-container" :class="{ 'dropdown-open': showDropdown }">
              <input id="collaborators" v-model="userSearch" type="text" class="form-input"
                :class="{ 'error': validationErrors.collaborators }"
                :placeholder="isLoadingUsers ? 'Loading users...' : 'Search and select collaborators...'"
                @focus="handleInputFocus(); validateField('collaborators', formData.assignedto)" @blur="handleInputBlur"
                @input="handleSearchInput" @keydown.enter.prevent="selectFirstMatch" @keydown.escape="closeDropdown"
                @keydown.arrow-down.prevent="navigateDown" @keydown.arrow-up.prevent="navigateUp"
                :disabled="isAtLimit || isLoadingUsers" />

              <!-- Dropdown icon -->
              <div class="dropdown-toggle-icon" @click="toggleDropdown" :class="{ 'rotated': showDropdown }">
                ▼
              </div>

              <!-- Dropdown options list -->
              <div v-if="showDropdown" class="dropdown-list" @mousedown.prevent @click.prevent>
                <!-- Loading state -->
                <div v-if="isLoadingUsers" class="dropdown-item loading">
                  Loading users...
                </div>

                <!-- No results found -->
                <div v-else-if="filteredUsers.length === 0 && userSearch" class="dropdown-item no-results">
                  No users found matching "{{ userSearch }}"
                </div>

                <!-- Show all users when no search -->
                <div v-else-if="filteredUsers.length === 0 && !userSearch" class="dropdown-item no-results">
                  No more users available
                </div>

                <!-- User options -->
                <div v-for="(user, index) in filteredUsers" :key="`user-${index}-${user.id || user.name || 'unknown'}`"
                  class="dropdown-item" :class="{
                    'highlighted': index === highlightedIndex,
                    'selected': isUserSelected(user)
                  }" @mousedown.prevent="selectUser(user)" @mouseenter="highlightedIndex = index">
                  <div class="user-info">
                    <span class="user-name">{{ user.name }}</span>
                    <span v-if="user.email" class="user-email">{{ user.email }}</span>
                  </div>
                  <span v-if="isUserSelected(user)" class="selected-indicator">✓</span>
                </div>
              </div>
            </div>

            <!-- Selected collaborators tags -->
            <div class="assignee-tags" v-if="formData.assignedto.length > 0">
              <span v-for="(assignee, index) in formData.assignedto"
                :key="`assignee-${index}-${assignee.id || assignee.name || 'unknown'}`" class="assignee-tag">
                {{ assignee.name }}
                <button type="button" class="remove-tag" @click="removeAssignee(index)"
                  :title="`Remove ${assignee.name}`">×</button>
              </span>
            </div>

            <!-- Status messages -->
            <div v-if="isAtLimit" class="status-message warning">
              Maximum number of collaborators reached (10)
            </div>

            <div v-if="formData.assignedto.length > 0" class="status-message info">
              {{ formData.assignedto.length }} collaborator{{ formData.assignedto.length !== 1 ? 's' : '' }} selected
            </div>

            <!-- Collaborators validation error -->
            <span v-if="validationErrors.collaborators" class="error-message">
              {{ validationErrors.collaborators }}
            </span>
          </div>

          <!-- Form Actions -->
          <div class="form-actions">
            <button type="button" class="btn btn-cancel" @click="$emit('close')" :disabled="loading">
              Cancel
            </button>
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
import { projectAPI, userAPI } from '../services/api.js'

export default {
  name: 'CreateProjectForm',
  emits: ['close', 'project-created'],
  data() {
    return {
      loading: false,
      dateValidationError: '',
      currentUser: null,

      // User management - matching CreateTaskForm
      users: [],
      userSearch: '',
      showDropdown: false,
      isLoadingUsers: false,
      highlightedIndex: -1,
      dropdownCloseTimeout: null,

      formData: {
        proj_name: '',
        proj_desc: '',
        start_date: '',
        end_date: '',
        created_by: '',
        assignedto: [] // Matching CreateTaskForm structure
      },
      validationErrors: {
        proj_name: '',
        proj_desc: '',
        start_date: '',
        end_date: '',
        collaborators: ''
      },
      touchedFields: {
        proj_name: false,
        proj_desc: false,
        start_date: false,
        end_date: false,
        collaborators: false
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
      return !hasValidationErrors && !hasDateError &&
        this.formData.proj_name.trim() &&
        this.formData.start_date &&
        this.formData.end_date &&
        this.formData.assignedto.length > 0
    },

    // Matching CreateTaskForm filtering logic exactly
    filteredUsers() {
      let filtered = this.users.filter(user => {
        // Filter out already selected users
        const isAlreadySelected = this.formData.assignedto.some(assignee =>
          assignee.id === user.id
        )
        return !isAlreadySelected
      })

      // Filter by role_num - only show users with same or lower role (higher or equal role_num)
      if (this.currentUser && this.currentUser.role_num !== undefined) {
        const currentUserRoleNum = this.currentUser.role_num
        console.log('Current user role_num:', currentUserRoleNum)

        filtered = filtered.filter(user => {
          // Only show users whose role_num is >= current user's role_num
          // (higher role_num = lower role/authority)
          const userRoleNum = user.role_num
          const isEligible = userRoleNum !== undefined && userRoleNum >= currentUserRoleNum

          if (!isEligible) {
            console.log(`Filtering out ${user.name} - role_num ${userRoleNum} is lower (higher authority) than current user's ${currentUserRoleNum}`)
          }

          return isEligible
        })
      }

      if (this.userSearch.trim()) {
        const searchTerm = this.userSearch.toLowerCase().trim()
        filtered = filtered.filter(user => {
          return user.name.toLowerCase().includes(searchTerm) ||
            (user.email && user.email.toLowerCase().includes(searchTerm))
        })
      }

      return filtered.slice(0, 20) // Limit results
    },

    isAtLimit() {
      return this.formData.assignedto.length >= 10
    }
  },

  async created() {
    console.log('CreateProjectForm created, getting current user...')

    this.currentUser = AuthService.getCurrentUser()
    console.log('Current user from AuthService:', this.currentUser)

    if (this.currentUser) {
      this.formData.created_by = this.currentUser.id || this.currentUser.user_ID || 'Unknown ID'
      console.log('Set created_by to:', this.formData.created_by)

      // Auto-add current user as collaborator
      this.formData.assignedto.push({
        id: this.currentUser.id || this.currentUser.user_ID,
        name: this.currentUser.name || this.currentUser.email || 'Current User',
        email: this.currentUser.email || ''
      })

      // Load users from same division
      await this.loadUsers()
    } else {
      console.warn('No current user found!')
    }
  },

  methods: {
    getCurrentDate() {
      const today = new Date()
      return today.toISOString().split('T')[0]
    },

    // Load users from same division - matching CreateTaskForm
    async loadUsers() {
      if (!this.currentUser?.division_name) {
        console.log('No division name available')
        return
      }

      this.isLoadingUsers = true
      try {
        console.log(`Loading users from ${this.currentUser.division_name} division...`)

        const allUsers = await userAPI.getAllUsers()

        // Filter by same division only
        this.users = allUsers.filter(user =>
          user.division_name === this.currentUser.division_name
        )

        console.log(`Found ${this.users.length} users in ${this.currentUser.division_name} division`)

      } catch (error) {
        console.error('Error loading users:', error)
        this.users = []
      } finally {
        this.isLoadingUsers = false
      }
    },

    // Dropdown methods - matching CreateTaskForm exactly
    handleInputFocus() {
      if (!this.isAtLimit && !this.isLoadingUsers) {
        this.showDropdown = true
        this.highlightedIndex = -1
      }
    },

    handleInputBlur(event) {
      if (this.dropdownCloseTimeout) {
        clearTimeout(this.dropdownCloseTimeout)
      }

      const relatedTarget = event.relatedTarget
      const dropdownContainer = document.querySelector('.search-dropdown-container')

      if (relatedTarget && dropdownContainer && dropdownContainer.contains(relatedTarget)) {
        return
      }

      this.dropdownCloseTimeout = setTimeout(() => {
        this.closeDropdown()
      }, 500)
    },

    handleSearchInput() {
      if (!this.showDropdown && !this.isAtLimit) {
        this.showDropdown = true
      }
      this.highlightedIndex = -1
    },

    toggleDropdown() {
      if (this.isAtLimit || this.isLoadingUsers) return

      if (this.dropdownCloseTimeout) {
        clearTimeout(this.dropdownCloseTimeout)
        this.dropdownCloseTimeout = null
      }

      this.showDropdown = !this.showDropdown

      if (this.showDropdown) {
        this.$nextTick(() => {
          document.getElementById('collaborators')?.focus()
        })
      }
    },

    closeDropdown() {
      this.showDropdown = false
      this.highlightedIndex = -1
      this.userSearch = ''
    },

    selectUser(user) {
      if (this.isAtLimit || this.isUserSelected(user)) return

      if (this.dropdownCloseTimeout) {
        clearTimeout(this.dropdownCloseTimeout)
        this.dropdownCloseTimeout = null
      }

      // Add user to collaborators
      this.formData.assignedto.push({
        id: user.id,
        name: user.name,
        email: user.email || ''
      })

      // Validate collaborators after adding
      this.validateField('collaborators', this.formData.assignedto, false)

      // Reset search but keep dropdown open if not at limit
      this.userSearch = ''

      if (!this.isAtLimit) {
        this.$nextTick(() => {
          const input = document.getElementById('collaborators')
          if (input) input.focus()
        })
        this.showDropdown = true
      } else {
        this.closeDropdown()
      }
    },

    isUserSelected(user) {
      return this.formData.assignedto.some(assignee => assignee.id === user.id)
    },

    selectFirstMatch() {
      if (this.filteredUsers.length > 0) {
        this.selectUser(this.filteredUsers[0])
      }
    },

    navigateDown() {
      if (!this.showDropdown) {
        this.showDropdown = true
        return
      }
      if (this.highlightedIndex < this.filteredUsers.length - 1) {
        this.highlightedIndex++
      }
    },

    navigateUp() {
      if (this.highlightedIndex > 0) {
        this.highlightedIndex--
      }
    },

    removeAssignee(index) {
      this.formData.assignedto.splice(index, 1)
      this.validateField('collaborators', this.formData.assignedto, false)
    },

    // Validation methods (existing ones)
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

    validateCollaborators(collaborators) {
      if (!collaborators || collaborators.length === 0) {
        return 'At least 1 collaborator is required'
      }
      if (collaborators.length > 10) {
        return 'Maximum 10 collaborators allowed'
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
          if (this.formData.end_date && this.touchedFields.end_date) {
            this.validationErrors.end_date = this.validateEndDate(this.formData.end_date, value)
          }
          break
        case 'end_date':
          this.validationErrors.end_date = this.touchedFields.end_date ? this.validateEndDate(value, this.formData.start_date) : ''
          break
        case 'collaborators':
          this.validationErrors.collaborators = this.touchedFields.collaborators ? this.validateCollaborators(value) : ''
          break
      }
    },

    async handleSubmit() {
      if (this.loading) return

      console.log('Form submitted, validating all fields...')

      // Mark all fields as touched
      Object.keys(this.touchedFields).forEach(key => {
        this.touchedFields[key] = true
      })

      // Validate all fields
      this.validateField('proj_name', this.formData.proj_name, true)
      this.validateField('proj_desc', this.formData.proj_desc, true)
      this.validateField('start_date', this.formData.start_date, true)
      this.validateField('end_date', this.formData.end_date, true)
      this.validateField('collaborators', this.formData.assignedto, true)
      this.validateDates()

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

        // Build collaborators array from selected users
        const collaboratorIds = this.formData.assignedto.map(user => user.id)

        const projectData = {
          proj_name: this.formData.proj_name.trim(),
          proj_desc: this.formData.proj_desc.trim(),
          start_date: this.formData.start_date,
          end_date: this.formData.end_date,
          created_by: creatorId,
          division_name: this.currentUser.division_name,
          collaborators: collaboratorIds
        }

        console.log('Creating project with collaborators:', projectData)

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

/* Error States */
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

/* Collaborators Section - EXACT CreateTaskForm Styles */
.search-dropdown-container {
  position: relative;
  display: flex;
  align-items: center;
}

.dropdown-toggle-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  color: #666666;
  font-size: 12px;
  transition: transform 0.2s ease;
  z-index: 10;
}

.dropdown-toggle-icon.rotated {
  transform: translateY(-50%) rotate(180deg);
}

.dropdown-open .form-input {
  border-bottom-color: #d1d1d1;
  border-bottom-left-radius: 0;
  border-bottom-right-radius: 0;
}

.dropdown-list {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #d1d1d1;
  border-top: none;
  border-radius: 0 0 6px 6px;
  max-height: 200px;
  overflow-y: auto;
  z-index: 1000;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.dropdown-item {
  padding: 12px 16px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s ease;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dropdown-item:hover,
.dropdown-item.highlighted {
  background-color: #f5f5f5;
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item.loading,
.dropdown-item.no-results {
  color: #666666;
  font-style: italic;
  cursor: default;
  justify-content: center;
}

.dropdown-item.loading:hover,
.dropdown-item.no-results:hover {
  background-color: transparent;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: #000000;
}

.user-email {
  font-size: 12px;
  color: #666666;
}

.selected-indicator {
  color: #28a745;
  font-weight: bold;
  font-size: 16px;
}

/* Selected Collaborators Tags */
.assignee-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.assignee-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background-color: #dbeafe;
  border: none;
  border-radius: 20px;
  padding: 8px 12px;
  font-size: 14px;
  white-space: nowrap;
  font-weight: 500;
}

.remove-tag {
  background: none;
  border: none;
  color: #3b82f6;
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
  padding: 0;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s ease;
  margin-left: 4px;
}

.remove-tag:hover {
  color: #2563eb;
  background-color: rgba(59, 130, 246, 0.1);
}

/* Status Messages */
.status-message {
  font-size: 12px;
  margin-top: 4px;
  padding: 4px 0;
}

.status-message.info {
  color: #3b82f6;
}

.status-message.warning {
  color: #856404;
}

/* Form Actions */
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