<template>
    <div>
        <h3>Total Tasks</h3>
        <div v-if="loading">Loading...</div>
        <div v-else-if="error">Error: {{ error }}</div>
        <div v-else>
            <p>Total Tasks: {{ data.total_tasks }}</p>
            <p>Staff Count: {{ data.staff_count }}</p>
            <p>Division: {{ data.division_name }}</p>
        </div>
    </div>
</template>

<script>
import { dashboardService } from '@/services/dashboardService';

export default {
    name: 'TotalTaskCount',
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
            console.log('TotalTaskCount - User ID:', userId);
            console.log('TotalTaskCount - Full User:', user);

            this.data = await dashboardService.getCountofAllTasksByTeam(userId);
            console.log('TotalTaskCount - Response:', this.data);
            this.loading = false;
        } catch (err) {
            console.error('TotalTaskCount - Error:', err);
            this.error = err.message;
            this.loading = false;
        }
    }
};
</script>