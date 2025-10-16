<template>
    <div class="deleted-items-page">
        <!-- Toast Notifications -->
        <div v-if="successMessage" class="toast-notification success-toast">
            <div class="toast-content">
                <svg class="toast-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M20 6L9 17l-5-5"></path>
                </svg>
                <span>{{ successMessage }}</span>
            </div>
            <button @click="successMessage = ''" class="toast-close">×</button>
        </div>

        <div v-if="errorMessage" class="toast-notification error-toast">
            <div class="toast-content">
                <svg class="toast-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="15" y1="9" x2="9" y2="15"></line>
                    <line x1="9" y1="9" x2="15" y2="15"></line>
                </svg>
                <span>{{ errorMessage }}</span>
            </div>
            <button @click="errorMessage = ''" class="toast-close">×</button>
        </div>

        <div v-if="infoMessage" class="toast-notification info-toast">
            <div class="toast-content">
                <svg class="toast-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <path d="M12 16v-4"></path>
                    <path d="M12 8h.01"></path>
                </svg>
                <span>{{ infoMessage }}</span>
            </div>
            <button @click="infoMessage = ''" class="toast-close">×</button>
        </div>

        <!-- Permanent Delete Confirmation Modal -->
        <div v-if="showConfirmModal" class="modal-overlay" @click="closeConfirmModal">
            <div class="modal-content permanent-delete-modal" @click.stop>
                <!-- Modal Header -->
                <div class="modal-header">
                    <h3 class="modal-title">{{ confirmModalData.title }}</h3>
                    <button @click="closeConfirmModal" class="close-btn">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"></line>
                            <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                    </button>
                </div>
                
                <!-- Modal Body -->
                <div class="modal-body">
                    <!-- Warning Icon -->
                    <div class="warning-icon-container">
                        <svg class="warning-icon" width="64" height="64" viewBox="0 0 24 24" fill="none">
                            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <circle cx="12" cy="12" r="2" fill="#ef4444"/>
                        </svg>
                    </div>
                    
                    <!-- Content -->
                    <div class="modal-content-text">
                        <p class="warning-message">{{ confirmModalData.message }}</p>
                        <div class="item-name-highlight">
                            "{{ confirmModalData.itemName }}"
                        </div>
                        <p class="warning-subtitle">
                            This action cannot be undone. The {{ confirmModalData.type }} will be permanently removed from the database.
                        </p>
                    </div>
                </div>
                
                <!-- Modal Footer -->
                <div class="modal-footer">
                    <button @click="closeConfirmModal" class="cancel-btn">
                        Cancel
                    </button>
                    <button @click="confirmPermanentDelete" class="permanent-delete-btn" :disabled="isDeleting">
                        <svg v-if="isDeleting" class="loading-text" width="16" height="16" viewBox="0 0 24 24" fill="none">
                            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" opacity="0.25"/>
                            <path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                        </svg>
                        <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="3,6 5,6 21,6"></polyline>
                            <path d="m19,6v14a2,2 0 0,1 -2,2H7a2,2 0 0,1 -2,-2V6m3,0V4a2,2 0 0,1 2,-2h4a2,2 0 0,1 2,2v2"></path>
                            <line x1="10" y1="11" x2="10" y2="17"></line>
                            <line x1="14" y1="11" x2="14" y2="17"></line>
                        </svg>
                        {{ isDeleting ? 'Deleting...' : 'Delete Forever' }}
                    </button>
                </div>
            </div>
        </div>

        <!-- Add the Navbar Component -->
        <Navbar />
        
        <div class="crm-container">
            <!-- Header Section -->
            <div class="header-section">
                <div class="container">
                    <div class="header-content">
                        <div class="title-section">
                            <h1 class="hero-title">🗑️ Deleted Items</h1>
                            <div class="division-badge" v-if="currentUser">
                                {{ currentUser.division_name }} Department
                            </div>
                        </div>
                    </div>

                    <div class="action-tabs">
                        <button 
                            class="tab-btn" 
                            :class="{ active: activeView === 'tasks' }" 
                            @click="switchTab('tasks')"
                        >
                            Deleted Tasks
                        </button>
                        <button 
                            class="tab-btn" 
                            :class="{ active: activeView === 'subtasks' }" 
                            @click="switchTab('subtasks')"
                        >
                            Deleted Subtasks
                        </button>
                    </div>
                </div>
            </div>

            <!-- Deleted Items Content -->
            <div class="dashboard-section">
                <div class="container">
                    <!-- Deleted Tasks View -->
                    <div v-if="activeView === 'tasks'">
                        <div class="filter-sort-bar">
                            <!-- Sort Mode Selector -->
                            <div class="sort-group">
                                <label>Sort By:</label>
                                <div class="sort-mode-toggle">
                                    <button
                                        :class="{ active: sortMode === 'deletedDate' }"
                                        @click="setSortMode('deletedDate')"
                                    >
                                        Deleted Date
                                    </button>
                                    <button
                                        :class="{ active: sortMode === 'name' }"
                                        @click="setSortMode('name')"
                                    >
                                        Name
                                    </button>
                                </div>
                            </div>

                            <!-- Ascending / Descending toggle -->
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

                        <!-- Tasks Section -->
                        <div class="tasks-section">
                            <div class="container">
                                <!-- Loading Text -->
                                <div v-if="loading" class="loading-section">
                                    <div class="container">
                                        <div class="loading-text">Loading Deleted Tasks...</div>
                                    </div>
                                </div>

                                <!-- Tasks Loaded -->
                                <div v-else>
                                    <!-- When there are deleted tasks -->
                                    <div v-if="sortedDeletedTasks.length">
                                        <div
                                            v-for="(task, index) in sortedDeletedTasks"
                                            :key="task.id || index"
                                            class="deleted-item-card"
                                        >
                                            <div class="deleted-item-content">
                                                <div class="item-info">
                                                    <h3 class="item-title">{{ task.task_name || task.name }}</h3>
                                                    <p class="item-description">{{ task.task_description || task.description || 'No description available' }}</p>
                                                    <div class="item-meta">
                                                        <span class="meta-item">
                                                            <strong>Deleted:</strong> {{ formatDate(task.deleted_at) }}
                                                        </span>
                                                        <span class="meta-item" v-if="task.project_name">
                                                            <strong>Project:</strong> {{ task.project_name }}
                                                        </span>
                                                        <span class="meta-item" v-if="task.priority_level">
                                                            <strong>Priority:</strong> {{ task.priority_level }}
                                                        </span>
                                                    </div>
                                                </div>
                                                <div class="item-actions">
                                                    <button @click="restoreTask(task)" class="restore-btn">
                                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                                            <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"></path>
                                                            <path d="M21 3v5h-5"></path>
                                                            <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"></path>
                                                            <path d="M3 21v-5h5"></path>
                                                        </svg>
                                                        Restore
                                                    </button>
                                                    <button @click="permanentlyDeleteTask(task)" class="delete-permanent-btn">
                                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                                            <polyline points="3,6 5,6 21,6"></polyline>
                                                            <path d="m19,6v14a2,2 0 0,1 -2,2H7a2,2 0 0,1 -2,-2V6m3,0V4a2,2 0 0,1 2,-2h4a2,2 0 0,1 2,2v2"></path>
                                                        </svg>
                                                        Delete Forever
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- When no deleted tasks found -->
                                    <div v-else class="nofound-section">
                                        <div class="mt-5">
                                            <div class="d-flex justify-content-center">
                                                <svg
                                                    xmlns="http://www.w3.org/2000/svg"
                                                    height="100"
                                                    width="100"
                                                    fill="currentColor"
                                                    class="bi bi-trash"
                                                    viewBox="0 0 16 16"
                                                >
                                                    <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0z"/>
                                                    <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4zM2.5 3h11V2h-11z"/>
                                                </svg>
                                            </div>
                                            <h2 class="text-center mt-2">No deleted tasks found.</h2>
                                            <p class="text-center">
                                                There are no deleted tasks to display.
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Deleted Subtasks View -->
                    <div v-if="activeView === 'subtasks'">
                        <div class="filter-sort-bar">
                            <!-- Sort Mode Selector -->
                            <div class="sort-group">
                                <label>Sort By:</label>
                                <div class="sort-mode-toggle">
                                    <button
                                        :class="{ active: sortMode === 'deletedDate' }"
                                        @click="setSortMode('deletedDate')"
                                    >
                                        Deleted Date
                                    </button>
                                    <button
                                        :class="{ active: sortMode === 'name' }"
                                        @click="setSortMode('name')"
                                    >
                                        Name
                                    </button>
                                </div>
                            </div>

                            <!-- Ascending / Descending toggle -->
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

                        <!-- Subtasks Section -->
                        <div class="tasks-section">
                            <div class="container">
                                <!-- Loading Text -->
                                <div v-if="loading" class="loading-section">
                                    <div class="container">
                                        <div class="loading-text">Loading Deleted Subtasks...</div>
                                    </div>
                                </div>

                                <!-- Subtasks Loaded -->
                                <div v-else>
                                    <!-- When there are deleted subtasks -->
                                    <div v-if="sortedDeletedSubtasks.length">
                                        <div
                                            v-for="(subtask, index) in sortedDeletedSubtasks"
                                            :key="subtask.id || index"
                                            class="deleted-item-card"
                                        >
                                            <div class="deleted-item-content">
                                                <div class="item-info">
                                                    <h3 class="item-title">{{ subtask.subtask_name || subtask.name }}</h3>
                                                    <p class="item-description">{{ subtask.subtask_description || subtask.description || 'No description available' }}</p>
                                                    <div class="item-meta">
                                                        <span class="meta-item">
                                                            <strong>Deleted:</strong> {{ formatDate(subtask.deleted_at) }}
                                                        </span>
                                                        <span class="meta-item" v-if="subtask.parent_task_name">
                                                            <strong>Parent Task:</strong> {{ subtask.parent_task_name }}
                                                        </span>
                                                    </div>
                                                </div>
                                                <div class="item-actions">
                                                    <button @click="restoreSubtask(subtask)" class="restore-btn">
                                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                                            <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"></path>
                                                            <path d="M21 3v5h-5"></path>
                                                            <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"></path>
                                                            <path d="M3 21v-5h5"></path>
                                                        </svg>
                                                        Restore
                                                    </button>
                                                    <button @click="permanentlyDeleteSubtask(subtask)" class="delete-permanent-btn">
                                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                                            <polyline points="3,6 5,6 21,6"></polyline>
                                                            <path d="m19,6v14a2,2 0 0,1 -2,2H7a2,2 0 0,1 -2,-2V6m3,0V4a2,2 0 0,1 2,-2h4a2,2 0 0,1 2,2v2"></path>
                                                        </svg>
                                                        Delete Forever
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- When no deleted subtasks found -->
                                    <div v-else class="nofound-section">
                                        <div class="mt-5">
                                            <div class="d-flex justify-content-center">
                                                <svg
                                                    xmlns="http://www.w3.org/2000/svg"
                                                    height="100"
                                                    width="100"
                                                    fill="currentColor"
                                                    class="bi bi-trash"
                                                    viewBox="0 0 16 16"
                                                >
                                                    <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0z"/>
                                                    <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4zM2.5 3h11V2h-11z"/>
                                                </svg>
                                            </div>
                                            <h2 class="text-center mt-2">No deleted subtasks found.</h2>
                                            <p class="text-center">
                                                There are no deleted subtasks to display.
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import Navbar from '@/components/NavBar.vue';
import AuthService from '@/services/auth.js';

