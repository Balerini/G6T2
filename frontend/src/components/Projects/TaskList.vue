<template>
  <div class="task-list">
    <div v-if="tasks.length === 0" class="empty-state">
      <p>No tasks found</p>
    </div>
    
    <div v-else class="tasks-grid">
      <TaskCard
        v-for="task in tasks"
        :key="task.task_ID || task.id"
        :task="task"
        :users="users"
        @view-task="$emit('view-task', $event)"
      />
    </div>
  </div>
</template>

<script>
import TaskCard from './TaskCard.vue'

export default {
  name: 'TaskList',
  components: {
    TaskCard
  },
  props: {
    tasks: {
      type: Array,
      default: () => []
    },
    users: {
      type: Array,
      default: () => []
    }
  },
  emits: ['view-task']
}
</script>

<style scoped>
.task-list {
  width: 100%;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #6b7280;
}

.tasks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1.5rem;
}

@media (max-width: 768px) {
  .tasks-grid {
    grid-template-columns: 1fr;
  }
}
</style>
