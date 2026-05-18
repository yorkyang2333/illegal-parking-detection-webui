<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1 class="auth-title">登录</h1>
      <p class="auth-subtitle">车辆违停感知系统</p>

      <form class="auth-form" @submit.prevent="handleSubmit">
        <BaseInput
          v-model="form.username"
          label="用户名"
          placeholder="请输入用户名"
          :error="fieldErrors.username"
        />
        <BaseInput
          v-model="form.password"
          label="密码"
          type="password"
          placeholder="请输入密码"
          :error="fieldErrors.password"
        />

        <label class="remember-me">
          <input v-model="form.rememberMe" type="checkbox" class="remember-checkbox" />
          <span>记住我</span>
        </label>

        <p v-if="authStore.error" class="auth-error">{{ authStore.error }}</p>

        <BaseButton variant="primary" :loading="authStore.isLoading" class="auth-submit">
          登录
        </BaseButton>
      </form>

      <p class="auth-footer">
        还没有账号？
        <router-link to="/register" class="auth-link">注册</router-link>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/useAuthStore'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
  username: '',
  password: '',
  rememberMe: false,
})

const fieldErrors = ref<Record<string, string>>({})

function validate(): boolean {
  fieldErrors.value = {}
  if (!form.username.trim()) fieldErrors.value.username = '请输入用户名'
  if (!form.password) fieldErrors.value.password = '请输入密码'
  return Object.keys(fieldErrors.value).length === 0
}

async function handleSubmit() {
  if (!validate()) return
  authStore.clearError()
  const success = await authStore.login(form.username, form.password, form.rememberMe)
  if (success) router.push('/analysis')
}

onMounted(() => authStore.clearError())
</script>

<style scoped lang="scss">
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-lg);
}

.auth-card {
  width: 100%;
  max-width: 400px;
  background: var(--color-canvas);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-xl);
  padding: var(--space-xxl);
}

.auth-title {
  font-family: var(--font-display);
  font-size: 36px;
  font-weight: 400;
  letter-spacing: -0.5px;
  color: var(--color-ink);
  margin-bottom: var(--space-xs);
}

.auth-subtitle {
  font-size: 14px;
  color: var(--color-muted);
  margin-bottom: var(--space-xl);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.remember-me {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  font-size: 14px;
  color: var(--color-body);
  cursor: pointer;
}

.remember-checkbox {
  width: 16px;
  height: 16px;
  accent-color: var(--color-primary);
}

.auth-error {
  font-size: 13px;
  color: var(--color-error);
  padding: var(--space-sm) var(--space-md);
  background: rgba(198, 69, 69, 0.08);
  border-radius: var(--radius-md);
}

.auth-submit {
  width: 100%;
  margin-top: var(--space-xs);
}

.auth-footer {
  text-align: center;
  margin-top: var(--space-lg);
  font-size: 14px;
  color: var(--color-muted);
}

.auth-link {
  color: var(--color-primary);
  font-weight: 500;

  &:hover {
    text-decoration: underline;
  }
}
</style>
