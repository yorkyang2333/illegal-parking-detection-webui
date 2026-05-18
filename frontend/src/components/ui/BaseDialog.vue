<template>
  <Teleport to="body">
    <Transition name="dialog">
      <div v-if="modelValue" class="dialog-overlay" @click.self="$emit('update:modelValue', false)">
        <div class="dialog-content" :style="{ maxWidth: width }">
          <div v-if="title" class="dialog-header">
            <h3 class="dialog-title">{{ title }}</h3>
            <button class="dialog-close" @click="$emit('update:modelValue', false)">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 6L6 18M6 6l12 12"/>
              </svg>
            </button>
          </div>
          <div class="dialog-body">
            <slot />
          </div>
          <div v-if="$slots.footer" class="dialog-footer">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
defineProps<{
  modelValue: boolean
  title?: string
  width?: string
}>()

defineEmits<{
  'update:modelValue': [value: boolean]
}>()
</script>

<style scoped lang="scss">
.dialog-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(20, 20, 19, 0.4);
  backdrop-filter: blur(2px);
  padding: var(--space-lg);
}

.dialog-content {
  background: var(--color-canvas);
  border-radius: var(--radius-xl);
  width: 100%;
  max-width: 480px;
  max-height: 90vh;
  overflow-y: auto;
}

.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-lg) var(--space-xl);
  border-bottom: 1px solid var(--color-hairline-soft);
}

.dialog-title {
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 400;
  letter-spacing: -0.3px;
  color: var(--color-ink);
}

.dialog-close {
  color: var(--color-muted);
  padding: 4px;
  border-radius: var(--radius-sm);

  &:hover {
    color: var(--color-ink);
    background: var(--color-surface-soft);
  }
}

.dialog-body {
  padding: var(--space-xl);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-sm);
  padding: var(--space-lg) var(--space-xl);
  border-top: 1px solid var(--color-hairline-soft);
}

.dialog-enter-active,
.dialog-leave-active {
  transition: opacity 0.2s ease;
}

.dialog-enter-active .dialog-content,
.dialog-leave-active .dialog-content {
  transition: transform 0.2s ease;
}

.dialog-enter-from,
.dialog-leave-to {
  opacity: 0;
}

.dialog-enter-from .dialog-content,
.dialog-leave-to .dialog-content {
  transform: scale(0.95) translateY(10px);
}
</style>
