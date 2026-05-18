<template>
  <div class="video-preview">
    <div class="video-preview__player">
      <video :src="src" controls class="video-preview__video" />
    </div>
    <div class="video-preview__info">
      <span class="video-preview__name">{{ filename }}</span>
      <button class="video-preview__remove" @click="$emit('remove')">
        <X :size="16" />
        移除
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { X } from 'lucide-vue-next'

defineProps<{
  src: string
  filename: string
}>()

defineEmits<{
  remove: []
}>()
</script>

<style scoped lang="scss">
.video-preview {
  background: var(--color-surface-dark);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.video-preview__player {
  aspect-ratio: 16 / 9;
  background: #000;
}

.video-preview__video {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.video-preview__info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-sm) var(--space-md);
}

.video-preview__name {
  font-size: 13px;
  color: var(--color-on-dark-soft);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.video-preview__remove {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--color-on-dark-soft);
  padding: 4px 8px;
  border-radius: var(--radius-sm);

  &:hover {
    color: var(--color-error);
    background: rgba(198, 69, 69, 0.15);
  }
}
</style>
