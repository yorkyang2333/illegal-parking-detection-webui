<template>
  <AppLayout>
    <div class="analysis-page">
      <!-- 流程指示器 -->
      <div class="workflow-header">
        <div class="workflow-progress">
          <template v-for="(step, index) in analysisStore.steps" :key="step.id">
            <div 
              class="progress-step"
              :class="[
                step.status,
                { active: step.id === analysisStore.currentStep }
              ]"
              @click="analysisStore.goToStep(step.id)"
            >
              <div class="step-circle">
                <el-icon v-if="step.status === 'completed'"><Check /></el-icon>
                <el-icon v-else-if="step.status === 'running'" class="is-loading"><Loading /></el-icon>
                <el-icon v-else-if="step.status === 'error'"><Close /></el-icon>
                <span v-else>{{ step.id }}</span>
              </div>
              <div class="step-label">{{ step.title }}</div>
            </div>
            <div v-if="index < 3" class="step-connector" :class="step.status"></div>
          </template>
        </div>
        <el-button 
          class="reset-button" 
          @click="analysisStore.resetAnalysis()"
          :disabled="!analysisStore.hasVideo"
        >
          <el-icon><RefreshRight /></el-icon>
          重新分析
        </el-button>
      </div>

      <!-- 内容区域 -->
      <div class="workflow-content">
        <div v-if="analysisStore.currentStep === 1" class="step-content upload-step">
          <div class="step-header">
            <h2>上传监控视频</h2>
            <p>{{ analysisStore.steps[0]?.description }}</p>
          </div>

          <div class="upload-area" 
            :class="{ 'has-file': analysisStore.hasVideo }"
            @dragover.prevent
            @drop.prevent="handleDrop"
          >
            <div v-if="!analysisStore.hasVideo" class="upload-placeholder">
              <el-icon class="upload-icon"><Upload /></el-icon>
              <p>将视频文件拖拽到此处，或点击上传</p>
              <p class="upload-hint">支持 MP4, AVI, MOV 等格式</p>
              <input type="file" ref="fileInput" @change="handleFileSelect" accept="video/*" hidden>
              <el-button type="primary" @click="triggerFileInput">选择视频文件</el-button>
            </div>

            <div v-else class="video-preview">
              <video 
                :src="analysisStore.videoPreviewUrl!" 
                controls 
                class="preview-video"
              ></video>
              <div class="file-info">
                <span class="file-name">{{ analysisStore.videoFile?.name }}</span>
                <span class="file-size">{{ formatFileSize(analysisStore.videoFile?.size || 0) }}</span>
                <el-button type="danger" size="small" @click="analysisStore.clearVideoFile">
                  <el-icon><Delete /></el-icon> 移除
                </el-button>
              </div>
            </div>
          </div>

          <div class="step-actions">
            <el-button 
              type="primary" 
              size="large" 
              :disabled="!analysisStore.hasVideo"
              @click="analysisStore.startAnalysis"
            >
              <el-icon><VideoPlay /></el-icon>
              开始分析
            </el-button>
          </div>
        </div>

        <!-- Step 2: 违停检测 -->
        <div v-else-if="analysisStore.currentStep === 2" class="step-content analysis-step">
          <div class="step-header">
            <h2>违停检测</h2>
            <p>{{ analysisStore.steps[1]?.description }}</p>
          </div>

          <div class="result-area">
            <div v-if="analysisStore.steps[1]?.status === 'running'" class="analyzing">
              <el-icon class="is-loading"><Loading /></el-icon>
              <span>正在分析视频中的违停情况...</span>
            </div>
            <div v-if="analysisStore.steps[1]?.result" class="result-content" v-html="renderMarkdown(analysisStore.steps[1]?.result || '')"></div>
            <div v-if="analysisStore.steps[1]?.error" class="error-content">
              <el-alert :title="analysisStore.steps[1]?.error" type="error" :closable="false" />
            </div>
          </div>
        </div>

        <!-- Step 3: 车牌识别 -->
        <div v-else-if="analysisStore.currentStep === 3" class="step-content analysis-step">
          <div class="step-header">
            <h2>车牌识别</h2>
            <p>{{ analysisStore.steps[2]?.description }}</p>
          </div>

          <div class="result-area">
            <div v-if="analysisStore.steps[2]?.status === 'running'" class="analyzing">
              <el-icon class="is-loading"><Loading /></el-icon>
              <span>正在识别视频中的车牌号...</span>
            </div>
            <div v-if="analysisStore.steps[2]?.result" class="result-content" v-html="renderMarkdown(analysisStore.steps[2]?.result || '')"></div>
            <div v-if="analysisStore.steps[2]?.error" class="error-content">
              <el-alert :title="analysisStore.steps[2]?.error" type="error" :closable="false" />
            </div>
          </div>
        </div>

        <!-- Step 4: 报告生成 -->
        <div v-else-if="analysisStore.currentStep === 4" class="step-content analysis-step">
          <div class="step-header">
            <h2>报告生成</h2>
            <p>{{ analysisStore.steps[3]?.description }}</p>
          </div>

          <div class="result-area">
            <div v-if="analysisStore.steps[3]?.status === 'running'" class="analyzing">
              <el-icon class="is-loading"><Loading /></el-icon>
              <span>正在生成最终违停报告...</span>
            </div>
            <div v-if="analysisStore.steps[3]?.result" class="result-content final-report" v-html="renderMarkdown(analysisStore.steps[3]?.result || '')"></div>
            <div v-if="analysisStore.steps[3]?.error" class="error-content">
              <el-alert :title="analysisStore.steps[3]?.error" type="error" :closable="false" />
            </div>
          </div>

          <div v-if="analysisStore.isAllCompleted" class="step-actions">
            <el-button type="success" size="large" @click="downloadReport">
              <el-icon><Download /></el-icon>
              下载报告
            </el-button>
            <el-button size="large" @click="analysisStore.resetAnalysis">
              <el-icon><RefreshRight /></el-icon>
              重新分析
            </el-button>
          </div>
        </div>
      </div>

      <!-- 底部控制栏 -->
      <div v-if="analysisStore.isProcessing" class="control-bar">
        <el-button type="danger" @click="analysisStore.stopAnalysis">
          <el-icon><VideoPause /></el-icon>
          停止分析
        </el-button>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { 
  Check, Close, Loading, Upload, Delete, VideoPlay, 
  Download, RefreshRight, VideoPause 
} from '@element-plus/icons-vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useAnalysisStore } from '@/stores/useAnalysisStore'

