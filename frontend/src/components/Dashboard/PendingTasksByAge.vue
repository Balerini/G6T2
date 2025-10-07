<template>
    <div>
        <h3>Pending Tasks Summary</h3>
        <div v-if="loading">Loading...</div>
        <div v-else-if="error">Error: {{ error }}</div>
        <div v-else>
            <div v-if="data.summary">
                <p>Overdue: {{ data.summary.overdue }}</p>
                <p>Due Today: {{ data.summary.due_today }}</p>
                <p>Due in 1 Day: {{ data.summary.due_in_1_day }}</p>
                <p>Due in 3 Days: {{ data.summary.due_in_3_days }}</p>
                <p>Due in a Week: {{ data.summary.due_in_a_week }}</p>
                <p>Due in 2 Weeks: {{ data.summary.due_in_2_weeks }}</p>
                <p>Due in a Month: {{ data.summary.due_in_a_month }}</p>
            </div>
        </div>
    </div>
</template>

<script>
import { dashboardService } from '@/services/dashboardService';

export default {
    name: 'PendingTasksSummary',
    data() {
        return {
            data: {
                summary: {}
            },
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
            console.log('PendingTasksSummary - User ID:', userId);

            this.data = await dashboardService.getPendingTasksByAgeAndStaffName(userId);
            console.log('PendingTasksSummary - Response:', this.data);
            this.loading = false;
        } catch (err) {
            console.error('PendingTasksSummary - Error:', err);
            this.error = err.message;
            this.loading = false;
        }
    }
};
</script>