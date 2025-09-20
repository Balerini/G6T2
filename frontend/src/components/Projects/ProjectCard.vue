<template>
  <div class="project-card">
    <!-- Project Header -->
    <div class="project-header">
      <div class="project-status-indicator" :class="getStatusClass(project.status)"></div>
      <h2 class="project-title">{{ project.projectName }}</h2>
      <button class="edit-btn" @click="$emit('edit-project', project)">✏️</button>
    </div>

    <!-- Tasks -->
    <div class="tasks-container">
      <TaskItem
        v-for="task in project.tasks"
        :key="task.taskId"
        :task="task"
        @view-task="$emit('view-task', $event)"
      />
      
      <button class="add-task-btn" @click="$emit('add-task', project)">
        + Add
      </button>
    </div>
  </div>
</template>

<script>
import TaskItem from './TaskCard.vue'

export default {
  name: 'ProjectCard',
  components: {
    TaskItem
  },
  props: {
    project: {
      type: Object,
      required: true
    }
  },
  emits: ['edit-project', 'view-task', 'add-task'],
  methods: {
    getStatusClass(status) {
      const statusClasses = {
        'in-progress': 'status-progress',
        'to-do': 'status-todo',
        'completed': 'status-completed',
        'pending': 'status-pending'
      };
      return statusClasses[status] || 'status-default';
    }
  }
}
</script>

<style scoped>
.project-card {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.project-header {
  display: flex;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #f3f4f6;
  gap: 1rem;
}

.project-status-indicator {
  width: 4px;
  height: 40px;
  border-radius: 2px;
}

.status-progress {
  background: #fbbf24;
}

.status-todo {
  background: #ef4444;
}

.status-completed {
  background: #10b981;
}

.status-pending {
  background: #f59e0b;
}

.project-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
  flex: 1;
}

.edit-btn {
  background: #111827;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 0.5rem;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s ease;
}

.edit-btn:hover {
  background: #374151;
}

.tasks-container {
  padding: 1.5rem;
}

.add-task-btn {
  background: transparent;
  color: #111827;
  border: 1px dashed #111827;
  border-radius: 6px;
  padding: 0.75rem 1rem;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  width: 100%;
  transition: all 0.2s ease;
}

.add-task-btn:hover {
  background: #f9fafb;
  border-color: #374151;
  color: #374151;
}

@media (max-width: 768px) {
  .project-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
  
  .project-title {
    font-size: 1.25rem;
  }
}
</style>