<template>
  <div class="project-card">
    <!-- Project Header -->
    <div class="project-header">
      <div class="project-status-indicator" :class="getStatusClass(project.proj_status)"></div>
      <h2 class="project-title">{{ project.proj_name }}</h2>
      <button class="edit-btn" @click="$emit('edit-project', project)">✏️</button>
    </div>

    <!-- Project Details -->
    <div class="project-details">
      <p class="project-description">{{ project.proj_desc }}</p>
      <div class="project-meta">
        <div class="meta-item">
          <span class="meta-label">Duration:</span>
          <span class="meta-value">{{ formatDateRange(project.start_date, project.end_date) }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">Status:</span>
          <span class="status-badge" :class="getStatusClass(project.proj_status)">
            {{ formatStatus(project.proj_status) }}
          </span>
        </div>
        <div class="meta-item collaborators-section">
          <span class="meta-label">Collaborators:</span>
          <div class="collaborators-avatars">
            <div v-for="collaborator in uniqueCollaborators" :key="collaborator.id" class="collaborator-avatar"
              :title="collaborator.name">
              {{ collaborator.initials }}
            </div>
            <div v-if="uniqueCollaborators.length > 4" class="collaborator-more">
              +{{ uniqueCollaborators.length - 4 }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tasks -->
    <div class="tasks-container">
      <TaskItem
        v-for="task in project.tasks"
        :key="task.task_ID"
        :task="task"
        :users="users"
        @view-task="$emit('view-task', $event)"
        @edit-task="openEdit(task)"
      />

      <button class="add-task-btn" @click="$emit('add-task', project)">
        + Add Task
      </button>
    </div>
    <EditTask
      v-if="selectedTask"
      :visible="showEdit"
      :task="selectedTask"
      @close="showEdit = false"
      @saved="onTaskSaved"
    />
  </div>
</template>

<script>
// ProjectCard hosts the EditTask modal to enable inline editing of a task
// without leaving the project context. It wires the `edit-task` event from
// TaskItem to local state and applies a minimal optimistic update upon save.
import TaskItem from './TaskCard.vue'
import EditTask from '../EditTask.vue'

export default {
  name: 'ProjectCard',
  components: {
    TaskItem,
    EditTask
  },
  props: {
    project: {
      type: Object,
      required: true
    },
    users: {
      type: Array,
      default: () => []
    }
  },
  emits: ['edit-project', 'view-task', 'add-task'],
  data() {
    return {
      showEdit: false,
      selectedTask: null
    }
  },
  computed: {
    uniqueCollaborators() {
      const collaboratorIds = new Set();

      // Add project collaborators
      if (this.project.collaborators && Array.isArray(this.project.collaborators)) {
        this.project.collaborators.forEach(id => {
          if (id) collaboratorIds.add(String(id)); // Convert to string
        });
      }

      // Add task assignees
      if (this.project.tasks && Array.isArray(this.project.tasks)) {
        this.project.tasks.forEach(task => {
          if (task.assigned_to && Array.isArray(task.assigned_to)) {
            task.assigned_to.forEach(id => {
              if (id) collaboratorIds.add(String(id)); // Convert to string
            });
          }
          // Also add task creator
          if (task.created_by) {
            collaboratorIds.add(String(task.created_by)); // Convert to string
          }
        });
      }

      // Convert IDs to user objects and limit to 4 for display
      return Array.from(collaboratorIds)
        .map(id => this.getUser(id))
        .filter(user => user)
        .slice(0, 4);
    }
  },
  methods: {
    openEdit(task) {
      this.selectedTask = task
      this.showEdit = true
    },
    onTaskSaved(updated) {
      this.showEdit = false
      // Update task in local project view (minimal local sync)
      const id = updated.task_ID || updated.id
      const idx = (this.project.tasks || []).findIndex(t => (t.task_ID || t.id) === id)
      if (idx !== -1) {
        this.$set(this.project.tasks, idx, { ...this.project.tasks[idx], ...updated })
      }
    },
    getStatusClass(status) {
      if (!status) return 'status-default';

      // Convert status to lowercase and handle various formats
      const normalizedStatus = status.toLowerCase().replace(/[\s_]/g, '-');

      const statusClasses = {
        'not-started': 'status-todo',
        'in-progress': 'status-progress',
        'on-hold': 'status-pending',
        'completed': 'status-completed',
        'cancelled': 'status-pending'
      };

      return statusClasses[normalizedStatus] || 'status-default';
    },
    formatStatus(status) {
      return status?.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'Unknown';
    },
    formatDateRange(startDate, endDate) {
      if (!startDate || !endDate) return 'No dates set';
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
    handleViewTask(task) {
      // Emit the task with the project context
      this.$emit('view-task', {
        ...task,
        parentProjectId: this.project.id
      });
    },

    getUser(userId) {
      let user = this.users.find(user => String(user.id) === String(userId));
      if (!user) {
        user = this.users.find(user => String(user.user_ID) === String(userId));
      }
      if (user) {
        return {
          ...user,
          id: user.id || user.user_ID, 
          initials: this.getInitials(user.name)
        };
      }
      
      return null;
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
  }
}
</script>

<style scoped>
.project-card {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.project-header {
  display: flex;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #f3f4f6;
  gap: 1rem;
}

.project-status-indicator {
  width: 4px;
  height: 40px;
  border-radius: 2px;
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

.project-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
  flex: 1;
}

.edit-btn {
  background: #111827;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 0.5rem;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s ease;
}

.edit-btn:hover {
  background: #374151;
}

.project-details {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #f3f4f6;
}

.project-description {
  color: #6b7280;
  margin: 0 0 1rem 0;
  line-height: 1.6;
}

.project-meta {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
  align-items: center;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.collaborators-section {
  flex: 1;
  justify-content: flex-end;
}

.collaborators-avatars {
  display: flex;
  gap: 0.25rem;
  align-items: center;
}

.collaborator-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #6b7280;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
  color: #ffffff;
  border: 2px solid #ffffff;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.2s ease;
  margin-left: -4px;
  position: relative;
}

.collaborator-avatar:first-child {
  margin-left: 0;
}

.collaborator-avatar:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
  z-index: 10;
}

.collaborator-avatar:nth-child(1) {
  background: #6366f1;
}

.collaborator-avatar:nth-child(2) {
  background: #8b5cf6;
}

.collaborator-avatar:nth-child(3) {
  background: #06b6d4;
}

.collaborator-avatar:nth-child(4) {
  background: #10b981;
}

.collaborator-avatar:nth-child(5) {
  background: #f59e0b;
}

.collaborator-avatar:nth-child(6) {
  background: #ef4444;
}

/* Tooltip styles */
.collaborator-avatar::after {
  content: attr(title);
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: #111827;
  color: #ffffff;
  padding: 0.375rem 0.75rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
  white-space: nowrap;
  opacity: 0;
  visibility: hidden;
  transition: all 0.2s ease;
  margin-bottom: 4px;
  pointer-events: none;
  z-index: 20;
}

.collaborator-avatar::before {
  content: '';
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 4px solid transparent;
  border-top-color: #111827;
  opacity: 0;
  visibility: hidden;
  transition: all 0.2s ease;
  pointer-events: none;
  z-index: 20;
}

.collaborator-avatar:hover::after,
.collaborator-avatar:hover::before {
  opacity: 1;
  visibility: visible;
}

.collaborator-more {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.625rem;
  font-weight: 600;
  color: #6b7280;
  border: 2px solid #ffffff;
  margin-left: -4px;
}

.meta-label {
  color: #6b7280;
  font-weight: 500;
}

.meta-value {
  color: #111827;
  font-weight: 500;
}

.status-badge {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-weight: 500;
}

.status-badge.status-progress {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.status-todo {
  background: #fecaca;
  color: #991b1b;
}

.status-badge.status-completed {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.status-pending {
  background: #fed7aa;
  color: #9a3412;
}

.tasks-container {
  padding: 1.5rem;
}

.add-task-btn {
  background: transparent;
  color: #111827;
  border: 1px dashed #111827;
  border-radius: 6px;
  padding: 0.75rem 1rem;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  width: 100%;
  transition: all 0.2s ease;
}

.add-task-btn:hover {
  background: #f9fafb;
  border-color: #374151;
  color: #374151;
}

@media (max-width: 768px) {
  .project-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }

  .project-title {
    font-size: 1.25rem;
  }

  .project-meta {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }

  .collaborators-section {
    justify-content: flex-start;
  }
}
</style>