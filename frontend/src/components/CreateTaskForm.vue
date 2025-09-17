<template>
  <form class="task-form">
    <!-- Task Name -->
    <div class="form-group">
      <label class="form-label" for="taskName">Task Name *</label>
      <input
        id="taskName"
        type="text"
        class="form-input"
        placeholder="Enter task name"
        required
      />
    </div>

    <!-- Subtasks Checkbox -->
    <div class="form-group checkbox-group">
      <label class="checkbox-container">
        <input type="checkbox" class="checkbox-input" />
        <span class="checkbox-checkmark"></span>
        <span class="checkbox-label">Subtasks will have respective inputs</span>
      </label>
    </div>

    <!-- Deadline -->
    <div class="form-group">
      <label class="form-label" for="deadline">Deadline *</label>
      <input
        id="deadline"
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
        type="text"
        class="form-input"
        placeholder="Enter staff member name"
      />
      <div class="collaborator-tags">
        <!-- Example tags - these would be dynamic -->
        <span class="collaborator-tag">
          John Doe
          <button type="button" class="remove-tag">×</button>
        </span>
        <span class="collaborator-tag">
          Jane Smith
          <button type="button" class="remove-tag">×</button>
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
        />
        <label for="attachments" class="file-upload-label">
          Choose Files
        </label>
        <span class="file-status">No file chosen</span>
      </div>
    </div>

    <!-- Status -->
    <div class="form-group">
      <label class="form-label" for="status">Status *</label>
      <select id="status" class="form-select" required>
        <option value="" disabled selected>Select status</option>
        <option value="unassigned">Unassigned</option>
        <option value="ongoing">Ongoing</option>
        <option value="under-review">Under Review</option>
        <option value="completed">Completed</option>
      </select>
    </div>

    <!-- Form Actions -->
    <div class="form-actions">
      <button type="button" class="btn btn-cancel">Cancel</button>
      <button type="submit" class="btn btn-primary">Create Task</button>
    </div>
  </form>
</template>

<script>
export default {
  name: "TaskForm"
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

.btn-primary:hover {
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
