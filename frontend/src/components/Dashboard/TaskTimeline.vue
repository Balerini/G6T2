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
                <div v-if="expandedCategories['overdue'] && data.pending_tasks_by_age.overdue.length > 0"
                    class="task-list">
                    <div v-for="task in data.pending_tasks_by_age.overdue" :key="task.task_id" class="task-item">
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
                </div>
            </div>

            <!-- Due Today -->
            <div class="timeline-card due-today" @click="toggleCategory('due_today')">
                <div class="card-header">
                    <h4 class="category-title">DUE TODAY ({{ getCategoryCount('due_today') }})</h4>
                    <span class="expand-icon">{{ expandedCategories['due_today'] ? '▼' : '▶' }}</span>
                </div>
                <div v-if="expandedCategories['due_today'] && data.pending_tasks_by_age.due_today.length > 0"
                    class="task-list">
                    <div v-for="task in data.pending_tasks_by_age.due_today" :key="task.task_id" class="task-item">
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
                </div>
            </div>

            <!-- Due Tomorrow -->
            <div class="timeline-card due-tomorrow" @click="toggleCategory('due_in_1_day')">
                <div class="card-header">
                    <h4 class="category-title">DUE TOMORROW ({{ getCategoryCount('due_in_1_day') }})</h4>
                    <span class="expand-icon">{{ expandedCategories['due_in_1_day'] ? '▼' : '▶' }}</span>
                </div>
                <div v-if="expandedCategories['due_in_1_day'] && data.pending_tasks_by_age.due_in_1_day.length > 0"
                    class="task-list">
                    <div v-for="task in data.pending_tasks_by_age.due_in_1_day" :key="task.task_id" class="task-item">
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
                </div>
            </div>

            <!-- Due in 2-3 Days -->
            <div class="timeline-card due-soon" @click="toggleCategory('due_in_3_days')">
                <div class="card-header">
                    <h4 class="category-title">DUE IN 2-3 DAYS ({{ getCategoryCount('due_in_3_days') }})</h4>
                    <span class="expand-icon">{{ expandedCategories['due_in_3_days'] ? '▼' : '▶' }}</span>
                </div>
                <div v-if="expandedCategories['due_in_3_days'] && data.pending_tasks_by_age.due_in_3_days.length > 0"
                    class="task-list">
                    <div v-for="task in data.pending_tasks_by_age.due_in_3_days" :key="task.task_id" class="task-item">
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
                </div>
            </div>

            <!-- Due This Week -->
            <div class="timeline-card due-week" @click="toggleCategory('due_in_a_week')">
                <div class="card-header">
                    <h4 class="category-title">DUE THIS WEEK ({{ getCategoryCount('due_in_a_week') }})</h4>
                    <span class="expand-icon">{{ expandedCategories['due_in_a_week'] ? '▼' : '▶' }}</span>
                </div>
                <div v-if="expandedCategories['due_in_a_week'] && data.pending_tasks_by_age.due_in_a_week.length > 0"
                    class="task-list">
                    <div v-for="task in data.pending_tasks_by_age.due_in_a_week" :key="task.task_id" class="task-item">
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
                </div>
            </div>

            <!-- Due in 2 Weeks -->
            <div class="timeline-card due-2weeks" @click="toggleCategory('due_in_2_weeks')">
                <div class="card-header">
                    <h4 class="category-title">DUE IN 2 WEEKS ({{ getCategoryCount('due_in_2_weeks') }})</h4>
                    <span class="expand-icon">{{ expandedCategories['due_in_2_weeks'] ? '▼' : '▶' }}</span>
                </div>
                <div v-if="expandedCategories['due_in_2_weeks'] && data.pending_tasks_by_age.due_in_2_weeks.length > 0"
                    class="task-list">
                    <div v-for="task in data.pending_tasks_by_age.due_in_2_weeks" :key="task.task_id" class="task-item">
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
                </div>
            </div>

            <!-- Due This Month -->
            <div class="timeline-card due-month" @click="toggleCategory('due_in_a_month')">
                <div class="card-header">
                    <h4 class="category-title">DUE THIS MONTH ({{ getCategoryCount('due_in_a_month') }})</h4>
                    <span class="expand-icon">{{ expandedCategories['due_in_a_month'] ? '▼' : '▶' }}</span>
                </div>
                <div v-if="expandedCategories['due_in_a_month'] && data.pending_tasks_by_age.due_in_a_month.length > 0"
                    class="task-list">
                    <div v-for="task in data.pending_tasks_by_age.due_in_a_month" :key="task.task_id" class="task-item">
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
                </div>
            </div>

            <!-- Due More Than 1 Month Later -->
            <div class="timeline-card due-later" @click="toggleCategory('due_later')">
                <div class="card-header">
                    <h4 class="category-title">DUE MUCH LATER ({{ getCategoryCount('due_later') }})</h4>
                    <span class="expand-icon">{{ expandedCategories['due_later'] ? '▼' : '▶' }}</span>
                </div>
                <div v-if="expandedCategories['due_later'] && data.pending_tasks_by_age.due_later.length > 0"
                    class="task-list">
                    <div v-for="task in data.pending_tasks_by_age.due_later" :key="task.task_id" class="task-item">
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
            }
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

.task-item {
    padding: 14px;
    background: white;
    border-radius: 8px;
    margin-bottom: 10px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
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