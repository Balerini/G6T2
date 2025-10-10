// frontend/src/services/notificationService.js
/* global process */
import axios from 'axios';

const API_BASE_URL = process.env.VUE_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Simple event emitter for notification updates
class NotificationEventEmitter {
  constructor() {
    this.listeners = {};
  }

  on(event, callback) {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event].push(callback);
  }

  off(event, callback) {
    if (!this.listeners[event]) return;
    this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
  }

  emit(event, data) {
    if (!this.listeners[event]) return;
    this.listeners[event].forEach(callback => callback(data));
  }
}

const eventEmitter = new NotificationEventEmitter();

export const notificationService = {
  /**
   * Get notifications for a user
   * @param {string} userId - User ID
   * @param {boolean} unreadOnly - If true, only return unread notifications
   * @param {number} limit - Maximum number of notifications
   */
  async getNotifications(userId, unreadOnly = false, limit = 50) {
    try {
      const response = await api.get(`/api/notifications/${userId}`, {
        params: {
          unread_only: unreadOnly,
          limit: limit
        }
      });
      return response.data.notifications || [];
    } catch (error) {
      console.error('Error fetching notifications:', error);
      throw error;
    }
  },

  /**
   * Mark a notification as read
   * @param {string} notificationId - Notification ID
   */
  async markAsRead(notificationId) {
    try {
      const response = await api.put(`/api/notifications/${notificationId}/read`);
      // Emit event to notify other components
      eventEmitter.emit('notification-marked-read', { notificationId });
      return response.data;
    } catch (error) {
      console.error('Error marking notification as read:', error);
      throw error;
    }
  },

  /**
   * Mark all notifications as read for a user
   * @param {string} userId - User ID
   */
  async markAllAsRead(userId) {
    try {
      const response = await api.put(`/api/notifications/${userId}/mark-all-read`);
      // Emit event to notify other components
      eventEmitter.emit('notifications-marked-all-read', { userId });
      return response.data;
    } catch (error) {
      console.error('Error marking all as read:', error);
      throw error;
    }
  },

  /**
   * Delete a notification
   * @param {string} notificationId - Notification ID
   */
  async deleteNotification(notificationId) {
    try {
      const response = await api.delete(`/api/notifications/${notificationId}`);
      // Emit event to notify other components
      eventEmitter.emit('notification-deleted', { notificationId });
      return response.data;
    } catch (error) {
      console.error('Error deleting notification:', error);
      throw error;
    }
  },

  /**
   * Manually trigger deadline check (for testing)
   */
  async checkDeadlines() {
    try {
      const response = await api.post('/api/notifications/check-deadlines');
      return response.data;
    } catch (error) {
      console.error('Error checking deadlines:', error);
      throw error;
    }
  },

  /**
   * Get unread notification count for a user
   * @param {string} userId - User ID
   */
  async getUnreadCount(userId) {
    try {
      const notifications = await this.getNotifications(userId, true);
      return notifications.length;
    } catch (error) {
      console.error('Error getting unread count:', error);
      return 0;
    }
  },

  /**
   * Subscribe to notification events
   * @param {string} event - Event name (notification-deleted, notification-marked-read, notifications-marked-all-read)
   * @param {Function} callback - Callback function
   */
  on(event, callback) {
    eventEmitter.on(event, callback);
  },

  /**
   * Unsubscribe from notification events
   * @param {string} event - Event name
   * @param {Function} callback - Callback function
   */
  off(event, callback) {
    eventEmitter.off(event, callback);
  },

  /**
   * Trigger a notification refresh across all components
   * Call this after actions that might create notifications (task creation, assignment, etc.)
   */
  triggerRefresh() {
    eventEmitter.emit('notifications-refresh');
  },

  /**
   * Check for upcoming deadlines (calls backend to check tasks due within 24 hours)
   * Should be called on login or app initialization
   */
  async checkUpcomingDeadlines() {
    try {
      console.log('🔔 Checking for upcoming deadlines...');
      const response = await api.post('/api/notifications/check-deadlines');
      
      // Trigger refresh to load any new notifications
      this.triggerRefresh();
      
      return response.data;
    } catch (error) {
      console.error('Error checking deadlines:', error);
      // Don't throw - this is a background check, shouldn't break the app
      return null;
    }
  }
};

export default notificationService;

