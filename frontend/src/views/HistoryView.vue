<template>
  <div class="history">
    <header class="history__header">
      <h1 class="history__title">
        Activity <br/>
        <span class="italic">Log.</span>
      </h1>
      <p class="history__desc">查看您的历史分析与对话记录</p>
    </header>

    <div v-if="loading" class="history__loading">
      <div class="spinner" />
    </div>

    <div v-else-if="conversations.length === 0" class="history__empty">
      <p>暂无历史记录</p>
    </div>

    <div v-else class="history__grid">
      <div
        v-for="conv in conversations"
        :key="conv.id"
        class="history-card feature-card"
        @click="viewConversation(conv.id)"
      >
        <div class="history-card__content">
          <h3 class="history-card__title">{{ conv.title }}</h3>
          <span class="history-card__date">{{ formatDate(conv.created_at) }}</span>
        </div>
        <button class="history-card__delete" @click.stop="deleteConversation(conv.id)" title="删除记录">
          <Trash2 :size="16" stroke-width="1.5" />
        </button>
      </div>
    </div>

    <BaseDialog v-model="detailOpen" title="记录详情" width="720px">
      <div class="dialog-editorial-wrapper">
        <div v-if="detailMessages.length" class="history-detail">
          <div v-for="msg in detailMessages" :key="msg.id" class="detail-msg" :class="`detail-msg--${msg.role}`">
            <span class="detail-msg__role">{{ msg.role === 'user' ? 'USER' : 'SYSTEM' }}</span>
            <div class="detail-msg__content">
              <MarkdownRenderer :content="msg.content" />
            </div>
          </div>
        </div>
        <p v-else class="history-detail__empty">此对话暂无内容</p>
      </div>
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
  max-width: 900px;
  margin: 0 auto;
}

.history__header {
  margin-bottom: var(--space-xxl);
}

.history__title {
  font-family: var(--font-display);
  font-size: clamp(40px, 5vw, 56px);
  line-height: 0.95;
  font-weight: 400;
  letter-spacing: -1.5px;
  color: var(--color-ink);
  margin-bottom: var(--space-sm);

  .italic {
    font-style: italic;
    color: var(--color-muted);
  }
}

.history__desc {
  font-family: var(--font-body);
  font-size: 16px;
  color: var(--color-muted);
}

.history__loading {
  display: flex;
  justify-content: center;
  padding: var(--space-xxl);
}

.spinner {
  width: 32px;
  height: 32px;
  border: 2px solid var(--color-hairline);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s cubic-bezier(0.6, 0.2, 0.4, 0.8) infinite;
}

.history__empty {
  text-align: center;
  padding: var(--space-xxl);
  color: var(--color-muted);
  font-family: var(--font-mono);
  font-size: 14px;
  letter-spacing: 0.5px;
}

.history__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--space-lg);
}

.feature-card {
  background: var(--color-canvas);
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-xl);
  padding: var(--space-xl);
  box-shadow: 0 4px 20px rgba(0,0,0,0.02);
  transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  cursor: pointer;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.06);
    border-color: rgba(0,0,0,0.1);
  }
}

.history-card__content {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  flex: 1;
  min-width: 0;
}

.history-card__title {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 400;
  color: var(--color-ink);
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.history-card__date {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--color-muted);
  letter-spacing: 0.5px;
}

.history-card__delete {
  color: var(--color-muted-soft);
  padding: 8px;
  margin: -8px -8px 0 0;
  border-radius: 50%;
  transition: all 0.2s ease;
  background: transparent;

  &:hover {
    color: var(--color-error);
    background: rgba(198, 69, 69, 0.08);
  }
}

.dialog-editorial-wrapper {
  padding: var(--space-md) 0;
}

.history-detail {
  display: flex;
  flex-direction: column;
  gap: var(--space-xxl);
  max-height: 65vh;
  overflow-y: auto;
  padding-right: var(--space-md);
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  &::-webkit-scrollbar-thumb {
    background: var(--color-hairline);
    border-radius: 3px;
  }
}

.detail-msg {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);

  &__role {
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 500;
    color: var(--color-primary);
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  &__content {
    font-family: var(--font-body);
    font-size: 15px;
    line-height: 1.6;
    color: var(--color-ink);
  }

  &--system {
    .detail-msg__role {
      color: var(--color-muted);
    }
    padding-left: var(--space-lg);
    border-left: 1px solid var(--color-hairline);
  }
}

.history-detail__empty {
  text-align: center;
  color: var(--color-muted);
  padding: var(--space-xxl) 0;
  font-family: var(--font-mono);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
