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
  padding: var(--space-xs);
}

.conversation-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background-color 0.1s;

  &:hover {
    background: var(--color-surface-soft);
  }

  &--active {
    background: var(--color-surface-card);
  }

  &__title {
    font-size: 14px;
    font-weight: 500;
    color: var(--color-ink);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &__date {
    font-size: 12px;
    color: var(--color-muted-soft);
  }
}

.conversation-list__empty {
  padding: var(--space-xl);
  text-align: center;
  color: var(--color-muted-soft);
  font-size: 14px;
}
</style>
