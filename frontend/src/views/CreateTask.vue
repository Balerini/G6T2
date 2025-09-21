<template>
  <div class="create-task-page">
    <!-- Header -->
    <header class="page-header">
      <div class="header-container">
        <h1 class="page-title">Create Task</h1>
        <button class="back-button" @click="goBack">← Back to Projects</button>
      </div>
    </header>
    
    <!-- Success Message -->
    <div v-if="successMessage" class="alert alert-success">
      {{ successMessage }}
    </div>
    
    <!-- Error Message -->
    <div v-if="errorMessage" class="alert alert-error">
      {{ errorMessage }}
    </div>
    
    <!-- Main Content -->
    <main class="page-content">
      <div class="form-container">
        <TaskForm 
          @success="handleSuccess" 
          @error="handleError"
          @cancel="goBack"
        />
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
  data() {
    return {
      successMessage: '',
      errorMessage: ''
    };
  },
  methods: {
    goBack() {
      this.$router.push("/projects");
    },
    handleSuccess(taskData) {
      console.log('Success handler called with:', taskData);
      this.successMessage = `Task "${taskData.taskName}" created successfully!`;
      this.errorMessage = '';
      
      // Redirect after a short delay to show the success message
      setTimeout(() => {
        console.log('Redirecting back to projects...');
        this.goBack();
      }, 1500);
    },
    handleError(error) {
      console.log('Error handler called with:', error);
      this.errorMessage = `Error creating task: ${error}`;
      this.successMessage = '';
    }
  }
};
</script>

<style scoped>
/* Existing styles plus alerts */
.create-task-page {
  min-height: 100vh;
  background-color: #ffffff;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
}

.alert {
  max-width: 1200px;
  margin: 0 auto;
  padding: 12px 32px;
  margin-bottom: 16px;
  border-radius: 6px;
  font-weight: 500;
}

.alert-success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.alert-error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

/* Rest of existing styles */
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
