<template>
    <div>
        <div class="container">
            <div class="header-section">
                <h3 class="section-title">Task Calendar</h3>

                <!-- Tab Buttons -->
                <div class="action-tabs">
                    <button :class="['tab-btn', { active: activeTab === 'team' }]" @click="activeTab = 'team'">
                        Team Tasks
                    </button>
                    <button :class="['tab-btn', { active: activeTab === 'my' }]" @click="activeTab = 'my'">
                        My Tasks
                    </button>
                </div>

                <div v-if="loading" class="loading">Loading...</div>
                <div v-else-if="error" class="error">Error: {{ error }}</div>
                <div v-else class="calendar-card">
                    <FullCalendar :options="calendarOptions" />
                </div>
            </div>
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
            activeTab: 'team',
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

            if (props.proj_id && props.task_id) {
                this.$router.push(`/projects/${props.proj_id}/tasks/${props.task_id}`);
            } else {
                console.error('Missing project or task ID:', props);
                alert('Cannot navigate to task details - missing project or task ID');
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
.container {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
}

.section-title {
    font-size: 2.25rem;
    line-height: 1.2;
    font-weight: 800;
    color: #111827;
    margin: 0 0 1.5rem 0;
}

.header-section {
    background: #fff;
    border-bottom: 1px solid #e5e7eb;
    padding: 1.5rem 0;
}

.hero-title {
    font-size: 2.25rem;
    line-height: 1.2;
    font-weight: 800;
    color: #111827;
    margin: 0;
}

.action-tabs {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin-bottom: 1.5rem;
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

.tab-btn.active {
    background: #111827;
    color: #fff;
    border-color: #111827;
}

.tab-btn:hover {
    background: #f9fafb;
}

.tab-btn.active:hover {
    background: #374151;
}

.calendar-card {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border: 1px solid #e5e7eb;
}

.loading,
.error {
    color: #6b7280;
    font-size: 0.875rem;
    margin: 1rem 0;
}

.error {
    color: #dc2626;
}

@media (max-width: 768px) {
    .action-tabs {
        flex-direction: column;
        width: 100%;
    }

    .tab-btn {
        width: 100%;
    }

    .calendar-wrapper {
        padding: 0;
    }

    .calendar-card {
        padding: 1rem;
    }
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