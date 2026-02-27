<template>
  <div class="prts-log-entry" :class="[message.role, { streaming: message.isStreaming }]">
    <div class="log-header">
      <span class="log-role">{{ message.role === 'user' ? 'OPERATOR_INPUT' : 'PRTS_ANALYSIS' }}</span>
      <span class="log-time">[{{ formatTime(message.timestamp) }}]</span>
    </div>
    
    <!-- User Input -->
    <div v-if="message.role === 'user'" class="log-body prts-output">
      <div class="text-content">
        <span>> </span>{{ message.content }}
      </div>
    </div>

    <!-- AI Output -->
    <div v-else class="log-body prts-output">
      <div v-if="message.isStreaming && !message.content" class="typing-indicator">
        <span class="processing-text">PROCESSING_DATA...</span>
      </div>
      
      <!-- Structured PRTS Card -->
      <div v-else-if="hasStructuredData" class="prts-card-grid">
        <div class="card-row split">
          <div class="data-block">
            <div class="data-label">LICENSE_PLATE</div>
            <div class="data-value highlight">{{ parsedData.license_plate || 'SCANNING...' }}</div>
          </div>
          <div class="data-block">
            <div class="data-label">VEHICLE_COLOR</div>
            <div class="data-value">{{ parsedData.vehicle_color || '---' }}</div>
          </div>
        </div>
        
        <div class="card-row split">
          <div class="data-block">
            <div class="data-label">VIOLATION_TYPE</div>
            <div class="data-value warning">{{ parsedData.violation_type || 'ANALYZING...' }}</div>
          </div>
          <div class="data-block">
            <div class="data-label">INCIDENT_TIMESTAMP</div>
            <div class="data-value">{{ parsedData.timestamp || '---' }}</div>
          </div>
        </div>
        
        <div class="card-row full">
          <div class="data-block">
            <div class="data-label">TACTICAL_ANALYSIS</div>
            <div class="data-value log-text">{{ parsedData.analysis || 'AWAITING_CORE_DUMP...' }}</div>
          </div>
        </div>
        
        <div class="card-row full">
          <div class="data-block penalty-block">
            <div class="data-label">RECOMMENDED_PENALTY</div>
            <div class="data-value alert">{{ parsedData.suggested_penalty || 'PENDING...' }}</div>
          </div>
        </div>
        
        <!-- Raw JSON debug collapse or residual text -->
        <details class="raw-data-toggle" v-if="parsedData.raw">
          <summary>VIEW_RAW_STREAM</summary>
          <pre>{{ message.content }}</pre>
        </details>
      </div>
      
      <!-- Fallback to Markdown/Text if not JSON -->
      <div v-else class="markdown-content" @click="handleMarkdownClick">
        <MarkdownViewer :content="parseTimestamps(message.content)" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { User } from '@element-plus/icons-vue'
import MarkdownViewer from '@/components/common/MarkdownViewer.vue'
import type { ChatMessage } from '@/stores/useChatStore'

const props = defineProps<{
  message: ChatMessage
}>()

const emit = defineEmits<{
  'seek-video': [seconds: number]
}>()

