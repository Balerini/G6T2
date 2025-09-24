<template>
  <div class="subtask-form-container">
    <h2 class="form-title">Create New Subtask</h2>
    
    <form class="subtask-form" @submit.prevent="handleSubmit" novalidate>
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

          <!-- Add Collaborator dropdown -->
          <select 
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

      <!-- INPUT DEADLINE + DATE RESTRICTION -->
      <div class="form-group">
        <label for="deadline" class="form-label">
          Deadline *
        </label>
        <input
          id="deadline"
          v-model="form.deadline"
          type="date"
          required
          :min="today" 
          class="form-input"
          :class="{ 'error': errors.deadline }"
        />
        <span v-if="errors.deadline" class="error-message">{{ errors.deadline }}</span>
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
import { ref, computed } from 'vue'

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
  }
})

// Emits for notifying parent component
const emit = defineEmits(['subtask-created', 'cancel'])

const form = ref({
  name: '',
  deadline: '',
  status: ''
})

const errors = ref({})
const isSubmitting = ref(false)
const showSuccess = ref(false)
const showError = ref(false)
const errorMessage = ref('')

// Collaborators data
const selectedCollaborators = ref([])
const selectedCollaboratorId = ref('')
const currentUserRank = ref(3) 

// Mock Data (Replace with API call ltr)
const availableStaff = ref([
  { id: 1, name: 'John Doe', department: 'Engineering', rank: 4 },
  { id: 2, name: 'Jane Smith', department: 'Marketing', rank: 4 },
  { id: 3, name: 'Bob Wilson', department: 'Engineering', rank: 3 },
  { id: 4, name: 'Alice Brown', department: 'HR', rank: 2 },
  { id: 5, name: 'Charlie Davis', department: 'Finance', rank: 4 },
])

// File Attachments Data
const selectedFiles = ref([])
const fileInput = ref(null)

// DATE FORMAT (so date input don't select beyond past date)
const today = computed(() => {
  return new Date().toISOString().split('T')[0]
})

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

// Check if Name filled + Deadline Set (not past) + Status selected
const validateForm = () => {
  errors.value = {}
  
  if (!form.value.name.trim()) {
    errors.value.name = 'Subtask name is required'
  }
  
  if (!form.value.deadline) {
    errors.value.deadline = 'Deadline is required'
  } else if (new Date(form.value.deadline) < new Date()) {
    errors.value.deadline = 'Deadline cannot be in the past'
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
      deadline: '',
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
.form-select {
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
.form-select:focus {
  outline: none;
  border-color: #000000;
  box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.1);
}

.form-input.error,
.form-select.error {
  border-color: #dc3545;
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
</style>