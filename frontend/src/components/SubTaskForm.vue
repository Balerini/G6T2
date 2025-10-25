<template>
  <div class="subtask-form-container">
    <!-- Toast Notifications -->
    <div v-if="successMessage" class="toast toast-success">
      {{ successMessage }}
    </div>
    
    <div v-if="uploadProgressMessage" class="toast toast-info">
      {{ uploadProgressMessage }}
    </div>
    
    <!-- Form Header with Close Button -->
    <div class="form-header">
      <h2 class="form-title">Create New Subtask</h2>
      <button 
        type="button" 
        class="close-btn" 
        @click="$emit('cancel')"
        title="Close form"
      >
        ×
      </button>
    </div>
    
    <!-- Loading state -->
    <div v-if="isLoadingParentData" class="loading-state">
      <p>Loading parent task data...</p>
    </div>
    
    <!-- Form -->
    <form v-else class="task-form" @submit.prevent="handleSubmit" novalidate>
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
          v-model="form.name"
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
          v-model="form.description"
          class="form-textarea"
          :class="{ 'error': errors.description }"
          placeholder="Enter subtask description (max 500 characters)"
          rows="4"
        ></textarea>
        <div class="char-count">
          {{ form.description.length }}/500 characters
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
          v-model="form.startDate"
          type="date"
          class="form-input"
          :class="{ 'error': errors.startDate }"
          :min="getSubtaskMinStartDate()"
          :max="getSubtaskMaxStartDate()"
          @change="validateDates()"
          @input="clearError('startDate')"
          @blur="validateField('startDate')"
        />
        <span v-if="errors.startDate" class="error-message">
          {{ errors.startDate }}
        </span>
        <div v-if="getDateConstraintInfo()" class="date-constraint-info">
          {{ getDateConstraintInfo() }}
        </div>
      </div>

      <!-- End Date -->
      <div class="form-group">
        <label class="form-label" for="endDate">End Date *</label>
        <input
          id="endDate"
          v-model="form.endDate"
          type="date"
          class="form-input"
          :class="{ 'error': errors.endDate }"
          :min="form.startDate || getSubtaskMinStartDate()"
          :max="getSubtaskMaxEndDate()"
          @change="validateDates()"
          @input="clearError('endDate')"
          @blur="validateField('endDate')"
        />
        <span v-if="errors.endDate" class="error-message">
          {{ errors.endDate }}
        </span>
      </div>

      <!-- Owner (Auto-populated, read-only) -->
      <div class="form-group">
        <label class="form-label" for="owner">Subtask Owner</label>
        <input 
          id="owner" 
          v-model="ownerDisplayName" 
          type="text" 
          class="form-input readonly-input" 
          readonly 
          placeholder="Auto-populated from current user" 
        />
      </div>

      <!-- Assigned To -->
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
            v-model="userSearch"
            type="text"
            class="form-input"
            :class="{ 'error': errors.collaborators }"
            :placeholder="'Search and select collaborators...'"
            @focus="handleInputFocus"
            @blur="handleInputBlur"
            @input="handleSearchInput"
            @keydown.enter.prevent="selectFirstMatch"
            @keydown.escape="closeDropdown"
            @keydown.arrow-down.prevent="navigateDown"
            @keydown.arrow-up.prevent="navigateUp"
            :disabled="isAtLimit"
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
                'selected': isUserSelected(user)
              }"
              @mousedown.prevent="selectUser(user)"
              @mouseenter="highlightedIndex = index"
            >
              <div class="user-info">
                <span class="user-name">{{ user.name }}{{ isCurrentUser(user.id) ? ' (You)' : '' }}</span>
                <span v-if="user.department" class="user-email">{{ user.department }}</span>
              </div>
              <span v-if="isUserSelected(user)" class="selected-indicator">✓</span>
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

      <!-- Attachments -->
      <div class="form-group">
        <label class="form-label" for="attachments">Attachments (0-3 max)</label>
        <div class="file-upload-container">
          <input
            id="attachments"
            type="file"
            class="file-input"
            multiple
            accept=".pdf,.doc,.docx,.jpg,.png,.txt"
            @change="handleFileUpload"
            ref="fileInput"
          />
          <label for="attachments" class="file-upload-label">
            Choose Files
          </label>
          <span class="file-status">
            {{ selectedFiles.length > 0 ? `${selectedFiles.length} file(s) selected` : 'No file chosen' }}
          </span>
        </div>
        
        <!-- File Preview List -->
        <div class="file-preview-container" v-if="selectedFiles.length > 0">
          <div 
            v-for="(file, index) in selectedFiles" 
            :key="`file-${index}-${file.name || 'unknown'}`"
            class="file-preview-item"
            :style="{ borderLeftColor: getFileTypeColor(file.type) }"
          >
            <div class="file-icon">
              {{ getFileIcon(file.type) }}
            </div>
            <div class="file-info">
              <span class="file-name">{{ file.name }}</span>
              <span class="file-size">{{ formatFileSize(file.size) }}</span>
            </div>
            <button 
              type="button" 
              class="remove-file-btn" 
              @click="removeFile(index)"
              title="Remove file"
            >
              ×
            </button>
          </div>
        </div>
        
        <!-- Attachment validation error -->
        <span v-if="errors.attachments" class="error-message">
          {{ errors.attachments }}
        </span>
      </div>

      <!-- Subtask Status -->
      <div class="form-group">
        <label class="form-label" for="taskStatus">
          Subtask Status *
        </label>
        <select 
          id="taskStatus" 
          v-model="form.status" 
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

      <!-- Subtask Priority -->
      <div class="form-group">
        <label class="form-label" for="priority">
          Priority (1-10) *
        </label>
        <select 
          id="priority"
          v-model="form.priority"
          class="form-select"
          :class="{ 'error': errors.priority }"
          @change="validateField('priority')"
          @blur="validateField('priority')"
        >
          <option value="" disabled>Select priority (1-10)</option>
          <option value="1">1</option>
          <option value="2">2</option>
          <option value="3">3</option>
          <option value="4">4</option>
          <option value="5">5</option>
          <option value="6">6</option>
          <option value="7">7</option>
          <option value="8">8</option>
          <option value="9">9</option>
          <option value="10">10</option>
        </select>
        <span v-if="errors.priority" class="error-message">
          {{ errors.priority }}
        </span>
      </div>

      <!-- SUBMIT BUTTON, DISABLE WHEN SUBMITTING, CHANGE TO CREATING WHEN SUBMITTING -->
      <div class="form-actions">
        <button type="button" class="btn btn-cancel" @click="$emit('cancel')" :disabled="isSubmitting">
          Cancel
        </button>
        <button
          type="submit"
          :disabled="isSubmitting || isUploadingFiles"
          class="btn btn-primary"
        >
          {{ isUploadingFiles ? 'Uploading files...' : isSubmitting ? 'Creating...' : 'Create Subtask' }}
        </button>
      </div>
    </form>

    <!-- SUCCESS + ERROR MSG -->
    <div v-if="showSuccess" class="success-message">
      Subtask created successfully!
    </div>

    <div v-if="showError" class="error-message-block">
      {{ errorMessage }}
    </div>
  </div>
