<template>
  <div class="task-card">
    <!-- Task Header -->
    <div class="task-header">
      <div class="task-status-indicator" :class="getStatusClass(task.status)"></div>
      <h2 class="task-title">{{ task.taskName }}</h2>
      <button class="edit-btn" @click="$emit('edit-task', task)">✏️</button>
    </div>

    <!-- Subtasks -->
    <div class="subtasks-container">
      <SubtaskItem
        v-for="subtask in task.subtasks"
        :key="subtask.subTaskId"
        :subtask="subtask"
        @view-subtask="$emit('view-subtask', $event)"
      />
      
      <button class="add-subtask-btn" @click="$emit('add-subtask', task)">
        + Add
      </button>
    </div>
  </div>
</template>

<script>
import SubtaskItem from './SubTaskCard.vue'

export default {
  name: 'TaskCard',
  components: {
    SubtaskItem
  },
  props: {
    task: {
      type: Object,
      required: true
    }
  },
  emits: ['edit-task', 'view-subtask', 'add-subtask'],
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
.task-card {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.task-header {
  display: flex;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #f3f4f6;
  gap: 1rem;
}

.task-status-indicator {
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

.task-title {
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

.subtasks-container {
  padding: 1.5rem;
}

.add-subtask-btn {
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

.add-subtask-btn:hover {
  background: #f9fafb;
  border-color: #374151;
  color: #374151;
}

@media (max-width: 768px) {
  .task-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
  
  .task-title {
    font-size: 1.25rem;
  }
}
</style>