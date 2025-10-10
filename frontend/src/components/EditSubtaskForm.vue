<template>
    <div class="edit-subtask-wrapper">
    <div class="subtask-form-container">
      <!-- Toast Notifications -->
      <div v-if="successMessage" class="toast toast-success">
        {{ successMessage }}
      </div>
      
      <div v-if="uploadProgressMessage" class="toast toast-info">
        {{ uploadProgressMessage }}
      </div>
      
      <div v-if="errorMessage" class="toast toast-error">
        {{ errorMessage }}
      </div>
      
      <!-- Form Header with Close Button -->
      <div class="form-header">
        <h2 class="form-title">Edit Subtask</h2>
        <div class="header-actions">
          <button 
            v-if="canTransferOwnership"
            type="button" 
            class="transfer-ownership-btn" 
            @click="openTransferModal"
            title="Transfer ownership of this subtask"
          >
            🔄 Transfer Ownership
          </button>
          <button
            type="button" 
            class="close-btn" 
            @click="handleCancel"
            title="Close form"
          >
            ×
          </button>
        </div>
      </div>
      
      <!-- Form -->
      <form class="task-form" @submit.prevent="handleSubmit" novalidate>
        <!-- Subtask Name -->
        <div class="form-group">
          <label class="form-label" for="taskName">Subtask Name *</label>
          <input
            id="taskName"
            name="name"
            v-model="formData.name"
            type="text"
            class="form-input"
            :class="{ 'error': errors.name }"
            placeholder="Enter subtask name"
            @input="clearError('name')"
            @blur="validateField('name')"
          />
          <span v-if="errors.name" class="error-message">
            {{ errors.name }}
          </span>
        </div>

        <!-- Subtask Description -->
        <div class="form-group">
          <label class="form-label" for="taskDesc">Subtask Description</label>
          <textarea
            id="taskDesc"
            v-model="formData.description"
            class="form-textarea"
            :class="{ 'error': errors.description }"
            placeholder="Enter subtask description (max 500 characters)"
            rows="4"
            maxlength="500"
          ></textarea>
          <div class="char-count">
            {{ formData.description.length }}/500 characters
          </div>
          <span v-if="errors.description" class="error-message">
            {{ errors.description }}
          </span>
        </div>

        <!-- Assigned To / Collaborators -->
        <div class="form-group">
          <label class="form-label" for="assignedTo">
            Collaborators (Optional)
          </label>
          
          <!-- Show message when no collaborators are available -->
          <div v-if="availableStaff.length === 0" class="no-collaborators-message">
            No collaborators are assigned to the project. Please assign collaborators to the project first.
          </div>

          <!-- Combined search input with dropdown -->
          <div v-else class="search-dropdown-container" :class="{ 'dropdown-open': showDropdown }">
            <input
              id="assignedTo"
              name="assignedTo"
              v-model="userSearch"
              type="text"
              class="form-input"
              :class="{ 'error': errors.collaborators }"
              placeholder="Search and select collaborators..."
              @focus="handleInputFocus"
              @blur="handleInputBlur"
              @input="handleSearchInput"
              @keydown.enter.prevent="selectFirstMatch"
              @keydown.escape="closeDropdown"
              @keydown.arrow-down.prevent="navigateDown"
              @keydown.arrow-up.prevent="navigateUp"
            />
            
            <!-- Dropdown icon -->
            <div 
              class="dropdown-toggle-icon" 
              @click="toggleDropdown"
              :class="{ 'rotated': showDropdown }"
            >
              ▼
            </div>
            
            <!-- Dropdown options list -->
            <div 
              v-if="showDropdown" 
              class="dropdown-list"
              @mousedown.prevent
              @click.prevent
            >
              <!-- No results found -->
              <div 
                v-if="filteredUsers.length === 0 && userSearch" 
                class="dropdown-item no-results"
              >
                No users found matching "{{ userSearch }}"
              </div>
              
              <!-- Show all users when no search -->
              <div 
                v-else-if="filteredUsers.length === 0 && !userSearch" 
                class="dropdown-item no-results"
              >
                No more users available
              </div>
              
              <!-- User options -->
              <div 
                v-for="(user, index) in filteredUsers" 
                :key="`user-${index}-${user.id || user.name || 'unknown'}`"
                class="dropdown-item"
                :class="{ 
                  'highlighted': index === highlightedIndex,
                  'selected': isUserSelected(user),
                  'disabled': !canAssignTo(user)
                }"
                @mousedown.prevent="selectUser(user)"
                @mouseenter="highlightedIndex = index"
              >
                <div class="user-info">
                  <span class="user-name">{{ user.name }}{{ isCurrentUser(user.id) ? ' (You)' : '' }}</span>
                  <span v-if="user.department" class="user-email">{{ user.department }}</span>
                </div>
                <span v-if="isUserSelected(user)" class="selected-indicator">✓</span>
                <span v-if="!canAssignTo(user)" class="disabled-indicator">
                  (Cannot assign - higher rank)
                </span>
              </div>
            </div>
          </div>
          
          <!-- Selected collaborators tags -->
          <div class="assignee-tags" v-if="selectedCollaborators.length > 0">
            <span 
              v-for="(collaborator, index) in selectedCollaborators" 
              :key="`collaborator-${index}-${collaborator.id || 'unknown'}`"
              class="assignee-tag"
            >
              {{ collaborator.name }} ({{ collaborator.department }})
              <button 
                type="button" 
                class="remove-tag" 
                @click="removeCollaborator(index)"
                :title="`Remove ${collaborator.name}`"
              >
                ×
              </button>
            </span>
          </div>
          
          <!-- Status messages -->
          <div v-if="selectedCollaborators.length > 0" class="status-message info">
            {{ selectedCollaborators.length }} collaborator{{ selectedCollaborators.length !== 1 ? 's' : '' }} selected
          </div>
          
          <!-- Collaborators validation error -->
          <span v-if="errors.collaborators" class="error-message">
            {{ errors.collaborators }}
          </span>
        </div>

        <!-- Start Date -->
        <div class="form-group">
          <label class="form-label" for="startDate">Start Date *</label>
          <input
            id="startDate"
            name="startDate"
            v-model="formData.startDate"
            type="date"
            class="form-input"
            :class="{ 'error': errors.startDate }"
            @change="validateDates()"
            @input="clearError('startDate')"
            @blur="validateField('startDate')"
          />
          <span v-if="errors.startDate" class="error-message">
            {{ errors.startDate }}
          </span>
        </div>

        <!-- End Date -->
        <div class="form-group">
          <label class="form-label" for="endDate">End Date *</label>
          <input
            id="endDate"
            name="endDate"
            v-model="formData.endDate"
            type="date"
            class="form-input"
            :class="{ 'error': errors.endDate }"
            :min="formData.startDate"
            @change="validateDates()"
            @input="clearError('endDate')"
            @blur="validateField('endDate')"
          />
          <span v-if="errors.endDate" class="error-message">
            {{ errors.endDate }}
          </span>
        </div>

        <!-- Current Attachments (Read-only) -->
        <div class="form-group" v-if="formData.attachments && formData.attachments.length > 0">
          <label class="form-label">Current Attachments</label>
          <div class="file-preview-container">
            <div 
              v-for="(attachment, index) in formData.attachments" 
              :key="`attachment-${index}`"
              class="file-preview-item"
            >
              <div class="file-icon">
                {{ getFileIcon(attachment.name) }}
              </div>
              <div class="file-info">
                <span class="file-name">{{ attachment.name }}</span>
                <span class="file-size">Existing attachment</span>
              </div>
            </div>
          </div>
          <p class="helper-text">Note: Attachment editing not available in this version</p>
        </div>

        <!-- Subtask Status -->
        <div class="form-group">
          <label class="form-label" for="taskStatus">
            Subtask Status *
          </label>
          <select 
            id="taskStatus" 
            name="status"
            v-model="formData.status" 
            class="form-select"
            :class="{ 'error': errors.status }"
            @change="clearError('status')"
            @blur="validateField('status')"
          >
            <option value="" disabled>Select status</option>
            <option value="Unassigned">Unassigned</option>
            <option value="Ongoing">Ongoing</option>
            <option value="Under Review">Under Review</option>
            <option value="Completed">Completed</option>
          </select>
          <span v-if="errors.status" class="error-message">
            {{ errors.status }}
          </span>
        </div>

        <!-- Form Actions -->
        <div class="form-actions">
          <button type="button" class="btn btn-cancel" @click="handleCancel" :disabled="isSubmitting">
            Cancel
          </button>
          <button
            type="submit"
            :disabled="isSubmitting"
            class="btn btn-primary"
          >
            {{ isSubmitting ? 'Saving...' : 'Save Changes' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Transfer Ownership Modal -->
    <div v-if="showTransferModal" class="transfer-modal-overlay" @click="closeTransferModal">
      <div class="transfer-modal-content" @click.stop>
        <div class="transfer-modal-header">
          <h3>Transfer Subtask Ownership</h3>
          <button @click="closeTransferModal" class="transfer-close-btn">×</button>
        </div>
        <div class="transfer-modal-body">
          <div class="transfer-form">
            <div class="current-owner-info">
              <h4>Current Owner</h4>
              <div class="owner-display">
                <div class="owner-avatar">
                  {{ getInitials(getCurrentOwnerName()) }}
                </div>
                <div class="owner-details">
                  <p class="owner-name">{{ getCurrentOwnerName() }}</p>
                  <p class="owner-role">Subtask Owner</p>
                </div>
              </div>
            </div>

            <div class="new-owner-selection">
              <h4>Select New Owner</h4>
              <p class="transfer-description">
                You can only transfer ownership to collaborators assigned to this subtask.
              </p>
              
              <div v-if="transferEligibleUsers.length === 0" class="no-eligible-users">
                <p>No eligible users found for ownership transfer.</p>
                <p class="explanation">Only subtask collaborators can become the owner.</p>
              </div>

              <div v-else class="user-selection-list">
                <div 
                  v-for="user in transferEligibleUsers" 
                  :key="user.id" 
                  class="user-selection-item"
                  :class="{ selected: selectedNewOwner === user.id }"
                  @click="selectedNewOwner = user.id"
                >
                  <div class="owner-avatar">
                    {{ getInitials(user.name) }}
                  </div>
                  <div class="owner-details">
                    <p class="owner-name">{{ user.name }}</p>
                    <p class="owner-role">{{ user.department }}</p>
                  </div>
                  <div class="selection-indicator">
                    {{ selectedNewOwner === user.id ? '✓' : '' }}
                  </div>
                </div>
              </div>
            </div>

            <div class="transfer-modal-actions">
              <button @click="closeTransferModal" class="transfer-cancel-btn">Cancel</button>
              <button 
                @click="confirmTransferOwnership" 
                class="transfer-confirm-btn"
                :disabled="!selectedNewOwner || isTransferring"
              >
                {{ isTransferring ? 'Transferring...' : 'Transfer Ownership' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/* eslint-disable no-undef */
/* global defineProps, defineEmits */
import { ref, computed, onMounted, nextTick } from 'vue'
import { taskService } from '@/services/taskService'

// Props
const props = defineProps({
  subtask: {
    type: Object,
    required: true
  },
  availableCollaborators: {
    type: Function,
    required: true
  }
})

// Emits
const emit = defineEmits(['subtask-updated', 'cancel', 'validation-error'])

// Form data
const formData = ref({
  name: '',
  description: '',
  startDate: '',
  endDate: '',
  status: '',
  assigned_to: [],
  attachments: []
})

const errors = ref({})
const isSubmitting = ref(false)
const successMessage = ref('')
const errorMessage = ref('')
const uploadProgressMessage = ref('')
const originalStatus = ref('')

// Collaborators data
const selectedCollaborators = ref([])

// Dropdown-related reactive data
const userSearch = ref('')
const showDropdown = ref(false)
const highlightedIndex = ref(-1)
const dropdownCloseTimeout = ref(null)

// Transfer ownership data 
const showTransferModal = ref(false)  
const selectedNewOwner = ref(null)
const isTransferring = ref(false)
const transferEligibleUsers = ref([])

// Available staff from prop
const availableStaff = computed(() => {
  const collaborators = props.availableCollaborators()
  if (!collaborators || collaborators.length === 0) {
    return []
  }
  
  return collaborators.map(collaborator => ({
    id: collaborator.id,
    name: collaborator.name,
    department: collaborator.department || 'Unknown',
    rank: collaborator.rank || 3
  }))
})

// Filtered users for dropdown
const filteredUsers = computed(() => {
  let filtered = availableStaff.value.filter(user => {
    const isAlreadySelected = selectedCollaborators.value.some(collaborator => collaborator.id === user.id)
    return !isAlreadySelected
  })
  
  if (userSearch.value.trim()) {
    const searchTerm = userSearch.value.toLowerCase().trim()
    filtered = filtered.filter(user => 
      user.name.toLowerCase().includes(searchTerm) ||
      (user.department && user.department.toLowerCase().includes(searchTerm))
    )
  }
  
  return filtered.slice(0, 20)
})

// Get current user rank
const currentUserRank = computed(() => {
  if (typeof window !== 'undefined' && window.sessionStorage) {
    try {
      const currentUser = JSON.parse(sessionStorage.getItem('user') || '{}')
      return currentUser.role_num || currentUser.rank || 3
    } catch (error) {
      console.error('Error reading user from sessionStorage:', error)
      return 3
    }
  }
  return 3
})

// Check if current user can transfer ownership  
const canTransferOwnership = computed(() => {
  if (typeof window !== 'undefined' && window.sessionStorage) {
    try {
      const currentUser = JSON.parse(sessionStorage.getItem('user') || '{}')
      const userId = currentUser.id
      const userRole = currentUser.role_num || 4

      // Rule 1: Must be the owner of the subtask
      const isOwner = String(props.subtask.owner) === String(userId)

      // Rule 2: Must be a manager (role_num 3 only)
      const isManager = userRole === 3

      //Both conditions must be true 
      return isOwner && isManager
    } catch (error) {
      console.error('Error checking transfer permission:', error)
      return false
    }
  }
  return false
})

// Initialize form with subtask data
const initializeForm = () => {
  formData.value = {
    name: props.subtask.name || '',
    description: props.subtask.description || '',
    startDate: formatDateForInput(props.subtask.start_date),
    endDate: formatDateForInput(props.subtask.end_date),
    status: props.subtask.status || '',
    assigned_to: props.subtask.assigned_to ? [...props.subtask.assigned_to] : [],
    attachments: props.subtask.attachments ? [...props.subtask.attachments] : []
  }
  
  originalStatus.value = props.subtask.status || ''
  
  // Load selected collaborators
  if (props.subtask.assigned_to && props.subtask.assigned_to.length > 0) {
    selectedCollaborators.value = props.subtask.assigned_to
      .map(userId => {
        const user = availableStaff.value.find(u => String(u.id) === String(userId))
        return user ? {
          id: user.id,
          name: user.name,
          department: user.department
        } : null
      })
      .filter(user => user !== null)
  }
}

// Format date for input
const formatDateForInput = (date) => {
  if (!date) return ''
  const d = new Date(date)
  return d.toISOString().split('T')[0]
}

// Validate dates
const validateDates = () => {
  if (errors.value.startDate) delete errors.value.startDate
  if (errors.value.endDate) delete errors.value.endDate
  
  if (formData.value.startDate && formData.value.endDate) {
    const startDate = new Date(formData.value.startDate)
    const endDate = new Date(formData.value.endDate)
    
    if (endDate <= startDate) {
      errors.value.endDate = 'End date must be after start date'
    }
  }
}

// Validate specific field
const validateField = (fieldName) => {
  switch (fieldName) {
    case 'name':
      if (!formData.value.name.trim()) {
        errors.value.name = 'Subtask name is required'
      }
      break
    case 'startDate':
      if (!formData.value.startDate) {
        errors.value.startDate = 'Start date is required'
      } else {
        validateDates()
      }
      break
    case 'endDate':
      if (!formData.value.endDate) {
        errors.value.endDate = 'End date is required'
      } else {
        validateDates()
      }
      break
    case 'status':
      if (!formData.value.status) {
        errors.value.status = 'Status is required'
      }
      break
  }
}

// Clear error
const clearError = (fieldName) => {
  if (errors.value[fieldName]) {
    delete errors.value[fieldName]
  }
}

// Validate form
const validateForm = () => {
  errors.value = {}
  
  if (!formData.value.name.trim()) {
    errors.value.name = 'Subtask name is required'
  }
  
  if (!formData.value.startDate) {
    errors.value.startDate = 'Start date is required'
  }
  
  if (!formData.value.endDate) {
    errors.value.endDate = 'End date is required'
  }
  
  validateDates()
  
  if (!formData.value.status) {
    errors.value.status = 'Status is required'
  }
  
  // Validate collaborators based on status
  if (formData.value.status !== 'Unassigned' && selectedCollaborators.value.length === 0) {
    errors.value.collaborators = 'At least one collaborator is required when status is not "Unassigned"'
  }
  
  return Object.keys(errors.value).length === 0
}

// Check if user can assign to staff member
const canAssignTo = (staff) => {
  let currentUser = {}
  if (typeof window !== 'undefined' && window.sessionStorage) {
    try {
      currentUser = JSON.parse(sessionStorage.getItem('user') || '{}')
    } catch (error) {
      console.error('Error reading user from sessionStorage:', error)
      currentUser = {}
    }
  }
  
  const currentUserId = currentUser.id
  
  if (staff.id === currentUserId) {
    return true
  }
  
  return staff.rank > currentUserRank.value
}

// Check if current user
const isCurrentUser = (userId) => {
  if (typeof window !== 'undefined' && window.sessionStorage) {
    try {
      const currentUser = JSON.parse(sessionStorage.getItem('user') || '{}')
      return currentUser.id === userId
    } catch (error) {
      console.error('Error reading user from sessionStorage:', error)
      return false
    }
  }
  return false
}

// Dropdown methods
const handleInputFocus = () => {
  showDropdown.value = true
  highlightedIndex.value = -1
}

const handleInputBlur = () => {
  if (dropdownCloseTimeout.value) {
    clearTimeout(dropdownCloseTimeout.value)
  }
  
  dropdownCloseTimeout.value = setTimeout(() => {
    showDropdown.value = false
    highlightedIndex.value = -1
  }, 150)
}

const handleSearchInput = () => {
  highlightedIndex.value = -1
  if (!showDropdown.value) {
    showDropdown.value = true
  }
}

const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value
  if (showDropdown.value) {
    highlightedIndex.value = -1
  }
}

const closeDropdown = () => {
  showDropdown.value = false
  highlightedIndex.value = -1
  if (dropdownCloseTimeout.value) {
    clearTimeout(dropdownCloseTimeout.value)
    dropdownCloseTimeout.value = null
  }
}

const selectUser = (user) => {
  if (isUserSelected(user) || !canAssignTo(user)) {
    return
  }
  
  if (dropdownCloseTimeout.value) {
    clearTimeout(dropdownCloseTimeout.value)
    dropdownCloseTimeout.value = null
  }
  
  selectedCollaborators.value.push({
    id: user.id,
    name: user.name,
    department: user.department
  })
  
  errors.value.collaborators = ''
  userSearch.value = ''
  
  nextTick(() => {
    const input = document.getElementById('assignedTo')
    if (input) {
      input.focus()
    }
    showDropdown.value = true
  })
}

const isUserSelected = (user) => {
  return selectedCollaborators.value.some(collaborator => collaborator.id === user.id)
}

const selectFirstMatch = () => {
  if (filteredUsers.value.length > 0) {
    selectUser(filteredUsers.value[0])
  }
}

const navigateDown = () => {
  if (!showDropdown.value) {
    showDropdown.value = true
    return
  }
  
  if (highlightedIndex.value < filteredUsers.value.length - 1) {
    highlightedIndex.value++
  }
}

const navigateUp = () => {
  if (highlightedIndex.value > 0) {
    highlightedIndex.value--
  }
}

const removeCollaborator = (index) => {
  selectedCollaborators.value.splice(index, 1)
  errors.value.collaborators = ''
}

// Get file icon
const getFileIcon = (fileName) => {
  if (!fileName) return '📄'
  const ext = fileName.split('.').pop().toLowerCase()
  const iconMap = {
    'pdf': '📄',
    'doc': '📝',
    'docx': '📝',
    'txt': '📄',
    'jpg': '🖼️',
    'jpeg': '🖼️',
    'png': '🖼️',
    'gif': '🖼️'
  }
  return iconMap[ext] || '📄'
}

// Check for unsaved changes
const hasUnsavedChanges = () => {
  return (
    formData.value.name !== (props.subtask.name || '') ||
    formData.value.description !== (props.subtask.description || '') ||
    formData.value.startDate !== formatDateForInput(props.subtask.start_date) ||
    formData.value.endDate !== formatDateForInput(props.subtask.end_date) ||
    formData.value.status !== (props.subtask.status || '') ||
    JSON.stringify(formData.value.assigned_to) !== JSON.stringify(props.subtask.assigned_to || [])
  )
}

// Handle cancel
const handleCancel = () => {
  if (hasUnsavedChanges()) {
    const confirmed = confirm('You have unsaved changes. Are you sure you want to cancel?')
    if (!confirmed) return
  }
  
  emit('cancel')
}

// Handle form submission
const handleSubmit = async () => {
  errorMessage.value = ''
  
  if (!validateForm()) {
    // Find the first error field
    const firstErrorField = Object.keys(errors.value)[0]
    const errorMessage = errors.value[firstErrorField]
    
    // Emit validation error to parent
    emit('validation-error', {
      message: errorMessage,
      field: firstErrorField
    })
    
    // Scroll to the error field
    nextTick(() => {
      const fieldElement = document.querySelector(`[name="${firstErrorField}"]`) || 
                          document.getElementById(firstErrorField)
      if (fieldElement) {
        fieldElement.scrollIntoView({ behavior: 'smooth', block: 'center' })
        fieldElement.focus()
      }
    })

    return
  }
  
  isSubmitting.value = true
  
  try {
    // Get current user
    const currentUser = JSON.parse(sessionStorage.getItem('user') || '{}')
    
    // Prepare update data
    const updateData = {
      name: formData.value.name.trim(),
      description: formData.value.description.trim(),
      start_date: formData.value.startDate,
      end_date: formData.value.endDate,
      status: formData.value.status,
      assigned_to: selectedCollaborators.value.map(collab => collab.id),
      attachments: formData.value.attachments
    }
    
    // Check if status changed - if so, add change log
    if (formData.value.status !== originalStatus.value) {
      const changeLog = {
        staff_name: currentUser.name || 'Unknown User',
        timestamp: new Date().toISOString(),
        old_status: originalStatus.value,
        new_status: formData.value.status
      }
      
      // Add to status history
      if (!props.subtask.status_history) {
        updateData.status_history = [changeLog]
      } else {
        updateData.status_history = [...props.subtask.status_history, changeLog]
      }
    }
    
    console.log('Updating subtask with data:', updateData)
    
    // Update subtask via backend
    const updatedSubtask = await taskService.updateSubtask(props.subtask.id, updateData)
    
    console.log('Subtask updated successfully:', updatedSubtask)
    
    // Show success message
    successMessage.value = 'Subtask updated successfully!'
    
    setTimeout(() => {
      successMessage.value = ''
      // Emit success event with updated data
      emit('subtask-updated', {
        ...props.subtask,
        ...updatedSubtask
      })
    }, 1500)
    
  } catch (error) {
    console.error('Error updating subtask:', error)
    
    // Emit error to parent
    emit('validation-error', {
      message: `Failed to update subtask: ${error.message}`,
      field: null
    })
  } finally {
    isSubmitting.value = false
  }
}

// Get initials for avatar
const getInitials = (name) => {
  if (!name) return 'U'
  return name
    .split(' ')
    .map(word => word.charAt(0))
    .join('')
    .substring(0, 2)
    .toUpperCase()
}

// Get current owner name
const getCurrentOwnerName = () => {
  if (!props.subtask.owner) return 'Unknown'
  
  const owner = availableStaff.value.find(u => String(u.id) === String(props.subtask.owner))
  return owner ? owner.name : 'Unknown User'
}

// Open transfer modal
const openTransferModal = () => {
  // Load eligible users (only subtask collaborators)
  if (selectedCollaborators.value.length === 0) {
    errorMessage.value = 'Cannot transfer ownership: No collaborators assigned to this subtask.'
    setTimeout(() => {
      errorMessage.value = ''
    }, 3000)
    return
  }

  // Get current user info
  const currentUser = JSON.parse(sessionStorage.getItem('user') || '{}')
  const currentUserRole = currentUser.role_num || 4

  // Filter eligible users:
  // 1. Exclude current owner
  // 2. Must be subtask collaborators
  // 3. Must have HIGHER role_num (lower position) - top-down only
  //    Manager (role 3) can only transfer to Staff (role 4)
  transferEligibleUsers.value = selectedCollaborators.value.filter(collab => {
    // Exclude current owner
    if (String(collab.id) === String(currentUser.id)) return false

    // Find user in available staff to get their role
    const user = availableStaff.value.find(u => String(u.id) === String(collab.id))
    if (!user) return false
    
    const userRole = user.rank || 4

    // Only allow transfer to users with HIGHER role_num (lower position)
    // Manager (role 3) can only transfer to Staff (role 4)
    return userRole > currentUserRole
  })
  
  if (transferEligibleUsers.value.length === 0) {
    errorMessage.value = 'Cannot transfer ownership: No eligible staff members found. You can only transfer to staff (role 4) assigned to this subtask.'
    setTimeout(() => {
      errorMessage.value = ''
    }, 4000)
    return
  }
  
  showTransferModal.value = true
  selectedNewOwner.value = null
}

// Close transfer modal
const closeTransferModal = () => {
  showTransferModal.value = false
  selectedNewOwner.value = null
  transferEligibleUsers.value = []
}

// Confirm transfer ownership
const confirmTransferOwnership = async () => {
  if (!selectedNewOwner.value || isTransferring.value) return
  
  // Get the new owner details
  const newOwner = transferEligibleUsers.value.find(u => u.id === selectedNewOwner.value)
  if (!newOwner) return
  
  // Confirmation dialog
  const confirmed = confirm(
    `Are you sure you want to transfer ownership of this subtask to ${newOwner.name}?\n\n` +
    `This action will make ${newOwner.name} the new owner, and they will have full control over this subtask.`
  )
  
  if (!confirmed) return
  
  isTransferring.value = true
  
  try {
    // Update subtask owner
    const updateData = {
      owner: selectedNewOwner.value
    }
    
    await taskService.updateSubtask(props.subtask.id, updateData)
    
    // Show success message
    successMessage.value = `✅ Ownership successfully transferred to ${newOwner.name}!`
    
    // Close modal
    closeTransferModal()
    
    // Clear success message and emit update
    setTimeout(() => {
      successMessage.value = ''
      emit('subtask-updated', {
        ...props.subtask,
        owner: selectedNewOwner.value
      })
    }, 2000)
    
  } catch (error) {
    console.error('Error transferring ownership:', error)
    
    // Show error with retry option
    const retry = confirm(
      `Failed to transfer ownership: ${error.message}\n\n` +
      `Would you like to retry?`
    )
    
    if (retry) {
      // Retry the transfer
      confirmTransferOwnership()
    } else {
      closeTransferModal()
    }
  } finally {
    isTransferring.value = false
  }
}

// Initialize on mount
onMounted(() => {
  initializeForm()
})
</script>

<style scoped>
.subtask-form-container {
  padding: 24px;
}

/* Toast Notifications */
.toast {
  position: fixed;
  top: 20px;
  right: 20px;
  min-width: 300px;
  max-width: 500px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 10000;
  padding: 16px;
  font-weight: 500;
  animation: slideInRight 0.3s ease;
}

.toast-success {
  border-left: 4px solid #10b981;
  background-color: #f0fdf4;
  color: #166534;
}

.toast-info {
  border-left: 4px solid #3b82f6;
  background-color: #eff6ff;
  color: #1e40af;
}

.toast-error {
  border-left: 4px solid #ef4444;
  background-color: #fef2f2;
  color: #dc2626;
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e5e5;
}

.form-title {
  font-size: 24px;
  font-weight: 700;
  color: #000000;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #666666;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.2s ease;
  line-height: 1;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background-color: #f5f5f5;
  color: #333333;
}

.task-form {
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

.form-textarea {
  resize: vertical;
  min-height: 100px;
  font-family: inherit;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #000000;
  box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.1);
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
}

/* Error styling for form inputs */
.form-input.error,
.form-select.error,
.form-textarea.error {
  border-color: #dc3545;
  box-shadow: 0 0 0 2px rgba(220, 53, 69, 0.1);
}

/* Character count */
.char-count {
  font-size: 12px;
  color: #666666;
  text-align: right;
  margin-top: 4px;
}

/* Helper text */
.helper-text {
  font-size: 12px;
  color: #666666;
  margin-top: 4px;
  font-style: italic;
}

/* Search Dropdown Container */
.search-dropdown-container {
  position: relative;
  width: 100%;
}

.search-dropdown-container.dropdown-open .form-input {
  border-bottom-left-radius: 0;
  border-bottom-right-radius: 0;
  border-bottom-color: transparent;
}

.dropdown-toggle-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #666;
  cursor: pointer;
  user-select: none;
  transition: transform 0.2s ease;
  font-size: 12px;
  z-index: 1;
}

.dropdown-toggle-icon.rotated {
  transform: translateY(-50%) rotate(180deg);
}

.dropdown-list {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e5e5e5;
  border-top: none;
  border-radius: 0 0 8px 8px;
  max-height: 200px;
  overflow-y: auto;
  z-index: 1000;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.dropdown-item {
  padding: 12px 16px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: background-color 0.2s ease;
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item:hover,
.dropdown-item.highlighted {
  background-color: #f8f9fa;
}

.dropdown-item.selected {
  background-color: #e3f2fd;
  color: #1976d2;
}

.dropdown-item.disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background-color: #f5f5f5;
}

.dropdown-item.no-results {
  color: #666;
  font-style: italic;
  cursor: default;
}

.dropdown-item.no-results:hover {
  background-color: transparent;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-name {
  font-weight: 500;
  color: #333;
}

.user-email {
  font-size: 0.875rem;
  color: #666;
}

.selected-indicator {
  color: #1976d2;
  font-weight: bold;
}

.disabled-indicator {
  font-size: 0.75rem;
  color: #999;
  font-style: italic;
}

/* Assignee Tags */
.assignee-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.assignee-tag {
  display: inline-flex;
  align-items: center;
  background-color: #e3f2fd;
  color: #1976d2;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.875rem;
  border: 1px solid #bbdefb;
}

.remove-tag {
  background: none;
  border: none;
  color: #1976d2;
  margin-left: 6px;
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
  transition: background-color 0.15s ease;
}

.remove-tag:hover {
  background-color: rgba(25, 118, 210, 0.1);
}

.status-message {
  margin-top: 8px;
  font-size: 0.875rem;
  padding: 4px 0;
}

.status-message.warning {
  color: #f57c00;
}

.status-message.info {
  color: #1976d2;
}

.no-collaborators-message {
  padding: 12px 16px;
  background-color: #fff3cd;
  border: 1px solid #ffeaa7;
  color: #856404;
  border-radius: 6px;
  font-size: 14px;
  text-align: center;
  margin-bottom: 12px;
}

/* File Preview */
.file-preview-container {
  margin-top: 16px;
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #e5e5e5;
  border-radius: 6px;
  padding: 12px;
}

.file-preview-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background-color: #f8f9fa;
  border-radius: 4px;
  margin-bottom: 8px;
}

.file-preview-item:last-child {
  margin-bottom: 0;
}

.file-icon {
  margin-right: 8px;
  font-size: 16px;
}

.file-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.file-name {
  font-weight: 500;
  color: #333333;
  font-size: 14px;
}

.file-size {
  font-size: 12px;
  color: #666666;
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
  
  .file-preview-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}

/* Transfer Ownership Button */
.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.transfer-ownership-btn {
  background: #059669;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s;
}

.transfer-ownership-btn:hover {
  background: #047857;
}

/* Transfer Modal */
.transfer-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10001;
}

.transfer-modal-content {
  background: white;
  border-radius: 12px;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
}

.transfer-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
}

.transfer-modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #111827;
}

