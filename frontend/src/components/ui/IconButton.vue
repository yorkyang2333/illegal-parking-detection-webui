<template>
  <button :class="['icon-btn', { 'icon-btn--active': active }]" @click="$emit('click', $event)">
    <slot />
  </button>
</template>

<script setup lang="ts">
defineProps<{
  active?: boolean
}>()

defineEmits<{
  click: [e: MouseEvent]
}>()
</script>

<style scoped lang="scss">
.icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-pill);
  color: var(--color-muted);
  transition: background-color 0.15s, color 0.15s;

  &:hover {
    background: var(--color-surface-soft);
    color: var(--color-ink);
  }

  &--active {
    background: var(--color-surface-card);
    color: var(--color-ink);
  }
}
</style>
