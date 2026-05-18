<template>
  <div :class="['input-wrapper', { 'input-wrapper--focused': focused, 'input-wrapper--error': error }]">
    <label v-if="label" class="input-label">{{ label }}</label>
    <div class="input-container">
      <input
        ref="inputRef"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        class="input-field"
        @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
        @focus="focused = true"
        @blur="focused = false"
      />
      <slot name="suffix" />
    </div>
    <span v-if="error" class="input-error">{{ error }}</span>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  modelValue?: string
  label?: string
  placeholder?: string
  type?: string
  disabled?: boolean
  error?: string
}>()

defineEmits<{
  'update:modelValue': [value: string]
}>()

const focused = ref(false)
const inputRef = ref<HTMLInputElement>()

defineExpose({ focus: () => inputRef.value?.focus() })
</script>

<style scoped lang="scss">
.input-wrapper {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.input-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-body-strong);
}

.input-container {
  display: flex;
  align-items: center;
  background: var(--color-canvas);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-md);
  height: 40px;
  padding: 0 14px;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.input-wrapper--focused .input-container {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(204, 120, 92, 0.15);
}

.input-wrapper--error .input-container {
  border-color: var(--color-error);
  box-shadow: 0 0 0 3px rgba(198, 69, 69, 0.1);
}

.input-field {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 16px;
  line-height: 1.55;
  color: var(--color-ink);
  width: 100%;

  &::placeholder {
    color: var(--color-muted-soft);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.input-error {
  font-size: 13px;
  color: var(--color-error);
}
</style>
