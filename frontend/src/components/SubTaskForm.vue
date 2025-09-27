<template>
  <div class="subtask-form-container">
    <h2 class="form-title">Create New Subtask</h2>
    
    <!-- Loading state -->
    <div v-if="isLoadingParentData" class="loading-state">
      <p>Loading parent task data...</p>
    </div>
    
    <!-- Form -->
    <form v-else class="subtask-form" @submit.prevent="handleSubmit" novalidate>
      <!-- PROJECT INFO (Pre-filled, read-only) -->
      <div class="form-group">
        <label class="form-label">Project</label>
        <input
          :value="parentProject?.proj_name || 'Loading...'"
          type="text"
          readonly
          class="form-input readonly"
        />
      </div>

      <!-- INPUT SUBTASK NAME -->
      <div class="form-group">
        <label for="name" class="form-label">
          Subtask Name *
        </label>
        <input
          id="name"
          v-model="form.name"
          type="text"
          required
          class="form-input"
          :class="{ 'error': errors.name }" 
        />
        <span v-if="errors.name" class="error-message">{{ errors.name }}</span>
      </div>

      <!-- SUBTASK DESCRIPTION -->
      <div class="form-group">
        <label for="description" class="form-label">
          Description
        </label>
        <textarea
          id="description"
          v-model="form.description"
          class="form-input"
          rows="3"
          :class="{ 'error': errors.description }"
        ></textarea>
        <span v-if="errors.description" class="error-message">{{ errors.description }}</span>
      </div>

      <div class="form-group">
        <label class="form-label">
          Collaborators (Optional - Max 10)
        </label>
        <div> 
          <div class="assignee-tags" v-if="selectedCollaborators.length > 0">
            <span
              v-for="collaborator in selectedCollaborators"
              :key="collaborator.id"
              class="assignee-tag"
            >
              {{ collaborator.name }} ({{ collaborator.department }})
              <button
                type="button"
                @click="removeCollaborator(collaborator.id)"
                class="remove-tag"
              >
                ×
              </button>
            </span>
          </div>

          <!-- Show message when no collaborators are available -->
          <div v-if="availableStaff.length === 0" class="no-collaborators-message">
            No collaborators are assigned to the parent task. Please assign collaborators to the main task first.
          </div>

          <!-- Add collaborator dropdown -->
          <select 
            v-else
            v-model="selectedCollaboratorId"
            @change="addCollaborator"
            :disabled="selectedCollaborators.length >= 10"
            class="form-select"
            :class="{
              'error': errors.collaborators,
            }"
          >
            <option value="">Select a collaborator to add</option>
            <option 
              v-for="staff in availableStaff" 
              :key="staff.id" 
              :value="staff.id"
              :disabled="!canAssignTo(staff)"
            >
              {{ staff.name }} - {{ staff.department }} {{ !canAssignTo(staff) ? '(Cannot assign - lower rank)' : '' }}
            </option>
          </select>
          <div v-if="selectedCollaborators.length > 0" class="status-message info">{{ selectedCollaborators.length }}/10 collaborators selected</div>
        </div>
        <span v-if="errors.collaborators" class="error-message">{{ errors.collaborators }}</span>
      </div>

      <!-- START DATE -->
      <div class="form-group">
        <label for="startDate" class="form-label">
          Start Date *
        </label>
        <input
          id="startDate"
          v-model="form.startDate"
          type="date"
          required
          :min="getSubtaskMinStartDate()"
          :max="getSubtaskMaxEndDate()"
          class="form-input"
          :class="{ 'error': errors.startDate }"
          @change="validateDates()"
          @blur="validateForm()"
        />
        <span v-if="errors.startDate" class="error-message">{{ errors.startDate }}</span>
        <div v-if="getDateConstraintInfo()" class="date-constraint-info">
          {{ getDateConstraintInfo() }}
        </div>
      </div>

      <!-- END DATE -->
      <div class="form-group">
        <label for="endDate" class="form-label">
          End Date *
        </label>
        <input
          id="endDate"
          v-model="form.endDate"
          type="date"
          required
          :min="form.startDate || getSubtaskMinStartDate()"
          :max="getSubtaskMaxEndDate()"
          class="form-input"
          :class="{ 'error': errors.endDate }"
          @change="validateDates()"
          @blur="validateForm()"
        />
        <span v-if="errors.endDate" class="error-message">{{ errors.endDate }}</span>
      </div>

      <!-- FILE ATTACHMENTS -->
      <div class="form-group">
        <label class="form-label">
          Attachments (Optional - Max 3 files)
        </label>
        <div class="file-upload-container">
          <input
          type="file"
          ref="fileInput"
          @change="handleFileUpload"
          multiple
          accept=".pdf,.doc,.docx,.jpg,.png,.txt"
          class="file-input"
          id="attachments"
        />
        <label for="attachments" class="file-upload-label">
          Choose Files
        </label>
        <span class="file-status">
          {{ selectedFiles.length > 0 ? `${selectedFiles.length} file(s) selected` : 'No file chosen' }}
        </span>
      </div>

      <!-- File Preview List -->

      <div class="file-preview-container" v-if="selectedFiles.length > 0 ">
        <div
          v-for="(file, index) in selectedFiles" 
          :key="index"
          class="file-preview-item"
        >
          <div class="file-info">
            <span class="file-name">{{ file.name }}</span>
            <span class="file-size">({{ formatFileSize(file.size) }})</span>
          </div>
          <button 
            type="button" 
            @click="removeFile(index)" 
            class="remove-file-btn"
            title="Remove file"
          >
            ×
          </button>
        </div>
      </div>

        <span v-if="errors.attachments" class="error-message">{{ errors.attachments }}</span>

      </div>

      <!-- DROPDOWN FOR STATUS SELECTION -->
      <div class="form-group">
        <label for="status" class="form-label">
          Status *
        </label>
        <select
          id="status"
          v-model="form.status"
          required
          class="form-select"
          :class="{ 'error': errors.status }"
        >
          <option value="">Select status</option>
          <option value="Unassigned">Unassigned</option>
          <option value="Ongoing">Ongoing</option>
          <option value="Under Review">Under Review</option>
          <option value="Completed">Completed</option>
        </select>
        <span v-if="errors.status" class="error-message">{{ errors.status }}</span>
      </div>

      <!-- SUBMIT BUTTON, DISABLE WHEN SUBMITTING, CHANGE TO CREATING WHEN SUBMITTING -->
      <div class="form-actions">
        <button type="button" class="btn btn-cancel" @click="$emit('cancel')" :disabled="isSubmitting">
          Cancel
        </button>
        <button
          type="submit"
          :disabled="isSubmitting"
          class="btn btn-primary"
        >
          {{ isSubmitting ? 'Creating...' : 'Create Subtask' }}
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
import { ref, computed, onMounted } from 'vue'
import { taskService } from '@/services/taskService'

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
const emit = defineEmits(['subtask-created', 'cancel'])

