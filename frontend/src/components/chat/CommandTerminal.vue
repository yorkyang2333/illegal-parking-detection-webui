<template>
  <div class="prts-terminal-container">
    <div class="input-wrapper">
      <button class="prts-attach-btn" @click="triggerFileUpload" title="UPLINK_VIDEO">
        <el-icon><PictureRounded /></el-icon>
      </button>
      <input 
        type="file" 
        ref="fileInputRef" 
        style="display: none" 
        accept="video/mp4,video/webm"
        @change="handleFileChange"
      />
      <textarea
        ref="textareaRef"
        v-model="inputText"
        :placeholder="placeholder"
        :disabled="disabled"
        @input="adjustHeight"
        @keydown="handleKeyDown"
        class="prts-textarea"
        rows="1"
      ></textarea>
      <button
        class="prts-send-btn"
        :disabled="!canSend"
        @click="handleSend"
        :title="disabled ? 'PROCESSING...' : 'TRANSMIT'"
      >
        <el-icon v-if="disabled" class="is-loading"><Loading /></el-icon>
        <svg v-else viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M22 2L11 13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>
    <div class="input-decorations">
      <span class="hud-line"></span>
      <span class="hud-text">PRTS_UPLINK_ESTABLISHED //</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from 'vue'
import { Loading, PictureRounded } from '@element-plus/icons-vue'

const props = withDefaults(defineProps<{
  placeholder?: string
  disabled?: boolean
}>(), {
  placeholder: 'ENTER_COMMAND...',
  disabled: false
})

const emit = defineEmits<{
  send: [content: string]
  'upload-video': [file: File]
}>()

const inputText = ref('')
const textareaRef = ref<HTMLTextAreaElement | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)

const canSend = computed(() => (inputText.value.trim().length > 0 || fileInputRef.value?.files?.length) && !props.disabled)

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
  if (inputText.value.trim()) {
    emit('send', inputText.value.trim())
  }
  inputText.value = ''
  nextTick(() => {
    if (textareaRef.value) {
      textareaRef.value.style.height = 'auto'
    }
  })
}

function triggerFileUpload() {
  fileInputRef.value?.click()
}

function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    emit('upload-video', target.files[0])
    // clear input
    target.value = ''
  }
}

onMounted(() => {
  textareaRef.value?.focus()
})

defineExpose({
  focus: () => textareaRef.value?.focus()
})
</script>

<style scoped lang="scss">
.prts-terminal-container {
  padding: 16px;
  background: white;
  position: relative;
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  background: #fdfdfd;
  border: 1px solid var(--ef-border-light);
  border-radius: 0;
  padding: 8px 12px;
  transition: all 0.2s ease;

  &:focus-within {
    border-color: var(--ef-accent);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  }
}

.prts-attach-btn {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  background: #f0f0f0;
  border: 1px solid var(--ef-border-light);
  color: var(--ef-text-dim);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;

  &:hover {
    border-color: var(--ef-accent);
    color: var(--ef-accent);
    background: #e6f6ff;
  }
}

.prts-textarea {
  flex: 1;
  border: none;
  background: transparent;
  resize: none;
  font-size: 14px;
  line-height: 1.5;
  color: var(--ef-text);
  font-family: monospace;
  max-height: 200px;
  overflow-y: auto;
  padding: 8px 0;

  &::placeholder {
    color: var(--ef-text-dim);
    opacity: 0.7;
  }

  &:focus {
    outline: none;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.prts-send-btn {
  flex-shrink: 0;
  width: 44px;
  height: 44px;
  border: 1px solid var(--ef-border);
  border-radius: 0;
  background: white;
  color: var(--ef-text);
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
    background: var(--ef-accent);
    color: white;
    border-color: var(--ef-accent);
  }

  &:active:not(:disabled) {
    transform: scale(0.95);
  }

  &:disabled {
    opacity: 0.3;
    border-color: var(--ef-border-light);
    color: var(--ef-border-light);
    cursor: not-allowed;
  }
}

.input-decorations {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 8px;

  .hud-line {
    flex: 1;
    height: 1px;
    background: repeating-linear-gradient(
      90deg,
      var(--ef-border-light),
      var(--ef-border-light) 4px,
      transparent 4px,
      transparent 8px
    );
  }

  .hud-text {
    font-family: monospace;
    font-size: 10px;
    color: var(--ef-text-dim);
    letter-spacing: 1px;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .prts-terminal-container {
    padding: 16px;
  }

  .prts-send-btn {
    width: 40px;
    height: 40px;
  }
}
</style>
