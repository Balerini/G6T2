<template>
  <div class="crm-container">
    <!-- Header Section -->
    <div class="header-section">
      <div class="container">
        <div class="header-content">
          <div class="title-section">
            <h1 class="hero-title">Projects</h1>
            <div class="division-badge" v-if="currentUser">
              {{ currentUser.division_name }} Department
            </div>
          </div>
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
            All Projects ({{ currentUser?.division_name || 'My Division' }})
          </button>
          <button class="tab-btn">
            Standalone Tasks
          </button>
        </div>
      </div>
    </div>

    <!-- Access Denied Section -->
    <div v-if="!currentUser" class="access-denied-section">
      <div class="container">
        <div class="access-denied-message">
          <h2>Access Denied</h2>
          <p>You need to be logged in to view projects. Please log in and try again.</p>
          <button class="login-btn" @click="redirectToLogin">Go to Login</button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-else-if="loading" class="loading-section">
      <div class="container">
        <div class="loading-spinner">Loading projects for {{ currentUser.division_name }} department...</div>
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
        <div v-if="filteredProjects.length === 0" class="no-projects">
          <h3>No Projects Found</h3>
          <p>There are no projects available for the {{ currentUser.division_name }} department yet.</p>
          <button class="create-project-btn" @click="navigateToCreateProject">Create First Project</button>
        </div>
        <ProjectList v-else :projects="filteredProjects" :users="users" @edit-project="handleEditProject"
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
import AuthService from '../services/auth.js'
import { projectAPI, userAPI } from '../services/api.js'

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
      currentUser: null,
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
    // Check authentication status and get current user
    if (!AuthService.checkAuthStatus()) {
      console.warn('User not authenticated, redirecting to login');
      this.loading = false;
      return;
    }

    this.currentUser = AuthService.getCurrentUser();
    console.log('Current user:', this.currentUser);
    
    if (!this.currentUser || !this.currentUser.division_name) {
      this.error = 'User division information not available';
      this.loading = false;
      return;
    }

    await this.fetchProjects();
    await this.fetchUsers();
  },
  methods: {
    async fetchProjects() {
      if (!this.currentUser || !this.currentUser.division_name) {
        this.error = 'User division information not available';
        this.loading = false;
        return;
      }

      try {
        this.loading = true;
        this.error = null;
        
        console.log(`Fetching projects for division: ${this.currentUser.division_name}`);
        
        // Use the new filtered endpoint
        this.projects = await projectAPI.getFilteredProjectsByDivision(this.currentUser.division_name);
        
        console.log('Fetched filtered projects:', this.projects);
        console.log(`Found ${this.projects.length} projects for ${this.currentUser.division_name} department`);
        
      } catch (error) {
        console.error('Error fetching projects:', error);
        this.error = error.error || error.message || 'Failed to fetch projects';
        
        // Fallback to regular projects if filtered endpoint fails
        try {
          console.log('Trying fallback to regular projects endpoint...');
          this.projects = await projectAPI.getAllProjects();
          console.log('Fallback successful, but data is not filtered by division');
        } catch (fallbackError) {
          console.error('Fallback also failed:', fallbackError);
        }
      } finally {
        this.loading = false;
      }
    },

    async fetchUsers() {
      if (!this.currentUser || !this.currentUser.division_name) {
        console.warn('Cannot fetch users - no division info');
        return;
      }

      try {
        console.log(`Fetching users for division: ${this.currentUser.division_name}`);
        
        // Use the new filtered endpoint to only get users from same division
        this.users = await userAPI.getFilteredUsersByDivision(this.currentUser.division_name);
        
        console.log('Fetched filtered users:', this.users);
        console.log(`Found ${this.users.length} users in ${this.currentUser.division_name} department`);
        
      } catch (error) {
        console.error('Error fetching users:', error);
        // Fallback to all users if filtered endpoint fails
        try {
          this.users = await userAPI.getAllUsers();
          console.log('Fell back to all users (not filtered by division)');
        } catch (fallbackError) {
          console.error('Fallback users fetch also failed:', fallbackError);
        }
      }
    },

    redirectToLogin() {
      // Clear any stale session data
      AuthService.logout();
      this.$router.push('/login');
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
      console.log('=== HANDLE VIEW TASK DEBUG ===');
      console.log('Task clicked:', {
        task: task,
        taskId: task.id,
        taskTaskId: task.task_ID,
        taskName: task.task_name,
        taskProjId: task.proj_ID,
        allTaskFields: Object.keys(task)
      });

      // Find the project that contains this task using multiple approaches
      let parentProject = null;

      // Method 1: Find by task's proj_ID field (most reliable)
      if (task.proj_ID) {
        parentProject = this.projects.find(project => String(project.id) === String(task.proj_ID));
        console.log('Method 1 (by task.proj_ID):', {
          searchingFor: task.proj_ID,
          found: parentProject ? parentProject.proj_name : 'NOT FOUND'
        });
      }

      // Method 2: If not found, search through all project tasks (fallback)
      if (!parentProject) {
        parentProject = this.projects.find(project =>
          project.tasks && project.tasks.some(t =>
            String(t.id) === String(task.id) ||
            String(t.task_ID) === String(task.task_ID) ||
            String(t.id) === String(task.task_ID) ||
            String(t.task_ID) === String(task.id)
          )
        );
        console.log('Method 2 (searching through tasks):', {
          found: parentProject ? parentProject.proj_name : 'NOT FOUND'
        });
      }

      if (!parentProject) {
        console.error('Could not find parent project for task:', task);
        console.error('Available projects:', this.projects.map(p => ({
          id: p.id,
          name: p.proj_name,
          taskCount: p.tasks ? p.tasks.length : 0
        })));
        return;
      }

      const projectId = task.proj_ID;
      const taskId = task.id; 

      console.log(projectId, taskId);

      this.$router.push(`/projects/${projectId}/tasks/${taskId}`);
    },

    handleAddTask(project) {
      this.selectedProject = project;
      this.showCreateTaskForm = true;
    },

    closeCreateTaskForm() {
      this.showCreateTaskForm = false;
      this.selectedProject = null;
    },

    async handleTaskSubmit(taskData) {
      console.log('Task submitted:', taskData);
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
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.title-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.hero-title {
  font-size: 2.25rem;
  line-height: 1.2;
  font-weight: 800;
  color: #111827;
  margin: 0;
}

.division-badge {
  background: #e0f2fe;
  color: #0277bd;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 500;
  align-self: flex-start;
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

/* Access Denied State */
.access-denied-section {
  padding: 4rem 0;
  text-align: center;
}

.access-denied-message h2 {
  font-size: 1.5rem;
  color: #dc2626;
  margin-bottom: 1rem;
}

.access-denied-message p {
  color: #6b7280;
  margin-bottom: 2rem;
}

.login-btn {
  background: #111827;
  color: #fff;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.login-btn:hover {
  background: #374151;
}

/* No Projects State */
.no-projects {
  text-align: center;
  padding: 4rem 2rem;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}

.no-projects h3 {
  font-size: 1.5rem;
  color: #111827;
  margin-bottom: 1rem;
}

.no-projects p {
  color: #6b7280;
  margin-bottom: 2rem;
}

.create-project-btn {
  background: #111827;
  color: #fff;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.create-project-btn:hover {
  background: #374151;
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