</template>

<script setup>
/* eslint-disable no-undef */
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { taskService } from '@/services/taskService'
import { fileUploadService } from '@/services/fileUploadService'

// Props for parent task and project IDs
// eslint-disable-next-line no-unused-vars
const props = defineProps({
  parentTaskId: {
    type: [String, Number],
    required: true
  },
  parentProjectId: {
    type: [String, Number], 
    required: true
  },
  availableCollaborators: {
    type: Array,
    default: () => []
  }
})


// Emits for notifying parent component
const emit = defineEmits(['subtask-created', 'cancel', 'upload-progress', 'upload-success', 'upload-error', 'subtask-error'])

const form = ref({
  name: '',
  description: '',
  startDate: '',
  endDate: '',
  status: '',
  owner: '',
  priority: '',
})

const errors = ref({})
const isSubmitting = ref(false)
const isUploadingFiles = ref(false)
const showSuccess = ref(false)
const showError = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const uploadProgressMessage = ref('')
const parentTaskName = ref('');

// Parent task and project data
const parentTask = ref(null)
const parentProject = ref(null)
const isLoadingParentData = ref(true)

// Collaborators data
const selectedCollaborators = ref([])

// Dropdown-related reactive data
const userSearch = ref('')
const showDropdown = ref(false)
const highlightedIndex = ref(-1)
const dropdownCloseTimeout = ref(null)

// Use prop instead of mock data    
const availableStaff = computed(() => {
  if (!props.availableCollaborators || props.availableCollaborators.length === 0) {
    return []
  }
  
  // Filter to only show collaborators from the parent task
  return props.availableCollaborators.map(collaborator => ({
    id: collaborator.id,
    name: collaborator.name,
    department: collaborator.department || 'Unknown',
    rank: collaborator.rank || 3
  }))
})

