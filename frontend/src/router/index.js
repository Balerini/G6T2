import { createRouter, createWebHistory } from 'vue-router';

import Login from '../views/Login.vue';
import Home from '../views/Home.vue';
import Projects from '../views/Projects.vue';
import Createtask from '../views/CreateTask.vue'
import ViewTaskDetails  from '../views/ViewTaskDetails.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: Home,
    meta: { showNav: true }
  },
  {
    path: '/login',
    name: 'login',
    component: Login
  },
  {
    path: '/projects',
    name: 'projects',
    component: Projects,
    meta: { showNav: true }
  },
  {
    path: '/createtask',
    name: 'createtask',
    component: Createtask,
    meta: { showNav: true }
  },
  {
    path: '/projects/:projectId/task/:taskId',
    name: 'viewtaskdetails',
    component: ViewTaskDetails,
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

export default router;