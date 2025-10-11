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

          <!-- Owner with Transfer Ownership -->
          <div class="form-group">
            <label class="form-label" for="owner">Owner</label>
            <div class="owner-field-container">
              <input
                id="owner"
                v-model="ownerName"
                type="text"
                class="form-input readonly-input owner-input"
                readonly
                :placeholder="'Auto-populated from current user'"
              />
              <button
                type="button"
                class="transfer-ownership-btn"
                @click="showTransferOwnership = true"
                :disabled="isSubmitting"
                title="Transfer ownership of this task"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
                  <circle cx="9" cy="7" r="4"/>
                  <path d="M22 21v-2a4 4 0 0 0-3-3.87"/>
                  <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                  <polyline points="17 11 22 6 17 1"/>
                </svg>
                Transfer
              </button>
            </div>
          </div>

          <!-- Transfer Ownership Component -->
          <TransferOwnership
            :visible="showTransferOwnership"
            :task="task"
            :users="users"
            :task-collaborators="localForm.assignee || []"
            @close="showTransferOwnership = false"
            @transfer-success="handleTransferSuccess"
            @transfer-error="handleTransferError"
          />

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

          <!-- Recurrence -->
          <div class="form-group recurrence-section">
            <div class="recurrence-toggle-row">
              <input
                id="editRecurrenceToggle"
                type="checkbox"
                class="recurrence-toggle-input"
                v-model="localForm.recurrence.enabled"
                @change="handleRecurrenceToggle"
              />
              <label class="recurrence-toggle-label" for="editRecurrenceToggle">
                Make this a recurring task
              </label>
            </div>
            <p class="recurrence-helper-text">
              Schedule this task to repeat automatically on a cadence.
            </p>

            <div v-if="localForm.recurrence.enabled" class="recurrence-config">
              <div class="recurrence-field">
                <label class="form-label" for="editRecurrenceFrequency">Frequency *</label>
                <select
                  id="editRecurrenceFrequency"
                  class="form-select"
                  v-model="localForm.recurrence.frequency"
                  :class="{ 'input-error': errors.recurrence_frequency }"
                  @change="handleRecurrenceFrequencyChange"
                >
                  <option value="" disabled>Select frequency</option>
                  <option
                    v-for="option in RECURRENCE_FREQUENCIES"
                    :key="`edit-recurrence-frequency-${option.value}`"
                    :value="option.value"
                  >
                    {{ option.label }}
                  </option>
                </select>
                <span v-if="errors.recurrence_frequency" class="error-message">
                  {{ errors.recurrence_frequency }}
                </span>
              </div>

              <div class="recurrence-field">
                <label class="form-label" for="editRecurrenceInterval">Repeat every</label>
                <div
                  class="recurrence-inline-group"
                  v-if="localForm.recurrence.frequency !== 'custom'"
                >
                  <input
                    id="editRecurrenceInterval"
                    type="number"
                    min="1"
                    class="form-input"
                    :class="{ 'input-error': errors.recurrence_interval }"
                    v-model="localForm.recurrence.interval"
                    @input="handleRecurrenceIntervalChange"
                  />
                  <span class="recurrence-interval-suffix">{{ recurrenceIntervalSuffix }}</span>
                </div>

                <div
                  class="recurrence-inline-group"
                  v-else
                >
                  <input
                    id="editRecurrenceIntervalCustom"
                    type="number"
                    min="1"
                    class="form-input"
                    :class="{ 'input-error': errors.recurrence_interval }"
                    v-model="localForm.recurrence.interval"
                    @input="handleRecurrenceIntervalChange"
                  />
                  <select
                    class="form-select recurrence-unit-select"
                    :class="{ 'input-error': errors.recurrence_custom_unit }"
                    v-model="localForm.recurrence.customUnit"
                    @change="handleRecurrenceCustomUnitChange"
                  >
                    <option
                      v-for="unit in CUSTOM_INTERVAL_UNITS"
                      :key="`edit-custom-unit-${unit.value}`"
                      :value="unit.value"
                    >
                      {{ unit.label }}
                    </option>
                  </select>
                </div>

                <span v-if="errors.recurrence_interval" class="error-message">
                  {{ errors.recurrence_interval }}
                </span>
                <span v-if="errors.recurrence_custom_unit" class="error-message">
                  {{ errors.recurrence_custom_unit }}
                </span>
              </div>

              <div
                v-if="localForm.recurrence.frequency === 'weekly'"
                class="recurrence-field"
              >
                <label class="form-label">Repeats on</label>
                <div class="weekday-selector">
                  <label
                    v-for="day in WEEKLY_DAY_OPTIONS"
                    :key="`edit-weekday-${day.value}`"
                    class="weekday-option"
                  >
                    <input
                      type="checkbox"
                      :value="day.value"
                      v-model="localForm.recurrence.weeklyDays"
                      @change="handleWeeklyDaysChange"
                    />
                    <span>{{ day.label }}</span>
                  </label>
                </div>
                <span v-if="errors.recurrence_weekly_days" class="error-message">
                  {{ errors.recurrence_weekly_days }}
                </span>
              </div>

              <div
                v-if="localForm.recurrence.frequency === 'monthly'"
                class="recurrence-field"
              >
                <label class="form-label" for="editRecurrenceMonthlyDay">Day of month</label>
                <input
                  id="editRecurrenceMonthlyDay"
                  type="number"
                  min="1"
                  max="31"
                  class="form-input"
                  :class="{ 'input-error': errors.recurrence_monthly_day }"
                  v-model="localForm.recurrence.monthlyDay"
                  @input="handleMonthlyDayChange"
                />
                <span v-if="errors.recurrence_monthly_day" class="error-message">
                  {{ errors.recurrence_monthly_day }}
                </span>
              </div>

              <div class="recurrence-field">
                <label class="form-label">Ends</label>
                <div class="recurrence-radio-group">
                  <label class="radio-option">
                    <input
                      type="radio"
                      value="never"
                      v-model="localForm.recurrence.endCondition"
                      @change="handleRecurrenceEndConditionChange"
                    />
                    <span>Never</span>
                  </label>
                  <label class="radio-option">
                    <input
                      type="radio"
                      value="after"
                      v-model="localForm.recurrence.endCondition"
                      @change="handleRecurrenceEndConditionChange"
                    />
                    <span>After</span>
                  </label>
                  <label class="radio-option">
                    <input
                      type="radio"
                      value="onDate"
                      v-model="localForm.recurrence.endCondition"
                      @change="handleRecurrenceEndConditionChange"
                    />
                    <span>On date</span>
                  </label>
                </div>

                <div
                  v-if="localForm.recurrence.endCondition === 'after'"
                  class="recurrence-secondary-field"
                >
                  <input
                    type="number"
                    min="1"
                    class="form-input small-input"
                    v-model="localForm.recurrence.endAfterOccurrences"
                    @input="handleRecurrenceOccurrencesChange"
                  />
                  <span class="secondary-label">occurrence(s)</span>
                </div>

                <div
                  v-else-if="localForm.recurrence.endCondition === 'onDate'"
                  class="recurrence-secondary-field"
                >
                  <input
                    type="date"
                    class="form-input"
                    :min="recurrenceEndDateMin"
                    v-model="localForm.recurrence.endDate"
                    @change="handleRecurrenceEndDateChange"
                  />
                </div>

                <span v-if="errors.recurrence_end" class="error-message">
                  {{ errors.recurrence_end }}
                </span>
              </div>

              <div v-if="recurrenceSummary" class="recurrence-summary">
                <span class="summary-label">Summary:</span>
                <span>{{ recurrenceSummary }}</span>
              </div>
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
import TransferOwnership from './TransferOwnership.vue'

