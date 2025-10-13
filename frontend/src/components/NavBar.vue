<template>
  <nav class="navbar">
    <div class="container navbar-container">
      <router-link to="/" class="navbar-logo">
        Task Quest
      </router-link>

      <div class="navbar-right">
        <router-link :to="dashboardLink" class="navbar-link"
          exact-active-class="router-link-active">Dashboard</router-link>
        <router-link to="/projects" class="navbar-link">Projects</router-link>
        <a href="/my-schedule" class="navbar-link" @click.prevent="navigateToSchedule">My Schedule</a>

        <!-- Notification Bell -->
        <div class="notification-wrapper" @click="toggleNotifications">
          <div class="notification-bell">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
              <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
            </svg>
            <span v-if="unreadCount > 0" class="notification-badge">{{ unreadCount > 9 ? '9+' : unreadCount }}</span>
          </div>
        </div>

        <!-- User Profile Icon -->
        <div class="profile-wrapper" @click="toggleProfileMenu">
          <div class="profile-avatar">
            {{ userInitials }}
          </div>
        </div>

        <button @click="logout" class="logout-btn">Logout</button>
      </div>

      <!-- Profile Dropdown -->
      <div v-if="showProfileMenu" class="profile-dropdown">
        <div class="profile-header">
          <div class="profile-avatar-large">
            {{ userInitials }}
          </div>
          <div class="profile-info">
            <p class="profile-name">{{ currentUser?.name || 'User' }}</p>
            <p class="profile-email">{{ currentUser?.email || '' }}</p>
          </div>
        </div>

        <div class="profile-divider"></div>

        <div class="profile-details-section">
          <div class="profile-detail-item">
            <span class="detail-label">Division</span>
            <span class="detail-value">{{ currentUser?.division_name || 'N/A' }}</span>
          </div>
          <div class="profile-detail-item">
            <span class="detail-label">Role</span>
            <span class="detail-value">{{ currentUser?.role_name || 'N/A' }}</span>
          </div>
        </div>
      </div>

      <!-- Notification Dropdown -->
      <div v-if="showNotifications" class="notification-dropdown">
        <div class="notification-header">
          <h3>Notifications</h3>
          <button @click="markAllAsRead" class="mark-read-btn">Mark all as read</button>
        </div>

        <div class="notification-list">
          <div v-if="recentNotifications.length === 0" class="no-notifications">
            <p>🔔 No notifications</p>
          </div>

          <div v-for="notification in recentNotifications" :key="notification.id" class="notification-item"
            :class="{ 'unread': !notification.read }" @click="handleNotificationClick(notification)">
            <div class="notification-content">
              <p class="notification-title">{{ notification.title }}</p>
              <p class="notification-message">{{ notification.message }}</p>
              <span class="notification-time">{{ formatTime(notification.time) }}</span>
            </div>
            <div v-if="!notification.read" class="unread-dot"></div>
          </div>
        </div>

        <!-- View All Button -->
        <div class="notification-footer">
          <router-link to="/notifications" class="view-all-btn" @click="showNotifications = false">
            View all notifications
          </router-link>
        </div>
      </div>

    </div>
  </nav>


</template>

<script>
import authService from '@/services/auth'
import notificationService from '@/services/notificationService'

