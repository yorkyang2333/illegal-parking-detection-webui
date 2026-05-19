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
  status?: string
  text?: string
  sam3_data?: Record<string, unknown>
  error?: string
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

// Agent SSE Event Types
export type AgentSSEEvent =
  | { type: 'phase'; phase: number; label: string; status: 'start' | 'done' }
  | { type: 'thought'; content: string }
  | { type: 'tool_call'; tool: string; args: Record<string, unknown> }
  | { type: 'tool_result'; tool: string; summary: string }
  | { type: 'frame_annotation'; data: AgentFrameAnnotation }
  | { type: 'final_report'; violations: AgentViolationRecord[]; markdown: string }
  | { type: 'error'; message: string }

export interface AgentFrameAnnotation {
  frame_index: number
  timestamp_sec: number
  fps?: number
  boxes: AgentBoundingBox[]
}

export interface AgentBoundingBox {
  track_id: number
  bbox: [number, number, number, number]
  label: string
  is_violation: boolean
  confidence: number
}

export interface AgentViolationRecord {
  track_id: number
  license_plate: string
  vehicle_class: string
  violation_reason: string
  stationary_duration_sec: number
  best_frame_index: number
  bbox: [number, number, number, number]
  scene_context?: string
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