const filteredUsers = computed(() => {
  let filtered = availableStaff.value.filter(user => {
    // Filter out already selected users
    const isAlreadySelected = selectedCollaborators.value.some(collaborator => collaborator.id === user.id);
    return !isAlreadySelected;
  });
  
  if (userSearch.value.trim()) {
    const searchTerm = userSearch.value.toLowerCase().trim();
    filtered = filtered.filter(user => 
      user.name.toLowerCase().includes(searchTerm) ||
      (user.department && user.department.toLowerCase().includes(searchTerm))
    );
  }
  
  return filtered.slice(0, 20);
});

const isAtLimit = computed(() => {
  return false // No limit for collaborators
});

const getSubtaskMinStartDate = () => {
  // Priority 1: Task start date (if task has dates, use task duration)
  if (parentTask.value?.start_date) {
    return new Date(parentTask.value.start_date).toISOString().split('T')[0]
  }
  
  // Priority 2: Project start date (if no task dates, use project duration)
  if (parentProject.value?.start_date) {
    return new Date(parentProject.value.start_date).toISOString().split('T')[0]
  }
  
  // Priority 3: Today (if no project/task dates)
  return new Date().toISOString().split('T')[0]
}

// Get maximum start date for subtask (must be within task duration)
const getSubtaskMaxStartDate = () => {
  // Priority 1: Task end date (if task has dates, use task duration)
  if (parentTask.value?.end_date) {
    return new Date(parentTask.value.end_date).toISOString().split('T')[0]
  }
  
  // Priority 2: Project end date (if no task dates, use project duration)
  if (parentProject.value?.end_date) {
    return new Date(parentProject.value.end_date).toISOString().split('T')[0]
  }
  
  // Priority 3: No constraint (if no project/task dates)
  return null
}

// Get maximum end date for subtask (must be within task duration)
const getSubtaskMaxEndDate = () => {
  // Priority 1: Task end date (if task has dates, use task duration)
  if (parentTask.value?.end_date) {
    return new Date(parentTask.value.end_date).toISOString().split('T')[0]
  }
  
  // Priority 2: Project end date (if no task dates, use project duration)
  if (parentProject.value?.end_date) {
    return new Date(parentProject.value.end_date).toISOString().split('T')[0]
  }
  
  // Priority 3: No constraint (if no project/task dates)
  return null
}

// Get info text about date constraints
const getDateConstraintInfo = () => {
  if (parentTask.value?.start_date && parentTask.value?.end_date) {
    const startDate = new Date(parentTask.value.start_date).toLocaleDateString('en-SG', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    })
    const endDate = new Date(parentTask.value.end_date).toLocaleDateString('en-SG', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    })
    return `Task dates: ${startDate} - ${endDate}`
  }
  
  if (parentProject.value?.start_date && parentProject.value?.end_date) {
    const startDate = new Date(parentProject.value.start_date).toLocaleDateString('en-SG', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    })
    const endDate = new Date(parentProject.value.end_date).toLocaleDateString('en-SG', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    })
    return `Project dates: ${startDate} - ${endDate}`
  }
  
  return null
}

// Validate dates with cascading logic
const validateUnassignedConstraint = () => {
  // Ensure assigned collaborators exist
  const collaborators = selectedCollaborators.value || [];
  
  // Rule 1: If subtask status is "Unassigned", there should be no collaborators
  if (form.value.status === 'Unassigned' && collaborators.length > 0) {
    return 'Unassigned subtasks cannot have collaborators. Please remove all collaborators or change the status.';
  }
  
  // Rule 2: If subtask status is NOT "Unassigned", must have at least 1 collaborator
  if (form.value.status && form.value.status !== 'Unassigned' && collaborators.length === 0) {
    return `Subtasks with status "${form.value.status}" must have at least 1 person assigned.`;
  }
  
  return null;
};

