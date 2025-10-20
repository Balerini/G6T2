<template>
  <div class="project-list">
    <ProjectCard v-for="project in projects" :key="project.id" :project="project" :users="users"
      :showCompletedProjects="showCompletedProjects" @view-task="$emit('view-task', $event)"
      @add-task="$emit('add-task', $event)" />
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
    },
    showCompletedProjects: {
      type: Boolean,
      default: false
    }
  },
  emits: ['view-task', 'add-task']
}
</script>

<style scoped>
.project-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
</style>