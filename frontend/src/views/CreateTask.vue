<template>
  <div class="create-task-page">
    <!-- Header -->
    <header class="page-header">
      <div class="header-container">
        <h1 class="page-title">Create Task</h1>
        <button class="back-button" @click="goBack">← Back to Projects</button>
      </div>
    </header>

    <!-- Main Content -->
    <main class="page-content">
      <div class="form-container">
        <TaskForm />
      </div>
    </main>
  </div>
</template>

<script>
import TaskForm from "@/components/CreateTaskForm.vue";

export default {
  name: "CreateTask",
  components: {
    TaskForm
  },
  methods: {
    goBack() {
      this.$router.push("/projects");
    }
  }
};
</script>

<style scoped>
.create-task-page {
  min-height: 100vh;
  background-color: #ffffff;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
}

.page-header {
  border-bottom: 1px solid #e5e5e5;
  background-color: #ffffff;
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: #000000;
  margin: 0;
  letter-spacing: -0.5px;
}

.back-button {
  background-color: #000000;
  color: #ffffff;
  border: none;
  padding: 12px 20px;
  font-size: 14px;
  font-weight: 500;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.back-button:hover {
  background-color: #333333;
}

.page-content {
  padding: 48px 32px;
}

.form-container {
  max-width: 800px;
  margin: 0 auto;
  background-color: #ffffff;
  border: 1px solid #e5e5e5;
  border-radius: 12px;
  padding: 48px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}
</style>
