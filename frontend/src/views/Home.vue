<template>
    <div class="crm-container">
        <!-- Header Section -->
        <div class="header-section">
            <div class="container">
                <div class="header-content">
                    <div class="title-section">
                        <h1 class="hero-title">📊 Dashboard</h1>
                        <div class="division-badge" v-if="currentUser">
                            {{ currentUser.division_name }} Department
                        </div>
                    </div>
                </div>

                <div class="action-tabs">
                    <!-- Only show Team Tasks for managers (role_num < 4) -->
                    <button v-if="isManager" class="tab-btn" :class="{ active: activeView === 'team' }"
                        @click="switchTab('team')">
                        Team Tasks
                    </button>
                    <!-- Show My Dashboard for staff -->
                    <button v-if="!isManager" class="tab-btn" :class="{ active: activeView === 'mydashboard' }"
                        @click="switchTab('mydashboard')">
                        My Dashboard
                    </button>
                    <button class="tab-btn" :class="{ active: activeView === 'my' }" @click="switchTab('my')">
                        My Tasks
                    </button>
                </div>
            </div>
        </div>

        <!-- Dashboard Content -->
        <div class="dashboard-section">
            <div class="container">
                <!-- Team Tasks View -->
                <div v-if="activeView === 'team'">
                    <TotalTaskCount />
                    <hr>
                    <div class="charts-grid">
                        <TasksByStatus />
                        <TasksByPriority />
                    </div>
                    <hr>
                    <TaskTimeline />
                    <hr>
                    <!-- Only show TasksByStaff for managers -->
                    <TasksByStaff v-if="isManager" />
                    <hr>
                    <!-- Only show Team's Subtasks for manangers -->
                    <TeamSubtasks v-if="isManager" />
                    <hr>
                    <ManagerViewTeamTaskSchedule v-if="currentUserId" :userid="currentUserId" />
                </div>

                <!-- My Dashboard View (for staff) -->
                <div v-if="activeView === 'mydashboard'">
                    <TotalTaskCount />
                    <hr>
                    <div class="charts-grid">
                        <TasksByStatus />
                        <TasksByPriority />
                    </div>
                    <hr>
                    <TaskTimeline />
                </div>

                <!-- My Tasks View -->
                <div v-if="activeView === 'my'">
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
                                <button :class="{ active: sortMode === 'dueDate' }" @click="setSortMode('dueDate')">
                                    Due Date
                                </button>
                                <button :class="{ active: sortMode === 'priority' }" @click="setSortMode('priority')">
                                    Priority
                                </button>
                            </div>
                        </div>

                        <!-- ✅ Ascending / Descending toggle -->
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
                    <!-- Tasks -->
                    <div class="tasks-section">
                        <div class="container">
                            <!-- ✅ Loading Spinner -->
                            <div v-if="loading" class="loading-section">
                                <div class="container">
                                    <div class="loading-spinner">Loading Tasks...</div>
                                </div>
                            </div>

                            <!-- ✅ Tasks Loaded -->
                            <div v-else>
                                <!-- ✅ When there are tasks after filtering/sorting -->
                                <div v-if="filteredAndSortedTasks.length">
                                    <div v-for="(task, index) in filteredAndSortedTasks" :key="task.id || index"
                                        class="task-card">
                                        <!-- ✅ Uses your TaskCard component -->
                                        <task-card :task="task" :users="users" class="mb-0"
                                            @view-task="handleViewTask" />
                                    </div>
                                </div>

                                <!-- ✅ When no tasks match filter -->
                                <div v-else class="nofound-section">
                                    <div class="mt-5">
                                        <div class="card">
                                            <div class="no-tasks-message">
                                                <div class="no-tasks-icon">📋</div>
                                                <div class="no-tasks-text">No tasks of this status found.</div>
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
    </div>
</template>

