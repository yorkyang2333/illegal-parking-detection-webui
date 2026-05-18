<template>
  <div class="dropdown" ref="dropdownRef">
    <div @click="toggle">
      <slot name="trigger" />
    </div>
    <Transition name="dropdown">
      <div v-if="open" class="dropdown-menu" :class="`dropdown-menu--${align}`">
        <slot />
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'

defineProps<{
  align?: 'left' | 'right'
}>()

const open = ref(false)
const dropdownRef = ref<HTMLElement>()

function toggle() {
  open.value = !open.value
}

function handleClickOutside(e: MouseEvent) {
  if (dropdownRef.value && !dropdownRef.value.contains(e.target as Node)) {
    open.value = false
  }
}

onMounted(() => document.addEventListener('click', handleClickOutside))
onBeforeUnmount(() => document.removeEventListener('click', handleClickOutside))

defineExpose({ close: () => { open.value = false } })
</script>

<style scoped lang="scss">
.dropdown {
  position: relative;
  display: inline-block;
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 8px);
  z-index: 100;
  min-width: 180px;
  background: var(--color-canvas);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-lg);
  padding: var(--space-xs);
  box-shadow: 0 4px 12px rgba(20, 20, 19, 0.08);

  &--left {
    left: 0;
  }

  &--right {
    right: 0;
  }
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.15s, transform 0.15s;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
