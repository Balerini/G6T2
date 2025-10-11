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
      
      <div class="form-header">
        <h2 class="form-title">Edit Subtask</h2>
        <div class="header-actions">
          <!-- Remove the transfer ownership button from here -->
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
        <!-- Task (Auto-populated, read-only) -->
        <div class="form-group">
          <label class="form-label" for="taskId">Task</label>
          <input 
            id="taskId" 
            :value="parentTaskName || 'Loading...'" 
            type="text" 
            class="form-input readonly-input" 
            readonly 
            placeholder="Parent task name" 
          />
        </div>

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

        <!-- Owner with Transfer Ownership -->
        <div class="form-group">
          <label class="form-label" for="owner">Owner</label>
          <div class="owner-field-container">
            <input 
              id="owner" 
              v-model="ownerDisplayName" 
              type="text" 
              class="form-input readonly-input owner-input" 
              readonly 
              placeholder="Auto-populated from owner" 
            />
            <button 
              v-if="canTransferOwnership"
              type="button" 
              class="transfer-ownership-btn" 
              @click="showTransferModal = true"
              :disabled="isSubmitting"
              title="Transfer ownership of this subtask"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
                <circle cx="9" cy="7" r="4"/>
                <path d="M22 21v-2a4 4 0 0 0-3-3.87"/>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                <polyline points="17 11 22 6 17 1"/>
              </svg>
              Transfer
            </button>
          </div>
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
    <TransferOwnership
      :visible="showTransferModal"
      :task="props.subtask"
      :users="availableStaffAsUsers"
      :task-collaborators="selectedCollaborators"
      :is-subtask="true"
      @close="closeTransferModal"
      @transfer-success="handleTransferSuccess"
      @transfer-error="handleTransferError"
    />
  </div>
</template>

<script setup>
/* eslint-disable no-undef */
/* global defineProps, defineEmits */
import { ref, computed, onMounted, nextTick } from 'vue'
import { taskService } from '@/services/taskService'
import TransferOwnership from './TransferOwnership.vue' 

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
  attachments: [],
  owner: ''
})

const errors = ref({})
const isSubmitting = ref(false)
const successMessage = ref('')
const errorMessage = ref('')
const uploadProgressMessage = ref('')
const originalStatus = ref('')
const ownerDisplayName = ref('')
const parentTaskName = ref('');

// Collaborators data
const selectedCollaborators = ref([])

// Dropdown-related reactive data
const userSearch = ref('')
const showDropdown = ref(false)
const highlightedIndex = ref(-1)
const dropdownCloseTimeout = ref(null)

// Transfer ownership data 
const showTransferModal = ref(false)  

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

// Get current user from session storage
const getCurrentUser = () => {
  try {
    const userData = sessionStorage.getItem('user');
    if (userData) {
      const user = JSON.parse(userData);
      return user; // Return the full user object
    }
    return null;
  } catch (error) {
    console.error('Error getting current user:', error);
    return null;
  }
};

// Get user by ID from available staff
const getUserById = (userId) => {
  return availableStaff.value.find(user => String(user.id) === String(userId));
};

// Add this function to load parent task data
const loadParentTaskData = async () => {
  try {
    // Get parent task ID from the subtask
    const parentTaskId = props.subtask.parent_task_id;
    if (parentTaskId) {
      console.log('Loading parent task with ID:', parentTaskId);
      const taskData = await taskService.getTaskById(parentTaskId);
      console.log('Parent task data:', taskData);
      
      // Try different possible field names for the task name
      parentTaskName.value = taskData.name || 
                           taskData.task_name || 
                           taskData.taskName || 
                           taskData.title || 
                           'Unknown Task';
      
      console.log('Final parent task name:', parentTaskName.value);
    }
  } catch (error) {
    console.error('Error loading parent task data:', error);
    parentTaskName.value = 'Error loading task';
  }
};

