// Mock data for tasks and subtasks
export const mockTasks = [
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
  },
  {
    taskId: 'task-004',
    taskName: 'Website Redesign Project',
    dueDate: new Date('2025-01-15'),
    assigner: 'user-001',
    collaborator: ['user-008', 'user-009'],
    indivSubtaskBool: true,
    status: 'in-progress',
    instruction: 'Complete redesign of company website',
    subtasks: [
      {
        taskId: 'task-004',
        subTaskId: 'subtask-005',
        subTaskName: 'UI/UX Design',
        dueDate: new Date('2024-12-20'),
        assigner: 'user-001',
        collaborator: ['user-008'],
        currentStatus: {
          statusId: 'status-005',
          statusName: 'In progress',
          statusTimestamp: new Date(),
          subTaskId: 'subtask-005',
          staffId: 'staff-005'
        },
        assignees: [
          { id: 'user-008', name: 'Emily Zhang', initials: 'EZ' },
          { id: 'user-009', name: 'Alex Rodriguez', initials: 'AR' }
        ],
        approver: { id: 'user-001', name: 'John Smith', initials: 'JS' },
        assignee: { id: 'user-008', name: 'Emily Zhang', initials: 'EZ' },
        instruction: 'Create modern and responsive design mockups'
      },
      {
        taskId: 'task-004',
        subTaskId: 'subtask-006',
        subTaskName: 'Frontend Development',
        dueDate: new Date('2025-01-10'),
        assigner: 'user-001',
        collaborator: ['user-009'],
        currentStatus: {
          statusId: 'status-006',
          statusName: 'To Do',
          statusTimestamp: new Date(),
          subTaskId: 'subtask-006',
          staffId: 'staff-006'
        },
        assignees: [
          { id: 'user-009', name: 'Alex Rodriguez', initials: 'AR' }
        ],
        approver: { id: 'user-001', name: 'John Smith', initials: 'JS' },
        assignee: { id: 'user-009', name: 'Alex Rodriguez', initials: 'AR' },
        instruction: 'Implement the new design with Vue.js and modern CSS'
      }
    ]
  }
];

// Additional mock users for reference
export const mockUsers = [
  { id: 'user-001', name: 'John Smith', initials: 'JS', role: 'Project Manager' },
  { id: 'user-002', name: 'Ang Koo Kueh', initials: 'AK', role: 'Developer' },
  { id: 'user-003', name: 'Turtle Tan', initials: 'TT', role: 'Team Lead' },
  { id: 'user-004', name: 'Jake Lee', initials: 'JL', role: 'Analyst' },
  { id: 'user-005', name: 'Maria Garcia', initials: 'MG', role: 'Sales Manager' },
  { id: 'user-006', name: 'David Chen', initials: 'DC', role: 'Financial Analyst' },
  { id: 'user-007', name: 'Sarah Wilson', initials: 'SW', role: 'Marketing Specialist' },
  { id: 'user-008', name: 'Mike Johnson', initials: 'MJ', role: 'Marketing Manager' },
  { id: 'user-009', name: 'Emily Zhang', initials: 'EZ', role: 'UI/UX Designer' },
  { id: 'user-010', name: 'Alex Rodriguez', initials: 'AR', role: 'Frontend Developer' }
];

// Status definitions
export const taskStatuses = [
  { value: 'to-do', label: 'To Do', color: '#ef4444' },
  { value: 'in-progress', label: 'In Progress', color: '#fbbf24' },
  { value: 'pending', label: 'Pending', color: '#f59e0b' },
  { value: 'completed', label: 'Completed', color: '#10b981' }
];

export const subtaskStatuses = [
  { value: 'To Do', label: 'To Do', color: '#ef4444' },
  { value: 'In progress', label: 'In Progress', color: '#fbbf24' },
  { value: 'Pending', label: 'Pending', color: '#f59e0b' },
  { value: 'Completed', label: 'Completed', color: '#10b981' }
];