<script>
import TotalTaskCount from '@/components/Dashboard/TotalTaskCount.vue';
import TasksByStatus from '@/components/Dashboard/TasksByStatus.vue';
import TasksByStaff from '@/components/Dashboard/TasksByStaff.vue';
import TasksByPriority from '@/components/Dashboard/TasksByPriority.vue';
import TaskTimeline from '@/components/Dashboard/TaskTimeline.vue';
import ManagerViewTeamTaskSchedule from '@/components/Dashboard/ManagerViewTeamTaskSchedule.vue';
// import TaskCalendar from '@/views/TaskCalendar.vue';
import AuthService from '@/services/auth.js';
import TaskCard from '@/components/Projects/TaskCard.vue';
import { ownTasksService } from '../services/myTaskService.js';
import notificationService from '@/services/notificationService';
import { userAPI } from '../services/api.js'
import TeamSubtasks from '@/components/Dashboard/TeamSubtasks.vue';
// import PendingTasksByAge from '@/components/Dashboard/PendingTasksByAge.vue';

export default {
    name: 'Home',
    components: {
        TotalTaskCount,
        TasksByStatus,
        TasksByStaff,
        TasksByPriority,
        // PendingTasksByAge,
        TaskTimeline,
        TaskCard,
        ManagerViewTeamTaskSchedule,
        TeamSubtasks
    },
    data() {
        return {
            currentUser: null,
            activeView: this.getDefaultView(),
            tasks: [],
            users: [],
            loading: true,
            error: null,
            selectedStatus: "active",
            sortMode: "dueDate",
            sortOrder: "asc",
        };
    },
    mounted() {
        console.log('Home.vue mounted - All components should load');

        // Check for upcoming deadlines when dashboard loads
        notificationService.checkUpcomingDeadlines();

        if (AuthService.checkAuthStatus()) {
            this.currentUser = AuthService.getCurrentUser();

            // ✅ ADD THESE LINES to get and store the user ID
            const userString = sessionStorage.getItem('user');
            if (userString) {
                const userData = JSON.parse(userString);
                this.currentUserId = userData.id;
                console.log('Current User ID set:', this.currentUserId);
            }
        }

        // Set active view from query parameter if present
        const view = this.$route.query.view;
        if (view === 'team' || view === 'my' || view === 'mydashboard') {
            this.activeView = view;
        }
    },
    created() {
        this.loadTaskData();
        this.fetchUsers();
    },
    watch: {
        $route(to) {
            // Set active view from query parameter
            const view = to.query.view;
            if (view === 'team' || view === 'my' || view === 'mydashboard') {
                this.activeView = view;
            }
            this.loadTaskData();
        }
    },
    methods: {
        getDefaultView() {
            // Get current user to determine default view
            const user = AuthService.getCurrentUser();

            // Staff (role_num = 4) start on My Dashboard
            // Managers/Directors start on Team Tasks
            if (user && user.role_num === 4) {
                return 'mydashboard';
            } else {
                return 'team';
            }
        },
        switchTab(view) {
            this.activeView = view;
            // Update URL query parameter
            this.$router.replace({ query: { view } });
        },
        async loadTaskData() {
            try {
                this.loading = true;
                this.error = null;

                const userString = sessionStorage.getItem('user');
                const userData = JSON.parse(userString);
                const currentUserId = userData.id;
                // console.log("user = ", userData);
                // console.log("id = ", currentUserId);

                // Fetch tasks for this user
                this.tasks = await ownTasksService.getTasks(currentUserId);
                // console.log("pulled tasks", this.tasks);
                if (!this.tasks.length) {
                    this.error = `No tasks found for user ${currentUserId}`;
                }
            } catch (error) {
                // console.error("Error loading tasks:", error);
                this.error = error.message;
            } finally {
                this.loading = false;
            }
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

        goBack() {
            this.$router.push("/projects");
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

        formatDateRange(startDate, endDate) {
            if (!startDate || !endDate) return "No dates set";
            const start = new Date(startDate).toLocaleDateString("en-US", {
                day: "2-digit",
                month: "short"
            });
            const end = new Date(endDate).toLocaleDateString("en-US", {
                day: "2-digit",
                month: "short",
                year: "numeric"
            });
            return `${start} - ${end}`;
        },
        handleViewTask(task) {
            const projectId = task.proj_ID || task.projectId;
            const taskId = task.id || task.task_ID || task.taskId;
            // console.log('Viewing task:', { projectId, taskId, task });

            // If task has a project, go to project task view
            if (projectId) {
                this.$router.push(`/projects/${projectId}/tasks/${taskId}`);
            } else {
                // If task has no project, go to standalone task view
                this.$router.push(`/tasks/${taskId}`);
            }
        },
        toggleSortOrder() {
            this.sortOrder = this.sortOrder === "asc" ? "desc" : "asc";
        },
        applyFilters() {
            // Trigger computed update
        },
        setSortOrder(order) {
            this.sortOrder = order;
        },
        setSortMode(mode) {
            this.sortMode = mode;
        },
    },
    computed: {
        isManager() {
            try {
                const userStr = sessionStorage.getItem('user');
                if (userStr) {
                    const user = JSON.parse(userStr);
                    let roleNum = user.role_num;
                    
                    console.log('isManager check - role_num:', roleNum, 'type:', typeof roleNum);

                    if (typeof roleNum === 'string') {
                        roleNum = parseInt(roleNum);
                    }

                    if (!roleNum && user.role_name) {
                        const roleName = user.role_name.toLowerCase();
                        if (roleName === 'manager') roleNum = 3;
                        else if (roleName === 'director') roleNum = 2;
                    }

                    const result = roleNum && roleNum < 4;
                    console.log('isManager result:', result, 'for role_num:', roleNum);
                    return result;
                }
            } catch (e) {
                console.error('Error checking manager role:', e);
            }
            return false;
        },
        isStaff() {
            try {
                const userStr = sessionStorage.getItem('user');
                if (userStr) {
                    const user = JSON.parse(userStr);
                    let roleNum = user.role_num;

                    if (typeof roleNum === 'string') {
                        roleNum = parseInt(roleNum);
                    }

                    if (!roleNum && user.role_name) {
                        const roleName = user.role_name.toLowerCase();
                        if (roleName === 'staff') roleNum = 4;
                    }

                    return roleNum === 4;
                }
            } catch (e) {
                console.error('Error checking staff role:', e);
            }
            return false;
        },
        filteredAndSortedTasks() {
        let result = [...this.tasks];
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
        // console.log("RESULTTT", result);
        return result;
        },
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

.dashboard-section {
    padding: 2rem 0;
}

hr {
    border: none;
    height: 1px;
    background: #e5e7eb;
    margin: 2rem 0;
}

.coming-soon {
    text-align: center;
    padding: 4rem 2rem;
    background: white;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
    color: #6b7280;
    font-size: 1.125rem;
}

/* ADD THIS NEW CSS */
.charts-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 2rem;
    margin: 0;
}

@media (max-width: 768px) {
    .header-section {
        padding: 1rem 0;
    }

    .header-content {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
        margin-bottom: 1rem;
    }

    .hero-title {
        font-size: 1.75rem;
    }

    .division-badge {
        font-size: 0.75rem;
        padding: 0.2rem 0.6rem;
    }

    .action-tabs {
        flex-wrap: wrap;
        gap: 0.5rem;
        width: 100%;
    }

    .tab-btn {
        flex: 1;
        min-width: calc(50% - 0.25rem);
        padding: 0.5rem 0.75rem;
        font-size: 0.875rem;
    }

    .dashboard-section {
        padding: 1rem 0;
    }

    .charts-grid {
        grid-template-columns: 1fr;
        gap: 1rem;
    }

    .charts-grid :deep(.card) {
        max-width: 100%;
        margin: 0;
        padding: 1.5rem;
    }

    .filter-sort-bar {
        flex-direction: column;
        align-items: stretch;
        gap: 0.75rem;
        padding: 0.75rem;
    }

    .filter-group,
    .sort-group {
        width: 100%;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .filter-group label,
    .sort-group label {
        margin-right: 0;
        margin-bottom: 0.25rem;
    }

    select {
        width: 100%;
    }

    .sort-toggle,
    .sort-mode-toggle {
        width: 100%;
        justify-content: stretch;
    }

    .sort-toggle button,
    .sort-mode-toggle button {
        flex: 1;
    }

    hr {
        margin: 1.5rem 0;
    }

    .container {
        padding: 0 0.75rem;
    }
}

@media (max-width: 480px) {
    .hero-title {
        font-size: 1.5rem;
    }

    .tab-btn {
        min-width: 100%;
        font-size: 0.8125rem;
    }

    .card {
        padding: 1.25rem;
    }

    .task-card {
        padding: 1rem;
    }
}

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
</style>