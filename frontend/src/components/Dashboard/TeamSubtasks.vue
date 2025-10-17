<template>
    <div>
        <h3 class="section-title">Team Subtasks</h3>
        
        <!-- Loading State -->
        <div v-if="loading" class="loading">Loading team subtasks...</div>
        
        <!-- Error State -->
        <div v-else-if="error" class="error">Error: {{ error }}</div>
        
        <!-- Main Content -->
        <div v-else class="team-subtasks-card">
            <!-- Filter and Sort Bar -->
            <div class="filter-sort-bar">
                <!-- Sort Dropdown -->
                <div class="sort-group">
                    <label>Sort By:</label>
                    <select v-model="sortBy" class="sort-dropdown">
                        <option value="">Default</option>
                        <option value="due_date">Due Date</option>
                        <option value="priority">Priority</option>
                    </select>
                </div>

                <!-- Filter Dropdown -->
                <div class="filter-group">
                    <label>Filter:</label>
                    <select v-model="filterStatus" class="filter-dropdown">
                        <option value="">All Statuses</option>
                        <option value="Unassigned">Unassigned</option>
                        <option value="Ongoing">Ongoing</option>
                        <option value="Under Review">Under Review</option>
                        <option value="Completed">Completed</option>
                    </select>
                </div>
            </div>

            <!-- Empty State -->
            <div v-if="filteredSubtasks.length === 0" class="empty-state">
                <div class="empty-icon">📋</div>
                <p class="empty-message">No subtasks found for your team</p>
                <p class="empty-submessage">
                    {{ filterStatus ? 'Try changing the filter' : 'Subtasks will appear here once team members create them' }}
                </p>
            </div>

            <!-- Subtasks Table -->
            <div v-else class="table-container">
                <table class="subtasks-table">
                    <thead>
                        <tr>
                            <th>Subtask Name</th>
                            <th>Owner</th>
                            <th>Due Date</th>
                            <th>Status</th>
                            <th>Priority</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="subtask in filteredSubtasks" :key="subtask.id" class="subtask-row">
                            <td class="subtask-name">{{ subtask.name }}</td>
                            <td class="subtask-owner">
                                <div class="owner-info">
                                    <div class="owner-avatar">{{ getInitials(subtask.ownerName) }}</div>
                                    <span>{{ subtask.ownerName }}</span>
                                </div>
                            </td>
                            <td class="subtask-due-date">
                                <span :class="getDueDateClass(subtask.end_date)">
                                    {{ formatDate(subtask.end_date) }}
                                </span>
                            </td>
                            <td class="subtask-status">
                                <span class="status-badge" :class="getStatusClass(subtask.status)">
                                    {{ subtask.status || 'Unassigned' }}
                                </span>
                            </td>
                            <td class="subtask-priority">
                                <span class="priority-badge" :class="getPriorityClass(subtask.priority)">
                                    {{ formatPriority(subtask.priority) }}
                                </span>
                            </td>
                            <td class="subtask-actions">
                                <button @click="viewSubtask(subtask)" class="view-btn">
                                    View
                                </button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Subtask Count -->
            <div v-if="filteredSubtasks.length > 0" class="subtask-count">
                Showing {{ filteredSubtasks.length }} of {{ allSubtasks.length }} subtasks
            </div>
        </div>
    </div>
</template>

<script>
import { taskService } from '@/services/taskService';

export default {
    name: 'TeamSubtasks',
    data() {
        return {
            allSubtasks: [],
            loading: true,
            error: null,
            sortBy: '',
            filterStatus: '',
            loadStartTime: null,
        };
    },
    computed: {
        filteredSubtasks() {
            let result = [...this.allSubtasks];

            // Filter by status
            if (this.filterStatus) {
                result = result.filter(subtask => subtask.status === this.filterStatus);
            }

            // Sort
            if (this.sortBy === 'due_date') {
                result.sort((a, b) => new Date(a.end_date) - new Date(b.end_date));
            } else if (this.sortBy === 'priority') {
                result.sort((a, b) => (b.priority || 0) - (a.priority || 0));
            }

            return result;
        }
    },
    async mounted() {
        try {
            this.loading = true;
            this.error = null;
            this.loadStartTime = Date.now();

            // Get current user (manager)
            const userString = sessionStorage.getItem('user');
            if (!userString) {
                this.error = 'User not found';
                return;
            }

            const currentUser = JSON.parse(userString);
            const userId = currentUser.id;

            console.log('TeamSubtasks - User ID:', userId);

            // Fetch team subtasks
            this.allSubtasks = await taskService.getTeamSubtasks(userId);

            console.log('TeamSubtasks - Response:', this.allSubtasks);

            // Check if loaded within 3 seconds
            const loadTime = Date.now() - this.loadStartTime;
            if (loadTime > 3000) {
                console.warn(`Load time exceeded 3 seconds: ${loadTime}ms`);
            }

        } catch (err) {
            console.error('TeamSubtasks - Error:', err);
            this.error = err.message;
        } finally {
            this.loading = false;
        }
    },
    methods: {
        getInitials(name) {
            if (!name) return '?';
            return name
                .split(' ')
                .map(word => word.charAt(0))
                .join('')
                .substring(0, 2)
                .toUpperCase();
        },

        formatDate(date) {
            if (!date) return 'No date';
            return new Date(date).toLocaleDateString('en-US', {
                day: '2-digit',
                month: 'short',
                year: 'numeric'
            });
        },

        formatPriority(priority) {
            if (!priority) return 'N/A';
            return `${priority}/10`;
        },

        getDueDateClass(dueDate) {
            if (!dueDate) return '';
            const now = new Date();
            const due = new Date(dueDate);
            const diffDays = Math.ceil((due - now) / (1000 * 60 * 60 * 24));

            if (diffDays < 0) return 'overdue';
            if (diffDays <= 1) return 'urgent';
            if (diffDays <= 7) return 'warning';
            return 'normal';
        },

        getStatusClass(status) {
            const statusMap = {
                'Unassigned': 'status-unassigned',
                'Ongoing': 'status-ongoing',
                'Under Review': 'status-review',
                'Completed': 'status-completed'
            };
            return statusMap[status] || 'status-default';
        },

        getPriorityClass(priority) {
            if (!priority) return 'priority-default';
            if (priority >= 8) return 'priority-high';
            if (priority >= 4) return 'priority-medium';
            return 'priority-low';
        },

        viewSubtask(subtask) {
            // Navigate to the task that contains this subtask
            this.$router.push({
                name: 'ViewTaskDetails',
                params: {
                    projectId: subtask.proj_ID,
                    taskId: subtask.task_id
                }
            });
        }
    }
};
</script>