const validateDates = () => {
  // Clear previous date errors
  if (errors.value.startDate) delete errors.value.startDate
  if (errors.value.endDate) delete errors.value.endDate
  
  // Validate start date
  if (form.value.startDate) {
    const startDate = new Date(form.value.startDate)
    
    // Priority 1: Check task constraints (if task has dates, use task duration)
    if (parentTask.value?.start_date) {
      const taskStartDate = new Date(parentTask.value.start_date)
      // Normalize dates to compare only the date part (ignore time)
      const startDateOnly = new Date(startDate.getFullYear(), startDate.getMonth(), startDate.getDate())
      const taskStartDateOnly = new Date(taskStartDate.getFullYear(), taskStartDate.getMonth(), taskStartDate.getDate())
      
      if (startDateOnly < taskStartDateOnly) {
        const formattedDate = new Date(parentTask.value.start_date).toLocaleDateString('en-SG', {
          day: '2-digit',
          month: 'short',
          year: 'numeric'
        })
        errors.value.startDate = `Start date cannot be before task start date (${formattedDate})`
        return
      }
    }
    
    if (parentTask.value?.end_date) {
      const taskEndDate = new Date(parentTask.value.end_date)
      // Normalize dates to compare only the date part (ignore time)
      const startDateOnly = new Date(startDate.getFullYear(), startDate.getMonth(), startDate.getDate())
      const taskEndDateOnly = new Date(taskEndDate.getFullYear(), taskEndDate.getMonth(), taskEndDate.getDate())
      
      if (startDateOnly > taskEndDateOnly) {
        const formattedDate = new Date(parentTask.value.end_date).toLocaleDateString('en-SG', {
          day: '2-digit',
          month: 'short',
          year: 'numeric'
        })
        errors.value.startDate = `Start date cannot be after task end date (${formattedDate})`
        return
      }
    }
    
    // Priority 2: Check project constraints (only if no task dates)
    if (!parentTask.value?.start_date && !parentTask.value?.end_date) {
      // Only check project constraints if task has no dates at all
      if (parentProject.value?.start_date) {
        const projectStartDate = new Date(parentProject.value.start_date)
        if (startDate < projectStartDate) {
          const formattedDate = new Date(parentProject.value.start_date).toLocaleDateString('en-SG', {
            day: '2-digit',
            month: 'short',
            year: 'numeric'
          })
          errors.value.startDate = `Start date cannot be before project start date (${formattedDate})`
          return
        }
      }
      
      if (parentProject.value?.end_date) {
        const projectEndDate = new Date(parentProject.value.end_date)
        if (startDate > projectEndDate) {
          const formattedDate = new Date(parentProject.value.end_date).toLocaleDateString('en-SG', {
            day: '2-digit',
            month: 'short',
            year: 'numeric'
          })
          errors.value.startDate = `Start date cannot be after project end date (${formattedDate})`
          return
        }
      }
    }
  }
  
  // Validate end date - no need to declare 'today' again
  if (form.value.endDate) {
    const endDate = new Date(form.value.endDate)
    
    // Must be after start date
    if (form.value.startDate) {
      const startDate = new Date(form.value.startDate)
      if (endDate <= startDate) {
        errors.value.endDate = 'End date must be after start date'
        return
      }
    }
    
    // Check task constraints first
    if (parentTask.value?.end_date) {
      const taskEndDate = new Date(parentTask.value.end_date)
      // Normalize dates to compare only the date part (ignore time)
      const endDateOnly = new Date(endDate.getFullYear(), endDate.getMonth(), endDate.getDate())
      const taskEndDateOnly = new Date(taskEndDate.getFullYear(), taskEndDate.getMonth(), taskEndDate.getDate())
      
      if (endDateOnly > taskEndDateOnly) {
        const formattedDate = new Date(parentTask.value.end_date).toLocaleDateString('en-SG', {
          day: '2-digit',
          month: 'short',
          year: 'numeric'
        })
        errors.value.endDate = `End date cannot be after task end date (${formattedDate})`
        return
      }
    }
    
    if (parentTask.value?.start_date) {
      const taskStartDate = new Date(parentTask.value.start_date)
      if (endDate < taskStartDate) {
        const formattedDate = new Date(parentTask.value.start_date).toLocaleDateString('en-SG', {
          day: '2-digit',
          month: 'short',
          year: 'numeric'
        })
        errors.value.endDate = `End date cannot be before task start date (${formattedDate})`
        return
      }
    }
    
    // If no task constraints, check project constraints
    if (!parentTask.value?.end_date && parentProject.value?.end_date) {
      const projectEndDate = new Date(parentProject.value.end_date)
      // Normalize dates to compare only the date part (ignore time)
      const endDateOnly = new Date(endDate.getFullYear(), endDate.getMonth(), endDate.getDate())
      const projectEndDateOnly = new Date(projectEndDate.getFullYear(), projectEndDate.getMonth(), projectEndDate.getDate())
      
      if (endDateOnly > projectEndDateOnly) {
        const formattedDate = new Date(parentProject.value.end_date).toLocaleDateString('en-SG', {
          day: '2-digit',
          month: 'short',
          year: 'numeric'
        })
        errors.value.endDate = `End date cannot be after project end date (${formattedDate})`
        return
      }
    }
    
    if (!parentTask.value?.start_date && parentProject.value?.start_date) {
      const projectStartDate = new Date(parentProject.value.start_date)
      if (endDate < projectStartDate) {
        const formattedDate = new Date(parentProject.value.start_date).toLocaleDateString('en-SG', {
          day: '2-digit',
          month: 'short',
          year: 'numeric'
        })
        errors.value.endDate = `End date cannot be before project start date (${formattedDate})`
        return
      }
    }
  }
}

