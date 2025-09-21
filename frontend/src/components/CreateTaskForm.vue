<template>
  <form class="task-form" @submit.prevent="handleSubmit">
    <!-- Project ID -->
    <div class="form-group">
      <label class="form-label" for="projId">Project ID *</label>
      <input
        id="projId"
        v-model="formData.proj_ID"
        type="text"
        class="form-input"
        placeholder="Enter project ID"
        required
      />
    </div>

    <!-- Task ID -->
    <div class="form-group">
      <label class="form-label" for="taskId">Task ID *</label>
      <input
        id="taskId"
        v-model="formData.task_ID"
        type="text"
        class="form-input"
        placeholder="Enter task ID"
        required
      />
    </div>

    <!-- Task Name -->
    <div class="form-group">
      <label class="form-label" for="taskName">Task Name *</label>
      <input
        id="taskName"
        v-model="formData.task_name"
        type="text"
        class="form-input"
        placeholder="Enter task name"
        required
      />
    </div>

    <!-- Task Description -->
    <div class="form-group">
      <label class="form-label" for="taskDesc">Task Description</label>
      <textarea
        id="taskDesc"
        v-model="formData.task_desc"
        class="form-textarea"
        placeholder="Enter task description"
        rows="4"
      ></textarea>
    </div>

    <!-- Start Date -->
    <div class="form-group">
      <label class="form-label" for="startDate">Start Date *</label>
      <input
        id="startDate"
        v-model="formData.start_date"
        type="date"
        class="form-input"
        required
        @change="validateDates"
      />
    </div>

    <!-- End Date -->
    <div class="form-group">
      <label class="form-label" for="endDate">End Date *</label>
      <input
        id="endDate"
        v-model="formData.end_date"
        type="date"
        class="form-input"
        required
        :min="formData.start_date"
        @change="validateDates"
      />
      <span v-if="dateValidationError" class="error-message">
        {{ dateValidationError }}
      </span>
    </div>

    <!-- Created By (Auto-populated, read-only) -->
    <div class="form-group">
      <label class="form-label" for="createdBy">Created By</label>
      <input
        id="createdBy"
        v-model="formData.created_by"
        type="text"
        class="form-input readonly-input"
        readonly
        placeholder="Auto-populated from current user"
      />
    </div>

    <!-- Assigned To -->
    <div class="form-group">
      <label class="form-label" for="assignedTo">Assigned To</label>
      <input
        id="assignedTo"
        v-model="assignedToInput"
        type="text"
        class="form-input"
        placeholder="Enter assignee name"
        @keyup.enter="addAssignee"
      />
      <div class="assignee-tags" v-if="formData.assigned_to.length > 0">
        <span 
          v-for="(assignee, index) in formData.assigned_to" 
          :key="index"
          class="assignee-tag"
        >
          {{ assignee }}
          <button type="button" class="remove-tag" @click="removeAssignee(index)">×</button>
        </span>
      </div>
    </div>

    <!-- Attachments -->
    <div class="form-group">
      <label class="form-label" for="attachments">Attachments</label>
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
          {{ formData.attachments.length > 0 ? `${formData.attachments.length} file(s) selected` : 'No file chosen' }}
        </span>
      </div>
      
      <!-- File Preview List -->
      <div class="file-preview-container" v-if="formData.attachments.length > 0">
        <div 
          v-for="(file, index) in formData.attachments" 
          :key="index"
          class="file-preview-item"
        >
          <div class="file-info">
            <span class="file-name">{{ file.name }}</span>
            <span class="file-size">({{ formatFileSize(file.size) }})</span>
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
    </div>

    <!-- Task Status -->
    <div class="form-group">
      <label class="form-label" for="taskStatus">Task Status *</label>
      <select id="taskStatus" v-model="formData.task_status" class="form-select" required>
        <option value="" disabled>Select status</option>
        <option value="not_started">Not Started</option>
        <option value="in_progress">In Progress</option>
        <option value="on_hold">On Hold</option>
        <option value="completed">Completed</option>
        <option value="cancelled">Cancelled</option>
      </select>
    </div>

    <!-- Form Actions -->
    <div class="form-actions">
      <button type="button" class="btn btn-cancel" @click="$emit('cancel')" :disabled="isSubmitting">
        Cancel
      </button>
      <button type="submit" class="btn btn-primary" :disabled="isSubmitting || !!dateValidationError">
        {{ isSubmitting ? 'Creating...' : 'Create Task' }}
      </button>
    </div>
  </form>
</template>

<script>
import { ref, reactive, onMounted } from 'vue';
import { db } from '@/firebase';
import { collection, addDoc, Timestamp } from 'firebase/firestore';
// Import your authentication service/composable here
// import { useAuth } from '@/composables/useAuth';

