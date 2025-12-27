<template>
  <header class="app-header">
    <div class="header-left">
      <div class="logo-section">
        <div class="logo-icon">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <span class="logo-text">多模态大模型-车辆违停感知</span>
      </div>
    </div>

    <div class="header-center">
      <a
        href="https://gemini.google.com"
        target="_blank"
        rel="noopener noreferrer"
        class="header-link"
      >
        <img src="/assets/gemini_logo.svg" class="link-icon" alt="Gemini">
        <span class="link-text">Gemini</span>
        <svg class="external-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
          <polyline points="15 3 21 3 21 9"/>
          <line x1="10" y1="14" x2="21" y2="3"/>
        </svg>
      </a>
      <a
        href="https://chat.qwen.ai"
        target="_blank"
        rel="noopener noreferrer"
        class="header-link"
      >
        <img src="/assets/qwen_logo.svg" class="link-icon" alt="Qwen">
        <span class="link-text">Qwen Chat</span>
        <svg class="external-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
          <polyline points="15 3 21 3 21 9"/>
          <line x1="10" y1="14" x2="21" y2="3"/>
        </svg>
      </a>
      <button class="new-chat-btn" @click="handleNewChat" :disabled="chatStore.isStreaming">
        <el-icon><Plus /></el-icon>
        <span>新建对话</span>
      </button>
    </div>

    <div class="header-right">
      <button class="user-info" @click="showProfileDialog = true" title="修改个人信息">
        <el-icon class="user-icon"><User /></el-icon>
        <span class="user-name">{{ authStore.user?.username || '用户' }}</span>
        <el-icon class="edit-icon"><Edit /></el-icon>
      </button>
      <button class="logout-btn" @click="handleLogout" title="退出登录">
        <el-icon><SwitchButton /></el-icon>
        <span class="logout-text">退出</span>
      </button>
    </div>

    <!-- 移动端汉堡菜单 -->
    <button class="mobile-menu-btn" @click="toggleMobileMenu">
      <span class="menu-line"></span>
      <span class="menu-line"></span>
      <span class="menu-line"></span>
    </button>

    <!-- 移动端下拉菜单 -->
    <div v-if="isMobileMenuOpen" class="mobile-menu-overlay" @click="closeMobileMenu"></div>
    <nav class="mobile-menu" :class="{ open: isMobileMenuOpen }">
      <a href="https://gemini.google.com" target="_blank" rel="noopener noreferrer" class="mobile-link" @click="closeMobileMenu">
        <img src="/assets/gemini_logo.svg" class="link-icon" alt="Gemini">
        Gemini
      </a>
      <a href="https://chat.qwen.ai" target="_blank" rel="noopener noreferrer" class="mobile-link" @click="closeMobileMenu">
        <img src="/assets/qwen_logo.svg" class="link-icon" alt="Qwen">
        Qwen Chat
      </a>
      <button class="mobile-link" @click="handleNewChat(); closeMobileMenu()">
        <el-icon><Plus /></el-icon>
        新建对话
      </button>
      <div class="mobile-divider"></div>
      <button class="mobile-link" @click="showProfileDialog = true; closeMobileMenu()">
        <el-icon><User /></el-icon>
        {{ authStore.user?.username || '用户' }}
        <el-icon class="edit-icon"><Edit /></el-icon>
      </button>
      <button class="mobile-link logout" @click="handleLogout">
        <el-icon><SwitchButton /></el-icon>
        退出登录
      </button>
    </nav>

    <!-- 个人信息修改弹窗 -->
    <el-dialog v-model="showProfileDialog" title="修改个人信息" width="400px" :close-on-click-modal="false">
      <el-form :model="profileForm" :rules="profileRules" ref="profileFormRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="profileForm.username" placeholder="请输入新用户名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="profileForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="新密码" prop="password">
          <el-input v-model="profileForm.password" type="password" placeholder="不修改请留空" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showProfileDialog = false">取消</el-button>
        <el-button type="primary" @click="handleUpdateProfile" :loading="isUpdatingProfile">
          保存
        </el-button>
      </template>
    </el-dialog>
  </header>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, User, SwitchButton, Edit } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '@/stores/useAuthStore'
import { useChatStore } from '@/stores/useChatStore'

