<template>
  <div class="chat-input-container">
    <div class="chat-input">
      <div v-if="hasMedia" class="chat-input__media-badge">
        <Paperclip :size="14" />
        <span>已附加文件</span>
      </div>
      <div class="chat-input__row">
        <!-- 模型选择器 -->
        <div class="model-selector" ref="modelSelectorRef">
          <button class="model-selector__trigger" @click="modelDropdownOpen = !modelDropdownOpen">
            <Cpu :size="14" />
            <span class="model-selector__label">{{ displayModelName }}</span>
            <ChevronDown :size="12" />
          </button>
          <Transition name="dropdown">
            <div v-if="modelDropdownOpen" class="model-selector__dropdown">
              <div
                v-if="models.length === 0"
                class="model-selector__empty"
              >
                未获取到模型列表，请先在设置中配置
              </div>
              <button
                v-for="m in models"
                :key="m.id"
                class="model-selector__item"
                :class="{ 'model-selector__item--active': m.id === currentModel }"
                @click="selectModelItem(m.id)"
              >
                <span class="model-selector__item-name">{{ m.id }}</span>
                <span v-if="m.owned_by" class="model-selector__item-provider">{{ m.owned_by }}</span>
              </button>
            </div>
          </Transition>
        </div>

        <label class="chat-input__upload">
          <Paperclip :size="20" stroke-width="1.5" />
          <input type="file" accept="video/*,image/*" @change="handleFileChange" />
        </label>
        <textarea
          ref="textareaRef"
          v-model="input"
          class="chat-input__textarea"
          placeholder="有什么我可以帮您的？"
          rows="1"
          @input="autoResize"
          @keydown.enter.exact.prevent="handleSend"
        />
        <button
          v-if="isStreaming"
          class="chat-input__stop"
          @click="$emit('stop')"
        >
          <Square :size="16" />
        </button>
        <button
          v-else
          class="chat-input__send"
          :class="{ 'chat-input__send--active': input.trim() }"
          :disabled="!input.trim()"
          @click="handleSend"
        >
          <ArrowUp :size="18" stroke-width="2.5" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { Paperclip, ArrowUp, Square, Cpu, ChevronDown } from 'lucide-vue-next'
import type { ModelInfo } from '@/api/types'

const props = defineProps<{
  isStreaming: boolean
  hasMedia: boolean
  models: ModelInfo[]
  currentModel: string
}>()

const emit = defineEmits<{
  send: [content: string]
  stop: []
  upload: [file: File]
  selectModel: [modelId: string]
}>()

const input = ref('')
const textareaRef = ref<HTMLTextAreaElement>()
const modelDropdownOpen = ref(false)
const modelSelectorRef = ref<HTMLElement>()

const displayModelName = computed(() => {
  if (!props.currentModel) return '未配置模型'
  const name = props.currentModel
  // 截取最后一段（按 / 分割），最多 16 字符
  const parts = name.split('/')
  const short = parts[parts.length - 1] || name
  return short.length > 16 ? short.slice(0, 14) + '…' : short
})

function autoResize() {
  const el = textareaRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 160) + 'px'
}

function handleSend() {
  if (!input.value.trim()) return
  emit('send', input.value.trim())
  input.value = ''
  nextTick(autoResize)
}

function handleFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) emit('upload', file)
}

function selectModelItem(modelId: string) {
  emit('selectModel', modelId)
  modelDropdownOpen.value = false
}

function handleClickOutside(e: MouseEvent) {
  if (modelSelectorRef.value && !modelSelectorRef.value.contains(e.target as Node)) {
    modelDropdownOpen.value = false
  }
}

onMounted(() => document.addEventListener('click', handleClickOutside))
onBeforeUnmount(() => document.removeEventListener('click', handleClickOutside))
</script>

<style scoped lang="scss">
.chat-input-container {
  padding: var(--space-xl);
  display: flex;
  justify-content: center;
  background: linear-gradient(to top, var(--color-canvas) 70%, transparent);
}

