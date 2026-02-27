<template>
  <AppLayout>
    <div class="dashboard-page prts-theme">
      
      <!-- 左侧：数据链入与历史 (Data Uplink & Archives) -->
      <aside class="uplink-sidebar prts-panel">
        <div class="panel-decor-top-left"></div>
        <div class="panel-decor-bottom-right"></div>
        <div class="panel-header">
          <span class="panel-title">PRTS_UPLINK <span class="blink-cursor">_</span></span>
          <button class="new-session-btn" @click="handleNewChat">
            <el-icon><Plus /></el-icon> NEW_SESSION
          </button>
        </div>
        
        <div class="history-list">
          <div class="section-label">
            <span class="label-text">ARCHIVED_SESSIONS</span>
            <span class="label-hex">0x8F22</span>
          </div>
          <div 
            v-for="conv in chatStore.conversations" 
            :key="conv.id"
            class="history-item"
            :class="{ 'active': chatStore.activeConversationId === conv.id }"
            @click="handleSelectConversation(conv.id)"
          >
            <el-icon><Document /></el-icon>
            <div class="history-info">
              <span class="history-title">{{ conv.title }}</span>
              <span class="history-meta">ID:{{ conv.id.toString().padStart(4, '0') }}</span>
            </div>
          </div>
        </div>
        
        <div class="panel-footer-decor">
          <div class="barcode"></div>
          <div class="sys-sig">RHODES_ISLAND // PRTS</div>
        </div>
      </aside>

      <!-- 中间：核心监控区 (Core Monitor Area) -->
      <main class="monitor-main prts-panel">
        <div class="panel-decor-top-left"></div>
        <div class="panel-decor-bottom-right"></div>
        <div class="panel-header monitor-header">
          <div class="telemetry">
            <span>SYS.VER: 9.22.4</span>
            <span>MEM: 48%</span>
          </div>
          <span class="panel-title main-title">MAIN_SENSOR_FEED // NODE_01</span>
        </div>
        <div class="video-container">
          <div class="scanner-sweep"></div>
          
          <!-- Camera HUD Overlays -->
          <div class="hud-corners">
            <div class="corner tl"></div>
            <div class="corner tr"></div>
            <div class="corner bl"></div>
            <div class="corner br"></div>
          </div>
          <div class="hud-rec blink-cursor">
            <span class="rec-dot"></span> REC
          </div>
          <div class="hud-crosshair">
            <div class="ch-h"></div>
            <div class="ch-v"></div>
          </div>

          <div class="video-placeholder" v-if="!latestMediaUrl">
            <el-icon><VideoCamera /></el-icon>
            <p>NO_SIGNAL</p>
            <div class="standby-text">AWAITING SYSTEM UPLINK...</div>
          </div>
          <template v-else>
            <img 
              v-if="isImageMedia"
              class="active-media-player image-feed"
              :src="latestMediaUrl"
              alt="Uplink Image Feed"
            />
            <video 
              v-else
              ref="videoPlayerRef"
              class="active-media-player video-feed"
              :src="latestMediaUrl"
              controls
              preload="metadata"
            ></video>
          </template>
        </div>
        
        <div class="system-status">
           <div class="status-group">
             <span class="label">STREAM_STATE:</span>
             <span class="value" :class="chatStore.isStreaming ? 'generating' : 'standby'">
               {{ chatStore.isStreaming ? 'ANALYZING' : 'STANDBY' }}
             </span>
           </div>
           
           <div class="status-divider"></div>
           
           <div class="status-group">
             <span class="label">CONN_STATUS:</span>
             <span class="value stable">[STABLE-UPLINK]</span>
           </div>
           
           <div class="status-divider"></div>
           
           <div class="status-group">
             <span class="label">LATENCY:</span>
             <span class="value sys-green">14ms</span>
           </div>

           <div v-if="chatStore.uploadedMediaFilename" class="status-group upload-ok ml-auto">
             <span class="label">CACHED_FEED:</span>
             <span class="value">{{ chatStore.uploadedMediaFilename }}</span>
           </div>
        </div>
      </main>

      <!-- 右侧：分析日志与指令输入 (Analysis Log & Command) -->
      <aside class="analysis-sidebar prts-panel">
        <div class="panel-decor-top-left log-decor"></div>
        <div class="panel-decor-bottom-right log-decor"></div>
        <div class="panel-header analysis-header">
          <span class="panel-title main-title">ANALYSIS_LOG // THREAD_02</span>
        </div>
        
        <div class="log-stream" ref="scrollContainer">
          <div v-if="!chatStore.hasMessages" class="system-ready">
            <h2>PRTS_ONLINE</h2>
            <p>Awaiting analysis parameters...</p>
            <div class="quick-commands">
              <button 
                v-for="(prompt, index) in quickPrompts" 
                :key="index"
                @click="handleQuickPrompt(prompt)"
              >
                {{ prompt.title }}
              </button>
            </div>
          </div>

          <div class="messages-list">
            <template v-if="chatStore.hasMessages">
              <AnalysisLog
                v-for="msg in chatStore.messages"
                :key="msg.id"
                :message="msg"
                @seek-video="handleSeekVideo"
              />
            </template>
          </div>
        </div>

        <div class="command-input-area">
          <div v-if="chatStore.error" class="error-banner">
            <el-alert :title="chatStore.error" type="error" :closable="false" />
          </div>

          <!-- Input Area -->
          <CommandTerminal 
            :disabled="chatStore.isStreaming"
            :placeholder="chatStore.isStreaming ? 'AWAITING_PRTS_RESPONSE...' : 'INPUT_PARAMETERS...'"
            @send="handleSend"
            @upload-media="handleMediaUpload"
          />
        </div>
      </aside>

    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onMounted, computed } from 'vue'
