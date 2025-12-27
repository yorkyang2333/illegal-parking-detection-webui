<template>
  <div class="chat-message" :class="[message.role, { streaming: message.isStreaming }]">
    <div class="message-avatar">
      <div v-if="message.role === 'user'" class="avatar user-avatar">
        <el-icon><User /></el-icon>
      </div>
      <div v-else class="avatar ai-avatar">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
    </div>
    <div class="message-content">
      <div class="message-header">
        <span class="message-role">{{ message.role === 'user' ? '你' : 'AI 助手' }}</span>
        <span class="message-time">{{ formatTime(message.timestamp) }}</span>
      </div>
      <div class="message-bubble">
        <div v-if="message.role === 'assistant' && message.content" class="markdown-content">
          <MarkdownViewer :content="message.content" />
        </div>
        <div v-else-if="message.role === 'assistant' && message.isStreaming && !message.content" class="typing-indicator">
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </div>
        <div v-else class="text-content">
          {{ message.content }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { User } from '@element-plus/icons-vue'
import MarkdownViewer from '@/components/common/MarkdownViewer.vue'
import type { ChatMessage } from '@/stores/useChatStore'

defineProps<{
  message: ChatMessage
}>()

function formatTime(date: Date): string {
  const d = new Date(date)
  const hours = d.getHours().toString().padStart(2, '0')
  const minutes = d.getMinutes().toString().padStart(2, '0')
  return `${hours}:${minutes}`
}
</script>

<style scoped lang="scss">
.chat-message {
  display: flex;
  gap: 16px;
  padding: 20px 0;
  animation: fadeIn 0.3s ease;

  &.user {
    flex-direction: row-reverse;

    .message-content {
      align-items: flex-end;
    }

    .message-header {
      flex-direction: row-reverse;
    }

    .message-bubble {
      background: #5b6eae;
      color: white;
      border-radius: 20px 20px 4px 20px;
    }

    .text-content {
      white-space: pre-wrap;
    }
  }

  &.assistant {
    .message-bubble {
      background: #f9fafb;
      border: 1px solid #e5e7eb;
      border-radius: 20px 20px 20px 4px;
    }
  }

  &.streaming .message-bubble {
    position: relative;

    &::after {
      content: '';
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      height: 2px;
      background: #5b6eae;
      animation: pulse 1.5s infinite ease-in-out;
    }
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.4;
  }
  50% {
    opacity: 1;
  }
}

.message-avatar {
  flex-shrink: 0;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;

  &.user-avatar {
    background: #5b6eae;
    color: white;
  }

  &.ai-avatar {
    background: #f3f4f6;
    border: 1px solid #e5e7eb;
    color: #5b6eae;

    svg {
      width: 22px;
      height: 22px;
    }
  }
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-width: 75%;
  min-width: 100px;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 4px;
}

.message-role {
  font-size: 13px;
  font-weight: 600;
  color: #1f2937;
}

.message-time {
  font-size: 12px;
  color: #9ca3af;
}

.message-bubble {
  padding: 14px 18px;
  line-height: 1.6;
  font-size: 15px;
  word-break: break-word;
}

.text-content {
  white-space: pre-wrap;
}

.markdown-content {
  :deep(p) {
    margin: 0 0 0.8em;

    &:last-child {
      margin-bottom: 0;
    }
  }

  :deep(ul), :deep(ol) {
    margin: 0.5em 0;
    padding-left: 1.5em;
  }

  :deep(code) {
    background: rgba(0, 0, 0, 0.06);
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'Fira Code', monospace;
    font-size: 0.9em;
  }

  :deep(pre) {
    background: #1f2937;
    color: #e5e7eb;
    padding: 16px;
    border-radius: 10px;
    overflow-x: auto;
    margin: 0.8em 0;

    code {
      background: transparent;
      padding: 0;
      color: inherit;
    }
  }

  :deep(blockquote) {
    border-left: 4px solid #5b6eae;
    padding-left: 16px;
    margin: 0.8em 0;
    color: #6b7280;
  }
}

.typing-indicator {
  display: flex;
  gap: 5px;
  padding: 4px 0;

  .dot {
    width: 8px;
    height: 8px;
    background: #9ca3af;
    border-radius: 50%;
    animation: bounce 1.4s infinite ease-in-out both;

    &:nth-child(1) {
      animation-delay: -0.32s;
    }

    &:nth-child(2) {
      animation-delay: -0.16s;
    }
  }
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0.6);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-message {
    gap: 12px;
    padding: 16px 0;
  }

  .avatar {
    width: 36px;
    height: 36px;
    border-radius: 10px;
  }

  .message-content {
    max-width: 85%;
  }

  .message-bubble {
    padding: 12px 14px;
    font-size: 14px;
  }
}
</style>
