<template>
    <div class="calendar-wrapper">
        <!-- Tab Buttons (only show for managers) -->
        <div class="tabs-container" v-if="isManager">
            <div class="action-tabs">
                <button :class="['tab-btn', { active: activeTab === 'team' }]" @click="activeTab = 'team'">
                    <span class="tab-icon">👥</span>
                    Team Tasks
                </button>
                <button :class="['tab-btn', { active: activeTab === 'my' }]" @click="activeTab = 'my'">
                    <span class="tab-icon">👤</span>
                    My Tasks
                </button>
            </div>
        </div>

        <!-- Calendar Content -->
        <div v-if="loading" class="loading-state">
            <div class="loading-spinner"></div>
            <p>Loading your schedule...</p>
        </div>
        <div v-else-if="error" class="error-state">
            <span class="error-icon">⚠️</span>
            <p>{{ error }}</p>
        </div>
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
            activeTab: this.getDefaultTab(),
            allEvents: [],
            myEvents: [],
            currentUserId: null,
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
    computed: {
        isManager() {
            try {
                const userStr = sessionStorage.getItem('user');
                if (userStr) {
                    const user = JSON.parse(userStr);
                    // Managers have role_num < 4
                    return user.role_num && user.role_num < 4;
                }
            } catch (error) {
                console.error('Error checking if user is manager:', error);
            }
            return false;
        }
    },
    watch: {
        activeTab(newTab) {
            this.updateCalendarEvents(newTab);
        }
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
            this.currentUserId = user.id;
            console.log('TaskCalendar - User ID:', this.currentUserId);

            this.data = await dashboardService.getPendingTasksByAgeAndStaffName(this.currentUserId);
            console.log('TaskCalendar - Response:', this.data);

            if (this.data.pending_tasks_by_age) {
                this.processCalendarEvents();
                this.updateCalendarEvents(this.activeTab);
            }

            this.loading = false;
        } catch (err) {
            console.error('TaskCalendar - Error:', err);
            this.error = err.message;
            this.loading = false;
        }
    },
    methods: {
        getDefaultTab() {
            // Get current user to determine default tab
            try {
                const userStr = sessionStorage.getItem('user');
                if (userStr) {
                    const user = JSON.parse(userStr);
                    // Staff (role_num = 4) should see "My Tasks" by default
                    // Managers should see "Team Tasks"
                    return user.role_num === 4 ? 'my' : 'team';
                }
            } catch (error) {
                console.error('Error getting user for default tab:', error);
            }
            return 'team'; // Default fallback
        },
        processCalendarEvents() {
            const allEvents = [];
            const myEvents = [];
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

                    const event = {
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
                            task_id: task.task_id,
                            assigned_to_id: task.assigned_to_id
                        }
                    };

                    allEvents.push(event);

                    // Check if task is assigned to current user
                    if (task.assigned_to_id === this.currentUserId) {
                        myEvents.push(event);
                    }
                });
            });

            this.allEvents = allEvents;
            this.myEvents = myEvents;
        },
        updateCalendarEvents(tab) {
            if (tab === 'team') {
                this.calendarOptions.events = this.allEvents;
            } else {
                this.calendarOptions.events = this.myEvents;
            }
        },
        handleEventClick(info) {
            const props = info.event.extendedProps;
            
            console.log('Calendar event clicked:', props);

            if (!props.task_id) {
                console.error('Missing task ID:', props);
                alert('Cannot navigate to task details - missing task ID');
                return;
            }

            // Navigate to task details (with or without project) from schedule
            if (props.proj_id) {
                // Task belongs to a project
                console.log(`Navigating to project task: /projects/${props.proj_id}/tasks/${props.task_id}`);
                window.location.href = `/projects/${props.proj_id}/tasks/${props.task_id}?from=schedule`;
            } else {
                // Standalone task
                console.log(`Navigating to standalone task: /tasks/${props.task_id}`);
                window.location.href = `/tasks/${props.task_id}?from=schedule`;
            }
        },
        getStatusColor(status) {
            const colorMap = {
                'Not Started': '#f87171',
                'In Progress': '#fbbf24',
                'Completed': '#34d399',
                'Pending': '#fb923c'
            };
            return colorMap[status] || '#9ca3af';
        }
    }
};
</script>

