<template>
  <div class="crm-container">
    <div class="container">
      <div class="header-section">
        <div class="header-content">
          <h1 class="hero-title">Tasks</h1>
        </div>

        <!-- Filter Tabs -->
        <div class="action-tabs mb-4">
          <button
            v-for="status in statuses"
            :key="status"
            @click="filter = status"
            :class="['tab-btn', filter === status ? 'active' : '']"
          >
            {{ status }}
          </button>
        </div>

        <!-- Project Filter -->
        <div class="action-tabs mb-4">
          <button
            v-for="project in projectList"
            :key="project"
            @click="projectFilter = project"
            :class="['tab-btn', projectFilter === project ? 'active' : '']"
          >
            {{ project }}
          </button>
        </div>
      </div>

      <!-- Tasks -->
      <div v-for="(task, index) in filteredTasks" :key="index" class="task-card">
        <div class="task-card-body">
          <div class="task-header">
            <h2 class="task-title">{{ task.name }}</h2>
            <span
              :class="[
                'status-badge',
                task.status === 'To Do' ? 'status-todo' :
                task.status === 'In Progress' ? 'status-progress' :
                'status-done'
              ]"
            >
              {{ task.status }}
            </span>
          </div>

          <p class="task-desc">{{ task.desc }}</p>

          <div class="task-details">
            <p><span class="label">Project:</span> {{ task.project }}</p>
            <p><span class="label">Created By:</span> {{ task.createdBy }}</p>
            <p><span class="label">Collaborators:</span> {{ task.collaborators.join(', ') }}</p>
            <p><span class="label">Approver:</span> {{ task.approver }}</p>
            <p><span class="label">Assignee:</span> {{ task.assignee }}</p>
            <p><span class="label">Start:</span> {{ task.startDate }}</p>
            <p><span class="label">End:</span> {{ task.endDate }}</p>
            <p>
              <span class="label">Attachments:</span>
              {{ task.attachments.length > 0 ? task.attachments.join(', ') : 'None' }}
            </p>
          </div>

          <div class="task-footer">
            <button class="view-btn">View</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";

const tasks = ref([
  {
    project: "Board Meeting",
    name: "Board Meeting Proposal",
    desc: "Prepare proposal for Q4 board meeting.",
    createdBy: "Ang Koo Kueh",
    collaborators: ["Turtle Tan"],
    approver: "Turtle Tan",
    assignee: "Jake Lee",
    attachments: ["proposal.docx"],
    status: "In Progress",
    startDate: "2024-10-10",
    endDate: "2024-10-19",
  },
  {
    project: "Sales Revenue 2022",
    name: "Analyse Sales",
    desc: "Analyse Q4 sales performance and trends.",
    createdBy: "Ang Koo Kueh",
    collaborators: ["Turtle Tan"],
    approver: "Turtle Tan",
    assignee: "Jake Lee",
    attachments: [],
    status: "To Do",
    startDate: "2024-11-01",
    endDate: "2024-11-29",
  },
  {
    project: "Sales Revenue 2022",
    name: "Revenue Forecasting",
    desc: "Create revenue forecast for next quarter.",
    createdBy: "Ang Koo Kueh",
    collaborators: ["Turtle Tan"],
    approver: "Turtle Tan",
    assignee: "Jake Lee",
    attachments: ["forecast.xlsx"],
    status: "Done",
    startDate: "2024-09-05",
    endDate: "2024-09-20",
  },
]);

const statuses = ["All", "To Do", "In Progress", "Done"];
const filter = ref("All");
const projectFilter = ref("All Projects");

const projectList = computed(() => ["All Projects", ...new Set(tasks.value.map(t => t.project))]);

const filteredTasks = computed(() => {
  return tasks.value.filter(task => {
    const statusMatch = filter.value === "All" || task.status === filter.value;
    const projectMatch = projectFilter.value === "All Projects" || task.project === projectFilter.value;
    return statusMatch && projectMatch;
  });
});
</script>

<style scoped>
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

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.hero-title {
  font-size: 2.25rem;
  line-height: 1.2;
  font-weight: 800;
  color: #111827;
  margin-bottom: 0.5rem;
}

.action-tabs {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
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
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 1.5rem;
}

.task-card-body {
  padding: 1.5rem;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.task-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
}

.task-desc {
  font-size: 0.875rem;
  color: #4b5563;
  margin-bottom: 1rem;
}

.task-details {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem 1rem;
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.label {
  font-weight: 500;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.status-todo {
  background-color: #fecaca;
  color: #991b1b;
}

.status-progress {
  background-color: #fef3c7;
  color: #92400e;
}

.status-done {
  background-color: #bbf7d0;
  color: #065f46;
}

.task-footer {
  display: flex;
  justify-content: flex-end;
}

.view-btn {
  padding: 0.5rem 1rem;
  background: #111827;
  color: #fff;
  border-radius: 8px;
  font-weight: 500;
  transition: background 0.2s ease;
}

.view-btn:hover {
  background: #374151;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .action-tabs {
    flex-direction: column;
  }

  .task-details {
    grid-template-columns: 1fr;
  }
}
</style>
