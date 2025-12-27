<template>
  <div class="register-page">
    <div class="register-container">
      <div class="register-header">
        <div class="logo-icon">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <h1 class="register-title">多模态大模型-车辆违停感知</h1>
        <p class="register-subtitle">基于AI的校园车辆违停智能分析系统</p>
      </div>

      <el-card class="register-card" shadow="never">
        <h2 class="card-title">注册</h2>

        <el-form :model="form" :rules="rules" ref="formRef" @submit.prevent="handleRegister">
          <el-form-item prop="username">
            <el-input
              v-model="form.username"
              placeholder="用户名（3-20个字符）"
              size="large"
              clearable
            >
              <template #prefix>
                <el-icon><User /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item prop="email">
            <el-input
              v-model="form.email"
              type="email"
              placeholder="邮箱"
              size="large"
              clearable
            >
              <template #prefix>
                <el-icon><Message /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="密码（至少6位）"
              size="large"
              show-password
            >
              <template #prefix>
                <el-icon><Lock /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item prop="confirmPassword">
            <el-input
              v-model="form.confirmPassword"
              type="password"
              placeholder="确认密码"
              size="large"
              show-password
              @keyup.enter="handleRegister"
            >
              <template #prefix>
                <el-icon><Lock /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item v-if="authStore.error">
            <el-alert :title="authStore.error" type="error" :closable="false" />
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="authStore.isLoading"
              @click="handleRegister"
              class="register-button"
            >
              {{ authStore.isLoading ? '注册中...' : '注册' }}
            </el-button>
          </el-form-item>

          <el-form-item class="login-link">
            <span>已有账号？</span>
            <router-link to="/login">立即登录</router-link>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock, Message } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/useAuthStore'
import type { FormInstance, FormRules } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref<FormInstance>()

const form = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
})

const validateConfirmPassword = (_rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为 6 位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' },
  ],
}

async function handleRegister() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      const success = await authStore.register(form.username, form.email, form.password)
      if (success) {
        router.push('/chat')
      }
    }
  })
}

onMounted(() => {
  authStore.clearError()
})
</script>

<style scoped lang="scss">
.register-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #ffffff;
  padding: 20px;
}

.register-container {
  width: 100%;
  max-width: 420px;
}

.register-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo-icon {
  width: 64px;
  height: 64px;
  background: #5b6eae;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  
  svg {
    width: 32px;
    height: 32px;
    color: white;
  }
}

.register-title {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 8px;
}

.register-subtitle {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

.register-card {
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  
  :deep(.el-card__body) {
    padding: 32px;
  }
}

.card-title {
  margin: 0 0 24px;
  text-align: center;
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
}

.register-button {
  width: 100%;
  background: #5b6eae;
  border-color: #5b6eae;
  
  &:hover {
    background: #4a5a94;
    border-color: #4a5a94;
  }
}

.login-link {
  text-align: center;
  margin: 0;

  :deep(.el-form-item__content) {
    justify-content: center;
  }

  span {
    color: #6b7280;
    margin-right: 8px;
  }

  a {
    color: #5b6eae;
    text-decoration: none;
    font-weight: 500;

    &:hover {
      text-decoration: underline;
    }
  }
}

/* 响应式 */
@media (max-width: 767px) {
  .register-container {
    max-width: 100%;
  }

  .register-header {
    margin-bottom: 30px;
  }

  .logo-icon {
    width: 56px;
    height: 56px;
    
    svg {
      width: 28px;
      height: 28px;
    }
  }

  .register-title {
    font-size: 20px;
  }

  .register-card {
    :deep(.el-card__body) {
      padding: 24px;
    }
  }

  .card-title {
    font-size: 18px;
  }
}
</style>
