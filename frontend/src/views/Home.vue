<template>
    <div class="crm-container">
        <!-- Header Section -->
        <div class="header-section">
            <div class="container">
                <div class="header-content">
                    <div class="title-section">
                        <h1 class="hero-title">Dashboard</h1>
                        <div class="division-badge" v-if="currentUser">
                            {{ currentUser.division_name }} Department
                        </div>
                    </div>
                </div>

                <div class="action-tabs">
                    <button class="tab-btn" :class="{ active: activeView === 'team' }" @click="activeView = 'team'">
                        Team Tasks
                    </button>
                    <button class="tab-btn" :class="{ active: activeView === 'my' }" @click="activeView = 'my'">
                        My Tasks
                    </button>
                    <button class="tab-btn" :class="{ active: activeView === 'calendar' }"
                        @click="activeView = 'calendar'">
                        Calendar
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
                    <TasksByStaff />
                </div>

                <!-- My Tasks View -->
                <div v-if="activeView === 'my'">
                    <!-- <p class="coming-soon">Teehee</p> -->
                    <div class="crm-container">
                        <div class="header-section">
                            <div class="container">
                                <!-- Status Filter Tabs -->
                                <div class="action-tabs mb-4">
                                    <button v-for="status in statuses" :key="status" @click="filter = status"
                                        :class="['tab-btn', { active: filter === status }]">
                                        {{ status }}
                                    </button>
                                </div>
                                <!-- Sort Filter Tabs -->
                                <div class="action-tabs flex space-x-2">
                                    <button v-for="option in sortOptions" :key="option.value"
                                        @click="sortBy = option.value" :class="[
                                            'tab-btn',
                                            { active: sortBy === option.value }]">
                                        {{ option.label }}
                                    </button>
                                </div>
                            </div>
                        </div>
                        <!-- Tasks -->
                        <div class="tasks-section">
                            <div class="container">
                                <div v-if="loading" class="loading-section">
                                    <div class="container">
                                        <div class="loading-spinner">Loading Tasks...</div>
                                    </div>
                                </div>
                                <div v-else>
                                    <div v-if="filteredTasks.length">
                                        <div v-for="(task, index) in this.filteredTasks" :key="index" class="task-card">
                                            <task-card :task="task" class="mb-0" @view-task="handleViewTask" />
                                        </div>
                                    </div>
                                    <div v-else class="nofound-section">
                                        <div class="mt-5">
                                            <div class="d-flex justify-content-center">
                                                <svg xmlns="http://www.w3.org/2000/svg" height="100" width="100"
                                                    fill="currentColor" class="bi bi-clipboard-x" viewBox="0 0 16 16">
                                                    <path fill-rule="evenodd"
                                                        d="M6.146 7.146a.5.5 0 0 1 .708 0L8 8.293l1.146-1.147a.5.5 0 1 1 .708.708L8.707 9l1.147 1.146a.5.5 0 0 1-.708.708L8 9.707l-1.146 1.147a.5.5 0 0 1-.708-.708L7.293 9 6.146 7.854a.5.5 0 0 1 0-.708" />
                                                    <path
                                                        d="M4 1.5H3a2 2 0 0 0-2 2V14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V3.5a2 2 0 0 0-2-2h-1v1h1a1 1 0 0 1 1 1V14a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V3.5a1 1 0 0 1 1-1h1z" />
                                                    <path
                                                        d="M9.5 1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-3a.5.5 0 0 1-.5-.5v-1a.5.5 0 0 1 .5-.5zm-3-1A1.5 1.5 0 0 0 5 1.5v1A1.5 1.5 0 0 0 6.5 4h3A1.5 1.5 0 0 0 11 2.5v-1A1.5 1.5 0 0 0 9.5 0z" />
                                                </svg>
                                            </div>
                                            <h2 class="text-center mt-2">
                                                No tasks found.
                                            </h2>
                                            <p class="text-center">
                                                There are no tasks found associated with this status.
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Calendar View -->
                <div v-if="activeView === 'calendar'">
                    <TaskCalendar />
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
import TaskCalendar from '@/components/Dashboard/TaskCalendar.vue';
import AuthService from '@/services/auth.js';
import TaskCard from '@/components/Projects/TaskCard.vue';
import { ownTasksService } from '../services/myTaskService.js'
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
        TaskCalendar,
        TaskCard
    },
    data() {
        return {
            currentUser: null,
            activeView: 'team',
            tasks: [],
            users: [],
            loading: true,
            error: null,
            filter: "All",
            statuses: ["All", "Unassigned", "Ongoing", "Under Review", "Completed", "Cancelled"],
            sortBy: "endDateAsc",
            sortOptions: [
                { value: "endDateAsc", label: "Earliest" },
                { value: "endDateDesc", label: "Latest" },
                { value: "priority", label: "Priority" }
            ]
        };
    },
    mounted() {
        console.log('Home.vue mounted - All components should load');

        if (AuthService.checkAuthStatus()) {
            this.currentUser = AuthService.getCurrentUser();
        }
    },
    created() {
        this.loadTaskData();
    },
    watch: {
        $route() {
            this.loadTaskData();
        }
    },
    methods: {
        async loadTaskData() {
            try {
                this.loading = true;
                this.error = null;

                // Replace with however you store logged-in user
                const userString = sessionStorage.getItem('user');
                const userData = JSON.parse(userString);
                const currentUserId = userData.id;
                console.log("user = ", userData);
                console.log("id = ", currentUserId);

                // Fetch tasks for this user
                this.tasks = await ownTasksService.getTasks(currentUserId);
                console.log("pulled tasks", this.tasks);
                if (!this.tasks.length) {
                    this.error = `No tasks found for user ${currentUserId}`;
                }
            } catch (error) {
                console.error("Error loading tasks:", error);
                this.error = error.message;
            } finally {
                this.loading = false;
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
            console.log('Viewing task:', { projectId, taskId, task });

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
        }
    },
    computed: {
        filteredTasks() {
            let result = this.tasks;

            // Filter by status
            if (this.filter !== "All") {
                result = result.filter(t => t.task_status === this.filter);
            }

            // Sort by end date
            result = result.slice().sort((a, b) => {
                if (this.sortBy === "priority") {
                    return (b.priority_bucket || 0) - (a.priority_bucket || 0); // high → low
                }
                if (this.sortBy === "endDateAsc") {
                    return new Date(a.end_date) - new Date(b.end_date);
                }
                if (this.sortBy === "endDateDesc") {
                    return new Date(b.end_date) - new Date(a.end_date);
                }
                return 0;
            });

            return result;
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

.tab-btn:hover {
    background: #f9fafb;
}

.tab-btn.active:hover {
    background: #374151;
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

    .charts-grid {
        grid-template-columns: 1fr;
    }

    .charts-grid :deep(.card) {
        max-width: 100%;
        margin: 0;
    }
}
</style>