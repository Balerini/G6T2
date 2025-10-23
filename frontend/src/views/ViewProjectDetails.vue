<template>
    <div class="view-project-container">
        <!-- Loading State -->
        <div v-if="loading" class="loading-state">
            <div class="spinner"></div>
            <p>Loading project data...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="error-state">
            <h2>⚠ Error</h2>
            <p>{{ error }}</p>
            <button @click="loadProjectData" class="retry-btn">Retry</button>
            <button @click="goBack" class="back-btn">Go Back</button>
        </div>

        <!-- Project Data Display -->
        <div v-else-if="projectData" class="project-content">
            <!-- Header -->
            <div class="project-header">
                <div class="header-actions">
                    <button @click="goBack" class="back-btn">← Back to Projects</button>
                    <button 
                        v-if="canEdit"
                        @click="openEditModal"
                        class="edit-btn"
                    >
                        ✏️ Edit Project
                    </button>
                </div>

                <h1>{{ projectData.proj_name }}</h1>
                <div class="project-meta">
                    <span class="date-range">
                        {{ formatDate(projectData.start_date) }} - {{ formatDate(projectData.end_date) }}
                    </span>
                </div>
                <p class="project-desc">{{ projectData.proj_desc || 'No description' }}</p>
                
                <!-- <button @click="exportProjectPDF" class="export-btn">
                    ⬇ Export Tasks to PDF
                </button>
                <button class="export-btn" :disabled="downloading" @click="exportProjectEXCEL">
                    <span v-if="!downloading">📊 Export Excel Report</span>
                    <span v-else>⏳ Generating...</span>
                </button>    -->

                <div class="export-dropdown">
                    <button @click="toggleDropdown" class="export-btn">
                    Export ▾
                    </button>

                    <transition name="fade">
                    <div v-if="dropdownOpen" class="dropdown-menu">
                        <button
                        @click="exportProjectPDF"
                        class="dropdown-item"
                        >
                        📄 Download as PDF
                        </button>
                        <button
                        @click="exportProjectEXCEL"
                        class="dropdown-item"
                        >
                        📊 Download as Excel
                        </button>
                    </div>
                    </transition>
                </div>
            
            </div>
            
            <!-- Collaborators Section -->
            <div class="collaborators-section">
                <h2>👥 Team Collaborators</h2>
                <div v-if="collaborators.length > 0" class="collaborators-badges">
                    <div v-for="(collab, index) in collaborators" :key="index" class="user-badge">
                        <div class="user-avatar">
                            <div class="avatar-placeholder">
                                {{ getCollabInitials(collab) }}
                            </div>
                        </div>
                        <div class="user-info">
                            <div class="user-name">{{ getCollabName(collab) }}</div>
                        </div>
                    </div>
                </div>
                <div v-else class="no-collaborators">
                    <p>No collaborators assigned to this project yet.</p>
                </div>
            </div>

            <!-- Timeline Summary -->
            <div class="timeline-summary" v-if="timelineSummary">
                <h2>📊 Timeline Summary</h2>
                <div class="summary-grid">
                    <div class="summary-card">
                        <div class="summary-label">Total Collaborators</div>
                        <div class="summary-value">{{ collaborators.length }}</div>
                    </div>
                    <div class="summary-card">
                        <div class="summary-label">Total Tasks</div>
                        <div class="summary-value">{{ allTasks.length }}</div>
                    </div>
                    <div class="summary-card" v-if="taskDateRange.earliest && taskDateRange.latest">
                        <div class="summary-label">Date Range</div>
                        <div class="summary-value small">
                            {{ formatDate(taskDateRange.earliest) }} <br>
                            to {{ formatDate(taskDateRange.latest) }}
                        </div>
                    </div>
                </div>

                <!-- Task Status Breakdown -->
                <div class="status-breakdown" v-if="taskStatusCounts && Object.keys(taskStatusCounts).length > 0">
                    <h3>Task Status:</h3>
                    <div class="status-chips">
                        <div v-for="(count, status) in taskStatusCounts" :key="status" class="status-chip">
                            <span class="status-name">{{ status }}</span>
                            <span class="status-count">{{ count }}</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- All Tasks Section -->
            <div class="all-tasks-section">
                <h2>📋 All Project Tasks</h2>

                <div v-if="allTasks.length > 0" class="tasks-list">
                    <div v-for="task in allTasks" :key="task.id" @click="goToTask(task.id)" class="task-card clickable"
                        :class="{ 'overdue': isOverdue(task.end_date) }">
                        <div class="task-header">
                            <div class="task-name">{{ task.task_name }}</div>
                            <span class="task-status" :class="getStatusClass(task.task_status)">
                                {{ task.task_status }}
                            </span>
                        </div>
                        <div class="task-meta">
                            <span>📅 {{ formatDate(task.start_date) }} - {{ formatDate(task.end_date) }}</span>
                            <span v-if="task.task_priority" class="task-priority"
                                :class="getPriorityClass(task.task_priority)">
                                {{ task.task_priority }}
                            </span>
                            <span v-if="isOverdue(task.end_date) && task.task_status !== 'Completed'"
                                class="overdue-badge">
                                ⚠️ Overdue
                            </span>
                        </div>
                        <div v-if="task.owner" class="task-assignee">
                            Owner: {{ getOwnerName(task.owner) }}
                        </div>
                    </div>
                </div>
                <div v-else class="no-tasks">
                    <p>No tasks found for this project.</p>
                </div>
            </div>

            <div>
                <ViewProjectTeamSchedule :projectId="projectId"/> 
            </div>
        </div>

        <!-- Edit Modal -->
        <CreateProjectForm
          v-if="showEditModal"
          :editMode="true"
          :existingProject="projectData"
          @close="closeEditModal"
          @project-updated="handleProjectUpdated"
          @error="handleProjectUpdateError"
        />

        <!-- Notification Toast -->
        <div v-if="notification.show" class="notification" :class="notification.type">
                {{ notification.message }}
        </div>
    </div>
