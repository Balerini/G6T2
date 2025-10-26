<template>
  <div class="project-card" :class="{ 'completed-project': isCompletedProject }">
    <!-- Debug info (remove in production) -->
    <div v-if="false" style="background: yellow; padding: 5px; font-size: 11px;">
      DEBUG: isCompleted={{ isCompletedProject }}, 
      showCompleted={{ showCompletedProjects }}, 
      filter={{ taskStatusFilter }},
      status={{ project.proj_status || project.status }}
    </div>
    
    <!-- Project Header -->
    <div class="project-header" data-testid='proj-list'>
      <h2 class="project-title">{{ project.proj_name }}</h2>
      <button class="view-btn" @click="viewProject" data-testid='proj-details'>
        <span class="btn-text">View Project Details</span>
        <svg class="btn-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M5 12h14M12 5l7 7-7 7"/>
        </svg>
        <div class="btn-underline"></div>
      </button>
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
            <span v-if="computedTaskStatusFilter !== 'Active'" class="filter-indicator"
              :class="`status-${computedTaskStatusFilter.toLowerCase().replace(' ', '-')}`">
              ({{ computedTaskStatusFilter }})
            </span>
          </h4>
        </div>

        <div class="tasks-controls">
          <!-- Status Filter -->
            <div class="status-filter">
              <label class="filter-label">Filter:</label>
              <select 
                :value="computedTaskStatusFilter" 
                @input="taskStatusFilter = $event.target.value"
                class="status-filter-select" 
                @change="onStatusFilterChange">
                <option value="Active">Active</option>
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
      </div>

      <!-- Add Task Button -->
      <button class="add-task-btn" @click="$emit('add-task', project)" :disabled="isCompletedProject">
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
    },
    showCompletedProjects: {
      type: Boolean,
      default: false
    }
  },
  emits: ['edit-project', 'view-task', 'add-task'],
  mounted() {
    // // Debug: Check what data the component receives when mounted
    // console.log('=== ProjectCard Debug ===');
    // console.log('Project name:', this.project.proj_name);
    // console.log('Project ID:', this.project.id);
    // console.log('Project status:', this.project.proj_status || this.project.status);
    // console.log('Show completed projects:', this.showCompletedProjects);
    // console.log('isCompletedProject computed:', this.isCompletedProject);

    if (!this.project.id) {
      console.error('⚠️ PROJECT ID IS MISSING!');
      console.error('This will cause navigation to fail');
    }

    // Initialize the filter based on project completion status
    this.initializeFilter();
  },

  created() {
    // Also try to initialize in created hook to ensure early setup
    this.initializeFilter();
  },
  data() {
    return {
      showEdit: false,
      selectedTask: null,
      taskSortOrder: 'asc',
      taskStatusFilter: null, // Will be set based on project status
      filterInitialized: false
    }
  },
  computed: {
    isCompletedProject() {
      // Check multiple possible fields for project completion status
      const status = this.project.proj_status || this.project.status || this.project.project_status || '';
      const statusLower = String(status).toLowerCase().trim();
      
      // Also check if all tasks are completed
      const allTasksCompleted = this.project.tasks && this.project.tasks.length > 0 && 
        this.project.tasks.every(task => {
          const taskStatus = task.task_status || task.status || '';
          return String(taskStatus).toLowerCase().trim() === 'completed';
        });
      
      const isCompleted = statusLower === 'completed' || allTasksCompleted;
      console.log('Project:', this.project.proj_name, 'Status:', status, 'Is Completed:', isCompleted);
      
      return isCompleted;
    },

    computedTaskStatusFilter() {
      // If taskStatusFilter hasn't been set yet, determine it from project status
      if (this.taskStatusFilter === null) {
        return this.isCompletedProject ? 'Completed' : 'Active';
      }
      return this.taskStatusFilter;
    },

    filteredAndSortedTasks() {
      if (!this.project.tasks || this.project.tasks.length === 0) {
        return [];
      }

      const filterValue = this.computedTaskStatusFilter;
      let filtered = [...this.project.tasks];

      if (filterValue === 'Active') {
        filtered = filtered.filter(task => this.isActiveStatus(task.task_status || task.status));
      } else if (filterValue === 'Completed') {
        filtered = filtered.filter(task => this.normalizeTaskStatus(task.task_status || task.status).toLowerCase() === 'completed');
      } else if (filterValue) {
        filtered = filtered.filter(task => this.normalizeTaskStatus(task.task_status || task.status) === filterValue);
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
        const status = this.normalizeTaskStatus(task.task_status || task.status);
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
  watch: {
    showCompletedProjects: {
      handler(newVal) {
        console.log('showCompletedProjects changed to:', newVal);
        // When the parent toggles completed projects visibility,
        // update the task filter accordingly
        this.$nextTick(() => {
          this.updateTaskFilterBasedOnProjectStatus();
        });
      },
      immediate: false // Changed to false since we handle this in mounted
    },
    
    isCompletedProject: {
      handler(newVal, oldVal) {
        console.log('isCompletedProject changed from:', oldVal, 'to:', newVal, 'for project:', this.project.proj_name);
        // When project completion status changes, update filter
        if (this.filterInitialized) {
          this.$nextTick(() => {
            this.updateTaskFilterBasedOnProjectStatus();
          });
        }
      },
      immediate: false // Changed to false since we handle this in mounted
    },

    'project.tasks': {
      handler() {
        // When tasks change, recheck if project is completed
        if (this.filterInitialized) {
          this.$nextTick(() => {
            this.updateTaskFilterBasedOnProjectStatus();
          });
        }
      },
      deep: true
    }
  },
  methods: {
    initializeFilter() {
      if (this.filterInitialized) {
        return; // Already initialized
      }

      const initialFilter = this.isCompletedProject ? 'Completed' : 'Active';
      console.log('🎯 initializeFilter for', this.project.proj_name, ':', initialFilter);
      console.log('   isCompletedProject:', this.isCompletedProject);
      
      this.taskStatusFilter = initialFilter;
      this.filterInitialized = true;
      
      console.log('   taskStatusFilter set to:', this.taskStatusFilter);
    },

    updateTaskFilterBasedOnProjectStatus() {
      console.log('=== updateTaskFilterBasedOnProjectStatus ===');
      console.log('Project:', this.project.proj_name);
      console.log('isCompletedProject:', this.isCompletedProject);
      console.log('showCompletedProjects:', this.showCompletedProjects);
      console.log('Current taskStatusFilter:', this.taskStatusFilter);
      console.log('filterInitialized:', this.filterInitialized);
      
      // If this is a completed project, ALWAYS show completed tasks
      if (this.isCompletedProject) {
        console.log('✅ Setting filter to Completed for completed project');
        this.taskStatusFilter = 'Completed';
      } else {
        // For active projects, show active tasks
        console.log('✅ Setting filter to Active for active project');
        this.taskStatusFilter = 'Active';
      }
      
      this.filterInitialized = true;
      console.log('New taskStatusFilter:', this.taskStatusFilter);
    },

    normalizeTaskStatus(status) {
      if (typeof status === 'string') {
        const trimmed = status.trim();
        if (!trimmed.length) {
          return 'Unassigned';
        }
        const lookup = {
          'active': 'Active',
          'unassigned': 'Unassigned',
          'ongoing': 'Ongoing',
          'under review': 'Under Review',
          'completed': 'Completed',
          'cancelled': 'Cancelled'
        };
        const normalizedLower = trimmed.toLowerCase();
        return lookup[normalizedLower] || trimmed;
      }
      return 'Unassigned';
    },

    isActiveStatus(status) {
      const normalized = this.normalizeTaskStatus(status).toLowerCase();
      return ['active', 'unassigned', 'ongoing', 'under review'].includes(normalized);
    },

    setTaskSortOrder(order) {
      this.taskSortOrder = order;
    },

    onStatusFilterChange() {
      console.log(`Filtering tasks by status: ${this.taskStatusFilter}`);
    },

    clearStatusFilter() {
      this.taskStatusFilter = 'Active';
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
/* Completed Project Styling */
.project-card.completed-project {
  opacity: 0.8;
  background: #fafafa;
  position: relative;
  border-color: #d1d5db;
  filter: grayscale(0.3);
}

.project-card.completed-project::before {
  content: '✓ COMPLETED';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 28px;
  background: linear-gradient(90deg, #10b981, #059669);
  border-radius: 12px 12px 0 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.65rem;
  font-weight: 700;
  color: white;
  letter-spacing: 0.5px;
}

.project-card.completed-project .project-header {
  margin-top: 28px;
}

.project-card.completed-project .project-title {
  color: #9ca3af;
  text-decoration: line-through;
  text-decoration-color: #d1d5db;
}

.project-card.completed-project .project-description {
  color: #b5b5b5;
}

.project-card.completed-project .meta-value,
.project-card.completed-project .meta-label {
  color: #9ca3af;
}

.project-card.completed-project .view-btn {
  color: #9ca3af;
  opacity: 0.7;
}

.project-card.completed-project .view-btn:hover {
  color: #6b7280;
  opacity: 1;
}

.project-card.completed-project .collaborator-avatar {
  opacity: 0.6;
  filter: grayscale(0.5);
}

.project-card.completed-project .add-task-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  background: #f9fafb;
  color: #d1d5db;
  border-color: #e5e7eb;
  border-style: solid;
}

.project-card.completed-project .add-task-btn:disabled:hover {
  background: #f9fafb;
  border-color: #e5e7eb;
  color: #d1d5db;
  transform: none;
}

.view-btn {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: none;
  padding: 0.5rem 0;
  cursor: pointer;
  color: #3b82f6;
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  align-self: start;
}

.view-btn:hover {
  color: #1d4ed8;
  transform: translateY(-1px);
}

.view-btn:active {
  transform: translateY(0);
}

.btn-text {
  position: relative;
  transition: all 0.3s ease;
}

.btn-arrow {
  width: 16px;
  height: 16px;
  stroke: currentColor;
  stroke-width: 2;
  transition: all 0.3s ease;
  opacity: 0.7;
}

.view-btn:hover .btn-arrow {
  opacity: 1;
  transform: translateX(2px);
}

.btn-underline {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 2px;
  background: linear-gradient(90deg, #3b82f6, #1d4ed8);
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 1px;
}

.view-btn:hover .btn-underline {
  width: 100%;
}

/* Alternative: Clean button style */
.view-btn.button-style {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 0.625rem 1rem;
  color: #475569;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.view-btn.button-style:hover {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  border-color: #3b82f6;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.view-btn.button-style .btn-underline {
  display: none;
}

.view-btn.button-style .btn-arrow {
  opacity: 1;
}

.view-btn.button-style:hover .btn-arrow {
  transform: translateX(2px);
}

.project-card {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
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
  transition: color 0.3s ease;
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
  transition: color 0.3s ease;
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
  transition: color 0.3s ease;
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