<template>
  <div class="settings">
    <header class="settings__header">
      <h1 class="settings__title">
        System <br/>
        <span class="italic">Preferences.</span>
      </h1>
      <p class="settings__desc">管理您的系统偏好与 AI 模型供应商配置</p>
    </header>

    <div class="settings__sections">
      <section class="settings-section feature-card">
        <h2 class="settings-section__title">供应商配置</h2>
        <p class="settings-section__desc">配置 OpenAI 兼容格式的 AI 模型服务供应商，支持通过 NewAPI 网关代理多种模型。</p>

        <div class="settings-section__fields">
          <BaseInput
            v-model="apiConfig.api_base"
            label="供应商地址 (Base URL)"
            placeholder="https://your-api.com/v1"
          />
          <BaseInput
            v-model="apiConfig.api_key"
            label="API Key"
            placeholder="sk-..."
            type="password"
          />
          <BaseButton variant="secondary" :loading="fetchingModels" @click="fetchModels" class="settings-btn">
            获取模型列表
          </BaseButton>
          <p v-if="modelMessage" class="settings-section__msg" :class="{ 'settings-section__msg--error': modelError }">
            {{ modelMessage }}
          </p>

          <template v-if="models.length > 0">
            <div class="model-field">
              <label class="model-field__label">对话模型 (Chat)</label>
              <div class="model-field__input-wrap">
                <input
                  v-model="apiConfig.chat_model"
                  class="model-field__input"
                  list="chat-model-list"
                  placeholder="选择或输入模型名称"
                />
                <datalist id="chat-model-list">
                  <option v-for="m in models" :key="m.id" :value="m.id" />
                </datalist>
              </div>
            </div>
            <div class="model-field">
              <label class="model-field__label">视觉模型 (Vision)</label>
              <div class="model-field__input-wrap">
                <input
                  v-model="apiConfig.vision_model"
                  class="model-field__input"
                  list="vision-model-list"
                  placeholder="选择或输入模型名称"
                />
                <datalist id="vision-model-list">
                  <option v-for="m in models" :key="m.id" :value="m.id" />
                </datalist>
              </div>
            </div>
            <div class="model-field">
              <label class="model-field__label">文本模型 (Text)</label>
              <div class="model-field__input-wrap">
                <input
                  v-model="apiConfig.text_model"
                  class="model-field__input"
                  list="text-model-list"
                  placeholder="选择或输入模型名称"
                />
                <datalist id="text-model-list">
                  <option v-for="m in models" :key="m.id" :value="m.id" />
                </datalist>
              </div>
            </div>
          </template>

          <BaseButton variant="primary" :loading="saving" @click="saveConfig" class="settings-btn">
            保存配置
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
import type { ModelInfo } from '@/api/types'

const authStore = useAuthStore()

// 供应商配置
const apiConfig = reactive({
  api_base: '',
  api_key: '',
  chat_model: '',
  vision_model: '',
  text_model: ''
})
const models = ref<ModelInfo[]>([])
const fetchingModels = ref(false)
const modelMessage = ref('')
const modelError = ref(false)
const saving = ref(false)
const saveMessage = ref('')
const saveError = ref(false)

// 个人信息
const profile = reactive({ username: '', email: '', password: '' })
const updatingProfile = ref(false)
const profileMessage = ref('')
const profileError = ref(false)

onMounted(async () => {
  // 加载已有配置
  try {
    const res = await fetch('/api/settings', { credentials: 'include' })
    if (res.ok) {
      const data = await res.json()
      apiConfig.api_base = data.api_base || ''
      apiConfig.api_key = data.api_key || ''
      apiConfig.chat_model = data.chat_model || ''
      apiConfig.vision_model = data.vision_model || ''
      apiConfig.text_model = data.text_model || ''
    }
  } catch { /* ignore */ }

  if (authStore.user) {
    profile.username = authStore.user.username
    profile.email = authStore.user.email
  }

  // 如果已有 base URL，尝试自动获取模型列表
  if (apiConfig.api_base) {
    fetchModels()
  }
})

async function fetchModels() {
  fetchingModels.value = true
  modelMessage.value = ''
  modelError.value = false
  try {
    const res = await fetch('/api/models', { credentials: 'include' })
    if (res.ok) {
      const data = await res.json()
      const list = Array.isArray(data) ? data : (data.models || [])
      models.value = list
      if (list.length > 0) {
        modelMessage.value = `获取到 ${list.length} 个可用模型`
      } else {
        modelMessage.value = data.error || '未获取到模型，请检查供应商地址和 API Key'
        modelError.value = true
      }
    } else {
      modelMessage.value = '获取模型列表失败'
      modelError.value = true
    }
  } catch {
    modelMessage.value = '网络错误，请检查供应商地址'
    modelError.value = true
  } finally {
    fetchingModels.value = false
  }
}

async function saveConfig() {
  saving.value = true
  saveMessage.value = ''
  try {
    const res = await fetch('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(apiConfig)
    })
    if (res.ok) {
      saveMessage.value = '配置已保存'
      saveError.value = false
      // 同步更新 localStorage 中的 chat_model
      if (apiConfig.chat_model) {
        localStorage.setItem('chat_model', apiConfig.chat_model)
      }
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

// 模型选择字段
.model-field {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);

  &__label {
    font-family: var(--font-body);
    font-size: 14px;
    font-weight: 500;
    color: var(--color-ink);
    letter-spacing: -0.2px;
  }

  &__input-wrap {
    position: relative;
  }

  &__input {
    width: 100%;
    padding: 12px 16px;
    font-family: var(--font-mono);
    font-size: 14px;
    color: var(--color-ink);
    background: var(--color-canvas);
    border: 1px solid var(--color-hairline);
    border-radius: var(--radius-md);
    outline: none;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
    box-sizing: border-box;

    &::placeholder {
      color: var(--color-muted-soft);
    }

    &:focus {
      border-color: var(--color-primary);
      box-shadow: 0 0 0 3px rgba(204, 120, 92, 0.1);
    }
  }
}
</style>
