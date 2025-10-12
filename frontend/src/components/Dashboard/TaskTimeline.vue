<template>
    <div>
        <h3 class="section-title">Task Timeline</h3>
        <div v-if="loading" class="loading">Loading...</div>
        <div v-else-if="error" class="error">Error: {{ error }}</div>
        <div v-else class="timeline-container">
            <!-- Overdue -->
            <div class="timeline-card overdue" @click="toggleCategory('overdue')">
                <div class="card-header">
                    <h4 class="category-title">OVERDUE ({{ getCategoryCount('overdue') }})</h4>
                    <span class="expand-icon">{{ expandedCategories['overdue'] ? '▼' : '▶' }}</span>
                </div>
                <div v-if="expandedCategories['overdue'] && data.pending_tasks_by_age.overdue.length === 0"
                    class="empty-state">
                    No overdue tasks 🎉
                </div>
                <div v-if="expandedCategories['overdue'] && data.pending_tasks_by_age.overdue.length > 0"
                    class="task-list">
                    <div v-for="task in getDisplayedTasks('overdue')" :key="task.task_id" class="task-item"
                        @click.stop="navigateToTask(task)">
                        <div class="task-header">
                            <div class="task-name">{{ task.task_name }}</div>
                            <span class="task-status" :class="task.task_status.toLowerCase().replace(' ', '-')">
                                {{ task.task_status }}
                            </span>
                        </div>
                        <div class="task-meta">
                            <span class="meta-item">👤 {{ task.assigned_to_name }}</span>
                            <span class="meta-item">🎯 {{ task.priority_level }}</span>
                            <span class="meta-item overdue-badge">⏰ Overdue by {{ Math.abs(task.days_until_due) }} day{{
                                Math.abs(task.days_until_due) !== 1 ? 's' : '' }}</span>
                        </div>
                    </div>
                    <button v-if="hasMoreTasks('overdue')" @click.stop="showAllTasks('overdue')" class="view-more-btn">
                        View {{ getRemainingCount('overdue') }} more tasks
                    </button>
                </div>
            </div>

            <!-- Due Today -->
            <div class="timeline-card due-today" @click="toggleCategory('due_today')">
                <div class="card-header">
                    <h4 class="category-title">DUE TODAY ({{ getCategoryCount('due_today') }})</h4>
                    <span class="expand-icon">{{ expandedCategories['due_today'] ? '▼' : '▶' }}</span>
                </div>
                <div v-if="expandedCategories['due_today'] && data.pending_tasks_by_age.due_today.length === 0"
                    class="empty-state">
                    No tasks due today
                </div>
                <div v-if="expandedCategories['due_today'] && data.pending_tasks_by_age.due_today.length > 0"
                    class="task-list">
                    <div v-for="task in getDisplayedTasks('due_today')" :key="task.task_id" class="task-item"
                        @click.stop="navigateToTask(task)">
                        <div class="task-header">
                            <div class="task-name">{{ task.task_name }}</div>
                            <span class="task-status" :class="task.task_status.toLowerCase().replace(' ', '-')">
                                {{ task.task_status }}
                            </span>
                        </div>
                        <div class="task-meta">
                            <span class="meta-item">👤 {{ task.assigned_to_name }}</span>
                            <span class="meta-item">🎯 {{ task.priority_level }}</span>
                            <span class="meta-item">⏰ Due today</span>
                        </div>
                    </div>
                    <button v-if="hasMoreTasks('due_today')" @click.stop="showAllTasks('due_today')"
                        class="view-more-btn">
                        View {{ getRemainingCount('due_today') }} more tasks
                    </button>
                </div>
            </div>

            <!-- Due Tomorrow -->
            <div class="timeline-card due-tomorrow" @click="toggleCategory('due_in_1_day')">
                <div class="card-header">
                    <h4 class="category-title">DUE TOMORROW ({{ getCategoryCount('due_in_1_day') }})</h4>
                    <span class="expand-icon">{{ expandedCategories['due_in_1_day'] ? '▼' : '▶' }}</span>
                </div>
                <div v-if="expandedCategories['due_in_1_day'] && data.pending_tasks_by_age.due_in_1_day.length === 0"
                    class="empty-state">
                    No tasks due tomorrow
                </div>
                <div v-if="expandedCategories['due_in_1_day'] && data.pending_tasks_by_age.due_in_1_day.length > 0"
                    class="task-list">
                    <div v-for="task in getDisplayedTasks('due_in_1_day')" :key="task.task_id" class="task-item"
                        @click.stop="navigateToTask(task)">
                        <div class="task-header">
                            <div class="task-name">{{ task.task_name }}</div>
                            <span class="task-status" :class="task.task_status.toLowerCase().replace(' ', '-')">
                                {{ task.task_status }}
                            </span>
                        </div>
                        <div class="task-meta">
                            <span class="meta-item">👤 {{ task.assigned_to_name }}</span>
                            <span class="meta-item">🎯 {{ task.priority_level }}</span>
                            <span class="meta-item">⏰ Due in 1 day</span>
                        </div>
                    </div>
                    <button v-if="hasMoreTasks('due_in_1_day')" @click.stop="showAllTasks('due_in_1_day')"
                        class="view-more-btn">
                        View {{ getRemainingCount('due_in_1_day') }} more tasks
                    </button>
                </div>
            </div>

            <!-- Due in 2-3 Days -->
            <div class="timeline-card due-soon" @click="toggleCategory('due_in_3_days')">
                <div class="card-header">
                    <h4 class="category-title">DUE IN 2-3 DAYS ({{ getCategoryCount('due_in_3_days') }})</h4>
                    <span class="expand-icon">{{ expandedCategories['due_in_3_days'] ? '▼' : '▶' }}</span>
                </div>
                <div v-if="expandedCategories['due_in_3_days'] && data.pending_tasks_by_age.due_in_3_days.length === 0"
                    class="empty-state">
                    No tasks in this range
                </div>
                <div v-if="expandedCategories['due_in_3_days'] && data.pending_tasks_by_age.due_in_3_days.length > 0"
                    class="task-list">
                    <div v-for="task in getDisplayedTasks('due_in_3_days')" :key="task.task_id" class="task-item"
                        @click.stop="navigateToTask(task)">
                        <div class="task-header">
                            <div class="task-name">{{ task.task_name }}</div>
                            <span class="task-status" :class="task.task_status.toLowerCase().replace(' ', '-')">
                                {{ task.task_status }}
                            </span>
                        </div>
                        <div class="task-meta">
                            <span class="meta-item">👤 {{ task.assigned_to_name }}</span>
                            <span class="meta-item">🎯 {{ task.priority_level }}</span>
                            <span class="meta-item">⏰ Due in {{ task.days_until_due }} days</span>
                        </div>
                    </div>
                    <button v-if="hasMoreTasks('due_in_3_days')" @click.stop="showAllTasks('due_in_3_days')"
                        class="view-more-btn">
                        View {{ getRemainingCount('due_in_3_days') }} more tasks
                    </button>
                </div>
            </div>

            <!-- Due This Week -->
            <div class="timeline-card due-week" @click="toggleCategory('due_in_a_week')">
                <div class="card-header">
                    <h4 class="category-title">DUE THIS WEEK ({{ getCategoryCount('due_in_a_week') }})</h4>
                    <span class="expand-icon">{{ expandedCategories['due_in_a_week'] ? '▼' : '▶' }}</span>
                </div>
                <div v-if="expandedCategories['due_in_a_week'] && data.pending_tasks_by_age.due_in_a_week.length === 0"
                    class="empty-state">
                    No tasks due this week
                </div>
                <div v-if="expandedCategories['due_in_a_week'] && data.pending_tasks_by_age.due_in_a_week.length > 0"
                    class="task-list">
                    <div v-for="task in getDisplayedTasks('due_in_a_week')" :key="task.task_id" class="task-item"
                        @click.stop="navigateToTask(task)">
                        <div class="task-header">
                            <div class="task-name">{{ task.task_name }}</div>
                            <span class="task-status" :class="task.task_status.toLowerCase().replace(' ', '-')">
                                {{ task.task_status }}
                            </span>
                        </div>
                        <div class="task-meta">
                            <span class="meta-item">👤 {{ task.assigned_to_name }}</span>
                            <span class="meta-item">🎯 {{ task.priority_level }}</span>
                            <span class="meta-item">⏰ Due in {{ task.days_until_due }} days</span>
                        </div>
                    </div>
                    <button v-if="hasMoreTasks('due_in_a_week')" @click.stop="showAllTasks('due_in_a_week')"
                        class="view-more-btn">
                        View {{ getRemainingCount('due_in_a_week') }} more tasks
                    </button>
                </div>
            </div>

            <!-- Due in 2 Weeks -->
            <div class="timeline-card due-2weeks" @click="toggleCategory('due_in_2_weeks')">
                <div class="card-header">
                    <h4 class="category-title">DUE IN 2 WEEKS ({{ getCategoryCount('due_in_2_weeks') }})</h4>
                    <span class="expand-icon">{{ expandedCategories['due_in_2_weeks'] ? '▼' : '▶' }}</span>
                </div>
                <div v-if="expandedCategories['due_in_2_weeks'] && data.pending_tasks_by_age.due_in_2_weeks.length === 0"
                    class="empty-state">
                    No tasks in this range
                </div>
                <div v-if="expandedCategories['due_in_2_weeks'] && data.pending_tasks_by_age.due_in_2_weeks.length > 0"
                    class="task-list">
                    <div v-for="task in getDisplayedTasks('due_in_2_weeks')" :key="task.task_id" class="task-item"
                        @click.stop="navigateToTask(task)">
                        <div class="task-header">
                            <div class="task-name">{{ task.task_name }}</div>
                            <span class="task-status" :class="task.task_status.toLowerCase().replace(' ', '-')">
                                {{ task.task_status }}
                            </span>
                        </div>
                        <div class="task-meta">
                            <span class="meta-item">👤 {{ task.assigned_to_name }}</span>
                            <span class="meta-item">🎯 {{ task.priority_level }}</span>
                            <span class="meta-item">⏰ Due in {{ task.days_until_due }} days</span>
                        </div>
                    </div>
                    <button v-if="hasMoreTasks('due_in_2_weeks')" @click.stop="showAllTasks('due_in_2_weeks')"
                        class="view-more-btn">
                        View {{ getRemainingCount('due_in_2_weeks') }} more tasks
                    </button>
                </div>
            </div>

            <!-- Due This Month -->
            <div class="timeline-card due-month" @click="toggleCategory('due_in_a_month')">
                <div class="card-header">
                    <h4 class="category-title">DUE THIS MONTH ({{ getCategoryCount('due_in_a_month') }})</h4>
                    <span class="expand-icon">{{ expandedCategories['due_in_a_month'] ? '▼' : '▶' }}</span>
                </div>
                <div v-if="expandedCategories['due_in_a_month'] && data.pending_tasks_by_age.due_in_a_month.length === 0"
                    class="empty-state">
                    No tasks due this month
                </div>
                <div v-if="expandedCategories['due_in_a_month'] && data.pending_tasks_by_age.due_in_a_month.length > 0"
                    class="task-list">
                    <div v-for="task in getDisplayedTasks('due_in_a_month')" :key="task.task_id" class="task-item"
                        @click.stop="navigateToTask(task)">
                        <div class="task-header">
                            <div class="task-name">{{ task.task_name }}</div>
                            <span class="task-status" :class="task.task_status.toLowerCase().replace(' ', '-')">
                                {{ task.task_status }}
                            </span>
                        </div>
                        <div class="task-meta">
                            <span class="meta-item">👤 {{ task.assigned_to_name }}</span>
                            <span class="meta-item">🎯 {{ task.priority_level }}</span>
                            <span class="meta-item">⏰ Due in {{ task.days_until_due }} days</span>
                        </div>
                    </div>
                    <button v-if="hasMoreTasks('due_in_a_month')" @click.stop="showAllTasks('due_in_a_month')"
                        class="view-more-btn">
                        View {{ getRemainingCount('due_in_a_month') }} more tasks
                    </button>
                </div>
            </div>

            <!-- Due More Than 1 Month Later -->
            <div class="timeline-card due-later" @click="toggleCategory('due_later')">
                <div class="card-header">
                    <h4 class="category-title">DUE MUCH LATER ({{ getCategoryCount('due_later') }})</h4>
                    <span class="expand-icon">{{ expandedCategories['due_later'] ? '▼' : '▶' }}</span>
                </div>
                <div v-if="expandedCategories['due_later'] && data.pending_tasks_by_age.due_later.length === 0"
                    class="empty-state">
                    No tasks in this range
                </div>
                <div v-if="expandedCategories['due_later'] && data.pending_tasks_by_age.due_later.length > 0"
                    class="task-list">
                    <div v-for="task in getDisplayedTasks('due_later')" :key="task.task_id" class="task-item"
                        @click.stop="navigateToTask(task)">
                        <div class="task-header">
                            <div class="task-name">{{ task.task_name }}</div>
                            <span class="task-status" :class="task.task_status.toLowerCase().replace(' ', '-')">
                                {{ task.task_status }}
                            </span>
                        </div>
                        <div class="task-meta">
                            <span class="meta-item">👤 {{ task.assigned_to_name }}</span>
                            <span class="meta-item">🎯 {{ task.priority_level }}</span>
                            <span class="meta-item">⏰ Due in {{ task.days_until_due }} days</span>
                        </div>
                    </div>
                    <button v-if="hasMoreTasks('due_later')" @click.stop="showAllTasks('due_later')"
                        class="view-more-btn">
                        View {{ getRemainingCount('due_later') }} more tasks
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { dashboardService } from '@/services/dashboardService';

