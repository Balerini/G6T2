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

      <form class="task-form" @submit.prevent="handleSubmit">
        <div class="form-grid">
          <div class="form-group">
            <label class="form-label" for="taskName">Task Name *</label>
            <input id="taskName" v-model="localForm.task_name" type="text" class="form-input" :class="{ 'input-error': errors.task_name }" required @input="clearError('task_name')" />
            <span v-if="errors.task_name" class="error-message">{{ errors.task_name }}</span>
          </div>

          <div class="form-group">
            <label class="form-label" for="taskDesc">Task Description</label>
            <textarea id="taskDesc" v-model="localForm.task_desc" class="form-textarea" rows="4" placeholder="Describe the task"></textarea>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label" for="startDate">Start Date *</label>
              <input id="startDate" v-model="localForm.start_date" type="date" class="form-input" :class="{ 'input-error': errors.start_date }" required @change="() => { clearError('start_date'); validateDates(); }" />
              <span v-if="errors.start_date" class="error-message">{{ errors.start_date }}</span>
            </div>
            <div class="form-group">
              <label class="form-label" for="endDate">End Date</label>
              <input id="endDate" v-model="localForm.end_date" type="date" class="form-input" :min="localForm.start_date || getCurrentDate()" @change="validateDates" />
              <span v-if="dateValidationError" class="error-message">{{ dateValidationError }}</span>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label" for="taskStatus">Task Status</label>
            <select id="taskStatus" v-model="localForm.task_status" class="form-select">
              <option value="" disabled>Select status</option>
              <option value="Not Started">Not Started</option>
              <option value="In Progress">In Progress</option>
              <option value="On Hold">On Hold</option>
              <option value="Completed">Completed</option>
              <option value="Cancelled">Cancelled</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label" for="assignees">Collaborators (comma-separated)</label>
            <input id="assignees" v-model="assigneesInput" type="text" class="form-input" placeholder="e.g. Alice, Bob" @blur="syncAssignees" />
            <div class="assignee-tags" v-if="localForm.assigned_to && localForm.assigned_to.length">
              <span v-for="(assignee, index) in localForm.assigned_to" :key="index" class="assignee-tag">
                {{ assignee }}
                <button type="button" class="remove-tag" @click="removeAssignee(index)">×</button>
              </span>
            </div>
          </div>
        </div>

        <div class="form-actions">
          <button type="button" class="btn btn-cancel" @click="handleClose" :disabled="isSubmitting">Cancel</button>
          <button type="submit" class="btn btn-primary" :disabled="isSubmitting || !!dateValidationError">
            {{ isSubmitting ? 'Saving...' : 'Save Changes' }}
          </button>
        </div>
      </form>
    </div>
  </div>
  
</template>

<script>
import { reactive, ref, watch } from 'vue'
import { taskService } from '@/services/taskService'

