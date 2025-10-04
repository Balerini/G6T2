<template>
    <div>
        <h3>Pending Tasks By Age</h3>
        <div v-if="loading">Loading...</div>
        <div v-else-if="error">Error: {{ error }}</div>
        <div v-else>
            <p>Division: {{ data.division_name }}</p>

            <h4>Summary</h4>
            <div v-if="data.summary">
                <p>Overdue: {{ data.summary.overdue }}</p>
                <p>Due Today: {{ data.summary.due_today }}</p>
                <p>Due in 1 Day: {{ data.summary.due_in_1_day }}</p>
                <p>Due in 3 Days: {{ data.summary.due_in_3_days }}</p>
                <p>Due in a Week: {{ data.summary.due_in_a_week }}</p>
                <p>Due in 2 Weeks: {{ data.summary.due_in_2_weeks }}</p>
                <p>Due in a Month: {{ data.summary.due_in_a_month }}</p>
            </div>

            <h4>Detailed Tasks</h4>
            <div v-if="data.pending_tasks_by_age">
                <div v-for="(tasks, category) in data.pending_tasks_by_age" :key="category">
                    <h5>{{ category.replace(/_/g, ' ').toUpperCase() }} ({{ tasks.length }})</h5>
                    <div v-if="tasks.length > 0">
                        <div v-for="task in tasks" :key="task.task_id">
                            <p>
                                - {{ task.task_name }}
                                | Assigned to: {{ task.assigned_to_name }}
                                | Priority: {{ task.task_priority }}
                                | Days until due: {{ task.days_until_due }}
                            </p>
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
    name: 'PendingTasksByAge',
    data() {
        return {
            data: {},
            loading: true,
            error: null,
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
            console.log('PendingTasksByAge - User ID:', userId);
            console.log('PendingTasksByAge - Full User:', user);

            this.data = await dashboardService.getPendingTasksByAgeAndStaffName(userId);
            console.log('PendingTasksByAge - Response:', this.data);
            this.loading = false;
        } catch (err) {
            console.error('PendingTasksByAge - Error:', err);
            this.error = err.message;
            this.loading = false;
        }
    }
};
</script>