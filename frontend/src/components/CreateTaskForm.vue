<template>
  <form class="task-form" @submit.prevent="handleSubmit" novalidate>
    <!-- Project Selection -->
    <div class="form-group">
      <label class="form-label" for="projId">
        Project
      </label>
      
      <!-- Project dropdown -->
      <div class="search-dropdown-container" :class="{ 'dropdown-open': showProjectDropdown }">
        <input
          v-if="!selectedProject"
          id="projId"
          v-model="displayValue"
          type="text"
          class="form-input"
          :class="{ 'error': validationErrors.proj_name }"
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
        
        <!-- Locked input for Add Task (project pre-selected) -->
        <div
          v-else
          class="form-input locked"
          :class="{ 'error': validationErrors.proj_name }"
        >
          {{ selectedProject.proj_name }}
        </div>
        
        <!-- Dropdown icon and clear button - only show for New Task (not Add Task) -->
        <div class="input-actions" v-if="!selectedProject">
          <div 
            v-if="selectedProjectRef" 
            class="clear-selection-btn" 
            @click="clearProjectSelection"
            title="Clear project selection"
          >
            ×
          </div>
          <div 
            class="dropdown-toggle-icon" 
            :class="{ 'rotated': showProjectDropdown }"
            @click="toggleProjectDropdown"
            title="Select project"
          >
            ▼
          </div>
        </div>
        
        
        <!-- Dropdown options list -->
        <div 
          v-if="showProjectDropdown && !selectedProject" 
          class="dropdown-list"
          @mousedown.prevent
          @click.prevent
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
            :key="`project-${index}-${project.id || project.proj_name || 'unknown'}`"
            class="dropdown-item"
            :class="{ 
              'highlighted': index === projectHighlightedIndex,
              'selected': isProjectSelected(project)
            }"
            @mousedown.prevent="selectProject(project)"
            @mouseenter="projectHighlightedIndex = index"
          >
            <div class="project-info">
              <span class="project-name">{{ project.proj_name }}</span>
              <span v-if="project.proj_desc" class="project-description">{{ project.proj_desc }}</span>
            </div>
            <span v-if="isProjectSelected(project)" class="selected-indicator">✓</span>
          </div>
        </div>
      </div>
      
      <!-- Project validation error -->
      <span v-if="validationErrors.proj_name" class="error-message">
        {{ validationErrors.proj_name }}
      </span>
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
        :min="getTaskMinStartDate()"
        :max="getTaskMaxEndDate()"
        @change="validateDates(); validateField('start_date', formData.start_date)"
        @blur="validateField('start_date', formData.start_date)"
      />
      <span v-if="validationErrors.start_date" class="error-message">
        {{ validationErrors.start_date }}
      </span>
      <div v-if="getSelectedProjectInfo().startDate" class="date-constraint-info">
        Project dates: {{ formatDateRange(getSelectedProjectInfo().startDate, getSelectedProjectInfo().endDate) }}
      </div>
    </div>

    <!-- End Date -->
    <div class="form-group">
      <label class="form-label" for="endDate">End Date *</label>
      <input
        id="endDate"
        v-model="formData.end_date"
        type="date"
        class="form-input"
        :class="{ 'error': validationErrors.end_date }"
        :min="formData.start_date || getTaskMinStartDate()"
        :max="getTaskMaxEndDate()"
        @change="validateDates(); validateField('end_date', formData.end_date)"
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
        @click.prevent
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
        :key="`assignee-${index}-${assignee.id || assignee.name || 'unknown'}`"
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
        {{ isUploadingFiles ? 'Uploading files...' : isSubmitting ? 'Creating...' : 'Create Task' }}
      </button>
    </div>
  </form>
</template>

<script>
import { ref, reactive, onMounted, computed, onBeforeUnmount, nextTick, watch } from 'vue';
import { taskService } from '@/services/taskService';
import { fileUploadService } from '@/services/fileUploadService';