// Robust streamed JSON extractor
const parsedData = computed(() => {
  if (props.message.role !== 'assistant') return {}
  const content = props.message.content
  if (!content.includes('{') && !content.includes('license_plate')) return {}

  const extract = (key: string) => {
    // Matches "key": "value" or "key":"value" with potential escaped quotes
    const regex = new RegExp(`"${key}"\\s*:\\s*"([^"]*)"?`)
    const match = content.match(regex)
    return match ? match[1].replace(/\\"/g, '"').replace(/\\n/g, '\n') : ''
  }

  // Check if we have at least one of our target keys to activate structured mode
  const license_plate = extract('license_plate')
  const vehicle_color = extract('vehicle_color')
  const violation_type = extract('violation_type')
  const timestamp = extract('timestamp')
  const analysis = extract('analysis')
  const suggested_penalty = extract('suggested_penalty')

  const hasAnyKey = license_plate || vehicle_color || violation_type || timestamp || analysis || suggested_penalty

  if (hasAnyKey) {
    return {
      license_plate,
      vehicle_color,
      violation_type,
      timestamp,
      analysis,
      suggested_penalty,
      raw: true
    }
  }

  return {}
})

const hasStructuredData = computed(() => Object.keys(parsedData.value).length > 0)

function formatTime(date: Date): string {
  const d = new Date(date)
  const hours = d.getHours().toString().padStart(2, '0')
  const minutes = d.getMinutes().toString().padStart(2, '0')
  return `${hours}:${minutes}`
}

// Convert [MM:SS] to clickable links in HTML
function parseTimestamps(text: string): string {
  if (!text) return text
  // Match formats like [10:30]
  const timeRegex = /\[(\d{1,2}):(\d{2})\]/g
  return text.replace(timeRegex, (match, m, s) => {
    const totalSeconds = parseInt(m, 10) * 60 + parseInt(s, 10)
    return `<a href="#" class="video-timestamp" data-seek="${totalSeconds}">${match}</a>`
  })
}

// Delegate event pattern for HTML generated inside Markdown
function handleMarkdownClick(event: MouseEvent) {
  const target = event.target as HTMLElement
  if (target && target.classList.contains('video-timestamp')) {
    event.preventDefault()
    const seekStr = target.getAttribute('data-seek')
    if (seekStr) {
      emit('seek-video', parseInt(seekStr, 10))
    }
  }
}
</script>

<style scoped lang="scss">
.prts-log-entry {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px;
  margin-bottom: 8px;
  border-left: 4px solid transparent;
  background: white;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  animation: fadeIn 0.3s ease;

  &.user {
    border-left-color: var(--ef-border-light);
    background: #fdfdfd;

    .log-role {
      color: var(--ef-text-dim);
    }
  }

  &.assistant {
    border-left-color: var(--ef-accent);
    background: #f0f9ff;

    .log-role {
      color: var(--ef-accent-hover);
      font-weight: 900;
    }
  }

  &.streaming {
    border-left-color: var(--ef-warning);
    background: #fffdf0;
  }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}

.log-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 6px;
  border-bottom: 1px dashed var(--ef-border-light);
  padding-bottom: 4px;
}

.log-role {
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: bold;
  letter-spacing: 2px;
  color: var(--ef-accent);
  text-shadow: 0 0 8px rgba(0, 240, 255, 0.4);
}

.log-time {
  font-size: 11px;
  color: var(--ef-text-dim);
  font-family: var(--font-mono);
}

.log-body {
  line-height: 1.6;
  font-size: 14px;
  font-family: var(--font-tech);
  font-weight: 500;
  word-break: break-word;
  color: var(--ef-text);
  text-shadow: 0 0 2px rgba(224, 250, 255, 0.2);
}

.text-content {
  white-space: pre-wrap;
}

.markdown-content {
  :deep(p) { margin: 0 0 0.8em; }
  
  /* Dynamic Timestamp Link Styles */
  :deep(.video-timestamp) {
    display: inline-block;
    background: var(--ef-accent);
    color: white !important;
    padding: 0 4px;
    border-radius: 2px;
    font-family: monospace;
    font-size: 0.9em;
    font-weight: bold;
    text-decoration: none;
    cursor: pointer;
    transition: all 0.2s;
    
    &:hover {
      background: var(--ef-accent-hover);
    }
  }

  :deep(code) {
    background: rgba(0, 0, 0, 0.05);
    border: 1px solid var(--ef-border-light);
    padding: 2px 4px;
    font-family: monospace;
    color: var(--ef-warning);
  }

  :deep(pre) {
    background: #f4f4f4;
    border: 1px solid var(--ef-border-light);
    border-left: 3px solid var(--ef-accent);
    color: var(--ef-text);
    padding: 12px;
    overflow-x: auto;
    margin: 0.8em 0;
  }

  :deep(blockquote) {
    border-left: 3px solid var(--ef-warning);
    padding-left: 12px;
    background: #fff8eb;
    margin: 0.8em 0;
    color: var(--ef-text-dim);
    font-style: italic;
  }
}

.typing-indicator {
  padding: 4px 0;
  .processing-text {
    font-family: monospace;
    font-size: 12px;
    color: var(--ef-warning);
    animation: flash 1s infinite alternate;
  }
}

@keyframes flash {
  from { opacity: 0.4; }
  to { opacity: 1; }
}

@media (max-width: 768px) {
  .prts-log-entry {
    padding: 10px;
  }
}