// Convert available staff to user format for TransferOwnership
const availableStaffAsUsers = computed(() => {
  return availableStaff.value.map(staff => ({
    id: staff.id,
    name: staff.name,
    email: staff.email || '',
    department: staff.department,
    role_num: staff.rank,
    rank: staff.rank
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
    attachments: props.subtask.attachments ? [...props.subtask.attachments] : [],
    owner: props.subtask.owner || ''  
  }
  
  originalStatus.value = props.subtask.status || ''

  loadParentTaskData();
  
  // Load owner display name - Add this section
  if (props.subtask.owner) {
    const ownerUser = getUserById(props.subtask.owner);
    if (ownerUser) {
      ownerDisplayName.value = ownerUser.name || 'Unknown User';
    } else {
      // If owner not found in available staff, try to get from current user if it's them
      const currentUser = getCurrentUser();
      if (currentUser && String(currentUser.id) === String(props.subtask.owner)) {
        ownerDisplayName.value = currentUser.name || 'Current User';
      } else {
        ownerDisplayName.value = 'Unknown User';
      }
    }
  }
  
  // Load selected collaborators (existing code)
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
      } else {
        // Clear the error if validation passes
        if (errors.value.name) {
          delete errors.value.name
        }
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
  console.log('=== FORM SUBMIT DEBUG ===')
  console.log('Original subtask name:', props.subtask.name)
  console.log('Current form name:', formData.value.name)
  console.log('Form data:', formData.value)
  console.log('Errors before validation:', errors.value)

  errorMessage.value = ''
  
  if (!validateForm()) {
    console.log('Validation failed, errors:', errors.value)
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
  console.log('Validation passed, proceeding with submit...')
  
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
      attachments: formData.value.attachments,
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

    // Create the complete updated subtask object
    const completeUpdatedSubtask = {
      ...props.subtask,
      ...updatedSubtask,
      // Ensure these fields are properly updated
      name: updateData.name,
      description: updateData.description,
      start_date: updateData.start_date,
      end_date: updateData.end_date,
      status: updateData.status,
      assigned_to: updateData.assigned_to,
      attachments: updateData.attachments,
      status_history: updateData.status_history || props.subtask.status_history
    }

    // Emit success event with updated data
    emit('subtask-updated', completeUpdatedSubtask)
    emit('cancel')

    // Clear success message after delay
    setTimeout(() => {
      successMessage.value = ''
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

// Close transfer modal
const closeTransferModal = () => {
  showTransferModal.value = false
}

// Transfer ownership event handlers  
const handleTransferSuccess = (data) => {
  console.log('Transfer success:', data);
  
  // Show success message
  successMessage.value = data.message || 'Ownership transferred successfully!';
  
  // Close the transfer modal
  closeTransferModal();
  
  // UPDATE LOCAL DATA instead of emitting to parent
  // Update the owner display name to show the new owner
  if (data.newOwnerId) {
    // Find the new owner in available staff
    const newOwner = availableStaff.value.find(staff => 
      String(staff.id) === String(data.newOwnerId)
    );
    
    if (newOwner) {
      ownerDisplayName.value = newOwner.name;
    } else {
      ownerDisplayName.value = 'Unknown User';
    }
    
    // Update the local subtask owner data
    formData.value.owner = data.newOwnerId;
  }
  
  // Update canTransferOwnership computed property by triggering reactivity
  // Since ownership changed, the current user can no longer transfer
  
  // Clear success message after delay
  setTimeout(() => {
    successMessage.value = '';
  }, 3000);
  
  // DON'T emit subtask-updated here - keep the form open
  // emit('subtask-updated', { ...props.subtask, owner: data.newOwnerId });
};

const handleTransferError = (message) => {
  errorMessage.value = message
  
  // Clear error message after delay
  setTimeout(() => {
    errorMessage.value = ''
  }, 5000)
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

/* Add this to your existing styles */
.readonly-input {
  background-color: #f8f9fa !important;
  color: #6c757d;
  cursor: default;
}

.readonly-input:focus {
  box-shadow: none !important;
  border-color: #ced4da !important;
}

/* Owner field with transfer button */
.owner-field-container {
  display: flex;
  gap: 8px;
  align-items: center;
}

.owner-input {
  flex: 1;
}

.transfer-ownership-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  background-color: #5d82ee;
  border: 1px solid #5d82ee;
  border-radius: 6px;
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.transfer-ownership-btn:hover:not(:disabled) {
  background-color: #4864e2;
  border-color: #4864e2;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(99, 102, 241, 0.3);
}

.transfer-ownership-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(99, 102, 241, 0.2);
}

.transfer-ownership-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.transfer-ownership-btn svg {
  flex-shrink: 0;
}
</style>