<template>
  <button
    :class="['btn', `btn--${variant}`, { 'btn--disabled': disabled, 'btn--loading': loading }]"
    :disabled="disabled || loading"
    @click="$emit('click', $event)"
  >
    <span v-if="loading" class="btn__spinner" />
    <slot />
  </button>
</template>

<script setup lang="ts">
defineProps<{
  variant?: 'primary' | 'secondary' | 'text' | 'danger'
  disabled?: boolean
  loading?: boolean
}>()

defineEmits<{
  click: [e: MouseEvent]
}>()
</script>

<style scoped lang="scss">
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-xs);
  font-family: var(--font-body);
  font-size: 14px;
  font-weight: 500;
  line-height: 1;
  padding: 12px 20px;
  height: 40px;
  border-radius: var(--radius-md);
  transition: background-color 0.15s, opacity 0.15s;
  white-space: nowrap;

  &--primary {
    background: var(--color-primary);
    color: var(--color-on-primary);

    &:hover:not(:disabled) {
      background: var(--color-primary-active);
    }
  }

  &--secondary {
    background: var(--color-canvas);
    color: var(--color-ink);
    border: 1px solid var(--color-hairline);

    &:hover:not(:disabled) {
      background: var(--color-surface-soft);
    }
  }

  &--text {
    background: transparent;
    color: var(--color-primary);
    padding: 8px 12px;
    height: auto;

    &:hover:not(:disabled) {
      background: var(--color-surface-soft);
    }
  }

  &--danger {
    background: var(--color-error);
    color: var(--color-on-primary);

    &:hover:not(:disabled) {
      background: #a83a3a;
    }
  }

  &--disabled,
  &:disabled {
    background: var(--color-primary-disabled);
    color: var(--color-muted);
    cursor: not-allowed;
  }

  &--loading {
    pointer-events: none;
    opacity: 0.7;
  }

  &__spinner {
    width: 14px;
    height: 14px;
    border: 2px solid currentColor;
    border-top-color: transparent;
    border-radius: 50%;
    animation: spin 0.6s linear infinite;
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
