<template>
  <AppLayout>
    <div class="chat-page">
      <!-- 聊天消息区域 -->
      <div class="chat-messages" ref="messagesContainerRef">
        <!-- 欢迎界面 -->
        <div v-if="!chatStore.hasMessages" class="welcome-screen">
          <div class="welcome-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h1 class="welcome-title">欢迎使用 AI 智能助手</h1>
          <p class="welcome-subtitle">基于多模态大模型的校园车辆违停感知与优化研究</p>
          
          <div class="quick-prompts">
            <button 
              v-for="(prompt, index) in quickPrompts" 
              :key="index"
              class="quick-prompt-btn"
              @click="handleQuickPrompt(prompt)"
            >
              <el-icon><ChatDotSquare /></el-icon>
              {{ prompt.title }}
            </button>
          </div>
        </div>

        <!-- 消息列表 -->
        <div v-else class="messages-list">
          <ChatMessage 
            v-for="message in chatStore.messages" 
            :key="message.id" 
            :message="message" 
          />
        </div>
      </div>

      <!-- 错误提示 -->
      <div v-if="chatStore.error" class="error-banner">
        <el-alert :title="chatStore.error" type="error" :closable="false" />
      </div>

      <!-- 输入区域 -->
      <ChatInput 
        :disabled="chatStore.isStreaming"
        placeholder="请输入您的问题，我会尽力帮助您..."
        @send="handleSend"
      />
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { ChatDotSquare } from '@element-plus/icons-vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import ChatMessage from '@/components/chat/ChatMessage.vue'
import ChatInput from '@/components/chat/ChatInput.vue'
import { useChatStore } from '@/stores/useChatStore'

const chatStore = useChatStore()
const messagesContainerRef = ref<HTMLElement | null>(null)

const quickPrompts = [
  {
    title: '分析违停报告并替换车牌号',
    content: `现有一段违停的分析报告：
[粘贴Gemini生成的违停分析报告]
由QVQ-Max重新识别了车牌号为：
[粘贴QVQ-Max识别到的车牌号]
请帮我把QVQ-Max识别到的车牌号替换报告中原先识别到的车牌号，依据且仅依据原报告中的内容，重新生成一份详尽违停报告。请依次输出：
1.违停车辆车牌号
2.该车辆违停原因（根据原分析报告中的内容进一步总结得出）
3.建议处罚（根据现行《中华人民共和国道路交通安全法》）
请确保仅按照原报告中的内容进行重新输出，保证格式清晰明确，逻辑性强，不要主观臆断。`
  },
  {
    title: '生成违停处罚建议',
    content: '请根据《中华人民共和国道路交通安全法》，为校园内违停车辆生成处罚建议。'
  },
  {
    title: '分析车辆违停原因',
    content: '请分析校园返校时段常见的车辆违停原因及优化建议。'
  }
]

function handleQuickPrompt(prompt: { title: string; content: string }) {
  chatStore.sendMessage(prompt.content)
}

function handleSend(content: string) {
  chatStore.sendMessage(content)
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
  if (messagesContainerRef.value) {
    messagesContainerRef.value.scrollTop = messagesContainerRef.value.scrollHeight
  }
}
</script>

<style scoped lang="scss">
.chat-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #ffffff;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
  scroll-behavior: smooth;
}

/* 欢迎界面 */
.welcome-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  text-align: center;
  padding: 40px 20px;
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.welcome-icon {
  width: 80px;
  height: 80px;
  background: #5b6eae;
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 30px;
  box-shadow: 0 8px 24px rgba(91, 110, 174, 0.25);

  svg {
    width: 40px;
    height: 40px;
    color: white;
  }
}

.welcome-title {
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 12px;
}

.welcome-subtitle {
  font-size: 16px;
  color: #6b7280;
  margin: 0 0 40px;
  max-width: 400px;
}

.quick-prompts {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
  max-width: 600px;
}

.quick-prompt-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  color: #4b5563;
  cursor: pointer;
  transition: all 0.2s ease;

  .el-icon {
    font-size: 18px;
    color: #5b6eae;
  }

  &:hover {
    border-color: #5b6eae;
    background: #f8f9ff;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(91, 110, 174, 0.15);
  }
}

/* 消息列表 */
.messages-list {
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
}

/* 错误提示 */
.error-banner {
  padding: 0 24px 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-messages {
    padding: 16px;
  }

  .welcome-screen {
    min-height: 50vh;
    padding: 30px 16px;
  }

  .welcome-icon {
    width: 60px;
    height: 60px;
    border-radius: 18px;
    margin-bottom: 24px;

    svg {
      width: 30px;
      height: 30px;
    }
  }

  .welcome-title {
    font-size: 24px;
  }

  .welcome-subtitle {
    font-size: 14px;
    margin-bottom: 30px;
  }

  .quick-prompts {
    flex-direction: column;
    width: 100%;
  }

  .quick-prompt-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
