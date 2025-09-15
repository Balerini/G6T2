<template>
  <div class="home">
    <section class="hero">
      <div class="container">
        <h1 class="hero-title">Stay organized. Get more done.</h1>
        <p class="hero-subtitle">A clean and simple task manager to help your team focus.</p>
      </div>
    </section>

    <section class="features">
      <div class="container grid">
        <div class="feature-card">
          <div class="feature-icon">✓</div>
          <h3 class="feature-title">Easy tracking</h3>
          <p class="feature-text">Create, assign, and track tasks with clarity and speed.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">⚡</div>
          <h3 class="feature-title">Fast and responsive</h3>
          <p class="feature-text">Built with modern tech for smooth performance across devices.</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🔒</div>
          <h3 class="feature-title">Secure by design</h3>
          <p class="feature-text">Your data stays private with best-practice security.</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: 'Home',
  methods: {
    learnMore() {
      window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    }
  }
}
</script>

<style scoped>
.home {
}

.container {
  width: 100%;
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 1rem;
}

.hero {
  padding: 4rem 0 3rem;
  background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%);
  border-bottom: 1px solid #e5e7eb;
}

.hero-title {
  font-size: 2.25rem;
  line-height: 1.2;
  font-weight: 800;
  color: #111827;
  margin-bottom: 0.5rem;
}

.hero-subtitle {
  color: #6b7280;
  margin-bottom: 1.25rem;
}

.hero-actions {
  display: flex;
  gap: 0.75rem;
}

.btn-dark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.625rem 1rem;
  background: #111827;
  color: #fff;
  border-radius: 10px;
  font-weight: 600;
}

.btn-light {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.625rem 1rem;
  background: #fff;
  color: #111827;
  border-radius: 10px;
  font-weight: 600;
  border: 1px solid #e5e7eb;
}

.features {
  padding: 2.5rem 0 3rem;
}

.grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
}

.feature-card {
  background: #fff;
  border: 1px solid #f3f4f6;
  border-radius: 14px;
  padding: 1.25rem;
  box-shadow: 0 10px 25px rgba(17, 24, 39, 0.06);
}

.feature-icon {
  font-size: 1.5rem;
}

.feature-title {
  margin-top: 0.5rem;
  font-weight: 700;
  color: #111827;
}

.feature-text {
  color: #6b7280;
  margin-top: 0.25rem;
}

@media (max-width: 900px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
