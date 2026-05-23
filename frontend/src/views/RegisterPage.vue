<template>
  <div class="split-layout">
    <!-- Left: Editorial Brand Panel -->
    <div class="brand-panel">
      <div class="brand-panel__content">
        <span class="brand-panel__logo">✦</span>
        <h1 class="brand-panel__headline">
          Create <br/>
          <span class="italic">System</span> <br/>
          Access.
        </h1>
        <p class="brand-panel__subheadline">
          加入平台，体验由多模态大模型驱动的智能化城市违停检测工作流。
        </p>
      </div>
      <div class="brand-panel__footer">
        <span>© 2026 Urban Mobility Intelligence</span>
      </div>
    </div>

    <!-- Right: Functional Form Panel -->
    <div class="form-panel">
      <div class="form-wrapper">
        <div class="form-header">
          <h2 class="form-title">注册</h2>
          <p class="form-subtitle">填写下方信息申请您的系统访问权限</p>
        </div>

        <form class="auth-form" @submit.prevent="handleSubmit">
          <div class="input-group" style="--delay: 1">
            <BaseInput
              v-model="form.username"
              label="用户名"
              placeholder="3-20个字符"
              :error="fieldErrors.username"
            />
          </div>
          <div class="input-group" style="--delay: 2">
            <BaseInput
              v-model="form.email"
              label="邮箱"
              type="email"
              placeholder="name@organization.com"
              :error="fieldErrors.email"
            />
          </div>
          <div class="input-group" style="--delay: 3">
            <BaseInput
              v-model="form.password"
              label="密码"
              type="password"
              placeholder="至少 6 个字符"
              :error="fieldErrors.password"
            />
          </div>
          <div class="input-group" style="--delay: 4">
            <BaseInput
              v-model="form.confirmPassword"
              label="确认密码"
              type="password"
              placeholder="请再次输入密码"
              :error="fieldErrors.confirmPassword"
            />
          </div>

          <p v-if="authStore.error" class="auth-error" style="--delay: 5">{{ authStore.error }}</p>

          <BaseButton variant="primary" :loading="authStore.isLoading" class="auth-submit" style="--delay: 5">
            提交申请
          </BaseButton>
        </form>

        <p class="auth-footer" style="--delay: 6">
          已经拥有账号？
          <router-link to="/login" class="auth-link">直接登录</router-link>
        </p>
      </div>
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
.split-layout {
  display: flex;
  min-height: 100vh;
  background: var(--color-canvas);
}

.brand-panel {
  flex: 1;
  background: var(--color-surface-dark);
  color: var(--color-canvas);
  padding: var(--space-section);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    inset: 0;
    opacity: 0.04;
    background-image: url('data:image/svg+xml,%3Csvg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"%3E%3Cfilter id="noiseFilter"%3E%3CfeTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="3" stitchTiles="stitch"/%3E%3C/filter%3E%3Crect width="100%25" height="100%25" filter="url(%23noiseFilter)"/%3E%3C/svg%3E');
    pointer-events: none;
  }
}

.brand-panel__logo {
  font-size: 40px;
  color: var(--color-primary);
  display: block;
  margin-bottom: clamp(var(--space-xl), 10vh, var(--space-section));
}

.brand-panel__headline {
  font-family: var(--font-display);
  font-size: clamp(48px, 6vw, 88px);
  line-height: 0.95;
  font-weight: 400;
  letter-spacing: -2px;
  margin-bottom: var(--space-xl);
  position: relative;
  z-index: 1;

  .italic {
    font-style: italic;
    color: var(--color-muted);
  }
}

.brand-panel__subheadline {
  font-family: var(--font-body);
  font-size: 18px;
  color: rgba(255, 255, 255, 0.6);
  max-width: 440px;
  line-height: 1.6;
  position: relative;
  z-index: 1;
}

.brand-panel__footer {
  font-family: var(--font-mono);
  font-size: 13px;
  color: rgba(255, 255, 255, 0.3);
  letter-spacing: 0.5px;
  position: relative;
  z-index: 1;
}

.form-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-section);
  position: relative;
}

.form-wrapper {
  width: 100%;
  max-width: 400px;
}

.form-header {
  margin-bottom: var(--space-xxl);
  animation: fadeUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) both;
}

.form-title {
  font-family: var(--font-display);
  font-size: 48px;
  font-weight: 400;
  color: var(--color-ink);
  letter-spacing: -1px;
  margin-bottom: var(--space-xs);
}

.form-subtitle {
  font-size: 16px;
  color: var(--color-muted);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
}

.input-group, .auth-submit, .auth-error, .auth-footer {
  animation: fadeUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) both;
  animation-delay: calc(var(--delay) * 0.1s);
}

.input-group {
  display: flex;
  flex-direction: column;
}

.auth-submit {
  width: 100%;
  height: 52px;
  font-size: 16px;
  margin-top: var(--space-xs);
}

.auth-error {
  font-size: 14px;
  color: var(--color-error);
  padding: var(--space-sm) 0;
}

.auth-footer {
  margin-top: var(--space-xxl);
  text-align: center;
  font-size: 15px;
  color: var(--color-muted);
}

.auth-link {
  color: var(--color-ink);
  font-weight: 500;
  text-decoration: none;
  margin-left: var(--space-xs);
  border-bottom: 1px solid var(--color-hairline);
  padding-bottom: 2px;
  transition: border-color 0.2s;

  &:hover {
    border-color: var(--color-primary);
  }
}

@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 900px) {
  .split-layout {
    flex-direction: column;
  }
  .brand-panel {
    flex: none;
    padding: var(--space-xl);
    min-height: auto;
  }
  .brand-panel__logo {
    font-size: 32px;
    margin-bottom: var(--space-xl);
  }
  .brand-panel__headline {
    font-size: 48px;
  }
  .form-panel {
    padding: var(--space-xl);
  }
}
</style>
