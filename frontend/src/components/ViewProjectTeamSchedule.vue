<template>
  <div class="team-schedule-container">
    <div class="schedule-header">
      <h3 class="schedule-title">📅 Team Schedule</h3>
      <p class="schedule-subtitle">Project timeline and task assignments</p>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading team schedule...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <span class="error-icon">⚠️</span>
      <p>{{ error }}</p>
    </div>

    <div v-else-if="!teamMembers || teamMembers.length === 0" class="no-data-state">
      <div class="no-data-icon">📋</div>
      <p>No team members or tasks found for this project.</p>
    </div>

    <div v-else class="gantt-container">
      <!-- Month Navigation -->
      <div class="month-navigation">
        <button @click="previousMonth" class="nav-btn">
          <span>←</span> Previous
        </button>
        <div class="current-month-display">
          <h3>{{ getCurrentMonthDisplay() }}</h3>
        </div>
        <button @click="nextMonth" class="nav-btn">
          Next <span>→</span>
        </button>
      </div>

      <!-- Gantt Chart -->
      <div class="gantt-chart">
        <!-- Header -->
        <div class="gantt-header">
          <div class="member-column">Team Members</div>
          <div class="timeline-column">
            <div class="timeline-header">
              <div v-for="date in timelineDates" :key="date" class="date-cell"
                :class="{ 'weekend': isWeekend(date), 'today': isToday(date) }">
                <div class="date-day">{{ getDateDay(date) }}</div>
                <div class="date-month">{{ getDateMonth(date) }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Rows -->
        <div class="gantt-rows">
          <div v-for="(member, index) in teamMembers" :key="index" class="gantt-row"
            :style="{ minHeight: (member.rowCount * 28 + 16) + 'px' }">
            <!-- Member Info -->
            <div class="member-info">
              <div class="member-avatar">{{ getInitials(member.name) }}</div>
              <div class="member-details">
                <span class="member-name">{{ member.name }}</span>
                <span class="member-task-count">{{ member.bars.length }} task{{ member.bars.length !== 1 ? 's' : ''
                }}</span>
              </div>
            </div>

            <!-- Timeline -->
            <div class="timeline-row">
              <div v-for="date in timelineDates" :key="date" class="grid-cell"
                :class="{ 'weekend': isWeekend(date), 'today': isToday(date) }"></div>

              <!-- Task Bars -->
              <div class="task-bars">
                <div v-for="(bar, barIndex) in member.bars" :key="barIndex" class="task-bar"
                  :style="getBarStyle(bar, barIndex)" :title="getTooltip(bar)">
                  <span class="task-text">{{ bar.ganttBarConfig.label }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { onMounted, ref } from "vue";
import { projectService } from "../services/projectService";

export default {
  name: "ViewProjectTeamSchedule",
  props: {
    projectId: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const loading = ref(true);
    const error = ref(null);
    const teamMembers = ref([]);

    const getInitials = (name) => {
      return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
    };

    const formatDate = (dateStr) => {
      return new Date(dateStr).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      });
    };

    // Gantt chart functions
    const timelineDates = ref([]);
    const currentMonth = ref(new Date());
    const allTasks = ref([]);

    const generateTimeline = (tasks) => {
      allTasks.value = tasks;

      // Set current month to today's date by default
      const today = new Date();
      currentMonth.value = new Date(today.getFullYear(), today.getMonth(), 1);

      updateTimelineForCurrentMonth();
    };

    const updateTimelineForCurrentMonth = () => {
      const year = currentMonth.value.getFullYear();
      const month = currentMonth.value.getMonth();

      // Get first and last day of the month
      const firstDay = new Date(year, month, 1);
      const lastDay = new Date(year, month + 1, 0);

      // Start from the first day of the month (removed the Sunday alignment)
      const startDate = new Date(firstDay);

      // End on the last day of the month (removed the Saturday alignment)
      const endDate = new Date(lastDay);

      const timeline = [];
      for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
        timeline.push(new Date(d).toISOString().split('T')[0]);
      }

      timelineDates.value = timeline;
    };

    const previousMonth = () => {
      currentMonth.value = new Date(currentMonth.value.getFullYear(), currentMonth.value.getMonth() - 1, 1);
      updateTimelineForCurrentMonth();
    };

    const nextMonth = () => {
      currentMonth.value = new Date(currentMonth.value.getFullYear(), currentMonth.value.getMonth() + 1, 1);
      updateTimelineForCurrentMonth();
    };

    const getCurrentMonthDisplay = () => {
      return currentMonth.value.toLocaleDateString('en-US', {
        month: 'long',
        year: 'numeric'
      });
    };

    const getDateDay = (dateStr) => {
      return new Date(dateStr).getDate();
    };

    const getDateMonth = (dateStr) => {
      return new Date(dateStr).toLocaleDateString('en', { month: 'short' });
    };

    const isWeekend = (dateStr) => {
      const day = new Date(dateStr).getDay();
      return day === 0 || day === 6;
    };

    const isToday = (dateStr) => {
      const today = new Date().toISOString().split('T')[0];
      return dateStr === today;
    };

    const getBarStyle = (bar) => {
      // Normalize dates to remove time components
      const taskStart = new Date(bar.start);
      taskStart.setHours(0, 0, 0, 0);

      const taskEnd = new Date(bar.end);
      taskEnd.setHours(0, 0, 0, 0);

      // Get the first and last dates in the visible timeline
      const timelineStart = new Date(timelineDates.value[0]);
      timelineStart.setHours(0, 0, 0, 0);

      const timelineEnd = new Date(timelineDates.value[timelineDates.value.length - 1]);
      timelineEnd.setHours(0, 0, 0, 0);

      // Check if task is completely outside the visible timeline
      if (taskEnd < timelineStart || taskStart > timelineEnd) {
        return { display: 'none' };
      }

      const cellWidth = 40;
      let left, width;

      // Find the actual start and end positions
      const startDateStr = taskStart < timelineStart ? timelineDates.value[0] : bar.start;
      const endDateStr = taskEnd > timelineEnd ? timelineDates.value[timelineDates.value.length - 1] : bar.end;

      const startIndex = timelineDates.value.indexOf(startDateStr);
      const endIndex = timelineDates.value.indexOf(endDateStr);

      if (startIndex === -1 || endIndex === -1) {
        // Fallback: calculate position based on date comparison
        let calculatedStartIndex = 0;
        let calculatedEndIndex = timelineDates.value.length - 1;

        for (let i = 0; i < timelineDates.value.length; i++) {
          const currentDate = new Date(timelineDates.value[i]);
          currentDate.setHours(0, 0, 0, 0);

          if (taskStart <= currentDate && calculatedStartIndex === 0) {
            calculatedStartIndex = i;
          }
          if (taskEnd >= currentDate) {
            calculatedEndIndex = i;
          }
        }

        left = calculatedStartIndex * cellWidth;
        width = (calculatedEndIndex - calculatedStartIndex + 1) * cellWidth;
      } else {
        left = startIndex * cellWidth;
        // The +1 ensures the end date is inclusive (covers the full day)
        width = (endIndex - startIndex + 1) * cellWidth;
      }

      // Ensure minimum width for visibility
      if (width < 20) {
        width = 20;
      }

      // Use the row assignment from the bar object
      const top = 8 + (bar.row || 0) * 28;

      return {
        left: `${left}px`,
        width: `${width}px`,
        top: `${top}px`,
        backgroundColor: bar.ganttBarConfig.style.backgroundColor,
        color: bar.ganttBarConfig.style.color
      };
    };

    const getTooltip = (bar) => {
      return `${bar.ganttBarConfig.label}\nStart: ${formatDate(bar.start)}\nEnd: ${formatDate(bar.end)}\nStatus: ${bar.status || 'N/A'}`;
    };

    onMounted(async () => {
      try {
        loading.value = true;
        error.value = null;

        if (!props.projectId) {
          throw new Error("Project ID is required");
        }

        // Get project data - this should return the structure from your JSON
        const projectData = await projectService.getProjectById(props.projectId);

        if (!projectData || !projectData.collaborators) {
          teamMembers.value = [];
          return;
        }

        // Extract collaborators array from the response
        const collaborators = projectData.collaborators;

        // Collect all tasks for timeline generation
        const allTasksList = [];

        // Helper function to check if two date ranges overlap
        const datesOverlap = (start1, end1, start2, end2) => {
          return start1 <= end2 && start2 <= end1;
        };

        // Helper function to assign rows to tasks to avoid overlap
        const assignTaskRows = (tasks) => {
          if (tasks.length === 0) return [];

          // Sort tasks by start date
          const sortedTasks = [...tasks].sort((a, b) =>
            new Date(a.start_date) - new Date(b.start_date)
          );

          // Track which rows are occupied and until when
          const rows = [];

          sortedTasks.forEach(task => {
            const taskStart = new Date(task.start_date);
            const taskEnd = new Date(task.end_date);

            // Find the first available row
            let assignedRow = 0;
            let rowFound = false;

            for (let i = 0; i < rows.length; i++) {
              // Check if this row is free for our task
              let canUseRow = true;
              for (const occupiedTask of rows[i]) {
                if (datesOverlap(taskStart, taskEnd,
                  new Date(occupiedTask.start_date),
                  new Date(occupiedTask.end_date))) {
                  canUseRow = false;
                  break;
                }
              }

              if (canUseRow) {
                assignedRow = i;
                rowFound = true;
                rows[i].push(task);
                break;
              }
            }

            // If no row was available, create a new one
            if (!rowFound) {
              assignedRow = rows.length;
              rows.push([task]);
            }

            task.assignedRow = assignedRow;
          });

          // Calculate the total height needed
          const maxRow = Math.max(...sortedTasks.map(t => t.assignedRow), 0);

          return { tasks: sortedTasks, rowCount: maxRow + 1 };
        };

        // Process each collaborator and their tasks
        teamMembers.value = collaborators.map(collaborator => {
          const tasks = collaborator.tasks || [];

          // Add tasks to the all tasks list for timeline generation
          allTasksList.push(...tasks);

          // Assign rows to avoid overlaps
          const { tasks: arrangedTasks, rowCount } = assignTaskRows(tasks);

          return {
            name: collaborator.name,
            email: collaborator.email,
            rowCount: rowCount,
            bars: arrangedTasks.map(task => ({
              start: task.start_date,
              end: task.end_date,
              status: task.task_status,
              row: task.assignedRow,
              ganttBarConfig: {
                id: task.task_id,
                label: task.task_name,
                style: {
                  backgroundColor: getTaskColor(task.task_status),
                  color: '#fff'
                },
              },
            })),
          };
        });

        // Generate timeline from all tasks
        generateTimeline(allTasksList);

      } catch (err) {
        console.error("Failed to load schedule:", err);
        error.value = err.message || "Failed to load team schedule";
      } finally {
        loading.value = false;
      }
    });

    // Helper function to get task color based on status
    const getTaskColor = (status) => {
      const colors = {
        'Not Started': '#f87171',
        'In Progress': '#fbbf24',
        'Completed': '#34d399',
        'Pending': '#fb923c',
        'Under Review': '#a78bfa'
      };
      return colors[status] || '#60a5fa';
    };

    return {
      loading,
      error,
      teamMembers,
      timelineDates,
      getInitials,
      formatDate,
      getDateDay,
      getDateMonth,
      isWeekend,
      isToday,
      getBarStyle,
      getTooltip,
      previousMonth,
      nextMonth,
      getCurrentMonthDisplay
    };
  },
};
</script>

