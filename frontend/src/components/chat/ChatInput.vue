<template>
  <div class="chat-input">
    <div v-if="hasMedia" class="chat-input__media-badge">
      <Paperclip :size="14" />
      <span>已附加文件</span>
    </div>
    <div class="chat-input__row">
      <label class="chat-input__upload">
        <Paperclip :size="18" />
        <input type="file" accept="video/*,image/*" @change="handleFileChange" />
      </label>
      <textarea
        ref="textareaRef"
        v-model="input"
        class="chat-input__textarea"
        placeholder="输入消息..."
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
        :disabled="!input.trim()"
        @click="handleSend"
      >
        <ArrowUp :size="18" />
      </button>
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
.chat-input {
  padding: var(--space-md) var(--space-xl);
  border-top: 1px solid var(--color-hairline-soft);
}

.chat-input__media-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--color-primary);
  background: rgba(204, 120, 92, 0.1);
  padding: 4px 10px;
  border-radius: var(--radius-pill);
  margin-bottom: var(--space-xs);
}

.chat-input__row {
  display: flex;
  align-items: flex-end;
  gap: var(--space-xs);
  background: var(--color-surface-soft);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-lg);
  padding: var(--space-xs) var(--space-sm);
}

.chat-input__upload {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  color: var(--color-muted);
  cursor: pointer;
  flex-shrink: 0;

  &:hover {
    color: var(--color-ink);
    background: var(--color-surface-card);
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
  font-size: 15px;
  line-height: 1.5;
  color: var(--color-ink);
  resize: none;
  padding: 8px 0;
  max-height: 160px;

  &::placeholder {
    color: var(--color-muted-soft);
  }
}

.chat-input__send,
.chat-input__stop {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  flex-shrink: 0;
}

.chat-input__send {
  background: var(--color-primary);
  color: var(--color-on-primary);

  &:disabled {
    background: var(--color-primary-disabled);
    color: var(--color-muted);
  }
}

.chat-input__stop {
  background: var(--color-error);
  color: white;
}
</style>
