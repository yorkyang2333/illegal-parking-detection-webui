<template>
  <div class="chat-input-container">
    <div class="input-wrapper">
      <textarea
        ref="textareaRef"
        v-model="inputText"
        :placeholder="placeholder"
        :disabled="disabled"
        @input="adjustHeight"
        @keydown="handleKeyDown"
        class="chat-textarea"
        rows="1"
      ></textarea>
      <button
        class="send-button"
        :disabled="!canSend"
        @click="handleSend"
        :title="disabled ? '正在生成...' : '发送消息 (Ctrl+Enter)'"
      >
        <el-icon v-if="disabled" class="is-loading"><Loading /></el-icon>
        <svg v-else viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M22 2L11 13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>
    <p class="input-hint">按 <kbd>Ctrl</kbd> + <kbd>Enter</kbd> 发送</p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from 'vue'
import { Loading } from '@element-plus/icons-vue'

const props = withDefaults(defineProps<{
  placeholder?: string
  disabled?: boolean
}>(), {
  placeholder: '请输入您的问题...',
  disabled: false
})

const emit = defineEmits<{
  send: [content: string]
}>()

const inputText = ref('')
const textareaRef = ref<HTMLTextAreaElement | null>(null)

const canSend = computed(() => inputText.value.trim().length > 0 && !props.disabled)

function adjustHeight() {
  nextTick(() => {
    const textarea = textareaRef.value
    if (textarea) {
      textarea.style.height = 'auto'
      const maxHeight = 200
      textarea.style.height = Math.min(textarea.scrollHeight, maxHeight) + 'px'
    }
  })
}

function handleKeyDown(event: KeyboardEvent) {
  if (event.ctrlKey && event.key === 'Enter') {
    event.preventDefault()
    handleSend()
  }
}

function handleSend() {
  if (!canSend.value) return
  emit('send', inputText.value.trim())
  inputText.value = ''
  nextTick(() => {
    if (textareaRef.value) {
      textareaRef.value.style.height = 'auto'
    }
  })
}

onMounted(() => {
  textareaRef.value?.focus()
})

defineExpose({
  focus: () => textareaRef.value?.focus()
})
</script>

<style scoped lang="scss">
.chat-input-container {
  padding: 20px 24px;
  background: #ffffff;
  border-top: 1px solid #e5e7eb;
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  background: #f9fafb;
  border: 2px solid #e5e7eb;
  border-radius: 16px;
  padding: 12px 16px;
  transition: all 0.2s ease;

  &:focus-within {
    border-color: #5b6eae;
    box-shadow: 0 0 0 3px rgba(91, 110, 174, 0.1);
    background: white;
  }
}

.chat-textarea {
  flex: 1;
  border: none;
  background: transparent;
  resize: none;
  font-size: 15px;
  line-height: 1.5;
  color: #1f2937;
  font-family: inherit;
  max-height: 200px;
  overflow-y: auto;

  &::placeholder {
    color: #9ca3af;
  }

  &:focus {
    outline: none;
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
}

.send-button {
  flex-shrink: 0;
  width: 44px;
  height: 44px;
  border: none;
  border-radius: 12px;
  background: #5b6eae;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;

  svg {
    width: 20px;
    height: 20px;
  }

  .el-icon {
    font-size: 20px;
  }

  &:hover:not(:disabled) {
    background: #4a5a94;
  }

  &:active:not(:disabled) {
    transform: scale(0.98);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
}

.input-hint {
  margin: 10px 0 0;
  text-align: center;
  font-size: 12px;
  color: #9ca3af;

  kbd {
    display: inline-block;
    padding: 2px 6px;
    background: #f3f4f6;
    border-radius: 4px;
    font-family: inherit;
    font-size: 11px;
    color: #6b7280;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-input-container {
    padding: 16px;
  }

  .input-wrapper {
    padding: 10px 12px;
    border-radius: 14px;
  }

  .chat-textarea {
    font-size: 14px;
  }

  .send-button {
    width: 40px;
    height: 40px;
    border-radius: 10px;

    svg {
      width: 18px;
      height: 18px;
    }
  }

  .input-hint {
    display: none;
  }
}
</style>
