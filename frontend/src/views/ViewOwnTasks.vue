<template>
  <div class="crm-container">
    <div class="header-section">
      <div class="container">
        <div class="header-content">
          <h1 class="hero-title">Tasks</h1>
        </div>
      </div>
      <div class="container"> 
        <!-- Status Filter Tabs -->
        <div class="action-tabs mb-4">
          <button
            v-for="status in statuses"
            :key="status"
            @click="filter = status"
            :class="['tab-btn', { active: filter === status }]"
          >
            {{ status }}
          </button>
        </div>
        <!-- Sort Filter Tabs -->
        <div class="action-tabs mb-4 flex space-x-2">
          <button
            v-for="order in sortOrders"
            :key="order.value"
            @click="sortOrder = order.value"
            :class="['tab-btn', {active: sortOrder === order.value}]"
          >
            {{ order.label }}
          </button>
        </div>
      </div>
    </div>
    <!-- Tasks -->
    <div class="tasks-section">
      <div class="container">
        <div v-if="loading" class="loading-section">
          <div class="container">
            <div class="loading-spinner">Loading Tasks...</div>
          </div>
        </div>
        <div v-else>
          <div v-if="filteredTasks.length">
            <div
              v-for="(task, index) in this.filteredTasks"
              :key="index"
              class="task-card"
            >
              <!-- <div class="p-4 space-y-3">
                <div class="flex justify-between items-center">
                  <h2 class="text-lg font-semibold">{{ task.task_name }}</h2>
                  <span
                    :class="[
                      'px-2 py-1 rounded-lg text-xs font-medium',
                      task.task_status === 'To Do' ? 'bg-red-200 text-red-800' :
                      task.task_status === 'In Progress' ? 'bg-yellow-200 text-yellow-800' :
                      'bg-green-200 text-green-800'
                    ]"
                  >
                    {{ task.task_status }}
                  </span>
                </div>

                <p class="text-sm text-gray-600">{{ task.task_desc }}</p>

                <div class="grid grid-cols-2 gap-2 text-sm">
                  <p><span class="font-medium">Project:</span> {{ task.proj_ID }}</p>
                  <p><span class="font-medium">Created By:</span> {{ task.created_by }}</p>
                  <p><span class="font-medium">Assigned To:</span> {{ task.assigned_to.join(', ') }}</p>
                  <p><span class="font-medium">Start:</span> {{ task.start_date }}</p>
                  <p><span class="font-medium">End:</span> {{ task.end_date || 'N/A' }}</p>
                  <p>
                    <span class="font-medium">Attachments:</span>
                    {{ task.attachments && task.attachments.length > 0 ? task.attachments.map(a => a.name || a).join(', ') : 'None' }}
                  </p>
                </div>

                <div class="flex justify-end">
                  <button class="px-4 py-2 bg-black text-white rounded-lg">View</button>
                </div>
              </div> -->
              <task-card :task="task" class="mb-0"
              @view-task="handleViewTask"/>
            </div>
          </div>
          <div v-else class="nofound-section">
            No tasks of this status found.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
import TaskCard from '@/components/Projects/TaskCard.vue';
import { ownTasksService } from '../services/myTaskService.js'

export default {
  name: "ViewMyTask",
  components: {
    TaskCard
  },
  data() {
    return {
      tasks: [],
      users: [],
      loading: true,
      error: null,
      filter: "All",
      statuses: ["All", "Not Started", "In Progress", "On Hold", "Completed"],
      sortOrder: "asc",
      sortOrders: [
        { value: "asc", label: "Earliest" },
        { value: "desc", label: "Latest" }
      ]
    };
  },
  created() {
    this.loadTaskData();
  },
  watch: {
    $route() {
      this.loadTaskData();
    }
  },
  methods: {
    async loadTaskData() {
      try {
        this.loading = true;
        this.error = null;

        // Replace with however you store logged-in user
        const userString = sessionStorage.getItem('user');
        const userData = JSON.parse(userString);
        const currentUserId = userData.id;
        console.log("user = ", userData);
        console.log("id = ", currentUserId);

        // Fetch tasks for this user
        this.tasks = await ownTasksService.getTasks(currentUserId);
        console.log("pulled tasks", this.tasks);
        if (!this.tasks.length) {
          this.error = `No tasks found for user ${currentUserId}`;
        }
      } catch (error) {
        console.error("Error loading tasks:", error);
        this.error = error.message;
      } finally {
        this.loading = false;
      }
    },

    goBack() {
      this.$router.push("/projects");
    },

    getTaskStatusClass(status) {
      if (!status) return "status-not-started";
      const statusClasses = {
        "in-progress": "status-progress",
        "to-do": "status-todo",
        completed: "status-completed",
        pending: "status-pending"
      };
      return statusClasses[status] || "status-default";
    },

    formatDate(date) {
      if (!date) return "No date set";
      return new Date(date).toLocaleDateString("en-US", {
        weekday: "long",
        day: "2-digit",
        month: "long",
        year: "numeric"
      });
    },

    formatDateRange(startDate, endDate) {
      if (!startDate || !endDate) return "No dates set";
      const start = new Date(startDate).toLocaleDateString("en-US", {
        day: "2-digit",
        month: "short"
      });
      const end = new Date(endDate).toLocaleDateString("en-US", {
        day: "2-digit",
        month: "short",
        year: "numeric"
      });
      return `${start} - ${end}`;
    },
    handleViewTask(task) {
      const projectId = task.proj_ID || task.projectId; 
      const taskId = task.id || task.task_ID || task.taskId; 
      console.log('Viewing task:', { projectId, taskId, task });
      
      // If task has a project, go to project task view
      if (projectId) {
        this.$router.push(`/projects/${projectId}/tasks/${taskId}`);
      } else {
        // If task has no project, go to standalone task view
        this.$router.push(`/tasks/${taskId}`);
      }
    },
    toggleSortOrder() {
      this.sortOrder = this.sortOrder === "asc" ? "desc" : "asc";
    }
  },
  computed: {
    filteredTasks() {
      let result = this.tasks;

      // Filter by status
      if (this.filter !== "All") {
        result = result.filter(t => t.task_status === this.filter);
      }

      // Sort by end date
      result = result.slice().sort((a, b) => {
        const dateA = new Date(a.end_date);
        const dateB = new Date(b.end_date);

        return this.sortOrder === "asc"
          ? dateA - dateB
          : dateB - dateA;
      });

      return result;
    }
  }
};
</script>

<style scoped>
/* Reuse the styles you pasted earlier */
.crm-container {
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
  font-weight: 800;
  color: #111827;
}
.action-tabs {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}
.tasks-section {
  padding: 2rem 0;
}
.loading-section, .nofound-section {
  padding: 4rem 0;
  text-align: center;
}
.loading-spinner {
  font-size: 1.25rem;
  color: #6b7280;
}
.tab-btn {
  padding: 0.625rem 1.25rem;
  border: 1px solid #374151;
  background: #fff;
  color: #374151;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}
.tab-btn.active {
  background: #111827;
  color: #fff;
  border-color: #111827;
}
.task-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  margin-bottom: 1rem;
}
</style>