const analysisStore = useAnalysisStore()
const fileInput = ref<HTMLInputElement | null>(null)

// Markdown 渲染函数
function renderMarkdown(content: string): string {
  if (!content) return ''
  const rawHtml = marked(content)
  return DOMPurify.sanitize(rawHtml as string)
}

function triggerFileInput() {
  fileInput.value?.click()
}

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    analysisStore.setVideoFile(file)
  }
}

function handleDrop(event: DragEvent) {
  const file = event.dataTransfer?.files[0]
  if (file && file.type.startsWith('video/')) {
    analysisStore.setVideoFile(file)
  }
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

function downloadReport() {
  const report = analysisStore.finalResult
  const blob = new Blob([report], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `违停分析报告_${new Date().toISOString().split('T')[0]}.md`
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped lang="scss">
.analysis-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f9fafb;
  padding: 24px;
  overflow: auto;
}

/* 流程指示器容器 */
.workflow-header {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 16px 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  margin-bottom: 24px;
  position: relative;
}

.workflow-progress {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  gap: 0;
}

.reset-button {
  flex-shrink: 0;
  margin-left: 24px;
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 80px;

  &:hover .step-circle {
    transform: scale(1.08);
  }

  &.active .step-circle {
    background: #5b6eae;
    color: white;
    box-shadow: 0 4px 12px rgba(91, 110, 174, 0.3);
  }

  &.completed .step-circle {
    background: #10b981;
    color: white;
  }

  &.running .step-circle {
    background: #5b6eae;
    color: white;
    animation: pulse 1.5s ease-in-out infinite;
  }

  &.error .step-circle {
    background: #ef4444;
    color: white;
  }
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(91, 110, 174, 0.4); }
  50% { box-shadow: 0 0 0 12px rgba(91, 110, 174, 0); }
}

.step-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #e5e7eb;
  color: #6b7280;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 600;
  transition: all 0.3s ease;
  flex-shrink: 0;

  .el-icon {
    font-size: 22px;
  }
}

