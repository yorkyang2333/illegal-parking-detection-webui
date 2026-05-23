<template>
  <div class="settings">
    <header class="settings__header">
      <h1 class="settings__title">
        System <br/>
        <span class="italic">Preferences.</span>
      </h1>
      <p class="settings__desc">管理您的系统偏好与基础模型配置</p>
    </header>

    <div class="settings__sections">
      <section class="settings-section feature-card">
        <h2 class="settings-section__title">API 密钥</h2>
        <p class="settings-section__desc">配置 AI 模型服务的 API 密钥，用于调用后台推理能力。</p>

        <div class="settings-section__fields">
          <BaseInput
            v-model="apiKeys.dashscope_key"
            label="DashScope API Key"
            placeholder="用于 Qwen / QVQ 模型"
            type="password"
          />
          <BaseInput
            v-model="apiKeys.gemini_key"
            label="Gemini API Key"
            placeholder="用于对话模式"
            type="password"
          />
          <BaseButton variant="primary" :loading="saving" @click="saveKeys" class="settings-btn">
            保存密钥
          </BaseButton>
          <p v-if="saveMessage" class="settings-section__msg" :class="{ 'settings-section__msg--error': saveError }">
            {{ saveMessage }}
          </p>
        </div>
      </section>

      <section class="settings-section feature-card">
        <h2 class="settings-section__title">个人信息</h2>
        <p class="settings-section__desc">修改您的账号标识与安全凭证。</p>

        <div class="settings-section__fields">
          <BaseInput v-model="profile.username" label="用户名" />
          <BaseInput v-model="profile.email" label="邮箱" type="email" />
          <BaseInput v-model="profile.password" label="新密码" type="password" placeholder="留空则不修改" />
          <BaseButton variant="primary" :loading="updatingProfile" @click="saveProfile" class="settings-btn">
            更新信息
          </BaseButton>
          <p v-if="profileMessage" class="settings-section__msg" :class="{ 'settings-section__msg--error': profileError }">
            {{ profileMessage }}
          </p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/useAuthStore'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'

const authStore = useAuthStore()

const apiKeys = reactive({ dashscope_key: '', gemini_key: '' })
const saving = ref(false)
const saveMessage = ref('')
const saveError = ref(false)

const profile = reactive({ username: '', email: '', password: '' })
const updatingProfile = ref(false)
const profileMessage = ref('')
const profileError = ref(false)

onMounted(async () => {
  try {
    const res = await fetch('/api/settings', { credentials: 'include' })
    if (res.ok) {
      const data = await res.json()
      apiKeys.dashscope_key = data.dashscope_key || ''
      apiKeys.gemini_key = data.gemini_key || ''
    }
  } catch { /* ignore */ }

  if (authStore.user) {
    profile.username = authStore.user.username
    profile.email = authStore.user.email
  }
})

async function saveKeys() {
  saving.value = true
  saveMessage.value = ''
  try {
    const res = await fetch('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(apiKeys)
    })
    if (res.ok) {
      saveMessage.value = '保存成功'
      saveError.value = false
    } else {
      saveMessage.value = '保存失败'
      saveError.value = true
    }
  } catch {
    saveMessage.value = '网络错误'
    saveError.value = true
  } finally {
    saving.value = false
  }
}

async function saveProfile() {
  updatingProfile.value = true
  profileMessage.value = ''
  const success = await authStore.updateProfile(
    profile.username,
    profile.email,
    profile.password || undefined
  )
  if (success) {
    profileMessage.value = '更新成功'
    profileError.value = false
    profile.password = ''
  } else {
    profileMessage.value = authStore.error || '更新失败'
    profileError.value = true
  }
  updatingProfile.value = false
}
</script>

<style scoped lang="scss">
.settings {
  padding: var(--space-xl) 0;
  max-width: 640px;
  margin: 0 auto;
}

.settings__header {
  margin-bottom: var(--space-xxl);
}

.settings__title {
  font-family: var(--font-display);
  font-size: clamp(40px, 5vw, 56px);
  line-height: 0.95;
  font-weight: 400;
  letter-spacing: -1.5px;
  color: var(--color-ink);
  margin-bottom: var(--space-sm);

  .italic {
    font-style: italic;
    color: var(--color-muted);
  }
}

.settings__desc {
  font-family: var(--font-body);
  font-size: 16px;
  color: var(--color-muted);
}

.settings__sections {
  display: flex;
  flex-direction: column;
  gap: var(--space-xxl);
}

.feature-card {
  background: var(--color-canvas);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-xl);
  padding: var(--space-xxl);
  box-shadow: 0 4px 20px rgba(0,0,0,0.02);
  transition: transform 0.3s ease, box-shadow 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.04);
  }
}

.settings-section {
  &__title {
    font-family: var(--font-display);
    font-size: 28px;
    font-weight: 400;
    letter-spacing: -0.5px;
    color: var(--color-ink);
    margin-bottom: var(--space-xs);
  }

  &__desc {
    font-size: 15px;
    color: var(--color-muted);
    margin-bottom: var(--space-xl);
  }

  &__fields {
    display: flex;
    flex-direction: column;
    gap: var(--space-lg);
  }

  &__msg {
    font-size: 14px;
    color: var(--color-success);
    margin-top: calc(-1 * var(--space-sm));

    &--error {
      color: var(--color-error);
    }
  }
}

.settings-btn {
  align-self: flex-start;
  min-width: 120px;
  margin-top: var(--space-sm);
}
</style>
