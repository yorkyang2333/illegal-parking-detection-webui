<template>
  <span :class="['badge', `badge--${variant}`]">
    <slot />
  </span>
</template>

<script setup lang="ts">
defineProps<{
  variant?: 'pill' | 'coral' | 'success' | 'warning'
}>()
</script>

<style scoped lang="scss">
.badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: var(--radius-pill);
  font-size: 13px;
  font-weight: 500;
  line-height: 1.4;

  &--pill {
    background: var(--color-surface-card);
    color: var(--color-ink);
  }

  &--coral {
    background: var(--color-primary);
    color: var(--color-on-primary);
    font-size: 12px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
  }

  &--success {
    background: rgba(93, 184, 114, 0.15);
    color: var(--color-success);
  }

  &--warning {
    background: rgba(212, 160, 23, 0.15);
    color: var(--color-warning);
  }
}
</style>
