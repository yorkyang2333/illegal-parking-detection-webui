<template>
  <div v-if="isLoading" class="loading-screen">
    <el-icon class="is-loading" :size="40"><Loading /></el-icon>
    <p>加载中...</p>
  </div>
  <router-view v-else />
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Loading } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/useAuthStore'

const authStore = useAuthStore()
const isLoading = ref(true)

onMounted(async () => {
  // Check authentication status on app startup
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
  background-color: var(--content-bg-color);
  color: var(--primary-color);

  .el-icon {
    margin-bottom: 20px;
  }

  p {
    font-size: 16px;
    font-weight: 500;
  }
}
</style>
