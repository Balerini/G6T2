import { createRouter, createWebHistory } from 'vue-router';

import Login from '../views/Login.vue';
import Home from '../views/Home.vue';
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
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

  const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;