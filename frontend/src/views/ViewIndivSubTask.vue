<template>
  <div class="view-subtask-page">
    <!-- Header -->
    <header class="page-header">
      <div class="header-container">
        <div class="breadcrumb">
          <button class="breadcrumb-link" @click="goBack">
            ← Back to Projects
          </button>
          <span class="breadcrumb-separator">/</span>
          <span class="breadcrumb-current">{{ parentTask?.taskName }}</span>
          <span class="breadcrumb-separator">/</span>
          <span class="breadcrumb-current">{{ subtask?.subTaskName }}</span>
        </div>
        
        <!-- <div class="header-actions">
          <button class="btn btn-secondary" @click="editSubtask">
            Edit Subtask
          </button>
          <button class="btn btn-danger" @click="deleteSubtask">
            Delete Subtask
          </button>
        </div> -->
      </div>
    </header>

    <!-- Main Content -->
    <main class="page-content" v-if="subtask && parentTask">
      <div class="content-container">
        
        <!-- Parent Task Context -->
        <div class="parent-task-banner">
          <div class="task-status-indicator" :class="getParentStatusClass(parentTask.status)"></div>
          <div class="banner-content">
            <h1 class="parent-task-title">{{ parentTask.taskName }}</h1>
            <p class="parent-task-description">{{ parentTask.instruction }}</p>
            <div class="parent-task-meta">
              <span class="meta-item">
                <strong>Status:</strong> {{ formatStatus(parentTask.status) }}
              </span>
              <span class="meta-item">
                <strong>Due:</strong> {{ formatDate(parentTask.dueDate) }}
              </span>
            </div>
          </div>
        </div>

        <!-- Subtask Details Card -->
        <div class="subtask-details-card">
          <div class="card-header">
            <h2 class="subtask-title">{{ subtask.subTaskName }}</h2>
            <div class="status-badge-large" :class="getSubtaskStatusClass(subtask.currentStatus?.statusName)">
              {{ subtask.currentStatus?.statusName || 'Not Started' }}
            </div>
          </div>

          <!-- Key Information Grid -->
          <div class="info-grid">
            <div class="info-card">
              <div class="info-icon">📅</div>
              <div class="info-content">
                <h3 class="info-title">Due Date</h3>
                <p class="info-value">{{ formatDate(subtask.dueDate) }}</p>
                <p class="info-meta" :class="getDueDateClass(subtask.dueDate)">
                  {{ getDueDateStatus(subtask.dueDate) }}
                </p>
              </div>
            </div>

            <div class="info-card">
              <div class="info-icon">👤</div>
              <div class="info-content">
                <h3 class="info-title">Assignee</h3>
                <div v-if="subtask.assignee" class="user-info">
                  <div class="user-avatar" :class="'assignee'">
                    {{ getInitials(subtask.assignee.name) }}
                  </div>
                  <div class="user-details">
                    <p class="user-name">{{ subtask.assignee.name }}</p>
                    <p class="user-role">Assignee</p>
                  </div>
                </div>
                <p v-else class="info-value empty">Not assigned</p>
              </div>
            </div>

            <div class="info-card">
              <div class="info-icon">✅</div>
              <div class="info-content">
                <h3 class="info-title">Approver</h3>
                <div v-if="subtask.approver" class="user-info">
                  <div class="user-avatar approver">
                    {{ getInitials(subtask.approver.name) }}
                  </div>
                  <div class="user-details">
                    <p class="user-name">{{ subtask.approver.name }}</p>
                    <p class="user-role">Approver</p>
                  </div>
                </div>
                <p v-else class="info-value empty">Not assigned</p>
              </div>
            </div>

            <div class="info-card">
              <div class="info-icon">👥</div>
              <div class="info-content">
                <h3 class="info-title">Collaborators</h3>
                <div v-if="subtask.assignees && subtask.assignees.length > 0" class="collaborators-list">
                  <div v-for="assignee in subtask.assignees" :key="assignee.id" class="user-info">
                    <div class="user-avatar">
                      {{ getInitials(assignee.name) }}
                    </div>
                    <div class="user-details">
                      <p class="user-name">{{ assignee.name }}</p>
                      <p class="user-role">Collaborator</p>
                    </div>
                  </div>
                </div>
                <p v-else class="info-value empty">No collaborators</p>
              </div>
            </div>
          </div>

          <!-- Description Section -->
          <div class="description-section">
            <h3 class="section-title">Description</h3>
            <p class="description-text">
              {{ subtask.instruction || 'No description provided for this subtask.' }}
            </p>
          </div>

          <!-- Status History -->
          <div class="status-history-section">
            <h3 class="section-title">Status History</h3>
            <div class="status-timeline">
              <div class="timeline-item">
                <div class="timeline-dot" :class="getSubtaskStatusClass(subtask.currentStatus?.statusName)"></div>
                <div class="timeline-content">
                  <h4 class="timeline-status">{{ subtask.currentStatus?.statusName || 'Not Started' }}</h4>
                  <p class="timeline-date">{{ formatDateTime(subtask.currentStatus?.statusTimestamp) }}</p>
                  <p class="timeline-user">Updated by Staff: {{ subtask.currentStatus?.staffId }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Task Metadata -->
          <div class="metadata-section">
            <h3 class="section-title">Task Information</h3>
            <div class="metadata-grid">
              <div class="metadata-item">
                <span class="metadata-label">Task ID</span>
                <span class="metadata-value">{{ subtask.taskId }}</span>
              </div>
              <div class="metadata-item">
                <span class="metadata-label">Subtask ID</span>
                <span class="metadata-value">{{ subtask.subTaskId }}</span>
              </div>
              <div class="metadata-item">
                <span class="metadata-label">Assigner</span>
                <span class="metadata-value">{{ getAssignerName(subtask.assigner) }}</span>
              </div>
              <div class="metadata-item">
                <span class="metadata-label">Created</span>
                <span class="metadata-value">{{ formatDateTime(subtask.currentStatus?.statusTimestamp) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Loading State -->
    <main v-else class="page-content">
      <div class="content-container">
        <div class="loading-state">
          <p>Loading subtask details...</p>
        </div>
      </div>
    </main>

    <!-- Edit Subtask Modal -->
    <div v-if="showEditModal" class="modal-overlay" @click="closeEditModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">Edit Subtask</h3>
          <button class="modal-close" @click="closeEditModal">&times;</button>
        </div>
        <SubTaskForm 
          :is-edit-mode="true"
          :initial-data="subtaskFormData"
          @success="handleEditSuccess"
          @cancel="closeEditModal"
        />
      </div>
    </div>
  </div>
</template>

<script>
import SubTaskForm from '../components/SubTaskForm.vue'
import { mockTasks, mockUsers } from '../dummyData/taskData.js'

export default {
  name: 'ViewIndivSubTask',
  components: {
    SubTaskForm
  },
  data() {
    return {
      tasks: mockTasks,
      users: mockUsers,
      subtask: null,
      parentTask: null,
      showEditModal: false
    }
  },
  computed: {
    subtaskFormData() {
      if (!this.subtask) return {};
      
      return {
        name: this.subtask.subTaskName,
        deadline: this.subtask.dueDate ? new Date(this.subtask.dueDate).toISOString().split('T')[0] : '',
        status: this.subtask.currentStatus?.statusName || '',
        assigneeId: this.subtask.assignee?.id || '',
        approverId: this.subtask.approver?.id || '',
        instruction: this.subtask.instruction || ''
      };
    }
  },
  created() {
    this.loadSubtaskData()
  },
  watch: {
    '$route'() {
      this.loadSubtaskData()
    }
  },
  methods: {
    loadSubtaskData() {
      const taskId = this.$route.params.taskId
      const subtaskId = this.$route.params.subtaskId
      
      // Find the parent task
      this.parentTask = this.tasks.find(task => task.taskId === taskId)
      
      // Find the specific subtask
      if (this.parentTask) {
        this.subtask = this.parentTask.subtasks.find(subtask => subtask.subTaskId === subtaskId)
      }
      
      // If no subtask found, redirect back
      if (!this.subtask) {
        this.$router.push('/tasks')
      }
    },

    goBack() {
      this.$router.push('/tasks')
    },

    getParentStatusClass(status) {
      const statusClasses = {
        'in-progress': 'status-progress',
        'to-do': 'status-todo',
        'completed': 'status-completed',
        'pending': 'status-pending'
      };
      return statusClasses[status] || 'status-default';
    },

    getSubtaskStatusClass(status) {
      if (!status) return 'status-not-started';
      const statusClasses = {
        'In progress': 'status-progress',
        'To Do': 'status-todo',
        'Completed': 'status-completed',
        'Pending': 'status-pending'
      };
      return statusClasses[status] || 'status-default';
    },

    formatDate(date) {
      if (!date) return 'No due date';
      return new Date(date).toLocaleDateString('en-US', { 
        weekday: 'long',
        day: '2-digit', 
        month: 'long', 
        year: 'numeric' 
      });
    },

    formatDateTime(date) {
      if (!date) return 'Unknown';
      return new Date(date).toLocaleDateString('en-US', { 
        day: '2-digit', 
        month: 'short', 
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },

    formatStatus(status) {
      return status?.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'Unknown';
    },

    getDueDateStatus(dueDate) {
      if (!dueDate) return 'No deadline';
      
      const now = new Date();
      const due = new Date(dueDate);
      const diffTime = due - now;
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      
      if (diffDays < 0) return `Overdue by ${Math.abs(diffDays)} days`;
      if (diffDays === 0) return 'Due today';
      if (diffDays === 1) return 'Due tomorrow';
      if (diffDays <= 7) return `Due in ${diffDays} days`;
      return `${diffDays} days remaining`;
    },

    getDueDateClass(dueDate) {
      if (!dueDate) return '';
      
      const now = new Date();
      const due = new Date(dueDate);
      const diffTime = due - now;
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      
      if (diffDays < 0) return 'overdue';
      if (diffDays <= 1) return 'urgent';
      if (diffDays <= 7) return 'warning';
      return 'normal';
    },

    getInitials(name) {
      if (!name) return 'U';
      return name
        .split(' ')
        .map(word => word.charAt(0))
        .join('')
        .substring(0, 2)
        .toUpperCase();
    },

    getAssignerName(assignerId) {
      const user = this.users.find(u => u.id === assignerId);
      return user ? user.name : 'Unknown User';
    },

    editSubtask() {
      this.showEditModal = true;
    },

    closeEditModal() {
      this.showEditModal = false;
    },

    handleEditSuccess() {
      this.showEditModal = false;
      this.loadSubtaskData();
    },

    deleteSubtask() {
      if (confirm('Are you sure you want to delete this subtask?')) {
        console.log('Delete subtask:', this.subtask);
        // Handle deletion logic here
        this.$router.push('/tasks');
      }
    }
  }
}
</script>

<style scoped>
.view-subtask-page {
  min-height: 100vh;
  background-color: #f8fafc;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
}

/* Header Styles */
.page-header {
  background-color: #ffffff;
  border-bottom: 1px solid #e5e7eb;
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.breadcrumb-link {
  color: #6b7280;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  font-size: 14px;
  text-decoration: none;
}

.breadcrumb-link:hover {
  color: #111827;
}

.breadcrumb-separator {
  color: #9ca3af;
}

.breadcrumb-current {
  color: #111827;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Content Styles */
.page-content {
  padding: 32px;
}

.content-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Parent Task Banner */
.parent-task-banner {
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  padding: 24px;
  display: flex;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.task-status-indicator {
  width: 4px;
  height: 60px;
  border-radius: 2px;
  flex-shrink: 0;
}

.status-progress { background: #fbbf24; }
.status-todo { background: #ef4444; }
.status-completed { background: #10b981; }
.status-pending { background: #f59e0b; }

.banner-content {
  flex: 1;
}

.parent-task-title {
  font-size: 24px;
  font-weight: 700;
  color: #111827;
  margin: 0 0 8px 0;
}

.parent-task-description {
  color: #6b7280;
  margin: 0 0 16px 0;
  line-height: 1.6;
}

.parent-task-meta {
  display: flex;
  gap: 24px;
  font-size: 14px;
}

.meta-item {
  color: #374151;
}

/* Subtask Details Card */
.subtask-details-card {
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 32px 32px 24px;
  border-bottom: 1px solid #f3f4f6;
}

.subtask-title {
  font-size: 28px;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.status-badge-large {
  font-size: 14px;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 600;
}

/* Info Grid */
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  padding: 32px;
  border-bottom: 1px solid #f3f4f6;
}

.info-card {
  display: flex;
  gap: 16px;
  padding: 20px;
  background: #f9fafb;
  border-radius: 12px;
  border: 1px solid #f3f4f6;
}

.info-icon {
  font-size: 24px;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e5e7eb;
  border-radius: 50%;
  flex-shrink: 0;
}

.info-content {
  flex: 1;
}

.info-title {
  font-size: 14px;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 8px 0;
}

.info-value {
  font-size: 16px;
  color: #111827;
  font-weight: 500;
  margin: 0 0 4px 0;
}

.info-value.empty {
  color: #9ca3af;
  font-style: italic;
}

.info-meta {
  font-size: 12px;
  font-weight: 500;
  margin: 0;
}

.info-meta.overdue { color: #dc2626; }
.info-meta.urgent { color: #ea580c; }
.info-meta.warning { color: #ca8a04; }
.info-meta.normal { color: #059669; }

/* User Info */
.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: #374151;
}

.user-avatar.approver {
  background: #ddd6fe;
  color: #5b21b6;
}

.user-avatar.assignee {
  background: #fef3c7;
  color: #92400e;
}

.user-details {
  flex: 1;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: #111827;
  margin: 0 0 2px 0;
}

.user-role {
  font-size: 12px;
  color: #6b7280;
  margin: 0;
}

.collaborators-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* Sections */
.description-section,
.status-history-section,
.metadata-section {
  padding: 32px;
  border-bottom: 1px solid #f3f4f6;
}

.metadata-section {
  border-bottom: none;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 16px 0;
}

.description-text {
  color: #6b7280;
  line-height: 1.6;
  margin: 0;
}

/* Timeline */
.status-timeline {
  position: relative;
}

.timeline-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.timeline-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 4px;
}

.timeline-content {
  flex: 1;
}

.timeline-status {
  font-weight: 600;
  color: #111827;
  margin: 0 0 4px 0;
  font-size: 16px;
}

.timeline-date {
  font-size: 14px;
  color: #6b7280;
  margin: 0 0 4px 0;
}

.timeline-user {
  font-size: 12px;
  color: #9ca3af;
  margin: 0;
}

/* Metadata Grid */
.metadata-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.metadata-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.metadata-label {
  font-size: 12px;
  font-weight: 500;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.metadata-value {
  font-size: 14px;
  color: #111827;
  font-weight: 500;
}

/* Buttons */
.btn {
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
  font-size: 14px;
}

.btn-secondary {
  background-color: #f3f4f6;
  color: #374151;
  border-color: #d1d5db;
}

.btn-secondary:hover {
  background-color: #e5e7eb;
}

.btn-danger {
  background-color: #dc2626;
  color: #ffffff;
}

.btn-danger:hover {
  background-color: #b91c1c;
}

/* Status Badge Colors */
.status-badge-large.status-progress {
  background: #fef3c7;
  color: #92400e;
}

.status-badge-large.status-todo {
  background: #fecaca;
  color: #991b1b;
}

.status-badge-large.status-completed {
  background: #d1fae5;
  color: #065f46;
}

.status-badge-large.status-pending {
  background: #fed7aa;
  color: #9a3412;
}

.status-badge-large.status-not-started {
  background: #f3f4f6;
  color: #6b7280;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #fff;
  border-radius: 12px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 0;
  margin-bottom: 16px;
}

.modal-title {
  font-size: 20px;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  color: #6b7280;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.modal-close:hover {
  background: #f3f4f6;
  color: #111827;
}

/* Loading State */
.loading-state {
  text-align: center;
  padding: 48px;
  color: #6b7280;
}

/* Responsive Design */
@media (max-width: 768px) {
  .header-container {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }
  
  .page-content {
    padding: 16px;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
    padding: 16px;
  }
  
  .parent-task-banner,
  .description-section,
  .status-history-section,
  .metadata-section {
    padding: 16px;
  }
  
  .card-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
    padding: 16px;
  }
  
  .metadata-grid {
    grid-template-columns: 1fr;
  }
}
</style>