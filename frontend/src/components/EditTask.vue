<!--
  Component: EditTask
  Purpose: Modal form to update an existing task.

  Props
  - visible:Boolean  Controls modal visibility
  - task:Object      The task to edit (can contain id or business task_ID)

  Emits
  - close            When modal should close without saving
  - saved(payload)   After successful save, returns updated task from API
  - error(message)   When save fails; message contains error text

  Behavior
  - Prefills local reactive form from the provided task
  - Validates required fields (task_name, start_date) inline
  - Validates date ordering (end > start if end provided)
  - On save, calls taskService.updateTask with either doc id or task_ID
  - Includes status change log entry (changed_by/timestamp/new_status) when status changes
  - Times out the update if API takes more than 3 seconds
  - Uses simple alerts for notifications to keep footprint small (swap with toast later)
-->
<template>
  <div v-if="visible" class="modal-overlay" @click.self="handleClose">
    <div class="modal-card">
      <div class="modal-header">
        <h2 class="modal-title">Edit Task</h2>
        <button class="icon-btn" @click="handleClose" aria-label="Close">×</button>
      </div>

      <form class="task-form" @submit.prevent="handleSubmit" novalidate>
        <div class="form-grid">
          <!-- Project Selection (Read-only for editing) -->
          <div class="form-group">
            <label class="form-label" for="projId">
              Project
            </label>

            <!-- Locked input for editing (project cannot be changed) -->
            <div class="form-input locked">
              {{ task?.proj_name || 'Unknown Project' }}
            </div>
          </div>

          <!-- Task Name -->
          <div class="form-group">
            <label class="form-label" for="taskName">Task Name *</label>
            <input
              id="taskName"
              v-model="localForm.task_name"
              type="text"
              class="form-input"
              :class="{ 'input-error': errors.task_name }"
              :placeholder="task?.task_name || 'Enter task name'"
              @input="clearError('task_name')"
            />
            <span v-if="errors.task_name" class="error-message">{{ errors.task_name }}</span>
          </div>

          <!-- Task Description -->
          <div class="form-group">
            <label class="form-label" for="taskDesc">Task Description</label>
            <textarea
              id="taskDesc"
              v-model="localForm.task_desc"
              class="form-textarea"
              :placeholder="task?.task_desc || 'Enter task description (max 500 characters)'"
              rows="4"
            ></textarea>
            <div class="char-count">
              {{ localForm.task_desc.length }}/500 characters
            </div>
          </div>

          <!-- Start Date -->
          <div class="form-group">
            <label class="form-label" for="startDate">Start Date *</label>
            <input
              id="startDate"
              v-model="localForm.start_date"
              type="date"
              class="form-input"
              :class="{ 'input-error': errors.start_date }"
              :max="getTaskMaxEndDate()"
              @change="() => { clearError('start_date'); validateDates(); }"
            />
            <span v-if="errors.start_date" class="error-message">{{ errors.start_date }}</span>
            <div v-if="getSelectedProjectInfo().startDate" class="date-constraint-info">
              Project dates: {{ formatDateRange(getSelectedProjectInfo().startDate, getSelectedProjectInfo().endDate) }}
            </div>
          </div>

          <!-- End Date -->
          <div class="form-group">
            <label class="form-label" for="endDate">End Date *</label>
            <input
              id="endDate"
              v-model="localForm.end_date"
              type="date"
              class="form-input"
              :class="{ 'input-error': errors.end_date }"
              :min="localForm.start_date"
              :max="getTaskMaxEndDate()"
              @change="validateDates"
            />
            <span v-if="errors.end_date || dateValidationError" class="error-message">
              {{ errors.end_date || dateValidationError }}
            </span>
          </div>

          <!-- Created By (Auto-populated, read-only) -->
          <div class="form-group">
            <label class="form-label" for="createdBy">Created By</label>
            <input
              id="createdBy"
              v-model="ownerName"
              type="text"
              class="form-input readonly-input"
              readonly
              :placeholder="'Auto-populated from current user'"
            />
          </div>

          <!-- Assigned To -->
          <div class="form-group">
            <label class="form-label" for="assignedTo">
              Collaborators
            </label>

            <!-- Combined search input with dropdown -->
            <div class="search-dropdown-container" :class="{ 'dropdown-open': showDropdown }">
              <input
                id="assignedTo"
                v-model="userSearch"
                type="text"
                class="form-input"
                :class="{ 'input-error': errors.collaborators }"
                :placeholder="isLoadingUsers ? 'Loading users...' : 'Search and select collaborators...'"
                @focus="handleInputFocus; clearError('collaborators')"
                @blur="handleInputBlur"
                @input="handleSearchInput"
                @keydown.enter.prevent="selectFirstMatch"
                @keydown.escape="closeDropdown"
                @keydown.arrow-down.prevent="navigateDown"
                @keydown.arrow-up.prevent="navigateUp"
                :disabled="isLoadingUsers"
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
            <div class="assignee-tags" v-if="localForm.assigned_to.length > 0">
              <span
                v-for="(assignee, index) in localForm.assigned_to"
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
            <div v-if="localForm.assigned_to.length > 0" class="status-message info">
              {{ localForm.assigned_to.length }} collaborator{{ localForm.assigned_to.length !== 1 ? 's' : '' }} selected
            </div>

            <!-- Collaborators validation error -->
            <span v-if="errors.collaborators" class="error-message">
              {{ errors.collaborators }}
            </span>
          </div>

          <!-- Attachments -->
          <div class="form-group">
            <label class="form-label" for="attachments">
              Attachments (max {{ maxAttachments }})
            </label>

            <div class="file-upload-container">
              <input
                id="attachments"
                ref="fileInput"
                type="file"
                class="file-input"
                multiple
                accept=".pdf,.doc,.docx,.jpg,.jpeg,.png,.txt"
                :disabled="existingAttachments.length + newAttachments.length >= maxAttachments || isSubmitting"
                @change="handleFileSelection"
              />
              <label
                for="attachments"
                class="file-upload-label"
                :class="{ disabled: existingAttachments.length + newAttachments.length >= maxAttachments || isSubmitting }"
              >
                Choose Files
              </label>
              <span class="file-status">{{ attachmentSummary }}</span>
            </div>

            <div v-if="existingAttachments.length > 0" class="file-preview-container">
              <div
                v-for="(attachment, index) in existingAttachments"
                :key="`existing-${index}-${attachment.id || attachment.name || 'attachment'}`"
                class="file-preview-item"
                :style="{ borderLeftColor: getFileTypeColor(attachment.type || attachment.mimeType || 'unknown') }"
              >
                <div class="file-icon">
                  {{ getFileIcon(attachment.type || attachment.mimeType || 'unknown') }}
                </div>
                <div class="file-info">
                  <span class="file-name">{{ attachment.name || attachment.originalName || 'Attachment' }}</span>
                  <span class="file-size">{{ formatFileSize(attachment.size || 0) }}</span>
                </div>
                <button
                  type="button"
                  class="remove-file-btn"
                  @click="markExistingAttachmentForRemoval(index)"
                  title="Remove attachment"
                >
                  x
                </button>
              </div>
            </div>

            <div v-if="newAttachments.length > 0" class="file-preview-container new-files">
              <div
                v-for="(attachment, index) in newAttachments"
                :key="`new-${index}-${attachment.tempId}`"
                class="file-preview-item"
                :style="{ borderLeftColor: getFileTypeColor(attachment.file.type || 'unknown') }"
              >
                <div class="file-icon">
                  {{ getFileIcon(attachment.file.type || 'unknown') }}
                </div>
                <div class="file-info">
                  <span class="file-name">{{ attachment.file.name }}</span>
                  <span class="file-size">{{ formatFileSize(attachment.file.size || 0) }}</span>
                </div>
                <button
                  type="button"
                  class="remove-file-btn"
                  @click="removeNewAttachment(index)"
                  title="Remove attachment"
                >
                  x
                </button>
              </div>
            </div>

            <div v-if="existingAttachments.length === 0 && newAttachments.length === 0" class="no-attachments">
              No attachments for this task
            </div>

            <div v-if="attachmentErrors" class="error-message">
              {{ attachmentErrors }}
            </div>

            <div class="attachment-note">
              Remove existing files or add new ones. All changes are saved when you update the task.
            </div>
          </div>
          <!-- Priority Level -->
          <div class="form-group">
            <label class="form-label" for="priorityLevel">
              Priority Level *
            </label>
            <select
              id="priorityLevel"
              v-model="localForm.priority_level"
              class="form-select"
              :class="{ 'input-error': errors.priority_level }"
              @change="clearError('priority_level')"
            >
              <option value="" disabled>Select priority level (1-10)</option>
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
            <span v-if="errors.priority_level" class="error-message">
              {{ errors.priority_level }}
            </span>
          </div>

          <!-- Task Status -->
          <div class="form-group">
            <label class="form-label" for="taskStatus">
              Task Status *
            </label>
            <select
              id="taskStatus"
              v-model="localForm.task_status"
              class="form-select"
              :class="{ 'input-error': errors.task_status }"
              @change="clearError('task_status')"
            >
              <option value="" disabled>Select status</option>
              <option value="Unassigned">Unassigned</option>
              <option value="Ongoing">Ongoing</option>
              <option value="Under Review">Under Review</option>
              <option value="Completed">Completed</option>
            </select>
            <span v-if="errors.task_status" class="error-message">
              {{ errors.task_status }}
            </span>
          </div>
        </div>

        <div class="form-actions">
          <button type="button" class="btn btn-cancel" @click="handleClose" :disabled="isSubmitting">
            Cancel
          </button>
          <button type="submit" class="btn btn-primary" :disabled="isSubmitting || !isFormValid">
            {{ isSubmitting ? 'Updating...' : 'Update Task' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Toast Notification -->
    <div v-if="showToast" class="toast-notification" :class="{ 'toast-success': toastType === 'success' }">
      {{ toastMessage }}
    </div>
  </div>
</template>

<script>
import { reactive, ref, watch, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { taskService } from '@/services/taskService'
import { fileUploadService } from '@/services/fileUploadService'

export default {
  name: 'EditTask',
  props: {
    visible: { type: Boolean, default: false },
    task: { type: Object, required: true },
    users: { type: Array, default: () => [] }
  },
  emits: ['close', 'saved', 'error'],
  setup(props, { emit }) {
    const isSubmitting = ref(false)
    const dateValidationError = ref('')
    const errors = reactive({
      task_name: '',
      task_desc: '',
      start_date: '',
      end_date: '',
      task_status: '',
      collaborators: '',
      priority_level: ''
    })

    // Toast notification system
    const showToast = ref(false)
    const toastMessage = ref('')
    const toastType = ref('success')
    const toastTimeout = ref(null)

    const fileInput = ref(null)
    const existingAttachments = ref([])
    const attachmentsToDelete = ref([])
    const newAttachments = ref([])
    const attachmentErrors = ref('')
    const maxAttachments = 3

    // Helper function to show toast
    const showToastNotification = (message, type = 'success') => {
      // Clear any existing toast
      if (toastTimeout.value) {
        clearTimeout(toastTimeout.value)
      }

      toastMessage.value = message
      toastType.value = type
      showToast.value = true

      // Auto-hide after 2 seconds
      toastTimeout.value = setTimeout(() => {
        showToast.value = false
      }, 2000)
    }

    const localForm = reactive({
      proj_name: '',
      task_ID: '',
      task_name: '',
      task_desc: '',
      start_date: '',
      end_date: '',
      owner: '',
      assigned_to: [], // This will store user objects with id and name
      task_status: '',
      priority_level: ''
    })

    // Dropdown-related reactive data
    const userSearch = ref('')
    const showDropdown = ref(false)
    const isLoadingUsers = ref(false)
    const highlightedIndex = ref(-1)
    const dropdownCloseTimeout = ref(null)

    const filteredUsers = computed(() => {
      let filtered = props.users.filter(user => {
        // Filter out already selected users
        const isAlreadySelected = localForm.assigned_to.some(assignee => assignee.id === user.id);

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

    const isFormValid = computed(() => {
      const hasErrors = Object.values(errors).some(error => error !== '');
      const hasDateError = Boolean(dateValidationError.value);
      const hasAttachmentError = Boolean(attachmentErrors.value);
      return !hasErrors && !hasDateError && !hasAttachmentError;
    });

    // Cleanup on unmount
    onBeforeUnmount(() => {
      document.removeEventListener('click', handleOutsideClick);
      if (dropdownCloseTimeout.value) {
        clearTimeout(dropdownCloseTimeout.value);
      }
      if (toastTimeout.value) {
        clearTimeout(toastTimeout.value);
      }
    });

    const fillFromProps = () => {
      const t = props.task || {}
      Object.assign(localForm, {
        proj_name: t.proj_name || '',
        task_ID: t.id || t.task_ID || '',
        task_name: t.task_name || '',
        task_desc: t.task_desc || '',
        start_date: t.start_date ? new Date(t.start_date).toISOString().split('T')[0] : '',
        end_date: t.end_date ? new Date(t.end_date).toISOString().split('T')[0] : '',
        owner: t.owner || '',
        assigned_to: [], // Will be populated below
        task_status: t.task_status || '',
        priority_level: t.priority_level !== undefined && t.priority_level !== null
          ? String(t.priority_level)
          : ''
      });

      // Populate assigned_to with user objects
      if (t.assigned_to && Array.isArray(t.assigned_to)) {
        localForm.assigned_to = t.assigned_to.map(userId => {
          const user = props.users.find(u => String(u.id) === String(userId));
          return user ? {
            id: user.id,
            name: user.name,
            email: user.email
          } : null;
        }).filter(user => user !== null);
      }

      existingAttachments.value = Array.isArray(t.attachments)
        ? t.attachments.map(attachment => ({ ...attachment }))
        : []
      attachmentsToDelete.value = []
      newAttachments.value = []
      attachmentErrors.value = ''
      if (fileInput.value) {
        fileInput.value.value = ''
      }

      // Clear errors when form is populated
      Object.keys(errors).forEach(key => {
        errors[key] = '';
      });
      dateValidationError.value = '';
    }

    watch(() => props.task, fillFromProps, { immediate: true, deep: true })

    watch(() => props.visible, (isVisible) => {
      if (isVisible) {
        nextTick(() => {
          fillFromProps()
        })
      } else {
        newAttachments.value = []
        attachmentsToDelete.value = []
        attachmentErrors.value = ''
        if (fileInput.value) {
          fileInput.value.value = ''
        }
      }
    })

    const getSelectedProjectInfo = () => {
      if (!props.task) {
        return { startDate: null, endDate: null, name: null }
      }

      const project = props.task.project || props.task.selectedProject || {}
      const startDate =
        project.start_date ||
        project.startDate ||
        props.task.project_start_date ||
        props.task.proj_start_date ||
        props.task.projectStartDate ||
        null
      const endDate =
        project.end_date ||
        project.endDate ||
        props.task.project_end_date ||
        props.task.proj_end_date ||
        props.task.projectEndDate ||
        null
      const name =
        project.proj_name ||
        project.name ||
        project.project_name ||
        props.task.proj_name ||
        props.task.project_name ||
        null

      return { startDate, endDate, name }
    }

    const getTaskMinStartDate = () => {
      const projectInfo = getSelectedProjectInfo()
      if (projectInfo.startDate) {
        return new Date(projectInfo.startDate).toISOString().split('T')[0]
      }

      return ''
    }

    const getTaskMaxEndDate = () => {
      const projectInfo = getSelectedProjectInfo()

      if (projectInfo.endDate) {
        return new Date(projectInfo.endDate).toISOString().split('T')[0]
      }

      return ''
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

    const attachmentSummary = computed(() => {
      const existingCount = existingAttachments.value.length
      const newCount = newAttachments.value.length
      if (!existingCount && !newCount) {
        return 'No files selected'
      }
      const parts = []
      if (existingCount) {
        parts.push(`${existingCount} existing`)
      }
      if (newCount) {
        parts.push(`${newCount} new`)
      }
      const remaining = maxAttachments - existingCount - newCount
      if (remaining > 0) {
        parts.push(`${remaining} slot${remaining === 1 ? '' : 's'} left`)
      }
      return parts.join(' | ')
    })

    const handleFileSelection = (event) => {
      attachmentErrors.value = ''
      const inputEl = event && event.target ? event.target : null
      const files = inputEl && inputEl.files ? Array.from(inputEl.files) : []
      if (files.length === 0) {
        if (fileInput.value) {
          fileInput.value.value = ''
        }
        return
      }

      const currentCount = existingAttachments.value.length + newAttachments.value.length
      if (currentCount >= maxAttachments) {
        attachmentErrors.value = `Maximum ${maxAttachments} files allowed`
        if (fileInput.value) {
          fileInput.value.value = ''
        }
        return
      }

      let added = false

      for (const file of files) {
        if (existingAttachments.value.length + newAttachments.value.length >= maxAttachments) {
          break
        }

        const validation = fileUploadService.validateFile(file)
        if (!validation.valid) {
          attachmentErrors.value = validation.error
          continue
        }

        newAttachments.value.push({
          file,
          tempId: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
        })
        added = true
      }

      if (!added && !attachmentErrors.value) {
        attachmentErrors.value = 'No files were added'
      }

      if (fileInput.value) {
        fileInput.value.value = ''
      }
    }

    const markExistingAttachmentForRemoval = (index) => {
      if (index < 0 || index >= existingAttachments.value.length) {
        return
      }

      const [removed] = existingAttachments.value.splice(index, 1)
      if (removed) {
        attachmentsToDelete.value.push(removed)
      }
      attachmentErrors.value = ''
    }

    const removeNewAttachment = (index) => {
      if (index < 0 || index >= newAttachments.value.length) {
        return
      }

      newAttachments.value.splice(index, 1)
      attachmentErrors.value = ''
    }

    // Dropdown interaction methods
    const handleInputFocus = () => {
      if (!isLoadingUsers.value) {
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
      if (!showDropdown.value) {
        showDropdown.value = true;
      }
      highlightedIndex.value = -1;
    };

    const toggleDropdown = () => {
      if (isLoadingUsers.value) return;

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
      const dropdownContainer = document.querySelector('.search-dropdown-container');
      if (dropdownContainer && !dropdownContainer.contains(event.target)) {
        closeDropdown();
      }
    };

    const selectUser = (user) => {
      if (isUserSelected(user)) return;

      // Clear any pending close timeout
      if (dropdownCloseTimeout.value) {
        clearTimeout(dropdownCloseTimeout.value);
        dropdownCloseTimeout.value = null;
      }

      // Add user to selected collaborators
      localForm.assigned_to.push({
        id: user.id,
        name: user.name,
        email: user.email
      });

      // Validate collaborators after adding
      validateField('collaborators', localForm.assigned_to);

      // Reset search but DON'T close dropdown
      userSearch.value = '';

      nextTick(() => {
        const input = document.getElementById('assignedTo');
        if (input) {
          input.focus();
        }
        showDropdown.value = true;
      });
    };

    const isUserSelected = (user) => {
      return localForm.assigned_to.some(assignee => assignee.id === user.id);
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

    // Remove assignee method for dropdown (works with objects now)
    const removeAssignee = (index) => {
      localForm.assigned_to.splice(index, 1);
      // Validate collaborators after removing
      validateField('collaborators', localForm.assigned_to);
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

    const validateDates = () => {
      dateValidationError.value = ''
      if (localForm.start_date && localForm.end_date) {
        const start = new Date(localForm.start_date)
        const end = new Date(localForm.end_date)
        if (end <= start) {
          dateValidationError.value = 'End date must be after start date'
          return false
        }
      }
      return true
    }

    const clearError = (field) => { if (errors[field]) errors[field] = '' }

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

      // In edit mode, allow past dates (the task was already created with this date)
      // Only validate against project constraints, not current date
      // So we skip the past date check entirely for edit mode

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

    const validatePriorityLevel = (value) => {
      if (!value || value === '') {
        return 'Priority level is required';
      }

      const numValue = parseInt(value, 10);
      if (Number.isNaN(numValue) || numValue < 1 || numValue > 10) {
        return 'Priority level must be between 1 and 10';
      }

      return '';
    };

    const validateCollaborators = () => '';

    const validateField = (fieldName, value) => {
      switch (fieldName) {
        case 'task_name':
          errors.task_name = validateTaskName(value);
          break;
        case 'task_desc':
          errors.task_desc = validateTaskDescription(value);
          break;
        case 'start_date':
          errors.start_date = validateStartDate(value);
          // Re-validate end date when start date changes
          if (localForm.end_date) {
            errors.end_date = validateEndDate(localForm.end_date, value);
          }
          break;
        case 'end_date':
          errors.end_date = validateEndDate(value, localForm.start_date);
          break;
        case 'task_status':
          errors.task_status = validateTaskStatus(value);
          break;
        case 'priority_level':
          errors.priority_level = validatePriorityLevel(value);
          break;
        case 'collaborators':
          errors.collaborators = validateCollaborators(value);
          break;
      }
    };

    const handleSubmit = async () => {
      if (isSubmitting.value) return

      // Trigger validation for all fields
      validateField('task_name', localForm.task_name);
      validateField('task_desc', localForm.task_desc);
      validateField('start_date', localForm.start_date);
      validateField('end_date', localForm.end_date);
      validateField('task_status', localForm.task_status);
      validateField('priority_level', localForm.priority_level);
      validateField('collaborators', localForm.assigned_to);

      // Check if form is valid
      if (!isFormValid.value) {
        return;
      }

      const totalAttachments = existingAttachments.value.length + newAttachments.value.length
      const allowedLimit = Math.max(maxAttachments, existingAttachments.value.length)
      if (totalAttachments > allowedLimit) {
        attachmentErrors.value = `Maximum ${maxAttachments} files allowed`
        return
      }

      isSubmitting.value = true

      try {
        const id = localForm.task_ID || props.task?.task_ID || props.task?.id
        if (!id) throw new Error('Missing task identifier')

        let uploadedAttachments = []
        if (newAttachments.value.length > 0) {
          const filesToUpload = newAttachments.value.map(item => item.file)
          const currentUser = JSON.parse(sessionStorage.getItem('user') || '{}')
          const userId = currentUser.id || currentUser.user_ID || currentUser.uid || localForm.owner || 'anonymous'
          const taskStorageId = props.task?.id || props.task?.task_ID || localForm.task_ID || id

          try {
            uploadedAttachments = await fileUploadService.uploadMultipleFiles(filesToUpload, taskStorageId, userId)
          } catch (uploadError) {
            attachmentErrors.value = uploadError.message || 'Failed to upload attachments'
            showToastNotification(attachmentErrors.value, 'error')
            return
          }
        }

        const finalAttachments = [
          ...existingAttachments.value.map(attachment => ({ ...attachment })),
          ...uploadedAttachments
        ]

        const payload = {
          proj_name: localForm.proj_name,
          task_ID: localForm.task_ID || props.task?.task_ID || id || '',
          task_name: localForm.task_name.trim(),
          task_desc: localForm.task_desc.trim(),
          start_date: localForm.start_date,
          end_date: localForm.end_date || null,
          owner: localForm.owner,
          assigned_to: localForm.assigned_to.map(user => user.id),
          task_status: localForm.task_status || null,
          priority_level: localForm.priority_level ? parseInt(localForm.priority_level, 10) : null,
          attachments: finalAttachments
        }

        // Status change log
        if ((props.task?.task_status || '') !== (localForm.task_status || '')) {
          payload.status_log = [
            {
              changed_by: 'Current User',
              timestamp: new Date().toISOString(),
              new_status: localForm.task_status || 'Unassigned'
            }
          ]
        }

        const updatePromise = taskService.updateTask(id, payload)
        const timeoutPromise = new Promise((_, reject) => setTimeout(() => reject(new Error('Update timed out')), 3000))
        const updated = await Promise.race([updatePromise, timeoutPromise])

        let deletionError = null
        if (attachmentsToDelete.value.length > 0) {
          const deletions = attachmentsToDelete.value
            .filter(attachment => attachment && attachment.storagePath)
            .map(attachment => fileUploadService.deleteFile(attachment.storagePath))

          if (deletions.length > 0) {
            try {
              await Promise.all(deletions)
            } catch (err) {
              deletionError = err
            }
          }
        }

        existingAttachments.value = finalAttachments
        newAttachments.value = []
        attachmentsToDelete.value = []
        attachmentErrors.value = ''
        if (fileInput.value) {
          fileInput.value.value = ''
        }

        if (deletionError) {
          showToastNotification('Task updated but some attachments could not be deleted', 'error')
        } else {
          showToastNotification('Changes made successfully')
        }

        emit('saved', updated)

        if (!deletionError) {
          setTimeout(() => {
            handleClose()
          }, 500)
        }
      } catch (error) {
        if (!attachmentErrors.value) {
          showToastNotification(error.message || 'Failed to update task', 'error')
        }
      } finally {
        isSubmitting.value = false
      }
    }


    const handleClose = () => emit('close')

    // Get user name by ID from the users array
    const getUserName = (userId) => {
      const user = props.users.find(u => u.id === userId)
      return user ? user.name : 'Unknown User'
    }

    // Computed property for displaying the owner name
    const ownerName = computed(() => {
      if (localForm.owner) {
        return getUserName(localForm.owner)
      }
      return ''
    })

    onMounted(() => {
      document.addEventListener('click', handleOutsideClick);
    });

    return {
      localForm,
      isSubmitting,
      dateValidationError,
      errors,
      showToast,
      toastMessage,
      toastType,
      attachmentErrors,
      maxAttachments,
      attachmentSummary,
      existingAttachments,
      newAttachments,
      fileInput,
      handleFileSelection,
      markExistingAttachmentForRemoval,
      removeNewAttachment,
      userSearch,
      showDropdown,
      isLoadingUsers,
      highlightedIndex,
      filteredUsers,
      isFormValid,
      getSelectedProjectInfo,
      getTaskMinStartDate,
      getTaskMaxEndDate,
      formatDateRange,
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
      removeAssignee,
      formatFileSize,
      getFileIcon,
      getFileTypeColor,
      validateDates,
      clearError,
      validateField,
      handleSubmit,
      handleClose,
      getUserName,
      ownerName
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  z-index: 50;
}

.modal-card {
  width: 100%;
  max-width: 720px;
  max-height: 90vh;
  background: #ffffff;
  border: 1px solid #e5e5e5;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #f3f4f6;
}

.modal-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #111827;
}

.icon-btn {
  background: #ffffff;
  border: 1px solid #d1d1d1;
  border-radius: 6px;
  width: 32px;
  height: 32px;
  cursor: pointer;
  color: #374151;
}

.task-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px;
  flex: 1;
  overflow-y: auto;
}

.form-grid { display: flex; flex-direction: column; gap: 16px; }

.form-group { display: flex; flex-direction: column; gap: 8px; }
.form-label { font-size: 14px; font-weight: 600; color: #000000; }

.form-input, .form-select, .form-textarea {
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

.form-textarea { resize: vertical; min-height: 100px; font-family: inherit; }

.form-input.locked {
  background-color: #f3f4f6;
  color: #374151;
  cursor: not-allowed;
  border-color: #d1d5db;
  pointer-events: none;
  user-select: none;
  opacity: 0.7;
}

.readonly-input {
  background-color: #f8f9fa;
  color: #6c757d;
  cursor: not-allowed;
}

.form-input:focus, .form-select:focus, .form-textarea:focus {
  outline: none;
  border-color: #000000;
  box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.1);
}

.error-message { color: #dc3545; font-size: 12px; }
.input-error { border-color: #dc3545; }

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
  flex-wrap: wrap;
}

.file-input {
  display: none;
}

.file-upload-label {
  background-color: #f5f5f5;
  color: #333333;
  padding: 10px 18px;
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

.file-upload-label.disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.file-status {
  font-size: 14px;
  color: #666666;
}

.file-preview-container {
  margin-top: 16px;
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #e5e5e5;
  border-radius: 6px;
  padding: 12px;
}

.file-preview-container.new-files {
  border-style: dashed;
}

.file-preview-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background-color: #f8f9fa;
  border-radius: 4px;
  margin-bottom: 8px;
  border-left: 4px solid;
}

.file-preview-item:last-child {
  margin-bottom: 0;
}

.file-icon {
  margin-right: 8px;
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
  color: #ffffff;
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

.no-attachments {
  color: #666666;
  font-style: italic;
  text-align: center;
  padding: 16px;
}

.attachment-note {
  color: #666666;
  font-size: 12px;
  font-style: italic;
  margin-top: 8px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 8px;
  border-top: 1px solid #f3f4f6;
}

.btn {
  padding: 12px 20px;
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

.btn-cancel { background-color: #ffffff; color: #666666; border-color: #d1d1d1; }
.btn-cancel:hover { background-color: #f5f5f5; color: #333333; }

.btn-primary { background-color: #000000; color: #ffffff; }
.btn-primary:hover:not(:disabled) { background-color: #333333; }

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

.date-constraint-info {
  font-size: 12px;
  color: #666666;
  margin-top: 4px;
}

@media (max-width: 768px) {
  .form-actions {
    flex-direction: column;
  }
}

/* Toast Notification */
.toast-notification {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 12px 20px;
  border-radius: 8px;
  color: white;
  font-weight: 500;
  font-size: 14px;
  z-index: 9999;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: slideInRight 0.3s ease-out;
}

.toast-notification.toast-success {
  background-color: #10b981;
}

.toast-notification.toast-error {
  background-color: #ef4444;
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
</style>


