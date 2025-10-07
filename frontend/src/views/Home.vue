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
                    <TasksByStatus />
                    <hr>
                    <TasksByPriority />
                    <hr>
                    <TaskTimeline />
                    <hr>
                    <TasksByStaff />
                </div>

                <!-- My Tasks View -->
                <div v-if="activeView === 'my'">
                    <p class="coming-soon">Teehee</p>
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
    },
    data() {
        return {
            currentUser: null,
            activeView: 'team',
        };
    },
    mounted() {
        console.log('Home.vue mounted - All components should load');

        if (AuthService.checkAuthStatus()) {
            this.currentUser = AuthService.getCurrentUser();
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
}
</style>