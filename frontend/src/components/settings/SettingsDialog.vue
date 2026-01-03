<template>
  <el-dialog
    v-model="visible"
    title="系统设置"
    width="500px"
    @close="handleClose"
  >
    <el-form 
      ref="formRef"
      :model="form"
      label-position="top"
      class="settings-form"
    >
      <el-form-item label="DashScope API Key (用于 Qwen/QVQ)">
        <el-input 
          v-model="form.dashscopeKey" 
          placeholder="请输入 DashScope API Key"
          type="password"
          show-password
        />
        <div class="form-tip">用于调用 Qwen-Plus, Qwen-Max, QVQ-Max 等模型</div>
      </el-form-item>

      <el-form-item label="Gemini API Key">
        <el-input 
          v-model="form.geminiKey" 
          placeholder="请输入 Gemini API Key"
          type="password"
          show-password
        />
        <div class="form-tip">用于调用 Google Gemini 3 Pro 模型</div>
      </el-form-item>
    </el-form>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveSettings">
          保存配置
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
}>()

const visible = ref(false)
const saving = ref(false)

const form = reactive({
  dashscopeKey: '',
  geminiKey: ''
})

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    loadSettings()
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

async function loadSettings() {
  try {
    const response = await fetch('/api/settings')
    if (response.ok) {
      const data = await response.json()
      form.dashscopeKey = data.dashscope_key || ''
      form.geminiKey = data.gemini_key || ''
    }
  } catch (error) {
    console.error('Failed to load settings:', error)
  }
}

async function saveSettings() {
  saving.value = true
  try {
    const response = await fetch('/api/settings', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        dashscope_key: form.dashscopeKey,
        gemini_key: form.geminiKey
      })
    })

    if (response.ok) {
      ElMessage.success('设置已保存')
      visible.value = false
    } else {
      ElMessage.error('保存失败')
    }
  } catch (error) {
    ElMessage.error('保存出错')
  } finally {
    saving.value = false
  }
}

function handleClose() {
  emit('update:modelValue', false)
}
</script>

<style scoped>
.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
