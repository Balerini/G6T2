// frontend/src/services/taskEventService.js

/**
 * Lightweight event emitter for task-related updates (e.g. calendar refreshes).
 * Components can subscribe to events without introducing a global state manager.
 */
class TaskEventEmitter {
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

  emit(event, payload) {
    if (!this.listeners[event]) return;
    this.listeners[event].forEach(callback => {
      try {
        callback(payload);
      } catch (error) {
        console.error(`taskEventService listener for "${event}" threw an error:`, error);
      }
    });
  }
}

const emitter = new TaskEventEmitter();

export const taskEventService = {
  on(event, callback) {
    emitter.on(event, callback);
  },
  off(event, callback) {
    emitter.off(event, callback);
  },
  /**
   * For cases where a specific task was created. Also triggers a general refresh.
   */
  triggerTaskCreated(task) {
    emitter.emit('task-created', task);
    emitter.emit('tasks-refresh', task);
  },
  /**
   * Trigger a general refresh for task consumers (calendar, dashboards, etc.).
   */
  triggerTasksRefresh(payload) {
    emitter.emit('tasks-refresh', payload);
  }
};

export default taskEventService;
