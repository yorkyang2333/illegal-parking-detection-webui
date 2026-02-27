<template>
  <AppLayout>
    <div class="dashboard-page prts-theme">
      
      <!-- 左侧：数据链入与历史 (Data Uplink & Archives) -->
      <aside class="uplink-sidebar prts-panel">
        <div class="panel-header">
          <span class="panel-title">PRTS_UPLINK</span>
          <button class="new-session-btn" @click="handleNewChat">
            <el-icon><Plus /></el-icon> NEW_SESSION
          </button>
        </div>
        
        <div class="history-list">
          <div class="section-label">ARCHIVED_SESSIONS</div>
          <div 
            v-for="conv in chatStore.conversations" 
            :key="conv.id"
            class="history-item"
            :class="{ 'active': chatStore.activeConversationId === conv.id }"
            @click="handleSelectConversation(conv.id)"
          >
            <el-icon><Document /></el-icon>
            <span class="history-title">{{ conv.title }}</span>
          </div>
        </div>
      </aside>

      <!-- 中间：核心监控区 (Core Monitor Area) -->
      <main class="monitor-main prts-panel">
        <div class="panel-header">
          <span class="panel-title">MAIN_SENSOR_FEED</span>
        </div>
        <div class="video-container">
          <div class="video-placeholder" v-if="!latestMediaUrl">
            <el-icon><VideoCamera /></el-icon>
            <p>NO_SIGNAL</p>
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
           <div class="status-group">
             <span class="label">CONN_STATUS:</span>
             <span class="value stable">[STABLE]</span>
           </div>
           <div v-if="chatStore.uploadedMediaFilename" class="status-group upload-ok">
             <span class="label">CACHED_FEED:</span>
             <span class="value">{{ chatStore.uploadedMediaFilename }}</span>
           </div>
        </div>
      </main>

      <!-- 右侧：分析日志与指令输入 (Analysis Log & Command) -->
      <aside class="analysis-sidebar prts-panel">
        <div class="panel-header">
          <span class="panel-title">ANALYSIS_LOG</span>
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
  overflow: hidden;
  position: relative;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);

  /* Top accented border */
  border-top: 4px solid var(--ef-border);
}

.panel-header {
  padding: 12px 16px;
  border-bottom: 1px solid var(--ef-border-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f8f9fa;

  .panel-title {
    font-family: 'Arial', sans-serif;
    font-size: 14px;
    font-weight: 900;
    color: var(--ef-text);
    text-transform: uppercase;
    letter-spacing: 1px;
  }
}

/* ---------------- Left Sidebar ---------------- */
.new-session-btn {
  background: transparent;
  border: 1px solid var(--ef-border);
  color: var(--ef-text);
  border-radius: 0;
  padding: 4px 12px;
  font-size: 12px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: var(--ef-text);
    color: var(--ef-panel-bg);
  }
}

.section-label {
  font-size: 11px;
  font-weight: bold;
  color: var(--ef-text-dim);
  margin-bottom: 8px;
  padding: 0 4px;
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
    background: #f4f4f4;

    &:hover {
      background: #eaeaea;
      border-color: var(--ef-border-light);
    }
    
    &.active {
      background: #e0f4fc;
      border-color: var(--ef-accent);
      color: var(--ef-accent-hover);
      border-left: 4px solid var(--ef-accent);
      font-weight: bold;
    }

    .history-title {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }
}

/* ---------------- Center Monitor ---------------- */
.video-container {
  flex: 1;
  background: #000;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  border-bottom: 1px solid var(--ef-border-light);
}

.video-placeholder {
  color: #555;
  display: flex;
  flex-direction: column;
  align-items: center;
  font-family: monospace;
  font-size: 16px;
  letter-spacing: 2px;
  
  .el-icon {
    font-size: 48px;
    margin-bottom: 16px;
    opacity: 0.5;
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
  background: #fdfdfd;
  font-family: monospace;
  font-size: 13px;

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
  background: #fafafa;
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
    gap: 8px;

    button {
      padding: 10px;
      background: white;
      border: 1px solid var(--ef-border-light);
      color: var(--ef-text);
      cursor: pointer;
      font-size: 13px;
      transition: all 0.2s;

      &:hover {
        border-color: var(--ef-accent);
        color: var(--ef-accent);
        background: #f0f9ff;
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
  background: white;
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