</template>

<script>
import ViewProjectTeamSchedule from '@/components/ViewProjectTeamSchedule.vue';
import CreateProjectForm from '@/components/CreateProjectForm.vue';
import { projectService } from '../services/projectService.js';
import AuthService from '../services/auth.js'; 

export default {
    name: 'ViewProject',
    data() {
        return {
            projectData: null,
            loading: false,
            error: null,
            downloading: false,
            projectId: null,
            usersMap: {}, // Map of userId -> user object
            showEditModal: false,
            notification: {
                show: false,
                message: '',
                type: 'success'
            },
            dropdownOpen: false,
        };
    },
    components: {
        ViewProjectTeamSchedule,
        CreateProjectForm
    },
    computed: {
        allTasks() {
            if (!this.projectData || !this.projectData.tasks) return [];
            return [...this.projectData.tasks].sort((a, b) => new Date(a.start_date) - new Date(b.start_date));
        },

        collaborators() {
            if (!this.projectData || !this.projectData.collaborators) return [];
            return this.projectData.collaborators;
        },

        timelineSummary() {
            return this.projectData && (this.collaborators.length > 0 || this.allTasks.length > 0);
        },

        taskDateRange() {
            if (!this.allTasks.length) return { earliest: null, latest: null };

            const dates = this.allTasks.map(t => new Date(t.start_date));
            const endDates = this.allTasks.map(t => new Date(t.end_date));

            return {
                earliest: new Date(Math.min(...dates)),
                latest: new Date(Math.max(...endDates))
            };
        },

        taskStatusCounts() {
            if (!this.allTasks.length) return {};

            const counts = {};
            this.allTasks.forEach(task => {
                const status = task.task_status || 'Unknown';
                counts[status] = (counts[status] || 0) + 1;
            });

            return counts;
        },

        canEdit() {
            const currentUser = AuthService.getCurrentUser()
            if (!currentUser || !this.projectData) return false

            const userId = currentUser.id || currentUser.user_ID
            return this.projectData.owner === userId
        }
    },
    created() {
        this.projectId = this.$route.params.project_id;
        console.log('ViewProject created with ID:', this.projectId);
        this.loadProjectData();
    },
    methods: {
        async loadProjectData() {
            this.loading = true;
            this.error = null;

            try {
                console.log('Fetching project data for ID:', this.projectId);

                // Fetch both project data and users in parallel
                const [projectResponse, usersResponse] = await Promise.all([
                    projectService.getProjectWithTasks(this.projectId),
                    projectService.getAllUsersUnfiltered()
                ]);

                console.log('✅ Project response:', projectResponse);
                console.log('✅ Users response:', usersResponse);

                this.projectData = projectResponse;

                // Create a map of userId -> user object
                if (Array.isArray(usersResponse)) {
                    this.usersMap = usersResponse.reduce((map, user) => {
                        map[user.id] = user;
                        return map;
                    }, {});
                }

                console.log('✅ Users map created:', this.usersMap);
            } catch (err) {
                console.error('❌ Error loading project:', err);
                this.error = err.message || 'Failed to load project data';
            } finally {
                this.loading = false;
            }
        },

        formatDate(dateString) {
            if (!dateString) return 'Not set';
            try {
                const date = new Date(dateString);
                return date.toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric'
                });
            } catch (e) {
                return dateString;
            }
        },

        getInitials(name) {
            if (!name) return '?';
            return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
        },

        getCollabInitials(collab) {
            const user = this.getUserFromId(collab);
            if (user && user.name) {
                return user.name.substring(0, 2).toUpperCase();
            }
            // Fallback to user ID
            if (typeof collab === 'string') {
                return collab.substring(0, 2).toUpperCase();
            }
            return '??';
        },

        getCollabName(collab) {
            const user = this.getUserFromId(collab);
            if (user) {
                return user.username || user.name || user.email || collab;
            }
            // Fallback to user ID
            return typeof collab === 'string' ? collab : 'Unknown User';
        },

        getUserFromId(userId) {
            if (typeof userId === 'string') {
                return this.usersMap[userId] || null;
            }
            return null;
        },

        getOwnerName(ownerId) {
            const user = this.getUserFromId(ownerId);
            return user ? (user.username || user.name || user.email) : ownerId;
        },

        isOverdue(endDate) {
            if (!endDate) return false;
            return new Date(endDate) < new Date();
        },

        getStatusClass(status) {
            const statusMap = {
                'Completed': 'status-completed',
                'In Progress': 'status-in-progress',
                'Not Started': 'status-not-started',
                'On Hold': 'status-on-hold',
                'Cancelled': 'status-cancelled'
            };
            return statusMap[status] || 'status-default';
        },

        getPriorityClass(priority) {
            const priorityMap = {
                'High': 'priority-high',
                'Medium': 'priority-medium',
                'Low': 'priority-low'
            };
            return priorityMap[priority] || 'priority-default';
        },

        goToTask(taskId) {
            this.$router.push(`/tasks/${taskId}`);
        },

        goBack() {
            this.$router.push('/projects');
        },
        async exportProjectPDF() {
            try {
                const projectId = this.projectId;
                const projectName = this.projectData.proj_name;
                const response = await fetch(`http://localhost:8000/api/projects/${projectId}/export`);
                if (!response.ok) throw new Error("Failed to export tasks");

                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = `Project_${projectName}_Tasks_Report.pdf`;
                a.click();
                window.URL.revokeObjectURL(url);
            } catch (error) {
                console.error("Export failed:", error);
                alert("Failed to export project tasks. Please try again.");
            }
        },

        openEditModal() {
           this.showEditModal = true 
        },

        closeEditModal() {
           this.showEditModal = false 
        },

        async handleProjectUpdated(updatedProject) {
            try {
                console.log('Project updated:', updatedProject);

                this.closeEditModal()

                // Reload fresh data from database
                await this.loadProjectData();

                // Show success notification
                this.showNotification('Project updated successfully!', 'success');

                // Scroll to top
                window.scrollTo({ top: 0, behavior: 'smooth' });
            
            } catch (error) {
                console.error('Error refreshing project:', error);
                this.showNotification('Failed to refresh project data', 'error');
            }
        },

        handleProjectUpdateError(errorMessage) {
            console.error('Project update error:', errorMessage);
            this.showNotification(`${errorMessage}`, 'error');
        },

        showNotification(message, type = 'success') {
            this.notification = {
            show: true,
            message,
            type
            }
            setTimeout(() => {
            this.notification.show = false
            }, 3000)
        },

        async exportProjectEXCEL() {
            this.downloading = true;
            this.error = null;

            try {
                const projectId = this.projectId;
                // console.log("What is going on: ", this.projectData);
                const projectName = this.projectData.proj_name;
                const response = await fetch(`http://localhost:8000/api/projects/${projectId}/export/xlsx`);
                if (!response.ok) throw new Error("Failed to export tasks");

                const blob = await response.blob();

                // Create a temporary download link
                const url = window.URL.createObjectURL(new Blob([blob]));
                const link = document.createElement("a");

                // Filename: <projectName>_Tasks_Report.xlsx
                const safeName = (projectName || "Project_Report").replace(/\s+/g, "_");
                link.href = url;
                link.setAttribute("download", `Project_${safeName}_Tasks_Report.xlsx`);

                document.body.appendChild(link);
                link.click();
                link.remove();
                window.URL.revokeObjectURL(url);
            } catch (error) {
                console.error("Error downloading XLSX:", error);
                this.error = "Failed to download Excel report.";
            } finally {
                this.downloading = false;
            }
        },
        toggleDropdown() {
            this.dropdownOpen = !this.dropdownOpen;
        },
    }
};
</script>

