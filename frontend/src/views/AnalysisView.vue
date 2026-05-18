<template>
  <div class="analysis">
    <header class="analysis__header">
      <h1 class="analysis__title">视频分析</h1>
      <p class="analysis__desc">上传监控视频，AI 自动检测违停车辆并生成报告</p>
    </header>

    <div class="analysis__body">
      <div class="analysis__left">
        <VideoUpload
          v-if="!analysisStore.hasVideo"
          @file-selected="handleFileSelected"
        />
        <VideoPreview
          v-else
          :src="analysisStore.videoPreviewUrl!"
          :filename="analysisStore.videoFile!.name"
          @remove="handleRemoveVideo"
        />

        <div class="analysis__actions">
          <BaseButton
            v-if="analysisStore.hasVideo && !analysisStore.isProcessing && !analysisStore.isAllCompleted"
            variant="primary"
            @click="analysisStore.startAnalysis()"
          >
            开始分析
          </BaseButton>
          <BaseButton
            v-if="analysisStore.isProcessing"
            variant="secondary"
            @click="analysisStore.stopAnalysis()"
          >
            停止
          </BaseButton>
          <BaseButton
            v-if="analysisStore.isAllCompleted"
            variant="secondary"
            @click="handleReset"
          >
            新建分析
          </BaseButton>
          <BaseButton
            v-if="analysisStore.isAllCompleted"
            variant="primary"
            @click="handleDownload"
          >
            下载报告
          </BaseButton>
        </div>
      </div>

      <div class="analysis__right">
        <PipelineTimeline :steps="analysisStore.steps" :current-step="analysisStore.currentStep" />
        <AnalysisReport v-if="analysisStore.isAllCompleted" :content="analysisStore.finalResult" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAnalysisStore } from '@/stores/useAnalysisStore'
import BaseButton from '@/components/ui/BaseButton.vue'
import VideoUpload from '@/components/analysis/VideoUpload.vue'
import VideoPreview from '@/components/analysis/VideoPreview.vue'
import PipelineTimeline from '@/components/analysis/PipelineTimeline.vue'
import AnalysisReport from '@/components/analysis/AnalysisReport.vue'

const analysisStore = useAnalysisStore()

function handleFileSelected(file: File) {
  analysisStore.setVideoFile(file)
}

function handleRemoveVideo() {
  analysisStore.clearVideoFile()
  analysisStore.resetAnalysis()
}

function handleReset() {
  analysisStore.clearVideoFile()
  analysisStore.resetAnalysis()
}

function handleDownload() {
  const content = analysisStore.finalResult
  const blob = new Blob([content], { type: 'text/markdown' })
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
}

.analysis__header {
  margin-bottom: var(--space-xl);
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

.analysis__body {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-xl);
  align-items: start;

  @media (max-width: 1023px) {
    grid-template-columns: 1fr;
  }
}

.analysis__left {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.analysis__right {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.analysis__actions {
  display: flex;
  gap: var(--space-sm);
  flex-wrap: wrap;
}
</style>
