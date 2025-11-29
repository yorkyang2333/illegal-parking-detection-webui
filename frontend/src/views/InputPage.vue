<template>
  <AppLayout>
    <div class="input-page">
    <h1 class="page-title">基于多模态大模型的校园返校时段车辆违停感知与优化研究</h1>

    <el-card class="input-card">
      <template #header>
        <div class="card-header">
          <h5>输入提示词</h5>
          <p>请先使用Gemini分析违停，QVQ-Max识别车牌号，再前往此处总结。</p>
        </div>
      </template>

      <div class="card-body">
        <el-input
          v-model="inferenceStore.userInput"
          type="textarea"
          :rows="15"
          placeholder="请在这里输入你的提示词……"
          class="prompt-textarea"
        />

        <div class="button-group">
          <el-button
            type="success"
            :loading="inferenceStore.isStreaming"
            @click="handleRun"
            size="large"
          >
            {{ inferenceStore.isStreaming ? '思考中...' : '运行' }}
          </el-button>

          <el-button
            type="danger"
            @click="handleReset"
            :disabled="inferenceStore.isStreaming"
            size="large"
          >
            重置
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
  </AppLayout>
</template>

<script setup lang="ts">
import AppLayout from '@/components/layout/AppLayout.vue'
import { useInferenceStore } from '@/stores/useInferenceStore'
import { useRouter } from 'vue-router'

const inferenceStore = useInferenceStore()
const router = useRouter()

async function handleRun() {
  await inferenceStore.startInference()
  router.push('/output')
}

function handleReset() {
  inferenceStore.resetPrompt()
  inferenceStore.clearOutput()
}
</script>

<style scoped lang="scss">
.input-page {
  max-width: 1400px;
  margin: 0 auto;
}

.page-title {
  text-align: center;
  color: #1c1e21;
  font-weight: 700;
  font-size: 24px;
  margin-bottom: 30px;
  transition: font-size 0.3s ease;
}

.input-card {
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
    margin: 0 0 10px 0;
    font-size: 18px;
    font-weight: 600;
  }

  p {
    margin: 0;
    color: #666;
    font-size: 14px;
  }
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.prompt-textarea {
  :deep(.el-textarea__inner) {
    font-family: 'Roboto', sans-serif;
    font-size: 14px;
    line-height: 1.5;
  }
}

.button-group {
  display: flex;
  gap: 10px;
}

/* 响应式设计 */

/* 移动端 (<768px) */
@media (max-width: 767px) {
  .page-title {
    font-size: 18px;
    margin-bottom: 20px;
  }

  .input-card {
    border-radius: 8px;
    min-height: auto;

    &:hover {
      transform: none;
    }
  }

  .prompt-textarea {
    :deep(.el-textarea__inner) {
      font-size: 13px;
    }
  }

  .button-group {
    flex-direction: column;

    :deep(.el-button) {
      width: 100%;
    }
  }
}

/* 平板 (768px-1024px) */
@media (min-width: 768px) and (max-width: 1023px) {
  .page-title {
    font-size: 20px;
    margin-bottom: 25px;
  }

  .input-card {
    min-height: 500px;
  }
}

/* 桌面 (>=1024px) - 保持原有样式 */
@media (min-width: 1024px) {
  .page-title {
    font-size: 24px;
  }
}
</style>
