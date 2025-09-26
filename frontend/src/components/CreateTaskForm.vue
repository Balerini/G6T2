<template>
  <form class="task-form" @submit.prevent="handleSubmit" novalidate>
    <!-- Project ID -->
    <div class="form-group">
      <label class="form-label" for="projId">
        Project 
      </label>
      
      <!-- Combined search input with dropdown for projects -->
      <div class="project-dropdown-container" :class="{ 'dropdown-open': showProjectDropdown }">
        <input
          id="projId"
          v-model="projectSearch"
          type="text"
          class="form-input"
          :placeholder="isLoadingProjects ? 'Loading projects...' : 'Search and select project...'"
          @focus="handleProjectInputFocus"
          @blur="handleProjectInputBlur"
          @input="handleProjectSearchInput"
          @keydown.enter.prevent="selectFirstProjectMatch"
          @keydown.escape="closeProjectDropdown"
          @keydown.arrow-down.prevent="navigateProjectDown"
          @keydown.arrow-up.prevent="navigateProjectUp"
          :disabled="isLoadingProjects"
        />
        
        <!-- Clear button when project is selected -->
        <div 
          v-if="isProjectSelected" 
          class="clear-selection-btn" 
          @click="clearProjectSelection"
          title="Clear selection"
        >
          ×
        </div>
        
        <!-- Dropdown icon when no project is selected -->
        <div 
          v-else
          class="dropdown-toggle-icon" 
          @click="toggleProjectDropdown"
          :class="{ 'rotated': showProjectDropdown }"
        >
          ▼
        </div>
        
        <!-- Dropdown options list -->
        <div 
          v-if="showProjectDropdown" 
          class="dropdown-list"
          @mousedown.prevent
        >
          <!-- Loading state -->
          <div v-if="isLoadingProjects" class="dropdown-item loading">
            Loading projects...
          </div>
          
          <!-- No results found -->
          <div 
            v-else-if="filteredProjects.length === 0 && projectSearch" 
            class="dropdown-item no-results"
          >
            No projects found matching "{{ projectSearch }}"
          </div>
          
          <!-- Show all projects when no search -->
          <div 
            v-else-if="filteredProjects.length === 0 && !projectSearch" 
            class="dropdown-item no-results"
          >
            No projects available
          </div>
          
          <!-- Project options -->
          <div 
            v-for="(project, index) in filteredProjects" 
            :key="project.id"
            class="dropdown-item"
            :class="{ 
              'highlighted': index === projectHighlightedIndex
            }"
            @mousedown="selectProject(project)"
            @mouseenter="projectHighlightedIndex = index"
          >
            <div class="user-info">
              <span class="user-name">{{ `${project.proj_name}` }}</span>
              <span v-if="project.name" class="user-email">{{ project.name }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Task Name -->
    <div class="form-group">
      <label class="form-label" for="taskName">Task Name *</label>
      <input
        id="taskName"
        v-model="formData.task_name"
        type="text"
        class="form-input"
        :class="{ 'error': validationErrors.task_name }"
        placeholder="Enter task name"
        @input="validateField('task_name', $event.target.value)"
        @blur="validateField('task_name', formData.task_name)"
      />
      <span v-if="validationErrors.task_name" class="error-message">
        {{ validationErrors.task_name }}
      </span>
    </div>

    <!-- Task Description -->
    <div class="form-group">
      <label class="form-label" for="taskDesc">Task Description</label>
      <textarea
        id="taskDesc"
        v-model="formData.task_desc"
        class="form-textarea"
        :class="{ 'error': validationErrors.task_desc }"
        placeholder="Enter task description (max 500 characters)"
        rows="4"
        @input="validateField('task_desc', $event.target.value)"
        @blur="validateField('task_desc', formData.task_desc)"
      ></textarea>
      <div class="char-count">
        {{ formData.task_desc.length }}/500 characters
      </div>
      <span v-if="validationErrors.task_desc" class="error-message">
        {{ validationErrors.task_desc }}
      </span>
    </div>

    <!-- Subtasks Checkbox -->
    <div class="form-group checkbox-group">
      <label class="checkbox-container">
        <input 
          type="checkbox" 
          class="checkbox-input"
          v-model="formData.hasSubtasks"
          @change="onSubtasksChange"
        />
        <span class="checkbox-checkmark"></span>
        <span class="checkbox-label">  Subtasks will have respective inputs</span>
      </label>
    </div>

    <!-- Start Date -->
    <div class="form-group">
      <label class="form-label" for="startDate">Start Date *</label>
      <input
        id="startDate"
        v-model="formData.start_date"
        type="date"
        class="form-input"
        :class="{ 'error': validationErrors.start_date }"
        :min="getCurrentDate()"
        @change="validateDates; validateField('start_date', formData.start_date)"
        @blur="validateField('start_date', formData.start_date)"
      />
      <span v-if="validationErrors.start_date" class="error-message">
        {{ validationErrors.start_date }}
      </span>
    </div>

    <!-- End Date -->
    <div class="form-group">
      <label class="form-label" for="endDate">
        End Date *
      </label>
      <input
        id="endDate"
        v-model="formData.end_date"
        type="date"
        class="form-input"
        :class="{ 'error': validationErrors.end_date }"
        :min="formData.start_date || getCurrentDate()"
        @change="validateDates; validateField('end_date', formData.end_date)"
        @blur="validateField('end_date', formData.end_date)"
      />
      <span v-if="validationErrors.end_date || dateValidationError" class="error-message">
        {{ validationErrors.end_date || dateValidationError }}
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
    <label class="form-label" for="assignedTo">
      Collaborators * ({{ formData.hasSubtasks ? '1-5' : '1-10' }} required)
    </label>
    
    <!-- Combined search input with dropdown -->
    <div class="search-dropdown-container" :class="{ 'dropdown-open': showDropdown }">
      <input
        id="assignedTo"
        v-model="userSearch"
        type="text"
        class="form-input"
        :class="{ 'error': validationErrors.collaborators }"
        :placeholder="isLoadingUsers ? 'Loading users...' : 'Search and select collaborators...'"
        @focus="handleInputFocus; validateField('collaborators', formData.assigned_to)"
        @blur="handleInputBlur"
        @input="handleSearchInput"
        @keydown.enter.prevent="selectFirstMatch"
        @keydown.escape="closeDropdown"
        @keydown.arrow-down.prevent="navigateDown"
        @keydown.arrow-up.prevent="navigateUp"
        :disabled="isAtLimit || isLoadingUsers"
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
      >
        <!-- Loading state -->
        <div v-if="isLoadingUsers" class="dropdown-item loading">
          Loading users...
        </div>
        
        <!-- No results found -->
        <div 
          v-else-if="filteredUsers.length === 0 && userSearch" 
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
          :key="user.id"
          class="dropdown-item"
          :class="{ 
            'highlighted': index === highlightedIndex,
            'selected': isUserSelected(user)
          }"
          @mousedown.prevent="selectUser(user)"
          @mouseenter="highlightedIndex = index"
        >
          <div class="user-info">
            <span class="user-name">{{ user.name }}</span>
            <span v-if="user.email" class="user-email">{{ user.email }}</span>
          </div>
          <span v-if="isUserSelected(user)" class="selected-indicator">✓</span>
        </div>
      </div>
    </div>
    
    <!-- Selected collaborators tags -->
    <div class="assignee-tags" v-if="formData.assigned_to.length > 0">
      <span 
        v-for="(assignee, index) in formData.assigned_to" 
        :key="assignee.id"
        class="assignee-tag"
      >
        {{ assignee.name }}
        <button 
          type="button" 
          class="remove-tag" 
          @click="removeAssignee(index)"
          :title="`Remove ${assignee.name}`"
        >
          ×
        </button>
      </span>
    </div>
    
    <!-- Status messages -->
    <div v-if="isAtLimit" class="status-message warning">
      Maximum number of collaborators reached ({{ formData.hasSubtasks ? '5' : '10' }})
    </div>
    
    <div v-if="formData.assigned_to.length > 0" class="status-message info">
      {{ formData.assigned_to.length }} collaborator{{ formData.assigned_to.length !== 1 ? 's' : '' }} selected
    </div>
    
    <!-- Collaborators validation error -->
    <span v-if="validationErrors.collaborators" class="error-message">
      {{ validationErrors.collaborators }}
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
      
      <!-- Attachment validation error -->
      <span v-if="validationErrors.attachments" class="error-message">
        {{ validationErrors.attachments }}
      </span>
    </div>

    <!-- Task Status -->
    <div class="form-group">
      <label class="form-label" for="taskStatus">
        Task Status *
      </label>
      <select 
        id="taskStatus" 
        v-model="formData.task_status" 
        class="form-select"
        :class="{ 'error': validationErrors.task_status }"
        @change="validateField('task_status', formData.task_status)"
        @blur="validateField('task_status', formData.task_status)"
      >
        <option value="" disabled>Select status</option>
        <option value="Not Started">Not Started</option>
        <option value="In Progress">In Progress</option>
        <option value="On Hold">On Hold</option>
        <option value="Completed">Completed</option>
        <option value="Cancelled">Cancelled</option>
      </select>
      <span v-if="validationErrors.task_status" class="error-message">
        {{ validationErrors.task_status }}
      </span>
    </div>

    <!-- Form Actions -->
    <div class="form-actions">
      <button type="button" class="btn btn-cancel" @click="$emit('cancel')" :disabled="isSubmitting">
        Cancel
      </button>
      <button type="submit" class="btn btn-primary" :disabled="isSubmitting || !isFormValid">
        {{ isSubmitting ? 'Creating...' : 'Create Task' }}
      </button>
    </div>
  </form>
