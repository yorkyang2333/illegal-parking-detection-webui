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
  animation: fadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) both;

  &--user {
    justify-content: flex-end;
  }

  &--assistant {
    justify-content: flex-start;
  }
}

.chat-message__bubble {
  max-width: 75%;
  border-radius: var(--radius-xl);
  padding: var(--space-md) var(--space-lg);
  font-family: var(--font-body);

  .chat-message--user & {
    background: var(--color-primary);
    color: var(--color-on-primary);
    border-bottom-right-radius: 4px;
    box-shadow: 0 4px 12px rgba(204, 120, 92, 0.15);
  }

  .chat-message--assistant & {
    background: transparent;
    padding-left: 0;
    padding-right: 0;
    color: var(--color-ink);
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

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
