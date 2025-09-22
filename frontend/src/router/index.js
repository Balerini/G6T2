import { createRouter, createWebHistory } from 'vue-router';
import authService from '../services/auth';

import Login from '../views/Login.vue';
import Home from '../views/Home.vue';
import Projects from '../views/Projects.vue';
import Createtask from '../views/CreateTask.vue'
import ViewTaskDetails  from '../views/ViewTaskDetails.vue'
import ViewOwnTasks from '../views/ViewOwnTasks.vue'

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
    path: '/projects',
    name: 'projects',
    component: Projects,
    meta: { showNav: true,requiresAuth: true }
  },

  {
    path: '/createtask',
    name: 'createtask',
    component: Createtask,
    meta: { showNav: true,requiresAuth: true }
  },
  {
    path: '/projects/:projectId/tasks/:taskId',
    name: 'viewtaskdetails',
    component: ViewTaskDetails,
    meta: { showNav: true }
  },
  {
    path: '/owntasks',
    name: 'owntasks',
    component: ViewOwnTasks,
    meta: { showNav: true }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
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
  } else if (to.path === '/login' && isLoggedIn) {
    // Redirect to home if trying to access login page while already logged in
    next('/');
  } else {
    // Allow navigation
    next();
  }
});

export default router;