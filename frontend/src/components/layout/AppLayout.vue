<template>
  <div class="app-layout">
    <AppHeader />
    <main class="content-area">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import AppHeader from './AppHeader.vue'
</script>

<style scoped lang="scss">
.app-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100%;
}

.content-area {
  flex-grow: 1;
  margin-top: 60px;
  overflow-y: auto;
  background-color: #ffffff;
  transition: padding 0.3s ease;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .content-area {
    margin-top: 60px;
  }
}
</style>