<style scoped>
.section-title {
    font-size: 20px;
    font-weight: 600;
    color: #111827;
    margin-bottom: 20px;
}

.team-subtasks-card {
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border: 1px solid #e5e7eb;
}

.loading,
.error {
    color: #6b7280;
    font-size: 14px;
    margin: 10px;
}

/* Filter/Sort Bar - matches Home.vue */
.filter-sort-bar {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 1rem;
    background: #f9fafb;
    padding: 0.75rem 1rem;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    margin-bottom: 1.5rem;
}

.filter-group label,
.sort-group label {
    font-weight: 500;
    color: #4b5563;
    margin-right: 0.5rem;
    font-size: 0.9rem;
}

.sort-dropdown,
.filter-dropdown {
    border: 1px solid #d1d5db;
    border-radius: 6px;
    padding: 0.4rem 0.75rem;
    font-size: 0.9rem;
    background: white;
    color: #111827;
    cursor: pointer;
}

.sort-dropdown:hover,
.filter-dropdown:hover {
    border-color: #9ca3af;
}

/* Empty State */
.empty-state {
    padding: 60px 24px;
    text-align: center;
}

.empty-icon {
    font-size: 48px;
    margin-bottom: 16px;
}

.empty-message {
    font-size: 18px;
    font-weight: 600;
    color: #374151;
    margin: 0 0 8px 0;
}

.empty-submessage {
    font-size: 14px;
    color: #6b7280;
    margin: 0;
}

/* Table Styles */
.table-container {
    overflow-x: auto;
}

.subtasks-table {
    width: 100%;
    border-collapse: collapse;
}

.subtasks-table thead {
    background: #f9fafb;
    border-bottom: 2px solid #e5e7eb;
}

.subtasks-table th {
    padding: 12px 16px;
    text-align: left;
    font-size: 12px;
    font-weight: 600;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.subtasks-table tbody tr {
    border-bottom: 1px solid #f3f4f6;
    transition: background-color 0.2s;
}

.subtasks-table tbody tr:hover {
    background: #f9fafb;
}

.subtasks-table td {
    padding: 16px;
    font-size: 14px;
    color: #374151;
}

.subtask-name {
    font-weight: 500;
    color: #111827;
}

.owner-info {
    display: flex;
    align-items: center;
    gap: 8px;
}

.owner-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #e0e7ff;
    color: #3730a3;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 600;
}

/* Due Date Colors */
.overdue {
    color: #dc2626;
    font-weight: 600;
}

.urgent {
    color: #ea580c;
    font-weight: 600;
}

.warning {
    color: #ca8a04;
    font-weight: 500;
}

.normal {
    color: #059669;
}

/* Status Badge */
.status-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
}

.status-unassigned {
    background: #f3f4f6;
    color: #6b7280;
}

.status-ongoing {
    background: #dbeafe;
    color: #1e40af;
}

.status-review {
    background: #fef3c7;
    color: #92400e;
}

.status-completed {
    background: #d1fae5;
    color: #065f46;
}

/* Priority Badge */
.priority-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
}

.priority-high {
    background: #fecaca;
    color: #991b1b;
}

.priority-medium {
    background: #fed7aa;
    color: #9a3412;
}

.priority-low {
    background: #d1fae5;
    color: #065f46;
}

.priority-default {
    background: #f3f4f6;
    color: #6b7280;
}

/* View Button */
.view-btn {
    background: #3b82f6;
    color: white;
    border: none;
    padding: 6px 16px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 13px;
    font-weight: 500;
    transition: background-color 0.2s;
}

.view-btn:hover {
    background: #2563eb;
}

/* Subtask Count */
.subtask-count {
    padding: 16px 0 0 0;
    text-align: center;
    font-size: 14px;
    color: #6b7280;
}

/* Responsive */
@media (max-width: 768px) {
    .filter-sort-bar {
        flex-direction: column;
        align-items: flex-start;
    }

    .sort-dropdown,
    .filter-dropdown {
        width: 100%;
    }

    .table-container {
        overflow-x: scroll;
    }
}
</style>