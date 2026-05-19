<template>
  <div class="thought-panel">
    <div class="thought-panel__header">
      <span class="thought-panel__title">PRTS 分析核心</span>
      <span v-if="agentStore.isProcessing" class="thought-panel__pulse" />
    </div>

    <div class="thought-panel__phases">
      <div
        v-for="phase in agentStore.phases"
        :key="phase.id"
        class="phase-item"
        :class="`phase-item--${phase.status}`"
      >
        <span class="phase-item__dot" />
        <span class="phase-item__label">{{ phase.label }}</span>
      </div>
    </div>

    <div class="thought-panel__stream" ref="streamRef">
      <div v-if="agentStore.thoughts.length === 0" class="thought-panel__empty">
        等待分析启动...
      </div>
      <TransitionGroup name="thought-fade" tag="div">
        <div
          v-for="entry in agentStore.thoughts"
          :key="entry.id"
          class="thought-entry"
          :class="`thought-entry--${entry.type}`"
        >
          <span class="thought-entry__icon">
            {{ entry.type === 'tool_call' ? '⚙' : entry.type === 'tool_result' ? '✓' : '◈' }}
          </span>
          <span class="thought-entry__content">{{ entry.content }}</span>
        </div>
      </TransitionGroup>
    </div>

    <div v-if="agentStore.isCompleted" class="thought-panel__footer">
      <span class="thought-panel__done-badge">分析完成</span>
      <span class="thought-panel__violation-count">
        {{ agentStore.violations.length }} 辆违停
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { useAgentStore } from '@/stores/useAgentStore'

const agentStore = useAgentStore()
const streamRef = ref<HTMLDivElement>()

watch(
  () => agentStore.thoughts.length,
  async () => {
    await nextTick()
    if (streamRef.value) {
      streamRef.value.scrollTop = streamRef.value.scrollHeight
    }
  }
)
</script>

<style scoped lang="scss">
.thought-panel {
  background: var(--color-surface-dark);
  border-radius: var(--radius-lg);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 100%;

  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-md) var(--space-lg);
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    flex-shrink: 0;
  }

  &__title {
    font-family: var(--font-mono, monospace);
    font-size: 11px;
    letter-spacing: 2px;
    color: var(--color-primary, #7ba7c2);
    text-transform: uppercase;
  }

  &__pulse {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--color-primary, #7ba7c2);
    animation: pulse 1.2s ease-in-out infinite;
  }

  &__phases {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-xs, 4px) var(--space-sm, 8px);
    padding: var(--space-sm, 8px) var(--space-lg, 16px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    flex-shrink: 0;
  }

  &__stream {
    flex: 1;
    overflow-y: auto;
    padding: var(--space-md, 12px) var(--space-lg, 16px);
    display: flex;
    flex-direction: column;
    gap: var(--space-xs, 4px);
    min-height: 0;
  }

  &__empty {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.25);
    font-family: var(--font-mono, monospace);
    padding: var(--space-md, 12px) 0;
  }

  &__footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-sm, 8px) var(--space-lg, 16px);
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    flex-shrink: 0;
  }

  &__done-badge {
    font-size: 11px;
    color: var(--color-success, #5aac73);
    background: rgba(90, 172, 115, 0.15);
    padding: 2px 8px;
    border-radius: 10px;
    font-family: var(--font-mono, monospace);
  }

  &__violation-count {
    font-size: 12px;
    color: var(--color-on-dark-soft, rgba(255, 255, 255, 0.5));
  }
}

.phase-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-family: var(--font-mono, monospace);
  font-size: 11px;
  color: rgba(255, 255, 255, 0.35);

  &__dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.2);
    flex-shrink: 0;
    transition: background 0.2s;
  }

  &__label {
    transition: color 0.2s;
  }

  &--running {
    color: var(--color-primary, #7ba7c2);

    .phase-item__dot {
      background: var(--color-primary, #7ba7c2);
      animation: pulse 0.8s ease-in-out infinite;
    }
  }

  &--done {
    color: var(--color-success, #5aac73);

    .phase-item__dot {
      background: var(--color-success, #5aac73);
    }
  }
}

.thought-entry {
  display: flex;
  gap: var(--space-xs, 4px);
  font-size: 12px;
  line-height: 1.5;
  color: rgba(255, 255, 255, 0.5);

  &__icon {
    flex-shrink: 0;
    font-size: 11px;
    margin-top: 2px;
    opacity: 0.7;
  }

  &__content {
    word-break: break-word;
  }

  &--tool_call {
    color: #e8c46a;
  }

  &--tool_result {
    color: var(--color-success, #5aac73);
  }
}

.thought-fade-enter-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.thought-fade-enter-from {
  opacity: 0;
  transform: translateY(6px);
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.35; }
}
</style>