// Load parent task data and pre-fill form
const loadParentTaskData = async () => {
  try {
    isLoadingParentData.value = true;
    
    // Validate props
    if (!props.parentTaskId || !props.parentProjectId) {
      throw new Error(`Invalid props: parentTaskId=${props.parentTaskId}, parentProjectId=${props.parentProjectId}`);
    }
    
    console.log('Loading parent task data:', { 
      parentTaskId: props.parentTaskId, 
      parentProjectId: props.parentProjectId 
    });
    
    // Load parent task data
    const taskData = await taskService.getTaskById(props.parentTaskId);
    parentTask.value = taskData;
    console.log('Parent task loaded:', taskData);

    // Try multiple possible field names for the task name
    parentTaskName.value = taskData.name || 
                        taskData.task_name || 
                        taskData.taskName || 
                        taskData.title || 
                        taskData.task_title ||
                        taskData.taskTitle ||
                        'Unknown Task';

    // Debug: Log what we found
    console.log('Final parent task name:', parentTaskName.value);
    console.log('Available task fields:', Object.keys(taskData));
    
    // Load parent project data
    const projectData = await taskService.getProjectById(props.parentProjectId);
    parentProject.value = projectData;
    console.log('Parent project loaded:', projectData);
    
    // Pre-fill form with parent task data
    if (parentTask.value) {
      // Don't pre-fill the subtask name and description - let user enter unique values
      form.value.name = '';
      form.value.description = '';
      
      // Always pre-fill start date with task start date
      if (parentTask.value.start_date) {
        const date = new Date(parentTask.value.start_date);
        const startDate = date.getFullYear() + '-' + 
          String(date.getMonth() + 1).padStart(2, '0') + '-' + 
          String(date.getDate()).padStart(2, '0');
        form.value.startDate = startDate;
      } else {
        form.value.startDate = '';
      }
      
      // Pre-fill end date with task end date
      if (parentTask.value.end_date) {
        const date = new Date(parentTask.value.end_date);
        const endDate = date.getFullYear() + '-' + 
          String(date.getMonth() + 1).padStart(2, '0') + '-' + 
          String(date.getDate()).padStart(2, '0');
        form.value.endDate = endDate;
      } else {
        form.value.endDate = '';
      }
      
      // Don't pre-fill status - let user choose
      form.value.status = '';
      
      // Don't pre-fill collaborators - let user choose from project collaborators
      selectedCollaborators.value = [];
    }
    
  } catch (error) {
    console.error('Error loading parent task data:', error);
    console.error('Parent Task ID:', props.parentTaskId);
    console.error('Parent Project ID:', props.parentProjectId);
    errorMessage.value = `Failed to load parent task data. Task ID: ${props.parentTaskId}, Project ID: ${props.parentProjectId}. Error: ${error.message}`;
    showError.value = true;
    parentTaskName.value = 'Error loading task';
  } finally {
    isLoadingParentData.value = false;
  }
}

// Initialize on component mount
onMounted(() => {
  loadParentTaskData();

  const currentUser = getCurrentUser();
  if (currentUser) {
    ownerDisplayName.value = currentUser.name || 'Current User';
    form.value.owner = currentUser.id;
  }
});

// File Attachments Data
const selectedFiles = ref([])
const fileInput = ref(null)

// Add this near the top with other refs
const ownerDisplayName = ref('');

// Add this helper function (copy from createtaskform)
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

// Check if Current user can assign tasks to this staff member
const canAssignTo = (staff) => {
  // Get current user info
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
  
  console.log('canAssignTo check:', {
    staffName: staff.name,
    staffId: staff.id,
    currentUserId: currentUserId,
  });

  // Subtask owner can invite any collaborators from the parent task 
  // No rank restrictions 
  return true;
}

// Dropdown interaction methods
const handleInputFocus = () => {
  if (!isAtLimit.value) {
    showDropdown.value = true;
    highlightedIndex.value = -1;
  }
};

const handleInputBlur = () => {
  // Clear any existing timeout
  if (dropdownCloseTimeout.value) {
    clearTimeout(dropdownCloseTimeout.value);
  }
  
  // Set a timeout to close dropdown after a short delay
  // This allows click events on dropdown items to fire before closing
  dropdownCloseTimeout.value = setTimeout(() => {
    showDropdown.value = false;
    highlightedIndex.value = -1;
  }, 150);
};