/* ---------------- PRTS Animations ---------------- */
@keyframes prtsGlitch {
  0% {
    clip-path: polygon(0 2%, 100% 2%, 100% 5%, 0 5%);
    transform: translate(-2px, 2px);
  }
  20% {
    clip-path: polygon(0 15%, 100% 15%, 100% 15%, 0 15%);
    transform: translate(2px, -2px);
  }
  40% {
    clip-path: polygon(0 10%, 100% 10%, 100% 20%, 0 20%);
    transform: translate(-2px, 2px);
  }
  60% {
    clip-path: polygon(0 1%, 100% 1%, 100% 2%, 0 2%);
    transform: translate(2px, -2px);
  }
  80% {
    clip-path: polygon(0 33%, 100% 33%, 100% 33%, 0 33%);
    transform: translate(-2px, 2px);
  }
  100% {
    clip-path: polygon(0 44%, 100% 44%, 100% 44%, 0 44%);
    transform: translate(2px, -2px);
  }
}

.glitch-effect {
  position: relative;
  animation: glitch-anim 0.4s cubic-bezier(.25, .46, .45, .94) both;
}

@keyframes glitch-anim {
  0% { opacity: 0; transform: skewX(-5deg) translateY(-5px); }
  50% { opacity: 1; transform: skewX(5deg) translateY(0); filter: hue-rotate(90deg); }
  100% { opacity: 1; transform: skewX(0) translateY(0); filter: hue-rotate(0); }
}
/* Structured Data Card */
.prts-card-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: rgba(0, 240, 255, 0.03);
  border: 1px solid var(--ef-border-light);
  padding: 12px;
  margin-top: 8px;
  clip-path: polygon(
    0 0, 
    calc(100% - 15px) 0, 
    100% 15px, 
    100% 100%, 
    15px 100%, 
    0 calc(100% - 15px)
  );
  box-shadow: inset 0 0 20px rgba(0, 240, 255, 0.05);
  position: relative;
  /* Add glitch on spawn */
  animation: glitch-anim 0.3s cubic-bezier(0.25, 1, 0.5, 1) both;
  
  &::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 2px; height: 30px;
    background: var(--ef-accent);
    box-shadow: 0 0 10px var(--ef-accent);
  }
}

.card-row {
  display: flex;
  gap: 8px;
  
  &.split > .data-block {
    flex: 1;
  }
  
  &.full > .data-block {
    flex: 1;
    width: 100%;
  }
}

.data-block {
  background: rgba(10, 15, 20, 0.8);
  border: 1px solid var(--ef-border-light);
  padding: 8px 12px;
  position: relative;
  transition: all 0.2s ease;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 2px;
    height: 100%;
    background: var(--ef-border-light);
  }

  &:hover {
    background: rgba(0, 240, 255, 0.1);
    border-color: var(--ef-border);
    box-shadow: 0 0 15px rgba(0, 240, 255, 0.2);
    
    &::before {
      background: var(--ef-accent);
      box-shadow: 0 0 8px var(--ef-accent);
    }
  }
}

.penalty-block {
  background: rgba(255, 215, 0, 0.05);
  border-color: rgba(255, 215, 0, 0.3);
  &::before {
    background: var(--ef-warning);
  }
  &:hover {
    background: rgba(255, 215, 0, 0.15);
    border-color: var(--ef-warning);
    box-shadow: 0 0 15px rgba(255, 215, 0, 0.3);
  }
}

.data-label {
  font-family: var(--font-display);
  font-size: 11px;
  color: var(--ef-text-dim);
  margin-bottom: 4px;
  letter-spacing: 1.5px;
}

.data-value {
  font-family: var(--font-mono);
  font-size: 15px;
  font-weight: bold;
  color: var(--ef-text);
  
  &.highlight {
    color: var(--ef-accent);
    text-shadow: 0 0 8px rgba(0, 240, 255, 0.5);
  }
  
  &.warning {
    color: var(--ef-warning);
    text-shadow: 0 0 8px rgba(255, 215, 0, 0.5);
  }
  
  &.alert {
    color: var(--ef-danger);
    text-shadow: 0 0 8px rgba(255, 42, 42, 0.6);
  }
  
  &.log-text {
    font-weight: normal;
    font-family: var(--font-tech);
    white-space: pre-wrap;
    line-height: 1.6;
    letter-spacing: 0.5px;
  }
}

.raw-data-toggle {
  margin-top: 8px;
  cursor: pointer;
  
  summary {
    font-family: monospace;
    font-size: 11px;
    color: var(--ef-text-dim);
    outline: none;
    
    &:hover {
      color: var(--ef-accent);
    }
  }
  
  pre {
    margin-top: 8px;
    background: rgba(0, 0, 0, 0.5);
    padding: 8px;
    font-size: 11px;
    border: 1px solid var(--ef-border-light);
    overflow-x: auto;
    color: var(--ef-accent);
  }
}
</style>
