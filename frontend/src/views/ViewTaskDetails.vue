<template>
  <div class="view-task-page">
    <!-- Toast Notifications -->
    <div v-if="successMessage"
      style="position: fixed; top: 20px; right: 20px; background: #10b981; color: white; padding: 16px; border-radius: 8px; z-index: 10000; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); min-width: 300px;">
      {{ successMessage }}
    </div>

    <div v-if="uploadProgressMessage"
      style="position: fixed; top: 20px; right: 20px; background: #3b82f6; color: white; padding: 16px; border-radius: 8px; z-index: 10000; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); min-width: 300px;">
      {{ uploadProgressMessage }}
    </div>

    <div v-if="errorMessage"
      style="position: fixed; top: 20px; right: 20px; background: #ef4444; color: white; padding: 16px; border-radius: 8px; z-index: 10000; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); min-width: 300px;">
      {{ errorMessage }}
    </div>


    <!-- Header -->
    <header class="page-header">
      <div class="header-container">
        <div class="breadcrumb">
          <button class="breadcrumb-link" @click="goBack">
            {{ backButtonText }}
          </button>
          <template v-if="parentProject">
            <span class="breadcrumb-separator">/</span>
            <span class="breadcrumb-current">{{ parentProject.proj_name }}</span>
          </template>
          <span class="breadcrumb-separator">/</span>
          <span class="breadcrumb-current">{{ task ? task.task_name : '' }}</span>
        </div>
      </div>
    </header>

    <!-- Loading State -->
    <main v-if="loading" class="page-content">
      <div class="content-container">
        <div class="loading-state">
          <p>Loading task details...</p>
        </div>
      </div>
    </main>

    <!-- Error State -->
    <main v-else-if="error" class="page-content">
      <div class="content-container">
        <div class="error-state">
          <p class="error-message">{{ error }}</p>
          <button class="retry-btn" @click="loadTaskData">Retry</button>
        </div>
      </div>
    </main>

    <!-- Main Content -->
    <main v-else-if="task" class="page-content">
      <div class="content-container">

        <!-- Parent Project Context (only show if task has a parent project) -->
        <div v-if="parentProject" class="parent-project-banner">
          <div class="project-status-indicator" :class="getParentStatusClass(parentProject.proj_status)"></div>
          <div class="banner-content">
            <h1 class="parent-project-title">{{ parentProject.proj_name }}</h1>
            <p class="parent-project-description">{{ parentProject.proj_desc }}</p>
            
            <!-- Project Collaborators -->
            <div v-if="parentProject.collaborators && parentProject.collaborators.length > 0" class="project-collaborators-row">
              <span class="collaborators-label">Collaborators:</span>
              <div class="collaborator-avatars">
                <div v-for="collaboratorId in parentProject.collaborators.slice(0, 6)" :key="collaboratorId" 
                     class="collaborator-avatar" :title="getUserName(collaboratorId)">
                  {{ getInitials(getUserName(collaboratorId)) }}
                </div>
                <div v-if="parentProject.collaborators.length > 6" class="collaborator-more" 
                     :title="`${parentProject.collaborators.length - 6} more collaborators`">
                  +{{ parentProject.collaborators.length - 6 }}
                </div>
              </div>
            </div>
            
            <div class="parent-project-meta">
              <span class="meta-item">
                <strong>Status:</strong> {{ formatStatus(parentProject.proj_status) }}
              </span>
              <span class="meta-item">
                <strong>Duration:</strong> {{ formatDateRange(parentProject.start_date, parentProject.end_date) }}
              </span>
            </div>
          </div>
        </div>

        <!-- Task Details Card -->
        <div class="task-details-card">
          <div class="card-header">
            <h2 class="task-title">{{ task.task_name }}</h2>
            <div class="header-actions">
            <div class="status-badge-large" :class="getTaskStatusClass(task.task_status)">
                {{ formatStatus(task.task_status) }}
            </div>
              <button @click="openEditModal" class="edit-task-btn" v-if="task">
                ✏️ Edit Task
              </button>
            <button @click="openSubtaskModal" class="add-subtask-btn">
              + Add Subtask
            </button>
            </div>
          </div>

          <!-- Key Information Grid -->
          <div class="info-grid">
            <div class="info-card">
              <div class="info-icon">📅</div>
              <div class="info-content">
                <h3 class="info-title">Start Date</h3>
                <p class="info-value">{{ formatDate(task.start_date) }}</p>
              </div>
            </div>

            <div class="info-card">
              <div class="info-icon">⏰</div>
              <div class="info-content">
                <h3 class="info-title">Due Date</h3>
                <p class="info-value">{{ formatDate(task.end_date) }}</p>
                <p class="info-meta" :class="getDueDateClass(task.end_date)">
                  {{ getDueDateStatus(task.end_date) }}
                </p>
              </div>
            </div>

            <div class="info-card">
              <div class="info-icon">👤</div>
              <div class="info-content">
                <h3 class="info-title">Owner</h3>
                <div v-if="task.owner" class="user-info">
                  <div class="user-avatar creator">
                    {{ getInitials(getCreatorName(task.owner)) }}
                  </div>
                  <div class="user-details">
                    <p class="user-name">{{ getCreatorName(task.owner) }}</p>
                    <p class="user-role">Owner</p>
                  </div>
                </div>
                <p v-else class="info-value empty">Not assigned</p>
              </div>
            </div>

            <div class="info-card">
              <div class="info-icon">👥</div>
              <div class="info-content">
                <h3 class="info-title">Assigned To</h3>
                <div v-if="task.assigned_to && task.assigned_to.length > 0" class="assignees-list">
                  <div v-for="userId in task.assigned_to" :key="userId" class="user-info">
                    <div class="user-avatar assignee">
                      {{ getInitials(getUserName(userId)) }}
                    </div>
                    <div class="user-details">
                      <p class="user-name">{{ getUserName(userId) }}</p>
                      <p class="user-role">Assignee</p>
                    </div>
                  </div>
                </div>
                <p v-else class="info-value empty">No assignees</p>
              </div>
            </div>

            <div class="info-card">
              <div class="info-icon">🎯</div>
              <div class="info-content">
                <h3 class="info-title">Priority Level</h3>
                <p class="info-value">{{ formatPriority(task.priority_level) }}</p>
              </div>
            </div>
          </div>

          <!-- Description Section -->
          <div class="description-section">
            <h3 class="section-title">Description</h3>
            <p class="description-text">
              {{ task.task_desc || 'No description provided for this task.' }}
            </p>
          </div>

          <!-- Attachments Section -->
          <div class="attachments-section" v-if="task.attachments && task.attachments.length > 0">
            <h3 class="section-title">Attachments</h3>
            <div class="attachments-grid">
              <div v-for="attachment in task.attachments" :key="attachment" class="attachment-item"
                @click="downloadAttachment(attachment, $event)">
                <div class="attachment-icon">{{ getFileIcon(attachment.name) }}</div>
                <div class="attachment-info">
                  <p class="attachment-name">{{ attachment.name }}</p>
                  <p class="attachment-size">Click to download</p>
                </div>
                <div class="download-icon">⬇️</div>
              </div>
            </div>
          </div>

          <!-- Task Metadata -->
          <div class="metadata-section">
            <h3 class="section-title">Task Information</h3>
            <div class="metadata-grid">
              <div class="metadata-item">
                <span class="metadata-label">Project ID</span>
                <span class="metadata-value">{{ task.proj_ID }}</span>
              </div>
              <div class="metadata-item">
                <span class="metadata-label">Task ID</span>
                <span class="metadata-value">{{ task.id }}</span>
              </div>
              <div class="metadata-item">
                <span class="metadata-label">Owner</span>
                <span class="metadata-value">{{ getCreatorName(task.owner) }}</span>
              </div>
              <div class="metadata-item">
                <span class="metadata-label">Duration</span>
                <span class="metadata-value">{{ formatDateRange(task.start_date, task.end_date) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Subtasks Section with Accordion -->
        <div class="subtasks-section-card" v-if="task">
          <div class="subtasks-header">
            <h3 class="section-title">Subtasks</h3>
          </div>

          <!-- Loading subtasks -->
          <div v-if="loadingSubtasks" class="subtasks-loading">
            <p>Loading subtasks...</p>
          </div>

          <!-- No subtasks -->
          <div v-else-if="!subtasks || subtasks.length === 0" class="no-subtasks">
            <div class="empty-state-icon">📋</div>
            <p class="empty-state-text">No subtasks yet</p>
            <p class="empty-state-subtext">Break down this task into smaller subtasks</p>
          </div>

          <!-- Subtasks accordion list -->
          <div v-else class="subtasks-accordion">
            <div v-for="(subtask, index) in subtasks" :key="subtask.id" class="accordion-item"
              :class="{ 'expanded': expandedSubtask === index }">
              <!-- Accordion Header - Always Visible -->
              <div class="accordion-header" @click="toggleSubtask(index)">
                <div class="subtask-status-indicator" :class="getSubtaskStatusClass(subtask.status)"></div>

                <div class="accordion-header-content">
                  <h4 class="subtask-name">{{ subtask.name }}</h4>

                  <div class="subtask-preview-info">
                    <span class="preview-item">
                      <span class="preview-icon">📅</span>
                      {{ formatDateShort(subtask.start_date) }} - {{ formatDateShort(subtask.end_date) }}
                    </span>
                    <span class="preview-item" v-if="subtask.assigned_to && subtask.assigned_to.length > 0">
                      <span class="preview-icon">👥</span>
                      {{ subtask.assigned_to.length }} collaborator{{ subtask.assigned_to.length !== 1 ? 's' : '' }}
                    </span>
                    <span class="preview-item empty" v-else>
                      <span class="preview-icon">👥</span>
                      No collaborators
                    </span>
                  </div>
                </div>

                <div class="subtask-status-badge" :class="getSubtaskStatusClass(subtask.status)">
                  {{ subtask.status || 'Unassigned' }}
                </div>

                <!-- Edit Button -->
                <button @click.stop="openEditSubtaskModal(subtask)" class="edit-subtask-btn">
                  ✏️ Edit Subtask
                </button>

                <!-- View Details -->
                <div class="accordion-toggle">
                  <span class="view-details-text">View Details</span>
                  <span class="toggle-icon">{{ expandedSubtask === index ? '▼' : '▶' }}</span>
                </div>
              </div>

              <!-- Accordion Body - Expandable Details -->
              <div class="accordion-body" v-show="expandedSubtask === index">
                <div class="subtask-details-grid">
                  <!-- Description -->
                  <div class="detail-section full-width">
                    <h5 class="detail-label">Description</h5>
                    <p class="detail-value" v-if="subtask.description">
                      {{ subtask.description }}
                    </p>
                    <p class="detail-value empty" v-else>
                      No description provided
                    </p>
                  </div>

                  <!-- Start Date -->
                  <div class="detail-section">
                    <h5 class="detail-label">Start Date</h5>
                    <p class="detail-value">{{ formatDate(subtask.start_date) }}</p>
                  </div>

                  <!-- End Date -->
                  <div class="detail-section">
                    <h5 class="detail-label">End Date</h5>
                    <p class="detail-value">{{ formatDate(subtask.end_date) }}</p>
                    <p class="detail-meta" :class="getDueDateClass(subtask.end_date)">
                      {{ getDueDateStatus(subtask.end_date) }}
                    </p>
                  </div>

                  <!-- Collaborators -->
                  <div class="detail-section full-width">
                    <h5 class="detail-label">Collaborators</h5>
                    <div v-if="subtask.assigned_to && subtask.assigned_to.length > 0" class="collaborators-list">
                      <div v-for="userId in subtask.assigned_to" :key="userId" class="collaborator-item">
                        <div class="collaborator-avatar">
                          {{ getInitials(getUserName(userId)) }}
                        </div>
                        <span class="collaborator-name">{{ getUserName(userId) }}</span>
                      </div>
                    </div>
                    <p class="detail-value empty" v-else>
                      No collaborators assigned
                    </p>
                  </div>

                  <!-- Attachments -->
                  <div class="detail-section full-width">
                    <h5 class="detail-label">Attachments</h5>
                    <div v-if="subtask.attachments && subtask.attachments.length > 0" class="attachments-list">
                      <a v-for="(attachment, attachIndex) in subtask.attachments" :key="attachIndex"
                        :href="attachment.url" target="_blank" class="attachment-link">
                        <span class="attachment-icon">{{ getFileIcon(attachment.name) }}</span>
                        <span class="attachment-name">{{ attachment.name }}</span>
                      </a>
                    </div>
                    <p class="detail-value empty" v-else>
                      No attachments
                    </p>
                  </div>

                  <!-- Status -->
                  <div class="detail-section">
                    <h5 class="detail-label">Status</h5>
                    <div class="subtask-status-badge-large" :class="getSubtaskStatusClass(subtask.status)">
                      {{ subtask.status || 'Unassigned' }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Subtask Modal -->
    <div v-if="showSubtaskModal" class="modal-overlay" @click="closeSubtaskModal">
      <div class="modal-content" @click.stop>
        <SubtaskForm :parentTaskId="task.id" :parentProjectId="task.proj_ID"
          :availableCollaborators="getProjectCollaborators()" @subtask-created="handleSubtaskCreated"
          @cancel="closeSubtaskModal" />
      </div>
    </div>

    <!-- Edit Subtask Modal -->
    <div v-if="showEditSubtaskModal" class="modal-overlay" @click="closeEditSubtaskModal">
      <div class="modal-content" @click.stop>
        <EditSubtaskForm
          :subtask="selectedSubtask"
          :availableCollaborators="getProjectCollaborators"
          @subtask-updated="handleSubtaskUpdated"
          @cancel="closeEditSubtaskModal"
        />
      </div>
    </div>  

    <!-- Edit Task Modal -->
    <EditTask v-if="selectedTask" :visible="showEdit" :task="selectedTask" :users="users" :parentProject="parentProject" @close="showEdit = false" @saved="onTaskSaved" />
  </div>
</template>

<script>
import { projectService } from '../services/projectService.js'
import { taskService } from '../services/taskService.js'
import SubtaskForm from '../components/SubTaskForm.vue'
import EditTask from '../components/EditTask.vue'
import EditSubtaskForm from '../components/EditSubtaskForm.vue' 
import { storage } from '../firebase.js'
import { ref as storageRef, getBlob } from 'firebase/storage'

export default {
  name: 'ViewIndivTask',
  components: {
    SubtaskForm,
    EditTask,
    EditSubtaskForm,
  },
  data() {
    return {
      projects: [],
      tasks: [],
      users: [],
      task: null,
      parentProject: null,
      loading: true,
      error: null,
      showSubtaskModal: false,
      successMessage: '',
      errorMessage: '',
      uploadProgressMessage: '',
      showEdit: false,
      selectedTask: null,
      subtasks: [],
      loadingSubtasks: false,
      expandedSubtask: null,
      showEditSubtaskModal: false,
      selectedSubtask: null,
    }
  },
  created() {
    this.loadTaskData()
  },
  watch: {
    '$route'() {
      this.loadTaskData()
    }
  },
  computed: {
    isTaskOwner() {
      try {
        const userStr = sessionStorage.getItem('user');
        if (!userStr || !this.task) {
          return false;
        }
        const currentUser = JSON.parse(userStr);
        return String(this.task.owner) === String(currentUser.id);
      } catch (error) {
        console.error('Error checking task ownership:', error);
        return false;
      }
    },
    
    backButtonText() {
      const from = this.$route?.query?.from;
      
      if (from === 'dashboard') {
        return '← Back to Dashboard';
      } else if (from === 'schedule') {
        return '← Back to My Schedule';
      } else if (this.parentProject) {
        return '← Back to Projects';
      } else {
        return '← Back to My Tasks';
      }
    }
  },
  methods: {
    async loadTaskData() {
      try {
        this.loading = true;
        this.error = null;

        const projectId = this.$route.params.projectId;
        const taskId = this.$route.params.taskId;

        console.log('Route params:', { projectId, taskId });
        
        // Validate route parameters - taskId is required, projectId is optional (for standalone tasks)
        if (!taskId) {
          this.error = `Invalid route parameters. Task ID is required.`;
          return;
        }

        // Load users first
        try {
          this.users = await projectService.getAllUsersUnfiltered();
        } catch (userError) {
          console.warn('Could not load users:', userError);
        }

        // Load all projects to diagnose the issue
        const allProjects = await projectService.getAllProjects();
        
        if (!allProjects || allProjects.length === 0) {
          this.error = 'No projects found. Please check your connection and try again.';
          return;
        }

        // Find which project actually contains the task we're looking for
        let actualParentProject = null;
        let foundTask = null;

        for (const project of allProjects) {
          if (project.tasks) {
            const taskInThisProject = project.tasks.find(task =>
              String(task.id) === String(taskId) || String(task.task_ID) === String(taskId)
            );

            if (taskInThisProject) {
              actualParentProject = project;
              foundTask = taskInThisProject;
              break;
            }
          }
        }
        // Check if there's a mismatch
        if (actualParentProject && String(actualParentProject.id) !== String(projectId)) {
          this.parentProject = actualParentProject;
          this.task = foundTask;
        } else if (actualParentProject && foundTask) {
          // Everything matches correctly
          this.parentProject = actualParentProject;
          this.task = foundTask;
        } else {
          // Task genuinely not found anywhere
          console.error('Task not found in any project');
          console.log('Searching for taskId:', taskId);
          console.log('Searching for projectId:', projectId);
          
          allProjects.forEach(proj => {
            if (proj.tasks && proj.tasks.length > 0) {
              console.log(`${proj.proj_name}:`, proj.tasks.map(t => `${t.id} (${t.task_name})`));
            }
          });
          
          // Try to load the task directly from the backend as a fallback
          console.log('Attempting to load task directly from backend...');
          try {
            const directTask = await taskService.getTask(taskId);
            if (directTask) {
              // Find the parent project by the task's proj_ID
              // For standalone tasks (proj_ID is null), parentProject will be null
              const parentProject = directTask.proj_ID 
                ? allProjects.find(proj => String(proj.id) === String(directTask.proj_ID))
                : null;

              // If task has a proj_ID but project not found, show error
              // If task has no proj_ID (standalone), allow it to load without a project
              if (directTask.proj_ID && !parentProject) {
                this.error = `Task found but parent project not found. Task proj_ID: ${directTask.proj_ID}`;
                return;
              }

              // Load task (with or without parent project)
                this.task = directTask;
                this.parentProject = parentProject;
              console.log('Task loaded directly from backend successfully', parentProject ? '(with project)' : '(standalone task)');
                return;
            }
          } catch (directLoadError) {
            console.error('Failed to load task directly:', directLoadError);
          }
          
          this.error = `Task not found. Task ID: ${taskId}, Project ID: ${projectId}`;
          return;
        }

        // Double-check our final result
        if (!this.task) {
          this.error = `Failed to load task data. Task: ${this.task ? 'Found' : 'Missing'}`;
          return;
        }

        // ACCESS CONTROL CHECK
        if (this.task) {
          try {
            const currentUser = JSON.parse(sessionStorage.getItem('user') || '{}');
            const userId = currentUser.id;

            if (!userId) {
              this.error = 'Unable to verify user identity. Please log in again.';
              return;
            }

            // For standalone tasks, skip project collaborator check
            const isProjectCollaborator = this.parentProject 
              ? this.parentProject.collaborators?.includes(userId)
              : false;
            const isTaskAssignee = this.task.assigned_to?.includes(userId);
            const isTaskCreator = String(this.task.owner) === String(userId);

            console.log('Access Control Debug:', {
              userId,
              taskOwner: this.task.owner,
              taskAssignedTo: this.task.assigned_to,
              isProjectCollaborator,
              isTaskAssignee,
              isTaskCreator,
              parentProject: !!this.parentProject
            });

            const hasAccess = isProjectCollaborator || isTaskAssignee || isTaskCreator;

            if (!hasAccess) {
              console.error('Access denied for task:', this.task);
              this.error = 'Access denied. You do not have permission to view this task.';
              return;
            }
            
            console.log('✅ Access granted to task');

            await this.loadSubtasks();

          } catch (authError) {
            console.error('Error checking user access:', authError);
            this.error = 'Unable to verify access permissions. Please try again.';
            return;
          }
        }

      } catch (error) {
        console.error('Error loading task data:', error);
        this.error = error.message;
      } finally {
        this.loading = false;
      }
    },

    goBack() {
      // Check where user came from
      const from = this.$route?.query?.from;
      
      if (from === 'dashboard') {
        // User came from dashboard - go back to dashboard
        this.$router.push('/');
      } else if (from === 'schedule') {
        // User came from My Schedule - go back to My Schedule
        this.$router.push('/my-schedule');
      } else if (this.parentProject) {
        // Task belongs to a project - go back to projects page
        this.$router.push('/projects');
      } else {
        // Standalone task - go back to My Tasks view on dashboard
        this.$router.push('/?view=my');
      }
    },

    getParentStatusClass(status) {
      const statusClasses = {
        'in-progress': 'status-progress',
        'to-do': 'status-todo',
        'completed': 'status-completed',
        'pending': 'status-pending'
      };
      return statusClasses[status] || 'status-default';
    },

    getTaskStatusClass(status) {
      if (!status) return 'status-not-started';
      const statusClasses = {
        'Unassigned': 'status-unassigned',
        'Ongoing': 'status-ongoing',
        'Under Review': 'status-review',
        'Completed': 'status-completed'
      };
      return statusClasses[status] || 'status-default';
    },

    formatDate(date) {
      if (!date) return 'No date set';
      return new Date(date).toLocaleDateString('en-US', {
        weekday: 'long',
        day: '2-digit',
        month: 'long',
        year: 'numeric'
      });
    },

    formatDateRange(startDate, endDate) {
      if (!startDate || !endDate) return 'No start or end date set';
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

    formatStatus(status) {
      return status?.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'Not Started';
    },

    getDueDateStatus(dueDate) {
      if (!dueDate) return 'No deadline';

      const now = new Date();
      const due = new Date(dueDate);
      const diffTime = due - now;
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

      if (diffDays < 0) return `Overdue by ${Math.abs(diffDays)} days`;
      if (diffDays === 0) return 'Due today';
      if (diffDays === 1) return 'Due tomorrow';
      if (diffDays <= 7) return `Due in ${diffDays} days`;
      return `${diffDays} days remaining`;
    },

    getDueDateClass(dueDate) {
      if (!dueDate) return '';

      const now = new Date();
      const due = new Date(dueDate);
      const diffTime = due - now;
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

      if (diffDays < 0) return 'overdue';
      if (diffDays <= 1) return 'urgent';
      if (diffDays <= 7) return 'warning';
      return 'normal';
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

    getUserName(userId) {
      // First try to find by document ID (from backend API)
      let user = this.users.find(u => String(u.id) === String(userId));

      // Fallback to user_ID field if it exists
      if (!user) {
        user = this.users.find(u => String(u.user_ID) === String(userId));
      }

      return user ? user.name : 'Unknown User';
    },

    getCreatorName(userId) {
      // First try to find by document ID (from backend API)
      let user = this.users.find(u => String(u.id) === String(userId));

      // Fallback to user_ID field if it exists
      if (!user) {
        user = this.users.find(u => String(u.user_ID) === String(userId));
      }

      return user ? user.name : 'Unknown User';
    },

    openSubtaskModal() {
      this.showSubtaskModal = true;
    },


    closeSubtaskModal() {
      this.showSubtaskModal = false;
    },

    handleSubtaskCreated() {
      this.closeSubtaskModal();
      this.successMessage = '✅ Subtask created successfully!';
      this.errorMessage = '';
      this.uploadProgressMessage = '';

      // Clear success message after delay
      setTimeout(() => {
        this.successMessage = '';
      }, 4000);

      this.loadSubtasks();
    },

    handleUploadProgress(message) {
      this.uploadProgressMessage = message;
      this.successMessage = '';
      this.errorMessage = '';
    },

    handleUploadSuccess(message) {
      this.successMessage = message;
      this.uploadProgressMessage = '';
      this.errorMessage = '';

      // Clear success message after delay
      setTimeout(() => {
        this.successMessage = '';
      }, 3000);
    },

    handleUploadError(message) {
      this.errorMessage = message;
      this.uploadProgressMessage = '';
      this.successMessage = '';

      // Clear error message after delay
      setTimeout(() => {
        this.errorMessage = '';
      }, 5000);
    },

    handleSubtaskError(message) {
      this.errorMessage = `❌ ${message}`;
      this.successMessage = '';
      this.uploadProgressMessage = '';

      // Clear error message after delay
      setTimeout(() => {
        this.errorMessage = '';
      }, 5000);
    },

    getTaskCollaborators() {
      if (!this.task || !this.task.assigned_to || !Array.isArray(this.task.assigned_to)) {
        return [];
      }

      return this.task.assigned_to.map(userId => {
        const user = this.users.find(u => String(u.id) === String(userId));
        return user ? {
          id: user.id,
          name: user.name,
          email: user.email || '',
          department: user.department || 'Unknown',
          role_num: user.role_num || 4,  // Add this line
          rank: user.role_num || 4       // Add this line for compatibility
        } : null;
      }).filter(user => user !== null);
    },

    getProjectCollaborators() {
      if (!this.parentProject || !this.parentProject.collaborators || !Array.isArray(this.parentProject.collaborators)) {
        return [];
      }

      return this.parentProject.collaborators.map(userId => {
        const user = this.users.find(u => String(u.id) === String(userId));
        return user ? {
          id: user.id,
          name: user.name,
          email: user.email || '',
          department: user.division_name || 'Unknown',
          rank: user.role_num || 3
        } : null;
      }).filter(user => user !== null);
    },

    openEditModal() {
      this.selectedTask = this.task;
      this.showEdit = true;
    },

    async onTaskSaved(updated) {
      this.showEdit = false;
      this.task = { ...this.task, ...updated };
      
      // Refresh project data to get updated collaborators
      await this.refreshProjectData();
      
      // Show success message
      this.successMessage = '✅ Task updated successfully!';
      setTimeout(() => {
          this.successMessage = '';
      }, 3000);
    },

    async refreshProjectData() {
      try {
          const allProjects = await projectService.getAllProjects();
          const updatedProject = allProjects.find(proj => 
              String(proj.id) === String(this.parentProject.id)
          );
          
          if (updatedProject) {
              this.parentProject = updatedProject;
              console.log('Project data refreshed with updated collaborators');
          }
      } catch (error) {
          console.error('Error refreshing project data:', error);
      }
    },

    async loadSubtasks() {
      if (!this.task || !this.task.id) return;

      try {
        this.loadingSubtasks = true;
        this.subtasks = await taskService.getSubtasksByTask(this.task.id);
        console.log('Subtasks loaded:', this.subtasks);
      } catch (error) {
        console.error('Error loading subtasks:', error);
        this.subtasks = [];
      } finally {
        this.loadingSubtasks = false;
      }
    },

    toggleSubtask(index) {
      this.expandedSubtask = this.expandedSubtask === index ? null : index;
    },

    formatDateShort(date) {
      if (!date) return 'No date';
      return new Date(date).toLocaleDateString('en-US', {
        day: '2-digit',
        month: 'short'
      });
    },

    getSubtaskStatusClass(status) {
      if (!status) return 'status-unassigned';
      const statusMap = {
        'Unassigned': 'status-unassigned',
        'Ongoing': 'status-ongoing',
        'Under Review': 'status-review',
        'Completed': 'status-completed'
      };
      return statusMap[status] || 'status-default';
    },

    getFileIcon(fileName) {
      if (!fileName) return '📄';
      const ext = fileName.split('.').pop().toLowerCase();
      const iconMap = {
        'pdf': '📄',
        'doc': '📝',
        'docx': '📝',
        'txt': '📄',
        'jpg': '🖼️',
        'jpeg': '🖼️',
        'png': '🖼️',
        'gif': '🖼️'
      };
      return iconMap[ext] || '📄';
    },

    debugAttachments() {
      console.log('=== ATTACHMENT DEBUG ===');
      console.log('Task attachments:', this.task.attachments);
      if (this.task.attachments && this.task.attachments.length > 0) {
        this.task.attachments.forEach((attachment, index) => {
          console.log(`Attachment ${index}:`, attachment);
          console.log(`  - Type:`, typeof attachment);
          console.log(`  - Keys:`, Object.keys(attachment));
          console.log(`  - downloadURL:`, attachment.downloadURL);
          console.log(`  - url:`, attachment.url);
          console.log(`  - name:`, attachment.name);
          console.log(`  - storagePath:`, attachment.storagePath);
        });
      } else {
        console.log('No attachments found');
      }
      console.log('=== END DEBUG ===');
    },

    formatPriority(priority) {
      if (!priority) return 'N/A';
      const num = Number(priority);
      if (num >= 8) return `High ${num}/10`;
      if (num >= 4) return `Medium ${num}/10`;
      return `Low ${num}/10`;
    },
    getPriorityClass(priority) {
      if (!priority) return 'priority-default';
      if (priority >= 8) return 'priority-high';
      if (priority >= 4) return 'priority-medium';
      return 'priority-low';
    },

    async downloadAttachment(attachment, event) {
      try {
        // Prevent any default behavior that might cause redirecting
        if (event) {
          event.preventDefault();
          event.stopPropagation();
        }

        console.log('Downloading attachment:', attachment);

        // Show success message
        this.successMessage = `Downloading ${attachment.name}...`;

        // Get the file URL - try different possible properties
        const fileUrl = attachment.downloadURL || attachment.url || attachment.storagePath;
        console.log('File URL:', fileUrl);

        if (!fileUrl) {
          throw new Error('No download URL found for attachment');
        }

        // Check if it's a Firebase Storage URL (which has CORS restrictions)
        const isFirebaseUrl = fileUrl.includes('firebasestorage.googleapis.com');

        if (isFirebaseUrl) {
          console.log('Firebase Storage URL detected, downloading using Firebase SDK');

          try {
            // Extract the storage path from the URL
            // URL format: https://firebasestorage.googleapis.com/v0/b/bucket/o/path?...
            const urlParts = fileUrl.split('/o/')[1];
            const storagePath = decodeURIComponent(urlParts.split('?')[0]);

            console.log('Storage path:', storagePath);

            // Get reference to the file in Firebase Storage
            const fileRef = storageRef(storage, storagePath);

            // Download the file as a blob using Firebase SDK (no CORS issues)
            const blob = await getBlob(fileRef);
            console.log('Blob downloaded:', blob);

            // Create a download link from the blob
            const blobUrl = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = blobUrl;
            link.download = attachment.name;
            link.style.display = 'none';

            // Trigger download
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            // Clean up
            window.URL.revokeObjectURL(blobUrl);

            console.log('File downloaded successfully to computer');
            this.successMessage = `Downloaded ${attachment.name}`;
            setTimeout(() => {
              this.successMessage = '';
            }, 2000);

          } catch (firebaseError) {
            console.error('Firebase SDK download error:', firebaseError);

            // Fallback: open in new tab
            console.log('Falling back to new tab method');
            window.open(fileUrl, '_blank');

            this.successMessage = `Opening download for ${attachment.name}`;
            setTimeout(() => {
              this.successMessage = '';
            }, 2000);
          }

        } else {
          // For other URLs, try fetch first, then fallback to direct download
          try {
            const response = await fetch(fileUrl, {
              method: 'GET',
              headers: {
                'Accept': '*/*',
              },
            });

            if (!response.ok) {
              throw new Error(`HTTP error! status: ${response.status}`);
            }

            const blob = await response.blob();
            console.log('Blob created:', blob);

            // Create a blob URL
            const blobUrl = window.URL.createObjectURL(blob);

            // Create a temporary anchor element to trigger download
            const link = document.createElement('a');
            link.href = blobUrl;
            link.download = attachment.name;
            link.style.display = 'none';

            // Append to body, click, and remove
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            // Clean up the blob URL
            setTimeout(() => {
              window.URL.revokeObjectURL(blobUrl);
            }, 1000);

          } catch (fetchError) {
            console.log('Fetch failed, trying direct download:', fetchError);

            // Fallback: Direct download link (no redirects)
            const link = document.createElement('a');
            link.href = fileUrl;
            link.download = attachment.name;
            link.style.display = 'none';

            // Force download behavior - no redirects
            link.setAttribute('download', attachment.name);
            link.setAttribute('target', '_self');
            link.setAttribute('rel', 'noopener noreferrer');

            document.body.appendChild(link);
            link.click();

            // Remove immediately
            setTimeout(() => {
              if (document.body.contains(link)) {
                document.body.removeChild(link);
              }
            }, 100);
          }
        }

        // Clear success message after 2 seconds
        setTimeout(() => {
          this.successMessage = '';
        }, 2000);

      } catch (error) {
        console.error('Error downloading attachment:', error);
        this.errorMessage = `Failed to download ${attachment.name}: ${error.message}`;

        // Clear error message after 5 seconds
        setTimeout(() => {
          this.errorMessage = '';
        }, 5000);
      }
    },

    // Subtask Modal
    openEditSubtaskModal(subtask) {
      this.selectedSubtask = { ...subtask };
      this.showEditSubtaskModal = true;
    },

    closeEditSubtaskModal() {
      this.showEditSubtaskModal = false;
      this.selectedSubtask = null;
    },

    handleSubtaskUpdated(updatedSubtask) {
      const idx = this.subtasks.findIndex(s => s.id === updatedSubtask.id);
      if (idx !== -1) {
        this.subtasks[idx] = updatedSubtask;
      }
      this.closeEditSubtaskModal();
      this.successMessage = "Subtask updated successfully!";
      setTimeout(() => { this.successMessage = ""; }, 3000);
    }
  }
}
</script>

<style scoped>
.view-task-page {
  min-height: 100vh;
  background-color: #f8fafc;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
}

/* Toast Notifications */
.toast {
  position: fixed;
  top: 20px;
  right: 20px;
  min-width: 300px;
  max-width: 500px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 10000;
  padding: 16px;
  font-weight: 500;
  animation: slideInRight 0.3s ease;
}

.toast-success {
  border-left: 4px solid #10b981;
  background-color: #f0fdf4;
  color: #166534;
}

.toast-info {
  border-left: 4px solid #3b82f6;
  background-color: #eff6ff;
  color: #1e40af;
}

.toast-error {
  border-left: 4px solid #ef4444;
  background-color: #fef2f2;
  color: #dc2626;
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }

  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Header Styles */
.page-header {
  background-color: #ffffff;
  border-bottom: 1px solid #e5e7eb;
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.breadcrumb-link {
  color: #6b7280;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  font-size: 14px;
  text-decoration: none;
}

.breadcrumb-link:hover {
  color: #111827;
}

.breadcrumb-separator {
  color: #9ca3af;
}

.breadcrumb-current {
  color: #111827;
  font-weight: 500;
}

/* Content Styles */
.page-content {
  padding: 32px;
}

.content-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Parent Project Banner */
.parent-project-banner {
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  padding: 24px;
  display: flex;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.standalone-task-badge {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 20px 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 4px 6px rgba(102, 126, 234, 0.2);
  margin-bottom: 24px;
}

.badge-icon {
  font-size: 24px;
}

.badge-text {
  color: #ffffff;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.project-status-indicator {
  width: 4px;
  height: 60px;
  border-radius: 2px;
  flex-shrink: 0;
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

.banner-content {
  flex: 1;
}

.parent-project-title {
  font-size: 24px;
  font-weight: 700;
  color: #111827;
  margin: 0 0 8px 0;
}

.parent-project-description {
  color: #6b7280;
  margin: 0 0 16px 0;
  line-height: 1.6;
}

.project-collaborators-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 16px;
  font-size: 0.875rem;
}

.collaborators-label {
  color: #6b7280;
  font-weight: 500;
}

.collaborator-avatars {
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
  color: #ffffff !important;
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
  cursor: pointer;
  position: relative;
}

.collaborator-more::after {
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

.collaborator-more:hover::after {
  opacity: 1;
  visibility: visible;
}

.parent-project-meta {
  display: flex;
  gap: 24px;
  font-size: 14px;
}

.meta-item {
  color: #374151;
}

/* Task Details Card */
.task-details-card {
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 32px 32px 24px;
  border-bottom: 1px solid #f3f4f6;
}

.task-title {
  font-size: 28px;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.status-badge-large {
  font-size: 14px;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 600;
}

/* Info Grid */
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  padding: 32px;
  border-bottom: 1px solid #f3f4f6;
}

.info-card {
  display: flex;
  gap: 16px;
  padding: 20px;
  background: #f9fafb;
  border-radius: 12px;
  border: 1px solid #f3f4f6;
}

.info-icon {
  font-size: 24px;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e5e7eb;
  border-radius: 50%;
  flex-shrink: 0;
}

.info-content {
  flex: 1;
}

.info-title {
  font-size: 14px;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 8px 0;
}

.info-value {
  font-size: 16px;
  color: #111827;
  font-weight: 500;
  margin: 0 0 4px 0;
}

.info-value.empty {
  color: #9ca3af;
  font-style: italic;
}

.info-meta {
  font-size: 12px;
  font-weight: 500;
  margin: 0;
}

.info-meta.overdue {
  color: #dc2626;
}

.info-meta.urgent {
  color: #ea580c;
}

.info-meta.warning {
  color: #ca8a04;
}

.info-meta.normal {
  color: #059669;
}

/* User Info */
.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: #374151;
}

.user-avatar.creator {
  background: #e0e7ff;
  color: #3730a3;
}

.user-avatar.assignee {
  background: #fef3c7;
  color: #92400e;
}

.user-details {
  flex: 1;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: #111827;
  margin: 0 0 2px 0;
}

.user-role {
  font-size: 12px;
  color: #6b7280;
  margin: 0;
}

.assignees-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* Sections */
.description-section,
.attachments-section,
.metadata-section {
  padding: 32px;
  border-bottom: 1px solid #f3f4f6;
}

.metadata-section {
  border-bottom: none;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 16px 0;
}

.description-text {
  color: #6b7280;
  line-height: 1.6;
  margin: 0;
}

/* Attachments */
.attachments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #f9fafb;
  border: 1px solid #f3f4f6;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.attachment-item:hover {
  background: #f3f4f6;
  border-color: #3b82f6;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
}

.download-icon {
  font-size: 16px;
  opacity: 0.6;
  transition: opacity 0.2s ease;
}

.attachment-item:hover .download-icon {
  opacity: 1;
}

.attachment-icon {
  font-size: 20px;
}

.attachment-info {
  flex: 1;
}

.attachment-name {
  font-size: 14px;
  font-weight: 500;
  color: #111827;
  margin: 0 0 4px 0;
}

.attachment-size {
  font-size: 12px;
  color: #6b7280;
  margin: 0;
}

/* Metadata Grid */
.metadata-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.metadata-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.metadata-label {
  font-size: 12px;
  font-weight: 500;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.metadata-value {
  font-size: 14px;
  color: #111827;
  font-weight: 500;
}

/* Status Badge Colors */
.status-badge-large.status-progress {
  background: #fef3c7;
  color: #92400e;
}

.status-badge-large.status-todo {
  background: #fecaca;
  color: #991b1b;
}

.status-badge-large.status-completed {
  background: #d1fae5;
  color: #065f46;
}

.status-badge-large.status-pending {
  background: #fed7aa;
  color: #9a3412;
}

.status-badge-large.status-not-started {
  background: #f3f4f6;
  color: #6b7280;
}

/* Loading State */
.loading-state {
  text-align: center;
  padding: 48px;
  color: #6b7280;
}

/* Responsive Design */
@media (max-width: 768px) {
  .header-container {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .page-content {
    padding: 16px;
  }

  .info-grid {
    grid-template-columns: 1fr;
    padding: 16px;
  }

  .parent-project-banner,
  .description-section,
  .attachments-section,
  .metadata-section {
    padding: 16px;
  }

  .card-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
    padding: 16px;
  }

  .metadata-grid,
  .attachments-grid {
    grid-template-columns: 1fr;
  }
}

/* Header Actions */
.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.edit-task-btn {
  background: #1f2937;
  color: #ffffff;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s;
}

.edit-task-btn:hover {
  background: #111827;
}

.add-subtask-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s;
}

.add-subtask-btn:hover {
  background: #2563eb;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 800px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px 0;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 0;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #111827;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6b7280;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #374151;
}

/* Subtasks Section Styles */
.subtasks-section-card {
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.subtasks-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 32px;
  border-bottom: 1px solid #f3f4f6;
}

.subtasks-loading {
  padding: 40px;
  text-align: center;
  color: #6b7280;
}

.no-subtasks {
  padding: 60px 32px;
  text-align: center;
}

.empty-state-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-state-text {
  font-size: 18px;
  font-weight: 600;
  color: #374151;
  margin: 0 0 8px 0;
}

.empty-state-subtext {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

/* Accordion Styles */
.subtasks-accordion {
  display: flex;
  flex-direction: column;
}

.accordion-item {
  border-bottom: 1px solid #f3f4f6;
  transition: background-color 0.2s;
}

.accordion-item:last-child {
  border-bottom: none;
}

.accordion-item.expanded {
  background-color: #f9fafb;
}

.accordion-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 32px;
  cursor: pointer;
  transition: background-color 0.2s;
  user-select: none;
  flex-wrap: nowrap;
  min-height: 90px;
}

.accordion-header:hover {
  background-color: #f9fafb;
}

.accordion-item.expanded .accordion-header {
  background-color: transparent;
}

.subtask-status-indicator {
  width: 4px;
  height: 50px;
  border-radius: 2px;
  flex-shrink: 0;
}

.subtask-status-indicator.status-unassigned {
  background: #9ca3af;
}

.subtask-status-indicator.status-ongoing {
  background: #3b82f6;
}

.subtask-status-indicator.status-review {
  background: #f59e0b;
}

.subtask-status-indicator.status-completed {
  background: #10b981;
}

.accordion-header-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
  overflow: hidden;
  margin-right: auto;
}

.subtask-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.subtask-name {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.subtask-status-badge {
  font-size: 12px;
  padding: 4px 12px;
  border-radius: 12px;
  font-weight: 600;
  flex-shrink: 0;
  white-space: nowrap;
  align-self: center;
}

.subtask-status-badge.status-unassigned {
  background: #f3f4f6;
  color: #6b7280;
}

.subtask-status-badge.status-ongoing {
  background: #dbeafe;
  color: #1e40af;
}

.subtask-status-badge.status-review {
  background: #fef3c7;
  color: #92400e;
}

.subtask-status-badge.status-completed {
  background: #d1fae5;
  color: #065f46;
}

.subtask-preview-info {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.preview-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #374151;
}

.preview-item.empty {
  font-style: italic;
  color: #6b7280;
}

.preview-icon {
  font-size: 14px;
}

.accordion-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
  white-space: nowrap;
  margin-left: 16px;
}

.toggle-icon {
  color: #6b7280;
  font-size: 12px;
  transition: transform 0.2s;
}

/* Accordion Body */
.accordion-body {
  padding: 0 32px 24px 64px;
  animation: slideDown 0.2s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.subtask-details-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  background: white;
  padding: 24px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.detail-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-section.full-width {
  grid-column: 1 / -1;
}

.detail-label {
  font-size: 14px;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0;
}

.detail-value {
  font-size: 16px;
  color: #111827;
  margin: 0;
  line-height: 1.5;
  font-weight: 500;
}

.detail-value.empty {
  color: #9ca3af;
  font-style: italic;
}

.detail-meta {
  font-size: 12px;
  font-weight: 500;
  margin: 4px 0 0 0;
}

.collaborators-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.collaborator-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: #f3f4f6;
  border-radius: 20px;
}

.collaborator-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #e0e7ff;
  color: #3730a3;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
}

.collaborator-name {
  font-size: 14px;
  color: #111827;
  font-weight: 500;
}

.attachments-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.attachment-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  text-decoration: none;
  color: #374151;
  transition: all 0.2s;
}

.attachment-link:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
}

.attachment-icon {
  font-size: 18px;
}

.attachment-name {
  font-size: 14px;
  font-weight: 500;
}

.subtask-status-badge-large {
  display: inline-block;
  font-size: 14px;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 600;
}

.subtask-status-badge-large.status-unassigned {
  background: #f3f4f6;
  color: #6b7280;
}

.subtask-status-badge-large.status-ongoing {
  background: #dbeafe;
  color: #1e40af;
}

.subtask-status-badge-large.status-review {
  background: #fef3c7;
  color: #92400e;
}

.subtask-status-badge-large.status-completed {
  background: #d1fae5;
  color: #065f46;
}

/* Error State */
.error-state {
  text-align: center;
  padding: 48px;
}

.error-message {
  color: #dc2626;
  font-size: 16px;
  margin-bottom: 24px;
}

.retry-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s;
}

.retry-btn:hover {
  background: #2563eb;
}

/* Edit Subtask Button */
.edit-subtask-btn {
  background: #1f2937;
  color: #ffffff;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: background-color 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
  white-space: nowrap;
  align-self: center;
}

.edit-subtask-btn:hover {
  background: #111827;
}

/* Standardize subtask detail fonts */
.subtask-details-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  background: white;
  padding: 24px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.detail-label {
  font-size: 14px; /* Changed from 12px */
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0;
}

.detail-value {
  font-size: 16px; /* Changed from 15px */
  color: #111827;
  margin: 0;
  line-height: 1.5;
}

/* Fix View Details alignment */
.accordion-toggle {
  display: flex;
  align-items: center;
  gap: 8px; 
  flex-shrink: 0;
  white-space: nowrap; /* Prevent wrapping */
  align-self: center;
}

.view-details-text {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
}

.toggle-icon {
  color: #6b7280;
  font-size: 12px;
  transition: transform 0.2s;
}

/* Confirmation Modal Buttons */
.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}

.cancel-btn {
  background: #f3f4f6;
  color: #374151;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cancel-btn:hover {
  background: #e5e7eb;
}

.confirm-btn {
  background: #10b981; /* Green background */
  color: white;
  border: none; /* Remove the black border */
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  outline: none; /* Remove focus outline */
}

.confirm-btn:hover {
  background: #059669; /* Darker green on hover */
}

.confirm-btn:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.3); /* Green focus ring */
}

</style>