import { ChatDotSquare, Plus, Document, VideoCamera } from '@element-plus/icons-vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import AnalysisLog from '@/components/chat/AnalysisLog.vue'
import CommandTerminal from '@/components/chat/CommandTerminal.vue'
import { useChatStore } from '@/stores/useChatStore'

const chatStore = useChatStore()

// DOM Refs
const scrollContainer = ref<HTMLElement | null>(null)
const videoPlayerRef = ref<HTMLVideoElement | null>(null)

// Computed media URL based on the current context
const latestMediaUrl = computed(() => {
  if (chatStore.uploadedMediaFilename) {
    return `/api/uploads/${chatStore.uploadedMediaFilename}`
  }
  return null
})

const isImageMedia = computed(() => {
  const url = latestMediaUrl.value
  if (!url) return false
  const lowerUrl = url.toLowerCase()
  return lowerUrl.endsWith('.jpg') || lowerUrl.endsWith('.jpeg') || lowerUrl.endsWith('.png') || lowerUrl.endsWith('.webp')
})

// Initialize conversations
onMounted(() => {
  chatStore.fetchConversations()
})

const quickPrompts = [
  {
    title: '分析违停报告并替换车牌号',
    content: `现有一段违停的分析报告：\n[粘贴Gemini生成的违停分析报告]\n由QVQ-Max重新识别了车牌号为：\n[粘贴QVQ-Max识别到的车牌号]\n请帮我把QVQ-Max识别到的车牌号替换报告中原先识别到的车牌号，依据且仅依据原报告中的内容，重新生成一份详尽违停报告。\n请依次输出：\n1.违停车辆车牌号\n2.该车辆违停原因\n3.建议处罚`
  },
  {
    title: '生违违停处罚建议',
    content: '请根据《中华人民共和国道路交通安全法》，为校园内违停车辆生成处罚建议。'
  }
]

function handleQuickPrompt(prompt: { title: string; content: string }) {
  chatStore.sendMessage(prompt.content)
}

function handleSend(content: string) {
  chatStore.sendMessage(content)
}

async function handleMediaUpload(file: File) {
  try {
    await chatStore.uploadMedia(file)
  } catch (err) {
    console.error(err)
  }
}

function handleSeekVideo(seconds: number) {
  if (videoPlayerRef.value) {
    videoPlayerRef.value.currentTime = seconds
    videoPlayerRef.value.play()
  }
}

function handleNewChat() {
  chatStore.clearChat()
  chatStore.createNewConversation()
}

function handleSelectConversation(id: number) {
  chatStore.clearChat()
  chatStore.loadConversation(id)
}

// 自动滚动到底部
watch(
  () => chatStore.messages.length,
  () => {
    nextTick(() => {
      scrollToBottom()
    })
  }
)

