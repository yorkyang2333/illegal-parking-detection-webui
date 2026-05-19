<template>
  <div class="thought-panel">
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
  background: var(--color-surface-dark, #181715);
  border-radius: var(--radius-lg, 12px);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 100%;

  &__header {
    display: flex;
    align-items: center;
    gap: var(--space-sm, 8px);
    padding: var(--space-md, 14px) var(--space-lg, 20px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.07);
    flex-shrink: 0;
  }

  &__title {
    font-size: 14px;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.85);
    flex: 1;
  }

  &__indicator {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--color-primary, #cc785c);
    animation: blink 1.4s ease-in-out infinite;
  }

  &__done-badge {
    font-size: 11px;
    color: var(--color-success, #5aac73);
    background: rgba(90, 172, 115, 0.15);
    padding: 2px 10px;
    border-radius: 20px;
  }

  &__stream {
    flex: 1;
    overflow-y: auto;
    padding: var(--space-sm, 10px) var(--space-md, 14px);
    min-height: 0;

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
    gap: 4px;
  }

  &__empty {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.2);
    padding: var(--space-md, 12px) 4px;
  }
}

.thought-entry {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
  padding: 7px 10px;
  border-radius: 6px;
  border-left: 2px solid transparent;
  font-size: 12px;
  line-height: 1.55;

  &__body {
    flex: 1;
    min-width: 0;
  }

  &__tool-label {
    display: inline-block;
    font-family: var(--font-mono, monospace);
    font-size: 10px;
    background: rgba(232, 196, 106, 0.18);
    color: #e8c46a;
    padding: 1px 6px;
    border-radius: 4px;
    margin-bottom: 3px;
    letter-spacing: 0.3px;
  }

  &__content {
    color: rgba(255, 255, 255, 0.55);
    word-break: break-word;
    display: block;
  }

  &__time {
    font-size: 10px;
    color: rgba(255, 255, 255, 0.2);
    white-space: nowrap;
    flex-shrink: 0;
    margin-top: 2px;
  }

  &--thought {
    background: rgba(255, 255, 255, 0.025);
    border-left-color: transparent;
  }

  &--tool_call {
    background: rgba(232, 196, 106, 0.06);
    border-left-color: #e8c46a;

    .thought-entry__content {
      color: rgba(232, 196, 106, 0.75);
    }
  }

  &--tool_result {
    background: rgba(90, 172, 115, 0.06);
    border-left-color: var(--color-success, #5aac73);

    .thought-entry__content {
      color: rgba(90, 172, 115, 0.8);
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
