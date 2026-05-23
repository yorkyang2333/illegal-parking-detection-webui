<template>
  <div class="thought-panel code-window-card">
    <div class="thought-panel__header">
      <span class="thought-panel__title">分析过程</span>
      <span v-if="agentStore.isProcessing" class="thought-panel__indicator" />
      <span v-if="agentStore.isCompleted" class="thought-panel__done-badge">
        {{ agentStore.violations.length }} 项违停
      </span>
    </div>

    <div class="thought-panel__stream" ref="streamRef">
      <div v-if="agentStore.thoughts.length === 0" class="thought-panel__empty">
        等待分析启动...
      </div>
      <TransitionGroup name="thought-fade" tag="div" class="thought-panel__list">
        <div
          v-for="entry in agentStore.thoughts"
          :key="entry.id"
          class="thought-entry"
          :class="`thought-entry--${entry.type}`"
        >
          <div class="thought-entry__body">
            <div v-if="entry.type === 'tool_call'" class="thought-entry__tool-label">
              {{ entry.tool }}
            </div>
            <span class="thought-entry__content">{{ entry.content }}</span>
          </div>
          <span class="thought-entry__time">{{ relativeTime(entry.timestamp) }}</span>
        </div>
      </TransitionGroup>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useAgentStore } from '@/stores/useAgentStore'

const agentStore = useAgentStore()
const streamRef = ref<HTMLDivElement>()
const now = ref(Date.now())

let timer: ReturnType<typeof setInterval>
onMounted(() => { timer = setInterval(() => { now.value = Date.now() }, 10_000) })
onUnmounted(() => clearInterval(timer))

function relativeTime(ts: number): string {
  const diff = Math.floor((now.value - ts) / 1000)
  if (diff < 5) return '刚刚'
  if (diff < 60) return `${diff}s 前`
  return `${Math.floor(diff / 60)}m 前`
}

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
    gap: var(--space-sm);
    padding: var(--space-md) var(--space-xl);
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    flex-shrink: 0;
  }

  &__title {
    font-family: var(--font-body);
    font-size: 14px;
    font-weight: 500;
    color: var(--color-on-dark);
    flex: 1;
  }

  &__indicator {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--color-primary);
    animation: blink 1.4s ease-in-out infinite;
  }

  &__done-badge {
    font-size: 11px;
    color: var(--color-success);
    background: rgba(93, 184, 114, 0.15);
    padding: 2px 10px;
    border-radius: var(--radius-pill);
    font-family: var(--font-mono);
  }

  &__stream {
    flex: 1;
    overflow-y: auto;
    padding: var(--space-lg) var(--space-xl);
    min-height: 0;
    background: var(--color-surface-dark-soft);

    &::-webkit-scrollbar {
      width: 4px;
    }
    &::-webkit-scrollbar-track {
      background: transparent;
    }
    &::-webkit-scrollbar-thumb {
      background: rgba(255, 255, 255, 0.1);
      border-radius: 2px;
    }
  }

  &__list {
    display: flex;
    flex-direction: column;
    gap: var(--space-sm);
  }

  &__empty {
    font-size: 14px;
    color: var(--color-on-dark-soft);
    padding: var(--space-md) 0;
    font-family: var(--font-mono);
  }
}

.thought-entry {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-md);
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  font-size: 14px;
  line-height: 1.6;
  font-family: var(--font-mono);

  &__body {
    flex: 1;
    min-width: 0;
  }

  &__tool-label {
    display: inline-block;
    font-size: 12px;
    background: rgba(232, 165, 90, 0.15);
    color: var(--color-accent-amber);
    padding: 2px 8px;
    border-radius: var(--radius-sm);
    margin-bottom: var(--space-xs);
  }

  &__content {
    color: var(--color-on-dark-soft);
    word-break: break-word;
    display: block;
  }

  &__time {
    font-size: 12px;
    color: var(--color-muted);
    white-space: nowrap;
    flex-shrink: 0;
    margin-top: 2px;
  }

  &--thought {
    background: rgba(255, 255, 255, 0.02);
  }

  &--tool_call {
    background: rgba(232, 165, 90, 0.05);

    .thought-entry__content {
      color: var(--color-accent-amber);
      opacity: 0.8;
    }
  }

  &--tool_result {
    background: rgba(93, 184, 114, 0.05);

    .thought-entry__content {
      color: var(--color-success);
      opacity: 0.9;
    }
  }
}

.thought-fade-enter-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.thought-fade-enter-from {
  opacity: 0;
  transform: translateY(5px);
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}
</style>
