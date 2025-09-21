// Updated mock data to match database schema
export const mockProjects = [
  {
    proj_ID: 'proj-001',
    proj_name: 'Board Meeting',
    proj_desc: 'Prepare quarterly board meeting materials and documentation',
    start_date: new Date('2024-10-01'),
    end_date: new Date('2024-10-19'),
    collaborators: ['user-002', 'user-003'],
    attachments: ['board-meeting-agenda.pdf', 'quarterly-report.xlsx'],
    proj_status: 'in-progress'
  },
  {
    proj_ID: 'proj-002',
    proj_name: 'Sales Revenue 2022',
    proj_desc: 'Analyze sales performance and prepare comprehensive revenue report',
    start_date: new Date('2024-11-01'),
    end_date: new Date('2024-11-29'),
    collaborators: ['user-004', 'user-005'],
    attachments: ['sales-data-2022.xlsx'],
    proj_status: 'to-do'
  },
  {
    proj_ID: 'proj-003',
    proj_name: 'Marketing Campaign Q4',
    proj_desc: 'Plan and execute Q4 marketing initiatives across all channels',
    start_date: new Date('2024-10-15'),
    end_date: new Date('2024-12-01'),
    collaborators: ['user-006', 'user-007'],
    attachments: ['campaign-strategy.pptx', 'budget-allocation.xlsx'],
    proj_status: 'completed'
  },
  {
    proj_ID: 'proj-004',
    proj_name: 'Website Redesign Project',
    proj_desc: 'Complete redesign of company website with modern UI/UX',
    start_date: new Date('2024-11-15'),
    end_date: new Date('2025-01-15'),
    collaborators: ['user-008', 'user-009'],
    attachments: ['design-mockups.fig', 'requirements.docx'],
    proj_status: 'in-progress'
  }
];

export const mockTasks = [
  {
    proj_ID: 'proj-001',
    task_ID: 'task-001',
    task_name: 'Board Meeting Proposal',
    task_desc: 'Create comprehensive proposal for board review including financial summaries and strategic recommendations',
    start_date: new Date('2024-10-01'),
    end_date: new Date('2024-10-19'),
    created_by: 'user-001',
    assigned_to: ['user-002', 'user-003'],
    attachments: ['proposal-draft.docx', 'financial-summary.xlsx'],
    task_status: 'in-progress'
  },
  {
    proj_ID: 'proj-002',
    task_ID: 'task-002',
    task_name: 'Analyse Sales',
    task_desc: 'Comprehensive analysis of 2022 sales data and trends with comparative metrics',
    start_date: new Date('2024-11-01'),
    end_date: new Date('2024-11-29'),
    created_by: 'user-001',
    assigned_to: ['user-005'],
    attachments: ['sales-analysis-template.xlsx'],
    task_status: 'to-do'
  },
  {
    proj_ID: 'proj-002',
    task_ID: 'task-003',
    task_name: 'Revenue Forecasting',
    task_desc: 'Create detailed revenue projections for next quarter based on historical data',
    start_date: new Date('2024-11-15'),
    end_date: new Date('2024-12-15'),
    created_by: 'user-001',
    assigned_to: ['user-005', 'user-006'],
    attachments: ['forecasting-model.xlsx'],
    task_status: 'pending'
  },
  {
    proj_ID: 'proj-003',
    task_ID: 'task-004',
    task_name: 'Social Media Strategy',
    task_desc: 'Develop comprehensive social media campaign strategy for Q4 initiatives',
    start_date: new Date('2024-10-15'),
    end_date: new Date('2024-11-15'),
    created_by: 'user-001',
    assigned_to: ['user-006'],
    attachments: ['social-media-calendar.xlsx', 'content-guidelines.pdf'],
    task_status: 'completed'
  },
  {
    proj_ID: 'proj-004',
    task_ID: 'task-005',
    task_name: 'UI/UX Design',
    task_desc: 'Create modern and responsive design mockups for the new website',
    start_date: new Date('2024-11-15'),
    end_date: new Date('2024-12-20'),
    created_by: 'user-001',
    assigned_to: ['user-008', 'user-009'],
    attachments: ['wireframes.fig', 'style-guide.pdf'],
    task_status: 'in-progress'
  },
  {
    proj_ID: 'proj-004',
    task_ID: 'task-006',
    task_name: 'Frontend Development',
    task_desc: 'Implement the new design with Vue.js and modern CSS frameworks',
    start_date: new Date('2024-12-20'),
    end_date: new Date('2025-01-10'),
    created_by: 'user-001',
    assigned_to: ['user-009'],
    attachments: ['development-setup.md'],
    task_status: 'to-do'
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
  { value: 'to-do', label: 'To Do', color: '#ef4444' },
  { value: 'in-progress', label: 'In Progress', color: '#fbbf24' },
  { value: 'pending', label: 'Pending', color: '#f59e0b' },
  { value: 'completed', label: 'Completed', color: '#10b981' }
];

// Helper function to get tasks for a specific project
export function getTasksForProject(projectId) {
  return mockTasks.filter(task => task.proj_ID === projectId);
}

// Helper function to get project with tasks
// export function getProjectWithTasks(projectId) {
//   const project = mockProjects.find(p => p.proj_ID === projectId);
//   if (!project) return null;
  
//   return {
//     ...project,
//     tasks: getTasksForProject(projectId)
//   };
// }

// Helper function to get all projects with their tasks
export function getAllProjectsWithTasks() {
  return mockProjects.map(project => ({
    ...project,
    tasks: getTasksForProject(project.proj_ID)
  }));
}