<template>
  <div class="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
    <h2 class="text-2xl font-bold mb-6 text-gray-800">Create New Subtask</h2>
    
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <!-- INPUT SUBTASK NAME -->
      <div>
        <label for="name" class="block text-sm font-medium text-gray-700 mb-1">
          Subtask Name *
        </label>
        <input
          id="name"
          v-model="form.name"
          type="text"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          :class="{ 'border-red-500': errors.name }" 
        />
        <p v-if="errors.name" class="text-red-500 text-sm mt-1">{{ errors.name }}</p>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Collaborators (Optional - Max 10)
        </label>
        <div class="space-y-2">
          <div v-if="selectedCollaborators.length > 0" class="flex flex-wrap gap-2 mb-2">
            <span
              v-for="collaborator in selectedCollaborators"
              :key="collaborator.id"
              class="inline-flex items-center px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
            >
              {{ collaborator.name }} ({{ collaborator.department }})
              <button
                type="button"
                @click="removeCollaborator(collaborator.id)"
                class="ml-1 text-blue-600 hover:text-blue-800"
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
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            :class="{
              'border-red-500': errors.collaborators,
              'opacity-50 cursor-not-allowed': selectedCollaborators.length >= 10
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
          <p class="text-xs text-gray-500">{{ selectedCollaborators.length }}/10 collaborators selected</p>
        </div>
        <p v-if="errors.collaborators" class="text-red-500 text-sm mt-1">{{ errors.collaborators }}</p>
      </div>

      <!-- INPUT DEADLINE + DATE RESTRICTION -->
      <div>
        <label for="deadline" class="block text-sm font-medium text-gray-700 mb-1">
          Deadline *
        </label>
        <input
          id="deadline"
          v-model="form.deadline"
          type="date"
          required
          :min="today" 
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          :class="{ 'border-red-500': errors.deadline }"
        />
        <p v-if="errors.deadline" class="text-red-500 text-sm mt-1">{{ errors.deadline }}</p>
      </div>

      <!-- FILE ATTACHMENTS -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Attachments (Optional - Max 3 files)
        </label>
        <input
          type="file"
          ref="fileInput"
          @change="handleFileUpload"
          multiple
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          :class="{ 'border-red-500': errors.attachments }"
        />

        <!-- Selected Files Display -->
         <div v-if="selectedFiles.length > 0" class="mt-2 space-y-1">
          <div 
            v-for="(file, index) in selectedFiles" 
            :key="index"
            class="flex items-center justify-between text-sm bg-gray-50 p-2 rounded"
          >
            <span>{{ file.name }} ({{ formatFileSize(file.size) }})</span>
            <button 
              type="button" 
              @click="removeFile(index)" 
              class="text-red-500 hover:text-red-700"
            >
              Remove
            </button>
          </div>
        </div>
        <p class="text-xs text-gray-500 mt-1">{{ selectedFiles.length }}/3 files selected</p>
        <p v-if="errors.attachments" class="text-red-500 text-sm mt-1">{{ errors.attachments }}</p>
      </div>

      <!-- DROPDOWN FOR STATUS SELECTION -->
      <div>
        <label for="status" class="block text-sm font-medium text-gray-700 mb-1">
          Status *
        </label>
        <select
          id="status"
          v-model="form.status"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          :class="{ 'border-red-500': errors.status }"
        >
          <option value="">Select status</option>
          <option value="Unassigned">Unassigned</option>
          <option value="Ongoing">Ongoing</option>
          <option value="Under Review">Under Review</option>
          <option value="Completed">Completed</option>
        </select>
        <p v-if="errors.status" class="text-red-500 text-sm mt-1">{{ errors.status }}</p>
      </div>

      <!-- SUBMIT BUTTON, DISABLE WHEN SUBMITTING, CHANGE TO CREATING WHEN SUBMITTING -->
      <button
        type="submit"
        :disabled="isSubmitting"
        class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {{ isSubmitting ? 'Creating...' : 'Create Subtask' }}
      </button>
    </form>

    <!-- SUCCESS + ERROR MSG -->
    <div v-if="showSuccess" class="mt-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded">
      Subtask created successfully!
    </div>

    <div v-if="showError" class="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
      {{ errorMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

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