export default {
    name: 'DeletedItems',
    components: {
        Navbar, 
    },
    data() {
        return {
            currentUser: null,
            activeView: 'tasks',
            deletedTasks: [],
            deletedSubtasks: [],
            loading: true,
            error: null,
            sortMode: "deletedDate",    
            sortOrder: "desc",
            successMessage: '',
            errorMessage: '',
            infoMessage: '',
            showConfirmModal: false,
            confirmModalData: {
                title: '',
                message: '',
                itemName: '',
                type: '', // 'task' or 'subtask'
                action: '', // 'permanent_delete'
                item: null
            },
            isDeleting: false,
        };
    },
    mounted() {
        console.log('DeletedItems.vue mounted');
        
        if (AuthService.checkAuthStatus()) {
            this.currentUser = AuthService.getCurrentUser();
        }
        
        const view = this.$route.query.view;
        if (view === 'tasks' || view === 'subtasks') {
            this.activeView = view;
        }
    },
    created() {
        this.loadDeletedData();
    },
    watch: {
        $route(to) {
            const view = to.query.view;
            if (view === 'tasks' || view === 'subtasks') {
                this.activeView = view;
            }
            this.loadDeletedData();
        }
    },
    methods: {
        switchTab(view) {
            this.activeView = view;
            this.$router.replace({ query: { view } });
        },
        // Replace your current loadDeletedData method with this:
        async loadDeletedData() {
            try {
                this.loading = true;
                this.error = null;

                // Get current user ID
                const userString = sessionStorage.getItem('user');
                if (!userString) {
                    throw new Error('User not logged in');
                }
                
                const userData = JSON.parse(userString);
                const currentUserId = userData.id;

                console.log('Loading deleted data for user:', currentUserId);

                // Import taskService
                const { taskService } = await import('@/services/taskService.js');

                // Add this right before calling getDeletedSubtasks
                console.log('🔍 About to call API with user ID:', currentUserId);
                console.log('🔍 Expected user IDs from DB:');

                // Load deleted tasks and subtasks in parallel
                const [deletedTasks, deletedSubtasks] = await Promise.all([
                    taskService.getDeletedTasks(currentUserId),
                    taskService.getDeletedSubtasks(currentUserId)
                ]);

                this.deletedTasks = deletedTasks || [];
                this.deletedSubtasks = deletedSubtasks || [];
                console.log('🔍 API returned:', deletedSubtasks);

                console.log(`Loaded ${this.deletedTasks.length} deleted tasks and ${this.deletedSubtasks.length} deleted subtasks`);

            } catch (error) {
                console.error("Error loading deleted items:", error);
                this.error = error.message;
                // Set empty arrays on error
                this.deletedTasks = [];
                this.deletedSubtasks = [];
            } finally {
                this.loading = false;
            }
        },

        formatDate(date) {
            if (!date) return "No date set";
            return new Date(date).toLocaleDateString("en-US", {
                weekday: "long",
                day: "2-digit",
                month: "long",
                year: "numeric"
            });
        },
        setSortOrder(order) {
            this.sortOrder = order;
        },
        setSortMode(mode) {
            this.sortMode = mode;
        },
        async restoreTask(task) {
            try {
                console.log('Restoring task:', task);
                
                // Show loading info
                this.infoMessage = 'Restoring task...';
                
                const { taskService } = await import('@/services/taskService.js');
                await taskService.restoreTask(task.id);
                
                // Remove from deleted tasks list
                this.deletedTasks = this.deletedTasks.filter(t => t.id !== task.id);
                
                // Clear loading message and show success
                this.infoMessage = '';
                this.successMessage = `✅ Task "${task.task_name || task.name}" has been restored successfully!`;
                
                // Auto-hide success message after 4 seconds
                setTimeout(() => {
                    this.successMessage = '';
                }, 4000);
                
            } catch (error) {
                console.error('Error restoring task:', error);
                
                // Clear loading message and show error
                this.infoMessage = '';
                this.errorMessage = `❌ Failed to restore task: ${error.message}`;
                
                // Auto-hide error message after 6 seconds
                setTimeout(() => {
                    this.errorMessage = '';
                }, 6000);
            }
        },

        // Update your restore and permanent delete methods to handle subtasks:
        async restoreSubtask(subtask) {
            try {
                console.log('Restoring subtask:', subtask);
                const { taskService } = await import('@/services/taskService.js');
                await taskService.restoreSubtask(subtask.id);
                
                // Remove from deleted subtasks list
                this.deletedSubtasks = this.deletedSubtasks.filter(s => s.id !== subtask.id);
                
                // Show success message
                this.successMessage = `✅ Subtask "${subtask.name}" has been restored successfully!`;
                setTimeout(() => {
                    this.successMessage = '';
                }, 4000);
            } catch (error) {
                console.error('Error restoring subtask:', error);
                this.errorMessage = `❌ Failed to restore subtask: ${error.message}`;
                setTimeout(() => {
                    this.errorMessage = '';
                }, 6000);
            }
        },

        async permanentlyDeleteSubtask(subtask) {
            if (confirm('Are you sure you want to permanently delete this subtask? This action cannot be undone.')) {
                try {
                    console.log('Permanently deleting subtask:', subtask);
                    const { taskService } = await import('@/services/taskService.js');
                    await taskService.permanentlyDeleteSubtask(subtask.id);
                    
                    // Remove from deleted subtasks list
                    this.deletedSubtasks = this.deletedSubtasks.filter(s => s.id !== subtask.id);
                    
                    this.successMessage = `🗑️ Subtask "${subtask.name}" has been permanently deleted.`;
                    setTimeout(() => {
                        this.successMessage = '';
                    }, 4000);
                } catch (error) {
                    console.error('Error permanently deleting subtask:', error);
                    this.errorMessage = `❌ Failed to permanently delete subtask: ${error.message}`;
                    setTimeout(() => {
                        this.errorMessage = '';
                    }, 6000);
                }
            }
        },

        // This method shows the confirmation modal
        permanentlyDeleteTask(task) {
            this.confirmModalData = {
                title: 'Permanently Delete Task',
                message: 'Are you sure you want to permanently delete this task?',
                itemName: task.task_name || task.taskname || 'Unknown Task',
                type: 'task',
                action: 'permanent_delete',
                item: task
            };
            this.showConfirmModal = true;
        },

        // This method closes the modal
        closeConfirmModal() {
            this.showConfirmModal = false;
            this.confirmModalData = {
                title: '',
                message: '',
                itemName: '',
                type: '',
                action: '',
                item: null
            };
            this.isDeleting = false;
        },

        // This method executes the actual deletion
        async confirmPermanentDelete() {
            if (!this.confirmModalData.item) return;

            try {
                this.isDeleting = true;
                
                const { taskService } = await import('@/services/taskService.js');
                
                if (this.confirmModalData.type === 'task') {
                    await taskService.permanentlyDeleteTask(this.confirmModalData.item.id);
                    
                    // Remove from deleted tasks list
                    this.deletedTasks = this.deletedTasks.filter(t => t.id !== this.confirmModalData.item.id);
                    
                    // Show success toast
                    this.successMessage = `🗑️ Task "${this.confirmModalData.itemName}" has been permanently deleted.`;
                    
                } else if (this.confirmModalData.type === 'subtask') {
                    await taskService.permanentlyDeleteSubtask(this.confirmModalData.item.id);
                    
                    // Remove from deleted subtasks list
                    this.deletedSubtasks = this.deletedSubtasks.filter(s => s.id !== this.confirmModalData.item.id);
                    
                    // Show success toast
                    this.successMessage = `🗑️ Subtask "${this.confirmModalData.itemName}" has been permanently deleted.`;
                }
                
                // Close modal
                this.closeConfirmModal();
                
                // Auto-hide success message
                setTimeout(() => {
                    this.successMessage = '';
                }, 4000);
                
            } catch (error) {
                console.error('Error permanently deleting item:', error);
                
                // Show error toast
                this.errorMessage = `❌ Failed to permanently delete ${this.confirmModalData.type}: ${error.message}`;
                
                // Auto-hide error message
                setTimeout(() => {
                    this.errorMessage = '';
                }, 6000);
                
                this.isDeleting = false;
            }
        },

    },
    computed: {
        sortedDeletedTasks() {
            let result = [...this.deletedTasks];
            
            if (this.sortMode === "deletedDate") {
                result.sort((a, b) => {
                    const dateA = new Date(a.deleted_at);
                    const dateB = new Date(b.deleted_at);
                    return this.sortOrder === "asc" ? dateA - dateB : dateB - dateA;
                });
            } else if (this.sortMode === "name") {
                result.sort((a, b) => {
                    const nameA = (a.task_name || a.name || '').toLowerCase();
                    const nameB = (b.task_name || b.name || '').toLowerCase();
                    return this.sortOrder === "asc" 
                        ? nameA.localeCompare(nameB)
                        : nameB.localeCompare(nameA);
                });
            }

            return result;
        },
        sortedDeletedSubtasks() {
            let result = [...this.deletedSubtasks];
            
            if (this.sortMode === "deletedDate") {
                result.sort((a, b) => {
                    const dateA = new Date(a.deleted_at);
                    const dateB = new Date(b.deleted_at);
                    return this.sortOrder === "asc" ? dateA - dateB : dateB - dateA;
                });
            } else if (this.sortMode === "name") {
                result.sort((a, b) => {
                    const nameA = (a.subtask_name || a.name || '').toLowerCase();
                    const nameB = (b.subtask_name || b.name || '').toLowerCase();
                    return this.sortOrder === "asc" 
                        ? nameA.localeCompare(nameB)
                        : nameB.localeCompare(nameA);
                });
            }

            return result;
        }
    }
}
</script>

