<template>
  <div 
    class="assignee-avatar" 
    :class="{ 
      approver: type === 'approver', 
      assignee: type === 'assignee' 
    }"
    :title="user.name"
  >
    {{ user.initials || getInitials(user.name) }}
  </div>
</template>

<script>
export default {
  name: 'UserAvatar',
  props: {
    user: {
      type: Object,
      required: true
    },
    type: {
      type: String,
      default: 'default',
      validator: (value) => ['default', 'approver', 'assignee'].includes(value)
    }
  },
  methods: {
    getInitials(name) {
      if (!name) return 'U';
      return name
        .split(' ')
        .map(word => word.charAt(0))
        .join('')
        .substring(0, 2)
        .toUpperCase();
    }
  }
}
</script>

<style scoped>
.assignee-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s ease;
}

.assignee-avatar:hover {
  transform: scale(1.1);
}

.assignee-avatar.approver {
  background: #ddd6fe;
  color: #5b21b6;
}

.assignee-avatar.assignee {
  background: #fef3c7;
  color: #92400e;
}
</style>