<template>
  <div :class="['chat-message', `chat-message--${message.role}`]">
    <div class="chat-message__bubble">
      <MarkdownRenderer v-if="message.role === 'assistant'" :content="message.content" />
      <p v-else class="chat-message__text">{{ message.content }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'
import type { ChatMessage } from '@/stores/useChatStore'

defineProps<{
  message: ChatMessage
}>()
</script>

<style scoped lang="scss">
.chat-message {
  display: flex;

  &--user {
    justify-content: flex-end;
  }

  &--assistant {
    justify-content: flex-start;
  }
}

.chat-message__bubble {
  max-width: 75%;
  border-radius: var(--radius-lg);
  padding: var(--space-md) var(--space-lg);

  .chat-message--user & {
    background: var(--color-surface-card);
    color: var(--color-ink);
  }

  .chat-message--assistant & {
    background: transparent;
    padding-left: 0;
    padding-right: 0;
  }

  @media (max-width: 767px) {
    max-width: 90%;
  }
}

.chat-message__text {
  font-size: 15px;
  line-height: 1.55;
  white-space: pre-wrap;
}
</style>
