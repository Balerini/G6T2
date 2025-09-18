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
        <TaskList
          :tasks="filteredTasks"
          @edit-task="handleEditTask"
          @view-subtask="handleViewSubtask"
          @add-subtask="handleAddSubtask"
        />
      </div>
    </div>
  </div>
</template>

<script>
import TaskList from '../components/Projects/TaskList.vue'
import { mockTasks } from '../dummyData/taskData.js'

export default {
  name: 'CRMTaskManager',
  components: {
    TaskList
  },
  data() {
    return {
      activeTab: 'all',
      tasks: mockTasks
    }
  },
  computed: {
    filteredTasks() {
      if (this.activeTab === 'all') {
        return this.tasks;
      }
      return this.tasks.filter(task => task.collaborator && task.collaborator.length > 0);
    }
  },
  methods: {
    navigateToCreateProject() {
      this.$router.push('/createtask');
    },
    handleEditTask(task) {
      console.log('Edit task:', task);
      // edit task logic here
    },
    handleViewSubtask(subtask) {
      this.$router.push(`/tasks/${subtask.taskId}/subtask/${subtask.subTaskId}`);
      console.log('View subtask:', subtask);
      // view subtask logic here
    },
    handleAddSubtask(task) {
      console.log('Add subtask to task:', task);
      // subtask logic here
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