export default {
  name: "TaskForm",
  props: {
    selectedProject: {
      type: Object,
      default: null
    }
  },
  emits: ['submit', 'cancel', 'success', 'error'],
  setup(props, { emit }) {
    const isSubmitting = ref(false);
    const isUploadingFiles = ref(false);
    const assignedToInput = ref('');
    const fileInput = ref(null);
    const dateValidationError = ref('');
    
    // Helper function to get current user
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
    const isLoadingProjects = ref(false); 
    const currentUserId = ref(null);
    
    // Project dropdown state
    const projectSearch = ref('');
    const showProjectDropdown = ref(false);
    const projectHighlightedIndex = ref(-1);
    const projectDropdownCloseTimeout = ref(null);
    const selectedProjectRef = ref(null);

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


    const loadProjects = async () => {
      isLoadingProjects.value = true;
      try {
        console.log('Loading projects...');
        
        // Get current user info for filtering
        const currentUser = getCurrentUser();
        let projectsData;
        
        if (currentUser && currentUser.id && currentUser.division_name) {
          console.log('Loading projects for user:', currentUser.id, 'division:', currentUser.division_name);
          projectsData = await taskService.getProjects(currentUser.id, currentUser.division_name);
        } else {
          console.log('No user info available, loading all projects');
          projectsData = await taskService.getProjects();
        }
        
        console.log('Projects loaded:', projectsData);
        
        // Check for duplicate IDs
        const ids = projectsData.map(p => p.id);
        const duplicateIds = ids.filter((id, index) => ids.indexOf(id) !== index);
        if (duplicateIds.length > 0) {
          console.warn('Duplicate project IDs found:', duplicateIds);
        }
        
        projects.value = projectsData;
      } catch (error) {
        console.error('Error loading projects:', error);
      } finally {
        isLoadingProjects.value = false;
      }
    };


    const clearProjectSelection = () => {
      formData.proj_name = '';
      selectedProjectRef.value = null;
      projectSearch.value = '';
      validationErrors.proj_name = '';
      // Open dropdown after clearing to show all projects
      showProjectDropdown.value = true;
    };

    // Project dropdown methods
    const displayValue = computed({
      get() {
        // For Add Task (project pre-selected), return the project name
        if (props.selectedProject) {
          return props.selectedProject.proj_name;
        }
        
        // For New Task (no project pre-selected), handle dropdown logic
        if (showProjectDropdown.value) {
          return projectSearch.value;
        }
        return selectedProjectRef.value ? selectedProjectRef.value.proj_name : projectSearch.value;
      },
      set(value) {
        // Don't allow changes if project is pre-selected (Add Task button)
        if (props.selectedProject) {
          return;
        }
        
        projectSearch.value = value;
        // Clear selected project when user starts typing
        if (value && selectedProjectRef.value) {
          selectedProjectRef.value = null;
          formData.proj_name = '';
        }
      }
    });

    const filteredProjects = computed(() => {
      console.log('Filtering projects:', { search: projectSearch.value, projects: projects.value });
      if (!projectSearch.value) {
        return projects.value;
      }
      const filtered = projects.value.filter(project => 
        project.proj_name.toLowerCase().includes(projectSearch.value.toLowerCase()) ||
        (project.proj_desc && project.proj_desc.toLowerCase().includes(projectSearch.value.toLowerCase()))
      );
      console.log('Filtered projects:', filtered);
      
      // Check for duplicates in filtered results
      const filteredIds = filtered.map(p => p.id);
      const duplicateFilteredIds = filteredIds.filter((id, index) => filteredIds.indexOf(id) !== index);
      if (duplicateFilteredIds.length > 0) {
        console.warn('Duplicate IDs in filtered projects:', duplicateFilteredIds);
      }
      
      return filtered;
    });

    const isProjectSelected = (project) => {
      return selectedProjectRef.value && selectedProjectRef.value.id === project.id;
    };

    const selectProject = (project) => {
      console.log('Selecting project:', project);
      selectedProjectRef.value = project;
      formData.proj_name = project.proj_name;
      projectSearch.value = ''; // Clear search to allow new searches
      closeProjectDropdown();
      validateField('proj_name', project.proj_name);
    };

    const handleProjectInputFocus = () => {
      // Don't open dropdown if project is pre-selected (Add Task button)
      if (props.selectedProject) {
        return;
      }
      
      if (!isLoadingProjects.value) {
        showProjectDropdown.value = true;
        projectHighlightedIndex.value = -1;
        // Clear the search when focusing to allow new search
        if (selectedProjectRef.value) {
          projectSearch.value = '';
        }
      }
    };

    const handleProjectInputBlur = (event) => {
      if (projectDropdownCloseTimeout.value) {
        clearTimeout(projectDropdownCloseTimeout.value);
      }
      
      const relatedTarget = event.relatedTarget;
      const dropdownContainer = document.querySelector('.search-dropdown-container');
      
      if (relatedTarget && dropdownContainer && dropdownContainer.contains(relatedTarget)) {
        return;
      }
      
      projectDropdownCloseTimeout.value = setTimeout(() => {
        closeProjectDropdown();
      }, 500);
    };

    const handleProjectSearchInput = () => {
      projectHighlightedIndex.value = -1;
      if (!showProjectDropdown.value) {
        showProjectDropdown.value = true;
      }
    };

    const toggleProjectDropdown = () => {
      // Don't allow toggling if project is pre-selected (Add Task button)
      if (props.selectedProject) {
        return;
      }
      
      if (projectDropdownCloseTimeout.value) {
        clearTimeout(projectDropdownCloseTimeout.value);
        projectDropdownCloseTimeout.value = null;
      }
      
      showProjectDropdown.value = !showProjectDropdown.value;
      if (showProjectDropdown.value) {
        nextTick(() => {
          const input = document.getElementById('projId');
          if (input) {
            input.focus();
          }
        });
      }
    };

    const closeProjectDropdown = () => {
      showProjectDropdown.value = false;
      projectHighlightedIndex.value = -1;
    };

    const selectFirstProjectMatch = () => {
      if (filteredProjects.value.length > 0) {
        selectProject(filteredProjects.value[0]);
      }
    };

    const navigateProjectDown = () => {
      if (!showProjectDropdown.value) {
        showProjectDropdown.value = true;
        return;
      }
      
      if (projectHighlightedIndex.value < filteredProjects.value.length - 1) {
        projectHighlightedIndex.value++;
      }
    };

    const navigateProjectUp = () => {
      if (projectHighlightedIndex.value > 0) {
        projectHighlightedIndex.value--;
      }
    };

    const getSelectedProjectInfo = () => {
      // Check if we have a pre-selected project (Add Task)
      if (props.selectedProject) {
        return {
          startDate: props.selectedProject.start_date,
          endDate: props.selectedProject.end_date,
          name: props.selectedProject.proj_name
        }
      }
      
      // Check if user selected a project from dropdown (New Task)
      if (selectedProjectRef.value) {
        return {
          startDate: selectedProjectRef.value.start_date,
          endDate: selectedProjectRef.value.end_date,
          name: selectedProjectRef.value.proj_name
        }
      }
      
      return { startDate: null, endDate: null, name: null }
    }

    const getTaskMinStartDate = () => {
      const projectInfo = getSelectedProjectInfo()
      const today = getCurrentDate()
      
      if (projectInfo.startDate) {
        // Use the later of today or project start date
        const projectStartDate = new Date(projectInfo.startDate).toISOString().split('T')[0]
        return projectStartDate > today ? projectStartDate : today
      }
      
      return today
    }

    const getTaskMaxEndDate = () => {
      const projectInfo = getSelectedProjectInfo()
      
      if (projectInfo.endDate) {
        return new Date(projectInfo.endDate).toISOString().split('T')[0]
      }
      
      return null // No constraint if no project selected
    }

    const formatDateRange = (startDate, endDate) => {
      if (!startDate || !endDate) return ''
      
      const start = new Date(startDate).toLocaleDateString('en-SG', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
      })
      
      const end = new Date(endDate).toLocaleDateString('en-SG', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
      })
      
      return `${start} - ${end}`
    }

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
      // Clear any existing timeout
      if (dropdownCloseTimeout.value) {
        clearTimeout(dropdownCloseTimeout.value);
      }
      
      // Check if the blur is because user clicked on a dropdown item
      const relatedTarget = event.relatedTarget;
      const dropdownContainer = document.querySelector('.search-dropdown-container');
      
      if (relatedTarget && dropdownContainer && dropdownContainer.contains(relatedTarget)) {
        // Don't close if clicking within dropdown
        return;
      }
      
      // Use a longer delay to prevent bouncing
      dropdownCloseTimeout.value = setTimeout(() => {
        closeDropdown();
      }, 500);
    };

    const handleSearchInput = () => {
      if (!showDropdown.value && !isAtLimit.value) {
        showDropdown.value = true;
      }
      highlightedIndex.value = -1;
    };

    const toggleDropdown = () => {
      if (isAtLimit.value || isLoadingUsers.value) return;
      
      // Clear any pending close timeout when manually toggling
      if (dropdownCloseTimeout.value) {
        clearTimeout(dropdownCloseTimeout.value);
        dropdownCloseTimeout.value = null;
      }
      
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
      // Get current date in Singapore timezone
      const today = new Date();
      const sgTime = new Date(today.toLocaleString("en-US", {timeZone: "Asia/Singapore"}));
      return sgTime.toISOString().split('T')[0];
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
      
      // Validate each file
      for (let file of files) {
        const validation = fileUploadService.validateFile(file);
        if (!validation.valid) {
          validationErrors.attachments = validation.error;
          return;
        }
      }
      
      // Add files to form data (will be uploaded when form is submitted)
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
      return fileUploadService.formatFileSize(bytes);
    };

    const getFileIcon = (fileType) => {
      return fileUploadService.getFileIcon(fileType);
    };

    const getFileTypeColor = (fileType) => {
      return fileUploadService.getFileTypeColor(fileType);
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


    const validateStartDate = (value) => {
      if (!value) {
        return 'Start date is required'
      }
      
      const startDate = new Date(value)
      const today = new Date()
      const sgToday = new Date(today.toLocaleString("en-US", {timeZone: "Asia/Singapore"}))
      sgToday.setHours(0, 0, 0, 0)
      
      // Check if date is in the past
      if (startDate < sgToday) {
        return 'Start date cannot be in the past'
      }
      
      // Check project constraints
      const projectInfo = getSelectedProjectInfo()
      if (projectInfo.startDate) {
        const projectStartDate = new Date(projectInfo.startDate)
        if (startDate < projectStartDate) {
          const formattedDate = new Date(projectInfo.startDate).toLocaleDateString('en-SG', {
            day: '2-digit',
            month: 'short',
            year: 'numeric'
          })
          return `Start date cannot be before project start date (${formattedDate})`
        }
      }
      
      if (projectInfo.endDate) {
        const projectEndDate = new Date(projectInfo.endDate)
        if (startDate > projectEndDate) {
          const formattedDate = new Date(projectInfo.endDate).toLocaleDateString('en-SG', {
            day: '2-digit',
            month: 'short',
            year: 'numeric'
          })
          return `Start date cannot be after project end date (${formattedDate})`
        }
      }
      
      return ''
    }

    const validateEndDate = (value, startDate) => {
      if (!value) {
        return 'End date is required'
      }
      
      if (!startDate) {
        return ''
      }
      
      const start = new Date(startDate)
      const end = new Date(value)
      
      // Basic validation - end must be after start
      if (end <= start) {
        return 'End date must be after start date'
      }
      
      // Check project constraints
      const projectInfo = getSelectedProjectInfo()
      if (projectInfo.endDate) {
        const projectEndDate = new Date(projectInfo.endDate)
        if (end > projectEndDate) {
          const formattedDate = new Date(projectInfo.endDate).toLocaleDateString('en-SG', {
            day: '2-digit',
            month: 'short',
            year: 'numeric'
          })
          return `End date cannot be after project end date (${formattedDate})`
        }
      }
      
      if (projectInfo.startDate) {
        const projectStartDate = new Date(projectInfo.startDate)
        if (end < projectStartDate) {
          const formattedDate = new Date(projectInfo.startDate).toLocaleDateString('en-SG', {
            day: '2-digit',
            month: 'short',
            year: 'numeric'
          })
          return `End date cannot be before project start date (${formattedDate})`
        }
      }
      
      return ''
    }

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
        case 'proj_name':
          // Project is optional, no validation needed
          validationErrors.proj_name = '';
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
      const hasValidationErrors = Object.values(validationErrors).some(error => error !== '');
      const hasDateError = dateValidationError.value;
      
      console.log('=== FORM VALIDATION CHECK ===');
      console.log('Validation errors:', validationErrors);
      console.log('Date error:', dateValidationError.value);
      console.log('Has validation errors:', hasValidationErrors);
      console.log('Has date error:', hasDateError);
      console.log('Form valid:', !hasValidationErrors && !hasDateError);
      
      return !hasValidationErrors && !hasDateError;
    });

    // Watch for selectedProject prop changes to pre-fill project
    watch(() => props.selectedProject, (newProject) => {
      if (newProject) {
        const projectName = newProject.proj_name || newProject.name || '';
        formData.proj_name = projectName;
        selectedProjectRef.value = newProject;
        // Clear any existing project validation error
        validationErrors.proj_name = '';
        // Ensure dropdown is closed for Add Task
        showProjectDropdown.value = false;
      }
    }, { immediate: true });

    onMounted(() => {
      // Get current user using the helper function
      const currentUser = getCurrentUser();
      if (currentUser) {
        formData.created_by = currentUser.name;
        // Store current user for filtering
        currentUserId.value = currentUser.id; 
      } else {
        formData.created_by = 'Not Logged In';
      }
      
      loadUsers();
      loadProjects();
      document.addEventListener('click', handleOutsideClick);
      
      // Test Firebase Storage connection
      fileUploadService.testStorageConnection().then(success => {
        if (success) {
          console.log('Firebase Storage is working correctly');
        } else {
          console.error('Firebase Storage is not working - check your configuration');
        }
      });
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
      console.log('=== FORM SUBMISSION STARTED ===');
      console.log('Is submitting:', isSubmitting.value);
      console.log('Form valid:', isFormValid.value);
      console.log('Form data:', formData);
      console.log('Validation errors:', validationErrors);
      console.log('Date validation error:', dateValidationError.value);
      console.log('=== HANDLE SUBMIT FUNCTION CALLED ===');
      
      if (isSubmitting.value) {
        console.log('Already submitting, returning early');
        return;
      }
      
      // Trigger validation for all fields
      console.log('=== TRIGGERING ALL FIELD VALIDATIONS ===');
      validateField('proj_name', formData.proj_name, true);
      validateField('task_name', formData.task_name, true);
      validateField('task_desc', formData.task_desc, true);
      validateField('start_date', formData.start_date, true);
      validateField('end_date', formData.end_date, true);
      validateField('task_status', formData.task_status, true);
      validateField('collaborators', formData.assigned_to, true);
      
      // Check if form is actually valid
      if (!isFormValid.value) {
        console.log('Form is not valid, not submitting');
        console.log('Validation errors:', validationErrors);
        console.log('Date validation error:', dateValidationError.value);
        console.log('Form data:', formData);
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
      
      // Validate required fields (project is optional)
      validationErrors.task_name = validateTaskName(formData.task_name);
      validationErrors.start_date = validateStartDate(formData.start_date);
      validationErrors.end_date = validateEndDate(formData.end_date, formData.start_date);
      validationErrors.task_status = validateTaskStatus(formData.task_status);
      validationErrors.attachments = validateAttachments(formData.attachments);
      validationErrors.collaborators = validateCollaborators(formData.assigned_to);
      
      // Check for any validation errors (skip project validation)
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
        console.log('=== VALIDATION ERRORS PREVENTING SUBMISSION ===');
        console.log('Validation errors:', validationErrors);
        console.log('First error field:', firstErrorField);
        console.log('Form data:', formData);
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
        
        // Upload files to Firebase Storage first
        let uploadedAttachments = [];
        if (formData.attachments.length > 0) {
          isUploadingFiles.value = true;
          console.log('Uploading files to Firebase Storage...');
          console.log('Files to upload:', formData.attachments);
          const currentUser = JSON.parse(sessionStorage.getItem('user') || '{}');
          const userId = currentUser.id || 'anonymous';
          console.log('Current user:', currentUser);
          console.log('User ID:', userId);
          
          // Generate a temporary task ID for file organization
          const tempTaskId = `temp_${Date.now()}`;
          console.log('Temporary task ID:', tempTaskId);
          
          try {
            uploadedAttachments = await fileUploadService.uploadMultipleFiles(
              formData.attachments, 
              tempTaskId, 
              userId
            );
            console.log('Files uploaded successfully:', uploadedAttachments);
          } catch (uploadError) {
            console.error('File upload failed:', uploadError);
            throw uploadError;
          } finally {
            isUploadingFiles.value = false;
          }
        } else {
          console.log('No files to upload');
        }
        
        // Add other properties
        const finalTaskData = {
          ...taskData,
          task_name: taskData.task_name.trim(),
          task_desc: taskData.task_desc.trim(),
          start_date: taskData.start_date,
          end_date: taskData.end_date || null,
          created_by: taskData.created_by,
          attachments: uploadedAttachments, // Use uploaded file data instead of raw files
          task_status: taskData.task_status || null,
          hasSubtasks: taskData.hasSubtasks
        };

        console.log('=== FINAL TASK DATA DEBUG ===');
        console.log('Project name being sent:', finalTaskData.proj_name);
        console.log('Project name type:', typeof finalTaskData.proj_name);
        console.log('Project name length:', finalTaskData.proj_name ? finalTaskData.proj_name.length : 'null/undefined');

        console.log('Submitting task data to API:', finalTaskData);

        // Call backend API
        console.log('=== CALLING BACKEND API ===');
        console.log('Final task data being sent:', finalTaskData);
        console.log('API endpoint: /api/tasks');
        
        const response = await taskService.createTask(finalTaskData);
        
        console.log('=== TASK CREATED SUCCESSFULLY ===');
        console.log('Task created successfully:', response);
        console.log('About to reset form...');
        
        // Reset form first
        resetForm();
        console.log('Form reset completed');
        
        // Emit success event
        console.log('=== EMITTING SUCCESS EVENT ===');
        console.log('Response to emit:', response);
        console.log('Response type:', typeof response);
        console.log('Response keys:', response ? Object.keys(response) : 'No response');
        console.log('About to emit success event...');
        emit('success', response);
        console.log('Success event emitted successfully');
        
        // Add a small delay to ensure the event is processed
        setTimeout(() => {
          console.log('Success event should have been processed by now');
        }, 100);
        
      } catch (error) {
        console.error('=== ERROR CREATING TASK ===');
        console.error('Error details:', error);
        console.error('Error message:', error.message);
        console.error('Error response:', error.response);
        console.error('Error status:', error.response?.status);
        console.error('Error data:', error.response?.data);
        
        const errorMessage = error.message || 'An unexpected error occurred';
        emit('error', errorMessage);
        
      } finally {
        isSubmitting.value = false;
        isUploadingFiles.value = false;
        console.log('Form submission completed');
      }
    };


    return {
      // Existing returns
      formData,
      assignedToInput,
      fileInput,
      isSubmitting,
      isUploadingFiles,
      dateValidationError,
      validationErrors,
      isFormValid,
      removeAssignee,
      handleFileUpload,
      removeFile,
      formatFileSize,
      getFileIcon,
      getFileTypeColor,
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
      isLoadingProjects,
      getSelectedProjectInfo,
      getTaskMinStartDate,
      getTaskMaxEndDate,
      formatDateRange,
      clearProjectSelection,
      
      // Project dropdown methods
      projectSearch,
      displayValue,
      showProjectDropdown,
      projectHighlightedIndex,
      selectedProjectRef,
      filteredProjects,
      isProjectSelected,
      selectProject,
      handleProjectInputFocus,
      handleProjectInputBlur,
      handleProjectSearchInput,
      toggleProjectDropdown,
      closeProjectDropdown,
      selectFirstProjectMatch,
      navigateProjectDown,
      navigateProjectUp
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

.readonly-input,
.form-input.readonly {
  background-color: #f8f9fa;
  color: #6c757d;
  cursor: not-allowed;
}

.form-input.locked {
  background-color: #f3f4f6;
  color: #374151;
  cursor: not-allowed;
  border-color: #d1d5db;
  pointer-events: none;
  user-select: none;
  opacity: 0.7;
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

/* Project Dropdown Styles */
.input-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 10;
}

.clear-selection-btn {
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  color: #6b7280;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  height: 24px;
  width: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.clear-selection-btn:hover {
  background: #ef4444;
  color: white;
  border-color: #dc2626;
}

.project-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.project-info .project-name {
  font-weight: 600;
  color: #333;
}

.project-info .project-description {
  font-size: 0.875rem;
  color: #666;
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
  z-index: 1;
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
  z-index: 9999;
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

.date-constraint-info {
  font-size: 12px;
  color: #666666;
  margin-top: 4px;
  font-style: italic;
}
</style>