.chat-input {
  width: 100%;
  max-width: 800px;
  position: relative;
}

.chat-input__media-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.5px;
  color: var(--color-primary);
  background: rgba(204, 120, 92, 0.1);
  padding: 6px 12px;
  border-radius: var(--radius-pill);
  position: absolute;
  top: -36px;
  left: var(--space-md);
}

.chat-input__row {
  display: flex;
  align-items: flex-end;
  gap: var(--space-sm);
  background: var(--color-canvas);
  border: 1px solid var(--color-hairline);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.04);
  border-radius: 32px;
  padding: 8px 12px;
  transition: box-shadow 0.2s ease, border-color 0.2s ease;

  &:focus-within {
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
    border-color: rgba(0,0,0,0.15);
  }
}

// 模型选择器
.model-selector {
  position: relative;
  display: flex;
  align-items: center;
  flex-shrink: 0;
  align-self: center;

  &__trigger {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: var(--color-surface-soft);
    color: var(--color-muted);
    border: none;
    border-radius: var(--radius-pill);
    font-family: var(--font-mono);
    font-size: 12px;
    padding: 6px 10px;
    cursor: pointer;
    white-space: nowrap;
    transition: all 0.2s;
    max-width: 180px;

    &:hover {
      color: var(--color-ink);
      background: var(--color-surface-cream-strong);
    }
  }

  &__label {
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 120px;
  }

  &__dropdown {
    position: absolute;
    bottom: calc(100% + 8px);
    left: 0;
    z-index: 100;
    min-width: 220px;
    max-width: 320px;
    max-height: 240px;
    overflow-y: auto;
    background: var(--color-canvas);
    border: 1px solid var(--color-hairline);
    border-radius: var(--radius-lg);
    padding: var(--space-xs);
    box-shadow: 0 8px 24px rgba(20, 20, 19, 0.12);

    &::-webkit-scrollbar {
      width: 4px;
    }
    &::-webkit-scrollbar-thumb {
      background: var(--color-hairline);
      border-radius: 2px;
    }
  }

  &__empty {
    font-size: 13px;
    color: var(--color-muted);
    padding: var(--space-md);
    text-align: center;
    line-height: 1.5;
  }

  &__item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-sm);
    width: 100%;
    padding: 8px 12px;
    border: none;
    border-radius: var(--radius-md);
    background: transparent;
    cursor: pointer;
    font-family: var(--font-mono);
    font-size: 13px;
    color: var(--color-ink);
    text-align: left;
    transition: all 0.15s;

    &:hover {
      background: var(--color-surface-soft);
    }

    &--active {
      background: rgba(204, 120, 92, 0.08);
      color: var(--color-primary);
    }

    &-name {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      flex: 1;
    }

    &-provider {
      font-size: 11px;
      color: var(--color-muted-soft);
      flex-shrink: 0;
    }
  }
}

.chat-input__upload {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  color: var(--color-muted);
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.2s;

  &:hover {
    color: var(--color-ink);
    background: var(--color-surface-soft);
  }

  input {
    display: none;
  }
}

.chat-input__textarea {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-family: var(--font-body);
  font-size: 16px;
  line-height: 1.5;
  color: var(--color-ink);
  resize: none;
  padding: 8px 4px;
  max-height: 160px;
  align-self: center;

  &::placeholder {
    color: var(--color-muted-soft);
  }
}

.chat-input__send,
.chat-input__stop {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  flex-shrink: 0;
  border: none;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.chat-input__send {
  background: var(--color-surface-soft);
  color: var(--color-muted-soft);

  &--active {
    background: var(--color-primary);
    color: var(--color-canvas);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(204, 120, 92, 0.3);

    &:hover {
      background: var(--color-primary-hover);
      transform: translateY(-4px);
    }
  }
}

.chat-input__stop {
  background: var(--color-error);
  color: white;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
  }
}

// Dropdown transition
.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.15s, transform 0.15s;
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(4px);
}
</style>
