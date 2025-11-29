<template>
  <div class="app-layout">
    <AppSidebar />
    <div class="content-area">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import AppSidebar from './AppSidebar.vue'
</script>

<style scoped lang="scss">
.app-layout {
  display: flex;
  height: 100vh;
  width: 100%;
}

.content-area {
  flex-grow: 1;
  margin-left: 60px;
  padding: 20px;
  overflow-y: auto;
  background-color: #f0f2f5;
  transition: margin-left 0.3s ease, padding 0.3s ease;
}

/* 响应式设计 */

/* 移动端 (<768px) */
@media (max-width: 767px) {
  .content-area {
    margin-left: 0;
    padding: 10px;
  }
}

/* 平板 (768px-1024px) */
@media (min-width: 768px) and (max-width: 1023px) {
  .content-area {
    margin-left: 60px;
    padding: 15px;
  }
}

/* 桌面 (>=1024px) - 保持原有样式 */
@media (min-width: 1024px) {
  .content-area {
    margin-left: 60px;
    padding: 20px;
  }
}
</style>
