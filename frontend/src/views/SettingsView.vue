<template>
  <div class="settings">
    <header class="settings__header">
      <h1 class="settings__title">设置</h1>
    </header>

    <div class="settings__sections">
      <section class="settings-section">
        <h2 class="settings-section__title">API 密钥</h2>
        <p class="settings-section__desc">配置 AI 模型服务的 API 密钥</p>

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
          <BaseButton variant="primary" :loading="saving" @click="saveKeys">
            保存密钥
          </BaseButton>
          <p v-if="saveMessage" class="settings-section__msg" :class="{ 'settings-section__msg--error': saveError }">
            {{ saveMessage }}
          </p>
        </div>
      </section>

      <section class="settings-section">
        <h2 class="settings-section__title">个人信息</h2>
        <p class="settings-section__desc">修改您的账号信息</p>

        <div class="settings-section__fields">
          <BaseInput v-model="profile.username" label="用户名" />
          <BaseInput v-model="profile.email" label="邮箱" type="email" />
          <BaseInput v-model="profile.password" label="新密码" type="password" placeholder="留空则不修改" />
          <BaseButton variant="primary" :loading="updatingProfile" @click="saveProfile">
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
  max-width: 560px;
}

.settings__header {
  margin-bottom: var(--space-xl);
}

.settings__title {
  font-family: var(--font-display);
  font-size: 36px;
  font-weight: 400;
  letter-spacing: -0.5px;
  color: var(--color-ink);
}

.settings__sections {
  display: flex;
  flex-direction: column;
  gap: var(--space-xxl);
}

.settings-section {
  &__title {
    font-family: var(--font-display);
    font-size: 22px;
    font-weight: 400;
    letter-spacing: -0.3px;
    color: var(--color-ink);
    margin-bottom: var(--space-xs);
  }

  &__desc {
    font-size: 14px;
    color: var(--color-muted);
    margin-bottom: var(--space-lg);
  }

  &__fields {
    display: flex;
    flex-direction: column;
    gap: var(--space-md);
  }

  &__msg {
    font-size: 13px;
    color: var(--color-success);

    &--error {
      color: var(--color-error);
    }
  }
}
</style>
