<template>
  <div v-if="isLoading" class="loading-screen">
    <div class="loading-spinner" />
    <p class="loading-text">加载中...</p>
  </div>
  <AppShell v-else-if="isAuthenticated" />
  <router-view v-else />
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/useAuthStore'
import AppShell from '@/components/layout/AppShell.vue'

const authStore = useAuthStore()
const isLoading = ref(true)

const isAuthenticated = computed(() => authStore.isAuthenticated)

onMounted(async () => {
  await authStore.checkAuth()
  isLoading.value = false
})
</script>

<style scoped lang="scss">
.loading-screen {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--color-hairline);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: var(--space-md);
}

.loading-text {
  font-size: 14px;
  color: var(--color-muted);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
