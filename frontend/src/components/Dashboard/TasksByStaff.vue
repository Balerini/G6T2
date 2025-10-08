<template>
    <div>
        <h3 class="section-title">Tasks By Staff</h3>
        <div v-if="loading" class="loading">Loading...</div>
        <div v-else-if="error" class="error">Error: {{ error }}</div>
        <div v-else class="chart-card">
            <div class="chart-scroll-container">
                <div class="chart-container" :style="{ height: chartHeight + 'px' }">
                    <Bar :data="chartData" :options="chartOptions" />
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { dashboardService } from '@/services/dashboardService';
import { Bar } from 'vue-chartjs';
import { Chart as ChartJS, registerables } from 'chart.js';

ChartJS.register(...registerables);

export default {
    name: 'TasksByStaff',
    components: {
        Bar
    },
    data() {
        return {
            data: {},
            loading: true,
            error: null,
            chartData: {
                labels: [],
                datasets: []
            },
            chartOptions: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                return `${context.dataset.label}: ${context.parsed.x} tasks`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        stacked: true,
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        },
                        title: {
                            display: true,
                            text: 'Number of Tasks'
                        }
                    },
                    y: {
                        stacked: true,
                        title: {
                            display: true,
                            text: 'Staff Members'
                        }
                    }
                }
            },
            chartHeight: 400
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

            if (this.data.tasks_by_staff && this.data.tasks_by_staff.length > 0) {
                this.processChartData();
            }

            this.loading = false;
        } catch (err) {
            console.error('TasksByStaff - Error:', err);
            this.error = err.message;
            this.loading = false;
        }
    },
    methods: {
        getStatusColor(status) {
            const colorMap = {
                'Unassigned': '#f87171',
                'Ongoing': '#fbbf24',
                'Completed': '#34d399',
                'Under Review': '#fb923c'
            };
            return colorMap[status] || '#9ca3af';
        },

        processChartData() {
            const staffData = this.data.tasks_by_staff;

            const sortedStaffData = [...staffData].sort((a, b) =>
                a.staff_name.localeCompare(b.staff_name)
            );

            const statusSet = new Set();
            sortedStaffData.forEach(staff => {
                staff.tasks.forEach(task => {
                    if (task.task_status) {
                        statusSet.add(task.task_status);
                    }
                });
            });

            const uniqueStatuses = Array.from(statusSet).sort();

            console.log('Unique statuses found:', uniqueStatuses);

            // Build datasets - one for each status with matching colors
            this.chartData.datasets = uniqueStatuses.map((status) => ({
                label: status,
                data: [],
                backgroundColor: this.getStatusColor(status)
            }));

            this.chartData.labels = sortedStaffData.map(staff =>
                `${staff.staff_name} (${staff.staff_role})`
            );

            sortedStaffData.forEach(staff => {
                const statusCounts = {};

                uniqueStatuses.forEach(status => {
                    statusCounts[status] = 0;
                });

                staff.tasks.forEach(task => {
                    const status = task.task_status;
                    if (status && Object.prototype.hasOwnProperty.call(statusCounts, status)) {
                        statusCounts[status]++;
                    }
                });

                uniqueStatuses.forEach((status, index) => {
                    this.chartData.datasets[index].data.push(statusCounts[status]);
                });
            });

            const staffCount = sortedStaffData.length;
            this.chartHeight = Math.max(400, staffCount * 40);

            console.log('Chart height set to:', this.chartHeight, 'for', staffCount, 'staff members');
        }
        // Remove the generateColors method entirely - it's no longer needed
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

.chart-card {
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border: 1px solid #e5e7eb;
}

.chart-scroll-container {
    max-height: 600px;
    overflow-y: auto;
    overflow-x: hidden;
}

.chart-container {
    min-height: 400px;
    position: relative;
}

.loading,
.error {
    color: #6b7280;
    font-size: 14px;
    margin: 10px;
}

/* Scrollbar styling */
.chart-scroll-container::-webkit-scrollbar {
    width: 8px;
}

.chart-scroll-container::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 4px;
}

.chart-scroll-container::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 4px;
}

.chart-scroll-container::-webkit-scrollbar-thumb:hover {
    background: #a8a8a8;
}
</style>