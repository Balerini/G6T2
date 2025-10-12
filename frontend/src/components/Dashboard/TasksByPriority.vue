<template>
    <div>
        <h3 class="section-title">Tasks By Priority</h3>
        <div v-if="loading" class="loading">Loading...</div>
        <div v-else-if="error" class="error">Error: {{ error }}</div>
        <div v-else class="card">
            <div v-if="hasNoTasks" class="no-tasks-message">
                <div class="no-tasks-icon">📋</div>
                <div class="no-tasks-text">No tasks assigned</div>
            </div>
            <div v-else class="chart-container">
                <Doughnut :data="chartData" :options="chartOptions" />
            </div>
        </div>
    </div>
</template>

<script>
import { dashboardService } from '@/services/dashboardService';
import { Doughnut } from 'vue-chartjs';

export default {
    name: 'TasksByPriority',
    components: {
        Doughnut
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
                        '#ef4444',  // High - red
                        '#f59e0b',  // Medium - amber
                        '#10b981',  // Low - green
                        '#94a3b8'   // Unknown - gray
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
    computed: {
        hasNoTasks() {
            if (!this.data.tasks_by_priority) return true;
            const totalTasks = Object.values(this.data.tasks_by_priority).reduce((sum, count) => sum + count, 0);
            return totalTasks === 0;
        }
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
            console.log('TasksByPriority - User ID:', userId);
            console.log('TasksByPriority - Full User:', user);

            this.data = await dashboardService.getCountofAllTasksByPriority(userId);
            console.log('TasksByPriority - Response:', this.data);

            if (this.data.tasks_by_priority) {
                // Define the order we want: High, Medium, Low
                const priorityOrder = ['High', 'Medium', 'Low'];
                const labels = [];
                const values = [];

                // Add priorities in order if they exist
                priorityOrder.forEach(priority => {
                    if (this.data.tasks_by_priority[priority]) {
                        labels.push(priority);
                        values.push(this.data.tasks_by_priority[priority]);
                    }
                });

                // Add Unknown if it exists
                if (this.data.tasks_by_priority['Unknown']) {
                    labels.push('Unknown');
                    values.push(this.data.tasks_by_priority['Unknown']);
                }

                this.chartData.labels = labels;
                this.chartData.datasets[0].data = values;
            }

            this.loading = false;
        } catch (err) {
            console.error('TasksByPriority - Error:', err);
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
    max-width: 100%;
    margin: 0;
}

.chart-container {
    max-width: 400px;
    max-height: 400px;
    margin: 0 auto;
}

.no-tasks-message {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60px 20px;
    text-align: center;
}

.no-tasks-icon {
    font-size: 64px;
    margin-bottom: 16px;
    opacity: 0.5;
}

.no-tasks-text {
    font-size: 18px;
    color: #6b7280;
    font-weight: 500;
}

.loading,
.error {
    color: #6b7280;
    font-size: 14px;
    margin: 10px;
}
</style>