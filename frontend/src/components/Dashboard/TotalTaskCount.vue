<template>
    <div>
        <h3 class="section-title">Total Tasks</h3>
        <div v-if="loading" class="loading">Loading...</div>
        <div v-else-if="error" class="error">Error: {{ error }}</div>
        <div v-else class="cards-container">
            <div class="card card-blue">
                <div class="stat-number">{{ data.total_tasks }}</div>
                <div class="stat-label">Total Tasks</div>
            </div>
            <!-- Only show staff count for managers (when staff_count > 1) -->
            <div v-if="data.staff_count > 1" class="card card-green">
                <div class="stat-number">{{ data.staff_count }}</div>
                <div class="stat-label">Staff Members</div>
            </div>
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

<style scoped>
.section-title {
    font-size: 20px;
    font-weight: 600;
    color: #111827;
    margin-bottom: 20px;
}

.cards-container {
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
}

.card {
    background: white;
    border-radius: 12px;
    padding: 32px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border: 1px solid #e5e7eb;
    flex: 1;
    min-width: 200px;
    margin: 10px;
    text-align: center;
}

.stat-number {
    font-size: 64px;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 12px;
}

.card-blue .stat-number {
    background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.card-green .stat-number {
    background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.stat-label {
    font-size: 14px;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 500;
}

.loading,
.error {
    color: #6b7280;
    font-size: 14px;
    margin: 10px;
}
</style>