.step-connector {
  width: 60px;
  height: 3px;
  background: #e5e7eb;
  margin-top: 20px;
  flex-shrink: 0;
  transition: all 0.3s ease;

  &.completed {
    background: #10b981;
  }

  &.running {
    background: linear-gradient(90deg, #10b981 50%, #e5e7eb 50%);
    background-size: 200% 100%;
    animation: loading-bar 1s ease-in-out infinite;
  }
}

@keyframes loading-bar {
  0% { background-position: 100% 0; }
  100% { background-position: 0 0; }
}

.step-label {
  margin-top: 8px;
  font-size: 13px;
  font-weight: 500;
  color: #4b5563;
  text-align: center;
  white-space: nowrap;
}

/* 内容区域 */
.workflow-content {
  flex: 1;
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  padding: 32px;
  overflow: auto;
}

.step-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.step-header {
  text-align: center;
  margin-bottom: 32px;

  h2 {
    font-size: 24px;
    font-weight: 700;
    color: #1f2937;
    margin: 0 0 8px;
  }

  p {
    font-size: 14px;
    color: #6b7280;
    margin: 0;
  }
}

/* 上传区域 */
.upload-area {
  border: 2px dashed #d1d5db;
  border-radius: 16px;
  padding: 48px;
  text-align: center;
  transition: all 0.3s ease;
  background: #fafafa;

  &:hover {
    border-color: #5b6eae;
    background: #f8f9ff;
  }

  &.has-file {
    border-style: solid;
    border-color: #5b6eae;
    background: white;
    padding: 24px;
  }
}

.upload-placeholder {
  .upload-icon {
    font-size: 64px;
    color: #9ca3af;
    margin-bottom: 16px;
  }

  p {
    color: #6b7280;
    margin: 8px 0;

    &.upload-hint {
      font-size: 12px;
      color: #9ca3af;
    }
  }

  .el-button {
    margin-top: 16px;
  }
}

.video-preview {
  .preview-video {
    max-width: 100%;
    max-height: 400px;
    border-radius: 12px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  }

  .file-info {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 16px;
    margin-top: 16px;

    .file-name {
      font-weight: 600;
      color: #1f2937;
    }

    .file-size {
      color: #6b7280;
      font-size: 14px;
    }
  }
}

/* 结果区域 */
.result-area {
  min-height: 200px;
  background: #f9fafb;
  border-radius: 12px;
  padding: 24px;
}

.analyzing {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #5b6eae;
  font-size: 16px;
  font-weight: 500;
  padding: 40px 0;

  .el-icon {
    font-size: 24px;
  }
}

.result-content {
  font-size: 14px;
  line-height: 1.8;
  color: #374151;

  &.final-report {
    background: white;
    padding: 24px;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
  }

  :deep(h1), :deep(h2), :deep(h3) {
    color: #1f2937;
    margin-top: 16px;
    margin-bottom: 8px;
  }

  :deep(ul), :deep(ol) {
    padding-left: 20px;
  }

  :deep(code) {
    background: #f3f4f6;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 13px;
  }

  :deep(pre) {
    background: #1f2937;
    color: #e5e7eb;
    padding: 16px;
    border-radius: 8px;
    overflow-x: auto;
  }
}

.error-content {
  padding: 20px 0;
}

/* 操作按钮区域 */
.step-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 32px;
}

/* 底部控制栏 */
.control-bar {
  display: flex;
  justify-content: center;
  padding-top: 16px;
  margin-top: 16px;
  border-top: 1px solid #e5e7eb;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .analysis-page {
    padding: 16px;
  }

  .workflow-progress {
    padding: 16px;
    flex-wrap: nowrap;
    overflow-x: auto;
  }

  .step-circle {
    width: 40px;
    height: 40px;
    font-size: 16px;

    .el-icon {
      font-size: 18px;
    }
  }

  .step-connector {
    width: 40px;
  }

  .step-label {
    font-size: 12px;
  }

  .workflow-content {
    padding: 20px;
  }

  .step-header h2 {
    font-size: 20px;
  }

  .upload-area {
    padding: 24px;
  }
}
</style>