export default {
  name: 'NavBar',
  data() {
    return {
      showNotifications: false,
      showProfileMenu: false,
      notifications: [],
      loadingNotifications: false
    }
  },
  computed: {
    currentUser() {
      return authService.getCurrentUser()
    },
    userInitials() {
      const user = this.currentUser
      if (!user || !user.name) return 'U'

      const nameParts = user.name.trim().split(' ')
      if (nameParts.length === 1) {
        return nameParts[0].charAt(0).toUpperCase()
      }
      return (nameParts[0].charAt(0) + nameParts[nameParts.length - 1].charAt(0)).toUpperCase()
    },
    unreadCount() {
      return this.notifications.filter(n => !n.read).length
    },
    recentNotifications() {
      // Show only the 5 most recent notifications in dropdown
      return this.notifications.slice(0, 5)
    },
    dashboardLink() {
      // Get current user
      const user = authService.getCurrentUser()

      // For staff (role_num = 4), show My Dashboard view
      // For managers/directors (role_num < 4), show Team Tasks view
      if (user && user.role_num === 4) {
        return '/?view=mydashboard'
      } else {
        return '/?view=team'
      }
    }
  },
  methods: {
    navigateToSchedule() {
      console.log('Navigating to My Schedule');
      this.$router.push('/my-schedule').catch(err => {
        console.error('Router navigation to schedule failed:', err);
        window.location.href = '/my-schedule';
      });
    },

    logout() {
      try {
        authService.logout();
        this.$router.push('/login').catch(err => {
          // Handle navigation error (e.g., already on login page)
          console.log('Navigation after logout:', err);
        });
      } catch (error) {
        console.error('Error during logout:', error);
        // Force redirect to login even if there's an error
        window.location.href = '/login';
      }
    },

    async loadNotifications() {
      try {
        const currentUser = authService.getCurrentUser()
        if (!currentUser || !currentUser.id) {
          console.log('No user logged in')
          return
        }

        this.loadingNotifications = true
        const notifications = await notificationService.getNotifications(currentUser.id)

        // Map backend data to frontend format
        this.notifications = notifications.map(n => ({
          id: n.id,
          icon: this.getNotificationIcon(n.type),
          title: n.title,
          message: n.message,
          time: new Date(n.timestamp),
          read: n.read,
          type: n.type,
          task_id: n.task_id,
          project_id: n.project_id
        }))

        console.log('Loaded notifications:', this.notifications.length)
      } catch (error) {
        console.error('Error loading notifications:', error)
      } finally {
        this.loadingNotifications = false
      }
    },

    toggleNotifications() {
      this.showNotifications = !this.showNotifications
      this.showProfileMenu = false // Close profile menu

      // Load notifications when opening dropdown
      if (this.showNotifications) {
        this.loadNotifications()
      }
    },

    toggleProfileMenu() {
      this.showProfileMenu = !this.showProfileMenu
      this.showNotifications = false // Close notifications
    },

    async markAllAsRead() {
      try {
        const currentUser = authService.getCurrentUser()
        if (!currentUser || !currentUser.id) return

        await notificationService.markAllAsRead(currentUser.id)
        this.notifications.forEach(n => n.read = true)
      } catch (error) {
        console.error('Error marking all as read:', error)
      }
    },

    async handleNotificationClick(notification) {
      try {
        // Mark as read
        await notificationService.markAsRead(notification.id)
        notification.read = true

        // Close dropdown
        this.showNotifications = false

        // Navigate to task details
        if (notification.task_id && notification.project_id) {
          // Task with project
          this.$router.push(`/projects/${notification.project_id}/tasks/${notification.task_id}`)
        } else if (notification.task_id) {
          // Standalone task (no project)
          this.$router.push(`/tasks/${notification.task_id}`)
        }

        console.log('Navigating to task:', notification.task_id)
      } catch (error) {
        console.error('Error handling notification click:', error)
      }
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
      return time.toLocaleDateString()
    },

    getNotificationIcon(type) {
      const iconMap = {
        'task_assigned': '📋',
        'deadline': '⏰',
        'task_updated': '✏️',
        'completion': '✅',
        'comment': '💬',
        'mention': '🎯',
        'attachment': '📎'
      }
      return iconMap[type] || '📋'
    },

    // Event handlers for notification updates
    handleNotificationDeleted({ notificationId }) {
      console.log('NavBar: Notification deleted event received:', notificationId)
      const index = this.notifications.findIndex(n => n.id === notificationId)
      if (index > -1) {
        this.notifications.splice(index, 1)
      }
    },

    handleNotificationMarkedRead({ notificationId }) {
      console.log('NavBar: Notification marked read event received:', notificationId)
      const notification = this.notifications.find(n => n.id === notificationId)
      if (notification) {
        notification.read = true
      }
    },

    handleAllMarkedRead() {
      console.log('NavBar: All notifications marked read event received')
      this.notifications.forEach(n => n.read = true)
    },

    handleNotificationsRefresh() {
      console.log('NavBar: Notification refresh triggered')
      this.loadNotifications()
    }
  },
  mounted() {
    // Load notifications on mount
    this.loadNotifications()

    // Set up periodic refresh (every 10 seconds for faster updates)
    this.notificationInterval = setInterval(() => {
      this.loadNotifications()
    }, 10000)

    // Subscribe to notification events
    notificationService.on('notification-deleted', this.handleNotificationDeleted)
    notificationService.on('notification-marked-read', this.handleNotificationMarkedRead)
    notificationService.on('notifications-marked-all-read', this.handleAllMarkedRead)
    notificationService.on('notifications-refresh', this.handleNotificationsRefresh)

    // Close dropdowns when clicking outside
    document.addEventListener('click', (e) => {
      if (!this.$el.contains(e.target)) {
        this.showNotifications = false
        this.showProfileMenu = false
      }
    })
  },
  beforeUnmount() {
    // Clean up interval
    if (this.notificationInterval) {
      clearInterval(this.notificationInterval)
    }

    // Unsubscribe from notification events
    notificationService.off('notification-deleted', this.handleNotificationDeleted)
    notificationService.off('notification-marked-read', this.handleNotificationMarkedRead)
    notificationService.off('notifications-marked-all-read', this.handleAllMarkedRead)
    notificationService.off('notifications-refresh', this.handleNotificationsRefresh)
  }
}
</script>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 50;
  background-color: rgba(255, 255, 255, 0.85);
  backdrop-filter: saturate(180%) blur(10px);
  -webkit-backdrop-filter: saturate(180%) blur(10px);
  border-bottom: 1px solid #e5e7eb;
}

