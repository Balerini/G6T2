<template>
  <div class="project-list-container">
    <!-- Project List -->
    <div class="project-list">
      <ProjectCard v-for="project in projects" :key="project.id" :project="project" :users="users"
        @edit-project="$emit('edit-project', $event)" @view-task="$emit('view-task', $event)"
        @add-task="$emit('add-task', $event)" />
    </div>
  </div>
</template>

<script>
import ProjectCard from './ProjectCard.vue'

export default {
  name: 'ProjectList',
  components: {
    ProjectCard
  },
  props: {
    projects: {
      type: Array,
      required: true
    },
    users: {
      type: Array,
      default: () => []
    }
  },
  emits: ['edit-project', 'view-task', 'add-task']
}
</script>

<style scoped>
.project-list-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.project-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
</style>