const handleSearchInput = () => {
  highlightedIndex.value = -1;
  if (!showDropdown.value) {
    showDropdown.value = true;
  }
};

const toggleDropdown = () => {
  if (isAtLimit.value) return;
  showDropdown.value = !showDropdown.value;
  if (showDropdown.value) {
    highlightedIndex.value = -1;
  }
};

const closeDropdown = () => {
  showDropdown.value = false;
  highlightedIndex.value = -1;
  if (dropdownCloseTimeout.value) {
    clearTimeout(dropdownCloseTimeout.value);
    dropdownCloseTimeout.value = null;
  }
};

const selectUser = (user) => {
  console.log('selectUser called with:', user);
  console.log('isAtLimit:', isAtLimit.value);
  console.log('isUserSelected:', isUserSelected(user));
  
  if (isAtLimit.value || isUserSelected(user) || !canAssignTo(user)) {
    console.log('User selection blocked');
    return;
  }
  
  // Clear any pending close timeout
  if (dropdownCloseTimeout.value) {
    clearTimeout(dropdownCloseTimeout.value);
    dropdownCloseTimeout.value = null;
  }
  
  // Add user to selected collaborators
  selectedCollaborators.value.push({
    id: user.id,
    name: user.name,
    department: user.department
  });
  
  // Clear any collaborator errors
  errors.value.collaborators = '';
  
  // Reset search but DON'T close dropdown
  userSearch.value = '';
  
  // Keep dropdown open if not at limit and re-focus input
  if (!isAtLimit.value) {
    nextTick(() => {
      const input = document.getElementById('assignedTo');
      if (input) {
        input.focus(); // Re-focus the input
      }
      // Keep dropdown open for next selection
      showDropdown.value = true;
    });
  } else {
    // Only close if at limit
    closeDropdown();
  }
};

const isUserSelected = (user) => {
  return selectedCollaborators.value.some(collaborator => collaborator.id === user.id);
};

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

const selectFirstMatch = () => {
  if (filteredUsers.value.length > 0) {
    selectUser(filteredUsers.value[0]);
  }
};

const navigateDown = () => {
  if (!showDropdown.value) {
    showDropdown.value = true;
    return;
  }
  
  if (highlightedIndex.value < filteredUsers.value.length - 1) {
    highlightedIndex.value++;
  }
};

const navigateUp = () => {
  if (highlightedIndex.value > 0) {
    highlightedIndex.value--;
  }
};

// Remove Collaborator
const removeCollaborator = (index) => {
  selectedCollaborators.value.splice(index, 1);
  errors.value.collaborators = '';
};

// Handle file upload
const handleFileUpload = (event) => {
  const files = Array.from(event.target.files)
  
  if (files.length + selectedFiles.value.length > 3) {
    errors.value.attachments = 'Maximum 3 files allowed'
    
    // Clear the error message after 3 seconds
    setTimeout(() => {
      errors.value.attachments = ''
    }, 3000)
    
    return
  }
  
  selectedFiles.value = [...selectedFiles.value, ...files].slice(0, 3)
  errors.value.attachments = ''
}

// Remove file
const removeFile = (index) => {
  selectedFiles.value.splice(index, 1)
  
  // Clear file input if no files left
  if (fileInput.value && selectedFiles.value.length === 0) {
    fileInput.value.value = ''
  }

  // Clear any file-related error   
  if (selectedFiles.value.length <= 3) {
    errors.value.attachments = ''
  }
}

// Format file size
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// Get file icon based on file type
const getFileIcon = (fileType) => {
  if (!fileType) return '📄'
  
  const type = fileType.toLowerCase()
  if (type.includes('pdf')) return '📄'
  if (type.includes('doc') || type.includes('docx')) return '📝'
  if (type.includes('jpg') || type.includes('jpeg') || type.includes('png') || type.includes('gif')) return '🖼️'
  if (type.includes('txt')) return '📄'
  return '📄'
}

// Get file type color for border
const getFileTypeColor = (fileType) => {
  if (!fileType) return '#666666'
  
  const type = fileType.toLowerCase()
  if (type.includes('pdf')) return '#dc3545'
  if (type.includes('doc') || type.includes('docx')) return '#007bff'
  if (type.includes('jpg') || type.includes('jpeg') || type.includes('png') || type.includes('gif')) return '#28a745'
  if (type.includes('txt')) return '#6c757d'
  return '#666666'
}

// Clear specific field error
const clearError = (fieldName) => {
  if (errors.value[fieldName]) {
    delete errors.value[fieldName]
  }
}

