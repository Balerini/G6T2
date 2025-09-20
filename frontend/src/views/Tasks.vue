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

    <!-- Modal for Create Task Form -->
    <div v-if="showCreateTaskForm" class="modal-overlay" @click="closeCreateTaskForm">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">Create Subtask</h2>
          <button class="close-button" @click="closeCreateTaskForm">×</button>
        </div>
        <div class="modal-body">
          <CreateTaskForm @submit="handleTaskSubmit" @cancel="closeCreateTaskForm" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import TaskList from '../components/Projects/TaskList.vue'
import CreateTaskForm from '../components/CreateTaskForm.vue'
import { mockTasks } from '../dummyData/taskData.js'

export default {
  name: 'CRMTaskManager',
  components: {
    TaskList,
    CreateTaskForm
  },
  data() {
    return {
      activeTab: 'all',
      tasks: mockTasks,
      showCreateTaskForm: false,
      selectedTask: null
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
      this.selectedTask = task;
      this.showCreateTaskForm = true;
    },
    closeCreateTaskForm() {
      this.showCreateTaskForm = false;
      this.selectedTask = null;
    },
    handleTaskSubmit(taskData) {
      console.log('Task submitted:', taskData);
      // Handle task submission logic here
      this.closeCreateTaskForm();
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

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
  padding: 0.25rem;
  line-height: 1;
  transition: color 0.2s ease;
}

.close-button:hover {
  color: #374151;
}

.modal-body {
  padding: 2rem;
}

@media (max-width: 768px) {
  .modal-content {
    margin: 1rem;
    max-height: 95vh;
  }
  
  .modal-header {
    padding: 1rem 1.5rem;
  }
  
  .modal-body {
    padding: 1.5rem;
  }
  
  .modal-title {
    font-size: 1.25rem;
  }
}
</style>