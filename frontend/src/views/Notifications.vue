<template>
  <div class="notifications-page">
    <!-- Header -->
    <header class="page-header">
      <div class="header-container">
        <h1 class="page-title">Notifications</h1>
        <div class="header-actions">
          <button @click="markAllAsRead" class="btn-secondary">
            <span class="btn-icon">✓</span>
            Mark all as read
          </button>
          <button @click="clearAll" class="btn-danger">
            <span class="btn-icon">🗑️</span>
            Clear all
          </button>
        </div>
      </div>
    </header>

    <!-- Filters -->
    <div class="filters-container">
      <div class="filter-tabs">
        <button 
          @click="currentFilter = 'all'" 
          class="filter-tab"
          :class="{ active: currentFilter === 'all' }"
        >
          All ({{ notifications.length }})
        </button>
        <button 
          @click="currentFilter = 'unread'" 
          class="filter-tab"
          :class="{ active: currentFilter === 'unread' }"
        >
          Unread ({{ unreadCount }})
        </button>
        <button 
          @click="currentFilter = 'read'" 
          class="filter-tab"
          :class="{ active: currentFilter === 'read' }"
        >
          Read ({{ readCount }})
        </button>
      </div>
    </div>

    <!-- Notifications List -->
    <main class="page-content">
      <div class="notifications-container">
        <!-- Empty State -->
        <div v-if="filteredNotifications.length === 0" class="empty-state">
          <div class="empty-icon">🔔</div>
          <h2 class="empty-title">No notifications</h2>
          <p class="empty-message">
            {{ currentFilter === 'unread' ? "You're all caught up!" : "No notifications to show" }}
          </p>
        </div>

        <!-- Notification Cards -->
        <div v-else class="notifications-list">
          <div 
            v-for="notification in filteredNotifications" 
            :key="notification.id"
            class="notification-card"
            :class="{ 'unread': !notification.read }"
            @click="handleNotificationClick(notification)"
          >
            <div class="notification-indicator" :class="notification.type"></div>
            
            <div class="notification-content">
              <div class="notification-header">
                <h3 class="notification-title">{{ notification.title }}</h3>
                <span class="notification-time">{{ formatTime(notification.time) }}</span>
              </div>
              
              <p class="notification-message">{{ notification.message }}</p>
              
              <div class="notification-meta">
                <span class="notification-type-badge" :class="notification.type">
                  {{ notification.type }}
                </span>
                <span class="notification-date">{{ formatFullDate(notification.time) }}</span>
              </div>
            </div>

            <div class="notification-actions">
              <button 
                v-if="!notification.read" 
                @click.stop="markAsRead(notification)"
                class="action-btn"
                title="Mark as read"
              >
                ✓
              </button>
              <button 
                @click.stop="deleteNotification(notification)"
                class="action-btn delete"
                title="Delete"
              >
                ✕
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
export default {
  name: 'NotificationsPage',
  data() {
    return {
      currentFilter: 'all',
      notifications: [
        // Sample notifications - replace with real data later
        {
          id: 1,
          icon: '📋',
          type: 'task',
          title: 'New Task Assigned',
          message: 'You have been assigned to "Update Dashboard UI". The task is due on March 15, 2024.',
          time: new Date(Date.now() - 5 * 60000),
          read: false
        },
        {
          id: 2,
          icon: '✅',
          type: 'completion',
          title: 'Task Completed',
          message: 'John Smith completed "Design Landing Page". You can now review the submitted work.',
          time: new Date(Date.now() - 2 * 3600000),
          read: false
        },
        {
          id: 3,
          icon: '⏰',
          type: 'deadline',
          title: 'Deadline Approaching',
          message: 'Task "API Integration" is due in 2 days. Make sure to complete it on time.',
          time: new Date(Date.now() - 24 * 3600000),
          read: true
        },
        {
          id: 4,
          icon: '💬',
          type: 'comment',
          title: 'New Comment',
          message: 'Sarah Johnson commented on "Update Dashboard UI": "Great progress so far! Just need a few minor tweaks."',
          time: new Date(Date.now() - 3 * 24 * 3600000),
          read: true
        },
        {
          id: 5,
          icon: '🎯',
          type: 'mention',
          title: 'You were mentioned',
          message: 'Mike Wilson mentioned you in "Project Planning Meeting Notes".',
          time: new Date(Date.now() - 5 * 24 * 3600000),
          read: true
        },
        {
          id: 6,
          icon: '📎',
          type: 'attachment',
          title: 'New Attachment',
          message: 'Emily Chen added a new attachment to "Design Mockups" task.',
          time: new Date(Date.now() - 7 * 24 * 3600000),
          read: true
        }
      ]
    }
  },
  computed: {
    filteredNotifications() {
      if (this.currentFilter === 'unread') {
        return this.notifications.filter(n => !n.read)
      } else if (this.currentFilter === 'read') {
        return this.notifications.filter(n => n.read)
      }
      return this.notifications
    },
    unreadCount() {
      return this.notifications.filter(n => !n.read).length
    },
    readCount() {
      return this.notifications.filter(n => n.read).length
    }
  },
  methods: {
    markAllAsRead() {
      this.notifications.forEach(n => n.read = true)
    },
    
    clearAll() {
      if (confirm('Are you sure you want to clear all notifications?')) {
        this.notifications = []
      }
    },
    
    markAsRead(notification) {
      notification.read = true
    },
    
    deleteNotification(notification) {
      const index = this.notifications.findIndex(n => n.id === notification.id)
      if (index > -1) {
        this.notifications.splice(index, 1)
      }
    },
    
    handleNotificationClick(notification) {
      if (!notification.read) {
        notification.read = true
      }
      // TODO: Navigate to relevant page based on notification type
      console.log('Notification clicked:', notification)
    },
    
    formatTime(time) {
      const now = new Date()
      const diff = now - time
      const minutes = Math.floor(diff / 60000)
      const hours = Math.floor(diff / 3600000)
      const days = Math.floor(diff / 86400000)
      
      if (minutes < 1) return 'Just now'
      if (minutes < 60) return `${minutes}m ago`
      if (hours < 24) return `${hours}h ago`
      if (days < 7) return `${days}d ago`
      return `${days} days ago`
    },
    
    formatFullDate(time) {
      return time.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  }
}
</script>

<style scoped>
.notifications-page {
  min-height: 100vh;
  background: #f8fafc;
}

/* Header */
.page-header {
  background: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 24px 0;
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn-secondary,
.btn-danger {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.875rem;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

.btn-danger {
  background: #fef2f2;
  color: #dc2626;
}

.btn-danger:hover {
  background: #fee2e2;
}

.btn-icon {
  font-size: 1rem;
}

/* Filters */
.filters-container {
  background: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 0 32px;
}

.filter-tabs {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  gap: 8px;
}

.filter-tab {
  padding: 12px 24px;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  color: #6b7280;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-tab:hover {
  color: #111827;
  background: #f9fafb;
}

.filter-tab.active {
  color: #6366f1;
  border-bottom-color: #6366f1;
}

/* Content */
.page-content {
  padding: 32px;
}

.notifications-container {
  max-width: 1200px;
  margin: 0 auto;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 8px 0;
}

.empty-message {
  font-size: 1rem;
  color: #6b7280;
  margin: 0;
}

/* Notifications List */
.notifications-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.notification-card {
  display: flex;
  gap: 0;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  padding-left: 24px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  overflow: hidden;
}

.notification-card:hover {
  border-color: #d1d5db;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transform: translateY(-1px);
}

.notification-card.unread {
  background: #f0f9ff;
  border-color: #bae6fd;
}

.notification-card.unread:hover {
  background: #e0f2fe;
}

.notification-indicator {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
}

.notification-indicator.task {
  background: #6366f1;
}

.notification-indicator.completion {
  background: #10b981;
}

.notification-indicator.deadline {
  background: #f59e0b;
}

.notification-indicator.comment {
  background: #8b5cf6;
}

.notification-indicator.mention {
  background: #ec4899;
}

.notification-indicator.attachment {
  background: #06b6d4;
}

/* Removed large icon - using colored indicator bar instead */

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 8px;
}

.notification-title {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
  line-height: 1.4;
}

.notification-time {
  font-size: 0.75rem;
  color: #9ca3af;
  white-space: nowrap;
}

.notification-message {
  font-size: 0.875rem;
  color: #6b7280;
  line-height: 1.6;
  margin: 0 0 12px 0;
}

.notification-meta {
  display: flex;
  gap: 12px;
  align-items: center;
}

.notification-type-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 6px;
  text-transform: capitalize;
}

.notification-type-badge.task {
  background: #eef2ff;
  color: #6366f1;
}

.notification-type-badge.completion {
  background: #f0fdf4;
  color: #10b981;
}

.notification-type-badge.deadline {
  background: #fef3c7;
  color: #f59e0b;
}

.notification-type-badge.comment {
  background: #f5f3ff;
  color: #8b5cf6;
}

.notification-type-badge.mention {
  background: #fdf2f8;
  color: #ec4899;
}

.notification-type-badge.attachment {
  background: #ecfeff;
  color: #06b6d4;
}

.notification-date {
  font-size: 0.75rem;
  color: #9ca3af;
}

.notification-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.action-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  border: none;
  border-radius: 6px;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 1rem;
}

.action-btn:hover {
  background: #e5e7eb;
  color: #111827;
}

.action-btn.delete:hover {
  background: #fee2e2;
  color: #dc2626;
}

/* Responsive */
@media (max-width: 768px) {
  .header-container {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .page-content {
    padding: 16px;
  }

  .notification-card {
    padding: 16px;
    padding-left: 20px;
  }

  .notification-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .notification-actions {
    flex-direction: row;
    justify-content: flex-end;
  }
}
</style>

