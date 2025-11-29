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
}
</style>
