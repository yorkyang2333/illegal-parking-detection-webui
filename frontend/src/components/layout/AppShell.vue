<template>
  <div class="app-shell">
    <TopNav />
    <main class="app-shell__content">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import TopNav from './TopNav.vue'
</script>

<style scoped lang="scss">
.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-shell__content {
  flex: 1;
  width: 100%;
  max-width: var(--content-max-width);
  margin: 0 auto;
  padding: var(--space-xl) var(--space-lg);

  @media (max-width: 767px) {
    padding: var(--space-md);
  }
}
</style>