export default {
    name: 'TaskTimeline',
    data() {
        return {
            data: {
                pending_tasks_by_age: {
                    overdue: [],
                    due_today: [],
                    due_in_1_day: [],
                    due_in_3_days: [],
                    due_in_a_week: [],
                    due_in_2_weeks: [],
                    due_in_a_month: [],
                    due_later: []
                }
            },
            loading: true,
            error: null,
            expandedCategories: {
                overdue: false,
                due_today: false,
                due_in_1_day: false,
                due_in_3_days: false,
                due_in_a_week: false,
                due_in_2_weeks: false,
                due_in_a_month: false,
                due_later: false
            },
            taskLimit: 3,
            showAllForCategory: {}
        };
    },
    async mounted() {
        try {
            const userStr = sessionStorage.getItem('user');
            if (!userStr) {
                this.error = 'User not found';
                this.loading = false;
                return;
            }

            const user = JSON.parse(userStr);
            const userId = user.id;
            console.log('TaskTimeline - User ID:', userId);

            this.data = await dashboardService.getPendingTasksByAgeAndStaffName(userId);
            console.log('TaskTimeline - Response:', this.data);

            Object.keys(this.expandedCategories).forEach(category => {
                if (this.data.pending_tasks_by_age[category].length > 0) {
                    this.expandedCategories[category] = true;
                } else {
                    this.expandedCategories[category] = false;
                }
            });

            this.loading = false;
        } catch (err) {
            console.error('TaskTimeline - Error:', err);
            this.error = err.message;
            this.loading = false;
        }
    },
    methods: {
        toggleCategory(category) {
            this.expandedCategories[category] = !this.expandedCategories[category];
        },
        getCategoryCount(category) {
            return this.data.pending_tasks_by_age[category]?.length || 0;
        },
        getDisplayedTasks(category) {
            const tasks = this.data.pending_tasks_by_age[category] || [];
            if (this.showAllForCategory[category]) {
                return tasks;
            }
            return tasks.slice(0, this.taskLimit);
        },
        hasMoreTasks(category) {
            const tasks = this.data.pending_tasks_by_age[category] || [];
            return tasks.length > this.taskLimit && !this.showAllForCategory[category];
        },
        getRemainingCount(category) {
            const tasks = this.data.pending_tasks_by_age[category] || [];
            return tasks.length - this.taskLimit;
        },
        showAllTasks(category) {
            this.showAllForCategory[category] = true;
        },
        navigateToTask(task) {
            console.log('🔍 Task clicked:', task);
            console.log('🔍 Task ID:', task.task_id);
            console.log('🔍 Project ID:', task.proj_id);
            
            // Check if task has required IDs
            if (!task.task_id) {
                console.error('❌ Task missing task_id:', task);
                alert('Cannot navigate: Task ID is missing');
                return;
            }
            
            // Build the target URL with "from" parameter to indicate source
            const baseUrl = task.proj_id 
                ? `/projects/${task.proj_id}/tasks/${task.task_id}`
                : `/tasks/${task.task_id}`;
            
            const targetUrl = `${baseUrl}?from=dashboard`;
            
            console.log(`🚀 Attempting navigation to: ${targetUrl}`);
            console.log('🔍 Current route:', this.$route.path);
            
            // Use window.location for reliable navigation
            try {
                window.location.href = targetUrl;
                console.log('✅ Navigation initiated');
            } catch (err) {
                console.error('❌ Navigation failed:', err);
                alert(`Failed to navigate to task. URL: ${targetUrl}`);
            }
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

.timeline-container {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
}

.timeline-card {
    background: white;
    border-radius: 8px;
    padding: 16px;
    cursor: pointer;
    transition: all 0.2s;
    border: 1px solid #e5e7eb;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.timeline-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.overdue .category-title {
    color: #dc2626;
}

.due-today .category-title {
    color: #ea580c;
}

.due-tomorrow .category-title {
    color: #ca8a04;
}

.due-soon .category-title {
    color: #d97706;
}

.due-week .category-title {
    color: #2563eb;
}

.due-2weeks .category-title {
    color: #059669;
}

.due-month .category-title {
    color: #6b7280;
}

.due-later .category-title {
    color: #9ca3af;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.category-title {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    letter-spacing: 0.5px;
}

.expand-icon {
    font-size: 12px;
    opacity: 0.7;
}

.task-list {
    margin-top: 16px;
    border-top: 1px solid rgba(0, 0, 0, 0.1);
    padding-top: 12px;
}

.empty-state {
    margin-top: 16px;
    padding: 24px;
    text-align: center;
    color: #9ca3af;
    font-size: 14px;
    font-style: italic;
    border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.task-item {
    padding: 14px;
    background: white;
    border-radius: 8px;
    margin-bottom: 10px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    cursor: pointer;
    transition: all 0.2s;
}

.task-item:hover {
    background: #f9fafb;
    border-color: #6366f1;
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.15);
    transform: translateX(4px);
}

.task-item:last-child {
    margin-bottom: 0;
}

.task-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 8px;
    margin-bottom: 10px;
}

.task-name {
    font-weight: 600;
    font-size: 15px;
    color: #111827;
    flex: 1;
    line-height: 1.4;
}

.task-status {
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    white-space: nowrap;
    flex-shrink: 0;
}

.task-status.not-started {
    background: #fef2f2;
    color: #dc2626;
}

.task-status.in-progress {
    background: #fef3c7;
    color: #d97706;
}

.task-status.completed {
    background: #d1fae5;
    color: #059669;
}

.task-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    font-size: 13px;
}

.meta-item {
    color: #6b7280;
    display: flex;
    align-items: center;
    gap: 4px;
}

.overdue-badge {
    color: #dc2626;
    font-weight: 600;
}

.loading,
.error {
    color: #6b7280;
    font-size: 14px;
    margin: 10px;
}

.error {
    color: #dc2626;
}

.view-more-btn {
    width: 100%;
    padding: 10px;
    margin-top: 10px;
    background: #f3f4f6;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    color: #6366f1;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}

.view-more-btn:hover {
    background: #e5e7eb;
    border-color: #6366f1;
    color: #4f46e5;
}

@media (max-width: 1024px) {
    .timeline-container {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 640px) {
    .timeline-container {
        grid-template-columns: 1fr;
    }
}
</style>