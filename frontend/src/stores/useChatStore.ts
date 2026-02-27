import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useSSE } from '@/composables/useSSE'
import { useAuthStore } from './useAuthStore'
import router from '@/router'
import type { InferenceRequest, PromptMessage, ConversationMessage, Conversation } from '@/api/types'

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

  // Conversation State
  const conversations = ref<Conversation[]>([])
  const activeConversationId = ref<number | null>(null)
  const uploadedVideoFilename = ref<string | null>(null)

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
      // Handle custom status updates from app.py
      if (data.status) {
        const lastMessage = messages.value[messages.value.length - 1]
        if (lastMessage && lastMessage.role === 'assistant') {
          currentStreamingContent.value = data.text + '\n\n'
          lastMessage.content = currentStreamingContent.value
        }
        return // Wait for actual completion and choices
      }

      // Handle standard text generation
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
    onError: (err: Error | any) => {
      if (err.status === 401) {
        const authStore = useAuthStore()
        authStore.clearError()
        error.value = '登录已过期，请重新登录'
        router.push('/login')
      } else {
        error.value = err.message || 'Unknown stream error'
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

    if (!activeConversationId.value) {
      await createNewConversation()
    }

    const payload: InferenceRequest = {
      prompt: formatPromptForAPI(content.trim()),
      model: 'gemini',
      conversation_id: activeConversationId.value!,
      video_filename: uploadedVideoFilename.value || undefined
    }

    try {
      await sse.start(payload)
      // Clear attached video after successful transmission
      uploadedVideoFilename.value = null
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      isStreaming.value = false
      assistantMessage.isStreaming = false
    }
  }

  function clearChat() {
    messages.value = []
    currentStreamingContent.value = ''
    activeConversationId.value = null
    uploadedVideoFilename.value = null
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

  async function fetchConversations() {
    try {
      const res = await fetch('/api/conversations')
      if (res.ok) {
        conversations.value = await res.json()
      }
    } catch (e) {
      console.error('Failed to fetch conversations', e)
    }
  }

  async function loadConversation(id: number) {
    try {
      const res = await fetch(`/api/conversations/${id}`)
      if (res.ok) {
        const data = await res.json()
        activeConversationId.value = data.conversation.id
        messages.value = data.messages.map((m: ConversationMessage) => ({
          id: m.id.toString(),
          role: m.role,
          content: m.content,
          timestamp: new Date(m.created_at)
        }))
      }
    } catch (e) {
      console.error('Failed to load conversation', e)
    }
  }

  async function createNewConversation(title = 'New Analysis') {
    try {
      const res = await fetch('/api/conversations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title })
      })
      if (res.ok) {
        const conv = await res.json()
        activeConversationId.value = conv.id
        conversations.value.unshift(conv)
      }
    } catch (e) {
      console.error('Failed to create conversation', e)
    }
  }

  async function uploadVideo(file: File) {
    try {
      const formData = new FormData()
      formData.append('video', file)

      const res = await fetch('/api/upload-video', {
        method: 'POST',
        body: formData
      })
      if (res.ok) {
        const data = await res.json()
        uploadedVideoFilename.value = data.filename
      } else {
        throw new Error('Upload failed')
      }
    } catch (e) {
      console.error('Video upload failed', e)
      error.value = 'Failed to upload video'
    }
  }

  return {
    // State
    messages,
    isStreaming,
    error,
    conversations,
    activeConversationId,
    uploadedVideoFilename,
    // Computed
    hasMessages,
    // Actions
    sendMessage,
    clearChat,
    stopStreaming,
    fetchConversations,
    loadConversation,
    createNewConversation,
    uploadVideo
  }
})
