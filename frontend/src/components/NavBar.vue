<template>
    <nav class="navbar">
      <div class="container navbar-container">
        <router-link to="/" class="navbar-logo">
         Task Quest
        </router-link>
        
        <div class="navbar-right">
          <router-link to="/" class="navbar-link">Home</router-link>
          <router-link to="/projects" class="navbar-link">All Projects</router-link>
          <router-link to="" class="navbar-link">Link 2</router-link>
          <router-link to="" class="navbar-link">My Schedule</router-link>
          <button @click="logout" class="logout-btn">Logout</button>
        </div>
        
      </div>
    </nav>
    
    
  </template>

  <script>
  import authService from '@/services/auth'

  export default {
    name: 'NavBar',
    methods: {
      logout() {
        authService.logout();
        this.$router.push('/login');
      }
    }
  }
  </script>

  <style scoped>
  .navbar {
    position: sticky;
    top: 0;
    z-index: 50;
    background-color: rgba(255, 255, 255, 0.85);
    backdrop-filter: saturate(180%) blur(10px);
    -webkit-backdrop-filter: saturate(180%) blur(10px);
    border-bottom: 1px solid #e5e7eb;
  }
  
  .navbar-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 64px;
  }

  .navbar-right {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .navbar-actions {
    display: flex;
    align-items: center;
  }

  
  .navbar-logo {
    font-size: 1.1rem;
    font-weight: 800;
    letter-spacing: 0.2px;
    color: #111827;
  }
  
  .navbar-links {
    display: flex;
    gap: 1rem;
  }
  
  .navbar-link {
    color: #4b5563;
    font-weight: 600;
    padding: 0.4rem 0.6rem;
    border-radius: 8px;
    transition: color 0.2s, background-color 0.2s;
    text-decoration: none;
  }

  .logout-btn {
    background: #dc2626;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    font-family: inherit;
    font-size: 0.875rem;
  }

  
  /* .navbar-link:hover, .navbar-link.router-link-active {
    color: #111827;
    background: #f3f4f6;
  } */
  
  @media (max-width: 768px) {
    .navbar-links {
      display: none;
    }
  }
  </style>