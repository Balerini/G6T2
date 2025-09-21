<template>
  <form class="task-form" @submit.prevent="handleSubmit">
    <!-- Task Name -->
    <div class="form-group">
      <label class="form-label" for="taskName">Task Name *</label>
      <input
        id="taskName"
        v-model="formData.taskName"
        type="text"
        class="form-input"
        placeholder="Enter task name"
        required
      />
    </div>

    <!-- Subtasks Checkbox -->
    <div class="form-group checkbox-group">
      <label class="checkbox-container">
        <input 
          type="checkbox" 
          class="checkbox-input"
          v-model="formData.hasSubtasks"
        />
        <span class="checkbox-checkmark"></span>
        <span class="checkbox-label">Subtasks will have respective inputs</span>
      </label>
    </div>

    <!-- Deadline -->
    <div class="form-group">
      <label class="form-label" for="deadline">Deadline *</label>
      <input
        id="deadline"
        v-model="formData.deadline"
        type="date"
        class="form-input"
        required
      />
    </div>

    <!-- Collaborators -->
    <div class="form-group">
      <label class="form-label" for="collaborators">Collaborators (10 max)</label>
      <input
        id="collaborators"
        v-model="collaboratorInput"
        type="text"
        class="form-input"
        placeholder="Enter staff member name"
        @keyup.enter="addCollaborator"
      />
      <div class="collaborator-tags">
        <span 
          v-for="(collaborator, index) in formData.collaborators" 
          :key="index"
          class="collaborator-tag"
        >
          {{ collaborator }}
          <button type="button" class="remove-tag" @click="removeCollaborator(index)">×</button>
        </span>
      </div>
    </div>

    <!-- Attachments -->
    <div class="form-group">
      <label class="form-label" for="attachments">Attachments (up to 3)</label>
      <div class="file-upload-container">
        <input
          id="attachments"
          type="file"
          class="file-input"
          multiple
          accept=".pdf,.doc,.docx,.jpg,.png"
          @change="handleFileUpload"
          ref="fileInput"
        />
        <label for="attachments" class="file-upload-label">
          Choose Files
        </label>
        <span class="file-status">
          {{ formData.attachments.length > 0 ? `${formData.attachments.length} file(s) selected` : 'No file chosen' }}
        </span>
      </div>
    </div>

    <!-- Status -->
    <div class="form-group">
      <label class="form-label" for="status">Status *</label>
      <select id="status" v-model="formData.status" class="form-select" required>
        <option value="" disabled>Select status</option>
        <option value="unassigned">Unassigned</option>
        <option value="ongoing">Ongoing</option>
        <option value="under-review">Under Review</option>
        <option value="completed">Completed</option>
      </select>
    </div>

    <!-- Form Actions -->
    <div class="form-actions">
      <button type="button" class="btn btn-cancel" @click="$emit('cancel')" :disabled="isSubmitting">Cancel</button>
      <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
        {{ isSubmitting ? 'Creating...' : 'Create Task' }}
      </button>
    </div>
  </form>
</template>

<script>
import { ref, reactive } from 'vue';
import { db } from '@/firebase';
import { collection, addDoc, serverTimestamp } from 'firebase/firestore';

export default {
  name: "TaskForm",
  emits: ['submit', 'cancel', 'success', 'error'],
  setup(props, { emit }) {
    const isSubmitting = ref(false);
    const collaboratorInput = ref('');
    const fileInput = ref(null);

    const formData = reactive({
      taskName: '',
      hasSubtasks: false,
      deadline: '',
      collaborators: [],
      attachments: [],
      status: ''
    });

    const addCollaborator = () => {
      const name = collaboratorInput.value.trim();
      if (name && formData.collaborators.length < 10 && !formData.collaborators.includes(name)) {
        formData.collaborators.push(name);
        collaboratorInput.value = '';
      }
    };

    const removeCollaborator = (index) => {
      formData.collaborators.splice(index, 1);
    };

    const handleFileUpload = (event) => {
      const files = Array.from(event.target.files);
      if (files.length <= 3) {
        formData.attachments = files;
      } else {
        alert('Maximum 3 files allowed');
        if (fileInput.value) {
          fileInput.value.value = '';
        }
      }
    };

    const resetForm = () => {
      Object.assign(formData, {
        taskName: '',
        hasSubtasks: false,
        deadline: '',
        collaborators: [],
        attachments: [],
        status: ''
      });
      
      if (fileInput.value) {
        fileInput.value.value = '';
      }
      
      collaboratorInput.value = '';
    };

    const handleSubmit = async () => {
      // Prevent multiple submissions
      if (isSubmitting.value) {
        return;
      }
      
      // Set loading state
      isSubmitting.value = true;
      
      try {
        // Validate required fields
        if (!formData.taskName.trim()) {
          throw new Error('Task name is required');
        }
        if (!formData.deadline) {
          throw new Error('Deadline is required');
        }
        if (!formData.status) {
          throw new Error('Status is required');
        }

        // Prepare task data for Firestore
        const taskData = {
          taskName: formData.taskName.trim(),
          hasSubtasks: formData.hasSubtasks,
          deadline: formData.deadline,
          collaborators: [...formData.collaborators], // Create a copy
          status: formData.status,
          createdAt: serverTimestamp(),
          updatedAt: serverTimestamp(),
          attachmentNames: formData.attachments.map(file => file.name)
        };

        console.log('Submitting task data:', taskData);

        // Add document to Firestore
        const docRef = await addDoc(collection(db, 'tasks'), taskData);
        
        console.log('Task created successfully with ID:', docRef.id);
        
        // Create response object with the ID
        const responseData = {
          id: docRef.id,
          ...taskData
        };
        
        // Reset form first
        resetForm();
        
        // Emit success event
        emit('success', responseData);
        
      } catch (error) {
        console.error('Error creating task:', error);
        
        // Emit error event with proper error message
        const errorMessage = error.message || 'An unexpected error occurred';
        emit('error', errorMessage);
        
      } finally {
        // Always reset loading state
        isSubmitting.value = false;
        console.log('Form submission completed, loading state reset');
      }
    };

    return {
      formData,
      collaboratorInput,
      fileInput,
      isSubmitting,
      addCollaborator,
      removeCollaborator,
      handleFileUpload,
      handleSubmit
    };
  }
};
</script>

<style scoped>
/* Keep existing styles */
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

.form-input::placeholder {
  color: #888888;
}

/* Checkbox Styling */
.checkbox-group {
  margin: 8px 0;
}

.checkbox-container {
  display: flex;
  align-items: center;
  cursor: pointer;
  gap: 12px;
}

.checkbox-input {
  width: 18px;
  height: 18px;
  margin: 0;
  cursor: pointer;
}

.checkbox-label {
  font-size: 14px;
  color: #333333;
  cursor: pointer;
}

/* Collaborator Tags */
.collaborator-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.collaborator-tag {
  display: inline-flex;
  align-items: center;
  background-color: #f5f5f5;
  color: #333333;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 14px;
  gap: 8px;
}

.remove-tag {
  background: none;
  border: none;
  color: #666666;
  font-size: 16px;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.remove-tag:hover {
  color: #000000;
}

/* File Upload */
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

.btn-cancel:hover {
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
