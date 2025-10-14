<template>
  <div>
    <div v-if="loading">Loading team schedule...</div>
    <div v-else-if="error">Error: {{ error }}</div>
    <div v-else-if="teamSchedule">
      <h3>Team Schedule</h3>
      <div v-if="teamSchedule.collaborators && teamSchedule.collaborators.length > 0">
        <div v-for="(member, index) in teamSchedule.collaborators" :key="index">
          <h4>{{ member.name }} ({{ member.email }})</h4>
          <p>Completed: {{ member.completed_tasks }} | In Progress: {{ member.in_progress_tasks }} | Not Started: {{ member.not_started_tasks }} | Overdue: {{ member.overdue_tasks }}</p>
          
          <div v-if="member.tasks && member.tasks.length > 0">
            <div v-for="(task, taskIndex) in member.tasks" :key="taskIndex">
              <p>
                <strong>{{ task.task_name }}</strong><br>
                Start: {{ formatDate(task.start_date) }} | 
                End: {{ formatDate(task.end_date) }}<br>
                Status: {{ task.task_status }} | 
                Priority: {{ task.priority_level }} | 
                Completion: {{ task.completion_percentage }}%
                <span v-if="task.is_overdue"> (OVERDUE)</span>
              </p>
            </div>
          </div>
          <div v-else>
            <p>No tasks assigned</p>
          </div>
          <hr>
        </div>
      </div>
      <div v-else>
        <p>No collaborators found</p>
      </div>
    </div>
  </div>
</template>

<script>
import { projectService } from '../services/projectService';

export default {
  name: 'ViewProjectTeamSchedule',
  
  props: {
    projectId: {
      type: [String, Number],
      required: true
    }
  },

  data() {
    return {
      teamSchedule: null,
      loading: false,
      error: null
    }
  },

  mounted() {
    this.fetchTeamSchedule();
  },

  watch: {
    projectId(newVal) {
      if (newVal) {
        this.fetchTeamSchedule();
      }
    }
  },

  methods: {
    async fetchTeamSchedule() {
      this.loading = true;
      this.error = null;
      
      try {
        const data = await projectService.getProjectById(this.projectId);
        this.teamSchedule = data;
        console.log('Team schedule data:', data);
      } catch (err) {
        this.error = err.message;
        console.error('Failed to fetch team schedule:', err);
      } finally {
        this.loading = false;
      }
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleDateString();
    }
  }
}
</script>