<style scoped>
.team-schedule-container {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  margin: 1rem 0;
}

.schedule-header {
  margin-bottom: 2rem;
  text-align: center;
}

.schedule-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
  margin: 0 0 0.5rem 0;
}

.schedule-subtitle {
  color: #6b7280;
  font-size: 0.875rem;
  margin: 0;
}

.loading-state,
.error-state,
.no-data-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  text-align: center;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f3f4f6;
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-icon {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.no-data-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.loading-state p,
.error-state p,
.no-data-state p {
  color: #6b7280;
  font-size: 0.875rem;
  margin: 0;
}

.error-state p {
  color: #dc2626;
}

.gantt-container {
  background: white;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
  max-height: 600px;
}

/* Month Navigation */
.month-navigation {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  background: #f8fafc;
  border-bottom: 1px solid #e5e7eb;
  border-radius: 8px 8px 0 0;
}

.nav-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  color: #374151;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.nav-btn:hover {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.nav-btn span {
  font-size: 1.2rem;
  font-weight: bold;
}

.current-month-display {
  text-align: center;
}

.current-month-display h3 {
  margin: 0;
  color: #111827;
  font-size: 1.25rem;
  font-weight: 600;
}

.gantt-chart {
  min-width: 800px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  overflow-x: auto;
  overflow-y: auto;
  max-height: 500px;
  scroll-behavior: smooth;
}

