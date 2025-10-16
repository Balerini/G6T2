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
        <div class="toast-icon">⌘</div>
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
        <!-- Add Sort Controls -->
        <div v-if="filteredProjects.length > 0" class="projects-header">
          <div class="projects-info">
            <h3 class="projects-count">{{ filteredProjects.length }} Projects</h3>
          </div>
          
          <div class="sort-controls">
            <span class="sort-label">Sort by:</span>
            <div class="sort-toggle-group">
              <button 
                class="sort-toggle-btn"
                :class="{ 'active': sortOrder === 'asc' }"
                @click="setSortOrder('asc')"
              >
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                  <path d="M6 3L9 6H3L6 3Z" fill="currentColor"/>
                </svg>
                Earliest
              </button>
              <button 
                class="sort-toggle-btn"
                :class="{ 'active': sortOrder === 'desc' }"
                @click="setSortOrder('desc')"
              >
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                  <path d="M6 9L3 6H9L6 9Z" fill="currentColor"/>
                </svg>
                Latest
              </button>
            </div>
          </div>
        </div>

        <div v-if="filteredProjects.length === 0" class="no-projects">
          <h3>No Projects Found</h3>
          <p>There are no projects available for the {{ currentUser.division_name }} department yet.</p>
          <button class="create-project-btn" @click="navigateToCreateProject">Create First Project</button>
        </div>

        <!-- UPDATE: Change from filteredProjects to sortedProjects -->
        <ProjectList v-else :projects="sortedProjects" :users="users"
          @view-task="handleViewTask" @add-task="handleAddTask" />
      </div>
    </div>

    <!-- Standalone Tasks Section -->
    <div v-else-if="activeTab === 'standalone'" class="standalone-tasks-section">
      <!-- filter bar -->
      <div class="container">
        <div class="filter-sort-bar">
          <!-- ✅ Status Filter -->
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

          <!-- ✅ Sort Mode Selector -->
          <div class="sort-group">
          <label>Sort By:</label>
          <div class="sort-mode-toggle">
              <button
              :class="{ active: sortMode === 'dueDate' }"
              @click="setSortMode('dueDate')"
              >
              Due Date
              </button>
              <button
              :class="{ active: sortMode === 'priority' }"
              @click="setSortMode('priority')"
              >
              Priority
              </button>
          </div>
          </div>

          <!-- ✅ Ascending / Descending toggle -->
          <div class="sort-group">
          <label>Order:</label>
          <div class="sort-toggle">
              <button
              :class="{ active: sortOrder === 'asc' }"
              @click="setSortOrder('asc')"
              >
              ▲ Asc
              </button>
              <button
              :class="{ active: sortOrder === 'desc' }"
              @click="setSortOrder('desc')"
              >
              ▼ Desc
              </button>
          </div>
          </div>
        </div>
      </div>

      <div class="tasks-section">
        <div class="container">
            <!-- ✅ Loading Spinner -->
            <div v-if="loadingStandaloneTasks" class="loading-section">
            <div class="container">
                <div class="loading-spinner">Loading Standalone Tasks...</div>
            </div>
            </div>

            <!-- ✅ Tasks Loaded -->
            <div v-else>
            <!-- ✅ When there are tasks after filtering/sorting -->
            <div v-if="filteredAndSortedTasks.length">
                <div
                v-for="(task, index) in filteredAndSortedTasks"
                :key="task.id || index"
                class="task-card"
                >
                <!-- ✅ Uses your TaskCard component -->
                <task-card
                    :task="task"
                    :users="users"
                    class="mb-0"
                    @view-task="handleViewTask"
                />
                </div>
            </div>

            <!-- ✅ When no tasks match filter -->
            <div v-else class="nofound-section">
                <div class="mt-5">
                <!-- <div class="d-flex justify-content-center">
                    <svg
                    xmlns="http://www.w3.org/2000/svg"
                    height="100"
                    width="100"
                    fill="currentColor"
                    class="bi bi-clipboard-x"
                    viewBox="0 0 16 16"
                    >
                    <path
                        fill-rule="evenodd"
                        d="M6.146 7.146a.5.5 0 0 1 .708 0L8 8.293l1.146-1.147a.5.5 0 1 1 .708.708L8.707 9l1.147 1.146a.5.5 0 0 1-.708.708L8 9.707l-1.146 1.147a.5.5 0 0 1-.708-.708L7.293 9 6.146 7.854a.5.5 0 0 1 0-.708"
                    />
                    <path
                        d="M4 1.5H3a2 2 0 0 0-2 2V14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V3.5a2 2 0 0 0-2-2h-1v1h1a1 1 0 0 1 1 1V14a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V3.5a1 1 0 0 1 1-1h1z"
                    />
                    <path
                        d="M9.5 1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-3a.5.5 0 0 1-.5-.5v-1a.5.5 0 0 1 .5-.5zm-3-1A1.5 1.5 0 0 0 5 1.5v1A1.5 1.5 0 0 0 6.5 4h3A1.5 1.5 0 0 0 11 2.5v-1A1.5 1.5 0 0 0 9.5 0z"
                    />
                    </svg>
                </div> -->
                <div class="card">
                  <div class="no-tasks-message">
                    <div class="no-tasks-icon">📋</div>
                  <div class="no-tasks-text">No standalone tasks found with this filter or status</div>
                </div>
              </div>
                <!-- <h2 class="text-center mt-2">No standalone tasks found.</h2>
                <p class="text-center">
                    There are no tasks found associated with this filter or status.
                </p> -->
                </div>
            </div>
            </div>
        </div>
        <!-- <div v-if="loadingStandaloneTasks" class="loading-state">
          <p>Loading standalone tasks...</p>
        </div>
        
        <div v-else-if="standaloneTasks.length === 0" class="no-standalone-tasks">
          <div class="empty-state-content">
            <div class="empty-icon">📋</div>
            <h3 class="empty-title">No Standalone Tasks</h3>
           
          </div>
        </div>
        
        <div v-else class="tasks-grid">
          <task-card 
            v-for="task in standaloneTasks" 
            :key="task.id" 
            :task="task" 
            :users="users"
            @view-task="handleViewTask"
          />
        </div> -->
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
          <CreateTaskForm 
            :selectedProject="selectedProject" 
            @success="handleTaskSubmit" 
            @error="handleTaskError" 
            @cancel="closeCreateTaskForm" 
          />
        </div>
      </div>
    </div>

    <!-- Add this modal/form section -->
    <CreateProjectForm 
      v-if="showCreateProjectForm"
      @close="closeCreateProjectForm"
      @project-created="handleProjectCreated"
    />
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
        // Handle projects without start_date (put them at the end)
        if (!a.end_date && !b.end_date) return 0;
        if (!a.end_date) return 1;
        if (!b.end_date) return -1;
        
        const dateA = new Date(a.end_date);
        const dateB = new Date(b.end_date);
        
        if (this.sortOrder === 'asc') {
          return dateA - dateB; // Earliest first
        } else {
          return dateB - dateA; // Latest first
        }
      });

      return sorted;
    },
    
    // NEW: Process projects to add auto-collaborators
    processedProjects() {
      return this.filteredProjects.map(project => {
        return this.addAutoCollaborators(project);
      });
    },

    // standalone tasks
    filteredAndSortedTasks() {
      let result = [...this.standaloneTasks];
      // excluded completed tasks from all
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

      // sort due date
      if (this.sortMode === "dueDate") {
          result.sort((a, b) => {
          const dateA = new Date(a.end_date);
          const dateB = new Date(b.end_date);
          return this.sortOrder === "asc" ? dateA - dateB : dateB - dateA;
          });
      } else if (this.sortMode === "priority") {
          // sort priority (1–10)
          result.sort((a, b) => {
          return this.sortOrder === "asc"
              ? a.priority_level - b.priority_level
              : b.priority_level - a.priority_level;
          });
      }
      console.log("filtered tasks", result)
      return result;
      },
    
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

  async mounted() {
    // Check if we need to refresh data (e.g., after task creation)
    if (this.$route.query.refresh === 'true') {
      console.log('Refreshing projects due to refresh parameter');
      await this.fetchProjects();
      // Also refresh standalone tasks if on that tab
      if (this.activeTab === 'standalone') {
        await this.loadStandaloneTasks();
      }
      // Remove the refresh parameter from URL
      this.$router.replace({ path: '/projects' });
    }
  },
  watch: {
    async activeTab(newTab) {
      if (newTab === 'standalone') {
        await this.loadStandaloneTasks();
      }
    }
  },
  methods: {
    // NEW: Method to automatically add collaborators from tasks
    addAutoCollaborators(project) {
      // Create a deep copy of the project to avoid mutating the original
      const processedProject = JSON.parse(JSON.stringify(project));
      
      // console.log(`=== PROCESSING PROJECT: ${processedProject.proj_name} ===`);
      // console.log('Project data:', {
      //   id: processedProject.id,
      //   name: processedProject.proj_name,
      //   tasksCount: processedProject.tasks ? processedProject.tasks.length : 0,
      //   existingCollaborators: processedProject.collaborators
      // });
      
      // Get existing collaborator IDs (if any)
      const existingCollaboratorIds = new Set();
      if (processedProject.collaborators && Array.isArray(processedProject.collaborators)) {
        processedProject.collaborators.forEach(collab => {
          if (typeof collab === 'object' && collab.id) {
            existingCollaboratorIds.add(collab.id);
            // console.log(`Existing collaborator (object): ID ${collab.id}, Name: ${collab.name || collab.username}`);
          } else if (typeof collab === 'number') {
            existingCollaboratorIds.add(collab);
            // console.log(`Existing collaborator (ID only): ${collab}`);
          } else if (typeof collab === 'string') {
            existingCollaboratorIds.add(collab);
            // console.log(`Existing collaborator (string): ${collab}`);
          }
        });
      }
      
      // Collect unique user IDs from tasks
      const taskUserIds = new Set();
      const taskUserNames = new Set(); // Also collect by name in case it's stored as string
      
      if (processedProject.tasks && Array.isArray(processedProject.tasks)) {
        processedProject.tasks.forEach((task, index) => {
          console.log(`Task ${index + 1}:`, {
            name: task.task_name,
            owner: task.owner,
            assigned_to: task.assigned_to,
            assignee_id: task.assignee_id,
            allFields: Object.keys(task)
          });
          
          // Add owner user (could be ID or name)
          if (task.owner) {
            // Check if it looks like an ID (long string) or a name
            if (typeof task.owner === 'string' && task.owner.length > 15) {
              // Looks like an ID
              taskUserIds.add(task.owner);
              // console.log(`Added owner ID: ${task.owner}`);
            } else if (typeof task.owner === 'string') {
              // Looks like a name
              taskUserNames.add(task.owner);
              // console.log(`Added owner name: ${task.owner}`);
            } else {
              // It's a number ID
              taskUserIds.add(task.owner);
              // console.log(`Added owner ID: ${task.owner}`);
            }
          }
          
          // Add assigned users
          if (task.assigned_to) {
            if (Array.isArray(task.assigned_to)) {
              task.assigned_to.forEach(userId => {
                if (typeof userId === 'string' && userId.length > 15) {
                  // Looks like an ID
                  taskUserIds.add(userId);
                  // console.log(`Added assigned_to ID: ${userId}`);
                } else if (typeof userId === 'string') {
                  // Looks like a name
                  taskUserNames.add(userId);
                  // console.log(`Added assigned_to name: ${userId}`);
                } else {
                  // It's a number ID
                  taskUserIds.add(userId);
                  // console.log(`Added assigned_to ID: ${userId}`);
                }
              });
            } else {
              if (typeof task.assigned_to === 'string' && task.assigned_to.length > 15) {
                // Looks like an ID
                taskUserIds.add(task.assigned_to);
                console.log(`Added assigned_to ID: ${task.assigned_to}`);
              } else if (typeof task.assigned_to === 'string') {
                // Looks like a name
                taskUserNames.add(task.assigned_to);
                console.log(`Added assigned_to name: ${task.assigned_to}`);
              } else {
                // It's a number ID
                taskUserIds.add(task.assigned_to);
                console.log(`Added assigned_to ID: ${task.assigned_to}`);
              }
            }
          }
          
          // Also check for assignee_id field
          if (task.assignee_id) {
            if (typeof task.assignee_id === 'string' && task.assignee_id.length > 15) {
              // Looks like an ID
              taskUserIds.add(task.assignee_id);
              console.log(`Added assignee_id ID: ${task.assignee_id}`);
            } else if (typeof task.assignee_id === 'string') {
              // Looks like a name
              taskUserNames.add(task.assignee_id);
              console.log(`Added assignee_id name: ${task.assignee_id}`);
            } else {
              // It's a number ID
              taskUserIds.add(task.assignee_id);
              console.log(`Added assignee_id ID: ${task.assignee_id}`);
            }
          }
        });
      }
      
      // console.log('Collected user IDs:', Array.from(taskUserIds));
      // console.log('Collected user names:', Array.from(taskUserNames));
      // console.log('Available users detailed:', this.users.map(u => ({ 
      //   id: u.id, 
      //   name: `"${u.name}"`, 
      //   username: `"${u.username}"`,
      //   nameType: typeof u.name,
      //   usernameType: typeof u.username
      // })));
      
      // Find user IDs for the collected IDs and names
      const newCollaboratorIds = [];
      
      // Match by ID
      taskUserIds.forEach(userId => {
        if (!existingCollaboratorIds.has(userId)) {
          const user = this.users.find(u => u.id === userId);
          if (user) {
            newCollaboratorIds.push(user.id);
          //   console.log(`✅ Auto-adding collaborator by ID: ${user.name || user.username} (ID: ${user.id})`);
          // } else {
          //   console.log(`❌ Could not find user with ID: ${userId}`);
          }
        }
      });
      
      // Match by name/username (case insensitive and flexible)
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
            console.log(`✅ Auto-adding collaborator by name: ${user.name || user.username} (matched: ${userName})`);
          } else if (!user) {
            console.log(`❌ Could not find user with name/username: ${userName}`);
            console.log(`Available user names: ${this.users.map(u => u.name).join(', ')}`);
          }
        }
      });
      
      // Merge existing and new collaborator IDs
      if (!processedProject.collaborators) {
        processedProject.collaborators = [];
      }
      
      processedProject.collaborators = [...processedProject.collaborators, ...newCollaboratorIds];
      
      // console.log(`Final result for "${processedProject.proj_name}":`, {
      //   totalCollaborators: processedProject.collaborators.length,
      //   addedCount: newCollaboratorIds.length,
      //   collaboratorIds: processedProject.collaborators
      // });
      // console.log('=== END PROCESSING ===\n');
      
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
        
        // console.log(`Fetching projects for division: ${this.currentUser.division_name}`);
        
        // Use the new filtered endpoint with user ID
        this.projects = await projectAPI.getFilteredProjectsByDivision(this.currentUser.division_name, this.currentUser.id);
        
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

    async loadStandaloneTasks() {
      try {
        this.loadingStandaloneTasks = true;
        this.error = null;
        
        // Get current user ID
        const userString = sessionStorage.getItem('user');
        const userData = JSON.parse(userString);
        const currentUserId = userData.id;
        
        // Get all tasks for this user
        const allTasks = await ownTasksService.getTasks(currentUserId);
        console.log('All tasks for user:', allTasks);

        // ✅ Filter out tasks that belong to a project (keep only those without proj_ID or with null)
        this.standaloneTasks = allTasks.filter(task => !task.proj_ID || task.proj_ID === null);

          // if (!this.standaloneTasks.length) {
          //   this.error = `No standalone tasks found for user ${currentUserId}`;
          // }
        } 
      catch (error) {
        console.error('Error loading standalone tasks:', error);
        this.errorMessage = 'Failed to load standalone tasks';
        } 
      finally {
        this.loadingStandaloneTasks = false;
        }
      
        // Debug: Check proj_ID values
        // allTasks.forEach(task => {
        //   console.log(`Task: ${task.task_name}, proj_ID: ${task.proj_ID}, type: ${typeof task.proj_ID}`);
        // });
        
        // Filter to only tasks without proj_ID (standalone tasks)
      //   this.standaloneTasks = allTasks.filter(task => {
      //     const hasNoProject = !task.proj_ID || task.proj_ID === null || task.proj_ID === '' || task.proj_ID === 'null';
      //     console.log(`Task: ${task.task_name}, hasNoProject: ${hasNoProject}`);
      //     return hasNoProject;
      //   });
        
      //   console.log('Filtered standalone tasks:', this.standaloneTasks.length, this.standaloneTasks);
      // } catch (error) {
      //   console.error('Error loading standalone tasks:', error);
      //   this.errorMessage = 'Failed to load standalone tasks';
      // } finally {
      //   this.loadingStandaloneTasks = false;
      // }
    },

    async fetchUsers() {
      try {
        console.log('Fetching all users for avatar display');
        
        // Load all users to ensure we have all assignees
        this.users = await userAPI.getAllUsers();
        
        // console.log('Fetched all users:', this.users);
        // console.log(`Found ${this.users.length} users total`);
        
      } catch (error) {
        console.error('Error fetching users:', error);
        this.users = [];
      }
    },

    redirectToLogin() {
      // Clear any stale session data
      AuthService.logout();
      this.$router.push('/login');
    },

    navigateToCreateProject() {
      console.log('Showing create project form...')
      this.showCreateProjectForm = true  
    },

    closeCreateProjectForm() {
      this.showCreateProjectForm = false
    },

    handleProjectCreated(newProject) {
      console.log('Project created successfully:', newProject)
      
      // Close the form
      this.showCreateProjectForm = false
      
      // Refresh the projects list
      this.fetchProjects() // Note: you have fetchProjects, not loadProjects
      
      // Show success message
      const projectName = newProject?.proj_name || newProject?.project?.proj_name || 'Project'
      this.successMessage = `✅ Project "${projectName}" created successfully!`
      this.errorMessage = ''
      
      // Scroll to top to show the toast
      window.scrollTo({ top: 0, behavior: 'smooth' })
      
      // Clear success message after delay
      setTimeout(() => {
        this.clearSuccessMessage()
      }, 4000)
    },

    navigateToCreateTask() {
      this.selectedProject = null; // No pre-selected project
      this.showCreateTaskForm = true;
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
        parentProject = this.processedProjects.find(project => String(project.id) === String(task.proj_ID));
        console.log('Method 1 (by task.proj_ID):', {
          searchingFor: task.proj_ID,
          found: parentProject ? parentProject.proj_name : 'NOT FOUND'
        });
      }

      // Method 2: If not found, search through all project tasks (fallback)
      if (!parentProject) {
        parentProject = this.processedProjects.find(project =>
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
        console.error('Available projects:', this.processedProjects.map(p => ({
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
      console.log('=== PROJECTS PAGE SUCCESS HANDLER ===');
      console.log('Task submitted:', taskData);
      console.log('Task data type:', typeof taskData);
      console.log('Task data keys:', taskData ? Object.keys(taskData) : 'No task data');
      
      // Show success feedback
      const taskName = taskData?.task_name || taskData?.name || 'Task';
      this.successMessage = `✅ Task "${taskName}" created successfully!`;
      this.errorMessage = '';
      
      // Scroll to top to show the toast
      window.scrollTo({ top: 0, behavior: 'smooth' });
      
      // Close the modal
      this.closeCreateTaskForm();
      
      // Refresh projects to show new task
      await this.fetchProjects();
      console.log('Projects refreshed after task creation');
      
      // Also refresh standalone tasks (in case it was a standalone task)
      await this.loadStandaloneTasks();
      console.log('Standalone tasks refreshed after task creation');
      
      // Clear success message after a delay
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
      // console.log(`Setting sort order to: ${order}`);
      this.sortOrder = order;
    },
    setSortMode(mode) {
      this.sortMode = mode;
    },
  }
}
</script>

<style scoped>
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

/* Toast Notifications */
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

/* Toast Animations */
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

/* Responsive */
@media (max-width: 768px) {
  .toast {
    right: 10px;
    left: 10px;
    min-width: auto;
    max-width: none;
  }
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

/* Standalone Tasks Section */
.standalone-tasks-section {
  padding: 2rem 0;
}

.no-standalone-tasks {
  text-align: center;
  padding: 5rem 2rem;
  background: #fff;
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.empty-state-content {
  max-width: 500px;
  margin: 0 auto;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1.5rem;
  opacity: 0.6;
}

.empty-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 0.75rem;
}

.empty-message {
  font-size: 1rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
  line-height: 1.6;
}

.empty-hint {
  font-size: 0.875rem;
  color: #10b981;
  margin-top: 1rem;
  font-weight: 500;
}

.tasks-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

.loading-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #6b7280;
}

.loading-state p {
  font-size: 1rem;
  margin: 0;
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

/* Modern Sort Controls */
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

.sort-toggle-btn svg {
  width: 12px;
  height: 12px;
  transition: all 0.2s ease;
}

.sort-toggle-btn.active svg {
  color: #3b82f6;
}

/* Responsive Design */
@media (max-width: 768px) {
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

/* Match your existing theme colors */
@media (prefers-color-scheme: dark) {
  .projects-count {
    color: #f9fafb;
  }
  
  .sort-toggle-group {
    background: #374151;
    border-color: #4b5563;
  }
  
  .sort-toggle-btn {
    color: #d1d5db;
  }
  
  .sort-toggle-btn:hover {
    color: #f3f4f6;
    background: rgba(75, 85, 99, 0.7);
  }
  
  .sort-toggle-btn.active {
    background: #4b5563;
    color: #f9fafb;
  }
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

/* Labels */
.filter-group label,
.sort-group label {
  font-weight: 500;
  color: #4b5563;
  margin-right: 0.5rem;
  font-size: 0.9rem;
}

/* Dropdown */
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

/* ✅ Shared toggle style (radio-like) */
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
</style>