// Validate specific field
const validateField = (fieldName) => {
  switch (fieldName) {
    case 'name':
      if (!form.value.name.trim()) {
        errors.value.name = 'Subtask name is required'
      }
      break
    case 'startDate':
      if (!form.value.startDate) {
        errors.value.startDate = 'Start date is required'
      } else if (form.value.startDate || form.value.endDate) {
        validateDates()
      }
      break
    case 'endDate':
      if (!form.value.endDate) {
        errors.value.endDate = 'End date is required'
      } else if (form.value.startDate || form.value.endDate) {
        validateDates()
      }
      break
    case 'status': {
      if (!form.value.status) {
        errors.value.status = 'Status is required'
      }
      
      // Check unassigned constraint
      const constraintError = validateUnassignedConstraint();
      if (constraintError) {
        errors.value.status = constraintError;
        errors.value.collaborators = constraintError;
      } else if (form.value.status !== 'Unassigned') {
        // Clear collaborators error if status is not unassigned
        if (errors.value.collaborators && errors.value.collaborators.includes('Unassigned')) {
          delete errors.value.collaborators;
        }
      }
      break;
    }
    case 'priority':
      if (!form.value.priority && form.value.priority !== 0) {
        errors.value.priority = 'Priority is required'
      } else if (form.value.priority < 1 || form.value.priority > 10) {
        errors.value.priority = 'Priority must be between 1 and 10'
      }
      break
  }
}

// Check if Name filled + Dates Set + Status selected
const validateForm = () => {
  errors.value = {}
  
  if (!form.value.name.trim()) {
    errors.value.name = 'Subtask name is required'
  }
  
  if (!form.value.startDate) {
    errors.value.startDate = 'Start date is required'
  }
  
  if (!form.value.endDate) {
    errors.value.endDate = 'End date is required'
  }
  
  // Use the new date validation
  if (form.value.startDate || form.value.endDate) {
    validateDates()
  }
  
  if (!form.value.status) {
    errors.value.status = 'Status is required'
  }

  // Priority validation 
  if (!form.value.priority && form.value.priority !== 0) {
    errors.value.priority = 'Priority is required'
  } else if (form.value.priority < 1 || form.value.priority > 10) {
    errors.value.priority = 'Priority must be between 1 and 10'
  }

  // Check unassigned constraint  
  const constraintError = validateUnassignedConstraint();
  if (constraintError) {
    errors.value.status = constraintError;
    errors.value.collaborators = constraintError;
  }

  // Validate max 3 attachments
  if (selectedFiles.value.length > 3) {
    errors.value.attachments = 'Maximum 3 files allowed'
  }

  return Object.keys(errors.value).length === 0
}

// Watch for changes to status or collaborators for real-time validation
watch(() => form.value.status, () => {
  const constraintError = validateUnassignedConstraint();
  if (constraintError) {
    errors.value.status = constraintError;
    errors.value.collaborators = constraintError;
  } else {
    // Clear constraint errors if valid
    if (errors.value.status && errors.value.status.includes('must have at least')) {
      delete errors.value.status;
    }
    if (errors.value.collaborators && errors.value.collaborators.includes('must have at least')) {
      delete errors.value.collaborators;
    }
  }
})

watch(() => selectedCollaborators.value.length, () => {
  const constraintError = validateUnassignedConstraint();
  if (constraintError) {
    errors.value.status = constraintError;
    errors.value.collaborators = constraintError;
  } else {
    // Clear constraint errors if valid
    if (errors.value.status && errors.value.status.includes('must have at least')) {
      delete errors.value.status;
    }
    if (errors.value.collaborators && errors.value.collaborators.includes('must have at least')) {
      delete errors.value.collaborators;
    }
  }
})