.navbar-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.navbar-actions {
  display: flex;
  align-items: center;
}


.navbar-logo {
  font-size: 1.1rem;
  font-weight: 800;
  letter-spacing: 0.2px;
  color: #111827;
}

.navbar-links {
  display: flex;
  gap: 1rem;
}

.navbar-link {
  color: #4b5563;
  font-weight: 600;
  padding: 0.4rem 0.6rem;
  border-radius: 8px;
  transition: color 0.2s, background-color 0.2s;
  text-decoration: none;
}

.logout-btn {
  background: #dc2626;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  font-size: 0.875rem;
}

/* Notification Bell */
.notification-wrapper {
  position: relative;
  cursor: pointer;
}

.notification-bell {
  position: relative;
  padding: 0.5rem;
  color: #4b5563;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.notification-bell:hover {
  background: #f3f4f6;
  color: #111827;
}

.notification-badge {
  position: absolute;
  top: 2px;
  right: 2px;
  background: #ef4444;
  color: white;
  font-size: 0.625rem;
  font-weight: 700;
  padding: 2px 5px;
  border-radius: 10px;
  min-width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.9);
}

/* Profile Avatar */
.profile-wrapper {
  position: relative;
  cursor: pointer;
}

.profile-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.875rem;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.profile-avatar:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

/* Profile Dropdown */
.profile-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 20px;
  width: 280px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  border: 1px solid #e5e7eb;
  z-index: 1000;
  overflow: hidden;
  animation: slideDown 0.2s ease;
}

.profile-header {
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.profile-avatar-large {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.25);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.125rem;
  flex-shrink: 0;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.profile-info {
  flex: 1;
  min-width: 0;
}

.profile-name {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  color: white;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.profile-email {
  margin: 2px 0 0 0;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.9);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.profile-divider {
  height: 1px;
  background: #e5e7eb;
}

.profile-details-section {
  padding: 16px 20px;
}

.profile-detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
}

.profile-detail-item:not(:last-child) {
  border-bottom: 1px solid #f3f4f6;
}

.detail-label {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.detail-value {
  font-size: 0.875rem;
  color: #111827;
  font-weight: 600;
}

/* Notification Dropdown */
.notification-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 80px;
  width: 380px;
  max-height: 500px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  border: 1px solid #e5e7eb;
  z-index: 1000;
  overflow: hidden;
  animation: slideDown 0.2s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.notification-header {
  padding: 16px 20px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.notification-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  color: #111827;
}

.mark-read-btn {
  background: none;
  border: none;
  color: #6366f1;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.2s;
}

.mark-read-btn:hover {
  background: #f0f0ff;
}

.notification-list {
  max-height: 420px;
  overflow-y: auto;
}

.no-notifications {
  padding: 40px 20px;
  text-align: center;
  color: #9ca3af;
}

.no-notifications p {
  margin: 0;
  font-size: 0.875rem;
}

.notification-item {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border-bottom: 1px solid #f3f4f6;
  cursor: pointer;
  transition: background 0.2s;
  position: relative;
  align-items: flex-start;
}

.notification-item:hover {
  background: #f9fafb;
}

.notification-item.unread {
  background: #f0f9ff;
}

.notification-item.unread:hover {
  background: #e0f2fe;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  margin: 0 0 4px 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: #111827;
}

.notification-message {
  margin: 0 0 4px 0;
  font-size: 0.8125rem;
  color: #6b7280;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.notification-time {
  font-size: 0.75rem;
  color: #9ca3af;
}

.unread-dot {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  width: 8px;
  height: 8px;
  background: #3b82f6;
  border-radius: 50%;
}

/* Scrollbar styling */
.notification-list::-webkit-scrollbar {
  width: 6px;
}

.notification-list::-webkit-scrollbar-track {
  background: #f3f4f6;
}

.notification-list::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}

.notification-list::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

/* Notification Footer */
.notification-footer {
  padding: 12px 20px;
  border-top: 1px solid #e5e7eb;
  background: #fafafa;
}

.view-all-btn {
  display: block;
  width: 100%;
  text-align: center;
  color: #6366f1;
  font-size: 0.875rem;
  font-weight: 600;
  text-decoration: none;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.2s;
}

.view-all-btn:hover {
  background: #f0f0ff;
  color: #4f46e5;
}

@media (max-width: 768px) {
  .navbar-links {
    display: none;
  }

  .notification-dropdown {
    right: 20px;
    width: calc(100vw - 40px);
    max-width: 380px;
  }

  .profile-dropdown {
    right: 20px;
    width: calc(100vw - 40px);
    max-width: 280px;
  }
}
</style>