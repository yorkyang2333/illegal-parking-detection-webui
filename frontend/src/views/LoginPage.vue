<template>
  <div class="login-page">
    <el-card class="login-card">
      <template #header>
        <h2 class="card-title">登录</h2>
      </template>

      <el-form :model="form" :rules="rules" ref="formRef" @submit.prevent="handleLogin">
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名"
            size="large"
            clearable
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            size="large"
            show-password
            @keyup.enter="handleLogin"
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
            @click="handleLogin"
            class="login-button"
          >
            {{ authStore.isLoading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>

        <el-form-item class="register-link">
          <span>还没有账号？</span>
          <router-link to="/register">立即注册</router-link>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/useAuthStore'
import type { FormInstance, FormRules } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref<FormInstance>()

const form = reactive({
  username: '',
  password: '',
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      const success = await authStore.login(form.username, form.password)
      if (success) {
        router.push('/input')
      }
    }
  })
}

onMounted(() => {
  authStore.clearError()
})
</script>

<style scoped lang="scss">
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 400px;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.card-title {
  margin: 0;
  text-align: center;
  font-size: 24px;
  font-weight: 700;
  color: #1c1e21;
}

.login-button {
  width: 100%;
}

.register-link {
  text-align: center;
  margin: 0;

  span {
    color: #666;
    margin-right: 8px;
  }

  a {
    color: var(--primary-color);
    text-decoration: none;
    font-weight: 500;

    &:hover {
      text-decoration: underline;
    }
  }
}

/* 响应式 */
@media (max-width: 767px) {
  .login-card {
    max-width: 100%;
  }

  .card-title {
    font-size: 20px;
  }
}
</style>
