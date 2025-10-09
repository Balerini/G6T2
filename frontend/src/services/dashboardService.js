import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const dashboardService = {

    // ============================== MANAGERS ==============================

    // MANAGERS: COUNT TOTAL NUMBER OF TASKS OF TEAM
    getCountofAllTasksByTeam: async (userId) => {
        try {
            const response = await api.get(`/api/dashboard/manager/total-tasks/${userId}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching manager total tasks:', error);
            throw error;
        }
    },

    // MANAGERS: COUNT TASKS BY STATUS
    getCountofAllTasksByStatus: async (userId) => {
        try {
            const response = await api.get(`/api/dashboard/manager/tasks-by-status/${userId}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching tasks by status:', error);
            throw error;
        }
    },

    // MANAGERS: GET COUNT OF TASKS BASED ON PRIORITY 
    getCountofAllTasksByPriority: async (userId) => {
        try {
            const response = await api.get(`/api/dashboard/manager/tasks-by-priority/${userId}`);
            return response.data
        } catch (error) {
            console.log("Error fetching tasks by priority", error)
        }
    },

    // MANAGERS: COUNT AND NAME OF TASKS BY STAFF MEMBER
    getCountAndNameofTasksByStaff: async (userId) => {
        try {
            const response = await api.get(`/api/dashboard/manager/tasks-by-staff/${userId}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching tasks by staff:', error);
            throw error;
        }
    },

    // MANAGERS: PENDING TASKS BY AGE AND TASK NAME BASED ON TASK START DATE
    getPendingTasksByAgeAndStaffName: async (userId) => {
        try {
            const response = await api.get(`/api/dashboard/manager/pending-tasks-by-age/${userId}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching pending tasks by age:', error);
            throw error;
        }
    },

    // HELPER FUNCTION TO GET USER INFO 
    debugUserData: async (userId) => {
        try {
            const response = await api.get(`/api/dashboard/debug/user/${userId}`);
            return response.data;
        } catch (error) {
            console.error('Error in debug endpoint:', error);
            throw error;
        }
    },

    // HELPER FUNCTION TO GET DEPARTMENT STAFF
}