/* Header */
.gantt-header {
  display: flex;
  background: #f8fafc;
  border-bottom: 2px solid #e5e7eb;
  position: sticky;
  top: 0;
  z-index: 10;
}

.member-column {
  width: 200px;
  min-width: 200px;
  padding: 1rem;
  border-right: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  font-weight: 600;
  color: #374151;
  font-size: 0.875rem;
}

.timeline-column {
  flex: 1;
  overflow: visible;
}

.timeline-header {
  display: flex;
  min-width: 600px;
  position: sticky;
  top: 0;
  z-index: 10;
  background: #f8fafc;
}

.date-cell {
  width: 40px;
  min-width: 40px;
  height: 60px;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
  font-size: 0.75rem;
}

.date-cell.weekend {
  background: #f3f4f6;
}

.date-cell.today {
  background: #dbeafe;
  border-color: #3b82f6;
}

.date-day {
  font-weight: 600;
  color: #374151;
  font-size: 0.875rem;
}

.date-month {
  color: #6b7280;
  text-transform: uppercase;
  font-size: 0.625rem;
}

/* Rows */
.gantt-rows {
  position: relative;
}

.gantt-row {
  display: flex;
  border-bottom: 1px solid #f3f4f6;
  min-height: 60px;
  position: relative;
}

