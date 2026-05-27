<template>
  <div class="chat-view">
    <aside class="chat-view__sidebar" :class="{ 'chat-view__sidebar--open': sidebarOpen }">
      <div class="sidebar-header">
        <h3 class="sidebar-title">
          <span class="sidebar-title__icon">✦</span>
          COMMAND.
        </h3>
        <BaseButton variant="primary" @click="handleNewChat" class="sidebar-new-btn">
          新对话
        </BaseButton>
      </div>
      <ConversationList
        :conversations="chatStore.conversations"
        :active-id="chatStore.activeConversationId"
        @select="handleSelectConversation"
      />
    </aside>

    <main class="chat-view__main">
      <div class="chat-view__toggle">
        <IconButton @click="sidebarOpen = !sidebarOpen">
          <PanelLeft :size="18" />
        </IconButton>
      </div>

      <MessageThread :messages="chatStore.messages" :is-streaming="chatStore.isStreaming" />

      <ChatInput
        :is-streaming="chatStore.isStreaming"
        :has-media="!!chatStore.uploadedMediaFilename"
        :models="chatStore.availableModels"
        :current-model="chatStore.selectedModel"
        @send="handleSend"
        @stop="chatStore.stopStreaming()"
        @upload="handleUpload"
        @select-model="chatStore.setModel($event)"
      />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { PanelLeft } from 'lucide-vue-next'
import { useChatStore } from '@/stores/useChatStore'
import BaseButton from '@/components/ui/BaseButton.vue'
import IconButton from '@/components/ui/IconButton.vue'
import ConversationList from '@/components/chat/ConversationList.vue'
import MessageThread from '@/components/chat/MessageThread.vue'
import ChatInput from '@/components/chat/ChatInput.vue'

const chatStore = useChatStore()
const sidebarOpen = ref(true)

onMounted(() => {
  chatStore.fetchConversations()
  chatStore.fetchModels()
})

function handleNewChat() {
  chatStore.clearChat()
}

function handleSelectConversation(id: number) {
  chatStore.loadConversation(id)
}

function handleSend(content: string) {
  chatStore.sendMessage(content)
}

function handleUpload(file: File) {
  chatStore.uploadMedia(file)
}
</script>

<style scoped lang="scss">
.chat-view {
  display: flex;
  height: calc(100vh - var(--nav-height) - var(--space-xl) * 2);
  margin: calc(-1 * var(--space-xl)) calc(-1 * var(--space-lg));
  margin-top: 0;

  @media (max-width: 767px) {
    margin: calc(-1 * var(--space-md));
    margin-top: 0;
    height: calc(100vh - var(--nav-height) - var(--space-md) * 2);
  }
}

.chat-view__sidebar {
  width: 280px;
  flex-shrink: 0;
  border-right: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  flex-direction: column;
  background: var(--color-surface-dark);
  color: var(--color-canvas);
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    inset: 0;
    opacity: 0.04;
    background-image: url('data:image/svg+xml,%3Csvg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"%3E%3Cfilter id="noiseFilter"%3E%3CfeTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="3" stitchTiles="stitch"/%3E%3C/filter%3E%3Crect width="100%25" height="100%25" filter="url(%23noiseFilter)"/%3E%3C/svg%3E');
    pointer-events: none;
    z-index: 0;
  }

  > * {
    position: relative;
    z-index: 1;
  }

  @media (max-width: 767px) {
    position: fixed;
    left: 0;
    top: var(--nav-height);
    bottom: 0;
    z-index: 40;
    transform: translateX(-100%);
    transition: transform 0.2s ease;
    box-shadow: 4px 0 12px rgba(0, 0, 0, 0.08);

    &--open {
      transform: translateX(0);
    }
  }
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-lg);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.sidebar-title {
  font-family: var(--font-mono);
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 2px;
  color: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  gap: var(--space-sm);

  &__icon {
    color: var(--color-primary);
  }
}

.sidebar-new-btn {
  padding: 8px 14px;
  height: 32px;
  font-size: 13px;
}

.chat-view__main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  position: relative;
  background: var(--color-canvas);
}

.chat-view__toggle {
  position: absolute;
  top: var(--space-sm);
  left: var(--space-sm);
  z-index: 10;

  @media (min-width: 768px) {
    display: none;
  }
}
</style>
