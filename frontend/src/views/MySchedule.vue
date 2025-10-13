<template>
  <div class="my-schedule-page">
    <!-- Header Section -->
    <div class="header-section">
      <div class="container">
        <div class="header-content">

          <div class="title-section">
            <h1 class="hero-title">📆 Schedule</h1>
            <div class="division-badge" v-if="currentUser">
              {{ currentUser.division_name }} Department
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Calendar Section -->
    <div class="calendar-section">
      <div class="container">
        <TaskCalendar />
      </div>
    </div>
  </div>
</template>

<script>
import AuthService from '@/services/auth.js';
import TaskCalendar from '@/components/Dashboard/TaskCalendar.vue';

export default {
  name: 'MySchedule',
  components: {
    TaskCalendar
  },
  data() {
    return {
      currentUser: null
    };
  },
  mounted() {
    if (AuthService.checkAuthStatus()) {
      this.currentUser = AuthService.getCurrentUser();
    }
  }
}
</script>

<style scoped>
.my-schedule-page {
  min-height: 100vh;
  background: #f8fafc;
}

.container {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
}

.header-section {
  background: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 2rem 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
  flex-wrap: wrap;
}

.title-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.hero-title {
  font-size: 2.25rem;
  line-height: 1.2;
  font-weight: 800;
  color: #111827;
  margin: 0;
}

.hero-subtitle {
  font-size: 1rem;
  color: #6b7280;
  margin: 0.5rem 0 0 0;
  font-weight: 500;
}

.division-badge {
  background: #e0f2fe;
  color: #0277bd;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 500;
  align-self: flex-start;
}

.badge-icon {
  font-size: 1rem;
}

.calendar-section {
  padding: 2rem 0 4rem 0;
}

@media (max-width: 768px) {
  .container {
    padding: 0 1rem;
  }
  
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .hero-title {
    font-size: 2rem;
  }
  
  .division-badge {
    width: 100%;
    justify-content: center;
  }
}
</style>
