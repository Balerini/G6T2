import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Helper function to determine user role
const getUserRole = () => {
    try {
        const userStr = sessionStorage.getItem('user');
        if (!userStr) {
            console.log('getUserRole: No user in session storage');
            return null;
        }
        const user = JSON.parse(userStr);
        console.log('getUserRole: user object:', user);

        let roleNum = user.role_num;

        // Convert string to number if needed
        if (typeof roleNum === 'string') {
            roleNum = parseInt(roleNum);
        }

        // Fallback: derive from role_name if role_num is missing
        if (!roleNum && user.role_name) {
            const roleName = user.role_name.toLowerCase();
            if (roleName === 'staff') roleNum = 4;
            else if (roleName === 'manager') roleNum = 3;
            else if (roleName === 'director') roleNum = 2;
            console.log('getUserRole: Derived from role_name:', roleNum);
        }

        console.log('getUserRole: final role_num:', roleNum);
        return roleNum;
    } catch (error) {
        console.error('Error getting user role:', error);
        return null;
    }
};

export const dashboardService = {

    // ============================== MANAGERS & STAFF ==============================

    // COUNT TOTAL NUMBER OF TASKS (Auto-selects endpoint based on role)
    getCountofAllTasksByTeam: async (userId) => {
        try {
            const roleNum = getUserRole();
            const endpoint = roleNum === 4
                ? `/api/dashboard/staff/total-tasks/${userId}`
                : `/api/dashboard/manager/total-tasks/${userId}`;

            console.log(`getCountofAllTasksByTeam: roleNum=${roleNum}, endpoint=${endpoint}`);
            const response = await api.get(endpoint);
            return response.data;
        } catch (error) {
            console.error('Error fetching total tasks:', error);
            console.error('Error response:', error.response?.data);
            throw error;
        }
    },

    // COUNT TASKS BY STATUS (Auto-selects endpoint based on role)
    getCountofAllTasksByStatus: async (userId) => {
        try {
            const roleNum = getUserRole();
            const endpoint = roleNum === 4
                ? `/api/dashboard/staff/tasks-by-status/${userId}`
                : `/api/dashboard/manager/tasks-by-status/${userId}`;

            console.log(`getCountofAllTasksByStatus: roleNum=${roleNum}, endpoint=${endpoint}`);
            const response = await api.get(endpoint);
            return response.data;
        } catch (error) {
            console.error('Error fetching tasks by status:', error);
            throw error;
        }
    },

    // GET COUNT OF TASKS BASED ON PRIORITY (Auto-selects endpoint based on role)
    getCountofAllTasksByPriority: async (userId) => {
        try {
            const roleNum = getUserRole();
            const endpoint = roleNum === 4
                ? `/api/dashboard/staff/tasks-by-priority/${userId}`
                : `/api/dashboard/manager/tasks-by-priority/${userId}`;

            console.log(`getCountofAllTasksByPriority: roleNum=${roleNum}, endpoint=${endpoint}`);
            const response = await api.get(endpoint);
            return response.data;
        } catch (error) {
            console.log("Error fetching tasks by priority", error);
            throw error;
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

    // PENDING TASKS BY AGE (Auto-selects based on role)
    getPendingTasksByAgeAndStaffName: async (userId) => {
        try {
            const roleNum = getUserRole();
            const endpoint = roleNum === 4
                ? `/api/dashboard/staff/pending-tasks-by-age/${userId}`
                : `/api/dashboard/manager/pending-tasks-by-age/${userId}`;

            console.log(`getPendingTasksByAge: roleNum=${roleNum}, endpoint=${endpoint}`);
            const response = await api.get(endpoint);
            return response.data;
        } catch (error) {
            console.error('Error fetching pending tasks by age:', error);
            console.error('403 error? Using wrong endpoint. roleNum should be 4 for staff');
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

    // GET MANAGER'S TEAM'S TASK TIMELINE - TRACK TEAM TASK SCHEDULE 
    getDepartmentStaffTasksTimeline: async (userId) => {
        try {
            const endpoint = `/api/dashboard/manager/tasks-timeline/${userId}`;
            console.log(`getDepartmentStaffTasksTimeline: endpoint=${endpoint}`);
            const response = await api.get(endpoint);
            console.log("department staff task timeline", response); 
            return response.data;
        } catch (error) {
            console.error('Error fetching manager tasks timeline:', error);
            if (error.response?.status === 403) {
                console.error('403 error: User is not authorized as a manager');
            }
            throw error;
        }
    },
}