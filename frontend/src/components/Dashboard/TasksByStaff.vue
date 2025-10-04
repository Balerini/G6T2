<template>
    <div>
        <h3>Tasks By Staff</h3>
        <div v-if="loading">Loading...</div>
        <div v-else-if="error">Error: {{ error }}</div>
        <div v-else>
            <p>Division: {{ data.division_name }}</p>
            <div v-if="data.tasks_by_staff && data.tasks_by_staff.length > 0">
                <div v-for="staff in data.tasks_by_staff" :key="staff.staff_id">
                    <h4>{{ staff.staff_name }} ({{ staff.staff_role }})</h4>
                    <p>Task Count: {{ staff.task_count }}</p>
                    <div v-if="staff.tasks.length > 0">
                        <div v-for="task in staff.tasks" :key="task.task_id">
                            <p>- {{ task.task_name }} [{{ task.task_status }}] - Priority: {{ task.task_priority }}</p>
                        </div>
                    </div>
                </div>
            </div>
            <p v-else>No staff tasks found</p>
        </div>
    </div>
</template>

<script>
import { dashboardService } from '@/services/dashboardService';

export default {
    name: 'TasksByStaff',
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
            console.log('TasksByStaff - User ID:', userId);
            console.log('TasksByStaff - Full User:', user);

            this.data = await dashboardService.getCountAndNameofTasksByStaff(userId);
            console.log('TasksByStaff - Response:', this.data);
            this.loading = false;
        } catch (err) {
            console.error('TasksByStaff - Error:', err);
            this.error = err.message;
            this.loading = false;
        }
    }
};
</script>