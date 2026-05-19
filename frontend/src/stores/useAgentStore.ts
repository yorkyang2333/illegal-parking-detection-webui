import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useSSE } from '@/composables/useSSE'
import { useRouter } from 'vue-router'

export interface AgentPhase {
  id: number
  label: string
  status: 'pending' | 'running' | 'done' | 'error'
}

export interface ThoughtEntry {
  id: number
  content: string
  type: 'thought' | 'tool_call' | 'tool_result'
  tool?: string
  timestamp: number
}

export interface BoundingBox {
  track_id: number
  bbox: [number, number, number, number]
  label: string
  is_violation: boolean
  confidence: number
}

export interface FrameAnnotation {
  frame_index: number
  timestamp_sec: number
  fps?: number
  boxes: BoundingBox[]
}

export interface ViolationRecord {
  track_id: number
  license_plate: string
  vehicle_class: string
  violation_reason: string
  stationary_duration_sec: number
  best_frame_index: number
  bbox: [number, number, number, number]
  scene_context?: string
}

export const useAgentStore = defineStore('agent', () => {
  const router = useRouter()

  let _videoEl: HTMLVideoElement | null = null

  // 视频状态
  const videoFile = ref<File | null>(null)
  const videoPreviewUrl = ref<string | null>(null)
  const uploadedFilename = ref('')
  const isProcessing = ref(false)
  const isCompleted = ref(false)

  // Agent 阶段
  const phases = ref<AgentPhase[]>([
    { id: 0, label: '视频探针', status: 'pending' },
    { id: 1, label: '车辆追踪', status: 'pending' },
    { id: 2, label: 'Agent 分析', status: 'pending' },
    { id: 3, label: '报告生成', status: 'pending' },
  ])

  // 思考链
  const thoughts = ref<ThoughtEntry[]>([])
  let thoughtCounter = 0

  // 帧标注：Map<frame_index, FrameAnnotation>
  const frameAnnotations = ref<Map<number, FrameAnnotation>>(new Map())

  // 视频 FPS（从第一个 frame_annotation 事件中获取）
  const videoFps = ref(30)

  // 最终结果
  const violations = ref<ViolationRecord[]>([])
  const finalReport = ref('')

  // 当前帧索引（由 VideoAnnotationCanvas 写入）
  const currentFrameIndex = ref(0)

  const currentAnnotation = computed(() => {
    const exact = frameAnnotations.value.get(currentFrameIndex.value)
    if (exact) return exact

    // ±5 帧容差查找最近的标注
    let nearest: FrameAnnotation | null = null
    let minDist = Infinity
    for (const [fi, ann] of frameAnnotations.value) {
      const dist = Math.abs(fi - currentFrameIndex.value)
      if (dist < minDist && dist <= 5) {
        minDist = dist
        nearest = ann
      }
    }
    return nearest
  })

  const hasVideo = computed(() => videoFile.value !== null)

  function _handleSSEMessage(raw: unknown) {
    const event = raw as Record<string, unknown>
    switch (event.type) {
      case 'phase': {
        const phase = phases.value.find(p => p.id === event.phase)
        if (phase) {
          phase.status = event.status === 'start' ? 'running' : 'done'
        }
        break
      }
      case 'thought':
        thoughts.value.push({
          id: thoughtCounter++,
          content: event.content as string,
          type: 'thought',
          timestamp: Date.now(),
        })
        break
      case 'tool_call':
        thoughts.value.push({
          id: thoughtCounter++,
          content: `调用工具 ${event.tool}`,
          type: 'tool_call',
          tool: event.tool as string,
          timestamp: Date.now(),
        })
        break
      case 'tool_result':
        thoughts.value.push({
          id: thoughtCounter++,
          content: event.summary as string,
          type: 'tool_result',
          tool: event.tool as string,
          timestamp: Date.now(),
        })
        break
      case 'frame_annotation': {
        const ann = event.data as FrameAnnotation
        if (ann.fps && ann.fps !== videoFps.value) {
          videoFps.value = ann.fps
        }
        const existing = frameAnnotations.value.get(ann.frame_index)
        if (existing) {
          const existingIds = new Set(existing.boxes.map(b => b.track_id))
          for (const box of ann.boxes) {
            const idx = existing.boxes.findIndex(b => b.track_id === box.track_id)
            if (idx >= 0) {
              existing.boxes[idx] = box
            } else if (!existingIds.has(box.track_id)) {
              existing.boxes.push(box)
            }
          }
        } else {
          frameAnnotations.value.set(ann.frame_index, ann)
        }
        break
      }
      case 'final_report':
        violations.value = event.violations as ViolationRecord[]
        finalReport.value = event.markdown as string
        isCompleted.value = true
        isProcessing.value = false
        break
      case 'error':
        thoughts.value.push({
          id: thoughtCounter++,
          content: `错误：${event.message}`,
          type: 'thought',
          timestamp: Date.now(),
        })
        isProcessing.value = false
        break
    }
  }

  const agentSSE = useSSE('/api/analyze/agent', {
    onMessage: _handleSSEMessage,
    onError: (err: unknown) => {
      const e = err as { status?: number }
      if (e.status === 401) {
        router.push('/login')
      }
      isProcessing.value = false
    },
    onComplete: () => {
      isProcessing.value = false
    },
  })

  function setVideoFile(file: File) {
    videoFile.value = file
    if (videoPreviewUrl.value) URL.revokeObjectURL(videoPreviewUrl.value)
    videoPreviewUrl.value = URL.createObjectURL(file)
  }

  function clearVideoFile() {
    videoFile.value = null
    if (videoPreviewUrl.value) {
      URL.revokeObjectURL(videoPreviewUrl.value)
      videoPreviewUrl.value = null
    }
    uploadedFilename.value = ''
  }

  async function uploadVideo(): Promise<boolean> {
    if (!videoFile.value) return false
    const formData = new FormData()
    formData.append('video', videoFile.value)
    try {
      const resp = await fetch('/api/upload-media', {
        method: 'POST',
        body: formData,
        credentials: 'include',
      })
      if (!resp.ok) return false
      const data = await resp.json()
      uploadedFilename.value = data.filename
      return true
    } catch {
      return false
    }
  }

  async function startAgentAnalysis() {
    if (!videoFile.value) return

    // 重置状态
    isProcessing.value = true
    isCompleted.value = false
    thoughts.value = []
    frameAnnotations.value = new Map()
    violations.value = []
    finalReport.value = ''
    videoFps.value = 30
    phases.value.forEach(p => (p.status = 'pending'))

    if (!uploadedFilename.value) {
      const ok = await uploadVideo()
      if (!ok) {
        isProcessing.value = false
        return
      }
    }

    agentSSE.start({ video: uploadedFilename.value })
  }

  function stopAnalysis() {
    agentSSE.stop()
    isProcessing.value = false
  }

  function resetAnalysis() {
    stopAnalysis()
    clearVideoFile()
    thoughts.value = []
    frameAnnotations.value = new Map()
    violations.value = []
    finalReport.value = ''
    isCompleted.value = false
    uploadedFilename.value = ''
    phases.value.forEach(p => (p.status = 'pending'))
  }

  function registerVideoRef(el: HTMLVideoElement | null) {
    _videoEl = el
  }

  function jumpToFrame(frameIndex: number) {
    if (!_videoEl) return
    const fps = videoFps.value || 30
    _videoEl.currentTime = frameIndex / fps
  }

  return {
    videoFile,
    videoPreviewUrl,
    uploadedFilename,
    isProcessing,
    isCompleted,
    phases,
    thoughts,
    frameAnnotations,
    videoFps,
    violations,
    finalReport,
    currentFrameIndex,
    currentAnnotation,
    hasVideo,
    setVideoFile,
    clearVideoFile,
    startAgentAnalysis,
    stopAnalysis,
    resetAnalysis,
    registerVideoRef,
    jumpToFrame,
  }
})
