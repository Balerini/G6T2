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
                <button @click="goBack" class="back-btn">← Back to Projects</button>
                <h1>{{ projectData.proj_name }}</h1>
                <div class="project-meta">
                    <span class="date-range">
                        {{ formatDate(projectData.start_date) }} - {{ formatDate(projectData.end_date) }}
                    </span>
                </div>
                <p class="project-desc">{{ projectData.proj_desc || 'No description' }}</p>
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
        </div>
    </div>
</template>

<script>
import { projectService } from '../services/projectService.js';

export default {
    name: 'ViewProject',
    data() {
        return {
            projectData: null,
            loading: false,
            error: null,
            projectId: null,
            usersMap: {} // Map of userId -> user object
        };
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
            if (user && user.username) {
                return user.username.substring(0, 2).toUpperCase();
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
        }
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
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s;
    margin-bottom: 1rem;
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
</style>