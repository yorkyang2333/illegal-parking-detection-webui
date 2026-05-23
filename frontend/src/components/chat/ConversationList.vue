<template>
  <div class="conversation-list">
    <div
      v-for="conv in conversations"
      :key="conv.id"
      class="conversation-item"
      :class="{ 'conversation-item--active': conv.id === activeId }"
      @click="$emit('select', conv.id)"
    >
      <span class="conversation-item__title">{{ conv.title }}</span>
      <span class="conversation-item__date">{{ formatDate(conv.updated_at || conv.created_at) }}</span>
    </div>
    <div v-if="conversations.length === 0" class="conversation-list__empty">
      <p>暂无对话记录</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Conversation } from '@/api/types'

defineProps<{
  conversations: Conversation[]
  activeId: number | null
}>()

defineEmits<{
  select: [id: number]
}>()

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}
</script>

<style scoped lang="scss">
.conversation-list {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-md);
  
  &::-webkit-scrollbar {
    width: 4px;
  }
  &::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 2px;
  }
}

.conversation-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
  padding: var(--space-md);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: var(--space-xs);
  border: 1px solid transparent;

  &:hover {
    background: rgba(255, 255, 255, 0.04);
  }

  &--active {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(255, 255, 255, 0.1);
  }

  &__title {
    font-family: var(--font-body);
    font-size: 14px;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.9);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &__date {
    font-family: var(--font-mono);
    font-size: 11px;
    color: rgba(255, 255, 255, 0.4);
    letter-spacing: 0.5px;
  }
}

.conversation-list__empty {
  padding: var(--space-xl);
  text-align: center;
  color: rgba(255, 255, 255, 0.3);
  font-family: var(--font-mono);
  font-size: 13px;
  letter-spacing: 1px;
}
</style>
