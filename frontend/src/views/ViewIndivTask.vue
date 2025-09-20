<template>
  <div class="view-task-page">
    <!-- Header -->
    <header class="page-header">
      <div class="header-container">
        <div class="breadcrumb">
          <button class="breadcrumb-link" @click="goBack">
            ← Back to Projects
          </button>
          <span class="breadcrumb-separator">/</span>
          <span class="breadcrumb-current">{{ parentProject?.projectName }}</span>
          <span class="breadcrumb-separator">/</span>
          <span class="breadcrumb-current">{{ task?.taskName }}</span>
        </div>
        
        <!-- <div class="header-actions">
          <button class="btn btn-secondary" @click="editTask">
            Edit Task
          </button>
          <button class="btn btn-danger" @click="deleteTask">
            Delete Task
          </button>
        </div> -->
      </div>
    </header>

    <!-- Main Content -->
    <main class="page-content" v-if="task && parentProject">
      <div class="content-container">
        
        <!-- Parent Project Context -->
        <div class="parent-project-banner">
          <div class="project-status-indicator" :class="getParentStatusClass(parentProject.status)"></div>
          <div class="banner-content">
            <h1 class="parent-project-title">{{ parentProject.projectName }}</h1>
            <p class="parent-project-description">{{ parentProject.instruction }}</p>
            <div class="parent-project-meta">
              <span class="meta-item">
                <strong>Status:</strong> {{ formatStatus(parentProject.status) }}
              </span>
              <span class="meta-item">
                <strong>Due:</strong> {{ formatDate(parentProject.dueDate) }}
              </span>
            </div>
          </div>
        </div>

        <!-- Task Details Card -->
        <div class="task-details-card">
          <div class="card-header">
            <h2 class="task-title">{{ task.taskName }}</h2>
            <div class="status-badge-large" :class="getTaskStatusClass(task.currentStatus?.statusName)">
              {{ task.currentStatus?.statusName || 'Not Started' }}
            </div>
          </div>

          <!-- Key Information Grid -->
          <div class="info-grid">
            <div class="info-card">
              <div class="info-icon">📅</div>
              <div class="info-content">
                <h3 class="info-title">Due Date</h3>
                <p class="info-value">{{ formatDate(task.dueDate) }}</p>
                <p class="info-meta" :class="getDueDateClass(task.dueDate)">
                  {{ getDueDateStatus(task.dueDate) }}
                </p>
              </div>
            </div>

            <div class="info-card">
              <div class="info-icon">👤</div>
              <div class="info-content">
                <h3 class="info-title">Assignee</h3>
                <div v-if="task.assignee" class="user-info">
                  <div class="user-avatar" :class="'assignee'">
                    {{ getInitials(task.assignee.name) }}
                  </div>
                  <div class="user-details">
                    <p class="user-name">{{ task.assignee.name }}</p>
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
                <div v-if="task.approver" class="user-info">
                  <div class="user-avatar approver">
                    {{ getInitials(task.approver.name) }}
                  </div>
                  <div class="user-details">
                    <p class="user-name">{{ task.approver.name }}</p>
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
                <div v-if="task.assignees && task.assignees.length > 0" class="collaborators-list">
                  <div v-for="assignee in task.assignees" :key="assignee.id" class="user-info">
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
              {{ task.instruction || 'No description provided for this task.' }}
            </p>
          </div>

          <!-- Status History -->
          <div class="status-history-section">
            <h3 class="section-title">Status History</h3>
            <div class="status-timeline">
              <div class="timeline-item">
                <div class="timeline-dot" :class="getTaskStatusClass(task.currentStatus?.statusName)"></div>
                <div class="timeline-content">
                  <h4 class="timeline-status">{{ task.currentStatus?.statusName || 'Not Started' }}</h4>
                  <p class="timeline-date">{{ formatDateTime(task.currentStatus?.statusTimestamp) }}</p>
                  <p class="timeline-user">Updated by Staff: {{ task.currentStatus?.staffId }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Task Metadata -->
          <div class="metadata-section">
            <h3 class="section-title">Task Information</h3>
            <div class="metadata-grid">
              <div class="metadata-item">
                <span class="metadata-label">Project ID</span>
                <span class="metadata-value">{{ task.projectId }}</span>
              </div>
              <div class="metadata-item">
                <span class="metadata-label">Task ID</span>
                <span class="metadata-value">{{ task.taskId }}</span>
              </div>
              <div class="metadata-item">
                <span class="metadata-label">Assigner</span>
                <span class="metadata-value">{{ getAssignerName(task.assigner) }}</span>
              </div>
              <div class="metadata-item">
                <span class="metadata-label">Created</span>
                <span class="metadata-value">{{ formatDateTime(task.currentStatus?.statusTimestamp) }}</span>
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
          <p>Loading task details...</p>
        </div>
      </div>
    </main>

    <!-- Edit Task Modal -->
    <!-- 
    <div v-if="showEditModal" class="modal-overlay" @click="closeEditModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">Edit Task</h3>
          <button class="modal-close" @click="closeEditModal">&times;</button>
        </div>
        <TaskForm 
          :is-edit-mode="true"
          :initial-data="taskFormData"
          @success="handleEditSuccess"
          @cancel="closeEditModal"
        />
      </div>
    </div>
    -->
  </div>
</template>

<script>
// import TaskForm from '../components/TaskForm.vue' // Component doesn't exist yet
import { mockProjects, mockUsers } from '../dummyData/projectData.js'

export default {
  name: 'ViewIndivTask',
  // components: {
  //   TaskForm  // Component doesn't exist yet
  // },
  data() {
    return {
      projects: mockProjects,
      users: mockUsers,
      task: null,
      parentProject: null,
      showEditModal: false
    }
  },
  computed: {
    taskFormData() {
      if (!this.task) return {};
      
      return {
        name: this.task.taskName,
        deadline: this.task.dueDate ? new Date(this.task.dueDate).toISOString().split('T')[0] : '',
        status: this.task.currentStatus?.statusName || '',
        assigneeId: this.task.assignee?.id || '',
        approverId: this.task.approver?.id || '',
        instruction: this.task.instruction || ''
      };
    }
  },
  created() {
    this.loadTaskData()
  },
  watch: {
    '$route'() {
      this.loadTaskData()
    }
  },
  methods: {
    loadTaskData() {
      const projectId = this.$route.params.projectId
      const taskId = this.$route.params.taskId
      
      // Find the parent project
      this.parentProject = this.projects.find(project => project.projectId === projectId)
      
      // Find the specific task
      if (this.parentProject) {
        this.task = this.parentProject.tasks.find(task => task.taskId === taskId)
      }
      
      // If no task found, redirect back
      if (!this.task) {
        this.$router.push('/projects')
      }
    },

    goBack() {
      this.$router.push('/projects')
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

    getTaskStatusClass(status) {
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

    editTask() {
      this.showEditModal = true;
    },

    closeEditModal() {
      this.showEditModal = false;
    },

    handleEditSuccess() {
      this.showEditModal = false;
      this.loadTaskData();
    },

    deleteTask() {
      if (confirm('Are you sure you want to delete this task?')) {
        console.log('Delete task:', this.task);
        // Handle deletion logic here
        this.$router.push('/projects');
      }
    }
  }
}
</script>

<style scoped>
.view-task-page {
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

/* Parent Project Banner */
.parent-project-banner {
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  padding: 24px;
  display: flex;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.project-status-indicator {
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

.parent-project-title {
  font-size: 24px;
  font-weight: 700;
  color: #111827;
  margin: 0 0 8px 0;
}

.parent-project-description {
  color: #6b7280;
  margin: 0 0 16px 0;
  line-height: 1.6;
}

.parent-project-meta {
  display: flex;
  gap: 24px;
  font-size: 14px;
}

.meta-item {
  color: #374151;
}

/* Task Details Card */
.task-details-card {
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

.task-title {
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
  
  .parent-project-banner,
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