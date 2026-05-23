<template>
  <div
    class="upload-zone"
    :class="{ 'upload-zone--dragover': isDragover }"
    @dragover.prevent="isDragover = true"
    @dragleave="isDragover = false"
    @drop.prevent="handleDrop"
    @click="triggerInput"
  >
    <div class="upload-zone__inner">
      <div class="upload-zone__icon-wrapper">
        <Upload :size="28" stroke-width="1.5" class="upload-zone__icon" />
      </div>
      <h2 class="upload-zone__title">拖放视频文件到此处</h2>
      <p class="upload-zone__hint">或点击选择 (MP4, AVI, MOV)</p>
    </div>
    <input
      ref="fileInput"
      type="file"
      accept="video/*"
      class="upload-zone__input"
      @change="handleFileChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Upload } from 'lucide-vue-next'

const emit = defineEmits<{
  'file-selected': [file: File]
}>()

const isDragover = ref(false)
const fileInput = ref<HTMLInputElement>()

function triggerInput() {
  fileInput.value?.click()
}

function handleDrop(e: DragEvent) {
  isDragover.value = false
  const file = e.dataTransfer?.files[0]
  if (file && file.type.startsWith('video/')) {
    emit('file-selected', file)
  }
}

function handleFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) {
    emit('file-selected', file)
  }
}
</script>

<style scoped lang="scss">
.upload-zone {
  display: flex;
  flex-direction: column;
  background: var(--color-canvas);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-xl);
  cursor: pointer;
  flex: 1;
  min-height: 50vh;
  padding: var(--space-md);
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.02);

  &:hover,
  &--dragover {
    transform: translateY(-4px);
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.06);
    border-color: rgba(0,0,0,0.1);
  }
}

.upload-zone__inner {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 1px dashed var(--color-hairline-soft);
  border-radius: var(--radius-lg);
  padding: var(--space-xl);
  transition: border-color 0.4s ease;
  text-align: center;

  .upload-zone:hover & {
    border-color: rgba(204, 120, 92, 0.3);
  }
}

.upload-zone__icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--color-surface-soft);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--space-lg);
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);

  .upload-zone:hover & {
    transform: scale(1.05);
    background: var(--color-primary);
  }
}

.upload-zone__icon {
  color: var(--color-ink);
  transition: color 0.4s;

  .upload-zone:hover & {
    color: var(--color-on-primary);
  }
}

.upload-zone__title {
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 400;
  color: var(--color-ink);
  margin-bottom: var(--space-xs);
}

.upload-zone__hint {
  font-family: var(--font-body);
  font-size: 14px;
  color: var(--color-muted);
}

.upload-zone__input {
  display: none;
}
</style>
