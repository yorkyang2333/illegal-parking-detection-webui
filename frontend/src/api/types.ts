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

// Authentication Types
export interface User {
  id: number
  username: string
  email: string
  created_at: string
  is_active: boolean
}

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
}

export interface AuthResponse {
  message: string
  user?: User
}

export interface UserResponse {
  user: User
}
