<template>
  <div class="crm-container">
    <!-- Header Section -->
    <div class="header-section">
      <div class="container">
        <div class="header-content">
          <h1 class="hero-title">Projects</h1>
          <button class="tab-btn new-project-btn" @click="navigateToCreateProject">
            + New Task
          </button>
        </div>
        
        <div class="action-tabs">
          <button class="tab-btn" :class="{ active: activeTab === 'all' }" @click="activeTab = 'all'">
            All Tasks
          </button>
        </div>
      </div>
    </div>

    <!-- Tasks Section -->
    <div class="tasks-section">
      <div class="container">
        <!-- Loading State -->
        <div v-if="loading" class="loading-state">
          <p>Loading tasks...</p>
        </div>
        
        <!-- Error State -->
        <div v-else-if="error" class="error-state">
          <p class="error-message">{{ error }}</p>
          <button class="retry-btn" @click="loadTasks">Retry</button>
        </div>
        
        <!-- Tasks List -->
        <TaskList
          v-else
          :tasks="filteredTasks"
          :users="users"
          @view-task="handleViewTask"
        />
        
        <!-- Edit Task Modal -->
        <EditTask
          v-if="selectedTask"
          :visible="showEdit"
          :task="selectedTask"
          @close="showEdit = false"
          @saved="onTaskSaved"
        />
      </div>
    </div>
  </div>
</template>

<script>
import TaskList from '../components/Projects/TaskList.vue'
import EditTask from '../components/EditTask.vue'
import { taskService } from '../services/taskService.js'
import { projectService } from '../services/projectService.js'

export default {
  name: 'CRMTaskManager',
  components: {
    TaskList,
    EditTask
  },
  data() {
    return {
      activeTab: 'all',
      tasks: [],
      users: [],
      showEdit: false,
      selectedTask: null,
      loading: true,
      error: null
    }
  },
  async created() {
    await this.loadTasks()
  },
  computed: {
    filteredTasks() {
      if (this.activeTab === 'all') {
        return this.tasks;
      }
      return this.tasks.filter(task => task.assigned_to && task.assigned_to.length > 0);
    }
  },
  methods: {
    async loadTasks() {
      try {
        this.loading = true
        this.error = null
        
        // Load users first for name resolution
        this.users = await projectService.getAllUsers()
        
        // Load all tasks
        this.tasks = await taskService.getTasks()
        
      } catch (error) {
        console.error('Error loading tasks:', error)
        this.error = error.message || 'Failed to load tasks'
      } finally {
        this.loading = false
      }
    },
    navigateToCreateProject() {
      this.$router.push('/createtask');
    },
    handleViewTask(task) {
      // Navigate to task details view
      this.$router.push(`/projects/${task.proj_ID}/tasks/${task.task_ID}`);
    },
    handleEditTask(task) {
      this.selectedTask = task
      this.showEdit = true
    },
    onTaskSaved(updated) {
      this.showEdit = false
      // Update task in local list
      const id = updated.task_ID || updated.id
      const idx = this.tasks.findIndex(t => (t.task_ID || t.id) === id)
      if (idx !== -1) {
        this.$set(this.tasks, idx, { ...this.tasks[idx], ...updated })
      }
    }
  }
}
</script>

<style scoped>
.crm-container {
  min-height: 100vh;
  background: #f8fafc;
}

.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.header-section {
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  padding: 1.5rem 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.hero-title {
  font-size: 2.25rem;
  line-height: 1.2;
  font-weight: 800;
  color: #111827;
  margin-bottom: 0.5rem;
}

.action-tabs {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.tab-btn {
  padding: 0.625rem 1.25rem;
  border: 1px solid #374151;
  background: #fff;
  color: #374151;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn.active {
  background: #111827;
  color: #fff;
  border-color: #111827;
}

.new-project-btn {
  background: #111827;
  color: #fff;
  border-color: #111827;
}

.new-project-btn:hover {
  background: #374151;
  border-color: #374151;
}

.tasks-section {
  padding: 2rem 0;
}

/* Loading and Error States */
.loading-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #6b7280;
}

.error-state {
  text-align: center;
  padding: 3rem 1rem;
}

.error-message {
  color: #dc2626;
  margin-bottom: 1rem;
}

.retry-btn {
  background: #111827;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
}

.retry-btn:hover {
  background: #374151;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .action-tabs {
    flex-direction: column;
  }
}
</style>