<template>
  <div class="project-card">
    <!-- Project Header -->
    <div class="project-header">
      <h2 class="project-title">{{ project.proj_name }}</h2>
      <button class="view-btn" @click="viewProject">View Project</button>
    </div>

    <!-- Project Details -->
    <div class="project-details">
      <p class="project-description">{{ project.proj_desc }}</p>
      <div class="project-meta">
        <div class="meta-item">
          <span class="meta-label">Duration:</span>
          <span class="meta-value">{{ formatDateRange(project.start_date, project.end_date) }}</span>
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

    <!-- Tasks Container -->
    <div class="tasks-container">
      <!-- Tasks Header with Sort Controls and Status Filter -->
      <div v-if="project.tasks && project.tasks.length > 0" class="tasks-header">
        <div class="tasks-info">
          <h4 class="tasks-count">
            {{ filteredAndSortedTasks.length }} of {{ project.tasks.length }} Task{{ project.tasks.length !== 1 ? 's' :
            '' }}
            <span v-if="taskStatusFilter !== 'all'" class="filter-indicator"
              :class="`status-${taskStatusFilter.toLowerCase().replace(' ', '-')}`">
              ({{ taskStatusFilter }})
            </span>
          </h4>
        </div>

        <div class="tasks-controls">
          <!-- Status Filter -->
          <div class="status-filter">
            <label class="filter-label">Filter:</label>
            <select v-model="taskStatusFilter" class="status-filter-select" @change="onStatusFilterChange">
              <option value="all">All Status</option>
              <option value="Unassigned">Unassigned</option>
              <option value="Ongoing">Ongoing</option>
              <option value="Under Review">Under Review</option>
              <option value="Completed">Completed</option>
            </select>
          </div>

          <!-- Date Sort Controls -->
          <div class="tasks-sort-controls">
            <span class="sort-label">Sort:</span>
            <div class="sort-toggle-group">
              <button class="sort-toggle-btn" :class="{ 'active': taskSortOrder === 'asc' }"
                @click="setTaskSortOrder('asc')">
                <svg width="10" height="10" viewBox="0 0 12 12" fill="none">
                  <path d="M6 3L9 6H3L6 3Z" fill="currentColor" />
                </svg>
                Earliest
              </button>
              <button class="sort-toggle-btn" :class="{ 'active': taskSortOrder === 'desc' }"
                @click="setTaskSortOrder('desc')">
                <svg width="10" height="10" viewBox="0 0 12 12" fill="none">
                  <path d="M6 9L3 6H9L6 9Z" fill="currentColor" />
                </svg>
                Latest
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Tasks List (using filtered and sorted tasks) -->
      <div class="tasks-list">
        <TaskItem v-for="task in filteredAndSortedTasks" :key="task.task_ID" :task="task" :users="users"
          @view-task="$emit('view-task', $event)" @edit-task="openEdit(task)" />

        <!-- No tasks message when filtered -->
        <div v-if="filteredAndSortedTasks.length === 0 && project.tasks.length > 0" class="no-tasks-filtered">
          <p>No tasks found with status: <strong>{{ taskStatusFilter.replace('-', ' ') }}</strong></p>
          <button class="clear-filter-btn" @click="clearStatusFilter">Show All Tasks</button>
        </div>
      </div>

      <!-- Add Task Button -->
      <button class="add-task-btn" @click="$emit('add-task', project)">
        + Add Task
      </button>
    </div>

    <!-- Edit Task Modal -->
    <EditTask v-if="selectedTask" :visible="showEdit" :task="selectedTask" @close="showEdit = false"
      @saved="onTaskSaved" />
  </div>
</template>

