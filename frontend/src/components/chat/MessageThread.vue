<template>
  <div class="message-thread" ref="threadRef">
    <div v-if="messages.length === 0" class="message-thread__empty">
      <h2 class="empty-title">
        <span class="italic">Mobility</span> <br/>
        Intelligence.
      </h2>
      <p class="empty-desc">输入问题或上传视频，AI 将为您深入分析违停场景。</p>
    </div>

    <ChatMessage
      v-for="msg in messages"
      :key="msg.id"
      :message="msg"
    />

    <div v-if="isStreaming" class="streaming-indicator">
      <span class="streaming-dot" />
      <span class="streaming-dot" />
      <span class="streaming-dot" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import ChatMessage from './ChatMessage.vue'
import type { ChatMessage as ChatMessageType } from '@/stores/useChatStore'

const props = defineProps<{
  messages: ChatMessageType[]
  isStreaming: boolean
}>()

const threadRef = ref<HTMLElement>()

watch(() => props.messages.length, async () => {
  await nextTick()
  if (threadRef.value) {
    threadRef.value.scrollTop = threadRef.value.scrollHeight
  }
})

watch(() => props.messages[props.messages.length - 1]?.content, async () => {
  await nextTick()
  if (threadRef.value) {
    threadRef.value.scrollTop = threadRef.value.scrollHeight
  }
})
</script>

<style scoped lang="scss">
.message-thread {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-xxl) var(--space-xl);
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
  max-width: 800px;
  width: 100%;
  margin: 0 auto;

  &::-webkit-scrollbar {
    width: 6px;
  }
  &::-webkit-scrollbar-thumb {
    background: var(--color-hairline);
    border-radius: 3px;
  }
}

.message-thread__empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  animation: fadeIn 0.8s ease;
}

.empty-title {
  font-family: var(--font-display);
  font-size: clamp(48px, 6vw, 72px);
  font-weight: 400;
  line-height: 0.95;
  letter-spacing: -2px;
  color: var(--color-ink);
  margin-bottom: var(--space-md);

  .italic {
    font-style: italic;
    color: var(--color-muted);
  }
}

.empty-desc {
  font-family: var(--font-body);
  font-size: 16px;
  color: var(--color-muted);
}

.streaming-indicator {
  display: flex;
  gap: 6px;
  padding: var(--space-md) 0;
}

.streaming-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-primary);
  animation: pulse 1.2s ease-in-out infinite;

  &:nth-child(2) { animation-delay: 0.2s; }
  &:nth-child(3) { animation-delay: 0.4s; }
}

@keyframes pulse {
  0%, 100% { opacity: 0.2; transform: scale(0.8); }
  50% { opacity: 1; transform: scale(1); }
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
