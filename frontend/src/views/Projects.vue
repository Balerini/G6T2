<template>
  <div class="crm-container">
    <!-- Header Section -->
    <div class="header-section">
      <div class="container">
        <div class="header-content">
          <h1 class="hero-title">Projects</h1>
          <div class="header-buttons">
            <button class="tab-btn new-project-btn" @click="navigateToCreateProject">
              + New Project
            </button>
            <button class="tab-btn new-task-btn" @click="navigateToCreateTask">
              + New Task
            </button>
          </div>
        </div>

        <div class="action-tabs">
          <button class="tab-btn" :class="{ active: activeTab === 'all' }" @click="activeTab = 'all'">
            All Projects
          </button>
          <button class="tab-btn">
            Standalone Tasks
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-section">
      <div class="container">
        <div class="loading-spinner">Loading projects...</div>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-section">
      <div class="container">
        <div class="error-message">{{ error }}</div>
        <button class="retry-btn" @click="fetchProjects">Retry</button>
      </div>
    </div>

    <!-- Projects Section -->
    <div v-else class="projects-section">
      <div class="container">
        <ProjectList :projects="filteredProjects" :users="users" @edit-project="handleEditProject"
          @view-task="handleViewTask" @add-task="handleAddTask" />
      </div>
    </div>

    <!-- Modal for Create Task Form -->
    <div v-if="showCreateTaskForm" class="modal-overlay" @click="closeCreateTaskForm">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">Create Task</h2>
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
import ProjectList from '../components/Projects/ProjectList.vue'
import CreateTaskForm from '../components/CreateTaskForm.vue'
import { projectService } from '../services/projectService.js'

export default {
  name: 'CRMProjectManager',
  components: {
    ProjectList,
    CreateTaskForm
  },
  data() {
    return {
      activeTab: 'all',
      projects: [],
      users: [],
      showCreateTaskForm: false,
      selectedProject: null,
      loading: true,
      error: null
    }
  },
  computed: {
    filteredProjects() {
      if (this.activeTab === 'all') {
        return this.projects;
      }
      return this.projects.filter(project => project.collaborators && project.collaborators.length > 0);
    }
  },
  async created() {
    await this.fetchProjects();
    await this.fetchUsers();
  },
  methods: {
    async fetchProjects() {
      try {
        this.loading = true;
        this.error = null;
        this.projects = await projectService.getAllProjects();
      } catch (error) {
        console.error('Error fetching projects:', error);
        this.error = error.message;
      } finally {
        this.loading = false;
      }
    },

    async fetchUsers() {
      try {
        this.users = await projectService.getAllUsers();
        // console.log('Fetched users:', this.users);

        // // Verify user ID types
        // if (this.users.length > 0) {
        //   console.log('First user ID type:', typeof this.users[0].id);
        //   console.log('First user ID value:', this.users[0].id);
        // }
      } catch (error) {
        console.error('Error fetching users:', error);
      }
    },

    navigateToCreateProject() {
      this.$router.push('/createproject');
    },

    navigateToCreateTask() {
      this.$router.push('/createtask');
    },

    handleEditProject(project) {
      console.log('Edit project:', project);
      // edit project logic here
    },

    handleViewTask(task) {
      // Make sure you're using the correct field names from your database
      const projectId = task.proj_ID || task.projectId; // Adjust based on your DB structure
      const taskId = task.task_ID || task.taskId; // Adjust based on your DB structure

      this.$router.push(`/projects/${projectId}/tasks/${taskId}`);
    },

    handleAddTask(project) {
      // console.log('Add task to project:', project);
      this.selectedProject = project;
      this.showCreateTaskForm = true;
    },

    closeCreateTaskForm() {
      this.showCreateTaskForm = false;
      this.selectedProject = null;
    },

    async handleTaskSubmit(taskData) {
      console.log('Task submitted:', taskData);
      // Handle task submission logic here
      this.closeCreateTaskForm();
      // Refresh projects to show new task
      await this.fetchProjects();
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

.header-buttons {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.new-project-btn,
.new-task-btn {
  background: #111827;
  color: #fff;
  border-color: #111827;
}

.new-project-btn:hover,
.new-task-btn:hover {
  background: #374151;
  border-color: #374151;
}

.new-task-btn {
  background: #fff;
  color: #111827;
  border: 1px solid #d1d5db;
}

.new-task-btn:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

.projects-section {
  padding: 2rem 0;
}

/* Loading and Error States */
.loading-section,
.error-section {
  padding: 4rem 0;
  text-align: center;
}

.loading-spinner {
  font-size: 1.25rem;
  color: #6b7280;
}

.error-message {
  color: #dc2626;
  font-size: 1.125rem;
  margin-bottom: 1rem;
}

.retry-btn {
  background: #111827;
  color: #fff;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
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

  .header-buttons {
    width: 100%;
    justify-content: flex-start;
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