<style scoped>
.view-project-container {
    min-height: 100vh;
    background: #f8fafc;
    padding: 2rem 1rem;
}

.loading-state,
.error-state {
    max-width: 600px;
    margin: 4rem auto;
    text-align: center;
    padding: 3rem;
    background: white;
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #e5e7eb;
    border-top-color: #3b82f6;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 1rem;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

.error-state h2 {
    color: #dc2626;
    margin-bottom: 1rem;
}

.project-content {
    max-width: 1200px;
    margin: 0 auto;
}

.project-header {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    margin-bottom: 2rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.project-header h1 {
    font-size: 2rem;
    color: #111827;
    margin: 1rem 0;
}

.project-meta {
    display: flex;
    gap: 1rem;
    align-items: center;
    margin: 1rem 0;
}

.date-range {
    color: #6b7280;
    font-size: 0.875rem;
}

.project-desc {
    color: #6b7280;
    line-height: 1.6;
}

/* Collaborators Section */
.collaborators-section {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    margin-bottom: 2rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.collaborators-section h2 {
    color: #111827;
    margin-bottom: 1.5rem;
}

.collaborators-badges {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1rem;
}

.user-badge {
    display: flex;
    align-items: center;
    gap: 1rem;
    background: #f9fafb;
    padding: 1rem;
    border-radius: 12px;
    border: 2px solid #e5e7eb;
    transition: all 0.2s;
}

.user-badge:hover {
    border-color: #3b82f6;
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
}

.user-avatar {
    flex-shrink: 0;
}

.avatar,
.avatar-placeholder {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    object-fit: cover;
}

.avatar-placeholder {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 1.25rem;
}

.user-info {
    flex: 1;
    min-width: 0;
}

.user-name {
    font-weight: 600;
    color: #111827;
    font-size: 1rem;
    margin-bottom: 0.25rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.user-email {
    color: #6b7280;
    font-size: 0.75rem;
    margin-bottom: 0.5rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.user-task-count {
    display: inline-block;
    background: #3b82f6;
    color: white;
    padding: 0.25rem 0.625rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
}

.timeline-summary {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    margin-bottom: 2rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.timeline-summary h2 {
    color: #111827;
    margin-bottom: 1.5rem;
}

.summary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}

.summary-card {
    background: #f9fafb;
    padding: 1.5rem;
    border-radius: 8px;
    text-align: center;
}

.summary-label {
    color: #6b7280;
    font-size: 0.875rem;
    margin-bottom: 0.5rem;
}

.summary-value {
    font-size: 2rem;
    font-weight: 700;
    color: #111827;
}

.summary-value.small {
    font-size: 0.875rem;
    line-height: 1.6;
}

.status-breakdown h3 {
    color: #374151;
    font-size: 1rem;
    margin-bottom: 1rem;
}

.status-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
}

.status-chip {
    background: #f3f4f6;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.status-name {
    color: #374151;
    font-size: 0.875rem;
}

.status-count {
    background: #111827;
    color: white;
    padding: 0.125rem 0.5rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
}

/* All Tasks Section */
.all-tasks-section {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    margin-bottom: 2rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.all-tasks-section h2 {
    color: #111827;
    margin-bottom: 1.5rem;
}

.tasks-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.task-card {
    background: #f9fafb;
    padding: 1.25rem;
    border-radius: 10px;
    border: 2px solid #e5e7eb;
    transition: all 0.2s;
}

.task-card.clickable {
    cursor: pointer;
}

.task-card.clickable:hover {
    border-color: #3b82f6;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
    transform: translateY(-2px);
}

.task-card.overdue {
    border-left: 4px solid #ef4444;
}

.task-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
    gap: 1rem;
}

.task-name {
    font-weight: 600;
    color: #111827;
    font-size: 1rem;
}

.task-status {
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 500;
    white-space: nowrap;
}

.status-completed {
    background: #d1fae5;
    color: #065f46;
}

.status-in-progress {
    background: #dbeafe;
    color: #1e40af;
}

.status-not-started {
    background: #f3f4f6;
    color: #374151;
}

.status-on-hold {
    background: #fef3c7;
    color: #92400e;
}

.status-cancelled {
    background: #fee2e2;
    color: #991b1b;
}

.task-meta {
    display: flex;
    gap: 1rem;
    font-size: 0.875rem;
    color: #6b7280;
    margin-bottom: 0.5rem;
    flex-wrap: wrap;
}

.task-priority {
    padding: 0.125rem 0.5rem;
    border-radius: 8px;
    font-weight: 500;
}

.priority-high {
    background: #fee2e2;
    color: #991b1b;
}

.priority-medium {
    background: #fef3c7;
    color: #92400e;
}

.priority-low {
    background: #dbeafe;
    color: #1e40af;
}

.overdue-badge {
    color: #dc2626;
    font-weight: 600;
}

.task-assignee {
    color: #6b7280;
    font-size: 0.875rem;
    margin-top: 0.5rem;
}

.no-collaborators,
.no-tasks {
    text-align: center;
    padding: 2rem;
    color: #6b7280;
}

.back-btn,
.retry-btn {
    background: #111827;
    color: white;
    border: none;
    padding: 8px 16px; /* Standardized padding */
    border-radius: 6px; /* Standardized border radius */
    cursor: pointer;
    font-size: 14px; 
    font-weight: 500;
    transition: all 0.2s;
    margin-bottom: 0;
}

.back-btn:hover,
.retry-btn:hover {
    background: #374151;
}

@media (max-width: 768px) {
    .collaborators-badges {
        grid-template-columns: 1fr;
    }

    .summary-grid {
        grid-template-columns: 1fr;
    }

    .task-header {
        flex-direction: column;
        align-items: flex-start;
    }
}

.export-dropdown {
  position: relative;
  display: inline-block;
}

/* Main button */
.export-btn {
    background: #111827;
    color: white;
    border: none;
    padding: 8px 16px; 
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px; 
    font-weight: 500;
    transition: all 0.2s;
    margin-bottom: 0;
}

.export-btn:hover {
  background: #374151;
}

/* Dropdown menu */
.dropdown-menu {
  position: absolute;
  right: 0;
  top: 110%;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  width: 180px;
  z-index: 20;
  display: flex;
  flex-direction: column;
}

/* Dropdown items */
.dropdown-item {
  padding: 0.6rem 1rem;
  background: none;
  border: none;
  text-align: left;
  color: #111827;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.15s ease;
}

.dropdown-item:hover {
  background: #f3f4f6;
}

/* Fade-in animation */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}


/* Header actions layout */
.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

/* Edit button */
.edit-btn {
  background: #1f2937;
  color: #ffffff;
  border: none;
  padding: 8px 16px; /* Same height as back button */
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s;
  white-space: nowrap;
}

.edit-btn:hover {
  background: #111827;
}

/* Notification toast */
.notification {
  position: fixed;
  top: 2rem;
  right: 2rem;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  font-weight: 500;
  z-index: 9999;
  animation: slideIn 0.3s ease-out;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.notification.success {
  background: #10b981;
  color: white;
}

.notification.error {
  background: #ef4444;
  color: white;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .notification {
    left: 1rem;
    right: 1rem;
    top: 1rem;
  }
  
  .header-actions {
    flex-direction: column;
    align-items: flex-start;
  }

  .edit-btn,
  .back-btn {
    width: 100%; 
  }
}
</style>