export default {
  name: 'EditTask',
  props: {
    visible: { type: Boolean, default: false },
    task: { type: Object, required: true }
  },
  emits: ['close', 'saved', 'error'],
  setup(props, { emit }) {
    const isSubmitting = ref(false)
    const dateValidationError = ref('')
    const errors = reactive({ task_name: '', start_date: '' })
    const notify = (type, message) => {
      alert(message)
    }

    const localForm = reactive({
      proj_ID: '',
      task_ID: '',
      task_name: '',
      task_desc: '',
      start_date: '',
      end_date: '',
      task_status: '',
      assigned_to: []
    })

    const assigneesInput = ref('')

    const fillFromProps = () => {
      const t = props.task || {}
      localForm.proj_ID = t.proj_ID || ''
      localForm.task_ID = t.task_ID || t.id || ''
      localForm.task_name = t.task_name || ''
      localForm.task_desc = t.task_desc || ''
      localForm.start_date = t.start_date || ''
      localForm.end_date = t.end_date || ''
      localForm.task_status = t.task_status || ''
      localForm.assigned_to = Array.isArray(t.assigned_to) ? [...t.assigned_to] : []
      assigneesInput.value = localForm.assigned_to.join(', ')
      dateValidationError.value = ''
    }

    watch(() => props.task, fillFromProps, { immediate: true })

    const getCurrentDate = () => {
      const today = new Date()
      return today.toISOString().split('T')[0]
    }

    const syncAssignees = () => {
      if (!assigneesInput.value) {
        localForm.assigned_to = []
        return
      }
      localForm.assigned_to = assigneesInput.value
        .split(',')
        .map(s => s.trim())
        .filter(Boolean)
    }

    const removeAssignee = (index) => {
      localForm.assigned_to.splice(index, 1)
      assigneesInput.value = localForm.assigned_to.join(', ')
    }

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

    const handleClose = () => emit('close')

    const clearError = (field) => { if (errors[field]) errors[field] = '' }

    const validateRequired = () => {
      let valid = true
      if (!localForm.task_name.trim()) { errors.task_name = 'Task name is required'; valid = false }
      if (!localForm.start_date) { errors.start_date = 'Start date is required'; valid = false }
      return valid
    }

    const handleSubmit = async () => {
      if (isSubmitting.value) return
      if (localForm.end_date && !validateDates()) return
      if (!validateRequired()) { notify('error', 'Please fix the highlighted fields'); return }

      isSubmitting.value = true
      try {
        const id = localForm.task_ID || props.task?.task_ID || props.task?.id
        if (!id) throw new Error('Missing task identifier')

        const payload = {
          proj_ID: localForm.proj_ID,
          task_ID: localForm.task_ID,
          task_name: localForm.task_name.trim(),
          task_desc: localForm.task_desc.trim(),
          start_date: localForm.start_date,
          end_date: localForm.end_date || null,
          task_status: localForm.task_status || null,
          assigned_to: [...localForm.assigned_to]
        }

        // Status change log
        if ((props.task?.task_status || '') !== (localForm.task_status || '')) {
          payload.status_log = [
            {
              changed_by: 'Current User',
              timestamp: new Date().toISOString(),
              new_status: localForm.task_status || 'Not Started'
            }
          ]
        }

        const updatePromise = taskService.updateTask(id, payload)

        const timeoutPromise = new Promise((_, reject) => setTimeout(() => reject(new Error('Update timed out')), 3000))

        const updated = await Promise.race([updatePromise, timeoutPromise])
        notify('success', 'Task updated successfully')
        emit('saved', updated)
        handleClose()
      } catch (error) {
        notify('error', error.message || 'Failed to update task')
        emit('error', error.message || 'Failed to update task')
      } finally {
        isSubmitting.value = false
      }
    }

    return {
      localForm,
      isSubmitting,
      dateValidationError,
      errors,
      assigneesInput,
      getCurrentDate,
      syncAssignees,
      removeAssignee,
      clearError,
      validateDates,
      handleSubmit,
      handleClose
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
  background: #ffffff;
  border: 1px solid #e5e5e5;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.15);
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
}

.form-grid { display: flex; flex-direction: column; gap: 16px; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }

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

.form-input:focus, .form-select:focus, .form-textarea:focus {
  outline: none;
  border-color: #000000;
  box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.1);
}

.error-message { color: #dc3545; font-size: 12px; }
.input-error { border-color: #dc3545; }

.assignee-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.assignee-tag { display: inline-flex; align-items: center; background-color: #f5f5f5; color: #333333; padding: 6px 12px; border-radius: 20px; font-size: 14px; gap: 8px; }
.remove-tag { background: none; border: none; color: #666666; font-size: 16px; cursor: pointer; padding: 0; line-height: 1; }
.remove-tag:hover { color: #000000; }

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

.btn-cancel { background-color: #ffffff; color: #666666; border-color: #d1d1d1; }
.btn-cancel:hover { background-color: #f5f5f5; color: #333333; }

.btn-primary { background-color: #000000; color: #ffffff; }
.btn-primary:hover { background-color: #333333; }

@media (max-width: 768px) {
  .form-row { grid-template-columns: 1fr; }
}
</style>


