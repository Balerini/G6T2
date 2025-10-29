
<template>
    <div id="app">
      <NavBar v-if="$route.meta.showNav" />
      <router-view />
    </div>
</template>


<script>
import NavBar from '@/components/NavBar.vue';
  

export default {
  name: 'App',
  components: {
    NavBar
  }
}
</script>

<style>
/* Global CSS */
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }
  
  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    color: #333;
    background-color: #f9f9f9;
  }
  
  #app {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }
  
  button, input, select, textarea {
    font-family: inherit;
  }
  
  a {
    color: inherit;
    text-decoration: none;
  }
  
  .container {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
  }
  
  @media (max-width: 768px) {
    .container {
      padding: 0 0.75rem;
    }
  }

  /* Global Mobile Utilities */
  @media (max-width: 768px) {
    /* Touch-friendly buttons */
    button,
    .btn,
    a[role="button"] {
      min-height: 44px; /* iOS recommended touch target size */
      min-width: 44px;
    }

    /* Prevent text selection issues on mobile */
    input,
    textarea,
    select {
      font-size: 16px; /* Prevents zoom on iOS */
    }

    /* Improved scrolling */
    * {
      -webkit-overflow-scrolling: touch;
    }
  }

  @media (max-width: 480px) {
    /* Extra small screens */
    .container {
      padding: 0 0.5rem;
    }

    button,
    .btn,
    a[role="button"] {
      padding: 0.625rem 1rem;
      font-size: 0.875rem;
    }
  }
</style>