.gantt-row:hover {
  background: #f9fafb;
}

/* Member Info */
.member-info {
  width: 200px;
  min-width: 200px;
  padding: 1rem;
  border-right: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: white;
  position: sticky;
  left: 0;
  z-index: 15;
  box-shadow: 2px 0 4px rgba(0, 0, 0, 0.1);
}

.member-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #6366f1;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
  flex-shrink: 0;
}

.member-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  overflow: hidden;
}

.member-name {
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.member-task-count {
  font-size: 0.75rem;
  color: #6b7280;
}

/* Timeline Row */
.timeline-row {
  flex: 1;
  display: flex;
  position: relative;
  min-width: 600px;
  overflow: visible;
  height: 100%;
}

.grid-cell {
  width: 40px;
  min-width: 40px;
  background: white;
  border-right: 1px solid #f3f4f6;
  height: 100%;
}

.grid-cell.weekend {
  background: #fafafa;
}

.grid-cell.today {
  background: #f0f9ff;
}

/* Task Bars */
.task-bars {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.task-bar {
  position: absolute;
  height: 24px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  padding: 0 8px;
  pointer-events: auto;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  z-index: 3;
  min-width: 20px;
  font-size: 0.75rem;
  font-weight: 500;
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.task-bar:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 4;
}

.task-text {
  font-size: 0.75rem;
  font-weight: 500;
  color: white;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

/* Responsive design */
@media (max-width: 768px) {
  .team-schedule-container {
    padding: 1rem;
    margin: 0.5rem 0;
  }

  .schedule-title {
    font-size: 1.25rem;
  }

  .gantt-chart {
    min-width: 600px;
  }

  .member-column,
  .member-info {
    width: 150px;
    min-width: 150px;
  }

  .month-cell,
  .grid-cell {
    width: 80px;
    min-width: 80px;
  }

  .member-avatar {
    width: 24px;
    height: 24px;
    font-size: 0.625rem;
  }

  .member-name {
    font-size: 0.75rem;
  }

  .member-task-count {
    font-size: 0.625rem;
  }

  .task-text {
    font-size: 0.625rem;
  }

  .gantt-row {
    min-height: 50px;
  }

  .task-bar {
    height: 20px;
  }
}
</style>