<template>
  <div class="analysis">
    <header class="analysis__header">
      <h1 class="analysis__title">违停感知</h1>
      <p class="analysis__desc">多模态 AI Agent 自主分析，实时标注检测结果</p>
    </header>

    <!-- 上传区（无视频时显示） -->
    <VideoUpload
      v-if="!agentStore.hasVideo"
      @file-selected="agentStore.setVideoFile($event)"
    />

    <!-- 主分析区 -->
    <div v-else class="analysis__workspace">
      <!-- 左：视频 + Canvas 标注 -->
      <div class="analysis__video-col">
        <VideoAnnotationCanvas :src="agentStore.videoPreviewUrl!" />

        <div class="analysis__actions">
          <BaseButton
            v-if="!agentStore.isProcessing && !agentStore.isCompleted"
            variant="primary"
            @click="agentStore.startAgentAnalysis()"
          >
            启动 Agent 分析
          </BaseButton>
          <BaseButton
            v-if="agentStore.isProcessing"
            variant="secondary"
            @click="agentStore.stopAnalysis()"
          >
            中止
          </BaseButton>
          <BaseButton
            variant="secondary"
            @click="agentStore.resetAnalysis()"
          >
            重置
          </BaseButton>
          <BaseButton
            v-if="agentStore.isCompleted"
            variant="primary"
            @click="handleDownload"
          >
            下载报告
          </BaseButton>
        </div>
      </div>

      <!-- 右：Agent 思考面板 -->
      <div class="analysis__agent-col">
        <AgentThoughtPanel />
      </div>
    </div>

    <!-- 最终报告（完成后展示） -->
    <AnalysisReport
      v-if="agentStore.isCompleted"
      :content="agentStore.finalReport"
    />
  </div>
</template>

<script setup lang="ts">
import { useAgentStore } from '@/stores/useAgentStore'
import BaseButton from '@/components/ui/BaseButton.vue'
import VideoUpload from '@/components/analysis/VideoUpload.vue'
import VideoAnnotationCanvas from '@/components/analysis/VideoAnnotationCanvas.vue'
import AgentThoughtPanel from '@/components/analysis/AgentThoughtPanel.vue'
import AnalysisReport from '@/components/analysis/AnalysisReport.vue'

const agentStore = useAgentStore()

function handleDownload() {
  const blob = new Blob([agentStore.finalReport], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `违停分析报告_${new Date().toISOString().slice(0, 10)}.md`
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped lang="scss">
.analysis {
  padding: var(--space-xl) 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
}

.analysis__header {
  // keep existing header styles
}

.analysis__title {
  font-family: var(--font-display);
  font-size: 36px;
  font-weight: 400;
  letter-spacing: -0.5px;
  color: var(--color-ink);
  margin-bottom: var(--space-xs);
}

.analysis__desc {
  font-size: 16px;
  color: var(--color-muted);
}

.analysis__workspace {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: var(--space-xl);
  align-items: start;

  @media (max-width: 1023px) {
    grid-template-columns: 1fr;
  }
}

.analysis__video-col {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.analysis__agent-col {
  height: 600px;

  @media (max-width: 1023px) {
    height: 400px;
  }
}

.analysis__actions {
  display: flex;
  gap: var(--space-sm);
  flex-wrap: wrap;
}
</style>

