<template>
  <div class="annotation-player" ref="containerRef">
    <video
      ref="videoRef"
      :src="src"
      class="annotation-player__video"
      @timeupdate="onTimeUpdate"
      @loadedmetadata="onMetadataLoaded"
      controls
    />
    <canvas
      ref="canvasRef"
      class="annotation-player__canvas"
      :width="videoNativeWidth"
      :height="videoNativeHeight"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue'
import { useAgentStore } from '@/stores/useAgentStore'
import type { FrameAnnotation } from '@/stores/useAgentStore'

const props = defineProps<{ src: string }>()

const agentStore = useAgentStore()
const videoRef = ref<HTMLVideoElement>()
const canvasRef = ref<HTMLCanvasElement>()
const containerRef = ref<HTMLDivElement>()
const videoNativeWidth = ref(640)
const videoNativeHeight = ref(360)

function onMetadataLoaded() {
  if (!videoRef.value) return
  videoNativeWidth.value = videoRef.value.videoWidth || 640
  videoNativeHeight.value = videoRef.value.videoHeight || 360
}

function onTimeUpdate() {
  if (!videoRef.value) return
  const fps = agentStore.videoFps || 30
  const frameIndex = Math.round(videoRef.value.currentTime * fps)
  agentStore.currentFrameIndex = frameIndex
  drawAnnotations(frameIndex)
}

function findAnnotation(frameIndex: number): FrameAnnotation | null {
  const annotations = agentStore.frameAnnotations
  if (annotations.has(frameIndex)) return annotations.get(frameIndex)!

  let nearest: FrameAnnotation | null = null
  let minDist = Infinity
  for (const [fi, ann] of annotations) {
    const dist = Math.abs(fi - frameIndex)
    if (dist < minDist && dist <= 5) {
      minDist = dist
      nearest = ann
    }
  }
  return nearest
}

function drawAnnotations(frameIndex: number) {
  const canvas = canvasRef.value
  const video = videoRef.value
  if (!canvas || !video) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  // Scale canvas drawing coordinates to match native video resolution
  const scaleX = videoNativeWidth.value
  const scaleY = videoNativeHeight.value
  ctx.clearRect(0, 0, scaleX, scaleY)

  const annotation = findAnnotation(frameIndex)
  if (!annotation) return

  for (const box of annotation.boxes) {
    const [x1, y1, x2, y2] = box.bbox
    const w = x2 - x1
    const h = y2 - y1
    const color = box.is_violation ? '#ff4444' : '#44ff88'
    const bgColor = box.is_violation ? 'rgba(255,68,68,0.12)' : 'rgba(68,255,136,0.08)'

    // Background fill
    ctx.fillStyle = bgColor
    ctx.fillRect(x1, y1, w, h)

    // Border
    ctx.strokeStyle = color
    ctx.lineWidth = 2
    ctx.strokeRect(x1, y1, w, h)

    // Corner markers (sci-fi style)
    const cl = Math.min(14, w * 0.2, h * 0.2)
    ctx.lineWidth = 3
    ctx.strokeStyle = color
    const corners: [number, number, number, number, number, number][] = [
      [x1, y1 + cl, x1, y1, x1 + cl, y1],
      [x2 - cl, y1, x2, y1, x2, y1 + cl],
      [x1, y2 - cl, x1, y2, x1 + cl, y2],
      [x2 - cl, y2, x2, y2, x2, y2 - cl],
    ]
    for (const [ax, ay, mx, my, bx, by] of corners) {
      ctx.beginPath()
      ctx.moveTo(ax, ay)
      ctx.lineTo(mx, my)
      ctx.lineTo(bx, by)
      ctx.stroke()
    }

    // Label
    const labelText = box.label
    ctx.font = 'bold 12px "JetBrains Mono", "Courier New", monospace'
    const textW = ctx.measureText(labelText).width
    ctx.fillStyle = color
    ctx.fillRect(x1, y1 - 22, textW + 10, 20)
    ctx.fillStyle = '#000'
    ctx.fillText(labelText, x1 + 5, y1 - 6)

    // Confidence bar
    const barW = w * Math.min(box.confidence, 1)
    ctx.fillStyle = color
    ctx.fillRect(x1, y2 + 2, barW, 3)
  }
}

// Redraw when annotation data updates
watch(
  () => agentStore.frameAnnotations.size,
  () => {
    if (videoRef.value) {
      const fps = agentStore.videoFps || 30
      drawAnnotations(Math.round(videoRef.value.currentTime * fps))
    }
  }
)

onUnmounted(() => {
  const canvas = canvasRef.value
  if (canvas) {
    const ctx = canvas.getContext('2d')
    ctx?.clearRect(0, 0, canvas.width, canvas.height)
  }
})
</script>

<style scoped lang="scss">
.annotation-player {
  position: relative;
  background: #000;
  border-radius: var(--radius-lg);
  overflow: hidden;
  aspect-ratio: 16 / 9;

  &__video {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: contain;
    display: block;
  }

  &__canvas {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
  }
}
</style>