.transfer-close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6b7280;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.transfer-close-btn:hover {
  color: #374151;
}

.transfer-modal-body {
  padding: 24px;
}

.transfer-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.current-owner-info h4,
.new-owner-selection h4 {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 12px 0;
}

.transfer-description {
  font-size: 14px;
  color: #6b7280;
  margin: 0 0 16px 0;
}

.owner-display {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.owner-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #e0e7ff;
  color: #3730a3;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
}

.owner-details {
  flex: 1;
}

.owner-name {
  font-size: 14px;
  font-weight: 500;
  color: #111827;
  margin: 0 0 2px 0;
}

.owner-role {
  font-size: 12px;
  color: #6b7280;
  margin: 0;
}

.no-eligible-users {
  padding: 20px;
  background: #fef3c7;
  border-radius: 8px;
  text-align: center;
}

.no-eligible-users p {
  margin: 0 0 8px 0;
  color: #92400e;
}

.explanation {
  font-size: 14px;
  font-style: italic;
}

.user-selection-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 250px;
  overflow-y: auto;
}

.user-selection-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.user-selection-item:hover {
  background: #f9fafb;
  border-color: #d1d5db;
}

.user-selection-item.selected {
  background: #eff6ff;
  border-color: #3b82f6;
}

.selection-indicator {
  margin-left: auto;
  font-size: 18px;
  color: #10b981;
  font-weight: bold;
}

.transfer-modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
}

.transfer-cancel-btn {
  background: #f3f4f6;
  color: #374151;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s;
}

.transfer-cancel-btn:hover {
  background: #e5e7eb;
}

.transfer-confirm-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s;
}

.transfer-confirm-btn:hover:not(:disabled) {
  background: #2563eb;
}

.transfer-confirm-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}
</style>