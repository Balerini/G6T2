<template>
  <div class="crm-container">
    <!-- Header Section -->
    <div class="header-section">
      <div class="container">
        <div class="header-content">
          <div class="title-section">
            <h1 class="hero-title">🧑‍💻 Projects</h1>
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
            All Projects
          </button>
          <button class="tab-btn" :class="{ active: activeTab === 'standalone' }" @click="activeTab = 'standalone'">
            Standalone Tasks
          </button>
        </div>
      </div>
    </div>

    <!-- Success Toast -->
    <transition name="toast-slide">
      <div v-if="successMessage" class="toast toast-success">
        <div class="toast-icon">🎉</div>
        <div class="toast-content">
          <div class="toast-title">Success!</div>
          <div class="toast-message">{{ successMessage }}</div>
        </div>
        <button @click="clearSuccessMessage" class="toast-close">×</button>
      </div>
    </transition>

    <!-- Error Toast -->
    <transition name="toast-slide">
      <div v-if="errorMessage" class="toast toast-error">
        <div class="toast-icon">⚠</div>
        <div class="toast-content">
          <div class="toast-title">Error</div>
          <div class="toast-message">{{ errorMessage }}</div>
        </div>
        <button @click="clearErrorMessage" class="toast-close">×</button>
      </div>
    </transition>

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
    <div v-else-if="activeTab === 'all'" class="projects-section">
      <div class="container">
        <!-- Add Filter and Sort Controls -->
        <div v-if="sortedProjects.length > 0 || showCompletedProjects" class="projects-header">
          <div class="projects-info">
            <h3 class="projects-count">{{ sortedProjects.length }} Projects</h3>
          </div>

          <div class="header-controls">
            <!-- Filter Dropdown -->
            <div class="filter-dropdown">
              <button class="filter-btn" @click="toggleFilterMenu">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M2 3.5H14M4 8H12M6 12.5H10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
                Filter
                <span v-if="showCompletedProjects" class="filter-badge">1</span>
              </button>
              
              <!-- Dropdown Menu -->
              <div v-if="showFilterMenu" class="filter-menu" @click.stop>
                <div class="filter-menu-header">
                  <span class="filter-menu-title">Filters</span>
                  <button class="filter-close" @click="showFilterMenu = false">×</button>
                </div>
                <div class="filter-menu-content">
                  <label class="filter-option">
                    <input 
                      type="checkbox" 
                      v-model="showCompletedProjects" 
                      @change="handleToggleCompleted"
                    />
                    <span>Show Completed Projects</span>
                  </label>
                </div>
              </div>
            </div>

            <!-- Sort Controls -->
            <div class="sort-controls">
              <span class="sort-label">Sort:</span>
              <div class="sort-toggle-group">
                <button class="sort-toggle-btn" :class="{ 'active': sortOrder === 'asc' }" @click="setSortOrder('asc')">
                  <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                    <path d="M6 3L9 6H3L6 3Z" fill="currentColor" />
                  </svg>
                  Earliest
                </button>
                <button class="sort-toggle-btn" :class="{ 'active': sortOrder === 'desc' }" @click="setSortOrder('desc')">
                  <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                    <path d="M6 9L3 6H9L6 9Z" fill="currentColor" />
                  </svg>
                  Latest
                </button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="sortedProjects.length === 0 && !showCompletedProjects" class="no-projects">
          <h3>No Active Projects Found</h3>
          <p>There are no active projects available for the {{ currentUser.division_name }} department yet.</p>
          <button class="create-project-btn" @click="navigateToCreateProject">Create First Project</button>
        </div>

        <div v-else-if="sortedProjects.length === 0 && showCompletedProjects" class="no-projects">
          <h3>No Projects Found</h3>
          <p>There are no projects (including completed ones) available yet.</p>
        </div>

        <ProjectList 
          v-else 
          :projects="sortedProjects" 
          :users="users" 
          @view-task="handleViewTask"
          @add-task="handleAddTask" 
        />
      </div>
    </div>

    <!-- Standalone Tasks Section -->
    <div v-else-if="activeTab === 'standalone'" class="standalone-tasks-section">
      <div class="container">
        <div class="filter-sort-bar">
          <div class="filter-group">
            <label for="statusFilter">Filter:</label>
            <select id="statusFilter" v-model="selectedStatus" @change="applyFilters">
              <option value="active">Active</option>
              <option value="Completed">Completed</option>
              <option value="Unassigned">Unassigned</option>
              <option value="Ongoing">Ongoing</option>
              <option value="Under Review">Under Review</option>
            </select>
          </div>

          <div class="sort-group">
            <label>Sort By:</label>
            <div class="sort-mode-toggle">
              <button :class="{ active: sortMode === 'dueDate' }" @click="setSortMode('dueDate')">
                Due Date
              </button>
              <button :class="{ active: sortMode === 'priority' }" @click="setSortMode('priority')">
                Priority
              </button>
            </div>
          </div>

          <div class="sort-group">
            <label>Order:</label>
            <div class="sort-toggle">
              <button :class="{ active: sortOrder === 'asc' }" @click="setSortOrder('asc')">
                ▲ Asc
              </button>
              <button :class="{ active: sortOrder === 'desc' }" @click="setSortOrder('desc')">
                ▼ Desc
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="tasks-section">
        <div class="container">
          <div v-if="loadingStandaloneTasks" class="loading-section">
            <div class="container">
              <div class="loading-spinner">Loading Standalone Tasks...</div>
            </div>
          </div>

          <div v-else>
            <div v-if="filteredAndSortedTasks.length">
              <div v-for="(task, index) in filteredAndSortedTasks" :key="task.id || index" class="task-card">
                <task-card :task="task" :users="users" class="mb-0" @view-task="handleViewTask" />
              </div>
            </div>

            <div v-else class="nofound-section">
              <div class="mt-5">
                <div class="card">
                  <div class="no-tasks-message">
                    <div class="no-tasks-icon">📋</div>
                    <div class="no-tasks-text">No standalone tasks found with this filter or status</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal for Create Task Form -->
    <div v-if="showCreateTaskForm" class="modal-overlay" @click="closeCreateTaskForm">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">{{ selectedProject ? 'Add Task to ' + selectedProject.proj_name : 'Create New Task' }}</h2>
          <button class="close-button" @click="closeCreateTaskForm">×</button>
        </div>
        <div class="modal-body">
          <CreateTaskForm :selectedProject="selectedProject" @success="handleTaskSubmit" @error="handleTaskError" @cancel="closeCreateTaskForm" />
        </div>
      </div>
    </div>

    <CreateProjectForm v-if="showCreateProjectForm" @close="closeCreateProjectForm" @project-created="handleProjectCreated" />
  </div>
