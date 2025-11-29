// API Request/Response Types

export interface PromptContent {
  video: unknown[]
  text: string
}

export interface PromptMessage {
  role: 'user'
  content: [{ video: unknown[] }, { text: string }]
}

export interface InferenceRequest {
  prompt: PromptMessage[]
  model: string
}

export interface SSEResponseChunk {
  output: {
    choices: Array<{
      message: {
        content: Array<{
          text: string
        }>
      }
    }>
  }
}

export interface ErrorResponse {
  error: string
}
