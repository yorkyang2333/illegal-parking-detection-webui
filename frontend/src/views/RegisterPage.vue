<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1 class="auth-title">注册</h1>
      <p class="auth-subtitle">创建您的账号</p>

      <form class="auth-form" @submit.prevent="handleSubmit">
        <BaseInput
          v-model="form.username"
          label="用户名"
          placeholder="3-20个字符"
          :error="fieldErrors.username"
        />
        <BaseInput
          v-model="form.email"
          label="邮箱"
          type="email"
          placeholder="请输入邮箱"
          :error="fieldErrors.email"
        />
        <BaseInput
          v-model="form.password"
          label="密码"
          type="password"
          placeholder="至少6个字符"
          :error="fieldErrors.password"
        />
        <BaseInput
          v-model="form.confirmPassword"
          label="确认密码"
          type="password"
          placeholder="再次输入密码"
          :error="fieldErrors.confirmPassword"
        />

        <p v-if="authStore.error" class="auth-error">{{ authStore.error }}</p>

        <BaseButton variant="primary" :loading="authStore.isLoading" class="auth-submit">
          注册
        </BaseButton>
      </form>

      <p class="auth-footer">
        已有账号？
        <router-link to="/login" class="auth-link">登录</router-link>
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
  email: '',
  password: '',
  confirmPassword: '',
})

const fieldErrors = ref<Record<string, string>>({})

function validate(): boolean {
  fieldErrors.value = {}
  if (!form.username.trim() || form.username.length < 3 || form.username.length > 20) {
    fieldErrors.value.username = '用户名需要3-20个字符'
  }
  if (!form.email.trim() || !form.email.includes('@')) {
    fieldErrors.value.email = '请输入有效的邮箱'
  }
  if (!form.password || form.password.length < 6) {
    fieldErrors.value.password = '密码至少6个字符'
  }
  if (form.password !== form.confirmPassword) {
    fieldErrors.value.confirmPassword = '两次密码不一致'
  }
  return Object.keys(fieldErrors.value).length === 0
}

async function handleSubmit() {
  if (!validate()) return
  authStore.clearError()
  const success = await authStore.register(form.username, form.email, form.password)
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
