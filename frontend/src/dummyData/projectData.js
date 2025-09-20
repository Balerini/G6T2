// Mock data for projects and tasks
export const mockProjects = [
  {
    projectId: 'project-001',
    projectName: 'Board Meeting',
    dueDate: new Date('2024-10-19'),
    assigner: 'user-001',
    collaborator: ['user-002', 'user-003'],
    indivTaskBool: true,
    status: 'in-progress',
    instruction: 'Prepare quarterly board meeting materials',
    tasks: [
      {
        projectId: 'project-001',
        taskId: 'task-001',
        taskName: 'Board Meeting Proposal',
        dueDate: new Date('2024-10-19'),
        assigner: 'user-001',
        collaborator: ['user-002'],
        currentStatus: {
          statusId: 'status-001',
          statusName: 'In progress',
          statusTimestamp: new Date(),
          taskId: 'task-001',
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
    projectId: 'project-002',
    projectName: 'Sales Revenue 2022',
    dueDate: new Date('2024-11-29'),
    assigner: 'user-001',
    collaborator: ['user-004', 'user-005'],
    indivTaskBool: true,
    status: 'to-do',
    instruction: 'Analyze sales performance and prepare revenue report',
    tasks: [
      {
        projectId: 'project-002',
        taskId: 'task-002',
        taskName: 'Analyse Sales',
        dueDate: new Date('2024-11-29'),
        assigner: 'user-001',
        collaborator: ['user-004'],
        currentStatus: {
          statusId: 'status-002',
          statusName: 'To Do',
          statusTimestamp: new Date(),
          taskId: 'task-002',
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
        projectId: 'project-002',
        taskId: 'task-003',
        taskName: 'Revenue Forecasting',
        dueDate: new Date('2024-12-15'),
        assigner: 'user-001',
        collaborator: ['user-005', 'user-006'],
        currentStatus: {
          statusId: 'status-003',
          statusName: 'Pending',
          statusTimestamp: new Date(),
          taskId: 'task-003',
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
    projectId: 'project-003',
    projectName: 'Marketing Campaign Q4',
    dueDate: new Date('2024-12-01'),
    assigner: 'user-001',
    collaborator: ['user-006', 'user-007'],
    indivTaskBool: true,
    status: 'completed',
    instruction: 'Plan and execute Q4 marketing initiatives',
    tasks: [
      {
        projectId: 'project-003',
        taskId: 'task-004',
        taskName: 'Social Media Strategy',
        dueDate: new Date('2024-11-15'),
        assigner: 'user-001',
        collaborator: ['user-006'],
        currentStatus: {
          statusId: 'status-004',
          statusName: 'Completed',
          statusTimestamp: new Date(),
          taskId: 'task-004',
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
    projectId: 'project-004',
    projectName: 'Website Redesign Project',
    dueDate: new Date('2025-01-15'),
    assigner: 'user-001',
    collaborator: ['user-008', 'user-009'],
    indivTaskBool: true,
    status: 'in-progress',
    instruction: 'Complete redesign of company website',
    tasks: [
      {
        projectId: 'project-004',
        taskId: 'task-005',
        taskName: 'UI/UX Design',
        dueDate: new Date('2024-12-20'),
        assigner: 'user-001',
        collaborator: ['user-008'],
        currentStatus: {
          statusId: 'status-005',
          statusName: 'In progress',
          statusTimestamp: new Date(),
          taskId: 'task-005',
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
        projectId: 'project-004',
        taskId: 'task-006',
        taskName: 'Frontend Development',
        dueDate: new Date('2025-01-10'),
        assigner: 'user-001',
        collaborator: ['user-009'],
        currentStatus: {
          statusId: 'status-006',
          statusName: 'To Do',
          statusTimestamp: new Date(),
          taskId: 'task-006',
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
export const projectStatuses = [
  { value: 'to-do', label: 'To Do', color: '#ef4444' },
  { value: 'in-progress', label: 'In Progress', color: '#fbbf24' },
  { value: 'pending', label: 'Pending', color: '#f59e0b' },
  { value: 'completed', label: 'Completed', color: '#10b981' }
];

export const taskStatuses = [
  { value: 'To Do', label: 'To Do', color: '#ef4444' },
  { value: 'In progress', label: 'In Progress', color: '#fbbf24' },
  { value: 'Pending', label: 'Pending', color: '#f59e0b' },
  { value: 'Completed', label: 'Completed', color: '#10b981' }
];