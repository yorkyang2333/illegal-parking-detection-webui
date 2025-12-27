import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useSSE } from '@/composables/useSSE'
import { useAuthStore } from './useAuthStore'
import router from '@/router'
import type { InferenceRequest, PromptMessage } from '@/api/types'

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  isStreaming?: boolean
}

export const useChatStore = defineStore('chat', () => {
  // State
  const messages = ref<ChatMessage[]>([])
  const isStreaming = ref(false)
  const error = ref<string | null>(null)
  const currentStreamingContent = ref('')

  // Computed
  const hasMessages = computed(() => messages.value.length > 0)

  // Generate unique ID
  function generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`
  }

  // Format messages for API
  function formatPromptForAPI(userMessage: string): PromptMessage[] {
    return [
      {
        role: 'user' as const,
        content: [
          { video: [] as unknown[] },
          { text: userMessage }
        ]
      }
    ]
  }

  // API URL
  const apiUrl = '/api/run'

  // SSE instance
  const sse = useSSE(apiUrl, {
    onMessage: (data) => {
      const text = data.output?.choices?.[0]?.message?.content?.[0]?.text
      if (text) {
        currentStreamingContent.value += text
        // Update the last assistant message
        const lastMessage = messages.value[messages.value.length - 1]
        if (lastMessage && lastMessage.role === 'assistant') {
          lastMessage.content = currentStreamingContent.value
        }
      }
    },
    onError: (err: any) => {
      if (err.status === 401) {
        const authStore = useAuthStore()
        authStore.clearError()
        error.value = '登录已过期，请重新登录'
        router.push('/login')
      } else {
        error.value = err.message
      }
      isStreaming.value = false
      // Mark last message as not streaming
      const lastMessage = messages.value[messages.value.length - 1]
      if (lastMessage && lastMessage.role === 'assistant') {
        lastMessage.isStreaming = false
      }
    },
    onComplete: () => {
      isStreaming.value = false
      // Mark last message as not streaming
      const lastMessage = messages.value[messages.value.length - 1]
      if (lastMessage && lastMessage.role === 'assistant') {
        lastMessage.isStreaming = false
      }
    }
  })

  // Actions
  async function sendMessage(content: string) {
    if (!content.trim() || isStreaming.value) return

    // Add user message
    const userMessage: ChatMessage = {
      id: generateId(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date()
    }
    messages.value.push(userMessage)

    // Add placeholder assistant message
    currentStreamingContent.value = ''
    const assistantMessage: ChatMessage = {
      id: generateId(),
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isStreaming: true
    }
    messages.value.push(assistantMessage)

    // Start streaming
    error.value = null
    isStreaming.value = true

    const payload: InferenceRequest = {
      prompt: formatPromptForAPI(content.trim()),
      model: 'dashscope'
    }

    try {
      await sse.start(payload)
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      isStreaming.value = false
      assistantMessage.isStreaming = false
    }
  }

  function clearChat() {
    messages.value = []
    currentStreamingContent.value = ''
    error.value = null
    if (isStreaming.value) {
      sse.stop()
      isStreaming.value = false
    }
  }

  function stopStreaming() {
    sse.stop()
    isStreaming.value = false
    const lastMessage = messages.value[messages.value.length - 1]
    if (lastMessage && lastMessage.role === 'assistant') {
      lastMessage.isStreaming = false
    }
  }

  return {
    // State
    messages,
    isStreaming,
    error,
    // Computed
    hasMessages,
    // Actions
    sendMessage,
    clearChat,
    stopStreaming
  }
})
