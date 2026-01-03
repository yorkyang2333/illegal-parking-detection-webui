import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { loginApi, registerApi, logoutApi, getMeApi, updateProfileApi } from '@/api/auth'
import type { User } from '@/api/types'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const isAuthenticated = computed(() => user.value !== null)

  // Actions
  async function login(username: string, password: string, rememberMe: boolean = false) {
    try {
      isLoading.value = true
      error.value = null

      const response = await loginApi(username, password, rememberMe)
      user.value = response.user || null

      return true
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : '登录失败'
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function register(username: string, email: string, password: string) {
    try {
      isLoading.value = true
      error.value = null

      const response = await registerApi(username, email, password)
      user.value = response.user || null

      return true
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : '注册失败'
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function logout() {
    try {
      isLoading.value = true
      error.value = null

      await logoutApi()
      user.value = null

      return true
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : '登出失败'
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function checkAuth() {
    try {
      isLoading.value = true
      error.value = null

      const response = await getMeApi()
      user.value = response.user

      return true
    } catch (err: unknown) {
      if (err instanceof Error && err.message === 'UNAUTHORIZED') {
        user.value = null
        return false
      }
      error.value = err instanceof Error ? err.message : '获取用户信息失败'
      user.value = null
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function updateProfile(username: string, email: string, password?: string) {
    try {
      isLoading.value = true
      error.value = null

      const response = await updateProfileApi(username, email, password)
      user.value = response.user

      return true
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : '更新失败'
      return false
    } finally {
      isLoading.value = false
    }
  }

  function clearError() {
    error.value = null
  }

  return {
    // State
    user,
    isLoading,
    error,
    // Computed
    isAuthenticated,
    // Actions
    login,
    register,
    logout,
    checkAuth,
    updateProfile,
    clearError,
  }
})
