<template>
  <div
    class="upload-zone"
    :class="{ 'upload-zone--dragover': isDragover }"
    @dragover.prevent="isDragover = true"
    @dragleave="isDragover = false"
    @drop.prevent="handleDrop"
    @click="triggerInput"
  >
    <Upload :size="40" class="upload-zone__icon" />
    <p class="upload-zone__title">拖放视频文件到此处</p>
    <p class="upload-zone__hint">或点击选择文件 (MP4, AVI, MOV)</p>
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
  align-items: center;
  justify-content: center;
  padding: var(--space-xxl);
  background: var(--color-surface-card);
  border: 2px dashed var(--color-hairline);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: border-color 0.15s, background-color 0.15s;
  min-height: 240px;

  &:hover,
  &--dragover {
    border-color: var(--color-primary);
    background: var(--color-surface-soft);
  }

  &__icon {
    color: var(--color-muted-soft);
    margin-bottom: var(--space-md);
  }

  &__title {
    font-size: 16px;
    font-weight: 500;
    color: var(--color-body-strong);
    margin-bottom: var(--space-xs);
  }

  &__hint {
    font-size: 14px;
    color: var(--color-muted);
  }

  &__input {
    display: none;
  }
}
</style>