const handleSubmit = async () => {
  showSuccess.value = false
  showError.value = false
  
  if (!validateForm()) {
    return
  }
  
  isSubmitting.value = true
  
  try {
    // Get current user ID
    const currentUser = typeof window !== 'undefined' && window.sessionStorage 
      ? JSON.parse(sessionStorage.getItem('user') || '{}')
      : {};
    const userId = currentUser.id || 'unknown';
    
    let uploadedAttachments = [];
    
    // Upload files if any are selected
    if (selectedFiles.value.length > 0) {
      isUploadingFiles.value = true;
      
      // Show upload progress message
      uploadProgressMessage.value = `📤 Uploading ${selectedFiles.value.length} file(s)...`;
      successMessage.value = '';
      errorMessage.value = '';
      console.log('Upload progress message set:', uploadProgressMessage.value);
      
      try {
        // Generate a temporary subtask ID for file organization
        const tempSubtaskId = `temp_${Date.now()}`;
        console.log('Temporary subtask ID:', tempSubtaskId);
        
        uploadedAttachments = await fileUploadService.uploadMultipleSubtaskFiles(
          selectedFiles.value, 
          tempSubtaskId, 
          userId
        );
        console.log('Files uploaded successfully:', uploadedAttachments);
        
        // Show success message for file upload
        uploadProgressMessage.value = '';
        successMessage.value = `✅ ${uploadedAttachments.length} file(s) uploaded successfully!`;
        console.log('File upload success message set:', successMessage.value);
        
        // Clear success message after delay
        setTimeout(() => {
          successMessage.value = '';
        }, 3000);
      } catch (uploadError) {
        console.error('File upload failed:', uploadError);
        uploadProgressMessage.value = '';
        showError.value = true;
        errorMessage.value = `Failed to upload files: ${uploadError.message}`;
        return;
      } finally {
        isUploadingFiles.value = false;
      }
    }
    
    // Prepare subtask data
    const subtaskData = {
      name: form.value.name,
      description: form.value.description,
      start_date: form.value.startDate,
      end_date: form.value.endDate,
      status: form.value.status,
      priority: form.value.priority,
      parent_task_id: props.parentTaskId,
      project_id: props.parentProjectId,
      assigned_to: selectedCollaborators.value.map(collab => collab.id),
      attachments: uploadedAttachments,
      owner: form.value.owner
    };
    
    console.log('Creating subtask with data:', subtaskData);
    
    // Create subtask via API
    const response = await taskService.createSubtask(subtaskData);
    console.log('Subtask created successfully:', response);
    
    // Show success message
    successMessage.value = `✅ Subtask "${form.value.name}" created successfully!`;
    uploadProgressMessage.value = '';
    showSuccess.value = true
    emit('subtask-created')
    
    // FORM RESETS
    form.value = {
      name: '',
      description: '',
      startDate: '',
      endDate: '',
      status: '',
      priority: 5
    }
    selectedCollaborators.value = []
    selectedFiles.value = []
    if (fileInput.value) {
      fileInput.value.value = ''
    }
    
    setTimeout(() => {
      showSuccess.value = false
      successMessage.value = ''
    }, 3000)
    
  } catch (error) {
    console.error('=== ERROR CREATING SUBTASK ===');
    console.error('Error details:', error);
    console.error('Error message:', error.message);
    console.error('Error response:', error.response);
    console.error('Error status:', error.response?.status);
    console.error('Error data:', error.response?.data);
    
    // Show error message
    let errorMsg = 'Failed to create subtask. Please try again.';
    if (error.response?.data?.error) {
      errorMsg = error.response.data.error;
    } else if (error.message) {
      errorMsg = error.message;
    }
    
    successMessage.value = '';
    uploadProgressMessage.value = '';
    showError.value = true
    errorMessage.value = `❌ ${errorMsg}`;
  } finally {
    isSubmitting.value = false
    isUploadingFiles.value = false
  }
}
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

.loading-state {
  text-align: center;
  padding: 40px 20px;
  color: #666666;
  font-size: 16px;
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

.readonly-input,
.form-input.readonly {
  background-color: #f8f9fa;
  color: #6c757d;
  cursor: not-allowed;
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

/* Priority Input Styling */
.priority-input {
  max-width: 200px;
}

.helper-text-inline {
  font-size: 11px;
  font-weight: 400;
  color: #6b7280;
  font-style: italic;
  margin-left: 8px;
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

.file-upload-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-input {
  display: none;
}

.file-upload-label {
  background-color: #f5f5f5;
  color: #333333;
  padding: 12px 20px;
  border: 1px solid #d1d1d1;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s ease;
}

.file-upload-label:hover {
  background-color: #e5e5e5;
}

.file-status {
  font-size: 14px;
  color: #888888;
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

.remove-file-btn {
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s ease;
}

.remove-file-btn:hover {
  background-color: #c82333;
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

.success-message {
  margin-top: 16px;
  padding: 12px 16px;
  background-color: #d4edda;
  border: 1px solid #c3e6cb;
  color: #155724;
  border-radius: 6px;
}

.error-message-block {
  margin-top: 16px;
  padding: 12px 16px;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  color: #721c24;
  border-radius: 6px;
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

.date-constraint-info {
  font-size: 12px;
  color: #666666;
  margin-top: 4px;
  font-style: italic;
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
  
  .remove-file-btn {
    align-self: flex-end;
  }
}
</style>