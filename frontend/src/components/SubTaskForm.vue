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

// DATE FORMAT (so date input don't select beyond past date)
const today = computed(() => {
  return new Date().toISOString().split('T')[0]
})

// CHECK IF Name filled + Deadline Set (not past) + Status selected
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