export default {
  name: "TaskForm",
  emits: ['submit', 'cancel', 'success', 'error'],
  setup(props, { emit }) {
    const isSubmitting = ref(false);
    const assignedToInput = ref('');
    const fileInput = ref(null);
    const dateValidationError = ref('');
    
    // Uncomment and use your auth service
    // const { currentUser } = useAuth();

    const formData = reactive({
      proj_ID: '',
      task_ID: '',
      task_name: '',
      task_desc: '',
      start_date: '',
      end_date: '',
      created_by: '', // Will be auto-populated
      assigned_to: [],
      attachments: [],
      task_status: ''
    });

    // Auto-populate created_by on component mount
    onMounted(() => {
      // Replace this with your actual current user logic
      // formData.created_by = currentUser.value?.name || currentUser.value?.email || 'Current User';
      
      // For demo purposes, using a placeholder
      formData.created_by = 'Current User'; // Replace with actual user data
    });

    const addAssignee = () => {
      const name = assignedToInput.value.trim();
      if (name && !formData.assigned_to.includes(name)) {
        formData.assigned_to.push(name);
        assignedToInput.value = '';
      }
    };

    const removeAssignee = (index) => {
      formData.assigned_to.splice(index, 1);
    };

    const handleFileUpload = (event) => {
      const files = Array.from(event.target.files);
      // Add new files to existing ones
      formData.attachments = [...formData.attachments, ...files];
    };

    const removeFile = (index) => {
      formData.attachments.splice(index, 1);
      
      // Reset file input if no files remain
      if (formData.attachments.length === 0 && fileInput.value) {
        fileInput.value.value = '';
      }
    };

    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes';
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    const validateDates = () => {
      dateValidationError.value = '';
      
      if (formData.start_date && formData.end_date) {
        const startDate = new Date(formData.start_date);
        const endDate = new Date(formData.end_date);
        
        if (endDate <= startDate) {
          dateValidationError.value = 'End date must be after start date';
          return false;
        }
      }
      return true;
    };

    const resetForm = () => {
      Object.assign(formData, {
        proj_ID: '',
        task_ID: '',
        task_name: '',
        task_desc: '',
        start_date: '',
        end_date: '',
        created_by: '', // Will be auto-populated again
        assigned_to: [],
        attachments: [],
        task_status: ''
      });
      
      if (fileInput.value) {
        fileInput.value.value = '';
      }
      
      assignedToInput.value = '';
      dateValidationError.value = '';
      
      // Re-populate created_by
      // formData.created_by = currentUser.value?.name || currentUser.value?.email || 'Current User';
      formData.created_by = 'Current User'; // Replace with actual user data
    };

    const handleSubmit = async () => {
      if (isSubmitting.value) {
        return;
      }
      
      // Validate dates before submission
      if (!validateDates()) {
        return;
      }
      
      isSubmitting.value = true;
      
      try {
        // Validate required fields
        if (!formData.proj_ID.trim()) {
          throw new Error('Project ID is required');
        }
        if (!formData.task_ID.trim()) {
          throw new Error('Task ID is required');
        }
        if (!formData.task_name.trim()) {
          throw new Error('Task name is required');
        }
        if (!formData.start_date) {
          throw new Error('Start date is required');
        }
        if (!formData.end_date) {
          throw new Error('End date is required');
        }
        if (!formData.task_status) {
          throw new Error('Task status is required');
        }

        // Convert datetime strings to Firestore Timestamps
        const startTimestamp = Timestamp.fromDate(new Date(formData.start_date + 'T00:00:00'));
        const endTimestamp = Timestamp.fromDate(new Date(formData.end_date + 'T23:59:59'));

        // Prepare task data for Firestore
        const taskData = {
          proj_ID: formData.proj_ID.trim(),
          task_ID: formData.task_ID.trim(),
          task_name: formData.task_name.trim(),
          task_desc: formData.task_desc.trim(),
          start_date: startTimestamp,
          end_date: endTimestamp,
          created_by: formData.created_by,
          assigned_to: [...formData.assigned_to],
          attachments: formData.attachments.map(file => ({
            name: file.name,
            size: file.size,
            type: file.type
          })),
          task_status: formData.task_status,
          createdAt: Timestamp.now(),
          updatedAt: Timestamp.now()
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
        
        const errorMessage = error.message || 'An unexpected error occurred';
        emit('error', errorMessage);
        
      } finally {
        isSubmitting.value = false;
        console.log('Form submission completed, loading state reset');
      }
    };

    return {
      formData,
      assignedToInput,
      fileInput,
      isSubmitting,
      dateValidationError,
      addAssignee,
      removeAssignee,
      handleFileUpload,
      removeFile,
      formatFileSize,
      validateDates,
      handleSubmit
    };
  }
};
</script>

<style scoped>
/* Keep existing styles and add new ones */
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

.readonly-input {
  background-color: #f8f9fa;
  color: #6c757d;
  cursor: not-allowed;
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
