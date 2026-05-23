<template>
  <div class="chat-input-container">
    <div class="chat-input">
      <div v-if="hasMedia" class="chat-input__media-badge">
        <Paperclip :size="14" />
        <span>已附加文件</span>
      </div>
      <div class="chat-input__row">
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
import { ref, nextTick } from 'vue'
import { Paperclip, ArrowUp, Square } from 'lucide-vue-next'

defineProps<{
  isStreaming: boolean
  hasMedia: boolean
}>()

const emit = defineEmits<{
  send: [content: string]
  stop: []
  upload: [file: File]
}>()

const input = ref('')
const textareaRef = ref<HTMLTextAreaElement>()

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
</style>
