<template>
  <div 
    class="assignee-avatar" 
    :class="{ 
      approver: type === 'approver', 
      assignee: type === 'assignee',
      [`color-${getColorIndex(user.id)}`]: true
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
    },
    getColorIndex(userId) {
      // Generate a consistent color index based on user ID
      if (!userId) return 0;
      const hash = userId.toString().split('').reduce((a, b) => {
        a = ((a << 5) - a) + b.charCodeAt(0);
        return a & a;
      }, 0);
      return Math.abs(hash) % 6; // 6 different colors
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
  color: #ffffff;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.assignee-avatar:hover {
  transform: scale(1.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

/* Color variations */
.assignee-avatar.color-0 {
  background: #6366f1;
}

.assignee-avatar.color-1 {
  background: #8b5cf6;
}

.assignee-avatar.color-2 {
  background: #06b6d4;
}

.assignee-avatar.color-3 {
  background: #10b981;
}

.assignee-avatar.color-4 {
  background: #f59e0b;
}

.assignee-avatar.color-5 {
  background: #ef4444;
}

.assignee-avatar.approver {
  background: #ddd6fe;
  color: #5b21b6;
}

.assignee-avatar.assignee {
  /* Use the color classes instead of fixed color */
}
</style>