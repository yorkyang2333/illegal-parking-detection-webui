<template>
  <div class="message-thread" ref="threadRef">
    <div v-if="messages.length === 0" class="message-thread__empty">
      <h2 class="empty-title">开始对话</h2>
      <p class="empty-desc">输入问题或上传媒体文件，AI 将为您分析</p>
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
  padding: var(--space-xl);
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.message-thread__empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.empty-title {
  font-family: var(--font-display);
  font-size: 28px;
  font-weight: 400;
  letter-spacing: -0.3px;
  color: var(--color-ink);
  margin-bottom: var(--space-xs);
}

.empty-desc {
  font-size: 15px;
  color: var(--color-muted);
}

.streaming-indicator {
  display: flex;
  gap: 4px;
  padding: var(--space-sm) 0;
}

.streaming-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-muted-soft);
  animation: pulse 1.2s ease-in-out infinite;

  &:nth-child(2) { animation-delay: 0.2s; }
  &:nth-child(3) { animation-delay: 0.4s; }
}

@keyframes pulse {
  0%, 100% { opacity: 0.3; transform: scale(0.8); }
  50% { opacity: 1; transform: scale(1); }
}
</style>
