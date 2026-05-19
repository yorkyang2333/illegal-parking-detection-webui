<template>
  <div class="analysis">
    <header class="analysis__header">
      <h1 class="analysis__title">违停感知</h1>
      <p class="analysis__desc">多模态 AI Agent 自主分析，实时标注检测结果</p>
    </header>

    <VideoUpload
      v-if="!agentStore.hasVideo"
      @file-selected="agentStore.setVideoFile($event)"
    />

    <div v-else class="analysis__workspace">
      <!-- 左：视频 + 操作 + 进度条 -->
      <div class="col-video">
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

        <AnalysisProgress :phases="agentStore.phases" />
      </div>

      <!-- 中：Agent 思考链 -->
      <div class="col-thoughts">
        <AgentThoughtPanel />
      </div>

      <!-- 右：检测结果 -->
      <div class="col-results">
        <div class="results-panel">
          <div class="results-panel__header">
            <span class="results-panel__title">检测结果</span>
            <span
              v-if="agentStore.isCompleted"
              class="results-panel__count"
              :class="agentStore.violations.length > 0 ? 'results-panel__count--alert' : 'results-panel__count--ok'"
            >
              {{ agentStore.violations.length }} 辆
            </span>
          </div>

          <!-- 初始状态 -->
          <div
            v-if="!agentStore.isProcessing && !agentStore.isCompleted"
            class="results-panel__placeholder"
          >
            启动分析后，违停车辆将在此显示
          </div>

          <!-- 分析中：骨架占位 -->
          <div v-else-if="agentStore.isProcessing && !agentStore.isCompleted" class="results-panel__skeleton">
            <div v-for="i in 3" :key="i" class="skeleton-card" />
          </div>

          <!-- 完成 + 有违停 -->
          <div v-else-if="agentStore.isCompleted && agentStore.violations.length > 0" class="results-panel__list">
            <ViolationCard
              v-for="v in agentStore.violations"
              :key="v.track_id"
              :record="v"
              @jump="agentStore.jumpToFrame($event)"
            />
          </div>

          <!-- 完成 + 无违停 -->
          <div v-else-if="agentStore.isCompleted" class="results-panel__empty">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
              <polyline points="22 4 12 14.01 9 11.01" />
            </svg>
            <span>未检测到违停车辆</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 最终报告 -->
    <Transition name="slide-up">
      <AnalysisReport
        v-if="agentStore.isCompleted"
        :content="agentStore.finalReport"
      />
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { useAgentStore } from '@/stores/useAgentStore'
import BaseButton from '@/components/ui/BaseButton.vue'
import VideoUpload from '@/components/analysis/VideoUpload.vue'
import VideoAnnotationCanvas from '@/components/analysis/VideoAnnotationCanvas.vue'
import AgentThoughtPanel from '@/components/analysis/AgentThoughtPanel.vue'
import AnalysisProgress from '@/components/analysis/AnalysisProgress.vue'
import ViolationCard from '@/components/analysis/ViolationCard.vue'
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
  padding: var(--space-xl, 40px) 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-xl, 40px);
}

.analysis__header {
  // intentionally minimal
}

.analysis__title {
  font-family: var(--font-display, 'Cormorant Garamond', serif);
  font-size: 36px;
  font-weight: 400;
  letter-spacing: -0.5px;
  color: var(--color-ink, #1a1916);
  margin-bottom: var(--space-xs, 6px);
}

.analysis__desc {
  font-size: 15px;
  color: var(--color-muted, #a09a8e);
}

.analysis__workspace {
  display: grid;
  grid-template-columns: 1fr 300px 300px;
  gap: var(--space-lg, 24px);
  align-items: start;

  @media (max-width: 1200px) {
    grid-template-columns: 1fr 260px 260px;
  }

  @media (max-width: 900px) {
    grid-template-columns: 1fr 1fr;

    .col-video {
      grid-column: 1 / -1;
    }
  }

  @media (max-width: 600px) {
    grid-template-columns: 1fr;
  }
}

.col-video {
  display: flex;
  flex-direction: column;
  gap: var(--space-md, 16px);
}

.col-thoughts,
.col-results {
  min-height: 520px;
  height: 560px;
}

.analysis__actions {
  display: flex;
  gap: var(--space-sm, 8px);
  flex-wrap: wrap;
}

// Results panel
.results-panel {
  background: var(--color-surface-card, #efe9de);
  border-radius: var(--radius-lg, 12px);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 100%;

  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-md, 14px) var(--space-lg, 20px);
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);
    flex-shrink: 0;
  }

  &__title {
    font-size: 14px;
    font-weight: 500;
    color: var(--color-ink, #1a1916);
  }

  &__count {
    font-size: 12px;
    padding: 2px 10px;
    border-radius: 20px;
    font-family: var(--font-mono, monospace);

    &--alert {
      background: rgba(217, 79, 79, 0.12);
      color: var(--color-error, #d94f4f);
    }

    &--ok {
      background: rgba(90, 172, 115, 0.15);
      color: var(--color-success, #5aac73);
    }
  }

  &__placeholder {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    color: var(--color-muted, #a09a8e);
    padding: var(--space-lg, 24px);
    text-align: center;
  }

  &__list {
    flex: 1;
    overflow-y: auto;
    padding: var(--space-sm, 10px) var(--space-md, 14px);
    display: flex;
    flex-direction: column;
    gap: var(--space-sm, 10px);

    &::-webkit-scrollbar {
      width: 4px;
    }
    &::-webkit-scrollbar-thumb {
      background: rgba(0, 0, 0, 0.1);
      border-radius: 2px;
    }
  }

  &__skeleton {
    flex: 1;
    padding: var(--space-sm, 10px) var(--space-md, 14px);
    display: flex;
    flex-direction: column;
    gap: var(--space-sm, 10px);
  }

  &__empty {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: var(--space-sm, 10px);
    color: var(--color-success, #5aac73);
    font-size: 13px;

    svg {
      width: 36px;
      height: 36px;
      opacity: 0.7;
    }
  }
}

.skeleton-card {
  height: 100px;
  background: rgba(0, 0, 0, 0.06);
  border-radius: var(--radius-md, 8px);
  animation: skeleton-pulse 1.4s ease-in-out infinite;

  &:nth-child(2) { animation-delay: 0.2s; }
  &:nth-child(3) { animation-delay: 0.4s; }
}

// Slide-up transition for report
.slide-up-enter-active {
  transition: opacity 0.35s ease, transform 0.35s ease;
}
.slide-up-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

@keyframes skeleton-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.45; }
}
</style>