// 监听流式内容更新
watch(
  () => chatStore.messages[chatStore.messages.length - 1]?.content,
  () => {
    nextTick(() => {
      scrollToBottom()
    })
  }
)

function scrollToBottom() {
  if (scrollContainer.value) {
    scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight
  }
}
</script>

<style scoped lang="scss">
.dashboard-page.prts-theme {
  display: grid;
  /* Adjust proportions: Left Upload/History, Center Video, Right Log */
  grid-template-columns: 300px 1fr 450px;
  gap: 16px;
  height: 100%;
  background: var(--ef-bg-dark);
  padding: 16px;
  box-sizing: border-box;
}

/* Base Panel Styling */
.prts-panel {
  background: var(--ef-panel-bg);
  border: 1px solid var(--ef-border-light);
  display: flex;
  flex-direction: column;
  position: relative;
  box-shadow: 0 0 15px rgba(0, 240, 255, 0.05);
  backdrop-filter: blur(4px);
  
  /* Arknights Angle Cuts */
  clip-path: polygon(
    0 0, 
    calc(100% - 20px) 0, 
    100% 20px, 
    100% 100%, 
    20px 100%, 
    0 calc(100% - 20px)
  );
}

/* Decorative Corner Corners */
.panel-decor-top-left {
  position: absolute;
  top: 0; left: 0;
  width: 30px; height: 30px;
  border-top: 2px solid var(--ef-accent);
  border-left: 2px solid var(--ef-accent);
  pointer-events: none;
  z-index: 10;
}

.panel-decor-bottom-right {
  position: absolute;
  bottom: 0; right: 0;
  width: 30px; height: 30px;
  border-bottom: 2px solid var(--ef-accent);
  border-right: 2px solid var(--ef-accent);
  pointer-events: none;
  z-index: 10;
}

.panel-header {
  padding: 12px 16px;
  border-bottom: 1px solid var(--ef-border-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(0, 240, 255, 0.05);

  .panel-title {
    font-family: var(--font-display);
    font-size: 15px;
    font-weight: 700;
    color: var(--ef-accent);
    text-transform: uppercase;
    letter-spacing: 2px;
    text-shadow: 0 0 8px rgba(0, 240, 255, 0.4);
  }
}

.blink-cursor {
  animation: blink 1s step-end infinite;
}

@keyframes blink {
  50% { opacity: 0; }
}

.monitor-header {
  background: rgba(255, 215, 0, 0.05); /* Amber background for central monitor */
  border-bottom-color: rgba(255, 215, 0, 0.3);
  
  .telemetry {
    font-family: var(--font-mono);
    font-size: 10px;
    color: var(--ef-text-dim);
    display: flex;
    gap: 12px;
  }
  
  .main-title {
    color: var(--ef-warning); /* Amber title */
    text-shadow: 0 0 8px rgba(255, 215, 0, 0.4);
  }
}

.analysis-header {
  background: rgba(255, 42, 42, 0.05); /* Red/Danger background for analysis thread */
  border-bottom-color: rgba(255, 42, 42, 0.3);
  
  .main-title {
    color: var(--ef-danger); /* Red title */
    text-shadow: 0 0 8px rgba(255, 42, 42, 0.4);
  }
}

.log-decor.panel-decor-top-left {
  border-color: var(--ef-danger);
}
.log-decor.panel-decor-bottom-right {
  border-color: var(--ef-danger);
}

/* ---------------- Left Sidebar ---------------- */
.panel-footer-decor {
  padding: 12px 16px;
  border-top: 1px solid var(--ef-border-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(0, 0, 0, 0.2);
  
  .barcode {
    width: 60px;
    height: 15px;
    background: repeating-linear-gradient(
      90deg,
      var(--ef-text-dim),
      var(--ef-text-dim) 2px,
      transparent 2px,
      transparent 4px,
      var(--ef-text-dim) 4px,
      var(--ef-text-dim) 5px,
      transparent 5px,
      transparent 8px
    );
    opacity: 0.5;
  }
  
  .sys-sig {
    font-family: var(--font-display);
    font-size: 10px;
    color: var(--ef-text-dim);
    letter-spacing: 1px;
  }
}

.new-session-btn {
  background: transparent;
  border: 1px solid var(--ef-accent);
  color: var(--ef-accent);
  border-radius: 0;
  padding: 4px 12px;
  font-size: 11px;
  font-family: var(--font-display);
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: inset 0 0 0 0 var(--ef-accent);

  &:hover {
    color: var(--ef-bg-dark);
    box-shadow: inset 100px 0 0 0 var(--ef-accent);
  }
}

.section-label {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  font-family: var(--font-display);
  font-size: 11px;
  font-weight: bold;
  color: var(--ef-text-dim);
  margin-bottom: 8px;
  padding: 0 4px;
  border-bottom: 1px solid rgba(0, 240, 255, 0.2);
  padding-bottom: 4px;
  
  .label-hex {
    font-family: var(--font-mono);
    font-size: 9px;
    opacity: 0.5;
  }
}

.history-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;

  .history-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 12px;
    margin-bottom: 6px;
    color: var(--ef-text);
    cursor: pointer;
    border: 1px solid transparent;
    transition: all 0.2s;
    font-size: 13px;
    background: rgba(0, 240, 255, 0.02);

    &:hover {
      background: rgba(0, 240, 255, 0.08);
      border-color: var(--ef-accent);
      box-shadow: 0 0 8px rgba(0, 240, 255, 0.2);
    }
    
    &.active {
      background: rgba(0, 240, 255, 0.15);
      border-color: var(--ef-accent);
      color: var(--ef-text);
      border-left: 4px solid var(--ef-accent);
      font-weight: bold;
      box-shadow: 0 0 10px rgba(0, 240, 255, 0.3);
    }

    .history-info {
      display: flex;
      flex-direction: column;
      overflow: hidden;
      
      .history-title {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        font-family: var(--font-tech);
        font-size: 13px;
        letter-spacing: 0.5px;
      }
      
      .history-meta {
        font-family: var(--font-mono);
        font-size: 9px;
        color: var(--ef-text-dim);
        margin-top: 2px;
      }
    }
  }
}

