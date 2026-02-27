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
  conversation_id: number
  media_filename?: string
}

// Conversation Types
export interface Conversation {
  id: number
  user_id: number
  title: string
  created_at: string
  updated_at: string
}

export interface ConversationMessage {
  id: number
  conversation_id: number
  role: 'user' | 'assistant'
  content: string
  has_media: boolean
  media_path: string | null
  created_at: string
}

export interface ConversationDetailResponse {
  conversation: Conversation
  messages: ConversationMessage[]
}

export interface SSEResponseChunk {
  status?: string // Custom status like 'uploading_video', 'processing_video'
  text?: string // Custom messages accompanying status
  output?: {
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
  remember_me?: boolean
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
