<template>
  <div class="subtask-item">
    <h3 class="subtask-title">{{ subtask.subTaskName }}</h3>
    
    <div class="subtask-meta">
      <div class="meta-group">
        <span class="meta-label">Status:</span>
        <span class="status-badge" :class="getSubtaskStatusClass(subtask.currentStatus?.statusName)">
          {{ subtask.currentStatus?.statusName || 'Not Started' }}
        </span>
      </div>
      
      <div class="meta-group">
        <span class="meta-label">Due Date:</span>
        <span class="meta-value">📅 {{ formatDate(subtask.dueDate) }}</span>
      </div>
      
      <div class="meta-group"> 
        <span class="meta-label">Assigned To:</span>
        <div class="assignee-avatars">
          <UserAvatar
            v-for="assignee in subtask.assignees"
            :key="assignee.id"
            :user="assignee"
            type="assignee"
          />
        </div>
      </div>
      
      <div class="meta-group">
        <span class="meta-label">Approver:</span>
        <div class="assignee-avatars">
          <UserAvatar
            v-if="subtask.approver"
            :user="subtask.approver"
            type="approver"
          />
        </div>
      </div>
      
      <div class="meta-group">
        <span class="meta-label">Assignee:</span>
        <div class="assignee-avatars">
          <UserAvatar
            v-if="subtask.assignee"
            :user="subtask.assignee"
            type="assignee"
          />
        </div>
      </div>
      
      <button class="view-btn" @click="$emit('view-subtask', subtask)">View</button>
    </div>
  </div>
</template>

<script>
import UserAvatar from './UserAvatar.vue'

export default {
  name: 'SubtaskItem',
  components: {
    UserAvatar
  },
  props: {
    subtask: {
      type: Object,
      required: true
    }
  },
  emits: ['view-subtask'],
  methods: {
    getSubtaskStatusClass(status) {
      if (!status) return 'status-not-started';
      const statusClasses = {
        'In progress': 'status-progress',
        'To Do': 'status-todo',
        'Completed': 'status-completed',
        'Pending': 'status-pending'
      };
      return statusClasses[status] || 'status-default';
    },
    formatDate(date) {
      if (!date) return 'No due date';
      return new Date(date).toLocaleDateString('en-US', { 
        day: '2-digit', 
        month: 'short', 
        year: 'numeric' 
      });
    }
  }
}
</script>

<style scoped>
.subtask-item {
  background: #f9fafb;
  border: 1px solid #f3f4f6;
  border-radius: 8px;
  padding: 1.25rem;
  margin-bottom: 1rem;
}

.subtask-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 1rem 0;
}

.subtask-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  align-items: center;
}

.meta-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.meta-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.meta-value {
  font-size: 0.875rem;
  color: #111827;
}

.status-badge {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-weight: 500;
  display: inline-block;
}

.status-badge.status-progress {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.status-todo {
  background: #fecaca;
  color: #991b1b;
}

.status-badge.status-completed {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.status-pending {
  background: #fed7aa;
  color: #9a3412;
}

.status-badge.status-not-started {
  background: #f3f4f6;
  color: #6b7280;
}

.assignee-avatars {
  display: flex;
  gap: 0.5rem;
}

.view-btn {
  background: #111827;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  align-self: start;
  transition: all 0.2s ease;
}

.view-btn:hover {
  background: #374151;
}

@media (max-width: 768px) {
  .subtask-meta {
    grid-template-columns: 1fr;
  }
}
</style>