<style scoped>
.deleted-items-page {
    min-height: 100vh;
}

.crm-container {
    min-height: calc(100vh - 60px);
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

.tab-btn:hover {
    background: #f9fafb;
}

.tab-btn.active:hover {
    background: #374151;
}

.dashboard-section {
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

.sort-group label {
    font-weight: 500;
    color: #4b5563;
    margin-right: 0.5rem;
    font-size: 0.9rem;
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

.loading-section {
    text-align: center;
    padding: 2rem;
}

.loading-text {
    font-size: 1.125rem;
    color: #6b7280;
}

.deleted-item-card {
    background: #fff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    transition: all 0.2s ease;
}

.deleted-item-card:hover {
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.deleted-item-content {
    padding: 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
}

.item-info {
    flex: 1;
}

.item-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: #111827;
    margin: 0 0 0.5rem 0;
}

.item-description {
    color: #6b7280;
    margin: 0 0 1rem 0;
    line-height: 1.5;
}

.item-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    font-size: 0.875rem;
}

.meta-item {
    color: #6b7280;
}

.meta-item strong {
    color: #374151;
}

.item-actions {
    display: flex;
    gap: 0.5rem;
    flex-shrink: 0;
}

.restore-btn,
.delete-permanent-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    border: 1px solid;
    border-radius: 6px;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
}

.restore-btn {
    background: #fff;
    color: #059669;
    border-color: #059669;
}

.restore-btn:hover {
    background: #059669;
    color: #fff;
}

.delete-permanent-btn {
    background: #fff;
    color: #dc2626;
    border-color: #dc2626;
}

.delete-permanent-btn:hover {
    background: #dc2626;
    color: #fff;
}

.nofound-section {
    text-align: center;
    padding: 4rem 2rem;
    background: white;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
    color: #6b7280;
}

.nofound-section svg {
    color: #9ca3af;
}

.nofound-section h2 {
    color: #374151;
    margin: 1rem 0 0.5rem 0;
}

.mt-5 {
    margin-top: 3rem;
}

.mt-2 {
    margin-top: 0.5rem;
}

.d-flex {
    display: flex;
}

.justify-content-center {
    justify-content: center;
}

.text-center {
    text-align: center;
}

@media (max-width: 768px) {
    .header-content {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
    }

    .action-tabs {
        flex-direction: column;
        width: 100%;
    }

    .tab-btn {
        width: 100%;
    }

    .deleted-item-content {
        flex-direction: column;
        align-items: stretch;
    }

    .item-actions {
        justify-content: flex-start;
        flex-wrap: wrap;
    }

    .filter-sort-bar {
        flex-direction: column;
        align-items: stretch;
    }

    .sort-group {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
}

/* Toast Notification Styles */
.toast-notification {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 10000;
    max-width: 400px;
    min-width: 300px;
    padding: 16px;
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
    backdrop-filter: blur(8px);
    display: flex;
    align-items: center;
    justify-content: space-between;
    animation: toastSlideIn 0.3s ease-out;
}

@keyframes toastSlideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

.success-toast {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.error-toast {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.info-toast {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.toast-content {
    display: flex;
    align-items: center;
    gap: 12px;
    flex: 1;
}

.toast-icon {
    flex-shrink: 0;
    filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1));
}

.toast-close {
    background: none;
    border: none;
    color: white;
    font-size: 20px;
    font-weight: bold;
    cursor: pointer;
    padding: 4px 8px;
    border-radius: 4px;
    transition: background-color 0.2s ease;
    margin-left: 12px;
}

.toast-close:hover {
    background: rgba(255, 255, 255, 0.2);
}

/* Responsive Toast */
@media (max-width: 640px) {
    .toast-notification {
        top: 10px;
        right: 10px;
        left: 10px;
        max-width: none;
        min-width: auto;
    }
}

/* Permanent Delete Modal Styles */
.permanent-delete-modal {
    max-width: 500px;
    border-radius: 16px;
}

.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(4px);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 10000;
    padding: 20px;
    animation: overlayFadeIn 0.3s ease-out;
}

.modal-content {
    background: white;
    border-radius: 12px;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    max-width: 90%;
    max-height: 90vh;
    overflow: hidden;
    animation: modalSlideIn 0.3s ease-out;
}

@keyframes overlayFadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes modalSlideIn {
    from {
        opacity: 0;
        transform: scale(0.95) translateY(-10px);
    }
    to {
        opacity: 1;
        transform: scale(1) translateY(0);
    }
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 24px 24px 0 24px;
    margin-bottom: 8px;
}

.modal-title {
    font-size: 20px;
    font-weight: 600;
    color: #111827;
    margin: 0;
}

.close-btn {
    background: none;
    border: none;
    padding: 8px;
    cursor: pointer;
    border-radius: 8px;
    color: #6b7280;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
}

.close-btn:hover {
    background: #f3f4f6;
    color: #374151;
}

.modal-body {
    padding: 16px 24px 24px 24px;
    text-align: center;
}

.warning-icon-container {
    margin-bottom: 24px;
    display: flex;
    justify-content: center;
}

.warning-icon {
    filter: drop-shadow(0 4px 6px rgba(239, 68, 68, 0.2));
}

.modal-content-text {
    margin-bottom: 8px;
}

.warning-message {
    font-size: 16px;
    color: #111827;
    margin: 0 0 16px 0;
    font-weight: 500;
    line-height: 1.5;
}

.item-name-highlight {
    background: #fee2e2;
    color: #dc2626;
    padding: 8px 16px;
    border-radius: 8px;
    font-weight: 600;
    margin: 16px 0;
    border: 1px solid #fecaca;
}

.warning-subtitle {
    font-size: 14px;
    color: #6b7280;
    margin: 16px 0 0 0;
    line-height: 1.5;
}

.modal-footer {
    background: #f9fafb;
    padding: 24px;
    display: flex;
    gap: 12px;
    justify-content: flex-end;
    border-top: 1px solid #e5e7eb;
}

.cancel-btn {
    background: white;
    color: #374151;
    border: 1px solid #d1d5db;
    padding: 12px 20px;
    border-radius: 8px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 14px;
    min-width: 80px;
}

.cancel-btn:hover {
    background: #f9fafb;
    border-color: #9ca3af;
}

.permanent-delete-btn {
    background: #dc2626;
    color: white;
    border: none;
    padding: 12px 20px;
    border-radius: 8px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 140px;
    justify-content: center;
}

.permanent-delete-btn:hover:not(:disabled) {
    background: #b91c1c;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
}

.permanent-delete-btn:disabled {
    background: #9ca3af;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

/* Responsive Design */
@media (max-width: 640px) {
    .permanent-delete-modal {
        max-width: 95%;
        margin: 20px;
    }
    
    .modal-footer {
        flex-direction: column;
        gap: 8px;
    }
    
    .cancel-btn,
    .permanent-delete-btn {
        width: 100%;
        justify-content: center;
    }
}

</style>
