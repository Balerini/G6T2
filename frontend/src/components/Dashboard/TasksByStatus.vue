<template>
    <div>
        <h3 class="section-title">Tasks By Status</h3>
        <div v-if="loading" class="loading">Loading...</div>
        <div v-else-if="error" class="error">Error: {{ error }}</div>
        <div v-else class="card">
            <div class="chart-container">
                <Pie :data="chartData" :options="chartOptions" />
            </div>
        </div>
    </div>
</template>

<script>
import { dashboardService } from '@/services/dashboardService';
import { Pie } from 'vue-chartjs';

export default {
    name: 'TasksByStatus',
    components: {
        Pie
    },
    data() {
        return {
            data: {},
            loading: true,
            error: null,
            chartData: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: [
                        '#f87171',  // Not Started - red
                        '#fbbf24',  // In Progress - yellow
                        '#34d399',  // Completed - green
                        '#fb923c',  // Pending - orange
                        '#a78bfa',  // Any other status - purple
                        '#60a5fa'   // Any other status - blue
                    ],
                }]
            },
            chartOptions: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                    }
                }
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
            console.log('TasksByStatus - User ID:', userId);
            console.log('TasksByStatus - Full User:', user);

            this.data = await dashboardService.getCountofAllTasksByStatus(userId);
            console.log('TasksByStatus - Response:', this.data);

            if (this.data.tasks_by_status) {
                this.chartData.labels = Object.keys(this.data.tasks_by_status);
                this.chartData.datasets[0].data = Object.values(this.data.tasks_by_status);
            }

            this.loading = false;
        } catch (err) {
            console.error('TasksByStatus - Error:', err);
            this.error = err.message;
            this.loading = false;
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

.card {
    background: white;
    border-radius: 12px;
    padding: 32px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border: 1px solid #e5e7eb;
    max-width: 600px;
    margin: 10px auto;
}

.chart-container {
    max-width: 400px;
    max-height: 400px;
    margin: 0 auto;
}

.loading,
.error {
    color: #6b7280;
    font-size: 14px;
    margin: 10px;
}
</style>