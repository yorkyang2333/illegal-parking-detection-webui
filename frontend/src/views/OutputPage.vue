<template>
  <div class="output-page">
    <h1 class="page-title">基于多模态大模型的校园返校时段车辆违停感知与优化研究</h1>

    <el-card class="output-card">
      <template #header>
        <div class="card-header">
          <h5>输出结果</h5>
        </div>
      </template>

      <div class="card-body">
        <div v-if="inferenceStore.error" class="error-message">
          <el-alert
            :title="inferenceStore.error"
            type="error"
            :closable="false"
          />
        </div>

        <div v-else-if="inferenceStore.isStreaming" class="loading-indicator">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>正在思考中...</span>
        </div>

        <MarkdownViewer
          v-if="inferenceStore.hasOutput"
          :content="inferenceStore.streamingOutput"
        />

        <div v-if="!inferenceStore.hasOutput && !inferenceStore.isStreaming" class="empty-state">
          <el-empty description="暂无输出结果，请先在输入页运行推理" />
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { Loading } from '@element-plus/icons-vue'
import { useInferenceStore } from '@/stores/useInferenceStore'
import { useUiStore } from '@/stores/useUiStore'
import MarkdownViewer from '@/components/common/MarkdownViewer.vue'

const inferenceStore = useInferenceStore()
const uiStore = useUiStore()

onMounted(() => {
  // Clear notification badge when viewing output page
  uiStore.clearOutputNotification()
})
</script>

<style scoped lang="scss">
.output-page {
  max-width: 1400px;
  margin: 0 auto;
}

.page-title {
  text-align: center;
  color: #1c1e21;
  font-weight: 700;
  font-size: 24px;
  margin-bottom: 30px;
}

.output-card {
  min-height: 600px;
  border-radius: 12px;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s ease-in-out;

  &:hover {
    transform: translateY(-5px);
  }
}

.card-header {
  h5 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
  }
}

.card-body {
  display: flex;
  flex-direction: column;
  min-height: 400px;
}

.error-message {
  margin-bottom: 20px;
}

.loading-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 40px;
  color: #1877f2;
  font-size: 16px;

  .el-icon {
    font-size: 24px;
  }
}

.empty-state {
  flex-grow: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