export default {
  name: 'EditTask',
  components: {
    TransferOwnership
  },
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
      priority_level: '',
      recurrence_frequency: '',
      recurrence_interval: '',
      recurrence_weekly_days: '',
      recurrence_monthly_day: '',
      recurrence_custom_unit: '',
      recurrence_end: ''
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

    const getCurrentDate = () => {
      const today = new Date()
      const sgTime = new Date(today.toLocaleString('en-US', { timeZone: 'Asia/Singapore' }))
      return sgTime.toISOString().split('T')[0]
    }

    const getUserName = (userId) => {
      const user = props.users.find(u => String(u.id) === String(userId));
      return user ? user.name : 'Unknown User';
    }

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

    const createDefaultRecurrence = () => ({
      enabled: false,
      frequency: '',
      interval: 1,
      weeklyDays: [],
      monthlyDay: '',
      customUnit: 'days',
      endCondition: 'never',
      endAfterOccurrences: '',
      endDate: ''
    })

    const RECURRENCE_FREQUENCIES = [
      { value: 'daily', label: 'Daily' },
      { value: 'weekly', label: 'Weekly' },
      { value: 'monthly', label: 'Monthly' },
      { value: 'custom', label: 'Custom Interval' }
    ]

    const WEEKLY_DAY_OPTIONS = [
      { value: 'mon', label: 'Mon' },
      { value: 'tue', label: 'Tue' },
      { value: 'wed', label: 'Wed' },
      { value: 'thu', label: 'Thu' },
      { value: 'fri', label: 'Fri' },
      { value: 'sat', label: 'Sat' },
      { value: 'sun', label: 'Sun' }
    ]

    const CUSTOM_INTERVAL_UNITS = [
      { value: 'days', label: 'Day(s)' },
      { value: 'weeks', label: 'Week(s)' },
      { value: 'months', label: 'Month(s)' }
    ]

    const CUSTOM_UNIT_SUMMARY_LABELS = {
      days: 'day(s)',
      weeks: 'week(s)',
      months: 'month(s)'
    }

    const RECURRENCE_FIELD_KEYS = [
      'recurrence_frequency',
      'recurrence_interval',
      'recurrence_weekly_days',
      'recurrence_monthly_day',
      'recurrence_custom_unit',
      'recurrence_end'
    ]

    const recurrenceTouched = reactive({
      frequency: false,
      interval: false,
      weeklyDays: false,
      monthlyDay: false,
      customUnit: false,
      end: false
    })

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
      priority_level: '',
      recurrence: createDefaultRecurrence()
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

      localForm.proj_name = t.proj_name || ''
      localForm.task_ID = t.id || t.task_ID || ''
      localForm.task_name = t.task_name || ''
      localForm.task_desc = t.task_desc || ''
      localForm.start_date = t.start_date ? new Date(t.start_date).toISOString().split('T')[0] : ''
      localForm.end_date = t.end_date ? new Date(t.end_date).toISOString().split('T')[0] : ''
      localForm.owner = t.owner || ''
      localForm.task_status = t.task_status || ''
      localForm.priority_level = t.priority_level !== undefined && t.priority_level !== null
        ? String(t.priority_level)
        : ''

      // Reset assigned_to before repopulating
      localForm.assigned_to = []

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

      // Sync recurrence details without replacing the reactive object reference
      const normalizedRecurrence = normalizeRecurrence(t.recurrence)
      Object.assign(localForm.recurrence, normalizedRecurrence)

      existingAttachments.value = Array.isArray(t.attachments)
        ? t.attachments.map(attachment => ({ ...attachment }))
        : []
      attachmentsToDelete.value = []
      newAttachments.value = []
      attachmentErrors.value = ''
      if (fileInput.value) {
        fileInput.value.value = ''
      }

      clearRecurrenceValidation()
      if (localForm.recurrence.enabled) {
        if (localForm.recurrence.frequency === 'weekly' && localForm.recurrence.weeklyDays.length === 0) {
          const defaultDay = deriveWeekdayFromDate(localForm.start_date) || 'mon'
          localForm.recurrence.weeklyDays = [defaultDay]
        }
        if (localForm.recurrence.frequency === 'monthly' && !localForm.recurrence.monthlyDay) {
          localForm.recurrence.monthlyDay = deriveDefaultMonthlyDay()
        }
        validateRecurrence(false)
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

    watch(() => localForm.start_date, (newStart) => {
      if (!localForm.recurrence.enabled) {
        return
      }

      if (localForm.recurrence.frequency === 'monthly' && !localForm.recurrence.monthlyDay) {
        localForm.recurrence.monthlyDay = deriveDefaultMonthlyDay()
      }

      if (localForm.recurrence.frequency === 'weekly' && localForm.recurrence.weeklyDays.length === 0) {
        const defaultDay = deriveWeekdayFromDate(newStart)
        if (defaultDay) {
          localForm.recurrence.weeklyDays = [defaultDay]
        }
      }

      if (
        localForm.recurrence.endCondition === 'onDate' &&
        localForm.recurrence.endDate &&
        newStart &&
        new Date(localForm.recurrence.endDate) < new Date(newStart)
      ) {
        localForm.recurrence.endDate = newStart
      }

      validateRecurrence(false)
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

    // Transfer ownership related data
    const showTransferOwnership = ref(false)

    // Transfer ownership event handlers
    const handleTransferSuccess = (payload) => {
      // Update the local form with the new owner
      localForm.owner = payload.newOwnerId
      
      // Show success toast
      showToastNotification(payload.message, 'success')
      
      // Close the transfer modal
      showTransferOwnership.value = false
      
      // Optionally emit an event to parent component
      emit('owner-transferred', payload)
    }

    const handleTransferError = (errorMessage) => {
      // Show error toast
      showToastNotification(errorMessage, 'error')
      
      // Keep the transfer modal open so user can try again
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

    function clearRecurrenceValidation() {
      RECURRENCE_FIELD_KEYS.forEach((key) => {
        errors[key] = '';
      });
      recurrenceTouched.frequency = false;
      recurrenceTouched.interval = false;
      recurrenceTouched.weeklyDays = false;
      recurrenceTouched.monthlyDay = false;
      recurrenceTouched.customUnit = false;
      recurrenceTouched.end = false;
    }

    function deriveWeekdayFromDate(dateString) {
      if (!dateString) {
        return null;
      }
      const date = new Date(`${dateString}T00:00:00`);
      const map = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'];
      return map[date.getDay()] || null;
    }

    function deriveDefaultMonthlyDay() {
      if (!localForm.start_date) {
        return '1';
      }
      const date = new Date(`${localForm.start_date}T00:00:00`);
      return String(date.getDate());
    }

    function validateRecurrence(markAllTouched = false) {
      if (!localForm.recurrence.enabled) {
        clearRecurrenceValidation();
        return true;
      }

      if (markAllTouched) {
        recurrenceTouched.frequency = true;
        recurrenceTouched.interval = true;
        recurrenceTouched.end = true;
        if (localForm.recurrence.frequency === 'weekly') {
          recurrenceTouched.weeklyDays = true;
        }
        if (localForm.recurrence.frequency === 'monthly') {
          recurrenceTouched.monthlyDay = true;
        }
        if (localForm.recurrence.frequency === 'custom') {
          recurrenceTouched.customUnit = true;
        }
      }

      errors.recurrence_frequency = recurrenceTouched.frequency
        ? (localForm.recurrence.frequency ? '' : 'Select a recurrence frequency')
        : '';

      const intervalNumber = Number(localForm.recurrence.interval);
      errors.recurrence_interval = recurrenceTouched.interval
        ? (!Number.isInteger(intervalNumber) || intervalNumber < 1 ? 'Interval must be at least 1' : '')
        : '';

      if (localForm.recurrence.frequency === 'weekly') {
        errors.recurrence_weekly_days = recurrenceTouched.weeklyDays
          ? (localForm.recurrence.weeklyDays.length > 0 ? '' : 'Select at least one day')
          : '';
      } else {
        errors.recurrence_weekly_days = '';
        recurrenceTouched.weeklyDays = false;
      }

      if (localForm.recurrence.frequency === 'monthly') {
        const monthlyValue = Number(localForm.recurrence.monthlyDay);
        errors.recurrence_monthly_day = recurrenceTouched.monthlyDay
          ? (Number.isFinite(monthlyValue) && monthlyValue >= 1 && monthlyValue <= 31
            ? ''
            : 'Enter a day between 1 and 31')
          : '';
      } else {
        errors.recurrence_monthly_day = '';
        recurrenceTouched.monthlyDay = false;
      }

      if (localForm.recurrence.frequency === 'custom') {
        errors.recurrence_custom_unit = recurrenceTouched.customUnit
          ? (localForm.recurrence.customUnit ? '' : 'Select a custom interval unit')
          : '';
      } else {
        errors.recurrence_custom_unit = '';
        recurrenceTouched.customUnit = false;
      }

      let endError = '';
      if (localForm.recurrence.endCondition === 'after') {
        const occurrences = Number(localForm.recurrence.endAfterOccurrences);
        if (!Number.isInteger(occurrences) || occurrences < 1) {
          endError = 'Occurrences must be at least 1';
        }
      } else if (localForm.recurrence.endCondition === 'onDate') {
        if (!localForm.recurrence.endDate) {
          endError = 'Select an end date';
        } else if (
          localForm.start_date &&
          new Date(localForm.recurrence.endDate) < new Date(localForm.start_date)
        ) {
          endError = 'End date must be on or after the start date';
        }
      } else if (!localForm.recurrence.endCondition) {
        endError = 'Choose how the recurrence ends';
      }

      errors.recurrence_end = recurrenceTouched.end ? endError : '';

      return RECURRENCE_FIELD_KEYS.every((key) => errors[key] === '');
    }

    const handleRecurrenceToggle = () => {
      if (!localForm.recurrence.enabled) {
        Object.assign(localForm.recurrence, createDefaultRecurrence());
        clearRecurrenceValidation();
        return;
      }

      clearRecurrenceValidation();

      if (!localForm.recurrence.frequency) {
        localForm.recurrence.frequency = 'daily';
      }

      if (!localForm.recurrence.interval || Number(localForm.recurrence.interval) < 1) {
        localForm.recurrence.interval = 1;
      }

      if (!localForm.recurrence.endCondition) {
        localForm.recurrence.endCondition = 'never';
      }

      if (!localForm.recurrence.customUnit) {
        localForm.recurrence.customUnit = 'days';
      }

      if (localForm.recurrence.frequency === 'weekly' && localForm.recurrence.weeklyDays.length === 0) {
        const defaultDay = deriveWeekdayFromDate(localForm.start_date) || 'mon';
        localForm.recurrence.weeklyDays = [defaultDay];
      }

      if (localForm.recurrence.frequency === 'monthly' && !localForm.recurrence.monthlyDay) {
        localForm.recurrence.monthlyDay = deriveDefaultMonthlyDay();
      }

      validateRecurrence(false);
    };

    const handleRecurrenceFrequencyChange = () => {
      recurrenceTouched.frequency = true;

      if (localForm.recurrence.frequency !== 'weekly') {
        localForm.recurrence.weeklyDays = [];
        errors.recurrence_weekly_days = '';
        recurrenceTouched.weeklyDays = false;
      } else if (localForm.recurrence.weeklyDays.length === 0) {
        const defaultDay = deriveWeekdayFromDate(localForm.start_date) || 'mon';
        localForm.recurrence.weeklyDays = [defaultDay];
      }

      if (localForm.recurrence.frequency !== 'monthly') {
        localForm.recurrence.monthlyDay = '';
        errors.recurrence_monthly_day = '';
        recurrenceTouched.monthlyDay = false;
      } else if (!localForm.recurrence.monthlyDay) {
        localForm.recurrence.monthlyDay = deriveDefaultMonthlyDay();
      }

      if (localForm.recurrence.frequency !== 'custom') {
        localForm.recurrence.customUnit = 'days';
        errors.recurrence_custom_unit = '';
        recurrenceTouched.customUnit = false;
      }

      validateRecurrence(false);
    };

    const handleRecurrenceIntervalChange = () => {
      recurrenceTouched.interval = true;
      if (!localForm.recurrence.interval || Number(localForm.recurrence.interval) < 1) {
        localForm.recurrence.interval = 1;
      } else {
        localForm.recurrence.interval = Math.floor(Number(localForm.recurrence.interval));
      }
      validateRecurrence(false);
    };

    const handleWeeklyDaysChange = () => {
      recurrenceTouched.weeklyDays = true;
      validateRecurrence(false);
    };

    const handleMonthlyDayChange = () => {
      recurrenceTouched.monthlyDay = true;
      if (localForm.recurrence.monthlyDay) {
        let value = Number(localForm.recurrence.monthlyDay);
        if (value < 1) value = 1;
        if (value > 31) value = 31;
        localForm.recurrence.monthlyDay = String(value);
      }
      validateRecurrence(false);
    };

    const handleRecurrenceCustomUnitChange = () => {
      recurrenceTouched.customUnit = true;
      validateRecurrence(false);
    };

    const handleRecurrenceEndConditionChange = () => {
      recurrenceTouched.end = true;

      if (localForm.recurrence.endCondition === 'after') {
        if (!localForm.recurrence.endAfterOccurrences) {
          localForm.recurrence.endAfterOccurrences = '1';
        }
        localForm.recurrence.endDate = '';
      } else if (localForm.recurrence.endCondition === 'onDate') {
        localForm.recurrence.endAfterOccurrences = '';
        if (!localForm.recurrence.endDate) {
          localForm.recurrence.endDate = localForm.start_date || getCurrentDate();
        }
      } else {
        localForm.recurrence.endAfterOccurrences = '';
        localForm.recurrence.endDate = '';
      }

      validateRecurrence(false);
    };

    const handleRecurrenceOccurrencesChange = () => {
      recurrenceTouched.end = true;
      if (localForm.recurrence.endAfterOccurrences) {
        let value = Number(localForm.recurrence.endAfterOccurrences);
        if (value < 1) value = 1;
        localForm.recurrence.endAfterOccurrences = String(Math.floor(value));
      }
      validateRecurrence(false);
    };

    const handleRecurrenceEndDateChange = () => {
      recurrenceTouched.end = true;
      validateRecurrence(false);
    };

    const recurrenceIntervalSuffix = computed(() => {
      if (!localForm.recurrence.enabled) {
        return 'day(s)';
      }

      switch (localForm.recurrence.frequency) {
        case 'weekly':
          return 'week(s)';
        case 'monthly':
          return 'month(s)';
        default:
          return 'day(s)';
      }
    });

    const recurrenceEndDateMin = computed(() => localForm.start_date || getCurrentDate());

    const recurrenceSummary = computed(() => {
      if (!localForm.recurrence.enabled || !localForm.recurrence.frequency) {
        return '';
      }

      const intervalNumber = Number(localForm.recurrence.interval) || 1;
      const plural = (value, base) => `${base}${value === 1 ? '' : 's'}`;
      let summary = '';

      switch (localForm.recurrence.frequency) {
        case 'daily':
          summary = `Repeats every ${intervalNumber} ${plural(intervalNumber, 'day')}`;
          break;
        case 'weekly': {
          const dayLabels = localForm.recurrence.weeklyDays.map((day) => {
            const option = WEEKLY_DAY_OPTIONS.find(opt => opt.value === day);
            return option ? option.label : day;
          });
          const daysText = dayLabels.length > 0 ? dayLabels.join(', ') : 'no days selected';
          summary = `Repeats every ${intervalNumber} ${plural(intervalNumber, 'week')} on ${daysText}`;
          break;
        }
        case 'monthly':
          summary = `Repeats every ${intervalNumber} ${plural(intervalNumber, 'month')} on day ${localForm.recurrence.monthlyDay || '?'}`;
          break;
        case 'custom': {
          const customUnit = localForm.recurrence.customUnit || 'days';
          const unitLabel = CUSTOM_UNIT_SUMMARY_LABELS[customUnit] || 'day(s)';
          summary = `Repeats every ${intervalNumber} ${unitLabel}`;
          break;
        }
        default:
          summary = '';
      }

      if (!summary) {
        return '';
      }

      if (localForm.recurrence.endCondition === 'after') {
        const occurrences = Number(localForm.recurrence.endAfterOccurrences) || 0;
        summary += ` - Ends after ${occurrences} occurrence${occurrences === 1 ? '' : 's'}`;
      } else if (localForm.recurrence.endCondition === 'onDate' && localForm.recurrence.endDate) {
        const formatted = new Date(localForm.recurrence.endDate).toLocaleDateString('en-SG', {
          day: '2-digit',
          month: 'short',
          year: 'numeric'
        });
        summary += ` - Ends on ${formatted}`;
      } else {
        summary += ' - No end date';
      }

      return summary;
    });

    const buildRecurrencePayload = () => {
      if (!localForm.recurrence?.enabled) {
        return { enabled: false };
      }

      const intervalValue = Number(localForm.recurrence.interval) || 1;
      const payload = {
        enabled: true,
        frequency: localForm.recurrence.frequency,
        interval: intervalValue,
        endCondition: localForm.recurrence.endCondition,
      };

      if (localForm.recurrence.frequency === 'weekly') {
        payload.weeklyDays = [...localForm.recurrence.weeklyDays];
      }

      if (localForm.recurrence.frequency === 'monthly') {
        payload.monthlyDay = localForm.recurrence.monthlyDay
          ? Number(localForm.recurrence.monthlyDay)
          : null;
      }

      if (localForm.recurrence.frequency === 'custom') {
        payload.customUnit = localForm.recurrence.customUnit;
      }

      if (localForm.recurrence.endCondition === 'after') {
        payload.endAfterOccurrences = localForm.recurrence.endAfterOccurrences
          ? Number(localForm.recurrence.endAfterOccurrences)
          : null;
      } else if (localForm.recurrence.endCondition === 'onDate') {
        payload.endDate = localForm.recurrence.endDate || null;
      }

      return payload;
    };

    function normalizeRecurrence(recurrence) {
      const defaults = createDefaultRecurrence();
      if (!recurrence || !recurrence.enabled) {
        return defaults;
      }

      return {
        ...defaults,
        enabled: Boolean(recurrence.enabled),
        frequency: recurrence.frequency || '',
        interval: recurrence.interval || 1,
        weeklyDays: Array.isArray(recurrence.weeklyDays) ? [...recurrence.weeklyDays] : [],
        monthlyDay: recurrence.monthlyDay !== undefined && recurrence.monthlyDay !== null
          ? String(recurrence.monthlyDay)
          : '',
        customUnit: recurrence.customUnit || 'days',
        endCondition: recurrence.endCondition || 'never',
        endAfterOccurrences: recurrence.endAfterOccurrences
          ? String(recurrence.endAfterOccurrences)
          : '',
        endDate: recurrence.endDate || ''
      };
    }

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
        case 'recurrence':
          validateRecurrence(true);
          break;
        case 'recurrence_frequency':
          recurrenceTouched.frequency = true;
          validateRecurrence(false);
          break;
        case 'recurrence_interval':
          recurrenceTouched.interval = true;
          validateRecurrence(false);
          break;
        case 'recurrence_weekly_days':
          recurrenceTouched.weeklyDays = true;
          validateRecurrence(false);
          break;
        case 'recurrence_monthly_day':
          recurrenceTouched.monthlyDay = true;
          validateRecurrence(false);
          break;
        case 'recurrence_custom_unit':
          recurrenceTouched.customUnit = true;
          validateRecurrence(false);
          break;
        case 'recurrence_end':
          recurrenceTouched.end = true;
          validateRecurrence(false);
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
      validateField('recurrence', localForm.recurrence);

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
          attachments: finalAttachments,
          recurrence: buildRecurrencePayload()
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
      RECURRENCE_FREQUENCIES,
      WEEKLY_DAY_OPTIONS,
      CUSTOM_INTERVAL_UNITS,
      recurrenceIntervalSuffix,
      recurrenceEndDateMin,
      recurrenceSummary,
      handleRecurrenceToggle,
      handleRecurrenceFrequencyChange,
      handleRecurrenceIntervalChange,
      handleWeeklyDaysChange,
      handleMonthlyDayChange,
      handleRecurrenceCustomUnitChange,
      handleRecurrenceEndConditionChange,
      handleRecurrenceOccurrencesChange,
      handleRecurrenceEndDateChange,
      formatFileSize,
      getFileIcon,
      getFileTypeColor,
      validateDates,
      clearError,
      validateField,
      handleSubmit,
      handleClose,
      getUserName,
      ownerName,
      showTransferOwnership,
      handleTransferSuccess,
      handleTransferError,
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

.recurrence-section {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  background-color: #fafafa;
}

.recurrence-toggle-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.recurrence-toggle-input {
  width: 18px;
  height: 18px;
}

.recurrence-toggle-label {
  font-weight: 600;
  color: #333;
}

.recurrence-helper-text {
  margin: 8px 0 16px;
  font-size: 0.875rem;
  color: #555;
}

.recurrence-config {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.recurrence-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.recurrence-inline-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.recurrence-interval-suffix {
  font-size: 0.9rem;
  color: #555;
}

.recurrence-unit-select {
  max-width: 160px;
}

.weekday-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.weekday-option {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border: 1px solid #d0d0d0;
  border-radius: 6px;
  background-color: #fff;
  cursor: pointer;
  font-size: 0.85rem;
}

.weekday-option input {
  margin: 0;
}

.recurrence-radio-group {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.radio-option {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.9rem;
  color: #444;
}

.recurrence-secondary-field {
  display: flex;
  align-items: center;
  gap: 8px;
}

.recurrence-secondary-field .small-input {
  max-width: 120px;
}

.secondary-label {
  font-size: 0.85rem;
  color: #555;
}

.recurrence-summary {
  padding: 12px;
  border-radius: 6px;
  background-color: #eef5ff;
  color: #1a3a6b;
  font-size: 0.9rem;
}

.summary-label {
  font-weight: 600;
  margin-right: 6px;
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

/* Owner field with transfer button */
.owner-field-container {
  display: flex;
  gap: 8px;
  align-items: center;
}

.owner-input {
  flex: 1;
}

.transfer-ownership-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  background-color: #5d82ee; 
  border: 1px solid #5d82ee;
  border-radius: 6px;
  color: white; /* White text for contrast */
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.transfer-ownership-btn:hover:not(:disabled) {
  background-color: #4864e2; 
  border-color: #4864e2;
  transform: translateY(-1px); /* Subtle lift effect */
  box-shadow: 0 4px 8px rgba(99, 102, 241, 0.3);
}

.transfer-ownership-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(99, 102, 241, 0.2);
}

.transfer-ownership-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.transfer-ownership-btn svg {
  flex-shrink: 0;
}
</style>


