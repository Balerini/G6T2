<template>
  <div class="team-schedule-container">
    <div v-if="loading">
      <p>Loading team schedule...</p>
    </div>

    <div v-else>
      <g-gantt-chart
        chart-start="2025-01-01"
        chart-end="2025-12-31"
        precision="day"
        bar-start="start"
        bar-end="end"
      >
        <g-gantt-row
          v-for="(member, index) in teamMembers"
          :key="index"
          :label="member.name"
          :bars="member.bars"
        />
      </g-gantt-chart>
    </div>
  </div>
</template>

<script>
import { onMounted, ref } from "vue";
import { projectService } from "../services/projectService";

export default {
  name: "ViewProjectTeamSchedule",
  setup() {
    const loading = ref(true);
    const teamMembers = ref([]);

    onMounted(async () => {
      try {
        const data = await projectService.getProjectById();
        teamMembers.value = data.map((member) => ({
          name: member.name,
          bars: member.tasks.map((task) => ({
            start: task.startDate,
            end: task.endDate,
            ganttBarConfig: {
              id: task.id,
              label: task.taskName,
              style: { backgroundColor: "#42b983" },
            },
          })),
        }));
      } catch (err) {
        console.error("Failed to load schedule:", err);
      } finally {
        loading.value = false;
      }
    });

    return { loading, teamMembers };
  },
};
</script>

<style scoped>
.team-schedule-container {
  padding: 1.5rem;
  background-color: #f9fafb;
  border-radius: 12px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}

p {
  text-align: center;
  color: #666;
}
</style>