</template>

<script>
import { ref, reactive, onMounted, computed, onBeforeUnmount, nextTick } from 'vue';
import { taskService } from '@/services/taskService';

export default {
  name: "TaskForm",
  emits: ['submit', 'cancel', 'success', 'error'],
  setup(props, { emit }) {
    const isSubmitting = ref(false);
    const assignedToInput = ref('');
    const fileInput = ref(null);
    const dateValidationError = ref('');
    
    // Enhanced validation state
    const validationErrors = reactive({
      task_ID: '',
      task_name: '',
      task_desc: '',
      proj_name: '',
      start_date: '',
      end_date: '',
      task_status: '',
      attachments: '',
      collaborators: ''
    });

    // Track which fields have been touched by the user
    const touchedFields = reactive({
      task_ID: false,
      task_name: false,
      task_desc: false,
      proj_name: false,
      start_date: false,
      end_date: false,
      task_status: false,
      attachments: false,
      collaborators: false
    });

    // NEW: Dropdown-related reactive data
    const users = ref([]);
    const userSearch = ref('');
    const showDropdown = ref(false);
    const isLoadingUsers = ref(false);
    const highlightedIndex = ref(-1);
    const dropdownCloseTimeout = ref(null);

    const projects = ref([]);
    const projectSearch = ref('');
    const showProjectDropdown = ref(false);
    const isLoadingProjects = ref(false); 
    const projectHighlightedIndex = ref(-1);
    const isProjectSelected = ref(false);
    const currentUserId = ref(null);

    const formData = reactive({
      proj_name: '',
      task_ID: '',
      task_name: '',
      task_desc: '',
      start_date: '',
      end_date: '',
      created_by: '',
      assigned_to: [], // This will now store user objects with id and name
      attachments: [],
      task_status: '',
      hasSubtasks: false
    });

    const filteredProjects = computed(() => {
      if (!projects.value || projects.value.length === 0) {
        return [];
      }
      
      // Don't show dropdown if project is selected
      if (isProjectSelected.value) {
        return [];
      }
      
      // If dropdown is closed, don't show results
      if (!showProjectDropdown.value) {
        return [];
      }
      
      let filtered = projects.value;
      
      if (projectSearch.value && projectSearch.value.trim()) {
        const searchTerm = projectSearch.value.toLowerCase().trim();
        
        filtered = filtered.filter(project => {
          if (!project) return false;
          
          const projName = (project.proj_name || '').toString().toLowerCase();
          const description = (project.description || '').toString().toLowerCase();
          
          return projName.includes(searchTerm) ||
                description.includes(searchTerm);
        });
      }
      
      return filtered.slice(0, 20);
    });

    const loadProjects = async () => {
      isLoadingProjects.value = true;
      try {
        projects.value = await taskService.getProjects();
      } catch (error) {
        console.error('Error loading projects:', error);
      } finally {
        isLoadingProjects.value = false;
      }
    };

    const selectProject = (project) => {
      // console.log('Selecting project:', project.proj_ID);
      
      // Set the form data
      formData.proj_name = project.proj_name;
      
      // Use proj_name instead of name
      projectSearch.value = project.proj_name;
      
      isProjectSelected.value = true;
      showProjectDropdown.value = false;
      
      // console.log('Final projectSearch.value:', projectSearch.value);
      // console.log('Final formData.proj_ID:', formData.proj_ID);
    };

    const clearProjectSelection = () => {
      isProjectSelected.value = false;
      formData.proj_name = '';
      projectSearch.value = '';
      showProjectDropdown.value = false;
    };

    const handleProjectInputFocus = () => {
      // Only show dropdown if no project is selected
      if (!isProjectSelected.value && !isLoadingProjects.value) {
        showProjectDropdown.value = true;
        projectHighlightedIndex.value = -1;
      }
      // Don't clear the text or show dropdown if project is already selected
    };

    const handleProjectSearchInput = () => {
    // Only reset selection if user actually changes the input content
    if (isProjectSelected.value && projectSearch.value !== getCurrentProjectDisplay()) {
      isProjectSelected.value = false;
      formData.proj_name = '';
      
      // Show dropdown for new search
      if (!showProjectDropdown.value) {
        showProjectDropdown.value = true;
      }
      projectHighlightedIndex.value = -1;
    } else if (!isProjectSelected.value) {
      // Show dropdown for new search when nothing is selected
      if (!showProjectDropdown.value) {
        showProjectDropdown.value = true;
      }
      projectHighlightedIndex.value = -1;
    }
  };

    // Helper function to get current project display
    const getCurrentProjectDisplay = () => {
      if (!formData.proj_name) return '';
      const selectedProject = projects.value.find(p => p.proj_name === formData.proj_name);
      if (!selectedProject) return formData.proj_name;
      
      return selectedProject.proj_name;
    };

    const toggleProjectDropdown = () => {
      showProjectDropdown.value = !showProjectDropdown.value;
    };

    const filteredUsers = computed(() => {
      let filtered = users.value.filter(user => {
        // Filter out already selected users
        const isAlreadySelected = formData.assigned_to.some(assignee => assignee.id === user.id);
        
        return !isAlreadySelected;
      });
      
      if (userSearch.value.trim()) {
        const searchTerm = userSearch.value.toLowerCase().trim();
        filtered = filtered.filter(user => 
          user.name.toLowerCase().includes(searchTerm) ||
          (user.email && user.email.toLowerCase().includes(searchTerm))
        );
      }
      
      return filtered.slice(0, 20);
    });

    const isAtLimit = computed(() => {
      const maxCollaborators = formData.hasSubtasks ? 5 : 10;
      return formData.assigned_to.length >= maxCollaborators;
    });

    // NEW: Cleanup on unmount
    onBeforeUnmount(() => {
      document.removeEventListener('click', handleOutsideClick);
      if (dropdownCloseTimeout.value) {
        clearTimeout(dropdownCloseTimeout.value);
      }
    });

    // NEW: Load users from backend API
    const loadUsers = async () => {
      isLoadingUsers.value = true;
      try {
        users.value = await taskService.getUsers();
      } catch (error) {
        console.error('Error loading users:', error);
        // You can add toast notification here if available
      } finally {
        isLoadingUsers.value = false;
      }
    };

    // NEW: Dropdown interaction methods
    const handleInputFocus = () => {
      if (!isAtLimit.value && !isLoadingUsers.value) {
        showDropdown.value = true;
        highlightedIndex.value = -1;
      }
    };

    const handleInputBlur = (event) => {
      // Check if the blur is because user clicked on a dropdown item
      const relatedTarget = event.relatedTarget;
      const dropdownContainer = document.querySelector('.search-dropdown-container');
      
      if (relatedTarget && dropdownContainer && dropdownContainer.contains(relatedTarget)) {
        // Don't close if clicking within dropdown
        return;
      }
      
      dropdownCloseTimeout.value = setTimeout(() => {
        closeDropdown();
      }, 200);
    };

    const handleSearchInput = () => {
      if (!showDropdown.value && !isAtLimit.value) {
        showDropdown.value = true;
      }
      highlightedIndex.value = -1;
    };

    const toggleDropdown = () => {
      if (isAtLimit.value || isLoadingUsers.value) return;
      
      showDropdown.value = !showDropdown.value;
      if (showDropdown.value) {
        nextTick(() => {
          document.getElementById('assignedTo')?.focus();
        });
      }
    };

    const closeDropdown = () => {
      showDropdown.value = false;
      highlightedIndex.value = -1;
      userSearch.value = '';
    };

    const handleOutsideClick = (event) => {
      // You'll need to add a ref to the dropdown container in template
      const dropdownContainer = document.querySelector('.search-dropdown-container');
      if (dropdownContainer && !dropdownContainer.contains(event.target)) {
        closeDropdown();
      }
    };

    const selectUser = (user) => {
      if (isAtLimit.value || isUserSelected(user)) return;
      
      // Clear any pending close timeout
      if (dropdownCloseTimeout.value) {
        clearTimeout(dropdownCloseTimeout.value);
        dropdownCloseTimeout.value = null;
      }
      
      // Add user to selected collaborators
      formData.assigned_to.push({
        id: user.id,
        name: user.name,
        email: user.email
      });
      
      // Validate collaborators after adding (don't mark as touched automatically)
      validateField('collaborators', formData.assigned_to, false);
      
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
      return formData.assigned_to.some(assignee => assignee.id === user.id);
    };

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

    // Keep all your existing functions
    const getCurrentDate = () => {
      const today = new Date();
      return today.toISOString().split('T')[0];
    };

    const onSubtasksChange = () => {
      if (formData.hasSubtasks && formData.assigned_to.length > 5) {
        formData.assigned_to = formData.assigned_to.slice(0, 5);
      }
      dateValidationError.value = '';
    };

    // UPDATED: Remove assignee method for dropdown (works with objects now)
    const removeAssignee = (index) => {
      formData.assigned_to.splice(index, 1);
      // Validate collaborators after removing (don't mark as touched automatically)
      validateField('collaborators', formData.assigned_to, false);
    };

    const handleFileUpload = (event) => {
      const files = Array.from(event.target.files);
      
      if (formData.attachments.length + files.length > 3) {
        validationErrors.attachments = 'Maximum 3 files allowed';
        return;
      }
      
      // Validate file sizes
      const maxFileSize = 10 * 1024 * 1024; // 10MB
      for (let file of files) {
        if (file.size > maxFileSize) {
          validationErrors.attachments = `File "${file.name}" is too large. Maximum size is 10MB`;
          return;
        }
      }
      
      formData.attachments = [...formData.attachments, ...files];
      validationErrors.attachments = ''; // Clear error if successful
    };

    const removeFile = (index) => {
      formData.attachments.splice(index, 1);
      
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

    // Enhanced validation functions
    const validateTaskName = (value) => {
      if (!value || !value.trim()) {
        return 'Task name is required';
      }
      if (value.length < 3) {
        return 'Task name must be at least 3 characters';
      }
      if (value.length > 100) {
        return 'Task name must be less than 100 characters';
      }
      return '';
    };

    const validateTaskDescription = (value) => {
      if (value && value.length > 500) {
        return 'Task description must be less than 500 characters';
      }
      return '';
    };

    const validateProjectSelection = (value) => {
      if (!value || !value.trim()) {
        return 'Please select a project';
      }
      return '';
    };

    const validateStartDate = (value) => {
      if (!value) {
        return 'Start date is required';
      }
      const startDate = new Date(value);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      
      if (startDate < today) {
        return 'Start date cannot be in the past';
      }
      return '';
    };

    const validateEndDate = (value, startDate) => {
      if (!value) {
        return 'End date is required';
      }
      if (!startDate) {
        return '';
      }
      const start = new Date(startDate);
      const end = new Date(value);
      
      if (end <= start) {
        return 'End date must be after start date';
      }
      return '';
    };

    const validateTaskStatus = (value) => {
      if (!value || !value.trim()) {
        return 'Task status is required';
      }
      return '';
    };

    const validateAttachments = (files) => {
      if (files.length > 3) {
        return 'Maximum 3 files allowed';
      }
      
      const maxFileSize = 10 * 1024 * 1024; // 10MB
      for (let file of files) {
        if (file.size > maxFileSize) {
          return `File "${file.name}" is too large. Maximum size is 10MB`;
        }
      }
      return '';
    };

    const validateCollaborators = (collaborators) => {
      if (!collaborators || collaborators.length === 0) {
        return 'At least 1 collaborator is required';
      }
      return '';
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

    // Real-time validation
    const validateField = (fieldName, value, markAsTouched = true) => {
      if (markAsTouched) {
        touchedFields[fieldName] = true;
      }
      
      switch (fieldName) {
        case 'task_name':
          validationErrors.task_name = touchedFields.task_name ? validateTaskName(value) : '';
          break;
        case 'task_desc':
          validationErrors.task_desc = touchedFields.task_desc ? validateTaskDescription(value) : '';
          break;
        case 'proj_ID':
          validationErrors.proj_ID = touchedFields.proj_ID ? validateProjectSelection(value) : '';
          break;
        case 'start_date':
          validationErrors.start_date = touchedFields.start_date ? validateStartDate(value) : '';
          // Re-validate end date when start date changes
          if (formData.end_date && touchedFields.end_date) {
            validationErrors.end_date = validateEndDate(formData.end_date, value);
          }
          break;
        case 'end_date':
          validationErrors.end_date = touchedFields.end_date ? validateEndDate(value, formData.start_date) : '';
          break;
        case 'task_status':
          validationErrors.task_status = touchedFields.task_status ? validateTaskStatus(value) : '';
          break;
        case 'attachments':
          validationErrors.attachments = touchedFields.attachments ? validateAttachments(value) : '';
          break;
        case 'collaborators':
          validationErrors.collaborators = touchedFields.collaborators ? validateCollaborators(value) : '';
          break;
      }
    };

    // Check if form is valid
    const isFormValid = computed(() => {
      return !Object.values(validationErrors).some(error => error !== '') && 
             !dateValidationError.value &&
             validateTaskName(formData.task_name) === '' &&
             validateStartDate(formData.start_date) === '' &&
             validateEndDate(formData.end_date, formData.start_date) === '' &&
             validateTaskStatus(formData.task_status) === '' &&
             validateAttachments(formData.attachments) === '' &&
             validateCollaborators(formData.assigned_to) === '';
    });

    onMounted(() => {
      // Get current user from sessionStorage
      const getCurrentUser = () => {
        try {
          const userData = sessionStorage.getItem('user');
          if (userData) {
            const user = JSON.parse(userData);
            console.log('Current user data:', user); // Debug log
            return user; // Return the full user object
          }
          return null;
        } catch (error) {
          console.error('Error getting current user:', error);
          return null;
        }
      };

      const currentUser = getCurrentUser();
      if (currentUser) {
        formData.created_by = currentUser.name;
        // Store current user for filtering
        currentUserId.value = currentUser.id; // Add this line
      } else {
        formData.created_by = 'Not Logged In';
      }
      
      loadUsers();
      loadProjects();
      document.addEventListener('click', handleOutsideClick);
    });

    const resetForm = () => {
      Object.assign(formData, {
        proj_name: '',
        task_ID: '',
        task_name: '',
        task_desc: '',
        start_date: '',
        end_date: '',
        created_by: '',
        assigned_to: [],
        attachments: [],
        task_status: '',
        hasSubtasks: false
      });
      
      if (fileInput.value) {
        fileInput.value.value = '';
      }
      
      assignedToInput.value = '';
      dateValidationError.value = '';
      userSearch.value = '';
      closeDropdown(); 
      formData.created_by = 'Current User';
      
      // Clear validation errors and touched fields
      Object.keys(validationErrors).forEach(key => {
        validationErrors[key] = '';
      });
      Object.keys(touchedFields).forEach(key => {
        touchedFields[key] = false;
      });
    };

    // UPDATED: Prepare form data for submission (send only user IDs)
    const prepareFormDataForSubmission = () => {
      return {
        ...formData,
        assigned_to: formData.assigned_to.map(user => typeof user === 'object' ? user.id : user)
      };
    };

    // UPDATED: Form submission method with comprehensive validation
    const handleSubmit = async () => {
      if (isSubmitting.value) {
        return;
      }
      
      // Function to scroll to and focus a field
      const scrollToField = (fieldId) => {
        const field = document.getElementById(fieldId);
        if (field) {
          field.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'center' 
          });
          setTimeout(() => {
            field.focus();
          }, 300);
        }
      };
      
      // Mark all fields as touched to show validation errors
      Object.keys(touchedFields).forEach(key => {
        touchedFields[key] = true;
      });
      
      // Validate all fields and show errors
      let hasErrors = false;
      let firstErrorField = null;
      
      // Validate required fields
      validationErrors.task_name = validateTaskName(formData.task_name);
      validationErrors.start_date = validateStartDate(formData.start_date);
      validationErrors.end_date = validateEndDate(formData.end_date, formData.start_date);
      validationErrors.task_status = validateTaskStatus(formData.task_status);
      validationErrors.attachments = validateAttachments(formData.attachments);
      validationErrors.collaborators = validateCollaborators(formData.assigned_to);
      
      // Check for any validation errors
      if (validationErrors.task_name) {
        hasErrors = true;
        if (!firstErrorField) firstErrorField = 'taskName';
      }
      if (validationErrors.start_date) {
        hasErrors = true;
        if (!firstErrorField) firstErrorField = 'startDate';
      }
      if (validationErrors.end_date) {
        hasErrors = true;
        if (!firstErrorField) firstErrorField = 'endDate';
      }
      if (validationErrors.task_status) {
        hasErrors = true;
        if (!firstErrorField) firstErrorField = 'taskStatus';
      }
      if (validationErrors.attachments) {
        hasErrors = true;
        if (!firstErrorField) firstErrorField = 'attachments';
      }
      if (validationErrors.collaborators) {
        hasErrors = true;
        if (!firstErrorField) firstErrorField = 'assignedTo';
      }
      
      // If there are errors, scroll to the first one and return
      if (hasErrors) {
        if (firstErrorField) {
          scrollToField(firstErrorField);
        }
        return;
      }

      // If we get here, all validation passed
      isSubmitting.value = true;
      
      try {
        // Prepare task data for API call
        const taskData = prepareFormDataForSubmission();
        
        // Add other properties
        const finalTaskData = {
          ...taskData,
          // proj_ID: taskData.proj_ID ? taskData.proj_ID.trim() : '', // Handle empty project ID
          task_ID: taskData.task_ID.trim(),
          task_name: taskData.task_name.trim(),
          task_desc: taskData.task_desc.trim(),
          start_date: taskData.start_date,
          end_date: taskData.end_date || null,
          created_by: taskData.created_by,
          attachments: formData.attachments.map(file => ({
            name: file.name,
            size: file.size,
            type: file.type
          })),
          task_status: taskData.task_status || null,
          hasSubtasks: taskData.hasSubtasks
        };

        console.log('Submitting task data to API:', finalTaskData);

        // Call backend API
        const response = await taskService.createTask(finalTaskData);
        
        console.log('Task created successfully:', response);
        
        // Reset form first
        resetForm();
        
        // Emit success event
        emit('success', response);
        
      } catch (error) {
        console.error('Error creating task:', error);
        
        const errorMessage = error.message || 'An unexpected error occurred';
        emit('error', errorMessage);
        
      } finally {
        isSubmitting.value = false;
        console.log('Form submission completed');
      }
    };

    return {
      // Existing returns
      formData,
      assignedToInput,
      fileInput,
      isSubmitting,
      dateValidationError,
      validationErrors,
      isFormValid,
      removeAssignee,
      handleFileUpload,
      removeFile,
      formatFileSize,
      validateDates,
      validateField,
      handleSubmit,
      getCurrentDate,
      onSubtasksChange,
      
      // NEW: Dropdown-related returns
      users,
      userSearch,
      showDropdown,
      isLoadingUsers,
      highlightedIndex,
      filteredUsers,
      isAtLimit,
      handleInputFocus,
      handleInputBlur,
      handleSearchInput,
      toggleDropdown,
      closeDropdown,
      selectUser,
      isUserSelected,
      selectFirstMatch,
      navigateDown,
      navigateUp,

      projects,
      projectSearch,
      showProjectDropdown,
      isLoadingProjects,
      filteredProjects,
      projectHighlightedIndex,
      isProjectSelected,
      handleProjectSearchInput, 
      clearProjectSelection,
      handleProjectInputFocus,
      toggleProjectDropdown,
      selectProject      
    };
  }
};
</script>

