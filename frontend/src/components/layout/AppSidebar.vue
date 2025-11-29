<template>
  <!-- 汉堡菜单按钮 (仅移动端) -->
  <button class="hamburger-menu" @click="toggleMobileSidebar" aria-label="Toggle menu">
    <span class="hamburger-line"></span>
    <span class="hamburger-line"></span>
    <span class="hamburger-line"></span>
  </button>

  <!-- 遮罩层 (仅移动端，侧边栏打开时) -->
  <div
    v-if="isMobileSidebarOpen"
    class="sidebar-overlay"
    @click="closeMobileSidebar"
  ></div>

  <!-- 侧边栏 -->
  <aside class="app-sidebar" :class="{ 'mobile-open': isMobileSidebarOpen }">
    <ul class="sidebar-nav">
      <li>
        <a
          href="https://gemini.google.com"
          target="_blank"
          rel="noopener noreferrer"
          class="sidebar-link"
          @click="closeMobileSidebar"
        >
          <img
            src="/assets/gemini_logo.svg"
            class="sidebar-icon"
            alt="Gemini"
          >
          <span class="sidebar-text">
            Gemini
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="1em"
              height="1em"
              viewBox="0 0 24 24"
              fill="transparent"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="external-icon"
            >
              <path d="M21 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h6"></path>
              <path d="m21 3-9 9"></path>
              <path d="M15 3h6v6"></path>
            </svg>
          </span>
        </a>
      </li>

      <li>
        <a
          href="https://chat.qwen.ai"
          target="_blank"
          rel="noopener noreferrer"
          class="sidebar-link"
          @click="closeMobileSidebar"
        >
          <img
            src="/assets/qwen_logo.svg"
            class="sidebar-icon"
            alt="Qwen"
          >
          <span class="sidebar-text">
            Qwen Chat
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="1em"
              height="1em"
              viewBox="0 0 24 24"
              fill="transparent"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="external-icon"
            >
              <path d="M21 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h6"></path>
              <path d="m21 3-9 9"></path>
              <path d="M15 3h6v6"></path>
            </svg>
          </span>
        </a>
      </li>

      <li>
        <a
          href="#"
          class="sidebar-link"
          :class="{ active: currentRoute === '/input' }"
          @click.prevent="handleNavigation('/input')"
        >
          <el-icon class="sidebar-icon"><Edit /></el-icon>
          <span class="sidebar-text">输入页</span>
        </a>
      </li>

      <li>
        <a
          href="#"
          class="sidebar-link"
          :class="{ active: currentRoute === '/output' }"
          @click.prevent="handleNavigation('/output')"
        >
          <el-icon class="sidebar-icon">
            <DataAnalysis />
          </el-icon>
          <span class="sidebar-text">输出页</span>
        </a>
      </li>
    </ul>

    <!-- 用户信息区域 -->
    <div class="user-section">
      <div class="user-info">
        <el-icon class="user-icon"><User /></el-icon>
        <span class="user-name">{{ authStore.user?.username || '用户' }}</span>
      </div>
      <button class="logout-button" @click="handleLogout" title="退出登录">
        <el-icon><SwitchButton /></el-icon>
        <span class="logout-text">退出</span>
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Edit, DataAnalysis, User, SwitchButton } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/useAuthStore'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const isMobileSidebarOpen = ref(false)

const currentRoute = computed(() => route.path)

function toggleMobileSidebar() {
  isMobileSidebarOpen.value = !isMobileSidebarOpen.value
}

function closeMobileSidebar() {
  isMobileSidebarOpen.value = false
}

function handleNavigation(path: string) {
  router.push(path)
  closeMobileSidebar()
}

async function handleLogout() {
  await authStore.logout()
  closeMobileSidebar()
  router.push('/login')
}
</script>

