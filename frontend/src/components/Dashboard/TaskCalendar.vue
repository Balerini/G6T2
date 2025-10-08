<template>
    <div>
        <h3 class="section-title">Task Calendar</h3>
        <div v-if="loading" class="loading">Loading...</div>
        <div v-else-if="error" class="error">Error: {{ error }}</div>
        <div v-else class="calendar-card">
            <FullCalendar :options="calendarOptions" />
        </div>
    </div>
</template>

<script>
import { dashboardService } from '@/services/dashboardService';
import FullCalendar from '@fullcalendar/vue3';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';

export default {
    name: 'TaskCalendar',
    components: {
        FullCalendar
    },
    data() {
        return {
            data: {},
            loading: true,
            error: null,
            calendarOptions: {
                plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin],
                initialView: 'dayGridMonth',
                headerToolbar: {
                    left: 'prev,next today',
                    center: 'title',
                    right: 'dayGridMonth,timeGridWeek,timeGridDay'
                },
                events: [],
                eventClick: this.handleEventClick,
                height: 'auto',
                eventTimeFormat: {
                    hour: '2-digit',
                    minute: '2-digit',
                    meridiem: false
                }
            }
        };
    },
    async mounted() {
        try {
            const userStr = sessionStorage.getItem('user');
            if (!userStr) {
                this.error = 'User not found';
                this.loading = false;
                return;
            }

            const user = JSON.parse(userStr);
            const userId = user.id;
            console.log('TaskCalendar - User ID:', userId);

            this.data = await dashboardService.getPendingTasksByAgeAndStaffName(userId);
            console.log('TaskCalendar - Response:', this.data);

            if (this.data.pending_tasks_by_age) {
                this.processCalendarEvents();
            }

            this.loading = false;
        } catch (err) {
            console.error('TaskCalendar - Error:', err);
            this.error = err.message;
            this.loading = false;
        }
    },
    methods: {
        processCalendarEvents() {
            const events = [];
            const allCategories = this.data.pending_tasks_by_age;

            Object.keys(allCategories).forEach(category => {
                const tasks = allCategories[category];

                tasks.forEach(task => {
                    let color = '#3b82f6';

                    if (task.days_until_due < 0) {
                        color = '#dc2626';
                    } else if (task.days_until_due === 0) {
                        color = '#ea580c';
                    } else if (task.days_until_due <= 1) {
                        color = '#ca8a04';
                    } else if (task.days_until_due <= 3) {
                        color = '#d97706';
                    } else if (task.days_until_due <= 7) {
                        color = '#2563eb';
                    } else {
                        color = '#059669';
                    }

                    events.push({
                        id: task.task_id,
                        title: task.task_name,
                        start: task.end_date,
                        allDay: true,
                        backgroundColor: color,
                        borderColor: color,
                        extendedProps: {
                            assignee: task.assigned_to_name,
                            priority: task.priority_level,
                            status: task.task_status,
                            daysUntilDue: task.days_until_due,
                            proj_id: task.proj_id,
                            task_id: task.task_id
                        }
                    });
                });
            });

            this.calendarOptions.events = events;
        },
        handleEventClick(info) {
            const props = info.event.extendedProps;

            // Check if we have the required IDs
            if (props.proj_id && props.task_id) {
                this.$router.push(`/projects/${props.proj_id}/tasks/${props.task_id}`);
            } else {
                console.error('Missing project or task ID:', props);
                alert('Cannot navigate to task details - missing project or task ID');
            }
        },
        // Add this helper method to get color for specific status
        getStatusColor(status) {
            const colorMap = {
                'Not Started': '#f87171',
                'In Progress': '#fbbf24',
                'Completed': '#34d399',
                'Pending': '#fb923c'
            };
            return colorMap[status] || '#9ca3af'; // gray as default
        }
    }
};
</script>

<style scoped>
.section-title {
    font-size: 20px;
    font-weight: 600;
    color: #111827;
    margin-bottom: 20px;
}

.calendar-card {
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border: 1px solid #e5e7eb;
}

.loading,
.error {
    color: #6b7280;
    font-size: 14px;
    margin: 10px;
}

.error {
    color: #dc2626;
}
</style>

<style>
.fc {
    font-family: inherit;
}

.fc .fc-button-primary {
    background-color: #111827;
    border-color: #111827;
}

.fc .fc-button-primary:hover {
    background-color: #374151;
    border-color: #374151;
}

.fc .fc-button-primary:not(:disabled).fc-button-active {
    background-color: #374151;
    border-color: #374151;
}

.fc-event {
    cursor: pointer;
    font-size: 12px;
    padding: 2px 4px;
}

.fc-daygrid-event {
    white-space: normal;
}
</style>