/* ---------------- Center Monitor ---------------- */
.video-container {
  flex: 1;
  background: #020305;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  border-bottom: 1px solid var(--ef-border-light);

  /* Inner glowing grid */
  background-image: 
    linear-gradient(rgba(0, 240, 255, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 240, 255, 0.05) 1px, transparent 1px);
  background-size: 40px 40px;
}

/* ---------------- Camera HUD Overlays ---------------- */
.hud-corners {
  position: absolute;
  top: 20px; left: 20px; right: 20px; bottom: 20px;
  pointer-events: none;
  z-index: 10;
  
  .corner {
    position: absolute;
    width: 30px; height: 30px;
    border: 2px solid rgba(0, 240, 255, 0.4);
    
    &.tl { top: 0; left: 0; border-right: none; border-bottom: none; }
    &.tr { top: 0; right: 0; border-left: none; border-bottom: none; }
    &.bl { bottom: 0; left: 0; border-right: none; border-top: none; }
    &.br { bottom: 0; right: 0; border-left: none; border-top: none; }
  }
}

.hud-rec {
  position: absolute;
  top: 30px;
  right: 40px;
  font-family: var(--font-display);
  color: var(--ef-text-dim);
  font-size: 14px;
  font-weight: bold;
  letter-spacing: 2px;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
  
  &.active {
    color: var(--ef-danger);
    text-shadow: 0 0 8px rgba(255, 42, 42, 0.5);
    
    .rec-dot {
      background: var(--ef-danger);
      box-shadow: 0 0 10px var(--ef-danger);
    }
  }

  .rec-dot {
    width: 10px;
    height: 10px;
    background: var(--ef-text-dim);
    border-radius: 50%;
    transition: all 0.3s;
  }
}

.hud-crosshair {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  width: 40px; height: 40px;
  pointer-events: none;
  z-index: 10;
  opacity: 0.2;
  
  .ch-h {
    position: absolute;
    top: 50%; left: 0; right: 0;
    height: 1px;
    background: var(--ef-accent);
  }
  .ch-v {
    position: absolute;
    top: 0; bottom: 0; left: 50%;
    width: 1px;
    background: var(--ef-accent);
  }
}

