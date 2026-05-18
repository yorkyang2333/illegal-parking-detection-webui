<template>
  <div :class="['card', `card--${variant}`]">
    <slot />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  variant?: 'cream' | 'feature' | 'dark' | 'hairline' | 'coral'
}>()
</script>

<style scoped lang="scss">
.card {
  border-radius: var(--radius-lg);
  padding: var(--space-xl);

  &--cream {
    background: var(--color-canvas);
  }

  &--feature {
    background: var(--color-surface-card);
  }

  &--dark {
    background: var(--color-surface-dark);
    color: var(--color-on-dark);
  }

  &--hairline {
    background: var(--color-canvas);
    border: 1px solid var(--color-hairline);
  }

  &--coral {
    background: var(--color-primary);
    color: var(--color-on-primary);
  }
}
</style>
