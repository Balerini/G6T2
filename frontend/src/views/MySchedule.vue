<template>
  <div class="my-schedule-page">
    <!-- Header Section -->
    <div class="header-section">
      <div class="container">
        <h1 class="hero-title">My Schedule</h1>
        <div class="division-badge" v-if="currentUser">
          {{ currentUser.division_name }} Department
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
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.header-section {
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  padding: 1.5rem 0;
}

.hero-title {
  font-size: 2.25rem;
  line-height: 1.2;
  font-weight: 800;
  color: #111827;
  margin: 0 0 0.5rem 0;
}

.division-badge {
  background: #e0f2fe;
  color: #0277bd;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 500;
  display: inline-block;
}

.calendar-section {
  padding: 2rem 0;
}
</style>
