import { createRouter, createWebHistory } from 'vue-router';

import Login from '../views/Login.vue';
import Home from '../views/Home.vue';
import Tasks from '../views/Tasks.vue';
import CreateTask from '../views/CreateTask.vue'

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
    path: '/tasks',
    name: 'tasks',
    component: Tasks,
    meta: { showNav: true }
  },
  {
    path: '/createtask',
    name: 'createtask',
    component: CreateTask,
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