const form = ref({
  name: '',
  description: '',
  startDate: '',
  endDate: '',
  status: ''
})

const errors = ref({})
const isSubmitting = ref(false)
const showSuccess = ref(false)
const showError = ref(false)
const errorMessage = ref('')

// Parent task and project data
const parentTask = ref(null)
const parentProject = ref(null)
const isLoadingParentData = ref(true)

// Collaborators data
const selectedCollaborators = ref([])
const selectedCollaboratorId = ref('')
const currentUserRank = ref(3) 

// Use prop instead of mock data    
const availableStaff = computed(() => {
  if (!props.availableCollaborators || props.availableCollaborators.length === 0) {
    return []
  }
  
  return props.availableCollaborators.map(collaborator => ({
    id: collaborator.id,
    name: collaborator.name,
    department: collaborator.department || 'Unknown',
    rank: collaborator.rank || 3
  }))
})

const getSubtaskMinStartDate = () => {
  const today = new Date().toISOString().split('T')[0]
  
  // Priority 1: Task dates (if both exist)
  if (parentTask.value?.start_date) {
    const taskStartDate = new Date(parentTask.value.start_date).toISOString().split('T')[0]
    return taskStartDate > today ? taskStartDate : today
  }
  
  // Priority 2: Project dates (if task dates don't exist)
  if (parentProject.value?.start_date) {
    const projectStartDate = new Date(parentProject.value.start_date).toISOString().split('T')[0]
    return projectStartDate > today ? projectStartDate : today
  }
  
  // Priority 3: Just today (if no project/task dates)
  return today
}

