<template>
    <nav class="navbar">
      <div class="container navbar-container">
        <router-link to="/" class="navbar-logo">
         Task Quest
        </router-link>
        
        <div class="navbar-right">
          <router-link to="/" class="navbar-link">Dashboard</router-link>
          <router-link to="/projects" class="navbar-link">Projects</router-link>
          <router-link to="/" class="navbar-link">Free slot</router-link>
          <router-link to="" class="navbar-link">My Schedule</router-link>
          
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

          <button @click="logout" class="logout-btn">Logout</button>
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
            
            <div 
              v-for="notification in recentNotifications" 
              :key="notification.id" 
              class="notification-item"
              :class="{ 'unread': !notification.read }"
              @click="handleNotificationClick(notification)"
            >
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

  export default {
    name: 'NavBar',
    data() {
      return {
        showNotifications: false,
        notifications: [
          // Sample notifications - replace with real data later
          {
            id: 1,
            icon: '📋',
            title: 'New Task Assigned',
            message: 'You have been assigned to "Update Dashboard UI"',
            time: new Date(Date.now() - 5 * 60000), // 5 minutes ago
            read: false
          },
          {
            id: 2,
            icon: '✅',
            title: 'Task Completed',
            message: 'John completed "Design Landing Page"',
            time: new Date(Date.now() - 2 * 3600000), // 2 hours ago
            read: false
          },
          {
            id: 3,
            icon: '⏰',
            title: 'Deadline Approaching',
            message: 'Task "API Integration" is due in 2 days',
            time: new Date(Date.now() - 24 * 3600000), // 1 day ago
            read: true
          }
        ]
      }
    },
    computed: {
      unreadCount() {
        return this.notifications.filter(n => !n.read).length
      },
      recentNotifications() {
        // Show only the 5 most recent notifications in dropdown
        return this.notifications.slice(0, 5)
      }
    },
    methods: {
      logout() {
        authService.logout();
        this.$router.push('/login');
      },
      
      toggleNotifications() {
        this.showNotifications = !this.showNotifications
      },
      
      markAllAsRead() {
        this.notifications.forEach(n => n.read = true)
      },
      
      handleNotificationClick(notification) {
        notification.read = true
        // TODO: Navigate to relevant page or perform action
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
        return time.toLocaleDateString()
      }
    },
    mounted() {
      // Close dropdown when clicking outside
      document.addEventListener('click', (e) => {
        if (!this.$el.contains(e.target)) {
          this.showNotifications = false
        }
      })
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
  
  /* .navbar-link:hover, .navbar-link.router-link-active {
    color: #111827;
    background: #f3f4f6;
  } */
  
  @media (max-width: 768px) {
    .navbar-links {
      display: none;
    }

    .notification-dropdown {
      right: 20px;
      width: calc(100vw - 40px);
      max-width: 380px;
    }
  }
  </style>