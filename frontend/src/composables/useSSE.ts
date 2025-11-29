import { ref } from 'vue'
import type { SSEResponseChunk } from '@/api/types'

interface UseSSEOptions {
  onMessage: (data: SSEResponseChunk) => void
  onError: (error: Error) => void
  onComplete: () => void
}

export function useSSE(url: string, options: UseSSEOptions) {
  const abortController = ref<AbortController | null>(null)

  async function start(payload: unknown) {
    // Create abort controller for cancellation
    abortController.value = new AbortController()

    try {
      // Fetch with streaming response
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: abortController.value.signal
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Request failed')
      }

      // Read stream
      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('Response body is not readable')
      }

      const decoder = new TextDecoder()

      while (true) {
        const { value, done } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.substring(6)) as SSEResponseChunk
              options.onMessage(data)
            } catch (parseError) {
              console.error('Failed to parse SSE message:', parseError)
            }
          }
        }
      }

      options.onComplete()
    } catch (error) {
      if (error instanceof Error && error.name !== 'AbortError') {
        options.onError(error)
      }
    }
  }

  function stop() {
    abortController.value?.abort()
  }

  return { start, stop }
}
