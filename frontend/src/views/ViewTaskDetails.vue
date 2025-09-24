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
          <span class="breadcrumb-current">{{ parentProject?.proj_name }}</span>
          <span class="breadcrumb-separator">/</span>
          <span class="breadcrumb-current">{{ task?.task_name }}</span>
        </div>
      </div>
    </header>

    <!-- Loading State -->
    <main v-if="loading" class="page-content">
      <div class="content-container">
        <div class="loading-state">
          <p>Loading task details...</p>
        </div>
      </div>
    </main>

    <!-- Error State -->
    <main v-else-if="error" class="page-content">
      <div class="content-container">
        <div class="error-state">
          <p class="error-message">{{ error }}</p>
          <button class="retry-btn" @click="loadTaskData">Retry</button>
        </div>
      </div>
    </main>

    <!-- Main Content -->
    <main v-else-if="task && parentProject" class="page-content">
      <div class="content-container">

        <!-- Parent Project Context -->
        <div class="parent-project-banner">
          <div class="project-status-indicator" :class="getParentStatusClass(parentProject.proj_status)"></div>
          <div class="banner-content">
            <h1 class="parent-project-title">{{ parentProject.proj_name }}</h1>
            <p class="parent-project-description">{{ parentProject.proj_desc }}</p>
            <div class="parent-project-meta">
              <span class="meta-item">
                <strong>Status:</strong> {{ formatStatus(parentProject.proj_status) }}
              </span>
              <span class="meta-item">
                <strong>Duration:</strong> {{ formatDateRange(parentProject.start_date, parentProject.end_date) }}
              </span>
            </div>
          </div>
        </div>

        <!-- Task Details Card -->
        <div class="task-details-card">
          <div class="card-header">
            <h2 class="task-title">{{ task.task_name }}</h2>
            <div class="header-actions"></div>
              <div class="status-badge-large" :class="getTaskStatusClass(task.task_status)">
                {{ formatStatus(task.task_status) || 'Not Started' }}
            </div>
            <button @click="openSubtaskModal" class="add-subtask-btn">
              + Add Subtask
            </button>
          </div>

          <!-- Key Information Grid -->
          <div class="info-grid">
            <div class="info-card">
              <div class="info-icon">📅</div>
              <div class="info-content">
                <h3 class="info-title">Start Date</h3>
                <p class="info-value">{{ formatDate(task.start_date) }}</p>
              </div>
            </div>

            <div class="info-card">
              <div class="info-icon">⏰</div>
              <div class="info-content">
                <h3 class="info-title">Due Date</h3>
                <p class="info-value">{{ formatDate(task.end_date) }}</p>
                <p class="info-meta" :class="getDueDateClass(task.end_date)">
                  {{ getDueDateStatus(task.end_date) }}
                </p>
              </div>
            </div>

            <div class="info-card">
              <div class="info-icon">👤</div>
              <div class="info-content">
                <h3 class="info-title">Created By</h3>
                <div v-if="task.created_by" class="user-info">
                  <div class="user-avatar creator">
                    {{ getInitials(getCreatorName(task.created_by)) }}
                  </div>
                  <div class="user-details">
                    <p class="user-name">{{ getCreatorName(task.created_by) }}</p>
                    <p class="user-role">Creator</p>
                  </div>
                </div>
                <p v-else class="info-value empty">Not assigned</p>
              </div>
            </div>

            <div class="info-card">
              <div class="info-icon">👥</div>
              <div class="info-content">
                <h3 class="info-title">Assigned To</h3>
                <div v-if="task.assigned_to && task.assigned_to.length > 0" class="assignees-list">
                  <div v-for="userId in task.assigned_to" :key="userId" class="user-info">
                    <div class="user-avatar assignee">
                      {{ getInitials(getUserName(userId)) }}
                    </div>
                    <div class="user-details">
                      <p class="user-name">{{ getUserName(userId) }}</p>
                      <p class="user-role">Assignee</p>
                    </div>
                  </div>
                </div>
                <p v-else class="info-value empty">No assignees</p>
              </div>
            </div>
          </div>

          <!-- Description Section -->
          <div class="description-section">
            <h3 class="section-title">Description</h3>
            <p class="description-text">
              {{ task.task_desc || 'No description provided for this task.' }}
            </p>
          </div>

          <!-- Attachments Section -->
          <div class="attachments-section" v-if="task.attachments && task.attachments.length > 0">
            <h3 class="section-title">Attachments</h3>
            <div class="attachments-grid">
              <div v-for="attachment in task.attachments" :key="attachment" class="attachment-item">
                <div class="attachment-icon">📎</div>
                <div class="attachment-info">
                  <p class="attachment-name">{{ attachment }}</p>
                  <p class="attachment-size">Click to download</p>
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
                <span class="metadata-value">{{ task.proj_ID }}</span>
              </div>
              <div class="metadata-item">
                <span class="metadata-label">Task ID</span>
                <span class="metadata-value">{{ task.id }}</span>
              </div>
              <div class="metadata-item">
                <span class="metadata-label">Created By</span>
                <span class="metadata-value">{{ getCreatorName(task.created_by) }}</span>
              </div>
              <div class="metadata-item">
                <span class="metadata-label">Duration</span>
                <span class="metadata-value">{{ formatDateRange(task.start_date, task.end_date) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Subtask Modal -->
    <div v-if="showSubtaskModal" class="modal-overlay" @click="closeSubtaskModal">
      <div class="modal-content" @click.stop>
        <SubtaskForm 
          :parentTaskId="task.id"
          :parentProjectId="task.proj_ID"
          @subtask-created="handleSubtaskCreated"
          @cancel="closeSubtaskModal"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { projectService } from '../services/projectService.js'
// import { taskService } from '../services/taskService.js'
import SubtaskForm from '../components/SubTaskForm.vue'

export default {
  name: 'ViewIndivTask',
  components: {
    SubtaskForm
  },
  data() {
    return {
      projects: [],
      tasks: [],
      users: [],
      task: null,
      parentProject: null,
      loading: true,
      error: null,
      showSubtaskModal: false
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
    async loadTaskData() {
      try {
        this.loading = true;
        this.error = null;

        const projectId = this.$route.params.projectId;
        const taskId = this.$route.params.taskId;

        console.log('Route params:', { projectId, taskId });

        // Load users first
        try {
          this.users = await projectService.getAllUsers();
        } catch (userError) {
          console.warn('Could not load users:', userError);
        }

        // Load all projects to diagnose the issue
        const allProjects = await projectService.getAllProjects();

        // Find which project actually contains the task we're looking for
        let actualParentProject = null;
        let foundTask = null;

        for (const project of allProjects) {
          if (project.tasks) {
            const taskInThisProject = project.tasks.find(task =>
              String(task.id) === String(taskId) || String(task.task_ID) === String(taskId)
            );

            if (taskInThisProject) {
              actualParentProject = project;
              foundTask = taskInThisProject;
              break;
            }
          }
        }
        // Check if there's a mismatch
        if (actualParentProject && String(actualParentProject.id) !== String(projectId)) {
          this.parentProject = actualParentProject;
          this.task = foundTask;
        } else if (actualParentProject && foundTask) {
          // Everything matches correctly
          this.parentProject = actualParentProject;
          this.task = foundTask;
        } else {
          // Task genuinely not found anywhere
          allProjects.forEach(proj => {
            if (proj.tasks && proj.tasks.length > 0) {
              console.log(`${proj.proj_name}:`, proj.tasks.map(t => `${t.id} (${t.task_name})`));
            }
          });
          return;
        }

        // Double-check our final result
        if (!this.task || !this.parentProject) {
          this.error = `Failed to load task data. Task: ${this.task ? 'Found' : 'Missing'}, Project: ${this.parentProject ? 'Found' : 'Missing'}`;
          return;
        }

      } catch (error) {
        console.error('Error loading task data:', error);
        this.error = error.message;
      } finally {
        this.loading = false;
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
        'in-progress': 'status-progress',
        'to-do': 'status-todo',
        'completed': 'status-completed',
        'pending': 'status-pending'
      };
      return statusClasses[status] || 'status-default';
    },

    formatDate(date) {
      if (!date) return 'No date set';
      return new Date(date).toLocaleDateString('en-US', {
        weekday: 'long',
        day: '2-digit',
        month: 'long',
        year: 'numeric'
      });
    },

    formatDateRange(startDate, endDate) {
      if (!startDate || !endDate) return 'No start or end date set';
      const start = new Date(startDate).toLocaleDateString('en-US', {
        day: '2-digit',
        month: 'short'
      });
      const end = new Date(endDate).toLocaleDateString('en-US', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
      });
      return `${start} - ${end}`;
    },

    formatStatus(status) {
      return status?.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'Not Started';
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


    getUserName(userId) {
      // First try to find by document ID (from backend API)
      let user = this.users.find(u => String(u.id) === String(userId));

      // Fallback to user_ID field if it exists
      if (!user) {
        user = this.users.find(u => String(u.user_ID) === String(userId));
      }

      return user ? user.name : 'Unknown User';
    },

    getCreatorName(userId) {
      // First try to find by document ID (from backend API)
      let user = this.users.find(u => String(u.id) === String(userId));

      // Fallback to user_ID field if it exists
      if (!user) {
        user = this.users.find(u => String(u.user_ID) === String(userId));
      }

      return user ? user.name : 'Unknown User';
    },

    openSubtaskModal() {
      this.showSubtaskModal = true;
    },

    closeSubtaskModal() {
      this.showSubtaskModal = false;
    },

    handleSubtaskCreated() {
      this.closeSubtaskModal();
      // Optionally refresh task data
      // this.loadTaskData();
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

.status-progress {
  background: #fbbf24;
}

.status-todo {
  background: #ef4444;
}

.status-completed {
  background: #10b981;
}

.status-pending {
  background: #f59e0b;
}

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

.info-meta.overdue {
  color: #dc2626;
}

.info-meta.urgent {
  color: #ea580c;
}

.info-meta.warning {
  color: #ca8a04;
}

.info-meta.normal {
  color: #059669;
}

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

.user-avatar.creator {
  background: #e0e7ff;
  color: #3730a3;
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

.assignees-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* Sections */
.description-section,
.attachments-section,
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

/* Attachments */
.attachments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #f9fafb;
  border: 1px solid #f3f4f6;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.attachment-item:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
}

.attachment-icon {
  font-size: 20px;
}

.attachment-info {
  flex: 1;
}

.attachment-name {
  font-size: 14px;
  font-weight: 500;
  color: #111827;
  margin: 0 0 4px 0;
}

.attachment-size {
  font-size: 12px;
  color: #6b7280;
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

  .page-content {
    padding: 16px;
  }

  .info-grid {
    grid-template-columns: 1fr;
    padding: 16px;
  }

  .parent-project-banner,
  .description-section,
  .attachments-section,
  .metadata-section {
    padding: 16px;
  }

  .card-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
    padding: 16px;
  }

  .metadata-grid,
  .attachments-grid {
    grid-template-columns: 1fr;
  }
}

/* Header Actions */
.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.add-subtask-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s;
}

.add-subtask-btn:hover {
  background: #2563eb;
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
  background: white;
  border-radius: 12px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px 0;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 0;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #111827;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6b7280;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #374151;
}


</style>