// Get maximum end date for subtask
const getSubtaskMaxEndDate = () => {
  // Priority 1: Task end date (if exists)
  if (parentTask.value?.end_date) {
    return new Date(parentTask.value.end_date).toISOString().split('T')[0]
  }
  
  // Priority 2: Project end date (if task end date doesn't exist)
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
// Validate dates with cascading logic
const validateDates = () => {
  // Clear previous date errors
  if (errors.value.startDate) delete errors.value.startDate
  if (errors.value.endDate) delete errors.value.endDate
  
  // Validate start date
  if (form.value.startDate) {
    const startDate = new Date(form.value.startDate)
    
    // Create today's date for comparison - more explicit usage
    const todayDate = new Date()
    todayDate.setHours(0, 0, 0, 0)
    
    // Cannot be in the past
    if (startDate < todayDate) {
      errors.value.startDate = 'Start date cannot be in the past'
      return
    }
    
    // Check task constraints first
    if (parentTask.value?.start_date) {
      const taskStartDate = new Date(parentTask.value.start_date)
      if (startDate < taskStartDate) {
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
      if (startDate > taskEndDate) {
        const formattedDate = new Date(parentTask.value.end_date).toLocaleDateString('en-SG', {
          day: '2-digit',
          month: 'short',
          year: 'numeric'
        })
        errors.value.startDate = `Start date cannot be after task end date (${formattedDate})`
        return
      }
    }
    
    // If no task constraints, check project constraints
    if (!parentTask.value?.start_date && parentProject.value?.start_date) {
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
    
    if (!parentTask.value?.end_date && parentProject.value?.end_date) {
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
      if (endDate > taskEndDate) {
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
      if (endDate > projectEndDate) {
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
    
    // Load parent task data
    const taskData = await taskService.getTaskById(props.parentTaskId);
    parentTask.value = taskData;
    
    // Load parent project data
    const projectData = await taskService.getProjectById(props.parentProjectId);
    parentProject.value = projectData;
    
    // Pre-fill form with parent task data only if parent task has hasSubtasks: true
    if (parentTask.value) {
      // Check if parent task was marked to have subtasks with pre-filled details
      if (parentTask.value.hasSubtasks === true) {
        // Don't pre-fill the subtask name and description - let user enter unique values
        form.value.name = '';
        form.value.description = '';
        form.value.startDate = parentTask.value.start_date ? parentTask.value.start_date.split('T')[0] : '';
        form.value.endDate = parentTask.value.end_date ? parentTask.value.end_date.split('T')[0] : '';
        form.value.status = parentTask.value.task_status || '';
        
        // Pre-fill collaborators from parent task
        if (parentTask.value.assigned_to && parentTask.value.assigned_to.length > 0) {
          selectedCollaborators.value = parentTask.value.assigned_to.map(collaborator => ({
            id: collaborator.id || collaborator,
            name: collaborator.name || collaborator,
            department: collaborator.department || 'Unknown',
            rank: collaborator.rank || 3
          }));
        }
      } else {
        // If checkbox was not ticked, don't pre-fill anything - start with empty form
        form.value.name = '';
        form.value.description = '';
        form.value.startDate = '';
        form.value.endDate = '';
        form.value.status = '';
        selectedCollaborators.value = [];
      }
    }
    
  } catch (error) {
    console.error('Error loading parent task data:', error);
    errorMessage.value = 'Failed to load parent task data';
    showError.value = true;
  } finally {
    isLoadingParentData.value = false;
  }
}

// Initialize on component mount
onMounted(() => {
  loadParentTaskData();
});

// File Attachments Data
const selectedFiles = ref([])
const fileInput = ref(null)

// Check if Current user can assign tasks to this staff member
const canAssignTo = (staff) => {
  return staff.rank >= currentUserRank.value
}

// Add Collaborator
const addCollaborator = () => {
  if (!selectedCollaboratorId.value) return

  // check if already at max limit
  if (selectedCollaborators.value.length >= 10) {
    errors.value.collaborators = 'Maximum 10 collaborators allowed'
    return
  } 

  const staff = availableStaff.value.find(s => s.id === parseInt(selectedCollaboratorId.value))
  if (staff && !selectedCollaborators.value.find(c => c.id === staff.id)){
    selectedCollaborators.value.push(staff)
    errors.value.collaborators = ''
  }
  selectedCollaboratorId.value = ''
}

// Remove Collaborator
const removeCollaborator = (CollaboratorId) => {
  selectedCollaborators.value = selectedCollaborators.value.filter(c => c.id !== CollaboratorId)
}

// Handle file upload
const handleFileUpload = (event) => {
  const files = Array.from(event.target.files)
  
  if (files.length + selectedFiles.value.length > 3) {
    errors.value.attachments = 'Maximum 3 files allowed'
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

  // Validate max 10 collaborators   
  if (selectedCollaborators.value.length > 10) {
    errors.value.collaborators = 'Maximum 10 collaborators allowed'
  }

  // Validate max 3 attachments
  if (selectedFiles.value.length > 3) {
    errors.value.attachments = 'Maximum 3 files allowed'
  }

  return Object.keys(errors.value).length === 0
}

const handleSubmit = async () => {
  showSuccess.value = false
  showError.value = false
  
  if (!validateForm()) {
    return
  }
  
  isSubmitting.value = true
  
  try {
    // API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // SUCCESS MSG
    showSuccess.value = true

    emit('subtask-created')
    
    // FORM RESETS
    form.value = {
      name: '',
      description: '',
      startDate: '',
      endDate: '',
      status: ''
    }
    selectedCollaborators.value = []
    selectedFiles.value = []
    if (fileInput.value) {
      fileInput.value.value = ''
    }

    
    setTimeout(() => {
      showSuccess.value = false
    }, 3000)
    
  } catch (error) {
    showError.value = true
    errorMessage.value = 'Failed to create subtask. Please try again.'
  } finally {
    isSubmitting.value = false
  }
}
</script>



<style scoped>
.subtask-form-container {
  padding: 24px;
}

.form-title {
  font-size: 24px;
  font-weight: 700;
  color: #000000;
  margin-bottom: 24px;
}

.loading-state {
  text-align: center;
  padding: 40px 20px;
  color: #666666;
  font-size: 16px;
}

.subtask-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
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
textarea {
  width: 100%;
  padding: 12px 16px;
  font-size: 16px;
  color: #000000;
  background-color: #ffffff;
  border: 1px solid #d1d1d1;
  border-radius: 6px;
  transition: all 0.2s ease;
  box-sizing: border-box;
  font-family: inherit;
}

textarea {
  resize: vertical;
  min-height: 80px;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: #000000;
  box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.1);
}

.form-input.error,
.form-select.error {
  border-color: #dc3545;
}

.form-input.readonly {
  background-color: #f5f5f5;
  color: #666666;
  cursor: not-allowed;
}

.form-input::placeholder {
  color: #888888;
}

.error-message {
  color: #dc3545;
  font-size: 12px;
  margin-top: 4px;
}

.assignee-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.assignee-tag {
  display: inline-flex;
  align-items: center;
  background-color: #e3f2fd;
  color: #1976d2;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 14px;
  border: 1px solid #bbdefb;
  gap: 8px;
}

.remove-tag {
  background: none;
  border: none;
  color: #1976d2;
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
  margin-top: 4px;
  font-size: 12px;
  padding: 4px 0;
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

.file-preview-container {
  margin-top: 12px;
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
</style>