.scanner-sweep {
  position: absolute;
  top: -100%;
  left: 0;
  width: 100%;
  height: 20%;
  background: linear-gradient(to bottom, transparent, rgba(0, 240, 255, 0.15), transparent);
  animation: sweep 4s infinite linear;
  pointer-events: none;
  z-index: 5;
}

@keyframes sweep {
  0% { top: -20%; }
  100% { top: 120%; }
}

.video-placeholder {
  color: var(--ef-text-dim);
  display: flex;
  flex-direction: column;
  align-items: center;
  font-family: var(--font-display);
  font-size: 16px;
  letter-spacing: 4px;
  text-shadow: 0 0 10px rgba(0, 240, 255, 0.2);
  z-index: 2;
  
  .el-icon {
    font-size: 64px;
    margin-bottom: 20px;
    opacity: 0.8;
    animation: pulse 2s infinite alternate;
  }
  
  .standby-text {
    margin-top: 12px;
    font-family: var(--font-mono);
    font-size: 10px;
    letter-spacing: 2px;
    color: var(--ef-text-dim);
    animation: blink 2s step-end infinite;
  }
}

.active-media-player {
  width: 100%;
  height: 100%;
  object-fit: contain;

  &.image-feed {
    border: 1px solid var(--ef-border);
  }
}

.system-status {
  padding: 12px 16px;
  display: flex;
  gap: 24px;
  background: rgba(10, 15, 20, 0.95);
  font-family: var(--font-mono);
  font-size: 12px;
  border-top: 1px solid var(--ef-border-light);

  .status-divider {
    width: 2px;
    height: 12px;
    background: var(--ef-accent);
    opacity: 0.3;
  }

  .ml-auto {
    margin-left: auto;
  }

  .sys-green {
    color: #00ff88 !important;
    text-shadow: 0 0 5px rgba(0, 255, 136, 0.5);
  }

  .status-group {
    display: flex;
    align-items: center;
    gap: 8px;

    .label {
      color: var(--ef-text-dim);
      font-weight: bold;
    }
    .value {
      font-weight: bold;
      color: var(--ef-text);

      &.generating {
        color: var(--ef-warning);
        animation: pulse 1s infinite alternate;
      }
      &.stable {
        color: var(--ef-accent);
      }
    }
  }
}

/* ---------------- Right Log ---------------- */
.log-stream {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: rgba(0, 0, 0, 0.2);
}

.system-ready {
  text-align: center;
  padding: 40px 20px;
  color: var(--ef-text-dim);
  
  h2 {
    color: var(--ef-text);
    font-size: 20px;
    margin-bottom: 8px;
    letter-spacing: 1px;
  }

  p {
    font-size: 13px;
    margin-bottom: 24px;
  }

  .quick-commands {
    display: flex;
    flex-direction: column;
    gap: 12px;

    button {
      padding: 12px;
      background: transparent;
      border: 1px solid var(--ef-border-light);
      color: var(--ef-text);
      cursor: pointer;
      font-size: 13px;
      transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
      position: relative;
      overflow: hidden;
      font-family: var(--font-tech);
      clip-path: polygon(10px 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) 100%, 0 100%, 0 10px);

      &::before {
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 100%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(0, 240, 255, 0.2), transparent);
        transition: left 0.5s;
      }

      &:hover {
        border-color: var(--ef-accent);
        color: var(--ef-bg-dark);
        background: var(--ef-accent);
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.5);

        &::before {
          left: 100%;
        }
      }
    }
  }
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.command-input-area {
  border-top: 1px solid var(--ef-border-light);
  padding: 16px;
  background: rgba(10, 15, 20, 0.95);
  position: relative;
}

.error-banner {
  margin-bottom: 12px;
}

@keyframes pulse {
  0% { opacity: 0.6; }
  100% { opacity: 1; }
}

@media (max-width: 1200px) {
  .dashboard-page.prts-theme {
    grid-template-columns: 260px 1fr;
    grid-template-rows: 1fr auto;
  }
  .uplink-sidebar {
    grid-column: 1;
  }
  .monitor-main {
    grid-column: 2;
  }
  .analysis-sidebar {
    grid-column: 1 / -1;
    grid-row: 2;
    height: 400px; /* fixed height for bottom panel */
  }
}
</style>