<style scoped lang="scss">
/* 汉堡菜单按钮 */
.hamburger-menu {
  position: fixed;
  top: 15px;
  left: 15px;
  width: 40px;
  height: 40px;
  background-color: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  display: none;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 5px;
  cursor: pointer;
  z-index: 1100;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: background-color 0.2s ease;

  &:hover {
    background-color: #f8f9fa;
  }

  &:active {
    background-color: #e4e6eb;
  }

  .hamburger-line {
    width: 20px;
    height: 2px;
    background-color: #333;
    border-radius: 2px;
    transition: all 0.3s ease;
  }
}

/* 遮罩层 */
.sidebar-overlay {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 999;
}

/* 侧边栏 */
.app-sidebar {
  position: fixed;
  left: 0;
  top: 0;
  width: 60px;
  height: 100vh;
  background-color: #f8f9fa;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  transition: width 0.3s ease;
  overflow-x: hidden;
  z-index: 1000;

  &:hover {
    width: 200px;

    .sidebar-text {
      opacity: 1;
    }
  }
}

.sidebar-nav {
  list-style: none;
  padding: 0;
  margin: 0;

  li {
    display: flex;
    align-items: center;
  }
}

.sidebar-link {
  display: flex;
  align-items: center;
  padding: 15px 18px;
  color: #333;
  text-decoration: none;
  transition: background-color 0.2s ease;
  width: 100%;
  position: relative;

  &:hover {
    background-color: #e4e6eb;
  }

  &.active {
    color: #1877f2;
    border-bottom: 2px solid #1877f2;
  }
}

.sidebar-icon {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
}

.sidebar-text {
  opacity: 0;
  transition: opacity 0.1s ease;
  margin-left: 15px;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 4px;
}

.external-icon {
  width: 1em;
  height: 1em;
}

/* 用户信息区域 */
.user-section {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  border-top: 1px solid #e0e0e0;
  background-color: #f8f9fa;
}

.user-info {
  display: flex;
  align-items: center;
  padding: 12px 18px;
  color: #333;

  .user-icon {
    width: 24px;
    height: 24px;
    flex-shrink: 0;
  }

  .user-name {
    opacity: 0;
    transition: opacity 0.1s ease;
    margin-left: 15px;
    white-space: nowrap;
    font-size: 14px;
    font-weight: 500;
  }
}

.logout-button {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 12px 18px;
  background: none;
  border: none;
  color: #dc3545;
  cursor: pointer;
  transition: background-color 0.2s ease;

  &:hover {
    background-color: #ffe6e6;
  }

  .el-icon {
    width: 24px;
    height: 24px;
    flex-shrink: 0;
  }

  .logout-text {
    opacity: 0;
    transition: opacity 0.1s ease;
    margin-left: 15px;
    white-space: nowrap;
    font-size: 14px;
  }
}

.app-sidebar:hover {
  .user-name,
  .logout-text {
    opacity: 1;
  }
}

/* 响应式设计 */

/* 移动端 (<768px) */
@media (max-width: 767px) {
  .hamburger-menu {
    display: flex;
  }

  .sidebar-overlay {
    display: block;
  }

  .app-sidebar {
    left: -250px;
    width: 250px;
    transition: left 0.3s ease;

    &.mobile-open {
      left: 0;
    }

    .sidebar-text {
      opacity: 1;
    }

    &:hover {
      width: 250px;
    }
  }

  .user-name,
  .logout-text {
    opacity: 1;
  }
}

/* 平板 (768px-1024px) */
@media (min-width: 768px) and (max-width: 1023px) {
  .app-sidebar {
    width: 60px;

    &:hover {
      width: 150px;

      .sidebar-text {
        opacity: 1;
      }
    }
  }

  .sidebar-text {
    opacity: 0;
  }
}

/* 桌面 (>=1024px) - 保持原有样式 */
@media (min-width: 1024px) {
  .app-sidebar {
    width: 60px;

    &:hover {
      width: 200px;

      .sidebar-text {
        opacity: 1;
      }
    }
  }

  .sidebar-text {
    opacity: 0;
  }
}
</style>
