<template>
  <div class="crm-container">
    <!-- Header Section -->
    <div class="header-section">
      <div class="container">
        <div class="header-content">
          <h1 class="hero-title">Projects</h1>
          <button class="tab-btn new-project-btn" @click="showNewProjectModal = true">
            + New Project
          </button>
        </div>
        
        <div class="action-tabs">
          <button class="tab-btn" :class="{ active: activeTab === 'all' }" @click="activeTab = 'all'">
            All Projects
          </button>
        </div>
      </div>
    </div>

    <!-- Tasks Section -->
    <div class="tasks-section">
      <div class="container">
        <div class="task-list">
          <div v-for="task in filteredTasks" :key="task.taskId" class="task-card">
            <!-- Task Header -->
            <div class="task-header">
              <div class="task-status-indicator" :class="getStatusClass(task.status)"></div>
              <h2 class="task-title">{{ task.taskName }}</h2>
              <button class="edit-btn">✏️</button>
            </div>

            <!-- Subtasks -->
            <div class="subtasks-container">
              <div v-for="subtask in task.subtasks" :key="subtask.subTaskId" class="subtask-item">
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
                      <span v-for="assignee in subtask.assignees" :key="assignee.id" 
                             :title="assignee.name">
                        {{ assignee.name }}
                      </span>
                    </div>
                  </div>
                  
                  <div class="meta-group">
                    <span class="meta-label">Approver:</span>
                    <div class="assignee-avatars">
                      <span :title="subtask.approver?.name">
                        {{ subtask.approver?.name }}
                      </span>
                    </div>
                  </div>
                  
                  <div class="meta-group">
                    <span class="meta-label">Assignee:</span>
                    <div class="assignee-avatars">
                      <span :title="subtask.assignee?.name">
                        {{ subtask.assignee?.name }}
                      </span>
                    </div>
                  </div>
                  
                  <button class="view-btn">View</button>
                </div>
              </div>
              
              <button class="add-subtask-btn">
                + Add
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CRMTaskManager',
  data() {
    return {
      activeTab: 'all',
      tasks: [
        {
          taskId: 'task-001',
          taskName: 'Board Meeting',
          dueDate: new Date('2024-10-19'),
          assigner: 'user-001',
          collaborator: ['user-002', 'user-003'],
          indivSubtaskBool: true,
          status: 'in-progress',
          instruction: 'Prepare quarterly board meeting materials',
          subtasks: [
            {
              taskId: 'task-001',
              subTaskId: 'subtask-001',
              subTaskName: 'Board Meeting Proposal',
              dueDate: new Date('2024-10-19'),
              assigner: 'user-001',
              collaborator: ['user-002'],
              currentStatus: {
                statusId: 'status-001',
                statusName: 'In progress',
                statusTimestamp: new Date(),
                subTaskId: 'subtask-001',
                staffId: 'staff-001'
              },
              assignees: [
                { id: 'user-002', name: 'Ang Koo Kueh', initials: 'AK' },
                { id: 'user-003', name: 'Turtle Tan', initials: 'TT' },
              ],
              approver: { id: 'user-003', name: 'Turtle Tan', initials: 'TT' },
              assignee: { id: 'user-004', name: 'Jake Lee', initials: 'JL' },
              instruction: 'Create comprehensive proposal for board review'
            }
          ]
        },
        {
          taskId: 'task-002',
          taskName: 'Sales Revenue 2022',
          dueDate: new Date('2024-11-29'),
          assigner: 'user-001',
          collaborator: ['user-004', 'user-005'],
          indivSubtaskBool: true,
          status: 'to-do',
          instruction: 'Analyze sales performance and prepare revenue report',
          subtasks: [
            {
              taskId: 'task-002',
              subTaskId: 'subtask-002',
              subTaskName: 'Analyse Sales',
              dueDate: new Date('2024-11-29'),
              assigner: 'user-001',
              collaborator: ['user-004'],
              currentStatus: {
                statusId: 'status-002',
                statusName: 'To Do',
                statusTimestamp: new Date(),
                subTaskId: 'subtask-002',
                staffId: 'staff-002'
              },
              assignees: [
                { id: 'user-005', name: 'Ang Koo Kueh', initials: 'AK' }
              ],
              approver: { id: 'user-003', name: 'Turtle Tan', initials: 'TT' },
              assignee: { id: 'user-004', name: 'Jake Lee', initials: 'JL' },
              instruction: 'Comprehensive analysis of 2022 sales data and trends'
            },
            {
              taskId: 'task-002',
              subTaskId: 'subtask-003',
              subTaskName: 'Revenue Forecasting',
              dueDate: new Date('2024-12-15'),
              assigner: 'user-001',
              collaborator: ['user-005', 'user-006'],
              currentStatus: {
                statusId: 'status-003',
                statusName: 'Pending',
                statusTimestamp: new Date(),
                subTaskId: 'subtask-003',
                staffId: 'staff-003'
              },
              assignees: [
                { id: 'user-005', name: 'Maria Garcia', initials: 'MG' }
              ],
              approver: { id: 'user-001', name: 'John Smith', initials: 'JS' },
              assignee: { id: 'user-006', name: 'David Chen', initials: 'DC' },
              instruction: 'Create detailed revenue projections for next quarter'
            }
          ]
        },
        {
          taskId: 'task-003',
          taskName: 'Marketing Campaign Q4',
          dueDate: new Date('2024-12-01'),
          assigner: 'user-001',
          collaborator: ['user-006', 'user-007'],
          indivSubtaskBool: true,
          status: 'completed',
          instruction: 'Plan and execute Q4 marketing initiatives',
          subtasks: [
            {
              taskId: 'task-003',
              subTaskId: 'subtask-004',
              subTaskName: 'Social Media Strategy',
              dueDate: new Date('2024-11-15'),
              assigner: 'user-001',
              collaborator: ['user-006'],
              currentStatus: {
                statusId: 'status-004',
                statusName: 'Completed',
                statusTimestamp: new Date(),
                subTaskId: 'subtask-004',
                staffId: 'staff-004'
              },
              assignees: [
                { id: 'user-006', name: 'Sarah Wilson', initials: 'SW' }
              ],
              approver: { id: 'user-001', name: 'John Smith', initials: 'JS' },
              assignee: { id: 'user-007', name: 'Mike Johnson', initials: 'MJ' },
              instruction: 'Develop comprehensive social media campaign strategy'
            }
          ]
        }
      ]
    }
  },
  computed: {
    filteredTasks() {
      if (this.activeTab === 'all') {
        return this.tasks;
      }
      return this.tasks.filter(task => task.collaborator && task.collaborator.length > 0);
    }
  },
  methods: {
    getStatusClass(status) {
      const statusClasses = {
        'in-progress': 'status-progress',
        'to-do': 'status-todo',
        'completed': 'status-completed',
        'pending': 'status-pending'
      };
      return statusClasses[status] || 'status-default';
    },
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
.crm-container {
  min-height: 100vh;
  background: #f8fafc;
}

.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.header-section {
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  padding: 1.5rem 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.hero-title {
  font-size: 2.25rem;
  line-height: 1.2;
  font-weight: 800;
  color: #111827;
  margin-bottom: 0.5rem;
}

.action-tabs {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.tab-btn {
  padding: 0.625rem 1.25rem;
  border: 1px solid #374151;
  background: #fff;
  color: #374151;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn:hover {
  background: #f9fafb;
  border-color: #111827;
  color: #111827;
}

.tab-btn.active {
  background: #111827;
  color: #fff;
  border-color: #111827;
}

.new-project-btn {
  background: #111827;
  color: #fff;
  border-color: #111827;
}

.new-project-btn:hover {
  background: #374151;
  border-color: #374151;
}

.tasks-section {
  padding: 2rem 0;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.task-card {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.task-header {
  display: flex;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #f3f4f6;
  gap: 1rem;
}

.task-status-indicator {
  width: 4px;
  height: 40px;
  border-radius: 2px;
}

.status-progress {
  background: #fbbf24;
}

.status-todo {
  background: #ef4444;
}

.status-completed {
  background: #10b981;
}

.status-pending {
  background: #f59e0b;
}

.task-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
  flex: 1;
}

.edit-btn {
  background: #111827;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 0.5rem;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s ease;
}

.edit-btn:hover {
  background: #374151;
}

.subtasks-container {
  padding: 1.5rem;
}

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
}

.assignee-avatar.approver {
  background: #ddd6fe;
  color: #5b21b6;
}

.assignee-avatar.assignee {
  background: #fef3c7;
  color: #92400e;
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

.add-subtask-btn {
  background: transparent;
  color: #111827;
  border: 1px dashed #111827;
  border-radius: 6px;
  padding: 0.75rem 1rem;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  width: 100%;
  transition: all 0.2s ease;
}

.add-subtask-btn:hover {
  background: #f9fafb;
  border-color: #374151;
  color: #374151;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #fff;
  border-radius: 12px;
  padding: 2rem;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-close-btn {
  background: #111827;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.modal-close-btn:hover {
  background: #374151;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .action-tabs {
    flex-direction: column;
  }
  
  .subtask-meta {
    grid-template-columns: 1fr;
  }
  
  .task-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
  
  .task-title {
    font-size: 1.25rem;
  }
}
</style>
