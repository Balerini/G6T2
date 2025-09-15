<template>
  <div class="login-page">
    <div class="login-wrapper">
      <div class="brand">
        <h1 class="brand-title">Task Quest</h1>
        <p class="brand-subtitle">Sign in to manage your tasks efficiently</p>
      </div>

      <div class="card">
        <h2 class="card-title">Welcome back</h2>
        <p class="card-subtitle">Please sign in to continue</p>

        <div class="form-group">
          <label for="email">Email</label>
          <input
            type="email"
            id="email"
            v-model="email"
            placeholder="name@example.com"
            class="form-control"
          />
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input
            type="password"
            id="password"
            v-model="password"
            placeholder="••••••••"
            class="form-control"
          />
        </div>

        <button @click="login" class="btn-primary">Sign In</button>

        <div class="divider">
          <span>or</span>
        </div>

        <div class="register">
          <span>New here?</span>
          <router-link to="/register" class="link">Create an account</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return {
      email: '',
      password: ''
    }
  },
  methods: {
    login() {
      // Placeholder action for now
      if (!this.email || !this.password) {
        alert('Please enter email and password');
        return;
      }
      // Replace with real auth flow later
      this.$router.push('/');
    }
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #eef2ff 0%, #fdf2f8 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
}

.login-wrapper {
  width: 100%;
  max-width: 960px;
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 2rem;
  align-items: center;
}

.brand {
  padding: 1rem 0;
}

.brand-title {
  font-size: 2.25rem;
  line-height: 1.2;
  font-weight: 800;
  color: #111827;
  margin-bottom: 0.5rem;
}

.brand-subtitle {
  color: #6b7280;
}

.card {
  background: #ffffff;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 10px 25px rgba(17, 24, 39, 0.08);
  border: 1px solid #f3f4f6;
}

.card-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
}

.card-subtitle {
  color: #6b7280;
  margin-top: 0.25rem;
  margin-bottom: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 1rem;
}

label {
  font-size: 0.875rem;
  color: #374151;
  margin-bottom: 0.375rem;
}

.form-control {
  appearance: none;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 0.75rem 1rem;
  outline: none;
  background: #fff;
  color: #111827;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-control:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.15);
}

.btn-primary {
  width: 100%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-radius: 10px;
  background: #111827;
  color: #fff;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: transform 0.05s ease-in, background-color 0.2s;
}

.btn-primary:hover {
  background: #1f2937;
}

.btn-primary:active {
  transform: translateY(1px);
}

.divider {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 1.25rem 0;
  color: #9ca3af;
  font-size: 0.875rem;
}

.divider::before,
.divider::after {
  content: '';
  height: 1px;
  background: #e5e7eb;
  flex: 1;
}

.register {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: #6b7280;
}

.link {
  color: #4f46e5;
  font-weight: 600;
}

@media (max-width: 900px) {
  .login-wrapper {
    grid-template-columns: 1fr;
  }
  .brand {
    text-align: center;
  }
}
</style>