<script>
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
  mounted() {
    // Debug: Check what data the component receives when mounted
    console.log('=== ProjectCard Debug ===');
    console.log('Project name:', this.project.proj_name);
    console.log('Project ID:', this.project.id);
    console.log('All project fields:', Object.keys(this.project));
    console.log('Full project object:', this.project);

    if (!this.project.id) {
      console.error('⚠️ PROJECT ID IS MISSING!');
      console.error('This will cause navigation to fail');
    }
  },
  data() {
    return {
      showEdit: false,
      selectedTask: null,
      taskSortOrder: 'asc',
      taskStatusFilter: 'all'
    }
  },
  computed: {
    filteredAndSortedTasks() {
      if (!this.project.tasks || this.project.tasks.length === 0) {
        return [];
      }

      let filtered = [...this.project.tasks];

      if (this.taskStatusFilter !== 'all') {
        filtered = filtered.filter(task => {
          const taskStatus = task.task_status || task.status || 'Unassigned';
          return taskStatus === this.taskStatusFilter;
        });
      }

      const sorted = filtered.sort((a, b) => {
        if (!a.end_date && !b.end_date) return 0;
        if (!a.end_date) return 1;
        if (!b.end_date) return -1;

        const dateA = new Date(a.end_date);
        const dateB = new Date(b.end_date);

        if (isNaN(dateA.getTime()) && isNaN(dateB.getTime())) return 0;
        if (isNaN(dateA.getTime())) return 1;
        if (isNaN(dateB.getTime())) return -1;

        if (this.taskSortOrder === 'asc') {
          return dateA - dateB;
        } else {
          return dateB - dateA;
        }
      });

      return sorted;
    },

    statusCounts() {
      if (!this.project.tasks || this.project.tasks.length === 0) {
        return {};
      }

      const counts = {
        'Unassigned': 0,
        'Ongoing': 0,
        'Under Review': 0,
        'Completed': 0
      };

      this.project.tasks.forEach(task => {
        const status = task.task_status || task.status || 'Unassigned';
        if (status in counts) {
          counts[status]++;
        }
      });

      return counts;
    },

    uniqueCollaborators() {
      const collaboratorIds = new Set();

      if (this.project.collaborators && Array.isArray(this.project.collaborators)) {
        this.project.collaborators.forEach(id => {
          if (id) {
            collaboratorIds.add(String(id));
          }
        });
      }

      const collaborators = Array.from(collaboratorIds)
        .map(id => this.getUser(id))
        .filter(user => user);

      return collaborators;
    }
  },
  methods: {
    setTaskSortOrder(order) {
      this.taskSortOrder = order;
    },

    onStatusFilterChange() {
      console.log(`Filtering tasks by status: ${this.taskStatusFilter}`);
    },

    clearStatusFilter() {
      this.taskStatusFilter = 'all';
    },

    getStatusCount(status) {
      return this.statusCounts[status] || 0;
    },

    openEdit(task) {
      this.selectedTask = task
      this.showEdit = true
    },

    onTaskSaved(updated) {
      this.showEdit = false
      const id = updated.task_ID || updated.id
      const idx = (this.project.tasks || []).findIndex(t => (t.task_ID || t.id) === id)
      if (idx !== -1) {
        this.$set(this.project.tasks, idx, { ...this.project.tasks[idx], ...updated })
      }
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

      if (!user) {
        user = this.users.find(user => user.name === userId);
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

    viewProject() {
      console.log('=== viewProject called ===');
      console.log('this.project:', this.project);
      console.log('this.project.id:', this.project.id);
      console.log('Type of id:', typeof this.project.id);

      const projectId = this.project.id;

      if (!projectId || projectId === 'undefined' || projectId === undefined) {
        console.error('❌ Project ID is invalid!');
        console.error('Project object:', JSON.stringify(this.project, null, 2));
        alert('Unable to view project: Project ID is missing or invalid');
        return;
      }

      console.log('✅ Navigating to project ID:', projectId);
      this.$router.push(`/projects/${projectId}`);
    }
  }
}
</script>

<style scoped>
.view-btn {
  background: #111827;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  align-self: start;
  transition: all 0.2s ease;
}

.view-btn:hover {
  background: #374151;
}

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

.tasks-container {
  margin-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
  padding-top: 1.5rem;
}

.tasks-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.tasks-info {
  flex: 1;
}

.tasks-count {
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
  margin: 0;
}

.filter-indicator {
  font-size: 0.875rem;
  font-weight: 500;
  color: #3b82f6;
  background: #dbeafe;
  padding: 0.125rem 0.5rem;
  border-radius: 12px;
  margin-left: 0.5rem;
}

.tasks-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.status-filter {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-label {
  font-size: 0.75rem;
  color: #6b7280;
  font-weight: 500;
}

.status-filter-select {
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: #ffffff;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 120px;
}

.status-filter-select:hover {
  border-color: #9ca3af;
}

.status-filter-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.tasks-sort-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tasks-sort-controls .sort-label {
  font-size: 0.75rem;
  color: #6b7280;
  font-weight: 500;
}

.sort-toggle-group {
  display: flex;
  background: #f9fafb;
  border-radius: 6px;
  padding: 1px;
  border: 1px solid #e5e7eb;
}

.sort-toggle-btn {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.375rem 0.625rem;
  font-size: 0.75rem;
  font-weight: 500;
  border: none;
  background: transparent;
  color: #6b7280;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.sort-toggle-btn:hover {
  color: #374151;
  background: rgba(255, 255, 255, 0.8);
}

.sort-toggle-btn.active {
  background: #ffffff;
  color: #111827;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  font-weight: 600;
}

.sort-toggle-btn svg {
  width: 10px;
  height: 10px;
  transition: all 0.2s ease;
}

.sort-toggle-btn.active svg {
  color: #3b82f6;
}

.no-tasks-filtered {
  text-align: center;
  padding: 2rem 1rem;
  color: #6b7280;
  border: 2px dashed #e5e7eb;
  border-radius: 8px;
  background: #f9fafb;
}

.no-tasks-filtered p {
  margin: 0 0 1rem 0;
  font-size: 0.875rem;
}

.clear-filter-btn {
  padding: 0.5rem 1rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.clear-filter-btn:hover {
  background: #2563eb;
}

@media (max-width: 768px) {
  .tasks-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .tasks-controls {
    width: 100%;
    justify-content: space-between;
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }

  .status-filter,
  .tasks-sort-controls {
    justify-content: space-between;
    width: 100%;
  }

  .status-filter-select {
    flex: 1;
    max-width: none;
  }
}

.filter-indicator.status-unassigned {
  background: #f3f4f6;
  color: #6b7280;
}

.filter-indicator.status-ongoing {
  background: #dbeafe;
  color: #3b82f6;
}

.filter-indicator.status-under-review {
  background: #fef3c7;
  color: #d97706;
}

.filter-indicator.status-completed {
  background: #d1fae5;
  color: #065f46;
}
</style>