<template>
    <nav class="navbar">
      <div class="container navbar-container">
        <router-link to="/" class="navbar-logo">
         Task Quest
        </router-link>
        
        <div class="navbar-links">
          <router-link to="/" class="navbar-link">Home</router-link>
          <router-link to="" class="navbar-link">Link1</router-link>
          <router-link to="" class="navbar-link">Link2</router-link>
          <router-link to="" class="navbar-link">Link3</router-link>
        </div>
        
      </div>
    </nav>
    
  </template>
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
  }
  
  .navbar-link:hover, .navbar-link.router-link-active {
    color: #111827;
    background: #f3f4f6;
  }
  
  @media (max-width: 768px) {
    .navbar-links {
      display: none;
    }
  }
  </style>