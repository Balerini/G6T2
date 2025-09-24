<template>
  <div class="task-item">
    <div class="task-title-row">
      <h3 class="task-title">{{ task.task_name }}</h3>
      <button class="edit-btn" @click.stop="$emit('edit-task', task)" title="Edit Task" aria-label="Edit Task">
        ✏️
      </button>
    </div>

    <div class="task-meta">
      <div class="meta-group">
        <span class="meta-label">Status:</span>
        <span class="status-badge" :class="getTaskStatusClass(task.task_status)">
          {{ formatStatus(task.task_status) || 'Not Started' }}
        </span>
      </div>

      <div class="meta-group">
        <span class="meta-label">Due Date:</span>
        <span class="meta-value">📅 {{ formatDate(task.end_date) }}</span>
      </div>

      <div class="meta-group">
        <span class="meta-label">Created By:</span>
        <span class="meta-value">{{ getCreatorName(task.created_by) }}</span>
      </div>

      <div class="meta-group">
        <span class="meta-label">Assigned To:</span>
        <div class="assignee-list">
          <UserAvatar v-for="userId in task.assigned_to" :key="userId" :user="getUser(userId)" type="assignee" />
        </div>
      </div>

      <!-- <div class="meta-group" v-if="task.attachments && task.attachments.length > 0">
        <span class="meta-label">Attachments:</span>
        <div class="attachments-list">
          <span class="attachment-count">{{ task.attachments.length }} file(s)</span>
        </div>
      </div> -->

      <button class="view-btn" @click="$emit('view-task', task)">View Details</button>
    </div>
  </div>
</template>

<script>
import UserAvatar from './UserAvatar.vue'

export default {
  name: 'TaskItem',
  components: {
    UserAvatar
  },
  props: {
    task: {
      type: Object,
      required: true
    },
    users: {
      type: Array,
      default: () => []
    }
  },
  emits: ['view-task', 'edit-task'],
  methods: {
    getTaskStatusClass(status) {
      const statusClasses = {
        'Not Started': 'status-todo',
        'In Progress': 'status-progress',
        'On Hold': 'status-pending',
        'Completed': 'status-completed',
        'Cancelled': 'status-pending'
      };
      const resultClass = statusClasses[status] || 'status-default';
      return resultClass;
    },

    formatStatus(status) {
      return status?.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'Not Started';
    },
    formatDate(date) {
      if (!date) return 'No due date';
      return new Date(date).toLocaleDateString('en-US', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
      });
    },
    getUser(userId) {
      // First try to find by document ID (from backend API)
      let user = this.users.find(user => String(user.id) === String(userId));

      // Fallback to user_ID field if it exists
      if (!user) {
        user = this.users.find(user => String(user.user_ID) === String(userId));
      }

      if (user) {
        return {
          ...user,
          id: user.id || user.user_ID,
          initials: this.getInitials(user.name)
        };
      }

      // console.log(`User not found for task assignee ID: ${userId}`);
      // console.log('Available users:', this.users.map(u => ({ id: u.id, user_ID: u.user_ID, name: u.name })));
      return {
        id: userId,
        name: 'Unknown User',
        initials: 'UU'
      };
    },
    getCreatorName(userId) {
      // First try to find by document ID (from backend API)  
      let user = this.users.find(u => String(u.id) === String(userId));

      // Fallback to user_ID field if it exists
      if (!user) {
        user = this.users.find(u => String(u.user_ID) === String(userId));
      }

      const name = user ? user.name : 'Unknown User';
      return name;
    },
    getInitials(name) {
      if (!name) return 'U';
      return name
        .split(' ')
        .map(word => word.charAt(0))
        .join('')
        .substring(0, 2)
        .toUpperCase();
    },
    handleViewTask() {
      console.log('TaskCard emitting task:', {
        id: this.task.id,
        task_ID: this.task.task_ID,
        name: this.task.task_name
      });
      this.$emit('view-task', this.task);
    }
  }
}
</script>

<style scoped>
.task-item {
  background: #f9fafb;
  border: 1px solid #f3f4f6;
  border-radius: 8px;
  padding: 1.25rem;
  margin-bottom: 1rem;
}

.task-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.task-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 1rem 0;
}

.edit-btn {
  background: #111827;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.edit-btn:hover { background: #374151; }

.task-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  align-items: center;
  margin-top: 0.5rem;
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

.assignee-list {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.attachments-list {
  font-size: 0.875rem;
}

.attachment-count {
  color: #6b7280;
  font-style: italic;
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

.status-badge.status-default {
  background: #f3f4f6;
  color: #374151;
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
  .task-meta {
    grid-template-columns: 1fr;
  }
}
</style>