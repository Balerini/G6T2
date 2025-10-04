<template>
    <div>
        <h3>Tasks By Status</h3>
        <div v-if="loading">Loading...</div>
        <div v-else-if="error">Error: {{ error }}</div>
        <div v-else>
            <p>Division: {{ data.division_name }}</p>
            <div v-if="data.tasks_by_status">
                <div v-for="(count, status) in data.tasks_by_status" :key="status">
                    <p>{{ status }}: {{ count }}</p>
                </div>
            </div>
            <p v-else>No tasks found</p>
        </div>
    </div>
</template>

<script>
import { dashboardService } from '@/services/dashboardService';

export default {
    name: 'TasksByStatus',
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
            console.log('TasksByStatus - User ID:', userId);
            console.log('TasksByStatus - Full User:', user);

            this.data = await dashboardService.getCountofAllTasksByStatus(userId);
            console.log('TasksByStatus - Response:', this.data);
            this.loading = false;
        } catch (err) {
            console.error('TasksByStatus - Error:', err);
            this.error = err.message;
            this.loading = false;
        }
    }
};
</script>