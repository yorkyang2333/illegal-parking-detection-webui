import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useSSE } from '@/composables/useSSE'
import { useAuthStore } from './useAuthStore'
import router from '@/router'
import type { InferenceRequest, PromptMessage } from '@/api/types'

const DEFAULT_PROMPT = `现有一段违停的分析报告：
[粘贴Gemini生成的违停分析报告]
由QVQ-Max重新识别了车牌号为：
[粘贴QVQ-Max识别到的车牌号]
请帮我把QVQ-Max识别到的车牌号替换报告中原先识别到的车牌号，依据且仅依据原报告中的内容，重新生成一份详尽违停报告。请依次输出：
1.违停车辆车牌号
2.该车辆违停原因（根据原分析报告中的内容进一步总结得出）
3.建议处罚（根据现行《中华人民共和国道路交通安全法》）
请确保仅按照原报告中的内容进行重新输出，保证格式清晰明确，逻辑性强，不要主观臆断。`

export const useInferenceStore = defineStore('inference', () => {
  // State
  const userInput = ref(DEFAULT_PROMPT)
  const streamingOutput = ref('')
  const isStreaming = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const hasOutput = computed(() => streamingOutput.value.length > 0)

  const formattedPrompt = computed((): PromptMessage[] => {
    return [
      {
        role: 'user' as const,
        content: [
          { video: [] as unknown[] },
          { text: userInput.value }
        ]
      }
    ]
  })

  // API URL - use proxy path
  const apiUrl = '/api/run'

  // SSE instance
  const sse = useSSE(apiUrl, {
    onMessage: (data) => {
      const text = data.output?.choices?.[0]?.message?.content?.[0]?.text
      if (text) {
        streamingOutput.value += text
      }
    },
    onError: (err: any) => {
      // Handle 401 Unauthorized - redirect to login
      if (err.status === 401) {
        const authStore = useAuthStore()
        authStore.clearError()
        error.value = '登录已过期，请重新登录'
        router.push('/login')
      } else {
        error.value = err.message
      }
      isStreaming.value = false
    },
    onComplete: () => {
      isStreaming.value = false
    }
  })

  // Actions
  async function startInference() {
    streamingOutput.value = ''
    error.value = null
    isStreaming.value = true

    const payload: InferenceRequest = {
      prompt: formattedPrompt.value,
      model: 'gemini'
    }

    try {
      await sse.start(payload)
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Unknown error'
      isStreaming.value = false
    }
  }

  function resetPrompt() {
    userInput.value = DEFAULT_PROMPT
  }

  function clearOutput() {
    streamingOutput.value = ''
    error.value = null
  }

  function stopInference() {
    sse.stop()
    isStreaming.value = false
  }

  return {
    // State
    userInput,
    streamingOutput,
    isStreaming,
    error,
    // Computed
    hasOutput,
    // Actions
    startInference,
    resetPrompt,
    clearOutput,
    stopInference
  }
})
