<template>
  <div class="history">
    <header class="history__header">
      <h1 class="history__title">历史记录</h1>
      <p class="history__desc">查看过往的分析和对话记录</p>
    </header>

    <div v-if="loading" class="history__loading">
      <div class="spinner" />
    </div>

    <div v-else-if="conversations.length === 0" class="history__empty">
      <p>暂无历史记录</p>
    </div>

    <div v-else class="history__list">
      <div
        v-for="conv in conversations"
        :key="conv.id"
        class="history-card"
        @click="viewConversation(conv.id)"
      >
        <div class="history-card__header">
          <h3 class="history-card__title">{{ conv.title }}</h3>
          <button class="history-card__delete" @click.stop="deleteConversation(conv.id)">
            <Trash2 :size="15" />
          </button>
        </div>
        <span class="history-card__date">{{ formatDate(conv.created_at) }}</span>
      </div>
    </div>

    <BaseDialog v-model="detailOpen" title="对话详情" width="640px">
      <div v-if="detailMessages.length" class="history-detail">
        <div v-for="msg in detailMessages" :key="msg.id" class="detail-msg" :class="`detail-msg--${msg.role}`">
          <span class="detail-msg__role">{{ msg.role === 'user' ? '用户' : 'AI' }}</span>
          <MarkdownRenderer :content="msg.content" />
        </div>
      </div>
      <p v-else class="history-detail__empty">无消息记录</p>
    </BaseDialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Trash2 } from 'lucide-vue-next'
import BaseDialog from '@/components/ui/BaseDialog.vue'
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'
import type { Conversation } from '@/api/types'

interface DetailMessage {
  id: number
  role: string
  content: string
}

const conversations = ref<Conversation[]>([])
const loading = ref(true)
const detailOpen = ref(false)
const detailMessages = ref<DetailMessage[]>([])

onMounted(fetchHistory)

async function fetchHistory() {
  loading.value = true
  try {
    const res = await fetch('/api/conversations', { credentials: 'include' })
    if (res.ok) conversations.value = await res.json()
  } finally {
    loading.value = false
  }
}

async function viewConversation(id: number) {
  try {
    const res = await fetch(`/api/conversations/${id}`, { credentials: 'include' })
    if (res.ok) {
      const data = await res.json()
      detailMessages.value = data.messages
      detailOpen.value = true
    }
  } catch { /* ignore */ }
}

async function deleteConversation(id: number) {
  try {
    const res = await fetch(`/api/conversations/${id}`, { method: 'DELETE', credentials: 'include' })
    if (res.ok) {
      conversations.value = conversations.value.filter(c => c.id !== id)
    }
  } catch { /* ignore */ }
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped lang="scss">
.history {
  padding: var(--space-xl) 0;
}

.history__header {
  margin-bottom: var(--space-xl);
}

.history__title {
  font-family: var(--font-display);
  font-size: 36px;
  font-weight: 400;
  letter-spacing: -0.5px;
  color: var(--color-ink);
  margin-bottom: var(--space-xs);
}

.history__desc {
  font-size: 16px;
  color: var(--color-muted);
}

.history__loading {
  display: flex;
  justify-content: center;
  padding: var(--space-xxl);
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid var(--color-hairline);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.history__empty {
  text-align: center;
  padding: var(--space-xxl);
  color: var(--color-muted);
}

.history__list {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.history-card {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
  padding: var(--space-lg);
  background: var(--color-surface-card);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: background-color 0.15s;

  &:hover {
    background: var(--color-surface-cream-strong);
  }
}

.history-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.history-card__title {
  font-size: 15px;
  font-weight: 500;
  color: var(--color-ink);
}

.history-card__delete {
  color: var(--color-muted-soft);
  padding: 4px;
  border-radius: var(--radius-sm);

  &:hover {
    color: var(--color-error);
    background: rgba(198, 69, 69, 0.08);
  }
}

.history-card__date {
  font-size: 13px;
  color: var(--color-muted-soft);
}

.history-detail {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
  max-height: 60vh;
  overflow-y: auto;
}

.detail-msg {
  &__role {
    display: inline-block;
    font-size: 12px;
    font-weight: 500;
    color: var(--color-muted);
    margin-bottom: var(--space-xs);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  &--user {
    padding-left: var(--space-md);
    border-left: 2px solid var(--color-hairline);
  }
}

.history-detail__empty {
  text-align: center;
  color: var(--color-muted);
  padding: var(--space-xl);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