<style scoped>
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

.search-dropdown-container {
  position: relative;
}

.search-dropdown-container .form-input {
  padding-right: 40px; /* Space for dropdown icon */
}

.dropdown-toggle-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  transition: transform 0.2s ease;
  color: #666;
  font-size: 12px;
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
  border: 1px solid #ddd;
  border-radius: 6px;
  max-height: 250px;
  overflow-y: auto;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  margin-top: 2px;
}

.dropdown-item {
  padding: 12px 16px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: background-color 0.15s ease;
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
}

.dropdown-item.loading,
.dropdown-item.no-results {
  color: #666;
  font-style: italic;
  cursor: default;
}

.dropdown-item.loading:hover,
.dropdown-item.no-results:hover {
  background-color: transparent;
}

.user-info {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.user-name {
  font-weight: 500;
  color: #333;
}

.user-email {
  font-size: 0.875rem;
  color: #666;
  margin-top: 2px;
}

.selected-indicator {
  color: #4caf50;
  font-weight: bold;
  margin-left: 8px;
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

/* Update existing assignee-tag styles to work with objects */
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

/* Dropdown scroll styling */
.dropdown-list::-webkit-scrollbar {
  width: 6px;
}

.dropdown-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.dropdown-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.dropdown-list::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}

.project-dropdown-container {
  position: relative;
}

.project-dropdown-container .form-input {
  padding-right: 40px; /* Space for dropdown icon */
}

.clear-selection-btn {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  color: #666;
  font-size: 18px;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.clear-selection-btn:hover {
  background-color: #f0f0f0;
  color: #333;
}
</style>