<style scoped>
.calendar-wrapper {
    width: 100%;
}

.tabs-container {
    background: white;
    border-radius: 12px 12px 0 0;
    padding: 1.5rem 1.5rem 0 1.5rem;
    border: 1px solid #e5e7eb;
    border-bottom: none;
}

.action-tabs {
    display: flex;
    gap: 0.5rem;
}

.tab-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    border: 1px solid #e5e7eb;
    background: #f9fafb;
    color: #6b7280;
    border-radius: 8px 8px 0 0;
    font-weight: 600;
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.2s ease;
    border-bottom: none;
}

.tab-btn:hover {
    background: #f3f4f6;
    color: #374151;
}

.tab-btn.active {
    background: white;
    color: #111827;
    border-color: #e5e7eb;
    border-bottom: 2px solid white;
    margin-bottom: -1px;
}

.tab-icon {
    font-size: 1rem;
}

.calendar-card {
    background: white;
    border-radius: 0 12px 12px 12px;
    padding: 2rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    border: 1px solid #e5e7eb;
}

.loading-state,
.error-state {
    background: white;
    border-radius: 12px;
    padding: 4rem 2rem;
    text-align: center;
    border: 1px solid #e5e7eb;
}

.loading-spinner {
    width: 48px;
    height: 48px;
    border: 4px solid #f3f4f6;
    border-top-color: #6366f1;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 1rem auto;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

.loading-state p {
    color: #6b7280;
    font-size: 0.875rem;
    margin: 0;
}

.error-state {
    color: #dc2626;
}

.error-icon {
    font-size: 3rem;
    display: block;
    margin-bottom: 1rem;
}

.error-state p {
    color: #dc2626;
    font-size: 0.875rem;
    margin: 0;
    font-weight: 500;
}

@media (max-width: 768px) {
    .tabs-container {
        padding: 1rem 1rem 0 1rem;
    }
    
    .action-tabs {
        flex-direction: column;
        gap: 0.25rem;
    }

    .tab-btn {
        width: 100%;
        justify-content: center;
        border-radius: 8px;
    }

    .calendar-card {
        padding: 1rem;
        border-radius: 12px;
    }
}
</style>

<style>
.fc {
    font-family: inherit;
}

.fc .fc-toolbar-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #111827;
}

.fc .fc-button-primary {
    background-color: #111827;
    border-color: #111827;
    font-weight: 600;
    text-transform: capitalize;
    padding: 0.5rem 1rem;
    border-radius: 8px;
}

.fc .fc-button-primary:hover {
    background-color: #374151;
    border-color: #374151;
}

.fc .fc-button-primary:not(:disabled).fc-button-active {
    background-color: #6366f1;
    border-color: #6366f1;
}

.fc .fc-button-primary:focus {
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
}

.fc-event {
    cursor: pointer;
    font-size: 0.75rem;
    padding: 4px 6px;
    border-radius: 4px;
    font-weight: 600;
    transition: all 0.2s ease;
}

.fc-event:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.fc-daygrid-event {
    white-space: normal;
}

.fc .fc-daygrid-day-number {
    font-weight: 600;
    color: #374151;
}

.fc .fc-col-header-cell-cushion {
    font-weight: 700;
    color: #111827;
    text-transform: uppercase;
    font-size: 0.75rem;
    letter-spacing: 0.5px;
}

.fc .fc-daygrid-day.fc-day-today {
    background-color: #f0f9ff !important;
}

.fc .fc-daygrid-day.fc-day-today .fc-daygrid-day-number {
    background: #6366f1;
    color: white;
    border-radius: 50%;
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 4px;
}
</style>