const router = useRouter()
const authStore = useAuthStore()
const chatStore = useChatStore()
const isMobileMenuOpen = ref(false)
const showProfileDialog = ref(false)
const isUpdatingProfile = ref(false)
const profileFormRef = ref<FormInstance>()

const profileForm = reactive({
  username: '',
  email: '',
  password: ''
})

const profileRules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

// 当弹窗打开时，填充当前用户信息
watch(showProfileDialog, (val) => {
  if (val && authStore.user) {
    profileForm.username = authStore.user.username || ''
    profileForm.email = authStore.user.email || ''
    profileForm.password = ''
  }
})

function toggleMobileMenu() {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}

function closeMobileMenu() {
  isMobileMenuOpen.value = false
}

function handleNewChat() {
  chatStore.clearChat()
}

async function handleUpdateProfile() {
  if (!profileFormRef.value) return

  await profileFormRef.value.validate(async (valid) => {
    if (valid) {
      isUpdatingProfile.value = true
      try {
        const success = await authStore.updateProfile(
          profileForm.username,
          profileForm.email,
          profileForm.password || undefined
        )
        if (success) {
          ElMessage.success('个人信息已更新')
          showProfileDialog.value = false
        }
      } finally {
        isUpdatingProfile.value = false
      }
    }
  })
}

async function handleLogout() {
  await authStore.logout()
  closeMobileMenu()
  router.push('/login')
}
</script>

<style scoped lang="scss">
.app-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  z-index: 1000;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.header-left {
  display: flex;
  align-items: center;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 36px;
  height: 36px;
  background: #5b6eae;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;

  svg {
    width: 20px;
    height: 20px;
  }
}

.logo-text {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  white-space: nowrap;
}

.header-center {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-link {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  color: #4b5563;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  border-radius: 8px;
  transition: all 0.2s ease;

  &:hover {
    background: #f3f4f6;
    color: #5b6eae;
  }

  .link-icon {
    width: 20px;
    height: 20px;
  }

  .external-icon {
    width: 14px;
    height: 14px;
    opacity: 0.5;
  }
}

.new-chat-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #5b6eae;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover:not(:disabled) {
    background: #4a5a94;
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  color: #4b5563;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: #e5e7eb;
    border-color: #d1d5db;
  }

  .user-icon {
    font-size: 18px;
  }

  .edit-icon {
    font-size: 14px;
    opacity: 0.6;
  }
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: transparent;
  border: 1px solid #ef4444;
  color: #ef4444;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: #ef4444;
    color: white;
  }
}

/* 移动端汉堡菜单按钮 */
.mobile-menu-btn {
  display: none;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 5px;
  width: 40px;
  height: 40px;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 8px;

  .menu-line {
    width: 22px;
    height: 2px;
    background: #4b5563;
    border-radius: 2px;
    transition: all 0.3s ease;
  }
}

.mobile-menu-overlay {
  display: none;
  position: fixed;
  top: 60px;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 998;
}

.mobile-menu {
  display: none;
  position: fixed;
  top: 60px;
  right: -280px;
  width: 280px;
  height: calc(100vh - 60px);
  background: white;
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.1);
  padding: 20px;
  z-index: 999;
  transition: right 0.3s ease;
  flex-direction: column;
  gap: 8px;

  &.open {
    right: 0;
  }
}

.mobile-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  color: #4b5563;
  text-decoration: none;
  font-size: 15px;
  font-weight: 500;
  border-radius: 10px;
  border: none;
  background: transparent;
  cursor: pointer;
  width: 100%;
  text-align: left;
  transition: all 0.2s ease;

  .link-icon {
    width: 22px;
    height: 22px;
  }

  .edit-icon {
    margin-left: auto;
    opacity: 0.6;
  }

  &:hover {
    background: #f3f4f6;
    color: #5b6eae;
  }

  &.logout {
    color: #ef4444;
    &:hover {
      background: #fef2f2;
    }
  }
}

.mobile-divider {
  height: 1px;
  background: #e5e7eb;
  margin: 10px 0;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .logo-text {
    display: none;
  }

  .header-link .link-text {
    display: none;
  }
}

@media (max-width: 768px) {
  .app-header {
    padding: 0 16px;
  }

  .header-center,
  .header-right {
    display: none;
  }

  .mobile-menu-btn {
    display: flex;
  }

  .mobile-menu-overlay {
    display: block;
  }

  .mobile-menu {
    display: flex;
  }
}
</style>
