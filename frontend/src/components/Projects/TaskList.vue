<template>
  <div class="task-list">
    <TaskCard
      v-for="task in tasks"
      :key="task.taskId"
      :task="task"
      @edit-task="$emit('edit-task', $event)"
      @view-subtask="$emit('view-subtask', $event)"
      @add-subtask="$emit('add-subtask', $event)"
    />
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
      required: true
    }
  },
  emits: ['edit-task', 'view-subtask', 'add-subtask']
}
</script>

<style scoped>
.task-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
</style>