</template>

<script>
import ProjectList from '../components/Projects/ProjectList.vue'
import TaskCard from '../components/Projects/TaskCard.vue'
import CreateTaskForm from '../components/CreateTaskForm.vue'
import CreateProjectForm from '../components/CreateProjectForm.vue'
import AuthService from '../services/auth.js'
import { projectAPI, userAPI } from '../services/api.js'
import { ownTasksService } from '../services/myTaskService.js'

export default {
  name: 'CRMProjectManager',
  components: {
    ProjectList,
    TaskCard,
    CreateTaskForm,
    CreateProjectForm
  },
  data() {
    return {
      activeTab: 'all',
      projects: [],
      users: [],
      currentUser: null,
      showCreateTaskForm: false,
      showCreateProjectForm: false,
      selectedProject: null,
      loading: true,
      error: null,
      successMessage: '',
      errorMessage: '',
      sortOrder: 'asc',
      standaloneTasks: [],
      loadingStandaloneTasks: true,
      selectedStatus: "active",
      sortMode: "dueDate",
      showCompletedProjects: false,  // Toggle for completed projects
      showFilterMenu: false  // NEW: Controls filter dropdown visibility
    }
  },
  computed: {
    filteredProjects() {
      if (this.activeTab === 'all') {
        return this.projects;
      }
      return this.projects.filter(project => project.collaborators && project.collaborators.length > 0);
    },

    sortedProjects() {
      if (!this.filteredProjects || this.filteredProjects.length === 0) {
        return [];
      }

      const sorted = [...this.filteredProjects].sort((a, b) => {
        if (!a.end_date && !b.end_date) return 0;
        if (!a.end_date) return 1;
        if (!b.end_date) return -1;

        const dateA = new Date(a.end_date);
        const dateB = new Date(b.end_date);

        if (this.sortOrder === 'asc') {
          return dateA - dateB;
        } else {
          return dateB - dateA;
        }
      });

      return sorted;
    },

    processedProjects() {
      return this.filteredProjects.map(project => {
        return this.addAutoCollaborators(project);
      });
    },

    filteredAndSortedTasks() {
      let result = [...this.standaloneTasks];
      
      if (this.selectedStatus === "active") {
        result = result.filter(
          (task) => task.task_status?.toLowerCase() !== "completed"
        );
      } else if (this.selectedStatus) {
        result = result.filter(
          (task) =>
            task.task_status?.toLowerCase() ===
            this.selectedStatus.toLowerCase()
        );
      }

      if (this.sortMode === "dueDate") {
        result.sort((a, b) => {
          const dateA = new Date(a.end_date);
          const dateB = new Date(b.end_date);
          return this.sortOrder === "asc" ? dateA - dateB : dateB - dateA;
        });
      } else if (this.sortMode === "priority") {
        result.sort((a, b) => {
          return this.sortOrder === "asc"
            ? a.priority_level - b.priority_level
            : b.priority_level - a.priority_level;
        });
      }
      
      return result;
    },
  },
  
  async created() {
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

  async mounted() {
    if (this.$route.query.refresh === 'true') {
      console.log('Refreshing projects due to refresh parameter');
      await this.fetchProjects();
      if (this.activeTab === 'standalone') {
        await this.loadStandaloneTasks();
      }
      this.$router.replace({ path: '/projects' });
    }

    // Close filter menu when clicking outside
    document.addEventListener('click', this.handleClickOutside);
  },

  beforeUnmount() {
    // Cleanup event listener
    document.removeEventListener('click', this.handleClickOutside);
  },
  
  watch: {
    async activeTab(newTab) {
      if (newTab === 'standalone') {
        await this.loadStandaloneTasks();
      }
    }
  },
  
  methods: {
    addAutoCollaborators(project) {
      const processedProject = JSON.parse(JSON.stringify(project));
      const existingCollaboratorIds = new Set();
      
      if (processedProject.collaborators && Array.isArray(processedProject.collaborators)) {
        processedProject.collaborators.forEach(collab => {
          if (typeof collab === 'object' && collab.id) {
            existingCollaboratorIds.add(collab.id);
          } else if (typeof collab === 'number' || typeof collab === 'string') {
            existingCollaboratorIds.add(collab);
          }
        });
      }

      const taskUserIds = new Set();
      const taskUserNames = new Set();

      if (processedProject.tasks && Array.isArray(processedProject.tasks)) {
        processedProject.tasks.forEach((task) => {
          if (task.owner) {
            if (typeof task.owner === 'string' && task.owner.length > 15) {
              taskUserIds.add(task.owner);
            } else if (typeof task.owner === 'string') {
              taskUserNames.add(task.owner);
            } else {
              taskUserIds.add(task.owner);
            }
          }

          if (task.assigned_to) {
            if (Array.isArray(task.assigned_to)) {
              task.assigned_to.forEach(userId => {
                if (typeof userId === 'string' && userId.length > 15) {
                  taskUserIds.add(userId);
                } else if (typeof userId === 'string') {
                  taskUserNames.add(userId);
                } else {
                  taskUserIds.add(userId);
                }
              });
            } else {
              if (typeof task.assigned_to === 'string' && task.assigned_to.length > 15) {
                taskUserIds.add(task.assigned_to);
              } else if (typeof task.assigned_to === 'string') {
                taskUserNames.add(task.assigned_to);
              } else {
                taskUserIds.add(task.assigned_to);
              }
            }
          }

          if (task.assignee_id) {
            if (typeof task.assignee_id === 'string' && task.assignee_id.length > 15) {
              taskUserIds.add(task.assignee_id);
            } else if (typeof task.assignee_id === 'string') {
              taskUserNames.add(task.assignee_id);
            } else {
              taskUserIds.add(task.assignee_id);
            }
          }
        });
      }

      const newCollaboratorIds = [];

      taskUserIds.forEach(userId => {
        if (!existingCollaboratorIds.has(userId)) {
          const user = this.users.find(u => u.id === userId);
          if (user) {
            newCollaboratorIds.push(user.id);
          }
        }
      });

      taskUserNames.forEach(userName => {
        if (!existingCollaboratorIds.has(userName)) {
          const user = this.users.find(u => {
            const nameMatch = u.name && u.name.toLowerCase().trim() === userName.toLowerCase().trim();
            const usernameMatch = u.username && u.username.toLowerCase().trim() === userName.toLowerCase().trim();
            const emailMatch = u.email && u.email.toLowerCase().trim() === userName.toLowerCase().trim();
            return nameMatch || usernameMatch || emailMatch;
          });

          if (user && !newCollaboratorIds.includes(user.id)) {
            newCollaboratorIds.push(user.id);
          }
        }
      });

      if (!processedProject.collaborators) {
        processedProject.collaborators = [];
      }

      processedProject.collaborators = [...processedProject.collaborators, ...newCollaboratorIds];
      return processedProject;
    },

    async fetchProjects() {
      if (!this.currentUser || !this.currentUser.division_name) {
        this.error = 'User division information not available';
        this.loading = false;
        return;
      }

      try {
        this.loading = true;
        this.error = null;

        console.log(`Fetching projects for division: ${this.currentUser.division_name}, showCompleted: ${this.showCompletedProjects}`);

        // Pass showCompletedProjects to API
        this.projects = await projectAPI.getFilteredProjectsByDivision(
          this.currentUser.division_name, 
          this.currentUser.id, 
          this.showCompletedProjects  // This parameter controls if completed projects are returned
        );

        console.log('Fetched filtered projects:', this.projects);
        console.log(`Found ${this.projects.length} projects`);

      } catch (error) {
        console.error('Error fetching projects:', error);
        this.error = error.error || error.message || 'Failed to fetch projects';

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

    async handleToggleCompleted() {
      console.log(`Toggle completed projects: ${this.showCompletedProjects}`);
      await this.fetchProjects();
    },

    toggleFilterMenu() {
      this.showFilterMenu = !this.showFilterMenu;
    },

    async loadStandaloneTasks() {
      try {
        this.loadingStandaloneTasks = true;
        this.error = null;

        const userString = sessionStorage.getItem('user');
        const userData = JSON.parse(userString);
        const currentUserId = userData.id;

        const allTasks = await ownTasksService.getTasks(currentUserId);
        this.standaloneTasks = allTasks.filter(task => !task.proj_ID || task.proj_ID === null);
      } catch (error) {
        console.error('Error loading standalone tasks:', error);
        this.errorMessage = 'Failed to load standalone tasks';
      } finally {
        this.loadingStandaloneTasks = false;
      }
    },

    async fetchUsers() {
      try {
        this.users = await userAPI.getAllUsers();
      } catch (error) {
        console.error('Error fetching users:', error);
        this.users = [];
      }
    },

    redirectToLogin() {
      AuthService.logout();
      this.$router.push('/login');
    },

    navigateToCreateProject() {
      this.showCreateProjectForm = true;
    },

    closeCreateProjectForm() {
      this.showCreateProjectForm = false;
    },

    handleProjectCreated(newProject) {
      this.showCreateProjectForm = false;
      this.fetchProjects();
      
      const projectName = newProject?.proj_name || newProject?.project?.proj_name || 'Project';
      this.successMessage = `✅ Project "${projectName}" created successfully!`;
      this.errorMessage = '';
      
      window.scrollTo({ top: 0, behavior: 'smooth' });
      
      setTimeout(() => {
        this.clearSuccessMessage();
      }, 4000);
    },

    navigateToCreateTask() {
      this.selectedProject = null;
      this.showCreateTaskForm = true;
    },

    handleViewTask(task) {
      let parentProject = null;

      if (task.proj_ID) {
        parentProject = this.processedProjects.find(project => String(project.id) === String(task.proj_ID));
      }

      if (!parentProject) {
        parentProject = this.processedProjects.find(project =>
          project.tasks && project.tasks.some(t =>
            String(t.id) === String(task.id) ||
            String(t.task_ID) === String(task.task_ID)
          )
        );
      }

      if (!parentProject) {
        console.error('Could not find parent project for task:', task);
        return;
      }

      const projectId = task.proj_ID;
      const taskId = task.id;

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
      const taskName = taskData?.task_name || taskData?.name || 'Task';
      this.successMessage = `✅ Task "${taskName}" created successfully!`;
      this.errorMessage = '';
      
      window.scrollTo({ top: 0, behavior: 'smooth' });
      this.closeCreateTaskForm();
      
      await this.fetchProjects();
      await this.loadStandaloneTasks();
      
      setTimeout(() => {
        this.clearSuccessMessage();
      }, 4000);
    },

    handleTaskError(error) {
      console.error('Task creation error:', error);
      this.errorMessage = `Error creating task: ${error}`;
      this.successMessage = '';
    },

    clearSuccessMessage() {
      this.successMessage = '';
    },

    clearErrorMessage() {
      this.errorMessage = '';
    },

    setSortOrder(order) {
      this.sortOrder = order;
    },
    
    setSortMode(mode) {
      this.sortMode = mode;
    },
    
    applyFilters() {
      // Filters are applied via computed property
    }
  }
}
</script>

<style scoped>
/* ... (keep all your existing styles) ... */

/* NEW STYLES FOR FILTER DROPDOWN */
.header-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.filter-dropdown {
  position: relative;
}

.filter-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #fff;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-btn:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

.filter-btn svg {
  width: 16px;
  height: 16px;
}

.filter-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  background: #3b82f6;
  color: white;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
}

.filter-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 240px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  z-index: 100;
  animation: slideDown 0.2s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.filter-menu-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.filter-menu-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #111827;
}

.filter-close {
  background: none;
  border: none;
  font-size: 1.25rem;
  color: #6b7280;
  cursor: pointer;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.filter-close:hover {
  background: #f3f4f6;
  color: #374151;
}

.filter-menu-content {
  padding: 0.75rem;
}

.filter-option {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-option:hover {
  background: #f9fafb;
}

.filter-option input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: #3b82f6;
}

.filter-option span {
  font-size: 0.875rem;
  color: #374151;
  user-select: none;
}

/* Close dropdown when clicking outside */
@media (max-width: 768px) {
  .filter-menu {
    right: auto;
    left: 0;
  }
}

/* Update projects-header to accommodate new layout */
.projects-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 0;
  background: transparent;
  border: none;
  flex-wrap: wrap;
  gap: 1rem;
}

@media (max-width: 768px) {
  .header-controls {
    flex-direction: column;
    width: 100%;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .completed-toggle {
    width: 100%;
    justify-content: flex-start;
  }
  
  .sort-controls {
    width: 100%;
  }
}

/* Keep all your existing styles below */
.card {
  background: white;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  max-width: 100%;
  margin: 0;
}

.no-tasks-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.no-tasks-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.no-tasks-text {
  font-size: 18px;
  color: #6b7280;
  font-weight: 500;
}

.toast {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 10000;
  display: flex;
  align-items: center;
  min-width: 280px;
  max-width: 400px;
  padding: 12px 16px;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(10px);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  animation: toastBounce 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.toast-success {
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
  color: white;
  border-left: 4px solid #2E7D32;
  animation: toastBounce 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55), toastPulse 2s ease-in-out infinite;
}

.toast-error {
  background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
  color: white;
  border-left: 4px solid #c62828;
}

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

.projects-section {
  padding: 2rem 0;
}

.projects-info {
  flex: 1;
}

.projects-count {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.sort-controls {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.sort-label {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.sort-toggle-group {
  display: flex;
  background: #f3f4f6;
  border-radius: 8px;
  padding: 2px;
  border: 1px solid #e5e7eb;
}

.sort-toggle-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.875rem;
  font-size: 0.8125rem;
  font-weight: 500;
  border: none;
  background: transparent;
  color: #6b7280;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.sort-toggle-btn:hover {
  color: #374151;
  background: rgba(255, 255, 255, 0.7);
}

.sort-toggle-btn.active {
  background: #ffffff;
  color: #111827;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  font-weight: 600;
}

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

.tab-btn:hover {
  background: #f9fafb;
}

.tab-btn.active:hover {
  background: #374151;
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

.standalone-tasks-section {
  padding: 2rem 0;
}

.filter-sort-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem;
  background: #fff;
  padding: 0.75rem 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.filter-group label,
.sort-group label {
  font-weight: 500;
  color: #4b5563;
  margin-right: 0.5rem;
  font-size: 0.9rem;
}

select {
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 0.4rem 0.75rem;
  font-size: 0.9rem;
  background: #f9fafb;
  color: #111827;
  cursor: pointer;
}

select:hover {
  border-color: #9ca3af;
}

.sort-toggle,
.sort-mode-toggle {
  display: inline-flex;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  overflow: hidden;
}

.sort-toggle button,
.sort-mode-toggle button {
  background: #f9fafb;
  border: none;
  padding: 0.4rem 0.9rem;
  font-size: 0.9rem;
  color: #4b5563;
  cursor: pointer;
  transition: all 0.2s ease;
}

.sort-toggle button:hover,
.sort-mode-toggle button:hover {
  background: #f3f4f6;
}

.sort-toggle button.active,
.sort-mode-toggle button.active {
  background: #111827;
  color: white;
}

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

.toast-icon {
  font-size: 20px;
  margin-right: 10px;
  flex-shrink: 0;
}

.toast-content {
  flex: 1;
  min-width: 0;
}

.toast-title {
  font-weight: 600;
  font-size: 13px;
  margin-bottom: 2px;
  opacity: 0.9;
}

.toast-message {
  font-size: 12px;
  line-height: 1.3;
  opacity: 0.95;
}

.toast-close {
  background: none;
  border: none;
  color: white;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  padding: 0;
  margin-left: 10px;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s ease;
  flex-shrink: 0;
}

.toast-close:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.toast-slide-enter-active {
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.toast-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.toast-slide-enter-from {
  transform: translateX(100%) scale(0.8);
  opacity: 0;
}

.toast-slide-leave-to {
  transform: translateX(100%) scale(0.8);
  opacity: 0;
}

@keyframes toastBounce {
  0% {
    transform: translateX(100%) scale(0.8);
    opacity: 0;
  }
  50% {
    transform: translateX(-10px) scale(1.05);
  }
  100% {
    transform: translateX(0) scale(1);
    opacity: 1;
  }
}

@keyframes toastPulse {
  0%, 100% {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  }
  50% {
    box-shadow: 0 4px 16px rgba(76, 175, 80, 0.3), 0 0 12px rgba(76, 175, 80, 0.2);
  }
}

@media (max-width: 768px) {
  .toast {
    right: 10px;
    left: 10px;
    min-width: auto;
    max-width: none;
  }

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

  .projects-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .sort-controls {
    width: 100%;
    justify-content: space-between;
  }

  .projects-count {
    font-size: 1.125rem;
  }

  .sort-toggle-btn {
    padding: 0.5rem 0.75rem;
    font-size: 0.8rem;
  }
}
</style>