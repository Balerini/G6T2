import { createRouter, createWebHistory } from 'vue-router';
import authService from '../services/auth';

import Login from '../views/Login.vue';
import Register from '../views/Register.vue';
import Home from '../views/Home.vue';
import MySchedule from '../views/MySchedule.vue';
import Projects from '../views/Projects.vue';
import Createtask from '../views/CreateTask.vue'
import CreateProject from '../views/CreateProject.vue'
import ViewTaskDetails from '../views/ViewTaskDetails.vue'
import Notifications from '../views/Notifications.vue'
import ViewProject from '../views/ViewProjectDetails.vue';
import ForgotPassword from '@/components/ForgotPassword.vue';
import ResetPassword from '@/components/ResetPassword.vue';
import ManagerViewTeamTaskSchedule from '@/components/Dashboard/ManagerViewTeamTaskSchedule.vue';
// import ViewOwnTasks from '../views/ViewOwnTasks.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: Home,
    meta: { showNav: true, requiresAuth: true }
  },
  {
    path: '/login',
    name: 'login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'register',
    component: Register,
    meta: { requiresAuth: false }
  },
  {
    path: '/projects',
    name: 'projects',
    component: Projects,
    meta: { showNav: true, requiresAuth: true }
  },
  {
    path: '/projects/:project_id',
    name: 'ViewProject',
    component: ViewProject,
    meta: { showNav: true, requiresAuth: true }
  },
  {
    path: '/createproject',
    name: 'createproject',
    component: CreateProject,
    meta: { showNav: true, requiresAuth: true }
  },
  {
    path: '/createtask',
    name: 'createtask',
    component: Createtask,
    meta: { showNav: true, requiresAuth: true }
  },
  {
    path: '/projects/:projectId/tasks/:taskId',
    name: 'viewtaskdetails',
    component: ViewTaskDetails,
    meta: { showNav: true }
  },
  {
    path: '/tasks/:taskId',
    name: 'viewstandalonetask',
    component: ViewTaskDetails,
    meta: { showNav: true }
  },
  {
    path: '/my-schedule',
    name: 'myschedule',
    component: MySchedule,
    meta: { showNav: true, requiresAuth: true }
  },
  {
    path: '/manager/schedule/:userid',
    component: ManagerViewTeamTaskSchedule,
    meta: { showNav: true, requiresAuth: true }
  },
  {
    path: '/notifications',
    name: 'notifications',
    component: Notifications,
    meta: { showNav: true, requiresAuth: true }
  },
  // {
  //   path: '/owntasks',
  //   name: 'owntasks',
  //   component: ViewOwnTasks,
  //   meta: { showNav: true }
  // },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: ForgotPassword
  },
  {
    path: '/reset-password',
    name: 'ResetPassword',
    component: ResetPassword
  }

]

const router = createRouter({
  history: createWebHistory(),
  routes
});

// Navigation guard to check authentication
router.beforeEach((to, from, next) => {
  // Check if route requires authentication
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);

  // Check if user is logged in
  const isLoggedIn = authService.checkAuthStatus();

  if (requiresAuth && !isLoggedIn) {
    // Redirect to login if trying to access protected route without being logged in
    next('/login');
  } else if ((to.path === '/login' || to.path === '/register') && isLoggedIn) {
    // Redirect to home if trying to access login/register page while already logged in
    next('/');
  } else {
    // Allow navigation
    next();
  }
});

export default router;